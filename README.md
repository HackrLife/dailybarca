# dailybarca

Daily FC Barcelona briefing. One dated edition a day. Stories as dark cards, not a headline river.

Live: [dailybarca.vercel.app](https://dailybarca.vercel.app)  
Repo: [github.com/HackrLife/dailybarca](https://github.com/HackrLife/dailybarca)  
Domain to attach: dailybarca.com

People should get the story from the card. Clicking out is optional.

## What the reader sees

- Dark only. Barça blue `#004D98`, garnet `#A50044`, gold `#EDBB00`.
- Desktop: 3-column card grid. Mobile: one column.
- Edition chip: `Edition 241 · Saturday 29 Aug 2026`.
- Hero: a news headline and a news subhead for that day. Not UI instructions.
- Language switch: EN / ES / DE / FR / IT. Card copy is written in English and Spanish. German, French and Italian fall back to English. Source names and posts stay in the original language.
- Each card: kicker (UCL, Liga, transfer, health, La Masia, tactical, stats, club, finances), headline, 55–75 word blurb, one related post, 8 source links.
- Click the card: 180–220 word note on the same story, plus two different posts from the handle list.
- Archive: older editions by date.

Target: about 24 stories a day, mixed English and Spanish reporting, drawn from the site list and the X list.

## What an edition is not

- Not a Techmeme list.
- Not an X-only feed.
- Not light mode.
- Not a paid X API product. Posts are found with Grok X search and stored as handle + text + optional post ID.

## Source pool

| File | What it is |
| --- | --- |
| `data/sources.json` | 50 news and data sites (EN / ES / CA). Official club, UEFA, LaLiga, wires, English desks, Catalan and Spanish papers, stats sites. |
| `data/x-accounts.json` | 101 handles. Tiers A / B / C. `@BarcaFutbolLive` is #61 (featured analyst). |
| `docs/writing.md` | House style. Mandatory. |

Tiers:

- **A** club, competitions, original interviews, direct reporters, statistical providers.
- **B** established publications, tactical analysts, specialist journalists.
- **C** aggregators, fan accounts, podcasts. Discovery only. Never treat a C account as independent confirmation.

Score a cluster, not a pile of retweets:

- 40% source authority
- 20% independent confirmation
- 15% recency
- 10% Barcelona relevance
- 10% discussion velocity
- 5% editorial quality

If fifteen accounts repeat Fernando Polo, that is one source. Trace every cluster to the earliest identifiable origin.

## How a day is built

1. Pull the 50 sites (`scripts/source_engine.py`, RSS, free).
2. Search the 101 handles with Grok X search. Keep post IDs when you have them. Do not scrape X HTML. Do not buy the X API for this product.
3. Rank and cluster. One origin per story.
4. Write cards against `docs/writing.md`. Grok can attach posts and the fact sheet. A second pass (Claude or a human) can extend the open note and check the URLs. Neither agent invents sources the other did not attach.
5. Write `data/YYYY-MM-DD.json` plus part files if the edition is large (`YYYY-MM-DD-a2.json`, `-b.json`, …).
6. Add the date to `data/editions.json`.
7. Push to `main`. Vercel publishes.

GitHub Action: `.github/workflows/daily.yml`. The Action is a placeholder until the source lists and the daily Grok job are wired end to end. Planned cadence: once a day, 07:00 Australia/Sydney.

## Writing (non-negotiable)

Read `docs/writing.md` before any card is saved.

- Headline: one news sentence.
- Blurb: 55–75 words. Skimmable. Names, numbers, date.
- Open note: 180–220 words. New facts. Two or three paragraphs. Sounds like a person who read the papers.
- Face post = first item in `tweets`. Open view = items two and three.
- Handles only from `data/x-accounts.json`.

Banned: caption-line stacks, “one match is a small sample”, “it shows X / it does not yet show Y”, “the real story is”, “not X but Y”, “that is the test”, punchline dashes, wordplay, cute last lines.

If a sentence could be a tweet on its own, fold it into the paragraph.

## Data shape

`data/editions.json` lists dates. Each edition file has:

```json
{
  "number": 241,
  "date": "2026-08-29",
  "label": "Saturday 29 Aug 2026",
  "title": { "en": "…", "es": "…" },
  "deck": { "en": "…", "es": "…" },
  "defaultSources": [ { "label": "Mundo Deportivo", "url": "…" } ],
  "parts": [ "/data/2026-08-29-a2.json" ],
  "stories": []
}
```

Each story:

```json
{
  "theme": "ucl",
  "kicker": { "en": "UCL", "es": "Champions" },
  "headline": { "en": "…", "es": "…" },
  "summary": { "en": "…", "es": "…" },
  "body": { "en": "…", "es": "…" },
  "tweets": [
    { "name": "Sergi Sole", "handle": "@sergisoleMD", "text": "…" }
  ],
  "sources": [ { "label": "UEFA", "url": "…" } ]
}
```

`js/app.js` loads the edition, concatenates `parts`, paints the grid, and opens the reader. Source chips on a card are that story’s links plus `defaultSources`, de-duplicated.

## Site files

| Path | Role |
| --- | --- |
| `index.html` | Today’s edition |
| `archive.html` | Date list |
| `css/app.css` | Dark grid and reader |
| `js/app.js` | Load JSON, i18n chrome, modal |
| `emails/daily.html` | Mailercloud digest shell (top stories) |
| `scripts/source_engine.py` | RSS pull |
| `scripts/rank.py` | Score and origin rule |
| `scripts/x_pull.py` | Stub. Grok search fills posts |
| `vercel.json` | Static publish |

## Local check

Any static server from the repo root. Example:

```bash
python3 -m http.server 4173
```

Open `/` and `/archive.html`. Add `?date=2026-08-29` or `?story=3` to jump.

## Deploy

GitHub `main` → Vercel project `dailybarca`. No build step. Attach dailybarca.com on Vercel when the edition looks right.

Cost target: GitHub + Vercel hobby. No paid X API.

## Email (later)

Free subscribe on the site. Mailercloud sends a short digest (about 15 stories). Plan is to add those addresses as free members on barcafutbol.com (Ghost) as well. Do not build the send until the edition copy is stable.

## Agents

Two jobs, one handoff.

1. **Collect (Grok)** — sites, handles, origin, three posts, fact sheet. No polished copy.
2. **Write (Claude or Grok against `docs/writing.md`)** — blurb + open note. Check every claim against the attached URLs. Do not add tweets or sources that were not in the pack.

Do not publish a card that fails the pass test in `docs/writing.md`.
