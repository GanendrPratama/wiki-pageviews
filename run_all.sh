#!/usr/bin/env bash
# Rebuild the table end to end: download -> create table -> bulk load -> example queries.
# Usage: ./run_all.sh [START_DATE] [END_DATE]   (default 2026-10-25 2026-10-31, the original week)
# Each step's output is saved in outputs/.
set -euo pipefail
REPO=$(cd "$(dirname "$0")" && pwd)
source "$REPO/env.sh"
START=${1:-2026-10-25}; END=${2:-2026-10-31}
TSV=$REPO/data/tsv
OUT=$REPO/outputs
mkdir -p "$OUT"

"$REPO/scripts/fetch_pageviews.sh" "$START" "$END" "$TSV"
# fetch.log: one line per downloaded hour (ok <hour> <rows>), including hours from earlier runs
for f in "$TSV"/*.tsv; do echo "ok $(basename "$f" .tsv) $(wc -l < "$f")"; done > "$OUT/fetch.log"

if echo "exists 'wiki_pageviews_hourly'" | hbase shell -n 2>/dev/null | grep 'does exist' > /dev/null; then
  echo "Table exists; dropping it to reload"
  printf "disable 'wiki_pageviews_hourly'\ndrop 'wiki_pageviews_hourly'\n" | hbase shell -n
fi
hbase shell -n "$REPO/scripts/create_table.hbase" < /dev/null 2>/dev/null | tee "$OUT/create_table.out"
"$REPO/scripts/load_pageviews.sh" "$TSV" 2>&1 | tee "$OUT/load.log"
hbase shell -n "$REPO/scripts/queries.hbase" < /dev/null 2>/dev/null | tee "$OUT/queries.out"