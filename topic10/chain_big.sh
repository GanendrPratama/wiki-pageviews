#!/usr/bin/env bash
# Tunggu pemuatan Hive data besar selesai, lalu benchmark Hive big, lalu Spark big.
cd "$(dirname "$0")"
while pgrep -f "setup_hive_big" >/dev/null; do sleep 5; done
echo "load done $(date +%T)"
python3 hive_bench.py _big 2>&1 | tee hive_big.txt
pkill -f "memwatch.sh hive" ; sleep 1
nohup ./memwatch.sh "topic10-wiki|pyspark" mem_spark_big.txt >/dev/null 2>&1 &
mw=$!
echo "spark start $(date +%T)"
./venv/bin/python spark_bench.py data/pageviews_big.csv big 2>&1 | grep -v WARN | tee spark_big.txt
kill $mw
echo "all done $(date +%T)"
