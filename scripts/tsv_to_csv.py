#!/usr/bin/env python3
"""Turn the Topic 9 hourly TSV files into the Topic 10 CSV files.

Input:  data/tsv/*.tsv, one file per hour, each line:
        <judul>#<YYYYMMDDHH><TAB><desktop><TAB><mobile><TAB><total>
Output: <output.csv>, no header:  judul,waktu,desktop,mobile,total,tgl
          waktu = start of the hour in UTC (YYYY-MM-DD HH:00:00), tgl = YYYY-MM-DD
        jam_ref.csv in the same folder, with header: jam_utc,jam_wib,periode

Usage:  python3 scripts/tsv_to_csv.py <tsv_folder> <output.csv> [copies]
        copies > 1 makes enlarged data: the week is repeated, each copy shifted 7 days earlier.
"""
import sys, os, glob, datetime as dt
from collections import Counter


def periode(jam_wib):
    if jam_wib <= 4:
        return "Dini hari"
    if jam_wib <= 10:
        return "Pagi"
    if jam_wib <= 14:
        return "Siang"
    if jam_wib <= 17:
        return "Sore"
    return "Malam"


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    tsv_dir, out = sys.argv[1], sys.argv[2]
    copies = int(sys.argv[3]) if len(sys.argv) == 4 else 1
    files = sorted(glob.glob(os.path.join(tsv_dir, "*.tsv")))
    if not files:
        sys.exit(f"No .tsv files in {tsv_dir}")

    rows = bad = 0
    rows_day, views_day = Counter(), Counter()
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for k in range(copies):
            shift = dt.timedelta(days=7 * k)
            for path in files:
                with open(path, encoding="utf-8") as tsv:
                    for line in tsv:
                        try:
                            key, desktop, mobile, total = line.rstrip("\n").split("\t")
                            judul, jam = key.rsplit("#", 1)
                            d, m, t = int(desktop), int(mobile), int(total)
                            waktu = dt.datetime.strptime(jam, "%Y%m%d%H") - shift
                            if not judul or "," in judul or d + m != t:
                                raise ValueError
                        except ValueError:
                            bad += 1
                            continue
                        tgl = waktu.strftime("%Y-%m-%d")
                        f.write(f"{judul},{waktu:%Y-%m-%d %H:%M:%S},{d},{m},{t},{tgl}\n")
                        rows += 1
                        rows_day[tgl] += 1
                        views_day[tgl] += t

    jam_ref = os.path.join(os.path.dirname(out) or ".", "jam_ref.csv")
    with open(jam_ref, "w", encoding="utf-8", newline="\n") as f:
        f.write("jam_utc,jam_wib,periode\n")
        for h in range(24):
            f.write(f"{h},{(h + 7) % 24},{periode((h + 7) % 24)}\n")

    print(f"TSV files: {len(files)}, copies: {copies}")
    print(f"Rows written: {rows}, bad lines: {bad}")
    for day in sorted(rows_day):
        print(f"  {day}  {rows_day[day]:>9} rows  {views_day[day]:>10} views")
    print(f"Wrote {out} and {jam_ref}")


if __name__ == "__main__":
    main()