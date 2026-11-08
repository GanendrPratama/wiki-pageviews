USE wiki;
SELECT r.periode, SUM(o.desktop) AS desktop, SUM(o.mobile) AS mobile,
       ROUND(100.0 * SUM(o.mobile) / SUM(o.total), 1) AS persen_mobile
FROM pageviews_pq o JOIN jam_ref r ON HOUR(o.waktu) = r.jam_utc
GROUP BY r.periode ORDER BY mobile DESC;
