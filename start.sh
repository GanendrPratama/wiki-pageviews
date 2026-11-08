#!/usr/bin/env bash
# Start HDFS, then HBase (ZooKeeper, master, regionserver). Uses per-daemon commands,
# so no passwordless ssh to localhost is needed.
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/env.sh"
running() { "$JAVA_HOME/bin/jps" | grep -qw "$1"; }
running NameNode || "$HADOOP_HOME/bin/hdfs" --daemon start namenode
running DataNode || "$HADOOP_HOME/bin/hdfs" --daemon start datanode
echo "Waiting for HDFS..."
for i in $(seq 30); do
  "$HADOOP_HOME/bin/hdfs" dfsadmin -safemode wait >/dev/null 2>&1 && break
  [[ $i == 30 ]] && { echo "HDFS did not come up; check $HADOOP_HOME/logs" >&2; exit 1; }
  sleep 3
done
running HQuorumPeer  || "$HBASE_HOME/bin/hbase-daemon.sh" start zookeeper
running HMaster      || "$HBASE_HOME/bin/hbase-daemon.sh" start master
running HRegionServer || "$HBASE_HOME/bin/hbase-daemon.sh" start regionserver
# Poll the master's JMX endpoint (cheap) instead of launching hbase shell (slow on a Pi).
# Gives up after ~3 minutes, or right away if the master or regionserver process dies.
echo "Waiting for HBase master..."
jmx='http://localhost:16010/jmx?qry=Hadoop:service=HBase,name=Master,sub=Server'
for _ in $(seq 60); do
  if curl -sf "$jmx" | grep -Eq '"numRegionServers" *: *[1-9]'; then
    "$JAVA_HOME/bin/jps"; echo "HBase is up. Web UI: http://localhost:16010"; exit 0
  fi
  for p in HMaster HRegionServer; do
    running "$p" || { echo "$p died; check $HBASE_HOME/logs" >&2; exit 1; }
  done
  sleep 3
done
echo "HBase did not come up within 3 minutes; check $HBASE_HOME/logs" >&2; exit 1
