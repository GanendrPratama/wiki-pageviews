#!/usr/bin/env bash
# One-time install of Java, Hadoop (HDFS only) and HBase in pseudo-distributed mode,
# using the same configuration as the original Raspberry Pi.
# Tested on Debian 13 (aarch64). Should work on Debian/Ubuntu x86_64 or aarch64.
# Usage: ./setup.sh            (installs to /opt, needs sudo once)
set -euo pipefail
REPO=$(cd "$(dirname "$0")" && pwd)

# 1) Packages
if command -v apt-get >/dev/null; then
  pkgs="curl python3"
  command -v java >/dev/null || pkgs+=" openjdk-21-jdk-headless"
  sudo apt-get update -qq
  sudo apt-get install -y -qq $pkgs
fi
source "$REPO/env.sh"
[[ -n ${JAVA_HOME:-} ]] || { echo "Java not found; install JDK 17 or 21 first" >&2; exit 1; }
echo "JAVA_HOME=$JAVA_HOME"

# 2) Download and extract
arch=$(uname -m)
hadoop_tar=hadoop-$HADOOP_VERSION.tar.gz
[[ $arch == aarch64 ]] && hadoop_tar=hadoop-$HADOOP_VERSION-aarch64.tar.gz
hbase_tar=hbase-$HBASE_VERSION-hadoop3-bin.tar.gz
dl() { # $1 = path under the Apache dist tree
  local f; f=$(basename "$1")
  [[ -s $REPO/downloads/$f ]] && return 0
  mkdir -p "$REPO/downloads"
  curl -fL --retry 3 -o "$REPO/downloads/$f.part" "https://dlcdn.apache.org/$1" \
    || curl -fL --retry 3 -o "$REPO/downloads/$f.part" "https://archive.apache.org/dist/$1"
  mv "$REPO/downloads/$f.part" "$REPO/downloads/$f"
}
sudo mkdir -p "$INSTALL_DIR"
if [[ ! -d $INSTALL_DIR/hadoop-$HADOOP_VERSION ]]; then
  dl "hadoop/common/hadoop-$HADOOP_VERSION/$hadoop_tar"
  sudo tar -xzf "$REPO/downloads/$hadoop_tar" -C "$INSTALL_DIR"
fi
if [[ ! -d $INSTALL_DIR/hbase-$HBASE_VERSION-hadoop3 ]]; then
  dl "hbase/$HBASE_VERSION/$hbase_tar"
  sudo tar -xzf "$REPO/downloads/$hbase_tar" -C "$INSTALL_DIR"
fi
sudo ln -sfn "$INSTALL_DIR/hadoop-$HADOOP_VERSION" "$HADOOP_HOME"
sudo ln -sfn "$INSTALL_DIR/hbase-$HBASE_VERSION-hadoop3" "$HBASE_HOME"
sudo chown -R "$(id -un):$(id -gn)" "$INSTALL_DIR/hadoop-$HADOOP_VERSION" "$INSTALL_DIR/hbase-$HBASE_VERSION-hadoop3"

# 3) Configuration
sed "s|__HADOOP_HOME__|$HADOOP_HOME|g" "$REPO/config/hadoop/core-site.xml" > "$HADOOP_HOME/etc/hadoop/core-site.xml"
sed "s|__HADOOP_HOME__|$HADOOP_HOME|g" "$REPO/config/hadoop/hdfs-site.xml" > "$HADOOP_HOME/etc/hadoop/hdfs-site.xml"
grep -q '^export JAVA_HOME=' "$HADOOP_HOME/etc/hadoop/hadoop-env.sh" \
  || echo "export JAVA_HOME=$JAVA_HOME" >> "$HADOOP_HOME/etc/hadoop/hadoop-env.sh"
sed "s|__ZK_DIR__|$ZK_DIR|g" "$REPO/config/hbase/hbase-site.xml" > "$HBASE_HOME/conf/hbase-site.xml"
if ! grep -q 'Appended to .*by setup.sh' "$HBASE_HOME/conf/hbase-env.sh"; then
  sed "s|__JAVA_HOME__|$JAVA_HOME|g" "$REPO/config/hbase/hbase-env.sh" >> "$HBASE_HOME/conf/hbase-env.sh"
fi
mkdir -p "$ZK_DIR"

# 4) Format HDFS once
if [[ ! -d $HADOOP_HOME/data/namenode/current ]]; then
  "$HADOOP_HOME/bin/hdfs" namenode -format -nonInteractive
fi
echo "Setup done. Next: ./start.sh"
