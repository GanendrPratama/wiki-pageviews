#!/usr/bin/env python3
"""Topic 10, Spark SQL: measure the five queries from the assignment.

Each query runs once as a warm-up (not counted), then 3 timed runs; the median is reported.
Usage:  python scripts/spark_bench.py <pageviews.csv> [suffix]
        suffix: "" for 1x (default), "_big" for the enlarged data
Reads:  <pageviews.csv> (table pageviews_txt), jam_ref.csv from the same folder,
        data/parquet/pageviews_pq<suffix> and data/parquet/pageviews_part<suffix>
        (written by spark_results.py, which must run first)
Run it from the repository folder (/var/opt/wiki-pageviews) with Spark's Python.
"""
import os, sys, time, statistics
from spark_results import session, PAGEVIEWS, JAM_REF
from queries import JOBS


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    csv_path = sys.argv[1]
    suffix = sys.argv[2] if len(sys.argv) == 3 else ""
    pq, part = f"data/parquet/pageviews_pq{suffix}", f"data/parquet/pageviews_part{suffix}"
    for folder in (pq, part):
        if not os.path.isdir(folder):
            sys.exit(f"{folder} not found. Run spark_results.py first.")

    spark = session()
    jam_ref = os.path.join(os.path.dirname(csv_path), "jam_ref.csv")
    spark.read.csv(jam_ref, header=True, schema=JAM_REF).createOrReplaceTempView("jam_ref")
    spark.read.csv(csv_path, schema=PAGEVIEWS).createOrReplaceTempView(f"pageviews_txt{suffix}")
    spark.read.parquet(pq).createOrReplaceTempView(f"pageviews_pq{suffix}")
    spark.read.parquet(part).createOrReplaceTempView(f"pageviews_part{suffix}")

    print(f"Data: {csv_path} | Spark {spark.version} | 1 warm-up + 3 runs, seconds")
    for name, query, table in JOBS:
        sql = query.format(t=table + suffix)
        spark.sql(sql).collect()  # warm-up, not counted
        runs = []
        for _ in range(3):
            t0 = time.perf_counter()
            spark.sql(sql).collect()
            runs.append(time.perf_counter() - t0)
        print(f"{name:15s} {table + suffix:19s}", " ".join(f"{x:7.2f}" for x in runs),
              f"| median {statistics.median(runs):7.2f}", flush=True)

    spark.stop()


if __name__ == "__main__":
    main()