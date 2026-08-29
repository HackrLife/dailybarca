"""Story scoring for dailybarca.

Weights: 40 authority / 20 independent confirmation / 15 recency /
10 relevance / 10 velocity / 5 editorial.
Origin rule: N reprints of the same reporter = one source.
"""
from __future__ import annotations
from datetime import datetime, timezone

TIER_SCORE = {"A": 1.0, "B": 0.62, "C": 0.28}

def authority(accounts):
    if not accounts:
        return 0.0
    return max(TIER_SCORE.get(a.get("tier", "C"), 0.28) for a in accounts)

def independent_confirmation(accounts, origin_handle=None):
    origins = set()
    for acc in accounts:
        handle = acc.get("handle", "").lstrip("@").lower()
        if acc.get("tier") == "C":
            continue
        if handle == (origin_handle or "").lower() or acc.get("group") in {"reporter", "official", "newsroom", "data"}:
            origins.add(handle)
    n = len(origins)
    if n <= 1:
        return 0.25 if n == 1 else 0.0
    if n == 2:
        return 0.7
    return 1.0

def recency(published, now=None):
    if not published:
        return 0.4
    now = now or datetime.now(timezone.utc)
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    hours = max(0.0, (now - published).total_seconds() / 3600)
    if hours <= 6: return 1.0
    if hours <= 24: return 0.75
    if hours <= 48: return 0.4
    return 0.15

def relevance(text, keywords):
    low = (text or "").lower()
    hits = sum(1 for k in keywords if k in low)
    return min(1.0, hits / 3)

def velocity(likes, reposts, replies):
    score = likes + reposts * 3 + replies * 2
    if score >= 8000: return 1.0
    if score >= 2000: return 0.75
    if score >= 400: return 0.5
    if score >= 80: return 0.3
    return 0.1

def editorial(summary, has_author):
    length = len(summary or "")
    base = 0.8 if 80 <= length <= 400 else 0.4
    if has_author:
        base = min(1.0, base + 0.15)
    return base

def story_score(*, accounts, origin_handle, published, text, keywords, likes=0, reposts=0, replies=0, summary="", has_author=False):
    parts = {
        "authority": authority(accounts),
        "independent_confirmation": independent_confirmation(accounts, origin_handle),
        "recency": recency(published),
        "relevance": relevance(text, keywords),
        "velocity": velocity(likes, reposts, replies),
        "editorial": editorial(summary, has_author),
    }
    total = 0.40*parts["authority"] + 0.20*parts["independent_confirmation"] + 0.15*parts["recency"] + 0.10*parts["relevance"] + 0.10*parts["velocity"] + 0.05*parts["editorial"]
    return {"total": round(total, 4), "parts": {k: round(v, 3) for k, v in parts.items()}}
