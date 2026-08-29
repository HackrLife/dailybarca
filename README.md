# dailybarca

Dark, mobile-first Barca daily. Cards on the phone, 4-up grid on desktop. One story per card: headline, summary, supporting posts, source links. Each day is an edition. Yesterday lives in the archive.

Static site on GitHub to Vercel.

- index.html reads data/editions.json and the latest (or ?date=) edition file
- archive.html lists every edition
- New day = new data/YYYY-MM-DD.json + a line in data/editions.json

GitHub Action .github/workflows/daily.yml runs every morning. Connect dailybarca.com in Vercel when ready.
