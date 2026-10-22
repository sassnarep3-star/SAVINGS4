# SAVINGS4 — U.S. National Bank Savings Research & Maximum FDIC Dashboard

**Live GitHub Pages Dashboard:** <https://sassnarep3-star.github.io/SAVINGS4/>  
**Assumed Account Opening & Verification Date:** `2026-10-22` (UTC) · **Applicant Context:** `New York City, NY, US`

---

## Overview

`SAVINGS4` is an independent, reproducible primary research dashboard evaluating **18 savings accounts across 16 distinct FDIC-insured U.S. national banking charters** ($43.5B to $4.09T in consolidated commercial bank assets per the Federal Reserve release). Small local banks, non-bank fintech sweeps, and credit unions are excluded.

### Core Research Standards
1. **100% Primary Official Sources Only:** Every single table row links directly to an official `.gov` regulator (`fdic.gov`, `federalreserve.gov`) or the chartered bank's own first-party disclosure domain (`openbank.us`, `everbank.com`, `cit.com`, `sofi.com`, `banking.us.barclays`, `synchrony.com`, `marcus.com`, `usbank.com`, `americanexpress.com`, `capitalone.com`, `ally.com`, `pnc.com`, `wellsfargo.com`, `chase.com`, `bankofamerica.com`, `citi.com`). Zero third-party rate aggregators or blogs are permitted.
2. **Strict Non-Hallucination Policy:** Where a bank's live official page masks rates behind stateful ZIP sessions or unrendered tokens (`Bank of America` `$XXXX` placeholder; `Citibank` `:BLUE_AccSavings_Rate%` token & NY Accelerate exclusion; `PNC` geo-block in NYC), numeric values remain strictly `null` / blank and are logged on **[Flagged for Review](pages/flagged.html)**.
3. **Deterministic Multi-Horizon Compounding (`2026-10-22`):** Exact calendar day counts (`92d` 3m, `182d` 6m, `365d` 1y, `1,096d` 3y, `1,826d` 5y) compute compound interest, promotional boost transitions, and single-owner `$250,000.00` principal headroom ceilings across `$1,000`–`$500,000` deposits.

---

## Multi-Page Site Architecture

- **[Overview (`index.html`)](index.html)** — Executive KPIs, national APY bar comparison, interactive deposit & lifespan calculator, and top national HYSA shortlist.
- **[National Banks Directory (`pages/accounts.html`)](pages/accounts.html)** — Searchable, filterable comparison of all 18 national accounts with Federal Reserve asset ranks, FDIC certificate IDs, base/promo APYs, minimums, fees, and waivers.
- **[Returns & FDIC Plan (`pages/returns.html`)](pages/returns.html)** — Interactive calculator + full multi-horizon tables (`$1k`–`$500k` × `3m`–`5y`), exact single-owner principal ceilings (`P + I ≤ $250,000`), and multi-charter `$250k` / `$500k` / `$1.0M` allocations.
- **[Bonuses & Promotions (`pages/bonuses.html`)](pages/bonuses.html)** — All 6 active national savings promotions (`Openbank`, `SoFi`, `CIT BOOST50`, `Barclays $200`, `Marcus Referral`, `Chase $100/$200`), all-in 12-month dollar comparisons, and blank unconfirmed offer tracking.
- **[Lifespan & Rate Cycle (`pages/lifespan.html`)](pages/lifespan.html)** — Short (`3m–6m`) vs long (`1y–5y`) competitiveness against `2026-10-19` FDIC National Rates (`0.38%` avg / `4.63%` cap) and `2026-09-17` FOMC `3.75%–4.00%` target range.
- **[App, Security & Rules (`pages/protection.html`)](pages/protection.html)** — Mobile apps, published MFA/passkey security controls, FDIC ownership multipliers (`$250k` single / `$500k` joint / `$1.25M` POD trust), shared-charter traps, and account opening rules.
- **[Flagged for Review (`pages/flagged.html`)](pages/flagged.html)** — Complete register of blank unconfirmed fields, bank site rendering defects, geo-blocks, and repository audit findings (`AUDIT-ERR-01`..`07`).
- **[Sources & Methodology (`pages/sources.html`)](pages/sources.html)** — Full 46-source primary evidence ledger, equations, CSV/JSON exports, and preserved multi-session artifacts (`audit/`, `research/`, `docs/`, `previous/`).

---

## Reproducible Build & Verification

```bash
python3 audit/compute_returns.py   # Regenerate audit/return-matrices.json
python3 scripts/build.py           # Build static Pages outputs & CSV export
python3 audit/verify_site.py       # Run unit tests, link checks, blank-field checks & repo-wide official-URL audit
```
