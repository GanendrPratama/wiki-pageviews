# Tiga query proyek (dipakai bersama oleh Hive dan Spark SQL). {t} = nama tabel.
TGL = "2026-10-31"
Q1 = f"""SELECT judul, SUM(total) AS kunjungan, SUM(mobile) AS mobile
FROM {{t}} WHERE tgl = '{TGL}'
GROUP BY judul ORDER BY kunjungan DESC LIMIT 20"""
Q2 = """SELECT r.periode, SUM(o.desktop) AS desktop, SUM(o.mobile) AS mobile,
       ROUND(100.0 * SUM(o.mobile) / SUM(o.total), 1) AS persen_mobile
FROM {t} o JOIN jam_ref r ON HOUR(o.waktu) = r.jam_utc
GROUP BY r.periode ORDER BY mobile DESC"""
Q3 = f"""SELECT COUNT(*) AS baris, SUM(total) AS kunjungan FROM {{t}} WHERE tgl = '{TGL}'"""

def jobs(suffix=""):
    return [("Q1 agregasi", Q1, "pageviews_txt" + suffix),
            ("Q1 agregasi", Q1, "pageviews_pq" + suffix),
            ("Q2 join", Q2, "pageviews_pq" + suffix),
            ("Q3 partisi", Q3, "pageviews_part" + suffix),
            ("Q3 non-partisi", Q3, "pageviews_pq" + suffix)]
