#!/usr/bin/env bash
# Stop HBase first, then HDFS.
set -uo pipefail
source "$(cd "$(dirname "$0")" && pwd)/env.sh"
"$HBASE_HOME/bin/hbase-daemon.sh" stop regionserver
"$HBASE_HOME/bin/hbase-daemon.sh" stop master
"$HBASE_HOME/bin/hbase-daemon.sh" stop zookeeper
"$HADOOP_HOME/bin/hdfs" --daemon stop datanode
"$HADOOP_HOME/bin/hdfs" --daemon stop namenode
"$JAVA_HOME/bin/jps"
