# HBase Wikipedia Pageviews (Kelompok 5, Tugas 9)

Hourly Wikipedia pageviews for `id` / `id.m` (2026-10-25..31 UTC) in HBase 2.6.7,
pseudo-distributed on Hadoop 3.5.0 HDFS with HBase-managed ZooKeeper (originally on a Raspberry Pi).

Table `wiki_pageviews_hourly`, row key `<normalized_title>#<YYYYMMDDHH>`,
column family `pv` (`desktop`, `mobile`, `total`), 5,717,607 rows for the full week.

## Topic 10: processing layer

Hive vs Spark SQL on the same data, with step-by-step instructions, results and screenshots: see [`topic10/`](topic10/README.md).

## Recreate it

Needs Debian/Ubuntu (x86_64 or aarch64), sudo, ~4 GB RAM, ~3 GB disk.

```bash
git clone git@github.com:GanendrPratama/wiki-pageviews.git
cd wiki-pageviews
./setup.sh      # one time: installs Java 21, Hadoop 3.5.0, HBase 2.6.7 to /opt and formats HDFS
./start.sh      # starts HDFS then HBase (no ssh to localhost needed)
./run_all.sh    # downloads the week from Wikimedia, creates the table, bulk-loads, runs queries
```

For a quick test, load one day only: `./run_all.sh 2026-10-31 2026-10-31`.
The full week downloads 168 hourly dumps (2 at a time, since Wikimedia returns 429 above that).

Then use `hbase shell` (after `source env.sh`), or the web UI at http://localhost:16010.
Stop with `./stop.sh`.

Settings such as install location are in `env.sh`. Override them by exporting first,
for example `INSTALL_DIR=$HOME/apps ./setup.sh`.

## Files

| File | Purpose |
|---|---|
| `setup.sh`, `start.sh`, `stop.sh`, `env.sh` | Install, start and stop Hadoop + HBase |
| `run_all.sh` | Full pipeline: fetch, create table, load, query |
| `config/` | Hadoop and HBase config templates (same as the Pi) |
| `scripts/fetch_pageviews.sh` | Download hourly dumps and filter `id`/`id.m` |
| `scripts/prepare_pageviews.py` | Convert a dump to TSV (row key uses file hour minus 1, since file names mark the end of the hour) |
| `scripts/create_table.hbase` | Create the table (GZ, row bloom filter, pre-split) |
| `scripts/load_pageviews.sh` | Bulk load with ImportTsv and completebulkload |
| `scripts/queries.hbase` | Example queries |
| `outputs/` | Logs and query output from the original Pi run |
