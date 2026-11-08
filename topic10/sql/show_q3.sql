USE wiki;
SELECT COUNT(*) AS baris, SUM(total) AS kunjungan FROM pageviews_part WHERE tgl = '2026-10-31';
SELECT COUNT(*) AS baris, SUM(total) AS kunjungan FROM pageviews_pq WHERE tgl = '2026-10-31';
