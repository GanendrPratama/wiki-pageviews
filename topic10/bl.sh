#!/usr/bin/env bash
# bl.sh FILE.sql : jalankan berkas SQL lewat Beeline di container (tanpa TTY)
docker exec -e HADOOP_CLIENT_OPTS=-Dorg.jline.terminal.provider=dumb hiveserver2 \
  beeline -u jdbc:hive2://localhost:10000/ -e "$(cat "$1")"
