# Line-by-Line Official Source Verification & Repository Audit Log (`339c96e1`)

- **Audit Session:** `339c96e1` (`arena/339c96e1-savings4`)
- **Assumed Account Opening Date:** `2026-10-22` (UTC)
- **Applicant Geographic Context:** `New York City, NY, US`
- **Strict Non-Hallucination Standard:** Every table row across the repository and site must cite a primary official source (`*.gov` or the chartered bank's own first-party domain). Where a live primary official source masks a value behind stateful ZIP/cookie sessions or server-side placeholders, the value is left strictly blank (`—` / `null`) and flagged on the **Flagged for Review** page.

---

## Part 1 — Federal Regulatory & Benchmark Verification (`2026-10-22`)

| Item | Verified Official Value | Official As-Of / Effective Date | Primary Official Source URL | Verification Status |
|---|---|---|---|---|
| Standard FDIC Deposit Insurance Limit | **$250,000** per depositor, per insured bank, per ownership category (*principal + accrued interest combined*) | Current statutory rule (verified `2026-10-22`) | https://www.fdic.gov/resources/deposit-insurance/brochures/deposits-at-a-glance | **Verified** |
| Joint Account FDIC Limit (2 Co-Owners) | **$500,000** combined ($250,000 per co-owner) | Current statutory rule (verified `2026-10-22`) | https://www.fdic.gov/resources/deposit-insurance/brochures/deposits-at-a-glance | **Verified** |
| Trust / POD Beneficiary FDIC Limit | **$250,000 per eligible beneficiary**, capped at **$1,250,000 per owner** at 5+ beneficiaries | Effective `2024-04-01` (verified `2026-10-22`) | https://www.fdic.gov/resources/deposit-insurance/brochures/deposits-at-a-glance | **Verified** |
| FDIC National Average — Savings | **0.38% APY** (National Rate Cap: **4.63%**) | `2026-10-19` | https://www.fdic.gov/national-rates-and-rate-caps | **Verified** |
| FDIC National Average — Money Market & CDs | MMA **0.63%**; 3m CD **1.14%**; 6m CD **1.39%**; 12m CD **1.76%**; 36m CD **1.39%**; 60m CD **1.41%** | `2026-10-19` | https://www.fdic.gov/national-rates-and-rate-caps | **Verified** |
| FOMC Target Federal Funds Rate Range | **3.75%–4.00%** (+25 bps increase) | `2026-09-17` | https://www.federalreserve.gov/monetarypolicy/openmarket.htm | **Verified** |
| Federal Reserve National Bank Asset Rankings | Consolidated assets & national rank for all U.S. commercial banks (#1 Chase $4.09T through #51 Barclays DE $43.5B) | Data as of `2026-06-30` (posted `2026-10-02`) | https://www.federalreserve.gov/releases/lbr/current/ | **Verified** |

---

## Part 2 — Repository Audit of Existing Merged Commits on `origin/main` (`e174205`)

Before publishing unified tables, Session `339c96e1` audited all files introduced on `origin/main` by PR #1 (`674b0fdc`) and PR #2 (`4b134088`) line by line against live official sources:

| Finding ID | Affected Repo File(s) on `origin/main` | Discrepancy Identified | Official Evidence & Resolution Applied |
|---|---|---|---|
| `AUDIT-ERR-01` | `docs/data/savings.json` (`citibank-accelerate`) | Cites third-party aggregator URL `https://www.nerdwallet.com/banking/learn/citibank-bonus` as `bonusSource` and `"citi.com via banksparency — 3.00% APY"` in `sourceLabel`, violating the official-sources-only rule. | Removed all third-party aggregator links; set live APY to `null` / blank with `UNVERIFIED — Blank` flag because `citi.com/banking/savings-account` renders `:BLUE_AccSavings_Rate%` unauthenticated AND `citi.com/banking/compare-bank-accounts` excludes `NY` from Citi Accelerate Savings. |
| `AUDIT-ERR-02` | `docs/data/savings.json` vs `accounts.html` (`capital-one`) | Internal contradiction inside `origin/main`: `docs/data/savings.json` listed **3.10% APY** (`2026-10-12`), whereas `accounts.html` listed **3.20% APY** (`2026-10-21`). | Verified directly against Capital One's official Truth-in-Savings Account Disclosures (`https://www.capitalone.com/bank/disclosures/savings-accounts/online-performance-savings-account/`): exact interest rate **3.1540%** / **3.20% APY**. Reconciled `docs/data/savings.json` and root tables to **3.20% APY** and logged the main product page's `NaN APY` server-render defect (`IRR-CAP1-01`). |
| `AUDIT-ERR-03` | `docs/data/savings.json`, `COORDINATION.md`, `methodology.html` | Stated FOMC rate hike date as **"Sep 16, 2026"**. | Official Federal Reserve Open Market Operations table (`https://www.federalreserve.gov/monetarypolicy/openmarket.htm`) lists exact date **September 17, 2026** (`+25 bps` to `3.75%–4.00%`). Updated across data and documentation. |
| `AUDIT-ERR-04` | Root site (`index.html`, `accounts.html`, `returns.html`) & `docs/` | Omitted two top-yielding large national commercial banks (**Openbank by Santander**, #29 U.S. bank, $104.0B assets, **4.00% standard / 4.35% 6-mo boosted APY**; **EverBank, N.A.**, #48 U.S. bank, $46.7B assets, **4.20% new-account APY**), and root `index.html` also omitted **CIT Bank / First Citizens** (#18 U.S. bank, $236.3B assets, **3.75% standard / 4.25% `BOOST50` 6-mo APY**). | Added all verified national bank entries to canonical JSON (`audit/verified-banks.json`), return matrices (`audit/return-matrices.json`), `docs/data/savings.json`, and all root category pages. |
| `AUDIT-ERR-05` | `accounts.html` (`barclays-tiered`) & `docs/data/savings.json` (`chase`) | `accounts.html` reported `"None listed"` for Barclays Tiered Savings bonus (missing active **$200** bonus expiring `10/31/2026` on `banking.us.barclays/tiered-savings.html`), while `docs/data/savings.json` reported `"savings not bonused"` for Chase (missing active **$100 / $200** Chase Savings bonus expiring `01/27/2027` at `account.chase.com/consumer/banking/savingsoffer`). | Added verified bonus terms, hold durations (120 days Barclays; 90 days Chase), and official URLs to both datasets. |
| `AUDIT-ERR-06` | Root HTML vs `docs/` HTML | Split-brain UX between root `/` and `/docs/` with unlinked navigation and divergent numbers, plus initial `04fd3ab` `README.md` (`# SAVINGS4` with missing trailing EOF newline). | Preserved every single file created by `674b0fdc` and `4b134088` while upgrading root `/` to a clean, unified multi-page category dashboard synchronized from one verified source of truth and cross-linking `docs/`. |

---

## Part 3 — Line-by-Line Verification Matrix for All 17 National Bank Entries

| # | Institution & Account | Fed Rank & Assets (`06/30/2026`) | FDIC Cert # | Verified Standard APY | Verified Promo / Tier Rate | Official Effective Date | Min Open | Monthly Fee | Official Primary URLs |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Openbank by Santander** — High Yield Savings | #29 ($103,965M) | `#29950` | **4.00%** | **4.35%** (6-mo `+0.35%` new-customer boost) | `2026-10-22` | $500 | $0 | https://www.openbank.us/banking/high-yield-savings-account/ |
| 2 | **EverBank, N.A.** — Performance® Savings | #48 ($46,691M) | `#34775` | **4.20%** *(new accts)* | — | `2026-10-16` | $0 | $0 | https://www.everbank.com/banking/performance-savings |
| 3 | **CIT Bank (First Citizens)** — Platinum Savings | #18 ($236,317M) | `#11063` | **3.75%** (`≥$5k`) / **0.25%** (`<$5k`) | **4.25%** (`BOOST50` `+0.50%` for 6 mos through `12/15/2026`) | `2026-07-01` (`BOOST50` `2026-09-29`) | $100 | $0 | https://www.cit.com/cit-bank/bank/savings/platinum-savings-account · https://www.cit.com/cit-bank/platinum-savings/boost |
| 4 | **Barclays Bank Delaware** — Tiered Savings | #51 ($43,454M) | `#57203` | **3.65%** (`$250k–$1M`) / **3.50%** (`<$250k`) | **+$200 cash bonus** (`≥$25k` for 120d; exp. `10/31/2026`) | `2026-10-07` | $0 | $0 | https://banking.us.barclays/tiered-savings.html |
| 5 | **Synchrony Bank** — High Yield Savings | FSB Charter *(see `IRR-FED-01`)* | `#27314` | **3.55%** | — | `2026-10-21` | $0 | $0 | https://www.synchrony.com/banking/products/hys-core |
| 6 | **Marcus by Goldman Sachs** — Online Savings | #5 ($758,788M) | `#33124` | **3.50%** | **4.50%** (`+1.00%` 3-mo referral boost) | `2026-10-21` | $0 | $0 | https://www.marcus.com/us/en/savings/high-yield-savings · https://www.marcus.com/us/en/savings/referrals |
| 7 | **U.S. Bank N.A.** — Bank Smartly® Savings | #6 ($705,555M) | `#6548` | **0.05%** *(standalone)* | **Up to 3.50%** (`≥$25k` CQB + Smartly Checking/Card) | `2026-10-21` | $25 | $5 *(waivable)* | https://www.usbank.com/bank-accounts/savings-accounts/bank-smartly-savings/savings-account-interest-rates.html |
| 8 | **SoFi Bank, N.A.** — Checking & Savings | #43 ($56,821M) | `#26881` | **3.30%** w/ DD (`0.80%` w/o DD) | **4.40%** (`+1.10%` 6-mo boost) + **$50/$400** DD bonus; **4.70%** SoFi Plus `≤$20k` | `2026-10-20` | $0 | $0 | https://www.sofi.com/banking/high-yield-savings-account/ · https://d32ijn7u0aqfv4.cloudfront.net/wp/wp-content/uploads/raw/SoFi-Bank-Rate-Sheet-October-20-2026.pdf |
| 9 | **Wells Fargo Bank, N.A.** — Platinum Savings | #4 ($1,907,928M) | `#3511` | **0.01%** *(standard)* | **3.25%** variable new-customer `≥$25k` tier (`0.05%` Premier rel.) | `2026-10-07` | $25 | $12 *(waived `≥$3.5k`)* | https://www.wellsfargo.com/savings-cds/rates/ · https://www.wellsfargo.com/fetch-pdf?documentName=Account+Addenda&subProductCode=ANY |
| 10 | **American Express National Bank** — HYSA | #21 ($213,946M) | `#27471` | **3.20%** | — | `2026-10-21` | $0 | $0 | https://www.americanexpress.com/en-us/banking/online-savings/account/ |
| 11 | **Capital One, N.A. (+ Discover)** — 360 Performance Savings | #7 ($662,157M) | `#4297` | **3.20%** (`3.1540%` rate) | — | `2026-10-21` *(disc. `2026-07-15`)* | $0 | $0 | https://www.capitalone.com/bank/disclosures/savings-accounts/online-performance-savings-account/ |
| 12 | **Barclays Bank Delaware** — Online Savings | #51 ($43,454M) | `#57203` | **3.20%** | — | `2026-10-07` | $0 | $0 | https://banking.us.barclays/online-savings.html |
| 13 | **PNC Bank, N.A.** — High Yield Savings® | #8 ($609,772M) | `#6384` | **3.15%** *(out-of-footprint only — ineligible in NYC)* | — | `2026-10-22` | $0 | $0 | https://www.pnc.com/en/personal-banking/banking/savings/high-yield-savings.html |
| 14 | **Ally Bank** — Savings Account | #23 ($188,184M) | `#57803` | **3.10%** | — | `2026-10-21` | $0 | $0 | https://www.ally.com/bank/online-savings-account/ |
| 15 | **JPMorgan Chase Bank, N.A.** — Chase Savings℠ | #1 ($4,091,315M) | `#628` | **0.01%** (`0.02%` Premier/CPC rel.) | **$100 / $200 cash bonus** (`$5k` / `$10k` held 90d; exp. `01/27/2027`) | `2026-10-16` | $0 | $5 *(waived `≥$300`)* | https://www.chase.com/content/dam/chase-ux/ratesheets/pdfs/rdny1.pdf · https://account.chase.com/consumer/banking/savingsoffer |
| 16 | **Bank of America, N.A.** — Advantage Savings | #2 ($2,654,645M) | `#3510` | **UNVERIFIED — Blank** *(masked `$XXXX` / HTTP 405; static NY sheet `0.01%` Reg. Savings)* | — | `2026-08-07` *(Fee Sched.)* | $100 | $8 *(waivable)* | https://www.bankofamerica.com/salesservices/deposits/resources/personal-schedule-fees/ · https://www.bankofamerica.com/content/ari-files/EXTE_NY.htm |
| 17 | **Citibank, N.A.** — Citi® Accelerate / Citi® Savings | #3 ($1,976,180M) | `#7213` | **UNVERIFIED — Blank** *(`:BLUE_AccSavings_Rate%` placeholder; NY excluded from Accelerate)* | — | `2026-10-21` *(footnote)* | $0 | $4.50 *(waivable)* | https://www.citi.com/banking/savings-account · https://www.citi.com/banking/compare-bank-accounts |
