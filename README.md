# dailybarca

Free daily Barça brief. Dark cards. Desktop 4-up, mobile stack.

No paid X API. Cost stays at GitHub + Vercel hobby.

## How an edition is made

1. GitHub Action pulls the **50 news sites** (RSS, free).
2. Grok searches the **101 X handles** and picks supporting posts (post IDs only, official embeds).
3. Cards are written to `data/YYYY-MM-DD.json` and Vercel publishes.

Ranking stays the same: 40% authority, 20% independent confirmation, 15% recency, 10% relevance, 10% velocity, 5% editorial. Echoes of one reporter count as one source.
