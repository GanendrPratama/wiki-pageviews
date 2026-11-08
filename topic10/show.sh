#!/usr/bin/env bash
# show.sh SQLFILE : tampilkan perintah lalu jalankan SQL lewat Beeline (keluaran dibersihkan dari log Java)
cd "$(dirname "$0")"
echo "$(whoami)@$(hostname):$(pwd)\$ docker exec hiveserver2 beeline -u jdbc:hive2://localhost:10000/ -e \"\$(cat $1)\""
./bl.sh "$1" 2>&1 | grep -vE 'SLF4J|NativeCodeLoader|^\s+at |^INFO  :|^\s*$|Transaction isolation|^Driver:'
