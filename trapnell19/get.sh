#!/bin/bash

set -euo pipefail

wget -O GSE139944_RAW.tar -c "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE139944&format=file"
tar -xf GSE139944_RAW.tar
rm GSE139944_RAW.tar
