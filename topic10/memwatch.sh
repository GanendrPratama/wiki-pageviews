#!/usr/bin/env bash
# memwatch.sh PATTERN OUTFILE : catat RSS maksimum (MB) proses java yang cocok PATTERN tiap 2 detik
pat=$1; out=$2; max=0
while true; do
  cur=$(ps -eo rss,args | grep java | grep -E "$pat" | grep -v grep | awk '{s+=$1} END {print int(s/1024)}')
  [[ ${cur:-0} -gt $max ]] && max=$cur && echo "$max" > "$out"
  sleep 2
done
