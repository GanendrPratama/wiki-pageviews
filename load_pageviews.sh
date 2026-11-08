#!/usr/bin/env bash
# Bulk load TSV hasil prepare_pageviews.py ke tabel HBase 'wiki_pageviews'.
# 1) salin TSV ke HDFS  2) ImportTsv menulis HFile  3) completebulkload memindahkan HFile ke region
set -euo pipefail
LOCAL_TSV=${1:-/home/pi/pageviews/tsv_fixed}
TABLE=wiki_pageviews_hourly
HDFS_IN=/user/pi/pageviews/tsv
HDFS_HFILE=/user/pi/pageviews/hfiles
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64
HDFS=/opt/hadoop/bin/hdfs
HBASE=/opt/hbase/bin/hbase

$HDFS dfs -rm -r -f -skipTrash "$HDFS_IN"
$HDFS dfs -mkdir -p "$HDFS_IN"
$HDFS dfs -put -f "$LOCAL_TSV"/*.tsv "$HDFS_IN"/
$HDFS dfs -rm -r -f -skipTrash "$HDFS_HFILE"

time $HBASE org.apache.hadoop.hbase.mapreduce.ImportTsv \
  -Dfs.defaultFS=hdfs://localhost:9000 \
  -Dmapreduce.framework.name=local \
  -Dimporttsv.separator=$'\t' \
  -Dimporttsv.columns=HBASE_ROW_KEY,pv:desktop,pv:mobile,pv:total \
  -Dimporttsv.bulk.output="$HDFS_HFILE" \
  "$TABLE" "$HDFS_IN"

time $HBASE completebulkload -Dfs.defaultFS=hdfs://localhost:9000 "$HDFS_HFILE" "$TABLE"
