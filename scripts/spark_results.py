#!/usr/bin/env python3
"""Topic 10, Spark SQL: write the Parquet tables and show the results of Q1, Q2 and Q3.

Usage:  python scripts/spark_results.py <pageviews.csv> [suffix]
        suffix: "" for 1x (default), "_big" for the enlarged data
Reads:  <pageviews.csv> and jam_ref.csv from the same folder
Writes: data/parquet/pageviews_pq<suffix>    (plain Parquet)
        data/parquet/pageviews_part<suffix>  (Parquet partitioned by tgl, one folder per day)
Run it from the repository folder (/var/opt/wiki-pageviews) with Spark's Python.
"""
import os, sys, time
from pyspark.sql import SparkSession
from pyspark.sql.types import (StructType, StructField, StringType,
                               TimestampType, LongType, IntegerType)
from queries import Q1, Q2, Q3

PAGEVIEWS = StructType([
    StructField("judul", StringType()), StructField("waktu", TimestampType()),
    StructField("desktop", LongType()), StructField("mobile", LongType()),
    StructField("total", LongType()), StructField("tgl", StringType())])
JAM_REF = StructType([
    StructField("jam_utc", IntegerType()), StructField("jam_wib", IntegerType()),
    StructField("periode", StringType())])


def session():
    # The group's settings from the Topic 10 report
    spark = (SparkSession.builder.master("local[*]").appName("topic10")
             .config("spark.driver.memory", "3g")
             .config("spark.sql.shuffle.partitions", "8")
             .config("spark.sql.session.timeZone", "UTC")
             .config("spark.ui.showConsoleProgress", "false")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    csv_path = sys.argv[1]
    suffix = sys.argv[2] if len(sys.argv) == 3 else ""
    pq, part = f"data/parquet/pageviews_pq{suffix}", f"data/parquet/pageviews_part{suffix}"

    spark = session()
    print("Spark", spark.version, "| data:", csv_path)

    txt = spark.read.csv(csv_path, schema=PAGEVIEWS)
    t0 = time.perf_counter()
    txt.write.mode("overwrite").parquet(pq)
    txt.write.mode("overwrite").partitionBy("tgl").parquet(part)
    print(f"Wrote Parquet in {time.perf_counter() - t0:.1f} seconds: {pq}, {part}")

    jam_ref = os.path.join(os.path.dirname(csv_path), "jam_ref.csv")
    spark.read.csv(jam_ref, header=True, schema=JAM_REF).createOrReplaceTempView("jam_ref")
    spark.read.parquet(pq).createOrReplaceTempView("pageviews_pq")
    spark.read.parquet(part).createOrReplaceTempView("pageviews_part")

    for title, query, table in [("Q1 aggregation", Q1, "pageviews_pq"),
                                ("Q2 join", Q2, "pageviews_pq"),
                                ("Q3 partitioned", Q3, "pageviews_part"),
                                ("Q3 not partitioned", Q3, "pageviews_pq")]:
        print(f"\n== {title} ({table})")
        spark.sql(query.format(t=table)).show(20, truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()