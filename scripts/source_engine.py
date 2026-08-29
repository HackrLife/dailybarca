#!/usr/bin/env python3
"""Pull Barca stories from the closed 50-source pool and cluster them."""
from __future__ import annotations
import json, re, sys, time, urllib.error, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES_PATH = ROOT / "data" / "sources.json"
OUT_DIR = ROOT / "data" / "sourced"
UA = "dailybarca-source-engine/1.0 (+https://dailybarca.com)"
TAG_RE = re.compile(r"<[^>]+>")
WORD_RE = re.compile(r"[a-zà-ÿ0-9]+")
STOP = {"the","a","an","and","or","to","of","in","on","for","with","el","la","los","las","un","una","de","del","en","por","con","que","se","su","es","al","vs","over","after","from","as"}

def load_config():
    data = json.loads(SOURCES_PATH.read_text())
    return data["sources"], [k.lower() for k in data["keywords"]]

def fetch(url, timeout=18):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, text/html"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None

def clean(text):
    text = unescape(TAG_RE.sub(" ", text or ""))
    return re.sub(r"\s+", " ", text).strip()

def relevant(text, keywords):
    low = text.lower()
    return any(k in low for k in keywords)

def tokens(text):
    return {w for w in WORD_RE.findall(text.lower()) if w not in STOP and len(w) > 2}

def parse_rss(xml_text):
    items = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items
    for node in list(root.iter()):
        tag = node.tag.lower().split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        fields = {}
        for child in node:
            ctag = child.tag.lower().split("}")[-1]
            fields[ctag] = (child.text or "") + "".join(child.itertext())
            if ctag == "link" and not child.text:
                fields["link"] = child.attrib.get("href", fields.get("link", ""))
        title = clean(fields.get("title", ""))
        link = clean(fields.get("link") or fields.get("id") or "")
        summary = clean(fields.get("description") or fields.get("summary") or fields.get("content") or "")
        published = clean(fields.get("pubdate") or fields.get("published") or fields.get("updated") or "")
        if title and link:
            items.append({"title": title, "url": link, "summary": summary[:400], "published": published})
    return items

def harvest_html(html):
    found = []
    for match in re.finditer(r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', html, re.I | re.S):
        url, inner = match.group(1), clean(match.group(2))
        if 28 <= len(inner) <= 180:
            found.append({"title": inner, "url": url, "summary": "", "published": ""})
    uniq, seen = [], set()
    for item in found:
        key = item["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(item)
    return uniq[:25]

def pull_source(source, keywords):
    rows = []
    if source.get("rss"):
        xml_text = fetch(source["rss"])
        if xml_text:
            rows.extend(parse_rss(xml_text))
    if len(rows) < 3:
        html = fetch(source["url"])
        if html:
            rows.extend(harvest_html(html))
    keep = []
    for row in rows:
        blob = f"{row['title']} {row['summary']}"
        if not relevant(blob, keywords):
            continue
        keep.append({"source_id": source["id"], "source": source["name"], "tier": source.get("tier", ""), "lang": source.get("lang", []), "title": row["title"], "url": row["url"], "summary": row["summary"], "published": row["published"]})
    return keep[:20]

def cluster(items, threshold=0.28):
    clusters = []
    for item in items:
        t = tokens(item["title"])
        if not t:
            continue
        matched, best = None, 0.0
        for cl in clusters:
            inter = len(t & cl["tokens"])
            union = len(t | cl["tokens"]) or 1
            score = inter / union
            if score > best and score >= threshold:
                best, matched = score, cl
        if matched:
            matched["items"].append(item)
            matched["tokens"] |= t
        else:
            clusters.append({"tokens": set(t), "items": [item]})
    ranked = []
    for cl in clusters:
        sources, seen = [], set()
        for it in cl["items"]:
            if it["source"] in seen:
                continue
            seen.add(it["source"])
            sources.append({"name": it["source"], "url": it["url"], "tier": it["tier"]})
        lead = cl["items"][0]
        ranked.append({"headline": lead["title"], "summary": lead["summary"] or lead["title"], "source_count": len(sources), "languages": sorted({lang for it in cl["items"] for lang in it.get("lang", [])}), "sources": sources[:8], "articles": cl["items"][:8]})
    ranked.sort(key=lambda c: (-c["source_count"], -len(c["articles"])))
    return ranked

def main():
    sources, keywords = load_config()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    items, failures = [], []
    for source in sources:
        got = pull_source(source, keywords)
        if got:
            items.extend(got)
        else:
            failures.append(source["name"])
        time.sleep(0.15)
    clusters = cluster(items)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"date": stamp, "generated_at": datetime.now(timezone.utc).isoformat(), "source_pool": len(sources), "articles_kept": len(items), "clusters": len(clusters), "failed_sources": failures, "stories": clusters[:50]}
    out = OUT_DIR / f"{stamp}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"wrote {out} · {len(items)} articles · {len(clusters)} clusters · {len(failures)} quiet sources")
    return 0

if __name__ == "__main__":
    sys.exit(main())
