# SAVINGS4 — Big-Bank Savings Research

Live site (GitHub Pages): **https://sassnarep3-star.github.io/SAVINGS4/** — built from `docs/` on `main`.

Independent research on **the best savings account among big national banks** — focused on large institutions with mobile apps, strong security, and full FDIC insurance. Every table row links to its **official verified source** (bank domain or fdic.gov) with a date. If we can't confirm it officially, we leave it blank and flag it — no hallucinations.

**Research date: October 21, 2026** — Fed funds 3.75%–4.00% (after Sep 16 hike); FDIC national average savings 0.37% Sep 21 / 0.38% Oct 19, 2026.

## What’s inside
- **Dashboard** (`docs/index.html`) — leaderboard: what $250k FDIC-max earns at each bank (leader: CIT 3.75% / Barclays Tiered 3.65% / Marcus 3.50%)
- **Rates** (`rates.html`) — sortable table: APY, minimums, fees, category, bonus, official source per row
- **FDIC-Max Returns** (`returns.html`) — $10k / $25k / $50k / $100k / $250k returns at 12 months + 6-mo/CD life-span comparison + interactive calculator
- **Bonuses & Rules** (`bonuses.html`) — BOOST50 4.25% (CIT), Barclays $200, Marcus referral +1%, Wells 3.25% promo, plus opening requirements
- **Security & Apps** (`security.html`) — FDIC $250k per depositor per bank per category (with joint/trust math), every bank’s app link + security disclosures + BankFind
- **Sources** (`sources.html`) — full ledger: 16 primary official sources (bank domains + fdic.gov) + secondary observed sources
- **Flagged for Review** (`flagged.html`) — items where static official page didn't render the rate (e.g., Capital One NaN JS bug) — published for you to re-check, non-blocking
- **Methodology** (`methodology.html`) — line-by-line verification process + formulas

## Data
Machine-readable: `docs/data/savings.json` — one object per bank with `apy`, `apyVerifiedDate`, `source`, `bonus`, `flag`, etc.

## Verification
- Every APY verified from official bank site or official PDF rate sheet (Chase). See `sources.html` + `docs/data/savings.json`.
- FDIC coverage $250k from [fdic.gov](https://www.fdic.gov/resources/deposit-insurance/understanding-deposit-insurance).
- National average 0.37% Sep 21 from [FDIC National Rates](https://www.fdic.gov/national-rates-and-rate-caps/national-rates-and-rate-caps-september-2026).
- Flagged / unverified items on `flagged.html` — not hidden.

## Coordination
Multi-session protocol lives in `COORDINATION.md` (sole session `4b134088-savings4` — all 7 tasks claimed and completed sequentially on branch `arena/4b134088-savings4`).

## Deploy
```bash
# site is static — open locally:
npx serve docs
# GitHub Pages: Settings → Pages → Source: Deploy from branch → Branch: main → Folder: /docs
```
