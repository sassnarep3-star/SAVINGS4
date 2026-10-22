# SAVINGS4 — Savings Account Research (Big National Banks) — Verified Oct 21–22, 2026

**Live site: https://sassnarep3-star.github.io/SAVINGS4/** — GitHub Pages (root `index.html` via Actions workflow `path:.`; detailed `docs/` site also at `/docs/`).

This repo is the result of **two parallel research sessions** (`4b134088-savings4` + `674b0fdc-savings4`) merged without discarding work, per `COORDINATION.md`.

Independent, zero-manual-input research on **the best savings account among big national banks** — institutions with a mobile app + strong security disclosures + full FDIC insurance. Every table row links to its **official verified source** (bank domain or fdic.gov) with an as-of date. If we can't confirm it officially, we leave it blank and flag it.

**Opening dates:** Oct 21, 2026 (docs site, `4b134088`) and Oct 22, 2026 (root site, `674b0fdc`) — Fed funds 3.75%–4.00% after Sep 16 hike.

## Two sites — one repo

| Site | Location | Entry | How published | When |
|---|---|---|---|---|
| **Detailed docs site** (docs) | `docs/` | `docs/index.html` | Standalone static (Settings Pages → /docs, or via Actions artifact) | 2026-10-21 |
| **Root site** (Actions) | repo root | `index.html` | `.github/workflows/pages.yml` uploads `path:.` to Pages | 2026-10-22 |

Both share the same headline findings; minor APY deltas reflect rendering time and whether an observed regional page is accepted as primary (disclosed in `flagged.html`).

## Headline findings (both sessions agree)

- **Highest flat unconditional APY:** **Synchrony 3.55%** (synchrony.com) — no minimum, no fee · Also **Marcus 3.50%** Oct 21 (marcus.com) + referral +1% 3 mo
- **Highest at $250k:** **Barclays Tiered 3.65%** on $250k–$1M tier (10/07/2026) — but single-owner $250k leaves interest uninsured; see FDIC strategy
- **FDIC:** $250,000 per depositor, per bank, per ownership **including interest** — joint = $500k; trusts/banks stack · National avg savings **0.37% Sep 21** / **0.38% Oct 19** (FDIC)
- **Big-branch yield trap:** Chase 0.01% / BofA 0.01–0.04% / Wells std 0.01% — on $250k that's $25–$100/yr vs **$8,875 at Synchrony**
- **Flagged:** Capital One renders “NaN APY” (rate taken from apply domain, flagged); Citi/BofA masked/placeholder → blank (flagged); Discover merged into Capital One May 18, 2025 (one $250k limit)

## What's inside

### `docs/` — detailed dashboard (session 4b134088, Oct 21)
- **Dashboard** (`docs/index.html`) — leaderboard $250k 1-yr interest: CIT 3.75% $9,375 / Barclays Tiered 3.65% $9,125 / Marcus 3.50% $8,750 vs Chase $25
- **Rates** (`docs/rates.html`) — sortable 15-row big-bank table: APY, min, fee, FDIC, category, bonus, official source per row
- **FDIC-Max Returns** (`docs/returns.html`) — $10k/$25k/$50k/$100k/$250k at 12 mo + 6-mo/CD life-span + calculator (open date Oct 21)
- **Bonuses & Rules** (`docs/bonuses.html`) — BOOST50 4.25% 6 mo (CIT), Barclays $200 to 10/31, Marcus +1% referral, Wells 3.25% promo + per-bank opening rules
- **Security & Apps** (`docs/security.html`) — FDIC math (single/joint/trust/2-bank), 12 app store links, BankFind, Discover+CapOne trap
- **Sources** (`docs/sources.html`) — 16 primary official sources dated + 6 secondary observed
- **Flagged** (`docs/flagged.html`) — 8 flagged items (Capital One NaN, Citi/BofA ZIP/Region, PNC ZIP, U.S. Bank CQB, Wells standard tiers, etc.)

### Root — clean research site (session 674b0fdc, Oct 22)
- `index.html` — Dashboard (kpi: Synchrony 3.55% / Barclays tiered 3.65% / FDIC 0.38% / $250k)
- `accounts.html` — All Accounts line-by-line (Category A HYSA + Category B branch, app/FDIC/security/bonus per row)
- `returns.html` — Returns By Deposit Size $1k–$250k over 6mo/1/3/5y + calculator
- `fdic.html` — Max FDIC Strategy (stay under $250k with interest, SoFi $3M Insured Deposit Program)
- `bonuses.html` — Bonuses & Promotions (only official-page bonuses, with deadlines)
- `methodology.html` — Methodology & Sources + Federal Reserve Sep 16 note
- `flagged.html` — Flagged for Review F1–F12 (NaN APY, unverified blanks, ZIP-gated, merged bank, etc.)

## Data
Machine-readable: `docs/data/savings.json` (15 banks, `apy`/`apyVerifiedDate`/`source`/`bonus`/`flag`) — verified Oct 21.

## Verification
- **Every row links an official bank / FDIC / Federal Reserve source with an as-of date.** See `COORDINATION.md` logs + per-page Sources+Methodology.
- **No hallucinations:** unverifiable values left blank and published on `flagged.html` (both root + docs), with links for manual review.
- FDIC: [$250k per depositor per bank per category](https://www.fdic.gov/resources/deposit-insurance/understanding-deposit-insurance) + [Deposits at a Glance](https://www.fdic.gov/resources/deposit-insurance/brochures/deposits-at-a-glance). National avg: [Oct 19 2026](https://www.fdic.gov/national-rates-and-rate-caps) / [Sep 21 2026](https://www.fdic.gov/national-rates-and-rate-caps/national-rates-and-rate-caps-september-2026).
- Research only — not financial advice.

## Coordination
Protocol in `COORDINATION.md` — two parallel sessions on non-overlapping scopes, merged via git with conflict resolution logged. See Log + Final Integration Checklist there.

## Deploy
```bash
# docs site locally
npx serve docs
# root site locally (same static files)
python3 -m http.server 8000
# Pages deploys automatically on push to main via .github/workflows/pages.yml (path: .)
```

Live URL after deploy: https://sassnarep3-star.github.io/SAVINGS4/
