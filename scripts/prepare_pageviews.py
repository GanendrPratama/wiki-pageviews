#!/usr/bin/env python3
"""Ubah satu file pageview Wikimedia per jam (dari stdin) menjadi TSV siap ImportTsv.

Input  : baris "domain_code page_title count_views total_response_size"
Output : <judul_ternormalisasi>#<YYYYMMDDHH> \t desktop \t mobile \t total

Hanya domain "id" (desktop) dan "id.m" (mobile) yang diambil.
Pemakaian: zcat pageviews-20261031-180000.gz | python3 prepare_pageviews.py 2026103117
(argumen = jam AWAL periode UTC; berkas ...-180000 berisi kunjungan 17:00-18:00 UTC)
"""
import re
import sys
import unicodedata
from collections import defaultdict
from urllib.parse import unquote

# Namespace non-artikel (Istimewa:, Berkas:, Pengguna:, dst.) dibuang.
NON_ARTICLE = re.compile(r"^[^:]+:")
SPECIAL = re.compile(r"[^\w]+", re.UNICODE)


def normalize(title: str) -> str:
    t = unquote(title)
    t = unicodedata.normalize("NFC", t).lower().replace(" ", "_")
    t = SPECIAL.sub("", t)  # \w mempertahankan huruf, angka, dan underscore
    return re.sub(r"_+", "_", t).strip("_")


def main() -> None:
    hour = sys.argv[1]
    desktop = defaultdict(int)
    mobile = defaultdict(int)
    for raw in sys.stdin.buffer:
        parts = raw.decode("utf-8", "replace").split(" ")
        if len(parts) != 4 or parts[0] not in ("id", "id.m"):
            continue
        title = parts[1]
        if NON_ARTICLE.match(title) or title == "-":
            continue
        key = normalize(title)
        if not key:
            continue
        target = desktop if parts[0] == "id" else mobile
        target[key] += int(parts[2])
    out = sys.stdout
    for key in desktop.keys() | mobile.keys():
        d, m = desktop.get(key, 0), mobile.get(key, 0)
        out.write(f"{key}#{hour}\t{d}\t{m}\t{d + m}\n")


if __name__ == "__main__":
    main()
