# Download data from the Virtual Cell Challenge 2025
# There is no Challenge training set this year.
# A virtual cell challenge account is required for downloading the data.
# See https://virtualcellchallenge.org/datasets for more information.

set -euo pipefail

mkdir validation
vcc datasets list
vcc datasets download controls -d ~/validation

cd ./validation
unzip ./vcc_2026_controls.zip
rm -f ./vcc_2026_controls.zip
