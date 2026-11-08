#!/usr/bin/env python3
"""Tampilkan hasil Q1-Q3 di Spark SQL (dari Parquet yang ditulis spark_bench.py) untuk dicocokkan dengan Hive."""
from pyspark.sql import SparkSession
from queries import Q1, Q2, Q3
spark = (SparkSession.builder.master("local[*]").appName("topic10-hasil")
         .config("spark.driver.memory", "3g").config("spark.sql.session.timeZone", "UTC")
         .config("spark.ui.showConsoleProgress", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
spark.read.csv("data/jam_ref.csv", header=True, inferSchema=True).createOrReplaceTempView("jam_ref")
spark.read.parquet("data/spark_pq_1x").createOrReplaceTempView("pageviews_pq")
spark.read.parquet("data/spark_part_1x").createOrReplaceTempView("pageviews_part")
for name, q, t, n in [("Q1", Q1, "pageviews_pq", 10), ("Q2", Q2, "pageviews_pq", 5),
                      ("Q3 partisi", Q3, "pageviews_part", 1), ("Q3 non-partisi", Q3, "pageviews_pq", 1)]:
    print(f"== {name} ({t})")
    spark.sql(q.format(t=t)).show(n, truncate=False)
