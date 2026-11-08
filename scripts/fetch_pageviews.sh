#!/usr/bin/env bash
# Unduh dump pageview per jam untuk rentang tanggal, saring id/id.m, dan tulis TSV per jam.
# Pemakaian: ./fetch_pageviews.sh 2026-10-25 2026-10-31 ./data/tsv
# (menghasilkan row key jam 2026102500..2026103123, dari berkas ...20261025-010000 s.d. ...20261101-000000)
set -euo pipefail
START=$1; END=$2; OUT=$3
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"

one_hour() {
  set -o pipefail
  # ts = jam AWAL periode (UTC) yang dipakai di row key.
  # Nama berkas Wikimedia menandai AKHIR periode, jadi jam 17:00-18:00 ada di berkas ...-180000.
  local ts=$1 out=$2 here=$3
  local f="$out/$ts.tsv"
  [[ -s $f ]] && return 0
  local fts; fts=$(date -u -d "${ts:0:8} ${ts:8:2}:00 UTC + 1 hour" +%Y%m%d%H)
  local y=${fts:0:4} m=${fts:4:2} d=${fts:6:2} h=${fts:8:2}
  local url="https://dumps.wikimedia.org/other/pageviews/$y/$y-$m/pageviews-$y$m$d-${h}0000.gz"
  for attempt in 1 2 3; do
    if curl -fsSL --retry 3 -A "KelompokBigData-HBase-tugas/1.0 (student project)" "$url" | zcat | grep -aE '^id(\.m)? ' \
        | python3 "$here/prepare_pageviews.py" "$ts" > "$f.part"; then
      mv "$f.part" "$f"; echo "ok $ts $(wc -l < "$f")"; return 0
    fi
    sleep 20
  done
  echo "FAIL $ts" >&2; return 1
}
export -f one_hour

d=$START
while [[ $d < $END || $d == "$END" ]]; do
  for h in $(seq -w 0 23); do echo "${d//-/}$h"; done
  d=$(date -I -d "$d + 1 day")
done | xargs -P 2 -I{} bash -c 'one_hour "$@"' _ {} "$OUT" "$HERE"
