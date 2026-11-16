#!/usr/bin/env python3
"""Topic 11 rate test: replay pageview titles as edit-shaped events at a fixed rate.

Usage:  /var/opt/spark/venv/bin/python scripts/suntingan_uji_producer.py <events per second> <seconds> [csv]
        csv: default data/csv/pageviews.csv (Topic 10)
Sends only to the test topic 'suntingan-uji', key = judul. Fields other than judul and waktu are
fixed test values, so suntingan_stream.py can process them exactly like real edits.
"""
import csv, json, sys, time
from datetime import datetime, timezone
from confluent_kafka import Producer

TOPIC = "suntingan-uji"


def titles(path):
    # Titles from the first CSV column, repeated from the top when the file runs out
    while True:
        with open(path, encoding="utf-8") as f:
            for row in csv.reader(f):
                yield row[0]


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    rate, duration = int(sys.argv[1]), int(sys.argv[2])
    path = sys.argv[3] if len(sys.argv) == 4 else "data/csv/pageviews.csv"
    p = Producer({"bootstrap.servers": "127.0.0.1:9092", "linger.ms": 20,
                  "queue.buffering.max.messages": 1000000})
    src = titles(path)
    start, sent = time.time(), 0
    while time.time() - start < duration:
        second_start = time.time()
        waktu = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        for _ in range(rate):
            judul = next(src)
            ev = {"judul": judul, "waktu": waktu, "jenis": "edit", "bot": False, "anonim": False,
                  "selisih_ukuran": 0, "minor": False, "revisi_baru": None}
            while True:
                try:
                    p.produce(TOPIC, key=judul, value=json.dumps(ev, ensure_ascii=False))
                    break
                except BufferError:  # send queue full: let it drain, then retry
                    p.poll(0.05)
            sent += 1
        p.poll(0)
        rest = 1 - (time.time() - second_start)
        if rest > 0:
            time.sleep(rest)
    p.flush()
    elapsed = time.time() - start
    print(f"sent: {sent} in {elapsed:.1f} s ({sent / elapsed:.0f} events/s, target {rate})")


if __name__ == "__main__":
    main()