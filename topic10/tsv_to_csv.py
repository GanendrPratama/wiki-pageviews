#!/usr/bin/env python3
"""Ubah TSV Topic 9 (row key HBase) menjadi CSV untuk Hive/Spark.

Input  : <judul>#<YYYYMMDDHH> \t desktop \t mobile \t total   (data/tsv/*.tsv)
Output : judul,waktu,desktop,mobile,total,tgl   (tanpa header)

Pemakaian:
  python3 tsv_to_csv.py TSV_DIR data/pageviews.csv          # data 1x (satu minggu)
  python3 tsv_to_csv.py TSV_DIR data/pageviews_big.csv 5    # data 5x: 5 salinan, tiap salinan
                                                            # digeser mundur 7 hari (5 minggu)
"""
import datetime as dt
import glob
import os
import sys

src, out = sys.argv[1], sys.argv[2]
copies = int(sys.argv[3]) if len(sys.argv) > 3 else 1
files = sorted(glob.glob(os.path.join(src, "*.tsv")))
with open(out, "w") as f:
    for k in range(copies):
        shift = dt.timedelta(days=7 * k)
        for path in files:
            h = dt.datetime.strptime(os.path.basename(path)[:10], "%Y%m%d%H") - shift
            waktu, tgl = h.strftime("%Y-%m-%d %H:00:00"), h.strftime("%Y-%m-%d")
            for line in open(path, encoding="utf-8"):
                key, d, m, t = line.rstrip("\n").split("\t")
                f.write(f"{key.rsplit('#', 1)[0]},{waktu},{d},{m},{t},{tgl}\n")
