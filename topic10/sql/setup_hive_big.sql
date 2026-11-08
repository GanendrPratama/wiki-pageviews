CREATE DATABASE IF NOT EXISTS wiki;
USE wiki;
DROP TABLE IF EXISTS pageviews_txt_big;
CREATE TABLE pageviews_txt_big (
  judul STRING, waktu TIMESTAMP, desktop BIGINT, mobile BIGINT, total BIGINT, tgl STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE;
LOAD DATA LOCAL INPATH '/data/pageviews_big.csv' INTO TABLE pageviews_txt_big;
SELECT COUNT(*) FROM pageviews_txt_big;

DROP TABLE IF EXISTS pageviews_pq_big;
CREATE TABLE pageviews_pq_big STORED AS PARQUET AS SELECT * FROM pageviews_txt_big;
SELECT COUNT(*) FROM pageviews_pq_big;

DROP TABLE IF EXISTS pageviews_part_big;
CREATE TABLE pageviews_part_big (
  judul STRING, waktu TIMESTAMP, desktop BIGINT, mobile BIGINT, total BIGINT)
PARTITIONED BY (tgl STRING)
STORED AS PARQUET;
SET hive.exec.dynamic.partition.mode=nonstrict;
INSERT OVERWRITE TABLE pageviews_part_big PARTITION (tgl)
  SELECT judul, waktu, desktop, mobile, total, tgl FROM pageviews_txt_big;
SHOW PARTITIONS pageviews_part_big;

SHOW TABLES;

