"""Topic 10 queries, shared by the Spark and Hive scripts.

{t} is replaced by the table name. Table names get a suffix for the
enlarged data: "" for 1x (pageviews_pq), "_big" for big (pageviews_pq_big).
"""

# Q1, aggregation: most visited articles on one day, and how many came from mobile
Q1 = """SELECT judul, SUM(total) AS kunjungan, SUM(mobile) AS mobile
FROM {t} WHERE tgl = '2026-10-31'
GROUP BY judul ORDER BY kunjungan DESC LIMIT 20"""

# Q2, join: visits per WIB time of day (jam_ref turns the UTC hour into a WIB period)
Q2 = """SELECT r.periode, SUM(o.desktop) AS desktop, SUM(o.mobile) AS mobile,
       ROUND(100.0 * SUM(o.mobile) / SUM(o.total), 1) AS persen_mobile
FROM {t} o JOIN jam_ref r ON HOUR(o.waktu) = r.jam_utc
GROUP BY r.periode ORDER BY mobile DESC"""

# Q3, partition: rows and visits on one day (run on the partitioned and the plain table)
Q3 = """SELECT COUNT(*) AS baris, SUM(total) AS kunjungan
FROM {t} WHERE tgl = '2026-10-31'"""

# The five measurements from the assignment: (name, query, table without suffix)
JOBS = [
    ("Q1 agregasi", Q1, "pageviews_txt"),
    ("Q1 agregasi", Q1, "pageviews_pq"),
    ("Q2 join", Q2, "pageviews_pq"),
    ("Q3 partisi", Q3, "pageviews_part"),
    ("Q3 non-partisi", Q3, "pageviews_pq"),
]