#!/usr/bin/env bash
# Siapkan data/ untuk Hive dan Spark dari TSV Topic 9.
# Pemakaian: ./prepare_data.sh [TSV_DIR]   (default ../data/tsv, hasil ../run_all.sh atau ../scripts/fetch_pageviews.sh)
set -euo pipefail
cd "$(dirname "$0")"
TSV=${1:-../data/tsv}
mkdir -p data
cp jam_ref.csv data/
python3 tsv_to_csv.py "$TSV" data/pageviews.csv        # data 1x (satu minggu)
python3 tsv_to_csv.py "$TSV" data/pageviews_big.csv 3  # data besar 3x (3 minggu, sintetis)
chmod -R a+rX data
wc -l data/*.csv
ls -lh data
