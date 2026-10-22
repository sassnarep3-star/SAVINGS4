#!/usr/bin/env python3
"""
Deterministic, tier-exact savings return calculation engine for SAVINGS4.
Account Opening Date: 2026-10-22 (UTC)
Strictly preserves null/blank values when official primary APY is unverified.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

OPEN_DATE = "2026-10-22"

DEPOSIT_TIERS: List[int] = [1000, 10000, 25000, 50000, 100000, 250000, 500000]

HORIZONS: List[Dict[str, Any]] = [
    {"key": "3m", "label": "3 Months", "years": 0.25, "months": 3, "maturityDate": "2027-01-22"},
    {"key": "6m", "label": "6 Months", "years": 0.50, "months": 6, "maturityDate": "2027-04-22"},
    {"key": "1y", "label": "1 Year", "years": 1.00, "months": 12, "maturityDate": "2027-10-22"},
    {"key": "3y", "label": "3 Years", "years": 3.00, "months": 36, "maturityDate": "2029-10-22"},
    {"key": "5y", "label": "5 Years", "years": 5.00, "months": 60, "maturityDate": "2031-10-22"},
]


def resolve_tier_rates(account: Dict[str, Any], principal: float) -> Tuple[Optional[float], Optional[float], int, int, str]:
    """
    Returns (standard_apy_pct, promo_apy_pct, promo_months, cash_bonus_usd, note)
    for a specific deposit amount `principal` based solely on verified official rules.
    Returns (None, None, 0, 0, reason) if unverified or below minimum opening deposit.
    """
    aid = account["id"]
    if account["apyStatus"] == "unverified-blank":
        return (None, None, 0, 0, "Official APY unverified (geo-gated/masked)")

    min_open = account.get("minOpeningDepositNum") or 0
    if principal < min_open:
        return (None, None, 0, 0, f"Below ${min_open:,} minimum opening deposit")

    if aid == "openbank-hys":
        return (4.00, 4.35, 6, 0, "4.35% for 6 mos new customer, then 4.00% standard")
    if aid == "everbank-performance":
        return (4.20, 4.20, 0, 0, "4.20% new-account variable APY across all tiers")
    if aid == "cit-platinum":
        if principal >= 5000:
            return (3.75, 4.25, 6, 0, "≥$5,000 tier: 3.75% std / 4.25% w/ BOOST50 (6 mos)")
        return (0.25, 0.75, 6, 0, "<$5,000 tier: 0.25% std / 0.75% w/ BOOST50 (6 mos)")
    if aid == "barclays-tiered":
        base = 3.65 if principal >= 250000 else 3.50
        bonus = 200 if principal >= 25000 else 0
        return (base, base, 0, bonus, f"{base:.2f}% tier" + (" + $200 cash bonus (held ≥120d)" if bonus else ""))
    if aid == "synchrony-hys":
        return (3.55, 3.55, 0, 0, "3.55% flat variable APY")
    if aid == "marcus-osa":
        return (3.50, 4.50, 3, 0, "3.50% std; 4.50% for 3 mos w/ 1 referral")
    if aid == "usbank-smartly":
        # Standalone is 0.05%; Relationship APY shown for Smartly Checking + CQB tier
        if principal >= 25000:
            rel = 3.50
        elif principal >= 5000:
            rel = 2.00
        else:
            rel = 1.00
        return (0.05, rel, 60, 0, f"0.05% standalone; {rel:.2f}% w/ Smartly Checking relationship")
    if aid == "sofi-savings":
        bonus = 400 if principal >= 5000 else 50
        return (3.30, 4.40, 6, bonus, f"3.30% w/ DD (4.40% 6-mo boost) + ${bonus} DD bonus; 0.80% w/o DD")
    if aid == "wellsfargo-platinum-promo":
        if principal >= 25000:
            return (0.01, 3.25, 60, 0, "0.01% standard; 3.25% variable new-customer ≥$25k tier (eff. 10/07/2026)")
        return (0.01, 0.01, 0, 0, "Below $25k new-customer tier: 0.01% standard APY")
    if aid == "amex-hysa":
        return (3.20, 3.20, 0, 0, "3.20% flat variable APY")
    if aid == "capitalone-360":
        return (3.20, 3.20, 0, 0, "3.20% flat variable APY (official disclosure)")
    if aid == "barclays-online":
        return (3.20, 3.20, 0, 0, "3.20% flat variable APY")
    if aid == "pnc-hysa":
        return (3.15, 3.15, 0, 0, "3.15% out-of-footprint markets only (NOT available in NYC)")
    if aid == "ally-savings":
        return (3.10, 3.10, 0, 0, "3.10% flat variable APY")
    if aid == "chase-savings":
        bonus = 200 if principal >= 10000 else (100 if principal >= 5000 else 0)
        return (0.01, 0.01, 0, bonus, "0.01% standard APY" + (f" + ${bonus} new-money bonus (90d hold)" if bonus else ""))

    return (account.get("standardApy"), account.get("standardApy"), 0, 0, "")


def calc_ending_balance(
    principal: float,
    std_apy_pct: float,
    promo_apy_pct: float,
    promo_months: int,
    cash_bonus_usd: int,
    months: int,
    include_promo: bool,
) -> float:
    """
    Exact compound growth using Annual Percentage Yield definition:
      After y years at constant APY a, balance = P * (1 + a)^y.
      If a promotional APY applies for `promo_months` before reverting to `std_apy_pct`:
        promo_years = min(months, promo_months) / 12.0
        rem_years = max(0, months - promo_months) / 12.0
        balance = P * ((1 + promo_apy)**promo_years) * ((1 + std_apy)**rem_years) + eligible_bonus
    """
    std_r = std_apy_pct / 100.0
    if not include_promo:
        years = months / 12.0
        return principal * ((1.0 + std_r) ** years)

    promo_r = promo_apy_pct / 100.0
    p_m = min(months, promo_months)
    r_m = max(0, months - promo_months)
    bal = principal * ((1.0 + promo_r) ** (p_m / 12.0)) * ((1.0 + std_r) ** (r_m / 12.0))

    # Cash bonus eligibility hold periods:
    # - Barclays $200 requires 120 days (~4 mos -> credited by >=6m horizon)
    # - Chase $100/$200 requires 90 days (3 mos -> credited at >=3m horizon)
    # - SoFi $50/$400 requires 25-day DD window (~1 mo -> credited at >=3m horizon)
    if cash_bonus_usd > 0:
        if cash_bonus_usd == 200 and std_apy_pct in (3.50, 3.65):
            # Barclays 120-day hold requirement -> not yet earned at 90 days (3m)
            if months >= 6:
                bal += cash_bonus_usd
        else:
            if months >= 3:
                bal += cash_bonus_usd
    return bal


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    banks_data = json.loads((root / "audit" / "verified-banks.json").read_text())
    reg_data = json.loads((root / "audit" / "regulatory-benchmarks.json").read_text())

    accounts_out: List[Dict[str, Any]] = []
    single_fdic_optimal: List[Dict[str, Any]] = []

    for acct in banks_data["accounts"]:
        row_entry: Dict[str, Any] = {
            "id": acct["id"],
            "bank": acct["bank"],
            "product": acct["product"],
            "categoryGroup": acct["categoryGroup"],
            "nycEligible": acct["nycEligible"],
            "apyStatus": acct["apyStatus"],
            "apyDisplay": acct["apyDisplay"],
            "officialSourceUrl": acct["officialSourceUrl"],
            "fdicCert": acct["fdicCert"],
            "fdicBankFindUrl": acct["fdicBankFindUrl"],
            "tiers": {},
        }

        for dep in DEPOSIT_TIERS:
            std_apy, promo_apy, promo_mos, bonus_usd, tier_note = resolve_tier_rates(acct, dep)
            if std_apy is None:
                row_entry["tiers"][str(dep)] = {
                    "verified": False,
                    "note": tier_note,
                    "horizons": {h["key"]: None for h in HORIZONS},
                }
                continue

            h_map: Dict[str, Any] = {}
            for h in HORIZONS:
                end_std = calc_ending_balance(dep, std_apy, promo_apy or std_apy, promo_mos, bonus_usd, h["months"], False)
                end_promo = calc_ending_balance(dep, std_apy, promo_apy or std_apy, promo_mos, bonus_usd, h["months"], True)
                h_map[h["key"]] = {
                    "maturityDate": h["maturityDate"],
                    "standardEndingBalance": round(end_std, 2),
                    "standardInterestEarned": round(end_std - dep, 2),
                    "withPromoEndingBalance": round(end_promo, 2),
                    "withPromoTotalGain": round(end_promo - dep, 2),
                    "exceedsSingleFdicCapAtEndStd": end_std > 250000.00,
                    "exceedsSingleFdicCapAtEndPromo": end_promo > 250000.00,
                }

            row_entry["tiers"][str(dep)] = {
                "verified": True,
                "appliedStandardApyPct": std_apy,
                "appliedPromoApyPct": promo_apy,
                "promoMonths": promo_mos,
                "cashBonusUsd": bonus_usd,
                "note": tier_note,
                "horizons": h_map,
            }

        accounts_out.append(row_entry)

        # Compute exact max initial principal P_max for a Single Owner (0 beneficiaries)
        # so ending balance (principal + accrued interest + cash bonus) == $250,000.00 exactly.
        std_250, promo_250, pmos_250, bonus_250, _ = resolve_tier_rates(acct, 240000)
        if std_250 is not None:
            # Note: for Barclays Tiered, if P_max < $250,000, rate drops from 3.65% to 3.50%!
            growth_1y_std = (1.0 + std_250 / 100.0) ** 1.0
            growth_1y_promo = (
                ((1.0 + (promo_250 or std_250) / 100.0) ** (min(12, pmos_250) / 12.0))
                * ((1.0 + std_250 / 100.0) ** (max(0, 12 - pmos_250) / 12.0))
            )
            growth_3y_std = (1.0 + std_250 / 100.0) ** 3.0
            growth_5y_std = (1.0 + std_250 / 100.0) ** 5.0

            pmax_1y_std = round(250000.0 / growth_1y_std, 2)
            pmax_1y_promo = round((250000.0 - bonus_250) / growth_1y_promo, 2)
            pmax_3y_std = round(250000.0 / growth_3y_std, 2)
            pmax_5y_std = round(250000.0 / growth_5y_std, 2)

            single_fdic_optimal.append(
                {
                    "id": acct["id"],
                    "bank": acct["bank"],
                    "product": acct["product"],
                    "nycEligible": acct["nycEligible"],
                    "appliedStandardApyAtSub250kPct": std_250,
                    "appliedPromoApyAtSub250kPct": promo_250,
                    "cashBonusUsd": bonus_250,
                    "maxPrincipal1YrStd": pmax_1y_std,
                    "insuredInterest1YrStd": round(250000.0 - pmax_1y_std, 2),
                    "maxPrincipal1YrWithPromo": pmax_1y_promo,
                    "insuredGain1YrWithPromo": round(250000.0 - pmax_1y_promo, 2),
                    "maxPrincipal3YrStd": pmax_3y_std,
                    "insuredInterest3YrStd": round(250000.0 - pmax_3y_std, 2),
                    "maxPrincipal5YrStd": pmax_5y_std,
                    "insuredInterest5YrStd": round(250000.0 - pmax_5y_std, 2),
                    "full250kWithPodOrJoint1YrStdInterest": row_entry["tiers"]["250000"]["horizons"]["1y"]["standardInterestEarned"],
                    "full250kWithPodOrJoint1YrPromoGain": row_entry["tiers"]["250000"]["horizons"]["1y"]["withPromoTotalGain"],
                    "officialSourceUrl": acct["officialSourceUrl"],
                }
            )

    # Benchmark row for FDIC National Average Savings (0.38% APY as of Oct 19, 2026)
    fdic_avg_rate = reg_data["fdicNationalRates"]["products"][0]["nationalRatePct"]
    fdic_bench = {}
    for dep in DEPOSIT_TIERS:
        fdic_bench[str(dep)] = {
            h["key"]: {
                "maturityDate": h["maturityDate"],
                "endingBalance": round(dep * ((1.0 + fdic_avg_rate / 100.0) ** h["years"]), 2),
                "interestEarned": round(dep * ((1.0 + fdic_avg_rate / 100.0) ** h["years"]) - dep, 2),
            }
            for h in HORIZONS
        }

    out = {
        "openingDate": OPEN_DATE,
        "depositTiersUsd": DEPOSIT_TIERS,
        "horizons": HORIZONS,
        "fdicNationalAverageBenchmark038Pct": fdic_bench,
        "accounts": accounts_out,
        "singleOwnerZeroUninsuredOptimalDeposits": single_fdic_optimal,
    }

    out_path = root / "audit" / "return-matrices.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"Wrote {out_path} ({len(accounts_out)} accounts, {len(single_fdic_optimal)} FDIC-optimal rows).")


if __name__ == "__main__":
    main()
