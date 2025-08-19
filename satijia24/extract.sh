#!/bin/bash
# Extract data from input

set -euo pipefail
IFS=$'\n\t'

for f in *.rds; do
	echo $f
	Rscript extract.r $f
done
