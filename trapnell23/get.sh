#!/bin/bash

set -euo pipefail

wget -O GSE225775_RAW.tar -c "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE225775&format=file"
tar -xf GSE225775_RAW.tar
rm GSE225775_RAW.tar
