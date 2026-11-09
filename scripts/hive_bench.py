#!/usr/bin/env python3
"""Topic 10, Hive: turn Beeline's output from `hive_sql.py bench` into a table of times.

Reads Beeline's output (stdout and stderr) from standard input, takes the time from every
"N rows selected (x seconds)" line, drops each query's warm-up run and reports the median
of the other 3, in the same layout as spark_bench.py.
Usage:  ... | python3 -B scripts/hive_bench.py <output.txt> [suffix]
        Writes the table to <output.txt> and also prints it.
"""
import re, sys, statistics
from queries import JOBS
from hive_sql import RUNS

TIME = re.compile(r"rows? selected \(([\d.]+) seconds\)")
VERSION = re.compile(r"Connected to: Apache Hive \(version ([^)]+)\)")


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    out = sys.argv[1]
    suffix = sys.argv[2] if len(sys.argv) == 3 else ""

    times, errors, version = [], [], "?"
    for line in sys.stdin:
        if m := TIME.search(line):
            times.append(float(m.group(1)))
        elif m := VERSION.search(line):
            version = m.group(1)
        elif "Error" in line:
            errors.append(line.rstrip())

    expected = len(JOBS) * RUNS
    if len(times) != expected:
        print(f"Expected {expected} timings, found {len(times)}. Beeline errors:")
        print("\n".join(errors[-10:]) or "(none found)")
        sys.exit(1)

    lines = [f"Data: {suffix or '1x'} | Hive {version} (Beeline, Tez) | 1 warm-up + 3 runs, seconds"]
    for i, (name, _, table) in enumerate(JOBS):
        runs = times[i * RUNS + 1:(i + 1) * RUNS]  # first run of each query is the warm-up
        lines.append(f"{name:15s} {table + suffix:19s} "
                     + " ".join(f"{x:7.2f}" for x in runs)
                     + f" | median {statistics.median(runs):7.2f}")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()