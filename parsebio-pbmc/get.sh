#!/bin/bash
# Download dataset from Figshare

# Files cannot be downloaded via the download link obtained
# from the webpage
# We need to use the web API instead and provide the file ID
# The download link supplied by the api call works as well

set -euo pipefail
IFS=$'\n\t'

wget -O adata_for_cellflow_datasets_with_embeddings.h5ad -c https://ndownloader.figshare.com/files/53372768

