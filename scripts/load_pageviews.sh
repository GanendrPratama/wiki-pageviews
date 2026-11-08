#!/usr/bin/env bash
# Bulk load TSV hasil prepare_pageviews.py ke tabel HBase 'wiki_pageviews_hourly'.
# 1) salin TSV ke HDFS  2) ImportTsv menulis HFile  3) completebulkload memindahkan HFile ke region
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
source "$HERE/../env.sh"
LOCAL_TSV=${1:-$HERE/../data/tsv}
TABLE=wiki_pageviews_hourly
HDFS_IN=/user/$(id -un)/pageviews/tsv
HDFS_HFILE=/user/$(id -un)/pageviews/hfiles
HDFS=$HADOOP_HOME/bin/hdfs
HBASE=$HBASE_HOME/bin/hbase

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
