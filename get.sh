#!/bin/bash
# Download dataset from Figshare

# Files cannot be downloaded via the download link obtained
# from the webpage
# We need to use the web API instead and provide the file ID

set -euo pipefail
IFS=$'\n\t'

# wget --no-check-certificate -c \
# 	-O HCT116_filtered_dual_guide_cells.h5ad.md5 \
# 	https://api.figshare.com/v2/file/download/55021208

# wget --no-check-certificate -c \
# 	-O HEK293T_filtered_dual_guide_cells.h5ad.md5 \
# 	https://api.figshare.com/v2/file/download/55025077

wget --no-check-certificate -c \
	-O HCT116_filtered_dual_guide_cells.h5ad \
	https://api.figshare.com/v2/file/download/55021257

# wget --no-check-certificate -c \
# 	-O HEK293T_filtered_dual_guide_cells.h5ad \
# 	https://api.figshare.com/v2/file/download/55074802

