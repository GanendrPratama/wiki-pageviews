USE wiki;
SELECT judul, SUM(total) AS kunjungan, SUM(mobile) AS mobile
FROM pageviews_pq WHERE tgl = '2026-10-31'
GROUP BY judul ORDER BY kunjungan DESC LIMIT 20;
