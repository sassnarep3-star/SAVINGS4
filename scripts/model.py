"""Deterministic return & FDIC headroom models starting 2026-10-22 (UTC)."""
from datetime import date
from math import floor

OPENED = date(2026, 10, 22)
HORIZONS = [
    (3, date(2027, 1, 22)),
    (6, date(2027, 4, 22)),
    (12, date(2027, 10, 22)),
    (36, date(2029, 10, 22)),
    (60, date(2031, 10, 22)),
]
HORIZONS_SHORT = HORIZONS[:3]
LIMIT = 250_000
JOINT_LIMIT = 500_000
RESERVE = 1


def factor(apy, days):
    if apy is None or apy < 0 or days < 0:
        raise ValueError("Need a verified nonnegative APY and nonnegative days")
    return (1 + apy / 100) ** (days / 365)


def interest(principal, apy, days):
    return principal * (factor(apy, days) - 1)


def effective_base_apy(account, principal):
    """Return tier-adjusted base APY for a given deposit size (None if unverified or below minimum to open)."""
    if account["apy"] is None:
        return None
    if account["minimum"] and principal < account["minimum"]:
        return None
    if account.get("minTier") and principal < account["minTier"] and account.get("belowTierApy") is not None:
        return account["belowTierApy"]
    if account["id"] == "barclays" and principal >= 250_000:
        return 3.65
    return account["apy"]


def promo_growth_factor(account, principal, days):
    """Growth factor incorporating verified promotional boost window if eligible at `principal`."""
    base = effective_base_apy(account, principal)
    if base is None:
        return None
    promo = account.get("promoApy")
    pmonths = account.get("promoMonths") or 0
    if not promo or pmonths <= 0:
        return factor(base, days)
    if account.get("minTier") and principal < account["minTier"]:
        return factor(base, days)
    promo_days_cap = {3: 92, 6: 182, 12: 365, 60: 1826}.get(pmonths, int(round(pmonths * 30.4375)))
    pdays = min(days, promo_days_cap)
    return factor(promo, pdays) * factor(base, days - pdays)


def promo_interest(account, principal, days):
    gf = promo_growth_factor(account, principal, days)
    if gf is None:
        return None
    return principal * (gf - 1)


def headroom_principal(apy, days, bonus_reserve=0, existing=0):
    """Floor to cents with $1 safety reserve so (P + bonus_reserve) * growth <= $249,999.00."""
    return max(0, floor(((LIMIT - RESERVE - existing) / factor(apy, days) - bonus_reserve) * 100) / 100)


def referral_factor(days):
    """Marcus referral scenario: Oct 22 at 3.50%, 92 days at 4.50%, remaining days at 3.50%."""
    boosted = min(max(days - 1, 0), 92)
    return factor(4.5, boosted) * factor(3.5, days - boosted)
