#!/usr/bin/env python3
"""Topic 11: count id.wikipedia article edits per minute from Kafka.

Usage:  /var/opt/spark/venv/bin/python scripts/suntingan_stream.py console
          Show the counts from topic 'suntingan' in the terminal (update mode).
        /var/opt/spark/venv/bin/python scripts/suntingan_stream.py parquet <output folder> <checkpoint folder>
          Write closed windows from topic 'suntingan' to Parquet (append mode), with a checkpoint.
        /var/opt/spark/venv/bin/python scripts/suntingan_stream.py bench <topic>
          Rate test: read only new events from <topic>, discard the results, and every 10 seconds
          print a summary of all batches finished in those 10 seconds.
Run it from the repository folder (/var/opt/wiki-pageviews) with Spark's Python.
"""
import sys, time
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, LongType

KAFKA = "127.0.0.1:9092"

# The 8 fields sent by suntingan_producer.py (and suntingan_uji_producer.py)
SKEMA = StructType([
    StructField("judul", StringType()), StructField("waktu", StringType()),
    StructField("jenis", StringType()), StructField("bot", BooleanType()),
    StructField("anonim", BooleanType()), StructField("selisih_ukuran", LongType()),
    StructField("minor", BooleanType()), StructField("revisi_baru", LongType())])


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def bench(q, topic):
    # Every second, read all new batch reports; every 10 seconds, print what happened in total:
    #   received   = rows that arrived per second (all batches together)
    #   processed  = rows per second while Spark was working (its capacity)
    #   busy       = share of the time Spark was working; near 100% means no spare capacity
    #   max delay  = oldest event's age when its batch finished; small and steady = keeping up,
    #                growing from one line to the next = falling behind (events wait in Kafka)
    print(f"Measuring topic '{topic}'. Start the test producer now. Stop with Ctrl+C.", flush=True)
    print("time      received rows/s  processed rows/s   busy   max delay   batches", flush=True)
    seen, rows, busy, delay, batches = -1, 0, 0.0, 0.0, 0
    start = time.time()
    try:
        while q.isActive:
            time.sleep(1)
            for pr in q.recentProgress:
                if pr["batchId"] <= seen:
                    continue
                seen = pr["batchId"]
                if pr["numInputRows"] == 0:
                    continue
                dur = pr["durationMs"].get("triggerExecution", 0) / 1000
                rows += pr["numInputRows"]
                busy += dur
                batches += 1
                if "min" in pr.get("eventTime", {}):
                    age = (ts(pr["timestamp"]) - ts(pr["eventTime"]["min"])).total_seconds() + dur
                    delay = max(delay, age)
            elapsed = time.time() - start
            if elapsed >= 10:
                if rows:
                    print(f"{time.strftime('%H:%M:%S')}  {rows / elapsed:15.1f}  {rows / busy:16.1f}"
                          f"  {100 * busy / elapsed:5.1f}%  {delay:8.1f} s  {batches:8d}", flush=True)
                rows, busy, delay, batches = 0, 0.0, 0.0, 0
                start = time.time()
    except KeyboardInterrupt:
        q.stop()


def main():
    args = sys.argv[1:]
    mode = args[0] if args else ""
    if mode == "console" and len(args) == 1 or mode == "parquet" and len(args) == 3:
        topic = "suntingan"
    elif mode == "bench" and len(args) == 2:
        topic = args[1]
    else:
        sys.exit(__doc__)

    spark = (SparkSession.builder.master("local[*]").appName(f"suntingan-{mode}")
             .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.3.0")
             .config("spark.driver.memory", "3g")
             .config("spark.sql.shuffle.partitions", "3")
             .config("spark.sql.session.timeZone", "UTC")
             .config("spark.ui.showConsoleProgress", "false")
             .getOrCreate())
    spark.sparkContext.setLogLevel("WARN")

    mentah = (spark.readStream.format("kafka")
              .option("kafka.bootstrap.servers", KAFKA)
              .option("subscribe", topic)
              # bench measures only events sent during the test; the others start from the oldest event
              .option("startingOffsets", "latest" if mode == "bench" else "earliest")
              .load())

    # Kafka's value is bytes: turn it into text, then into the 8 columns
    ev = (mentah.select(F.from_json(F.col("value").cast("string"), SKEMA).alias("e"))
          .select("e.*")
          .withColumn("waktu", F.to_timestamp("waktu")))

    per_menit = (ev.withWatermark("waktu", "2 minutes")
                 .groupBy(F.window("waktu", "1 minute"), "judul")
                 .agg(F.count("*").alias("jumlah_suntingan"),
                      F.sum(F.col("anonim").cast("int")).alias("suntingan_anonim"),
                      F.sum(F.col("bot").cast("int")).alias("suntingan_bot"),
                      F.sum(F.col("minor").cast("int")).alias("suntingan_minor"),
                      F.sum((F.col("jenis") == "new").cast("int")).alias("artikel_baru"),
                      F.min("selisih_ukuran").alias("selisih_terkecil"),
                      F.max("revisi_baru").alias("revisi_terakhir")))

    if mode == "console":
        q = (per_menit.writeStream.outputMode("update").format("console")
             .option("truncate", "false").trigger(processingTime="10 seconds").start())
    elif mode == "parquet":
        q = (per_menit.writeStream.outputMode("append").format("parquet")
             .option("path", args[1]).option("checkpointLocation", args[2])
             .trigger(processingTime="10 seconds").start())
    else:
        # No fixed trigger: Spark takes the next batch as soon as the previous one is done
        q = per_menit.writeStream.outputMode("update").format("noop").start()
        bench(q, topic)
        return
    q.awaitTermination()


if __name__ == "__main__":
    main()