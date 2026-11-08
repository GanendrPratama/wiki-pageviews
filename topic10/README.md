# Topic 10: Lapisan Processing (Hive vs Spark SQL)

Kelompok 5, Teknologi Big Data. Lanjutan dari Topic 9 (HBase, folder induk repo ini).

Kami membandingkan **Hive 4.2.1 (Tez, di Docker)** dan **Spark SQL (PySpark 4.3.0, local mode)** pada data proyek:
kunjungan per jam artikel Wikipedia bahasa Indonesia (`id` + `id.m`), 25 sampai 31 Oktober 2026.
Semua dijalankan di Raspberry Pi 4 (4 core ARM64, RAM 8 GB, Debian 13), mesin yang sama dengan HBase Topic 9.

**Keputusan: Spark SQL pada Parquet berpartisi tanggal (`tgl`).** Spark 4 sampai 10 kali lebih cepat
untuk query yang sama di mesin kami. HBase tetap dipakai untuk lookup riwayat satu artikel.

## Hasil (median 3 kali ukur setelah 1 pemanasan, detik)

| Query dan tabel | Hive 1x | Hive 3x | Spark 1x | Spark 3x |
|---|---|---|---|---|
| Q1 agregasi, teks (CSV) | 40.51 | 88.47 | 21.25 | 53.31 |
| Q1 agregasi, Parquet | 18.71 | 24.86 | 4.44 | 4.70 |
| Q2 join, Parquet | 34.51 | 82.45 | 5.38 | 11.39 |
| Q3 partisi | 4.64 | 3.53 | 0.44 | 0.71 |
| Q3 non-partisi | 6.16 | 7.24 | 0.64 | 1.11 |

- 1x = 5.717.607 baris, 303 MB CSV (7 hari). 3x = 17.152.821 baris, 909 MB CSV (21 hari, salinan sintetis
  dari minggu yang sama, digeser mundur 7 hari per salinan).
- Memori puncak (RSS): HiveServer2 1.697 MB (selalu hidup), Spark 3.007 MB (hanya saat skrip berjalan).
- Keluaran mentah ada di [`results/`](results/), screenshot di [`screenshots/`](screenshots/),
  diagram arsitektur v0.2 di [`diagram/`](diagram/).

## Tiga query

Teks SQL ada di [`queries.py`](queries.py) dan dipakai bersama oleh Hive dan Spark, jadi query-nya identik.

| Query | Pertanyaan proyek | Teknik |
|---|---|---|
| Q1 | 20 artikel terpopuler pada 31 Oktober 2026, berapa yang dari mobile | agregasi `GROUP BY judul` |
| Q2 | Periode WIB mana yang paling ramai, berapa persen mobile | `JOIN jam_ref ON HOUR(waktu) = jam_utc` |
| Q3 | Jumlah baris dan kunjungan pada satu hari | partisi `tgl` lawan tanpa partisi |

`jam_ref.csv` adalah tabel referensi kecil (24 baris): jam UTC ke jam WIB dan periode (Dini hari, Pagi, Siang, Sore, Malam).

## Cara mengulang dari awal

Prasyarat: Linux (Debian/Ubuntu, x86_64 atau ARM64), Docker, Python 3.10+, Java 17+, RAM minimal 8 GB.

### 0. Ambil data proyek (dari Topic 9)

```bash
git clone https://github.com/GanendrPratama/wiki-pageviews.git
cd wiki-pageviews
scripts/fetch_pageviews.sh 2026-10-25 2026-10-31 data/tsv   # 168 dump per jam dari Wikimedia, butuh waktu
cd topic10
./prepare_data.sh                                            # data/pageviews.csv (1x), data/pageviews_big.csv (3x), data/jam_ref.csv
```

Tidak perlu HBase untuk Topic 10; cukup TSV hasil `fetch_pageviews.sh`.

### 1. Jalankan Hive di Docker

```bash
sudo apt-get install -y docker.io python3-venv && sudo usermod -aG docker $USER   # login ulang setelah ini
docker pull apache/hive:4.2.1          # ada varian arm64, jalan di Raspberry Pi
docker run -d -p 10000:10000 -p 10002:10002 --env SERVICE_NAME=hiveserver2 \
  -v "$PWD/data:/data" --name hiveserver2 apache/hive:4.2.1
docker logs -f hiveserver2             # tunggu 1 sampai 2 menit, Ctrl+C
./show.sh sql/show_connect.sql         # SELECT version(); SET hive.execution.engine;  -> tez
```

Antarmuka web HiveServer2: `http://<ip-mesin>:10002`.

> **Catatan Beeline:** Beeline 4.2.1 di Java 21 gagal tanpa TTY (`Unable to create a terminal`,
> dan `-f` diam-diam tidak menjalankan apa pun). Karena itu semua skrip memanggil Beeline lewat
> [`bl.sh`](bl.sh): `HADOOP_CLIENT_OPTS=-Dorg.jline.terminal.provider=dumb` dan isi berkas SQL lewat `-e`.
> Untuk sesi interaktif biasa, `docker exec -it hiveserver2 beeline -u jdbc:hive2://localhost:10000/` tetap bisa dipakai.

### 2. Buat tabel Hive dan ukur (data 1x)

```bash
./bl.sh sql/setup_hive.sql            # pageviews_txt, pageviews_pq, pageviews_part (7 partisi), jam_ref; sekitar 9 menit di Pi
./show.sh sql/show_tables.sql         # SHOW TABLES, SHOW PARTITIONS, isi jam_ref
./show.sh sql/show_desc.sql           # DESCRIBE FORMATTED pageviews_pq
./show.sh sql/show_q1.sql             # hasil Q1 (juga show_q2.sql, show_q3.sql)
python3 hive_bench.py | tee results/hive_1x.txt    # 1 pemanasan + 3 ukur per query, median
```

### 3. Spark SQL (data 1x)

```bash
python3 -m venv venv && ./venv/bin/pip install pyspark
./venv/bin/python spark_bench.py data/pageviews.csv 1x | tee results/spark_1x.txt
./venv/bin/python spark_results.py    # cetak hasil Q1-Q3 untuk dicocokkan dengan Hive
```

Spark berjalan dengan `local[*]`, `spark.driver.memory=3g`, `spark.sql.shuffle.partitions=8`, zona waktu sesi UTC
(agar `HOUR(waktu)` sama dengan Hive). Jangan jalankan Hive dan Spark bersamaan saat mengukur.

### 4. Data besar (3x)

```bash
./bl.sh sql/setup_hive_big.sql        # tabel *_big; sekitar 20 menit di Pi
python3 hive_bench.py _big | tee results/hive_big.txt
./venv/bin/python spark_bench.py data/pageviews_big.csv big | tee results/spark_big.txt
```

Atau semuanya berurutan, dengan pencatatan memori puncak: `./chain_big.sh` (menunggu `setup_hive_big` selesai bila sedang berjalan).
Bilah progres Spark dari log lama bisa dibersihkan dengan `python3 clean_spark.py results/spark_1x.txt`.

## Berkas

| Berkas | Fungsi |
|---|---|
| `prepare_data.sh`, `tsv_to_csv.py` | TSV Topic 9 ke CSV (`judul,waktu,desktop,mobile,total,tgl`); argumen ketiga = jumlah salinan untuk data besar |
| `jam_ref.csv` | Tabel referensi untuk join (Q2) |
| `queries.py` | Teks Q1, Q2, Q3 untuk Hive dan Spark |
| `sql/setup_hive.sql`, `sql/setup_hive_big.sql` | Buat tabel teks, Parquet, Parquet berpartisi, jam_ref |
| `sql/show_*.sql` | Query untuk screenshot (koneksi, tabel, describe, Q1-Q3) |
| `bl.sh`, `show.sh` | Jalankan SQL lewat Beeline tanpa TTY; `show.sh` juga mencetak perintahnya |
| `hive_bench.py`, `spark_bench.py` | Benchmark: 1 pemanasan, 3 ukur, median |
| `spark_results.py` | Tampilkan hasil query Spark |
| `memwatch.sh`, `chain_big.sh` | Catat RSS maksimum; jalankan semua benchmark data besar berurutan |
| `clean_spark.py` | Hapus bilah progres Spark dari log |
| `results/` | Keluaran asli dari Raspberry Pi |
| `screenshots/` | Screenshot yang dipakai di laporan |
| `diagram/arsitektur_v02.svg` | Diagram arsitektur v0.2 (render ke PNG dengan `rsvg-convert`) |

## Batasan

- HiveServer2 di Docker memakai Metastore Derby dan warehouse `file:/opt/hive/data/warehouse` di dalam container (bukan HDFS).
  Hive 4.2.1 otomatis mengubah tabel managed menjadi EXTERNAL dengan `external.table.purge=TRUE`.
- Hive dan Spark berbagi CPU dan RAM satu Raspberry Pi, jadi perbandingannya relatif untuk mesin ini.
  Sebagian besar waktu Hive adalah biaya tetap Tez per query (sekitar 3 sampai 4 detik).
- Data besar 3x, bukan 5x, karena pemuatan Hive di Pi sudah sekitar 9 menit untuk data 1x.
