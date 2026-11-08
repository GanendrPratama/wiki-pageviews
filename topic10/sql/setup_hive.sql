CREATE DATABASE IF NOT EXISTS wiki;
USE wiki;
DROP TABLE IF EXISTS pageviews_txt;
CREATE TABLE pageviews_txt (
  judul STRING, waktu TIMESTAMP, desktop BIGINT, mobile BIGINT, total BIGINT, tgl STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE;
LOAD DATA LOCAL INPATH '/data/pageviews.csv' INTO TABLE pageviews_txt;
SELECT COUNT(*) FROM pageviews_txt;

DROP TABLE IF EXISTS pageviews_pq;
CREATE TABLE pageviews_pq STORED AS PARQUET AS SELECT * FROM pageviews_txt;
SELECT COUNT(*) FROM pageviews_pq;

DROP TABLE IF EXISTS pageviews_part;
CREATE TABLE pageviews_part (
  judul STRING, waktu TIMESTAMP, desktop BIGINT, mobile BIGINT, total BIGINT)
PARTITIONED BY (tgl STRING)
STORED AS PARQUET;
SET hive.exec.dynamic.partition.mode=nonstrict;
INSERT OVERWRITE TABLE pageviews_part PARTITION (tgl)
  SELECT judul, waktu, desktop, mobile, total, tgl FROM pageviews_txt;
SHOW PARTITIONS pageviews_part;

DROP TABLE IF EXISTS jam_ref;
CREATE TABLE jam_ref (jam_utc INT, jam_wib INT, periode STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE TBLPROPERTIES ('skip.header.line.count'='1');
LOAD DATA LOCAL INPATH '/data/jam_ref.csv' INTO TABLE jam_ref;
SELECT * FROM jam_ref;
SHOW TABLES;
