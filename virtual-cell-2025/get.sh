# Download data from the Virtual Cell Challenge 2025
gsutil rsync -r -x "FASTQ/.*" 'gs://arc-institute-virtual-cell-atlas/virtual-cell-challenge/2025' .
