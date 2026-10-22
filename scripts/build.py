"""Build the unified, dependency-free static GitHub Pages research workspace."""
import csv
import html
import json
import shutil
from pathlib import Path
from model import (
    OPENED,
    HORIZONS,
    LIMIT,
    JOINT_LIMIT,
    factor,
    interest,
    effective_base_apy,
    promo_growth_factor,
    promo_interest,
    headroom_principal,
    referral_factor,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"

accounts = json.loads((ROOT / "data/accounts.json").read_text())
sources = json.loads((ROOT / "data/sources.json").read_text())
flags = json.loads((ROOT / "data/flags.json").read_text())
S = {s["id"]: s for s in sources}
MODELED = [a for a in accounts if a["modelEligible"]]
HYSA_LEADERS = [a for a in MODELED if a["apy"] >= 3.0]

E = lambda x: html.escape(str(x), quote=True)
M = lambda x: f"${x:,.2f}"
D = lambda x: f"${x:,.0f}"
P = lambda x: f"{x:.2f}%"

NAV = [
    ("index.html", "Overview", "◫"),
    ("pages/accounts.html", "National Banks (18)", "▤"),
    ("pages/returns.html", "Returns & FDIC Plan", "↗"),
    ("pages/bonuses.html", "Bonuses & Promotions", "◇"),
    ("pages/lifespan.html", "Lifespan & Rate Cycle", "◷"),
    ("pages/protection.html", "App, Security & Rules", "⊙"),
    ("pages/flagged.html", "Flagged for Review", "⚑"),
    ("pages/sources.html", "Sources & Methodology", "≡"),
]

INITIALS = {
    "openbank": "OB",
    "everbank": "EV",
    "cit": "CIT",
    "barclays": "BC",
    "barclays-online": "BC",
    "synchrony": "SY",
    "marcus": "GS",
    "sofi": "SF",
    "amex": "AX",
    "capital": "C1",
    "ally": "AL",
    "wells-platinum": "WF",
    "wells": "WF",
    "usbank": "US",
    "chase": "JPM",
    "pnc": "PNC",
    "bofa": "BA",
    "citi": "CT",
}


def links(ids):
    return (
        '<div class="source-links">'
        + "".join(
            f'<a href="{E(S[i]["url"])}" target="_blank" rel="noopener noreferrer">'
            f'{E(S[i]["title"].split(" — ")[0])} ↗<span class="sr-only"> — {E(S[i]["title"])}</span></a>'
            for i in dict.fromkeys(ids)
        )
        + "</div>"
    )


def blank():
    return '<span class="sr-only">Unverified; value intentionally blank. See Flagged for Review.</span>'


def cell(v, money=False):
    if v is None:
        return blank()
    if money:
        return E(M(v) if isinstance(v, float) and not v.is_integer() else D(v))
    return E(v)


def bank(a):
    scale = (
        f"Fed Rank #{a['fedRank']} · ${a['assetsB']:,.1f}B assets · FDIC #{a['cert']}"
        if a.get("fedRank")
        else f"FSB Charter · FDIC #{a['cert']}"
    )
    return (
        f'<div class="bank-cell"><span class="bank-icon" aria-hidden="true">{INITIALS[a["id"]]}</span>'
        f'<div><strong>{E(a["bank"])}</strong><small>{E(a["product"])}<br>{E(scale)}</small></div></div>'
    )


def table(headers, rows, caption, cls=""):
    return (
        f'<div class="table-wrap"><table class="{cls}"><caption>{E(caption)}</caption>'
        f"<thead><tr>"
        + "".join(f'<th scope="col">{h}</th>' for h in headers)
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def row(values, attrs=""):
    return f"<tr {attrs}>" + "".join(f"<td>{v}</td>" for v in values) + "</tr>"


def panel(title, description, content, foot="", right=""):
    return (
        f'<section class="panel"><div class="panel-head"><div><h2>{title}</h2><p>{description}</p></div>{right}</div>'
        f"{content}" + (f'<div class="panel-foot">{foot}</div>' if foot else "") + "</section>"
    )


def heading(kicker, title, subtitle, button=""):
    return f'<div class="heading"><div><div class="eyebrow">{kicker}</div><h1>{title}</h1><div class="subtitle">{subtitle}</div></div>{button}</div>'


def notice(text, info=False):
    return f'<div class="callout{" info" if info else ""}">{text}</div>'


def calc_row_attrs(a):
    pm = a.get("promoMonths") or 0
    pdays = {3: 92, 6: 182, 12: 365, 60: 1826}.get(pm, 0)
    below = "" if a.get("belowTierApy") is None else str(a["belowTierApy"])
    promo = "" if a.get("promoApy") is None else str(a["promoApy"])
    return (
        f'data-calc-row data-account-id="{E(a["id"])}" '
        f'data-base-apy="{a["apy"]}" data-promo-apy="{promo}" data-promo-days="{pdays}" '
        f'data-min-open="{a["minimum"] or 0}" data-min-tier="{a.get("minTier") or 0}" data-below-apy="{below}"'
    )


def calc_controls(default_deposit=250000):
    presets = [
        (1000, "$1k"),
        (10000, "$10k"),
        (25000, "$25k"),
        (50000, "$50k"),
        (100000, "$100k"),
        (240000, "$240k Buffer"),
        (250000, "$250k Single Cap"),
        (500000, "$500k Joint / 2-Bank"),
    ]
    btns = "".join(
        f'<button type="button" class="btn" data-preset="{val}" aria-pressed="{"true" if val == default_deposit else "false"}">{lbl}</button>'
        for val, lbl in presets
    )
    return (
        '<div class="toolbar">'
        '<label for="calc-principal"><strong>Deposit ($):</strong></label>'
        f'<input id="calc-principal" data-calc-principal type="number" min="500" max="2000000" step="500" value="{default_deposit}">'
        '<label for="calc-days"><strong>Lifespan:</strong></label>'
        '<select id="calc-days" data-calc-days>'
        '<option value="92">3 months (92d → Jan 22, 2027)</option>'
        '<option value="182">6 months (182d → Apr 22, 2027)</option>'
        '<option value="365" selected>1 year (365d → Oct 22, 2027)</option>'
        '<option value="1096">3 years (1,096d → Oct 22, 2029)</option>'
        '<option value="1826">5 years (1,826d → Oct 22, 2031)</option>'
        "</select>"
        '<label for="calc-mode"><strong>Rate basis:</strong></label>'
        '<select id="calc-mode" data-calc-mode>'
        '<option value="promo" selected>Include verified rate boost window</option>'
        '<option value="base">Standard base APY only</option>'
        "</select>"
        f'<div class="preset-bar">{btns}</div>'
        "</div>"
    )


def page(path, title, content):
    sub = path.startswith("pages/")
    prefix = "../" if sub else ""
    nav = "".join(
        f'<a href="{prefix}{url}"'
        + (' aria-current="page"' if path == url else "")
        + f'><span class="nav-icon" aria-hidden="true">{icon}</span>{name}</a>'
        for url, name, icon in NAV
    )
    markup = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Line-by-line verified U.S. national bank savings research, multi-horizon compound returns, and maximum FDIC protection strategies. Opening date October 22, 2026."><meta name="theme-color" content="#163a34"><title>{E(title)} · Savings4</title><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brandmark" aria-hidden="true">↗</span>Savings<small>4</small></a><div class="nav-label">National Bank Research</div><nav aria-label="Main navigation">{nav}</nav><div class="sidebar-bottom"><b>Official sources only.</b>18 national accounts · 16 FDIC charters<br>Opening date · October 22, 2026<br><br><span class="dot"></span>Unconfirmed values left blank</div></aside>
<div class="workspace"><header class="topbar"><div class="crumb">SAVINGS4 Research <span aria-hidden="true">/</span> <strong>{E(title)}</strong></div><div><span class="dot"></span>Opening &amp; audit date <time datetime="2026-10-22">Oct 22, 2026</time> · NYC context</div><a href="{prefix}pages/sources.html">46 Official Sources ↗</a></header><main id="main"><div id="stale" class="callout">Historical research snapshot: rates and disclosures were verified on October 22, 2026. Account opening and projection horizons remain anchored to 2026-10-22.</div>{content}<footer><span>Savings4 · Independent line-by-line primary research. Not a bank or personalized investment advice.<br>Pre-tax variable-rate illustrations anchored to opening date 2026-10-22. Zero third-party rate quotes.</span><span><a href="{prefix}data/accounts.csv" download>Download CSV</a> · <a href="{prefix}data/accounts.json">Accounts JSON</a> · <a href="{prefix}data/sources.json">Sources JSON</a><br>FDIC $250k single / $500k joint · Fed Funds 3.75%–4.00% (Sep 17, 2026)</span></footer></main></div></body></html>'''
    dest = OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(markup)


def overview():
    result = heading(
        "U.S. National Bank Savings Audit · Opened Oct 22, 2026",
        "High yield, national scale, full FDIC protection.",
        "Every row verified line by line against official .gov regulators and first-party national bank disclosures — zero small local banks, zero third-party aggregators, and strict blanks for any unconfirmed field.",
        '<a class="btn primary" href="pages/returns.html">Explore FDIC Return Tables →</a>',
    )
    stats = [
        ("18", "National Bank Accounts", "16 distinct FDIC charters · $43.5B–$4.09T assets"),
        ("4.20<small>% APY</small>", "Top Unboosted Base APY", "EverBank (#48) · Openbank (#29) is 4.00% / 4.35% 6m"),
        ("$250<small>k</small> / $500<small>k</small>", "Standard FDIC Insurance", "Single vs 2-owner Joint · up to $1.25M POD trust"),
        ("0.38<small>% APY</small>", "FDIC National Avg (Oct 19)", "Top national HYSAs beat avg by +3.62 to +3.97 pp"),
    ]
    result += '<div class="stats">' + "".join(
        f'<div class="stat"><div class="label">{lbl}</div><div class="value">{val}</div><div class="note">{note}</div></div>'
        for val, lbl, note in stats
    ) + "</div>"
    result += '<div class="source-note">Primary regulatory &amp; leader citations: ' + links(
        ["everbank", "openbank", "cit-boost", "fdic-glance", "benchmark", "fed-fomc"]
    ) + "</div>"

    bars = [
        ("Openbank*", 4.35),
        ("EverBank", 4.20),
        ("CIT Boost*", 4.25),
        ("Barclays", 3.65),
        ("Synchrony", 3.55),
        ("Marcus", 3.50),
    ]
    result += (
        '<section class="hero"><div class="hero-copy"><div class="eyebrow">EXECUTIVE TAKEAWAY</div>'
        "<h2>Earn $9,500–$10,500/yr per insured slot — not $25 at a branch mega-bank.</h2>"
        "<p>America's largest branch banks (#1 Chase 0.01% NYC PDF, #4 Wells Way2Save 0.01%) pay <strong>$25/year</strong> on $250,000, while #2 Bank of America and #3 Citibank mask live rates behind stateful ZIP sessions. Moving reserve cash to nationally chartered digital divisions of major banks multiplies annual yield more than <strong>350×</strong> with zero monthly fees and full mobile security.</p>"
        "<p><strong>Critical FDIC rule:</strong> Deposit insurance caps principal <em>plus accrued interest</em> at $250,000 per owner per charter. Deposit <strong>~$239,800–$241,500</strong> for a 1-year single-owner account, open a <strong>$500,000 joint account</strong>, or split across distinct national charters.</p>"
        '<a class="btn" href="pages/returns.html">Model $1k–$500k returns across 3m–5y →</a>'
        '<p class="source-note">*6-month promotional boosts shown for Openbank (4.35% → 4.00% base) and CIT BOOST50 (4.25% → 3.75% base). Barclays 3.65% requires $250k+ (joint/multi-category for interest headroom).</p>'
        '</div><div class="hero-chart" role="img" aria-label="Top verified national bank APYs from 3.50 to 4.35 percent">'
        + "".join(
            f'<div class="bar-group"><b>{apy:.2f}%</b><div class="bar" style="height:{int(apy * 36)}px"></div><span>{lbl}</span></div>'
            for lbl, apy in bars
        )
        + "</div></section>"
    )

    calc_rows = []
    for a in HYSA_LEADERS:
        promo_tag = (
            f'<span class="pill">{P(a["promoApy"])} ({a["promoMonths"]}m boost)</span>'
            if a.get("promoApy")
            else '<span class="pill neutral">Flat variable rate</span>'
        )
        yr_promo = promo_interest(a, 250_000, 365)
        calc_rows.append(
            row(
                [
                    bank(a),
                    f'<span class="rate">{P(a["apy"])}</span><small>As of {a["rateAsOf"]}</small>',
                    promo_tag,
                    f'{D(a["minimum"])}<small>$0 monthly fee</small>',
                    f'<strong class="num">{M(yr_promo)}</strong>',
                    f'<span class="num">{M(250_000 + yr_promo)}</span>',
                    '<span class="pill warn">Joint ($500k) or 2 banks</span>',
                    links(a["sources"][:2] + a["bonusSources"]),
                ],
                calc_row_attrs(a)
                .replace('data-out-placeholder', '')
                + "",
            )
            .replace("<td><strong class=\"num\">", '<td data-out-interest><strong class="num">')
            .replace("<td><span class=\"num\">", '<td data-out-ending><span class="num">')
            .replace('<td><span class="pill warn">Joint ($500k) or 2 banks</span></td>', '<td data-out-fdic><span class="pill warn">Joint ($500k) or 2 banks</span></td>')
        )

    result += (
        '<div data-calc>'
        + panel(
            "Interactive National HYSA Shortlist (11 High-Yield Accounts ≥ 3.10% APY)",
            "Adjust deposit size ($1k–$500k+), investment lifespan (3m to 5y from 2026-10-22), or toggle promotional rate boosts.",
            calc_controls(250000)
            + table(
                [
                    "Bank / National Scale",
                    "Standard APY",
                    "Verified Boost",
                    "Min Open / Fee",
                    "Projected Interest",
                    "Ending Balance",
                    "FDIC Coverage Status",
                    "Official Sources",
                ],
                calc_rows,
                "Interactive national high-yield savings shortlist",
            ),
            "All 18 reviewed accounts — including branch mega-banks and blank unverified rows — are listed in the National Banks Directory.",
            '<a class="btn" href="pages/accounts.html">View All 18 Accounts →</a>',
        )
        + "</div>"
    )

    result += notice(
        f'<strong>{len(flags)} items documented on Flagged for Review.</strong> Bank of America Advantage Savings ($XXXX placeholder) and Citibank Savings (:BLUE_AccSavings_Rate% token &amp; NY Accelerate exclusion) remain strictly blank rather than inferred. <a href="pages/flagged.html">Inspect every audit item →</a>'
    )

    result += (
        '<div class="grid-three">'
        '<section class="card"><div class="number">01 / MAX FDIC ARCHITECTURE</div><h3>Single, Joint &amp; Multi-Bank Plans</h3>'
        "<p>See exact single-owner principal ceilings ($239.7k–$242.5k) that keep 12-month principal + interest under $250,000, or combine Openbank (#29950), EverBank (#34775), CIT (#11063), and Marcus (#33124) for $1M+ coverage.</p>"
        f'{links(["fdic-glance", "fdic-faq"])}<p><a href="pages/returns.html">Open Returns &amp; FDIC Plan →</a></p></section>'
        '<section class="card"><div class="number">02 / BONUSES &amp; PROMO MATH</div><h3>Cash Bonuses vs. Rate Boosts</h3>'
        "<p>Compare SoFi ($400 DD bonus + 4.40% 6m), Barclays ($200 bonus on $25k), Chase ($200 bonus on $10k), Openbank (4.35% 6m), CIT BOOST50 (4.25% 6m), and Marcus (+1.00% 3m referral).</p>"
        f'{links(["sofi", "barclays", "chase-bonus"])}<p><a href="pages/bonuses.html">Compare All 6 Promotions →</a></p></section>'
        '<section class="card"><div class="number">03 / LIFESPAN &amp; SECURITY</div><h3>3m–5y Competitiveness &amp; App Controls</h3>'
        "<p>Evaluate how rate boosts behave over 3–6 months versus base compounding over 1–5 years following the Sep 17, 2026 FOMC move to 3.75%–4.00%, alongside mobile MFA/passkey protections.</p>"
        f'{links(["fed-fomc", "chase-security", "ally-security"])}<p><a href="pages/lifespan.html">Lifespan Analysis →</a> · <a href="pages/protection.html">Security &amp; Rules →</a></p></section>'
        "</div>"
    )
    return result


def comparison():
    result = heading(
        "Complete National Directory · 18 Accounts Across 15 FDIC Charters",
        "National bank savings comparison",
        "Includes national direct banks backed by major commercial charters and top U.S. branch networks. Small local banks and credit unions are excluded; unconfirmed live rates remain blank.",
        '<a class="btn" href="../data/accounts.csv" download>↓ Download CSV</a>',
    )
    result += notice(
        "<strong>Strict Non-Hallucination Policy:</strong> Every numeric value below comes directly from an official bank page, Truth-in-Savings disclosure, or official PDF rate schedule checked on 2026-10-22. Unconfirmed live rates (Bank of America, Citibank, and geo-blocked PNC in NYC) are intentionally blank."
    )
    toolbar = (
        '<div class="toolbar">'
        '<label class="sr-only" for="search">Search bank or account</label>'
        '<input id="search" data-filter="search" type="search" placeholder="Search bank, charter, Cert #, or feature…">'
        '<label class="sr-only" for="category">Bank category</label>'
        '<select id="category" data-filter="category"><option value="">All categories</option><option>National digital</option><option>National branch + digital</option></select>'
        '<label class="sr-only" for="status">Rate status</label>'
        '<select id="status" data-filter="status"><option value="">All statuses</option><option value="confirmed">NYC rate verified (15)</option><option value="unverified">Blank / geo-restricted (3)</option></select>'
        '<span class="count" data-count aria-live="polite">18 rows shown</span></div>'
    )
    r = []
    for a in accounts:
        apy_html = (
            blank()
            if a["apy"] is None
            else f'<span class="rate">{P(a["apy"])}</span><small>As of {a["rateAsOf"]}'
            + (f" · {P(a['promoApy'])} promo" if a.get("promoApy") else "")
            + "</small>"
        )
        status = "confirmed" if a["apy"] is not None else "unverified"
        flaglinks = " · ".join(f'<a href="flagged.html#{E(i)}">{E(i)}</a>' for i in a["flags"])
        r.append(
            row(
                [
                    bank(a),
                    f'{E(a["category"])}<small>NYC: {E(a["nycEligible"])}</small>',
                    apy_html,
                    cell(a["minimum"], True),
                    cell(a["monthlyFee"], True) + f'<small>{cell(a["waiver"])}</small>',
                    cell(a["bonus"]) + "<small>" + ("Official promo terms linked" if a["bonus"] else "No public savings bonus verified") + "</small>",
                    f'<span class="pill{" warn" if status == "unverified" else ""}">{"Verified" if status == "confirmed" else "Unverified / Blank"}</span><small>{flaglinks}</small>',
                    links(a["sources"] + a["bonusSources"]),
                ],
                f'data-search="{E((a["bank"] + " " + a["product"] + " " + a["charter"] + " " + str(a["cert"])).lower())}" '
                f'data-category="{E(a["category"])}" data-status="{status}"',
            )
        )
    result += panel(
        "All 18 National Bank Savings Accounts",
        "Consolidated asset rankings reflect the Federal Reserve Large Commercial Banks Statistical Release (data as of June 30, 2026, posted October 2, 2026).",
        toolbar
        + table(
            [
                "Institution / Scale / Cert #",
                "Category & NYC Eligibility",
                "Verified Base / Promo APY",
                "Min Open",
                "Monthly Fee & Waiver",
                "Active Bonus / Boost",
                "Audit Status",
                "Official Sources",
            ],
            r,
            "All 18 national bank savings accounts",
        )
        + '<div class="no-results" hidden>No accounts match your current filter. Clear search or reset dropdowns.</div>',
        "Shared FDIC charters to watch: Openbank = Santander Bank, N.A. (#29950); CIT Bank = First Citizens Bank (#11063); Capital One = Discover (#4297); Barclays Tiered = Barclays Online (#57203); Wells Platinum = Way2Save (#3511).",
    )
    return result


def returns():
    result = heading(
        "Compound Return Matrices · Account Opened October 22, 2026",
        "Investment returns & maximum FDIC plan",
        "Deterministic compound return tables across deposit sizes ($1,000 to $500,000) and lifespans (3m, 6m, 1y, 3y, 5y) anchored to opening date 2026-10-22.",
    )
    result += notice(
        "<strong>FDIC Statutory Coverage Boundary:</strong> Deposit insurance covers <strong>$250,000 per depositor, per FDIC-insured bank charter, per ownership category</strong> — <em>principal plus accrued interest combined</em>. A single-owner $250,000 deposit leaves $0 insured room for interest unless paired with a joint owner ($500,000 cap), POD beneficiaries (up to $1,250,000), or monthly interest sweeps. <a href=\"https://www.fdic.gov/resources/deposit-insurance/faq\" target=\"_blank\" rel=\"noopener noreferrer\">Official FDIC FAQ ↗</a>"
    )

    horizon_rows = [
        row(
            [
                f"<strong>{m} months</strong>" + (f" ({m // 12} yr)" if m >= 12 else ""),
                OPENED.isoformat(),
                end.isoformat(),
                f'<span class="num">{(end - OPENED).days:,} days</span>',
                "Exact calendar day count; 2028 leap day included in 3y & 5y windows.",
                links(["fdic-faq", "benchmark"]),
            ]
        )
        for m, end in HORIZONS
    ]
    result += panel(
        "Exact Calendar Horizons (Opened 2026-10-22)",
        "Every table below uses exact calendar elapsed days from 2026-10-22 without rounding months to 30 days.",
        table(["Horizon", "Opening Date", "Maturity / Check Date", "Elapsed Days", "Day-Count Basis", "Official Reference"], horizon_rows, "Calendar horizons from October 22, 2026"),
    )

    # Interactive calculator across all 15 modeled accounts
    calc_rows = []
    for a in MODELED:
        yr_promo = promo_interest(a, 250_000, 365)
        calc_rows.append(
            row(
                [
                    bank(a),
                    f'<span class="rate">{P(a["apy"])}</span>' + (f"<small>{P(a['promoApy'])} ({a['promoMonths']}m)</small>" if a.get("promoApy") else f"<small>As of {a['rateAsOf']}</small>"),
                    f"{D(a['minimum'])} / {cell(a['monthlyFee'], True)}",
                    f'<strong class="num">{M(yr_promo)}</strong>',
                    f'<span class="num">{M(250_000 + yr_promo)}</span>',
                    '<span class="pill warn">Joint ($500k) or 2 banks</span>',
                    links(a["sources"][:1] + ["fdic-faq"]),
                ],
                calc_row_attrs(a),
            )
            .replace("<td><strong class=\"num\">", '<td data-out-interest><strong class="num">')
            .replace("<td><span class=\"num\">", '<td data-out-ending><span class="num">')
            .replace('<td><span class="pill warn">Joint ($500k) or 2 banks</span></td>', '<td data-out-fdic><span class="pill warn">Joint ($500k) or 2 banks</span></td>')
        )
    result += (
        "<div data-calc>"
        + panel(
            "Interactive Return & FDIC Headroom Calculator (All 15 Modeled Accounts)",
            "Enter any balance from $500 to $1,000,000+ or click a preset tier to compare exact interest earned, ending balance, and FDIC coverage status.",
            calc_controls(250000)
            + table(
                ["Bank / Charter", "Base / Boost APY", "Min / Fee", "Projected Interest", "Ending Balance", "FDIC Coverage Status", "Official Sources"],
                calc_rows,
                "Interactive compound return table across 15 modeled national accounts",
            ),
            "Unverified live APY banks (Bank of America, Citibank, NYC-blocked PNC) are excluded from numeric calculation rather than estimated.",
        )
        + "</div>"
    )

    # Multi-tier × Multi-horizon static matrix filterable by deposit tier
    tiers = [1000, 10000, 25000, 50000, 100000, 240000, 250000, 500000]
    tier_filter = (
        '<div class="toolbar">'
        '<label for="tier-select"><strong>Filter static table by deposit size:</strong></label>'
        '<select id="tier-select" data-filter="tier">'
        '<option value="250000" selected>$250,000 (Single-Owner FDIC Max)</option>'
        '<option value="500000">$500,000 (Joint FDIC Max / 2-Charter Split)</option>'
        '<option value="240000">$240,000 (1-Owner Buffered Principal)</option>'
        '<option value="100000">$100,000 Deposit</option>'
        '<option value="50000">$50,000 Deposit</option>'
        '<option value="25000">$25,000 Deposit</option>'
        '<option value="10000">$10,000 Deposit</option>'
        '<option value="1000">$1,000 Starter Deposit</option>'
        '<option value="">Show All 8 Deposit Tiers (120 rows)</option>'
        '</select><span class="count" data-count aria-live="polite">15 rows shown</span></div>'
    )
    matrix_rows = []
    for dep in tiers:
        for a in MODELED:
            vals = [bank(a), f"<strong>{D(dep)}</strong>"]
            base_apy = effective_base_apy(a, dep)
            if base_apy is None:
                vals += [blank()] * 6 + ['<span class="pill neutral">Below $500 min</span>', links(a["sources"][:1] + ["fdic-faq"])]
            else:
                for _, end in HORIZONS:
                    vals.append(f'<span class="num">{M(promo_interest(a, dep, (end - OPENED).days))}</span>')
                end_1y = dep + promo_interest(a, dep, 365)
                vals.append(f'<strong class="num">{M(end_1y)}</strong>')
                if end_1y <= LIMIT:
                    cov = '<span class="pill">1-Owner Insured</span>'
                elif end_1y <= JOINT_LIMIT:
                    cov = '<span class="pill warn">Joint / 2-Charter</span>'
                else:
                    cov = '<span class="pill warn">3-Charter Split</span>'
                vals.append(cov)
                vals.append(links(a["sources"][:1] + a["bonusSources"][:1] + ["fdic-faq"]))
            matrix_rows.append(row(vals, f'data-tier="{dep}"'))

    result += panel(
        "Complete Multi-Horizon Return Matrix ($1k to $500k × 3m, 6m, 1y, 3y, 5y)",
        "Interest earned incorporating verified initial boost windows followed by standard base APY compounding. Switch deposit size above or show all 120 rows at once.",
        tier_filter
        + table(
            [
                "Bank / Account",
                "Initial Deposit",
                "3m Interest (92d)",
                "6m Interest (182d)",
                "1y Interest (365d)",
                "3y Interest (1,096d)",
                "5y Interest (1,826d)",
                "1y Ending Balance",
                "FDIC Category",
                "Official Inputs",
            ],
            matrix_rows,
            "Multi-horizon interest and ending balance matrix from October 22, 2026",
        ),
        "Formula: Growth(d) = (1 + APY_promo/100)^(d_promo/365) × (1 + APY_base/100)^((d − d_promo)/365). Cash bonuses are modeled separately on Bonuses & Promotions.",
    )

    # Single-owner exact max principal table (12m horizon)
    head_rows = []
    for a in HYSA_LEADERS:
        bonus_res = a.get("bonusCash") or 0
        p12 = headroom_principal(a["apy"], 365, bonus_res)
        end12 = (p12 + bonus_res) * factor(a["apy"], 365)
        p36 = headroom_principal(a["apy"], 1096, bonus_res)
        head_rows.append(
            row(
                [
                    bank(a),
                    P(a["apy"]),
                    M(bonus_res),
                    f'<strong class="num">{M(p12)}</strong>',
                    f'<span class="num">{M(end12 - p12 - bonus_res)}</span>',
                    f'<span class="num">{M(end12)}</span>',
                    f'<span class="num">{M(p36)}</span>',
                    links(a["sources"][:1] + ["fdic-faq"]),
                ]
            )
        )
    result += panel(
        "Exact Single-Owner Maximum Deposit Ceiling (Principal + Accrued Interest ≤ $250,000)",
        "Maximum opening principal on 2026-10-22 so 12-month (or 36-month) compounded balance plus any cash bonus stays at or below $249,999.00 ($1 safety reserve).",
        table(
            [
                "Bank / Charter",
                "Base APY",
                "Cash Bonus Reserve",
                "Max 1y Principal",
                "1y Compounded Interest",
                "1y Insured Ending Total",
                "Max 3y Principal",
                "Official Sources",
            ],
            head_rows,
            "Single-owner exact FDIC principal ceilings",
        ),
        "Alternatively, link an external checking account to auto-sweep monthly interest credits out each month and hold the full $250,000 principal insured year-round.",
    )

    alloc = [
        row(["<strong>$250,000</strong> (1 Owner, 0 Sweep)", "2 Charters", "Openbank $150k (#29950) + EverBank $100k (#34775)", M(promo_interest(accounts[0], 150000, 365) + promo_interest(accounts[1], 100000, 365)), "Every charter stays well below $250k after 5 years of compounding.", links(["openbank", "everbank", "fdic-glance"])]),
        row(["<strong>$500,000</strong> (Joint OR 3 Single)", "1 Joint or 3 Single", "Joint: Openbank $240k + EverBank $240k + CIT $20k (#11063)", M(promo_interest(accounts[0], 240000, 365) + promo_interest(accounts[1], 240000, 365) + promo_interest(accounts[2], 20000, 365)), "Zero charter overlap; every account retains >$9,500 interest buffer.", links(["openbank", "everbank", "cit-boost", "fdic-glance"])]),
        row(["<strong>$1,000,000</strong> (Single Owner)", "5 Distinct Charters", "$238k each at Openbank (#29950), EverBank (#34775), CIT (#11063), Synchrony (#27314) + $48k at Marcus (#33124)", M(promo_interest(accounts[0], 238000, 365) + promo_interest(accounts[1], 238000, 365) + promo_interest(accounts[2], 238000, 365) + promo_interest(accounts[4], 238000, 365) + interest(48000, 3.50, 365)), "100% insured across 5 independent national FDIC certificates.", links(["openbank", "everbank", "cit-boost", "synchrony", "marcus", "fdic-bankfind"])]),
    ]
    result += panel(
        "Multi-Charter Maximum FDIC Portfolio Allocations ($250k, $500k & $1,000,000)",
        "Zero-overlap national bank portfolios built strictly from distinct FDIC certificates.",
        table(["Portfolio Size", "Charters Used", "Allocation Across Distinct National Banks", "1y Modeled Interest", "Coverage & Headroom Verification", "Official Sources"], alloc, "Multi-bank FDIC-insured portfolio blueprints"),
    )
    return result


def bonuses():
    result = heading(
        "Active Savings Promotions & Rate Boosts · Verified Oct 22, 2026",
        "Bonuses, promo codes & deposit thresholds",
        "Six national banks publish verifiable savings rate boosts or cash bonuses on official pages as of 2026-10-22. Unverified offers remain strictly blank.",
    )
    offers = [
        row(["<strong>Openbank by Santander</strong><small>High Yield Savings</small>", "<strong>+0.35% APY boost</strong> (4.35% total) for 6 months", "$500 opening minimum", "Active on 2026-10-22; boost applies first 6 months from opening, then 4.00% variable base.", "New Openbank customers; mobile device with biometric login required.", f"+{M(promo_interest(accounts[0], 240000, 365) - interest(240000, 4.00, 365))} extra on $240k in yr 1", links(["openbank"])]),
        row(["<strong>SoFi Bank, N.A.</strong><small>Checking &amp; Savings</small>", "<strong>+1.10% boost</strong> (4.40% 6m) + <strong>$50 / $400 DD bonus</strong>", "$1,000 DD ($50) or $5,000+ DD ($400) within 25 days", "DD offer runs through 2027-12-31; rate boost lasts up to 6 months.", "Requires ongoing Direct Deposit or $5k/31d deposits to keep 3.30% base (else 0.80%).", "$400 cash + 6m rate boost", links(["sofi", "sofi-ratesheet"])]),
        row(["<strong>CIT Bank (First Citizens)</strong><small>Platinum Savings</small>", "<strong>Code BOOST50: +0.50% boost</strong> (4.25% APY) for 6 months", "$5,000+ daily balance ($100 min open)", "Enroll Sep 29, 2026 – Dec 15, 2026; 6-month boost up to $9,999,999.", "Available to eligible new and existing Platinum Savings customers using BOOST50.", f"+{M(promo_interest(accounts[2], 240000, 365) - interest(240000, 3.75, 365))} extra on $240k in yr 1", links(["cit", "cit-boost"])]),
        row(["<strong>Barclays Bank Delaware</strong><small>Tiered Savings</small>", "<strong>$200 cash bonus</strong>", "$25,000+ external deposit within 30 days", "Open by 2026-10-31; hold $25,000+ for 120 consecutive days (to Feb 19, 2027 if funded Oct 22); payout ~60 days after hold.", "New Barclays Savings/CD customers only.", "$200 cash (= +0.80% on $25k; +0.08% on $250k)", links(["barclays"])]),
        row(["<strong>Marcus by Goldman Sachs</strong><small>Online Savings</small>", "<strong>+1.00% APY referral boost</strong> (4.50% APY) for 3 months", blank(), "Ongoing referral program; up to 5 boosts/year queued sequentially (1 active at a time).", "New customers opening via an existing customer referral link (no OSA/CD in prior 12m).", f"+{M(240000 * (referral_factor(365) - factor(3.5, 365)))} extra on $240k per 3m boost", links(["marcus-bonus"])]),
        row(["<strong>JPMorgan Chase</strong><small>Chase Savings</small>", "<strong>$100 or $200 cash bonus</strong>", "$5,000 ($100) or $10,000 ($200) new money within 30 business days", "Offer valid through 2027-01-27; hold balance 90 consecutive days.", "0.01% base APY means holding >90 days carries severe opportunity cost vs 4.00%+ HYSA.", "$201 total yr-1 yield on $10k (2.01% effective) vs $418 at Openbank", links(["chase-bonus", "chase-nyc-pdf"])]),
    ]
    result += panel(
        "6 Verified National Bank Savings Offers",
        "Every term, promo code, hold window, and expiration date verified directly from first-party bank disclosures.",
        table(["Institution", "Verified Reward", "Qualifying Deposit", "Timeline (If Opened 2026-10-22)", "Key Conditions", "Incremental Value", "Official Terms"], offers, "Verified national bank promotions", "long-table"),
    )

    comp = []
    for dep in [10000, 25000, 100000, 240000]:
        ob = promo_interest(accounts[0], dep, 365)
        cit_tot = promo_interest(accounts[2], dep, 365)
        barc_tot = interest(dep, 3.50, 365) + (200 if dep >= 25000 else 0)
        sofi_tot = promo_interest(accounts[6], dep, 365) + 400
        chase_tot = interest(dep, 0.01, 365) + (200 if dep >= 10000 else 0)
        comp.append(
            row(
                [
                    f"<strong>{D(dep)}</strong>",
                    f'<strong class="num">{M(ob)}</strong><small>Openbank 4.35%→4.00%</small>',
                    f'<span class="num">{M(sofi_tot)}</span><small>SoFi w/ $5k DD ($400 incl.)</small>',
                    f'<span class="num">{M(cit_tot)}</span><small>CIT BOOST50 4.25%→3.75%</small>',
                    f'<span class="num">{M(barc_tot)}</span><small>Barclays 3.50% + $200</small>',
                    f'<span class="num">{M(chase_tot)}</span><small>Chase 0.01% + $200</small>',
                    links(["openbank", "sofi", "cit-boost", "barclays", "chase-bonus"]),
                ]
            )
        )
    result += panel(
        "12-Month All-In Dollar Comparison (Interest + Qualified Cash Bonus)",
        "Demonstrates why cash bonuses matter at $10k–$25k (SoFi $400 + boost wins at every tier when Direct Deposit qualifies), whereas pure rate leaders dominate without Direct Deposit.",
        table(["Deposit Size", "Openbank (No DD)", "SoFi (With $5k DD)", "CIT BOOST50 (No DD)", "Barclays Tiered ($200)", "Chase ($200 Bonus)", "Official Inputs"], comp, "All-in 12-month promotional comparison"),
    )

    unv = [
        row([bank(a), blank(), '<span class="pill neutral">No public savings promo confirmed</span>', links(a["sources"][:1])])
        for a in accounts
        if not a["bonus"]
    ]
    result += panel(
        "Accounts Without Confirmed Public Savings Bonus (Left Blank)",
        "Blank indicates no standalone public savings bonus was confirmed on the inspected official product page as of 2026-10-22.",
        table(["Bank / Account", "Confirmed Savings Bonus", "Verification Note", "Official Page Checked"], unv, "Accounts with blank unconfirmed bonus status"),
    )
    return result


def lifespan():
    result = heading(
        "Rate Competitiveness Across Investment Lifespans · 3m to 5y",
        "Short-term boosts vs. multi-year compounding",
        "Following the Federal Reserve FOMC +25 bps hike to 3.75%–4.00% on September 17, 2026, national savings accounts span a 434 bps gulf from 0.01% branch accounts to 4.35%–4.40% boosted digital leaders.",
    )
    bench = [
        row(["<strong>3 Months (92d)</strong>", "SoFi 4.40% boost (+$400 DD) · Marcus 4.50% referral · Openbank 4.35%", "1.14% (3m CD) / 0.38% Savings", "+3.21 to +3.36 pp vs 3m CD", "Promotional rate boosts & quick cash bonuses dominate short parking horizons.", links(["sofi", "marcus-bonus", "openbank", "benchmark"])]),
        row(["<strong>6 Months (182d)</strong>", "SoFi 4.40% · Openbank 4.35% · CIT BOOST50 4.25% · EverBank 4.20%", "1.39% (6m CD) / 3.95% Marcus 6m CD", "+2.86 to +3.01 pp vs FDIC 6m CD", "Full 6-month boost windows beat Marcus's 6m fixed CD (3.95%) with full daily liquidity.", links(["openbank", "cit-boost", "marcus-cd", "benchmark"])]),
        row(["<strong>1 Year (365d)</strong>", "EverBank 4.20% ($10,500/$250k) · Openbank 4.17% eff. · CIT 4.00% eff.", "1.76% (12m CD) / 4.40% Marcus 12m CD", "Variable HYSA ~4.17%–4.20% vs 4.40% fixed CD", "If FOMC cuts rates in 2027, locking a 4.40% 12m CD edges variable HYSAs by ~20–25 bps in exchange for liquidity.", links(["everbank", "openbank", "marcus-cd", "benchmark"])]),
        row(["<strong>3 Years (1,096d)</strong>", "EverBank 4.20% ($32,870/$250k) · Openbank 4.00% base ($31,663/$250k)", "1.39% (36m CD) / 0.38% Savings", "+2.61 to +2.81 pp over 36m CD avg", "6-month intro boosts fade to <6 bps annualized impact by year 3; ongoing base APY rules.", links(["everbank", "openbank", "benchmark", "fed-fomc"])]),
        row(["<strong>5 Years (1,826d)</strong>", "EverBank 4.20% ($57,184/$250k) · Openbank 4.00% base ($54,602/$250k) vs Chase 0.01% ($125)", "1.41% (60m CD) / 0.38% Savings", "+$54,477 to +$57,059 vs Chase on $250k", "Compounding spread between a 4.00%+ national HYSA and a 0.01% branch account exceeds $54,000 per $250k slot.", links(["everbank", "openbank", "chase-nyc-pdf", "benchmark"])]),
    ]
    result += panel(
        "Competitiveness by Investment Lifespan (Anchored to FOMC 3.75%–4.00% & Oct 19 FDIC Benchmarks)",
        "How optimal product choice shifts across holding periods from 92 days to 1,826 days.",
        table(["Lifespan", "Top National Bank Strategy", "Official Benchmark", "Yield Spread", "Strategic Takeaway", "Official Sources"], bench, "Rate competitiveness across investment lifespans", "long-table"),
    )

    sens = []
    for label, apy in [
        ("Rate-Cut Cycle (−100 bps from Openbank base)", 3.00),
        ("Current Openbank Verified Base Rate", 4.00),
        ("Tightening Cycle (+100 bps scenario)", 5.00),
    ]:
        sens.append(
            row(
                [
                    f"<strong>{label}</strong>",
                    P(apy),
                    M(interest(240000, apy, 365)),
                    M(interest(240000, apy, 1096)),
                    M(interest(240000, apy, 1826)),
                    links(["openbank", "fed-fomc", "fdic-faq"]),
                ]
            )
        )
    result += panel(
        "Multi-Year Rate Sensitivity on a $240,000 Buffered Single-Owner Deposit",
        "Illustrates pre-tax interest earned at 1y, 3y, and 5y if variable HYSA rates move ±100 bps with future Federal Reserve policy.",
        table(["Policy Scenario", "Scenario APY", "1y Interest", "3y Interest", "5y Interest", "Official References"], sens, "Multi-year rate sensitivity scenarios"),
    )
    return result


def protection():
    result = heading(
        "Digital App, Security Controls & Opening Rules",
        "Protect the principal. Verify every charter.",
        "Every institution below is a nationally chartered FDIC-insured bank with an official iOS/Android mobile app. Authentication fields reflect only controls explicitly confirmed on official bank pages.",
    )
    cov = [
        row(["<strong>Single Accounts</strong>", "$250,000 per owner, per bank charter", "Checking + Savings + CDs held individually at the same charter aggregate.", links(["fdic", "fdic-glance"])]),
        row(["<strong>Joint Accounts</strong>", "$500,000 per 2-owner joint account ($250k/co-owner)", "Separate coverage bucket from single accounts at the exact same bank — allowing $1,000,000 combined family coverage at ONE national bank (2 single + 1 joint).", links(["fdic-glance", "fdic-edie"])]),
        row(["<strong>Trust / POD Accounts</strong>", "$250,000 per eligible beneficiary up to $1,250,000 per owner (5+)", "Unified FDIC trust rule effective April 1, 2024 applies equally to informal POD designations and formal revocable/irrevocable trusts.", links(["fdic-glance"])]),
        row(["<strong>Shared-Charter Mergers &amp; Divisions</strong>", "Brand names do NOT multiply insurance", "Openbank = Santander (#29950); CIT Bank = First Citizens (#11063); Capital One = Discover (#4297); Barclays Tiered = Barclays Online (#57203).", links(["openbank", "cit", "capital", "fdic-bankfind"])]),
    ]
    result += panel(
        "Statutory FDIC Insurance Rules & Ownership Multipliers",
        "Verified directly against fdic.gov rules and BankFind charter records.",
        table(["Ownership Structure", "Statutory Coverage Limit", "Operational Rule", "Official .gov Source"], cov, "Statutory FDIC rules"),
    )

    sec_rows = [
        row(
            [
                bank(a),
                cell(a["app"]),
                cell(a["security"]),
                cell(a["fdic"]),
                cell(a["opening"]),
                cell(a["access"]),
                links(a["sources"]),
            ]
        )
        for a in accounts
    ]
    result += panel(
        "Mobile App, Published Security Controls & Account Opening Rules (All 18 Entries)",
        "Security cells are intentionally blank where the bank's inspected product/security pages do not itemize granular authentication methods.",
        table(
            ["Bank / Charter / Cert #", "Official Mobile App", "Verified Security Controls", "FDIC Charter & Aggregation", "Minimums & Opening Rules", "Transfer & Access Limits", "Official Sources"],
            sec_rows,
            "Mobile app, security, FDIC charter, and opening rules",
            "long-table",
        ),
    )
    return result


def flagged():
    result = heading(
        "Line-by-Line Audit & Transparency Register",
        "Flagged for Review",
        "Every unconfirmed field left blank, every live bank website defect encountered on 2026-10-22, every geo-restriction, and every prior-commit discrepancy resolved across the repository.",
    )
    r = [
        row(
            [
                f'<span class="pill warn">{E(f["severity"])}</span>',
                f'<strong>{E(f["title"])}</strong><small>ID: {E(f["id"])}</small>',
                E(f["detail"]),
                '<span class="pill neutral">Logged · 2026-10-22</span>',
                links(f["sources"]),
            ],
            f'id="{E(f["id"])}"',
        )
        for f in flags
    ]
    result += panel(
        f"{len(flags)} Verified Irregularities, Blanks & Audit Findings",
        "Unconfirmed live rates are never filled with competitor numbers, stale PDFs, or third-party aggregator estimates.",
        table(["Category", "Finding", "Evidence & Treatment Applied", "Audit Status", "Official Evidence"], r, "Flagged items and repository audit register"),
    )
    return result


def methodology():
    result = heading(
        "Primary Evidence Ledger & Reproducible Methodology",
        "Official sources & mathematical contract",
        "46 primary evidence records from .gov regulators and official national bank domains checked October 22, 2026 (UTC). Zero third-party rate aggregators.",
    )
    result += panel(
        "Deterministic Compounding & FDIC Headroom Equations",
        "Identical formulas power Python static generation (scripts/model.py & audit/compute_returns.py) and interactive client-side previews (assets/app.js).",
        '<div class="card"><div class="formula">'
        "Opening Date = 2026-10-22 | Horizons = 92d (3m), 182d (6m), 365d (1y), 1,096d (3y), 1,826d (5y)\n"
        "Growth_Base(d)  = (1 + APY_base / 100) ^ (d / 365)\n"
        "Growth_Promo(d) = (1 + APY_promo / 100) ^ (min(d, d_promo) / 365) * (1 + APY_base / 100) ^ ((d - min(d, d_promo)) / 365)\n"
        "Max_Single_Principal(d) = floor_cents( ((250,000 - 1) / Growth(d)) - Cash_Bonus_Reserve )"
        "</div></div>",
        "Official benchmark & statutory references: " + links(["fdic", "fdic-faq", "fdic-glance", "benchmark", "fed-fomc", "fed-lbr"]),
    )
    r = [
        row(
            [
                f'<strong>{E(s["id"])}</strong><small>Checked {s["checked"]}</small>',
                E(s["asOf"]) if s["asOf"] else blank(),
                f'<strong>{E(s["title"])}</strong><p>{E(s["excerpt"])}</p>'
                + (f'<p class="source-note">Audit note: {E(s["note"])}</p>' if s["note"] else ""),
                f'<a class="source-url" href="{E(s["url"])}" target="_blank" rel="noopener noreferrer">Official source ↗</a>',
            ],
            f'id="{E(s["id"])}"',
        )
        for s in sources
    ]
    result += panel(
        f"All {len(sources)} Primary Official Sources",
        "Every table row across all 8 category pages cites one or more records in this ledger.",
        table(["Source ID", "Official Effective / As-Of Date", "Verbatim Evidence Summary", "Primary Link"], r, "Primary official evidence ledger", "sources-table"),
    )
    result += notice(
        '<strong>Preserved Multi-Session Repository Artifacts:</strong> '
        '<a href="../audit/verification-log.md">Session 339c96e1 Line-by-Line Audit Log</a> · '
        '<a href="../research/VERIFICATION.md">Session f025ed43 Verification Notes</a> · '
        '<a href="../docs/index.html">Reconciled /docs Research Site (Session 4b134088)</a> · '
        '<a href="../previous/root/index.html">Archived Initial Root Snapshot (Session 674b0fdc)</a>.',
        True,
    )
    return result


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(exist_ok=True)
    for folder in ["assets", "data", "research", "audit"]:
        if (ROOT / folder).exists():
            shutil.copytree(ROOT / folder, OUT / folder, dirs_exist_ok=True)
    for archive in ["previous", "docs"]:
        if (ROOT / archive).exists():
            shutil.copytree(ROOT / archive, OUT / archive, dirs_exist_ok=True)

    with (OUT / "data/accounts.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "bank", "charter", "fdic_cert", "fed_asset_rank", "assets_billions_usd",
            "account", "category", "nyc_eligible", "apy_percent", "promo_apy_percent",
            "promo_months", "rate_as_of", "checked", "opening_minimum_usd",
            "monthly_fee_usd", "fee_waiver", "confirmed_offer", "app", "security",
            "fdic_note", "opening_rules", "access", "review_flags", "official_sources",
        ])
        for a in accounts:
            writer.writerow([
                a["bank"], a["charter"], a["cert"], a["fedRank"], a["assetsB"],
                a["product"], a["category"], a["nycEligible"], a["apy"], a["promoApy"],
                a["promoMonths"] or "", a["rateAsOf"], "2026-10-22", a["minimum"],
                a["monthlyFee"], a["waiver"], a["bonus"], a["app"], a["security"],
                a["fdic"], a["opening"], a["access"], "; ".join(a["flags"]),
                " | ".join(S[x]["url"] for x in dict.fromkeys(a["sources"] + a["bonusSources"])),
            ])

    pages = [
        ("index.html", "Overview", overview),
        ("pages/accounts.html", "National Banks (18)", comparison),
        ("pages/returns.html", "Returns & FDIC Plan", returns),
        ("pages/bonuses.html", "Bonuses & Promotions", bonuses),
        ("pages/lifespan.html", "Lifespan & Rate Cycle", lifespan),
        ("pages/protection.html", "App, Security & Rules", protection),
        ("pages/flagged.html", "Flagged for Review", flagged),
        ("pages/sources.html", "Sources & Methodology", methodology),
    ]
    for path, title, fn in pages:
        page(path, title, fn())

    # Write clean category redirect stubs in categories/*.html
    cat_dir = OUT / "categories"
    cat_dir.mkdir(exist_ok=True)
    cat_map = {
        "accounts.html": "../pages/accounts.html",
        "returns.html": "../pages/returns.html",
        "bonuses.html": "../pages/bonuses.html",
        "lifespan.html": "../pages/lifespan.html",
        "security.html": "../pages/protection.html",
        "flagged.html": "../pages/flagged.html",
        "sources.html": "../pages/sources.html",
    }
    for name, target in cat_map.items():
        (cat_dir / name).write_text(
            f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0;url={target}">'
            f'<title>Redirecting · Savings4</title></head>'
            f'<body><p><a href="{target}">Continue to {target} →</a></p></body></html>\n'
        )

    (OUT / ".nojekyll").write_text("")
    shutil.copy2(OUT / "index.html", ROOT / "index.html")
    shutil.copytree(OUT / "pages", ROOT / "pages", dirs_exist_ok=True)
    shutil.copytree(OUT / "categories", ROOT / "categories", dirs_exist_ok=True)
    shutil.copy2(OUT / "data/accounts.csv", ROOT / "data/accounts.csv")
    (ROOT / ".nojekyll").write_text("")
    print(f"Built {len(pages)} pages, {len(accounts)} accounts, {len(sources)} official sources, {len(flags)} flags in {OUT}")


if __name__ == "__main__":
    build()
