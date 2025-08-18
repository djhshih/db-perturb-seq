#!/bin/bash
# Download dataset

set -euo pipefail
IFS=$'\n\t'

wget -cL https://ftp.ncbi.nlm.nih.gov/geo/series/GSE264nnn/GSE264667/suppl/GSE264667_hepg2_raw_singlecell_01.h5ad
wget -cL https://ftp.ncbi.nlm.nih.gov/geo/series/GSE264nnn/GSE264667/suppl/GSE264667_jurkat_raw_singlecell_01.h5ad

wget -cL https://ftp.ncbi.nlm.nih.gov/geo/series/GSE264nnn/GSE264667/suppl/GSE264667_RAW.tar
tar -xf GSE264667_RAW.tar
rm GSE264667_RAW.tar
