#!/usr/bin/env python3
"""Pull last-24h posts from the 101-account registry via official X API only."""
from __future__ import annotations
import json, os, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "x-accounts.json"
OUT_DIR = ROOT / "data" / "sourced"

def load_accounts():
    return json.loads(REG.read_text())

def api_search(token, handle, start):
    q = urllib.parse.quote(f"from:{handle} -is:retweet")
    url = "https://api.x.com/2/tweets/search/recent?query=" + q + f"&max_results=10&start_time={start}&tweet.fields=created_at,public_metrics,lang"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "dailybarca-x-pull/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            payload = json.loads(res.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return []
    rows = []
    for t in payload.get("data") or []:
        metrics = t.get("public_metrics") or {}
        rows.append({"id": t.get("id"), "handle": handle, "text": t.get("text", ""), "created_at": t.get("created_at"), "lang": t.get("lang"), "likes": metrics.get("like_count", 0), "reposts": metrics.get("retweet_count", 0), "replies": metrics.get("reply_count", 0), "embed": f"https://x.com/{handle}/status/{t.get('id')}"})
    return rows

def main():
    registry = load_accounts()
    token = os.environ.get("X_BEARER_TOKEN", "").strip()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{stamp}-x.json"
    if not token:
        out.write_text(json.dumps({"date": stamp, "status": "skipped", "reason": "X_BEARER_TOKEN not set. Use official X API or Grok X Search. Do not scrape HTML.", "accounts": len(registry["accounts"]), "posts": []}, indent=2))
        print(f"wrote {out} (no API token)")
        return 0
    posts, quiet = [], []
    for acc in registry["accounts"]:
        got = api_search(token, acc["handle"], start)
        if got:
            for p in got:
                p["tier"] = acc["tier"]
                p["group"] = acc["group"]
                p["corroborate"] = bool(acc.get("corroborate"))
            posts.extend(got)
        else:
            quiet.append(acc["handle"])
    out.write_text(json.dumps({"date": stamp, "status": "ok", "accounts": len(registry["accounts"]), "posts": posts, "quiet": quiet}, ensure_ascii=False, indent=2))
    print(f"wrote {out} · {len(posts)} posts")
    return 0

if __name__ == "__main__":
    sys.exit(main())
