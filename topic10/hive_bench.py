#!/usr/bin/env python3
"""Ukur 3 query di Hive lewat Beeline: 1 pemanasan + 3 kali ukur, catat median.
Pemakaian: python3 hive_bench.py [suffix]   (suffix '' = data 1x, '_big' = data besar)"""
import re, statistics, subprocess, sys
from queries import jobs
suffix = sys.argv[1] if len(sys.argv) > 1 else ""
print(f"Data: {'1x' if not suffix else suffix.strip('_')} | Hive (Beeline, Tez)", flush=True)
for name, q, t in jobs(suffix):
    sql = "USE wiki;\n" + "\n".join([q.format(t=t) + ";"] * 4)
    out = subprocess.run(["docker", "exec", "-e", "HADOOP_CLIENT_OPTS=-Dorg.jline.terminal.provider=dumb", "hiveserver2", "beeline", "-u",
                          "jdbc:hive2://localhost:10000/", "-e", sql],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout
    secs = [float(x) for x in re.findall(r"rows? selected \(([\d.]+) seconds\)", out)]
    if len(secs) != 4:
        print(name, t, "GAGAL", out[-1500:]); continue
    runs = secs[1:]
    print(f"{name:16s} {t:20s}", " ".join(f"{x:7.2f}" for x in runs),
          f"| median {statistics.median(runs):7.2f} detik", flush=True)
