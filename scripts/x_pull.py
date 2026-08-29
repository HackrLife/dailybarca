#!/usr/bin/env python3
"""X is curated by Grok, not the paid X API.

This script only writes a pointer file so the daily Action stays cheap.
Posts are attached when Grok writes data/YYYY-MM-DD.json.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "x-accounts.json"
OUT_DIR = ROOT / "data" / "sourced"

def main():
    registry = json.loads(REG.read_text())
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{stamp}-x.json"
    out.write_text(json.dumps({
        "date": stamp,
        "status": "grok-curated",
        "reason": "No X API. Grok searches the 101-handle registry and writes post IDs into the edition cards.",
        "accounts": len(registry["accounts"]),
        "posts": [],
    }, indent=2))
    print(f"wrote {out} · Grok-curated X · {len(registry['accounts'])} handles")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
