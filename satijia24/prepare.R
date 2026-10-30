library(io)
library(anndataR)
library(ptmaf)

# convert from Seurat object to anndata
seurat_to_anndata <- function(x) {
	counts <- ptmaf:::t_sparse(x@assays$RNA@counts);
	obs <- x@meta.data;
	stopifnot(nrow(counts) == nrow(obs));
	AnnData(
		X = counts, obs = obs
	)
}

in.fns <- c(
	ifnb = "Seurat_object_IFNB_Perturb_seq.rds",
	ifng = "Seurat_object_IFNG_Perturb_seq.rds",
	ins  = "Seurat_object_INS_Perturb_seq.rds",
	tgfb = "Seurat_object_TGFB_Perturb_seq.rds",
	tnfa = "Seurat_object_TNFA_Perturb_seq.rds"
);

# cell lines: A549, BXPC3, HAP1, HT29, K562, MCF7
# perturb target is in the "gene" field
# control is "NT"
# each stratum contains a different set of targets

for (stratum in names(in.fns)) {
	message(stratum)
	out.fn <- filename("satijia24", tag=c("perturb-seq", stratum), date=NA, ext="h5ad");
	x <- qread(in.fns[stratum]);
	adata <- seurat_to_anndata(x);
	ctype.levels <- unique(adata$obs$cell_type);
	for (ctype in ctype.levels) {
		message(ctype)
		idx <- adata$obs$cell_type == ctype;
		write_h5ad(adata[idx, ], tag(out.fn, tolower(ctype)), compression="gzip");
	}
	rm(x, adata); gc();
}

