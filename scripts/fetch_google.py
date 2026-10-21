#!/usr/bin/env python3
"""Google Trends KR Trending Now RSS -> static JSON. No dependencies."""
import datetime as dt
import json
import pathlib
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "google_kr.json"
URL = "https://trends.google.com/trending/rss?geo=KR"
NS = {"ht": "https://trends.google.com/trending/rss"}

def main():
    request = urllib.request.Request(URL, headers={
        "User-Agent": "TrendPick/0.2 (Google Trends public RSS; educational prototype)",
        "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.5",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        raw = response.read(2_000_000)
    root = ET.fromstring(raw)
    items = []
    for item in root.findall("./channel/item")[:25]:
        def value(tag):
            node = item.find(tag, NS)
            return (node.text or "").strip() if node is not None else ""
        title = value("title")
        if not title:
            continue
        news = []
        for n in item.findall("ht:news_item", NS)[:3]:
            def nv(tag):
                el = n.find("ht:" + tag, NS)
                return (el.text or "").strip() if el is not None else ""
            link = nv("news_item_url")
            if link.startswith("https://"):
                news.append({"title": nv("news_item_title"), "source": nv("news_item_source"), "url": link})
        items.append({"title": title, "approx_traffic": value("ht:approx_traffic"),
                      "published": value("pubDate"), "news": news})
    if not items:
        raise ValueError("RSS had no usable trend items; keeping previous data")
    payload = {"source": "Google Trends Trending Now RSS", "region": "KR",
               "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "items": items}
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(items)} trends to {DEST}")

if __name__ == "__main__":
    main()
