#!/bin/bash

set -euo pipefail

wget -e robots=off -r -np -nH --cut-dirs=5 -R "index.html*" https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl/

if [[ -f "GSE133344_RAW.tar" ]]; then
    tar -xf GSE133344_RAW.tar --one-top-level
    rm GSE133344_RAW.tar
fi

# wget -O GSE133344_RAW.tar -c "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE133344&format=file"
# tar -xf GSE133344_RAW.tar
# rm GSE133344_RAW.tar

# wget -O GSE133344_filtered_barcodes.tsv.gz -c https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl/GSE133344_filtered_barcodes.tsv.gz

# wget -O GSE133344_filtered_cell_identities.csv.gz -c https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl/GSE133344_filtered_cell_identities.csv.gz

# wget -O GSE133344_filtered_genes.tsv.gz -c https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl/GSE133344_filtered_genes.tsv.gz

# wget -O GSE133344_filtered_matrix.mtx.gz -c https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl/GSE133344_filtered_matrix.mtx.gz

# wget -O GSE133344_raw_barcodes.tsv.gz -c https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl/GSE133344_raw_barcodes.tsv.gz

# wget -O GSE133344_raw_cell_identities.csv.gz -c https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl/GSE133344_raw_cell_identities.csv.gz

# wget -O GSE133344_raw_genes.tsv.gz -c https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl/GSE133344_raw_genes.tsv.gz

# wget -O /GSE133344_raw_matrix.mtx.gz -c https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl/GSE133344_raw_matrix.mtx.gz

# wget -O filelist.txt -c https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl/filelist.txt
