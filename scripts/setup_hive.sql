-- Topic 10, Hive: create the tables from the CSV files in /data (inside the hiveserver2 container).
-- Run with: beeline -u 'jdbc:hive2://localhost:10000/' -f /data/setup_hive.sql
-- Safe to run again: every table is dropped and rebuilt.

CREATE DATABASE IF NOT EXISTS wiki;
USE wiki;
SET hive.exec.dynamic.partition.mode=nonstrict;

-- Reference table: UTC hour -> WIB hour and time of day
DROP TABLE IF EXISTS jam_ref;
CREATE TABLE jam_ref (jam_utc INT, jam_wib INT, periode STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE TBLPROPERTIES ('skip.header.line.count'='1');
LOAD DATA LOCAL INPATH '/data/jam_ref.csv' INTO TABLE jam_ref;

-- 1x data (one week)
DROP TABLE IF EXISTS pageviews_txt;
CREATE TABLE pageviews_txt (
  judul STRING, waktu TIMESTAMP, desktop BIGINT, mobile BIGINT, total BIGINT, tgl STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE;
LOAD DATA LOCAL INPATH '/data/pageviews.csv' INTO TABLE pageviews_txt;

DROP TABLE IF EXISTS pageviews_pq;
CREATE TABLE pageviews_pq STORED AS PARQUET AS SELECT * FROM pageviews_txt;

DROP TABLE IF EXISTS pageviews_part;
CREATE TABLE pageviews_part (
  judul STRING, waktu TIMESTAMP, desktop BIGINT, mobile BIGINT, total BIGINT)
PARTITIONED BY (tgl STRING) STORED AS PARQUET;
INSERT OVERWRITE TABLE pageviews_part PARTITION (tgl)
  SELECT judul, waktu, desktop, mobile, total, tgl FROM pageviews_txt;

-- 3x data (21 days)
DROP TABLE IF EXISTS pageviews_txt_big;
CREATE TABLE pageviews_txt_big (
  judul STRING, waktu TIMESTAMP, desktop BIGINT, mobile BIGINT, total BIGINT, tgl STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE;
LOAD DATA LOCAL INPATH '/data/pageviews_big.csv' INTO TABLE pageviews_txt_big;

DROP TABLE IF EXISTS pageviews_pq_big;
CREATE TABLE pageviews_pq_big STORED AS PARQUET AS SELECT * FROM pageviews_txt_big;

DROP TABLE IF EXISTS pageviews_part_big;
CREATE TABLE pageviews_part_big (
  judul STRING, waktu TIMESTAMP, desktop BIGINT, mobile BIGINT, total BIGINT)
PARTITIONED BY (tgl STRING) STORED AS PARQUET;
INSERT OVERWRITE TABLE pageviews_part_big PARTITION (tgl)
  SELECT judul, waktu, desktop, mobile, total, tgl FROM pageviews_txt_big;

-- Checks
SHOW TABLES;
SELECT COUNT(*) FROM jam_ref;
SELECT COUNT(*) FROM pageviews_txt;
SELECT COUNT(*) FROM pageviews_pq;
SHOW PARTITIONS pageviews_part;
SELECT COUNT(*) FROM pageviews_txt_big;
SELECT COUNT(*) FROM pageviews_pq_big;
SHOW PARTITIONS pageviews_part_big;