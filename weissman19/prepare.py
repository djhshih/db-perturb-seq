#!/usr/bin/env python3
"""Combine the filtered GSE133344 (Perturb-seq) release files into a single h5ad.

Inputs (default: the directory containing this script)
------------------------------------------------------
GSE133344_filtered_matrix.mtx.gz
    MatrixMarket sparse count matrix in 10x orientation: rows = genes
    (33694), columns = cells (111668).
GSE133344_filtered_genes.tsv.gz
    One gene per row: Ensembl gene id, gene symbol.
GSE133344_filtered_barcodes.tsv.gz
    One cell barcode (with gem-group suffix, e.g. ``-1``, ``-7``) per matrix
    column, in the order used by the matrix.
GSE133344_filtered_cell_identities.csv.gz
    Guide-capture per-cell metadata (columns: cell_barcode, guide_identity,
    read_count, UMI_count, coverage, gemgroup, good_coverage,
    number_of_cells).  One row per cell barcode, all of which are a subset of
    the barcodes file.

Output
------
GSE133344_filtered.h5ad (or --output), written with anndata.

AnnData layout
--------------
X     scipy.sparse.csr_matrix of the raw UMI counts with the dtype kept as it
      came out of the MatrixMarket file (int32), observations (cells) in rows
      and variables (genes) in columns, i.e. the 10x-style matrix transposed.
obs   The cell_identities columns joined on cell barcode, arranged in exactly
      the order of the barcodes file, restricted to barcodes that have a
      guide_identity row (223 of the 111668 matrix columns have none and are
      dropped, so obs has no NaNs; see ``adata.uns["n_matrix_columns_dropped"]``).
var   Gene symbols as the index.  34 symbols occur more than once in the gene
      file, so duplicates get ``_1``, ``_2`` ... suffixes to keep the index
      unique; the original symbol and its Ensembl id are kept as the
      ``gene_symbol`` / ``ensembl_id`` var columns for traceability.
"""

from __future__ import annotations

import argparse
import contextlib
import gc
import gzip
import shutil
import subprocess
import time
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, csr_matrix

BARCODES_FILE = "GSE133344_filtered_barcodes.tsv.gz"
GENES_FILE = "GSE133344_filtered_genes.tsv.gz"
MATRIX_FILE = "GSE133344_filtered_matrix.mtx.gz"
IDENTITIES_FILE = "GSE133344_filtered_cell_identities.csv.gz"
OUTPUT_FILE = "GSE133344_filtered.h5ad"

IDENTITY_COLUMNS = [
    "cell_barcode",
    "guide_identity",
    "read_count",
    "UMI_count",
    "coverage",
    "gemgroup",
    "good_coverage",
    "number_of_cells",
]

IDENTITY_DTYPES = {
    "cell_barcode": str,
    "guide_identity": str,
    "read_count": np.int32,
    "UMI_count": np.int32,
    "gemgroup": np.int32,
    "number_of_cells": np.int32,
    # "coverage" (float) and "good_coverage" (bool) are inferred from the file.
}


@contextlib.contextmanager
def _decompressed(path: Path):
    """Yield a binary stream with the contents of a gzipped file.

    Prefers the external ``zcat`` pipeline (noticeably faster on buffers this
    size) and falls back to the ``gzip`` module when ``zcat`` is unavailable.
    """
    zcat = shutil.which("zcat")
    if zcat is not None:
        proc = subprocess.Popen([zcat, str(path)], stdout=subprocess.PIPE)
        try:
            yield proc.stdout
        finally:
            # Explicitly close the pipe so zcat dies on EPIPE instead of
            # hanging, then reap it.
            proc.stdout.close()
            proc.wait()
    else:
        fh = gzip.open(path, "rb")
        try:
            yield fh
        finally:
            fh.close()


def make_index_unique(symbols: pd.Series) -> pd.Index:
    """Deduplicate gene symbols by appending _1, _2, ... in file order."""
    used: dict[str, int] = {}
    out: list[str] = []
    for symbol in symbols:
        if symbol not in used:
            used[symbol] = 0
            out.append(symbol)
            continue
        used[symbol] += 1
        candidate = f"{symbol}_{used[symbol]}"
        while candidate in used:  # guard against collisions like "GENE_1_1"
            used[symbol] += 1
            candidate = f"{symbol}_{used[symbol]}"
        used[candidate] = 0
        out.append(candidate)
    return pd.Index(out)


def read_barcodes(path: Path) -> pd.Series:
    """Cell barcodes, one per line, in matrix-column order."""
    with _decompressed(path) as stream:
        barcodes = pd.read_csv(
            stream, header=None, names=["cell_barcode"], dtype=str
        )["cell_barcode"]
    if not barcodes.is_unique:
        duplicates = barcodes[barcodes.duplicated()].unique()[:5].tolist()
        raise ValueError(f"duplicate barcodes in {path.name}: {duplicates}")
    return barcodes


def read_genes(path: Path) -> pd.DataFrame:
    """Two-column (Ensembl gene id, gene symbol) gene table."""
    with _decompressed(path) as stream:
        genes = pd.read_csv(
            stream,
            sep="\t",
            header=None,
            names=["ensembl_id", "gene_symbol"],
            dtype=str,
        )
    if not genes["ensembl_id"].is_unique:
        raise ValueError(f"Ensembl gene ids are not unique in {path.name}")
    if genes.isna().any().any():
        raise ValueError(f"missing gene id or symbol in {path.name}")
    return genes


def read_identities(path: Path) -> pd.DataFrame:
    """Guide-identity per-cell metadata table."""
    with _decompressed(path) as stream:
        identities = pd.read_csv(stream, dtype=IDENTITY_DTYPES)
    missing = set(IDENTITY_COLUMNS) - set(identities.columns)
    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")
    if not identities["cell_barcode"].is_unique:
        duplicates = (
            identities["cell_barcode"][identities["cell_barcode"].duplicated()]
            .unique()[:5]
            .tolist()
        )
        raise ValueError(f"duplicate cell barcodes in {path.name}: {duplicates}")
    return identities


def read_count_matrix(path: Path, n_genes: int, n_cells: int) -> csr_matrix:
    """Parse the MatrixMarket matrix and return cells x genes (transposed).

    The 10x-style matrix is features by cells, while AnnData wants cells x
    genes, so the row/column indices are swapped while building the COO
    matrix.  The count dtype from the file (int32 here) is preserved.
    """
    with _decompressed(path) as stream:
        banner = stream.readline().rstrip(b"\r\n").decode("ascii")
        _ = stream.readline()  # '%' comment line
        header = stream.readline().split()

        if not banner.startswith("%%MatrixMarket"):
            raise ValueError(f"{path.name} is not a MatrixMarket file")
        banner_tokens = banner.split()
        if banner_tokens[1:3] != ["matrix", "coordinate"]:
            raise ValueError(
                f"{path.name} is not a coordinate matrix: {banner_tokens}"
            )
        try:
            mtx_genes, mtx_cells, n_entries = (int(tok) for tok in header[:3])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"malformed shape line in {path.name}") from exc

        if (mtx_genes, mtx_cells) != (n_genes, n_cells):
            raise ValueError(
                f"{path.name} declares shape ({mtx_genes}, {mtx_cells}) but "
                f"the genes/barcodes files hold ({n_genes}, {n_cells})"
            )

        counts = pd.read_csv(
            stream,
            sep=" ",
            header=None,
            names=["gene", "cell", "count"],
            dtype=np.int32,
        )

    if len(counts) != n_entries:
        raise ValueError(
            f"{path.name} declares {n_entries} entries but {len(counts)} "
            "were parsed"
        )

    gene_idx = counts["gene"].to_numpy() - 1
    cell_idx = counts["cell"].to_numpy() - 1
    data = counts["count"].to_numpy()
    del counts
    gc.collect()

    if gene_idx.max() >= n_genes or cell_idx.max() >= n_cells:
        raise ValueError(f"{path.name} contains out-of-range indices")

    # MatrixMarket rows are genes, columns are cells -> build directly as
    # (cell, gene) so the CSR matrix lines up with AnnData's obs/var axes.
    matrix = coo_matrix((data, (cell_idx, gene_idx)), shape=(n_cells, n_genes)).tocsr()
    del data, gene_idx, cell_idx
    gc.collect()

    if matrix.data.dtype != np.int32:
        matrix = matrix.astype(np.int32)
    return matrix


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="directory holding the filtered GSE133344 release files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=f"output h5ad path (default: --data-dir/{OUTPUT_FILE})",
    )
    args = parser.parse_args(argv)

    data_dir = args.data_dir
    output = args.output if args.output is not None else data_dir / OUTPUT_FILE
    started = time.perf_counter()

    def log(message: str) -> None:
        print(f"[{time.perf_counter() - started:7.1f}s] {message}", flush=True)

    log(f"reading barcodes from {data_dir / BARCODES_FILE}")
    barcodes = read_barcodes(data_dir / BARCODES_FILE)

    log(f"reading genes from {data_dir / GENES_FILE}")
    genes = read_genes(data_dir / GENES_FILE)

    log(f"reading cell identities from {data_dir / IDENTITIES_FILE}")
    identities = read_identities(data_dir / IDENTITIES_FILE)

    # Sanity-check that every identity row belongs to a matrix barcode.
    if not pd.Index(identities["cell_barcode"]).difference(barcodes).empty:
        unexpected = (
            pd.Index(identities["cell_barcode"]).difference(barcodes).tolist()[:5]
        )
        raise ValueError(
            f"cell_identities contains barcodes absent from {BARCODES_FILE}: "
            f"{unexpected}"
        )

    # obs rows follow the barcodes-file order, restricted to cells with a
    # guide-identity row (per the requested handling of unannotated cells).
    identity_barcodes = pd.Index(identities["cell_barcode"])
    keep_positions = barcodes.isin(identity_barcodes).to_numpy()
    obs = identities.set_index("cell_barcode").reindex(
        barcodes.to_numpy()[np.flatnonzero(keep_positions)]
    )
    if obs.isna().any().any():
        raise ValueError("some kept cells have no guide-identity row")
    obs.index.name = "cell_barcode"
    obs["guide_identity"] = obs["guide_identity"].astype("category")

    var = pd.DataFrame(
        {
            "ensembl_id": genes["ensembl_id"].to_numpy(),
            "gene_symbol": genes["gene_symbol"].to_numpy(),
        },
        index=make_index_unique(genes["gene_symbol"]),
    )

    log(
        f"parsed {len(barcodes)} barcodes, {len(genes)} genes, "
        f"{len(identities)} guide-identity rows "
        f"({int((~keep_positions).sum())} matrix columns without identity)"
    )

    log(
        f"reading {MATRIX_FILE} "
        f"(expect {len(genes)} x {len(barcodes)} MatrixMarket slogans)"
    )
    x_full = read_count_matrix(data_dir / MATRIX_FILE, len(genes), len(barcodes))
    log(f"parsed {x_full.nnz:,} counts; restricting to guide-identity cells")
    x = x_full[keep_positions]
    del x_full
    gc.collect()
    if x.shape != (len(obs), len(var)):
        raise ValueError(f"X shape {x.shape} disagrees with ({len(obs)}, {len(var)})")

    adata = ad.AnnData(X=x, obs=obs, var=var)
    adata.uns = {
        "source": "GSE133344 (GEO series suppl. files)",
        "release": "filtered",
        "matrix_file": MATRIX_FILE,
        "cell_identities_file": IDENTITIES_FILE,
        "n_matrix_columns_dropped": int((~keep_positions).sum()),
    }

    log(f"writing {output}")
    adata.write_h5ad(output, compression="gzip")

    seconds = time.perf_counter() - started
    log(
        f"wrote {output} ({output.stat().st_size / 1e9:.2f} GB) in "
        f"{int(seconds // 60)}m{seconds % 60:04.1f}s: "
        f"{adata.shape[0]:,} cells x {adata.shape[1]:,} genes, "
        f"{adata.X.nnz:,} counts, {adata.X.dtype=}"
    )
    print("\nobs head:\n" + adata.obs.head(3).to_string(), flush=True)
    print("\nvar head:\n" + adata.var.head(3).to_string(), flush=True)


if __name__ == "__main__":
    main()
