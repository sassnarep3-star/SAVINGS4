# Savings4

Official-source savings research and a dependency-free static dashboard.

**Site:** https://sassnarep3-star.github.io/SAVINGS4/  
**Research / modeled opening date:** October 22, 2026 (UTC). This is a dated snapshot, not a live rate feed.

## What is included

- 12 product entries across 11 major bank groups, with national digital and branch-bank options.
- Official evidence ledger with publisher dates, read dates, selected evidence and manual-review links.
- Account comparison, opening requirements, fees, mobile/security evidence, confirmed promotion terms.
- Illustrative 3-, 6- and 12-month returns for multiple deposit sizes; conditional FDIC headroom and multi-bank examples.
- Clearly labeled **Flagged for Review** page for missing rates, conflicting pages, eligibility and geography gaps.
- Downloadable CSV and JSON. Unverified values stay null/empty—not guessed or replaced by zero.

This is a bounded shortlist, not a complete bank census or a claim to have found the highest APY in the entire market. Variable-rate calculations are scenarios, not official promises or personal financial advice. No accounts were opened.

## Run locally

Python 3.10+; no runtime dependencies, package installation, keys or user input required.

```sh
python3 scripts/build.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 -m http.server 8000 --bind 0.0.0.0 --directory _site
```

Optional aliases: `npm run build`, `npm test`, `npm run check`.

## Source of truth

- `data/accounts.json`: confirmed fields, nulls, source IDs and review flags.
- `data/sources.json`: official URLs, selected passages/transcriptions, dates and limitations.
- `data/flags.json`: published irregularities and unresolved facts.
- `research/VERIFICATION.md`: row-by-row research decisions and boundaries.
- `scripts/model.py`: transparent illustrative math.
- `scripts/build.py`: static HTML/CSV generator.
- `scripts/test_site.py`: evidence integrity, models, table-row sources, exports and internal-link/fragment checks.
- `COORDINATION.md`: task ownership, review and publication record.

Build output is `_site/`, ignored by Git. All assets are local; no third-party fonts, trackers, live bank requests or personal-data collection in the browser. Filters work locally with JavaScript; content is server-rendered static HTML and remains readable without it.

## Publish

GitHub Actions builds and validates on PRs and pushes to the session branch. Only successful builds on `main` deploy to GitHub Pages using the official Pages artifact workflow. Repository Pages must use the GitHub Actions build type. Published links are relative and work under `/SAVINGS4/`.

Official external pages were read in the research session; automated tests check internal links and evidence references, not the continuing truth or worldwide availability of external bank pages. Re-read official evidence before updating rates and both date types. Never silently roll forward the research date.
