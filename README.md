# dailybarca

Dark daily Barça cards. Desktop 4-up, mobile stack. One story per card.

## Sourcing engine

Closed pool of **50 English / Spanish / Catalan sites** in `data/sources.json`.

```
python scripts/source_engine.py
```

Writes `data/sourced/YYYY-MM-DD.json`:

- pulls RSS where a feed exists
- falls back to homepage link harvest
- keeps only Barça-relevant headlines
- clusters the same story across desks
- ranks clusters by how many of the 50 sources hit it

GitHub Action `.github/workflows/daily.yml` runs that job every morning and commits the file. Human (or a later step) still turns clusters into the public edition cards in `data/YYYY-MM-DD.json`.

X handles are a second pool and are not in this engine yet.
