#!/usr/bin/env python3
"""Topic 10, Hive: print SQL for Beeline, built from the query texts in queries.py.

Usage:  python3 -B scripts/hive_sql.py results
          Q1, Q2 and Q3 (partitioned and not) on the 1x tables, to compare with Spark.
        python3 -B scripts/hive_sql.py bench [suffix]
          The five measurements from queries.JOBS, each run 4 times (1 warm-up + 3 timed).
          suffix: "" for 1x (default), "_big" for the enlarged data.
The output is passed to Beeline with -e (see "Running a SQL file with Beeline" in the guide).
-B stops Python from writing a __pycache__ folder when it's run with podman exec (as root).
"""
import sys
from queries import Q1, Q2, Q3, JOBS

RUNS = 4  # 1 warm-up + 3 timed runs; hive_bench.py expects the same number


def results():
    statements = ["USE wiki"]
    for query, table in [(Q1, "pageviews_pq"), (Q2, "pageviews_pq"),
                         (Q3, "pageviews_part"), (Q3, "pageviews_pq")]:
        statements.append(query.format(t=table))
    return statements


def bench(suffix):
    # The results cache would answer repeated queries without running them
    statements = ["USE wiki", "SET hive.query.results.cache.enabled=false"]
    for _, query, table in JOBS:
        statements += [query.format(t=table + suffix)] * RUNS
    return statements


def main():
    args = sys.argv[1:]
    if args == ["results"]:
        statements = results()
    elif args[:1] == ["bench"] and len(args) <= 2:
        statements = bench(args[1] if len(args) == 2 else "")
    else:
        sys.exit(__doc__)
    print(";\n".join(statements) + ";")


if __name__ == "__main__":
    main()