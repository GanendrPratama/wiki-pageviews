# HBase Wikipedia Pageviews (Kelompok 5, Tugas 9)

Hourly Wikipedia pageviews for `id` / `id.m` (2026-10-25..31 UTC) loaded into HBase 2.6.7
on a Raspberry Pi (pseudo-distributed on Hadoop 3.5.0 HDFS, HBase-managed ZooKeeper).

Table `wiki_pageviews_hourly`, column family `pv` (`desktop`, `mobile`, `total`), 5,717,607 rows.

| File | Purpose |
|---|---|
| `fetch_pageviews.sh` | Download hourly pageview dumps from Wikimedia |
| `prepare_pageviews.py` | Filter and convert dumps to TSV (row key uses file hour minus 1) |
| `create_table.hbase` | Create the HBase table |
| `load_pageviews.sh` | Bulk-load TSV with ImportTsv |
| `queries.hbase` | Example queries |
| `outputs/` | Logs and query output from the Pi |
| `config/` | `hbase-site.xml` and active `hbase-env.sh` settings |

The raw TSV data (~390 MB) is not included.
