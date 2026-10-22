"""Illustrative models, not bank quotes. APY inputs are percentages."""
from datetime import date
from math import floor
OPENED = date(2026, 10, 22)
HORIZONS = [(3,date(2027,1,22)),(6,date(2027,4,22)),(12,date(2027,10,22))]
LIMIT = 250_000
RESERVE = 1

def factor(apy, days):
    if apy is None or apy < 0 or days < 0:
        raise ValueError('Need a verified nonnegative APY and nonnegative days')
    return (1 + apy / 100) ** (days / 365)

def interest(principal, apy, days):
    return principal * (factor(apy, days) - 1)

def headroom_principal(apy, days, bonus_reserve=0, existing=0):
    """Floor to cents, $1 reserve; reserve bonus as if received on day zero.

    Conditional upper bound under constant APY, not a coverage guarantee.
    """
    return max(0, floor(((LIMIT - RESERVE - existing) / factor(apy,days) - bonus_reserve)*100)/100)

def referral_factor(days):
    """Scenario only: rate boost starts Oct 23 for 3 calendar months (92 days).
    Standard 3.50%, promotional APY 4.50%; no referral link is assumed available.
    """
    boosted = min(max(days - 1, 0),92)
    return factor(4.5, boosted)*factor(3.5,days-boosted)
