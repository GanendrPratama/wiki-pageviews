#!/usr/bin/env python3
"""Topic 11: send id.wikipedia article edits from Wikimedia EventStreams to the Kafka topic 'suntingan'.

Usage:  /var/opt/spark/venv/bin/python scripts/suntingan_producer.py   (runs until Ctrl+C)
Event (key = judul): judul, waktu, jenis, bot, anonim, selisih_ukuran, minor, revisi_baru
"""
import ipaddress, json, time, unicodedata, urllib.request
from datetime import datetime, timezone
from urllib.parse import unquote
from confluent_kafka import Producer

URL = "https://stream.wikimedia.org/v2/stream/recentchange"
HEADERS = {"Accept": "text/event-stream", "User-Agent": "suntingan-producer/0.1 (educational use)"}
TOPIC = "suntingan"


def normalize(title):
    # Same rule as scripts/prepare_pageviews.py (Topic 9), so titles match the pageview data
    t = unquote(title)
    return unicodedata.normalize("NFC", t).lower().replace(" ", "_")


def is_anonymous(user):
    # Logged-out editors appear as temporary accounts (~2026-...) or, in older events, IP addresses
    if user.startswith("~"):
        return True
    try:
        ipaddress.ip_address(user)
        return True
    except ValueError:
        return False


def to_event(ev):
    # Keep only article edits and new articles on id.wikipedia
    if ev.get("wiki") != "idwiki" or ev.get("namespace") != 0 or ev.get("type") not in ("edit", "new"):
        return None
    length = ev.get("length") or {}
    return {
        "judul": normalize(ev["title"]),
        "waktu": datetime.fromtimestamp(ev["timestamp"], timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "jenis": ev["type"],
        "bot": bool(ev.get("bot")),
        "anonim": is_anonymous(ev.get("user", "")),
        "selisih_ukuran": (length.get("new") or 0) - (length.get("old") or 0),
        "minor": bool(ev.get("minor")),
        "revisi_baru": (ev.get("revision") or {}).get("new"),
    }


def lines(last_id):
    headers = dict(HEADERS)
    if last_id:
        headers["Last-Event-ID"] = last_id  # resume where the dropped connection stopped
    req = urllib.request.Request(URL, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        for raw in r:
            yield raw.decode("utf-8").rstrip("\n")


def main():
    p = Producer({"bootstrap.servers": "127.0.0.1:9092", "linger.ms": 20})
    last_id, sent = None, 0
    print(f"Sending id.wikipedia article edits to topic '{TOPIC}'. Stop with Ctrl+C.")
    try:
        while True:
            try:
                for line in lines(last_id):
                    if line.startswith("id:"):
                        last_id = line[3:].strip()
                    elif line.startswith("data:"):
                        try:
                            e = to_event(json.loads(line[5:]))
                        except (ValueError, KeyError):
                            continue  # skip a damaged line
                        if e:
                            p.produce(TOPIC, key=e["judul"], value=json.dumps(e, ensure_ascii=False))
                            p.poll(0)
                            sent += 1
                            print(f"{sent:6d}  {e['waktu']}  {e['jenis']:4s}  {e['selisih_ukuran']:+7d}  {e['judul']}")
            except OSError as err:  # connection dropped or timed out
                print("Connection lost, reconnecting in 5 s:", err)
                time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        p.flush(10)
        print("Sent:", sent)


if __name__ == "__main__":
    main()
