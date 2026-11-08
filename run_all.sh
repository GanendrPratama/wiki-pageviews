#!/usr/bin/env bash
# Rebuild the table end to end: download -> create table -> bulk load -> example queries.
# Usage: ./run_all.sh [START_DATE] [END_DATE]   (default 2026-10-25 2026-10-31, the original week)
set -euo pipefail
REPO=$(cd "$(dirname "$0")" && pwd)
source "$REPO/env.sh"
START=${1:-2026-10-25}; END=${2:-2026-10-31}
TSV=$REPO/data/tsv

"$REPO/scripts/fetch_pageviews.sh" "$START" "$END" "$TSV"
if echo "exists 'wiki_pageviews_hourly'" | hbase shell -n 2>/dev/null | grep -q 'does exist'; then
  echo "Table exists; dropping it to reload"
  printf "disable 'wiki_pageviews_hourly'\ndrop 'wiki_pageviews_hourly'\n" | hbase shell -n
fi
hbase shell -n "$REPO/scripts/create_table.hbase"
"$REPO/scripts/load_pageviews.sh" "$TSV"
hbase shell -n "$REPO/scripts/queries.hbase"
