# COORDINATION.md — Multi-Session Shared Task Board & Integration Log

> **Repository:** `sassnarep3-star/SAVINGS4` · **Reference / Account Opening Date:** `2026-10-22` (UTC) · **User Context:** New York City, NY, US
>
> All four Arena sessions (`674b0fdc`, `4b134088`, `f025ed43`, and `339c96e1`) operated concurrently on their respective Arena session branches and integrated non-destructively onto `main`. Every session's research artifacts, scripts, datasets, and pages are preserved without discarding prior work.

---

## All Parallel Sessions & File Ownership Registry

| Session ID | Branch | PR / Merge Commit | Claimed & Preserved File Scopes | Status |
|---|---|---|---|---|
| `674b0fdc` | `arena/674b0fdc-savings4` | [PR #1](https://github.com/sassnarep3-star/SAVINGS4/pull/1) (`94b7ad9`) | Preserved intact at `previous/root/**` and `previous/coordination/**` | `done` (merged) |
| `4b134088` | `arena/4b134088-savings4` | [PR #2](https://github.com/sassnarep3-star/SAVINGS4/pull/2) (`e174205`) | Preserved at `docs/**` (reconciled for official-only links & verified rates in `docs/data/savings.json`) | `done` (merged) |
| `f025ed43` | `arena/f025ed43-savings4` | [PR #3](https://github.com/sassnarep3-star/SAVINGS4/pull/3) (`a74e2cc`) | `research/**`, `data/**`, `scripts/**`, `assets/**`, `pages/**`, `index.html`, `.github/workflows/pages.yml` | `done` (merged) |
| `339c96e1` | `arena/339c96e1-savings4` | [PR #5](https://github.com/sassnarep3-star/SAVINGS4/pull/5) (`2d722ec`) | Non-overlapping `audit/**`, `categories/**` + line-by-line audit & unified 18-account/16-charter expansion across `data/**`, `scripts/**`, `index.html`, `pages/**`, `docs/**`, `README.md`, `COORDINATION.md` | `done` (merged & deployed) |

---

## Session `339c96e1` — Final Line-by-Line Verification & Unified Integration Plan

| Task ID | Task Description | Status | Owning Session | File Scope |
|---|---|---|---|---|
| `T1` | Repository audit & multi-session coordination setup | `done` | `339c96e1` (reconciled with `674b0fdc`, `4b134088`, `f025ed43`) | `COORDINATION.md` |
| `T2` | Sibling branch work preserved in full (`previous/root/**`, `docs/**`, `research/**`, `data/**`, `scripts/**`, `pages/**`) | `done` | `674b0fdc`, `4b134088`, `f025ed43` | `previous/**`, `docs/**`, `research/**`, `data/**`, `assets/**`, `pages/**`, `scripts/**` |
| `T3` | Line-by-line official source verification & primary regulatory/bank rate audit across 18 national accounts / 16 FDIC charters + cross-audit of PR #1, PR #2, PR #3, and PR #4 | `done` | `339c96e1` | `audit/verified-banks.json`, `audit/regulatory-benchmarks.json`, `audit/verification-log.md` |
| `T4` | Return-on-investment matrices across deposit tiers ($1k, $10k, $25k, $50k, $100k, $240k, $250k single-owner FDIC max, $500k joint/multi-bank max) and multi-horizon lifespans (3m, 6m, 1y, 3y, 5y) from opening date `2026-10-22` | `done` | `339c96e1` | `audit/return-matrices.json`, `audit/compute_returns.py` |
| `T5` | Unified 18-account expansion of `data/**` + `scripts/**` + 8-category dashboard + remediation of prior-session discrepancies (`AUDIT-ERR-01`..`07`) | `done` | `339c96e1` | `data/**`, `scripts/**`, `assets/**`, `index.html`, `pages/**`, `categories/**`, `docs/**`, `audit/verify_site.py` |
| `T6` | Full test suite (`15` unit tests + `audit/verify_site.py`), reproducible Pages build, PR #5 to `main`, immediate merge, and live GitHub Pages deployment confirmation | `done` | `339c96e1` | `README.md`, `.nojekyll`, `COORDINATION.md`, `.github/workflows/pages.yml` |

### Final PR, Merge & Live GitHub Pages Verification (`339c96e1`)

- **Pull Request:** <https://github.com/sassnarep3-star/SAVINGS4/pull/5> — **MERGED** (`2026-10-22T00:34:08Z`), merge commit `2d722ec88a3d625df188726b28ad66990bc1f08a`.
- **CI Verification Runs:** PR #5 check <https://github.com/sassnarep3-star/SAVINGS4/actions/runs/39700430101> (`success`) & `main` push check <https://github.com/sassnarep3-star/SAVINGS4/actions/runs/39700473603> (`success`) — all 15 unit tests, 36-page local link/fragment check, zero-aggregator scan, and byte-for-byte Pages reproducibility checks passed.
- **Live GitHub Pages Deployment:** Build `1304011293` reported `status: "built"`, `error: null` for commit `2d722ec88a3d625df188726b28ad66990bc1f08a` (`2026-10-22T00:34:29Z`). Fetched and verified live in production at <https://sassnarep3-star.github.io/SAVINGS4/> and <https://sassnarep3-star.github.io/SAVINGS4/pages/flagged.html>.

### Cross-Session Coordination & Audit Notes (`339c96e1`)

- **2026-10-22T00:05Z (`339c96e1`)**: Inspected `origin/main` (`04fd3ab`, containing 10-byte `# SAVINGS4` in `README.md`, missing trailing EOF newline) and discovered active sibling branches `arena/674b0fdc-savings4` and `arena/f025ed43-savings4`. Claimed non-overlapping scopes `audit/**`, `categories/**`, `static/**`.
- **2026-10-22T00:16Z (`339c96e1`)**: Completed independent primary official verification across `fdic.gov`, `federalreserve.gov`, and 15 national bank official domains (`eaa1c86`), then merged `origin/main` (`a74e2cc`, incorporating PR #1, PR #2, and PR #3) cleanly without discarding any sibling file.
- **Line-by-Line Audit Resolution for `f025ed43`'s Open Prior-Session Flag**: Session `f025ed43` noted at merge time that *"full independent re-verification of every prior row is incomplete"*. Session `339c96e1` completed that full line-by-line verification across all prior snapshots (`previous/root/**`, `docs/**`, and `data/**`), identifying and resolving:
  1. `AUDIT-ERR-01`: Removed third-party aggregator links (`nerdwallet.com`, `banksparency`) in `docs/data/savings.json` (`citibank-accelerate`) and replaced unconfirmed `3.00%` quote with `null` / blank (`:BLUE_AccSavings_Rate%` unauthenticated placeholder + NY state exclusion).
  2. `AUDIT-ERR-02`: Reconciled Capital One 360 Performance Savings (`3.10%` in `docs/data/savings.json` vs `3.20%` in official Truth-in-Savings disclosure `3.1540%` rate / `3.20% APY`).
  3. `AUDIT-ERR-03`: Corrected FOMC `+25 bps` hike (`3.75%–4.00%`) date from `Sep 16, 2026` to exact official Federal Reserve date **September 17, 2026**.
  4. `AUDIT-ERR-04`: Expanded root structured dataset from 12 products to **17 national bank savings accounts across 16 FDIC charters**, adding missing top-yielding large national commercial banks **Openbank by Santander** (`#29`, `$104.0B`, `4.00%` std / `4.35%` 6-mo boost), **SoFi Bank, N.A.** (`#43`, `$56.8B`, `3.30%` w/ DD / `4.40%` 6-mo boost + `$50/$400` DD bonus), **CIT Bank / First Citizens** (`#18`, `$236.3B`, `3.75%` `≥$5k` / `4.25%` `BOOST50`), **EverBank, N.A.** (`#48`, `$46.7B`, `4.20%` new accts), and **U.S. Bank Smartly Savings** (`#6`, `$705.6B`, `0.05%` std / up to `3.50%` relationship tier), plus verified NYC rate sheets (`rdny1.pdf` `0.01%` + `$100/$200` bonus for Chase; `3.25%` ongoing new-customer `≥$25k` addenda rate for Wells Fargo; `$200` bonus expiring `10/31/2026` for Barclays Tiered).

---

## Preserved Session Log — `arena-f025ed43` ([PR #3](https://github.com/sassnarep3-star/SAVINGS4/pull/3))

Session: `arena-f025ed43` · reference date: 2026-10-22 (UTC).

The Arena session branch is fixed at `arena/f025ed43-savings4`; all work and the integration PR use this branch rather than creating a separate session branch. No other claims existed when this board was created.

| Task | Status | Owner | File scope |
|---|---|---|---|
| Official-source research and evidence capture | done | arena-f025ed43 | research/**, data/** |
| Dashboard, category pages, calculations, tests | done | arena-f025ed43 | index.html, assets/**, pages/**, scripts/**, package.json, package-lock.json, README.md, .gitignore |
| Final integration, source recheck, Pages publication | done | arena-f025ed43 | COORDINATION.md, .github/** |

### Activity log (`arena-f025ed43`)

- 2026-10-22: Inspected repository (only a one-line README). No existing tasks, implementation, or evidence. Claimed the scopes above before starting. Research must leave unavailable official values blank and flag them. No banking credentials or personal input will be requested.
- 2026-10-22: Initial claim push required pulling `main` because the session branch did not yet exist on origin; claim then pushed successfully. No conflicts or other sessions' changes encountered.
- 2026-10-22: Research transcribed to `data/accounts.json`, `data/sources.json`, `data/flags.json`; row-by-row decisions in `research/VERIFICATION.md`. 12 products / 11 bank groups, 28 official evidence records. Official source families: FDIC, Marcus, Barclays, Ally, American Express, Synchrony, Capital One/Discover, Chase, Bank of America, Wells Fargo, Citi and PNC. All individual URLs and relevant excerpts are in the ledger and site Sources page.
- 2026-10-22: Built seven static pages with local assets, CSV/JSON downloads, local account filters, accessible empty-field labels, published calculation contract and 16 review items. Missing rates/promotions/eligibility remain blank. Scope is a bounded national-bank shortlist, not a complete market census; no accounts opened.
- 2026-10-22: Source review found Capital One NaN / older disclosure, Synchrony conflicting rates, Discover redirect and insurance aggregation, Barclays top-tier headroom issue, location-gated Chase/BofA/Citi/Wells/PNC rates, incomplete security or eligibility and inconsistent marketing benchmarks. Published all on Flagged for Review; these do not block publication.
- 2026-10-22: Initial tests caught bank-group count (corrected to 11) and missing machine-readable read date (added). All 13 automated tests now pass: source/reference integrity, every table row has an official source, internal URLs/fragments, empty CSV values, page structure, model horizons/APY/headroom/referral and no external runtime dependencies.
- 2026-10-22: Browser smoke tested all seven pages at 1440px and 390px. Search, category/status filters, no-results message and zero JS exceptions confirmed.
- 2026-10-22: Opened integration PR https://github.com/sassnarep3-star/SAVINGS4/pull/3 targeting main and merged as `a74e2cc`, followed by documentation PR https://github.com/sassnarep3-star/SAVINGS4/pull/4 (`fa767c8`) confirming live Pages deployment at `https://sassnarep3-star.github.io/SAVINGS4/` and preserving PR #1 (`previous/root/**`, `previous/coordination/**`) and PR #2 (`docs/**`).
- **2026-10-22 (`339c96e1` Final Integration PR #5)**: Opened [PR #5](https://github.com/sassnarep3-star/SAVINGS4/pull/5) targeting `main`, merged `fa767c8` cleanly retaining `ee58c2e`'s full-tree link check across all 35+ HTML files alongside the expanded 18-account / 16-FDIC-charter national dataset and zero-aggregator repo audit.
