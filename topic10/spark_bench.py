#!/usr/bin/env python3
"""Spark SQL: baca CSV, tulis Parquet (biasa dan berpartisi tgl), jalankan 3 query
dengan 1 pemanasan + 3 kali ukur. Pemakaian: python spark_bench.py data/pageviews.csv 1x"""
import statistics, sys, time
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from queries import jobs

csv_path = sys.argv[1]
tag = sys.argv[2] if len(sys.argv) > 2 else "1x"
spark = (SparkSession.builder.master("local[*]").appName("topic10-wiki")
         .config("spark.driver.memory", "3g")
         .config("spark.sql.session.timeZone", "UTC")
         .config("spark.sql.shuffle.partitions", "8")
         .config("spark.ui.showConsoleProgress", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
schema = StructType([StructField("judul", StringType()), StructField("waktu", TimestampType()),
    StructField("desktop", LongType()), StructField("mobile", LongType()),
    StructField("total", LongType()), StructField("tgl", StringType())])
spark.read.csv("data/jam_ref.csv", header=True, inferSchema=True).createOrReplaceTempView("jam_ref")
txt = spark.read.csv(csv_path, schema=schema)
pq, pp = f"data/spark_pq_{tag}", f"data/spark_part_{tag}"
t0 = time.perf_counter()
txt.write.mode("overwrite").parquet(pq)
txt.write.mode("overwrite").partitionBy("tgl").parquet(pp)
print(f"Tulis Parquet: {time.perf_counter() - t0:.1f} detik")
s = "" if tag == "1x" else "_big"
txt.createOrReplaceTempView("pageviews_txt" + s)
spark.read.parquet(pq).createOrReplaceTempView("pageviews_pq" + s)
spark.read.parquet(pp).createOrReplaceTempView("pageviews_part" + s)
print("Data:", tag, "| Spark", spark.version, flush=True)
for name, q, t in jobs(s):
    spark.sql(q.format(t=t)).collect()          # pemanasan, tidak dihitung
    runs = []
    for _ in range(3):
        t0 = time.perf_counter()
        spark.sql(q.format(t=t)).collect()
        runs.append(time.perf_counter() - t0)
    print(f"{name:16s} {t:20s}", " ".join(f"{x:7.2f}" for x in runs),
          f"| median {statistics.median(runs):7.2f} detik", flush=True)
