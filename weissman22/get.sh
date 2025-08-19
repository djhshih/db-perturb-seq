#!/bin/bash
# Download dataset from Figshare

# Files cannot be downloaded via the download link obtained
# from the webpage
# We need to use the web API instead and provide the file ID
# The download link supplied by file information provided by the api call works as well

set -euo pipefail
IFS=$'\n\t'

wget -O K562_essential_raw_bulk_01.h5ad -c https://ndownloader.figshare.com/files/35773070
wget -O K562_essential_normalized_singlecell_01.h5ad -c https://ndownloader.figshare.com/files/35773075
wget -O K562_gwps_normalized_bulk_01.h5ad -c https://ndownloader.figshare.com/files/35773217
wget -O K562_essential_raw_singlecell_01.h5ad -c https://ndownloader.figshare.com/files/35773219
wget -O K562_gwps_normalized_singlecell_01.h5ad -c https://ndownloader.figshare.com/files/35774440
wget -O K562_gwps_raw_bulk_01.h5ad -c https://ndownloader.figshare.com/files/35774443
wget -O K562_gwps_raw_singlecell_01.h5ad -c https://ndownloader.figshare.com/files/35775507
wget -O rpe1_normalized_bulk_01.h5ad -c https://ndownloader.figshare.com/files/35775512
wget -O rpe1_normalized_singlecell_01.h5ad -c https://ndownloader.figshare.com/files/35775554
wget -O rpe1_raw_bulk_01.h5ad -c https://ndownloader.figshare.com/files/35775581
wget -O rpe1_raw_singlecell_01.h5ad -c https://ndownloader.figshare.com/files/35775606
wget -O K562_essential_normalized_bulk_01.h5ad -c https://ndownloader.figshare.com/files/35780870