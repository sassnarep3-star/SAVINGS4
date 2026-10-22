# COORDINATION.md — Shared Task Board

Session ID for this session: `674b0fdc` (branch `arena/674b0fdc-savings4` — fixed by Arena; do not rename/switch)

| # | Task | Status | Owner | File scope |
|---|------|--------|-------|------------|
| 1 | Repo review + coordination setup | done | 674b0fdc | COORDINATION.md, README.md |
| 2 | Research: official rates/rules/bonuses — big national banks (HYSA + traditional) | done | 674b0fdc | docs/ (this branch only) |
| 3 | Return-on-deposit tables (incl. $250k FDIC max) + competitiveness analysis | done | 674b0fdc (claimed with #2) | site pages |
| 4 | Site creation (GitHub Pages, landing + subpages, dashboard) | done | 674b0fdc | index.html, pages, assets |
| 5 | Line-by-line verification, Flagged for Review page | done | 674b0fdc | flagged.html |
| 6 | Final integration, PR to main, merge, Pages deploy | in progress | 674b0fdc | all (integration) |

## Log
- 2026-10-22: Session 674b0fdc claimed tasks 1–6 on branch arena/674b0fdc-savings4 (single-session execution per user instruction "no manual input / work on your own"). Scopes non-overlapping with any other session (none listed).
- Verification rule: every table row links an official bank / FDIC / Federal Reserve source. Unverifiable values left blank + flagged.

- 2026-10-22: Tasks 2-5 done. Sources: official pages of Synchrony, Marcus/Goldman Sachs, Barclays, SoFi, Amex, Capital One, Ally, Wells Fargo, Chase, Citi, BofA; FDIC national rates + deposit-insurance pages; Federal Reserve 2026-09-16 implementation note. Full source list in methodology.html. Verification: every table row links its official source with as-of date; internal-link check passed (no broken links). Irregularities F1-F12 published in flagged.html (Capital One NaN APY; Citi/BofA APY unverified->blank; Chase ZIP-gated; Discover/Capital One FDIC aggregation; Wells conditional rate; SoFi Plus fee amount unstated; Barclays fee blank; AARP offer excluded).
