# Shared settings. Sourced by every script; override any value by exporting it first.
HADOOP_VERSION=${HADOOP_VERSION:-3.5.0}
HBASE_VERSION=${HBASE_VERSION:-2.6.7}
INSTALL_DIR=${INSTALL_DIR:-/opt}
export HADOOP_HOME=${HADOOP_HOME:-$INSTALL_DIR/hadoop}
export HBASE_HOME=${HBASE_HOME:-$INSTALL_DIR/hbase}
export ZK_DIR=${ZK_DIR:-$HOME/hbase-zk}
if [[ -z ${JAVA_HOME:-} ]] && command -v java >/dev/null; then
  JAVA_HOME=$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")
fi
export JAVA_HOME
export PATH=$HADOOP_HOME/bin:$HBASE_HOME/bin:$PATH
