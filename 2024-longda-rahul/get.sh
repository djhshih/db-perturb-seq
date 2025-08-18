#!/bin/bash
# Download dataset from Zenodo

set -euo pipefail
IFS=$'\n\t'

wget -O Seurat_object_IFNB_Perturb_seq.rds -cL \
	https://zenodo.org/records/14518762/files/Seurat_object_IFNB_Perturb_seq.rds?download=1

wget -O Seurat_object_IFNG_Perturb_seq.rds -cL \
	https://zenodo.org/records/14518762/files/Seurat_object_IFNG_Perturb_seq.rds?download=1

wget -O Seurat_object_INS_Perturb_seq.rds -cL \
	https://zenodo.org/records/14518762/files/Seurat_object_INS_Perturb_seq.rds?download=1

wget -O Seurat_object_TGFB_Perturb_seq.rds -cL \
	https://zenodo.org/records/14518762/files/Seurat_object_TGFB_Perturb_seq.rds?download=1

wget -O Seurat_object_TNFA_Perturb_seq.rds -cL \
	https://zenodo.org/records/14518762/files/Seurat_object_TNFA_Perturb_seq.rds?download=1

