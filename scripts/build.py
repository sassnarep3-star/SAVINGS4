"""Build a dependency-free static GitHub Pages site from reviewed JSON evidence."""
import csv
import html
import json
import shutil
from pathlib import Path
from model import OPENED, HORIZONS, LIMIT, factor, interest, headroom_principal, referral_factor

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'
accounts=json.loads((ROOT/'data/accounts.json').read_text())
sources=json.loads((ROOT/'data/sources.json').read_text())
flags=json.loads((ROOT/'data/flags.json').read_text())
S={s['id']:s for s in sources}
MODELED=[a for a in accounts if a['modelEligible']]
E=lambda x:html.escape(str(x),quote=True)
M=lambda x:f'${x:,.2f}'
D=lambda x:f'${x:,.0f}'
P=lambda x:f'{x:.2f}%'
NAV=[('index.html','Overview','◫'),('pages/accounts.html','Account comparison','▤'),('pages/returns.html','Returns & FDIC plan','↗'),('pages/bonuses.html','Bonuses & promotions','◇'),('pages/protection.html','Security & opening','⊙'),('pages/flagged.html','Flagged for Review','⚑'),('pages/sources.html','Sources & methodology','≡')]

def links(ids):
    return '<div class="source-links">'+''.join(f'<a href="{E(S[i]["url"])}" target="_blank" rel="noopener noreferrer">{E(S[i]["title"].split(" — ")[0])} ↗<span class="sr-only"> — {E(S[i]["title"])}</span></a>' for i in dict.fromkeys(ids))+'</div>'

def blank():
    return '<span class="sr-only">Unverified; value intentionally blank. See Flagged for Review.</span>'

def cell(v,money=False):
    return blank() if v is None else E(D(v) if money else v)

def bank(a):
    initials={'marcus':'M','barclays':'B','amex':'AX','ally':'a','capital':'C1','bofa':'BA','chase':'CH','wells':'WF','wells-platinum':'WF','synchrony':'SY','citi':'citi','pnc':'PNC'}
    return f'<div class="bank-cell"><span class="bank-icon" aria-hidden="true">{initials[a["id"]]}</span><div><strong>{E(a["bank"])}</strong><small>{E(a["product"])}</small></div></div>'

def table(headers,rows,caption,cls=''):
    return f'<div class="table-wrap"><table class="{cls}"><caption>{E(caption)}</caption><thead><tr>'+''.join(f'<th scope="col">{h}</th>' for h in headers)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

def row(values,attrs=''):
    return f'<tr {attrs}>'+''.join(f'<td>{v}</td>' for v in values)+'</tr>'

def panel(title,description,content,foot='',right=''):
    return f'<section class="panel"><div class="panel-head"><div><h2>{title}</h2><p>{description}</p></div>{right}</div>{content}'+(f'<div class="panel-foot">{foot}</div>' if foot else '')+'</section>'

def heading(kicker,title,subtitle,button=''):
    return f'<div class="heading"><div><div class="eyebrow">{kicker}</div><h1>{title}</h1><div class="subtitle">{subtitle}</div></div>{button}</div>'

def notice(text,info=False):
    return f'<div class="callout{ " info" if info else ""}">{text}</div>'

def page(path,title,content):
    sub=path.startswith('pages/')
    prefix='../' if sub else ''
    nav=''.join(f'<a href="{prefix}{url}"'+(' aria-current="page"' if path==url else '')+f'><span class="nav-icon" aria-hidden="true">{icon}</span>{name}</a>' for url,name,icon in NAV)
    markup=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Official-source savings account research, modeled returns and FDIC headroom. Research snapshot October 22, 2026."><meta name="theme-color" content="#163a34"><title>{E(title)} · Savings4</title><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brandmark" aria-hidden="true">↗</span>Savings<small>4</small></a><div class="nav-label">SAVINGS RESEARCH</div><nav aria-label="Main navigation">{nav}</nav><div class="sidebar-bottom"><b>Evidence over assumptions.</b>Official sources. Transparent models.<br>Snapshot · October 22, 2026<br><br><span class="dot"></span>No personal data collected</div></aside>
<div class="workspace"><header class="topbar"><div class="crumb">Research workspace <span aria-hidden="true"> / </span> <strong>{E(title)}</strong></div><div><span class="dot"></span>Research checked <time datetime="2026-10-22">Oct 22, 2026</time> · UTC</div><a href="{prefix}pages/sources.html">View evidence ↗</a></header><main id="main"><div id="stale" class="callout">Historical research snapshot: rates were checked October 22, 2026. Opening and projection dates below stay fixed to that research date; this page does not claim live rates.</div>{content}<footer><span>Savings4 · Independent research, not a bank or personalized financial advice.<br>Variable-rate estimates, before taxes. No accounts opened. No affiliate links.</span><span><a href="{prefix}data/accounts.csv" download>Download account CSV</a> · <a href="{prefix}data/sources.json">Evidence JSON</a><br>Opening scenario: October 22, 2026 · Sources checked on that date.</span></footer></main></div></body></html>'''
    dest=OUT/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(markup)


def overview():
    result=heading('Your savings, researched','Make your savings work harder.','A clear comparison of major national-bank savings options, with official sources, transparent return scenarios and room for FDIC protection.','<a class="btn" href="data/accounts.csv" download>↓ Export comparison</a>')
    stats=[('12','products reviewed','11 bank groups · bounded shortlist'),('3.50<small>% APY</small>','Highest confirmed below-limit base APY','Marcus & Barclays · not a market-wide best'),('$250<small>k</small>','FDIC standard coverage','Per depositor, bank & ownership category'),('$200','Confirmed conditional cash offer','Barclays · eligibility and holding rules apply')]
    result+='<div class="stats">'+''.join(f'<div class="stat"><div class="label">{label}</div><div class="value">{value}</div><div class="note">{note}</div></div>' for value,label,note in stats)+'</div>'
    result+='<div class="source-note">Snapshot facts: '+links(['marcus','barclays','fdic'])+'</div>'
    result+='''<section class="hero"><div class="hero-copy"><div class="eyebrow">THE RESEARCH TAKEAWAY</div><h2>Start with the return.<br>Leave room for the interest.</h2><p>Among the unambiguous rates checked, Marcus and Barclays both pay 3.50% below $250,000. Barclays adds a conditional $200 cash offer; Marcus offers a referral-only rate boost. Neither is an automatic entitlement.</p><p>Depositing $250,000 uses the full single-owner FDIC limit before interest. Under a constant 3.50% scenario, a $240,000 deposit grows to $248,400 in one year, before any bonus.</p><a class="btn" href="pages/returns.html">Explore the return & coverage plan →</a><p class="source-note">Inputs: <a href="https://www.marcus.com/us/en/savings/high-yield-savings">Marcus</a> · <a href="https://banking.us.barclays/tiered-savings.html">Barclays</a> · <a href="https://www.fdic.gov/resources/deposit-insurance/faq">FDIC</a>. End balance is our calculation, not a bank quote.</p></div><div class="hero-chart" role="img" aria-label="Confirmed base APYs: Marcus and Barclays 3.50 percent, Amex 3.20 percent, Ally 3.10 percent. Not a ranking of all banks.">'''
    for label,apy in [('Marcus',3.5),('Barclays',3.5),('Amex',3.2),('Ally',3.1)]:
        result+=f'<div class="bar-group"><b>{apy:.2f}%</b><div class="bar" style="height:{int(apy*40)}px"></div><span>{label}</span></div>'
    result+='</div></section>'
    r=[]
    for a in MODELED:
        r.append(row([bank(a),f'<span class="rate">{P(a["apy"])}</span><small>As of {a["rateAsOf"]} · variable</small>',f'<span class="num">{M(interest(100000,a["apy"],365))}</span><small>On $100,000 · constant APY</small>',f'{D(a["minimum"])}<small>Opening minimum · no monthly fee</small>',f'<span class="pill">Rate confirmed</span><small>Some eligibility/security review remains</small>',links(a['sources'][:1])]))
    result+=panel('Confirmed-rate shortlist','Only four products have an unambiguous rate usable in the below-limit model.',table(['Bank / account','Base APY','12-month modeled interest','Opening deposit','Evidence status','Official source'],r,'Confirmed rates and illustrative annual returns'),'Rates checked October 22, 2026; publisher dates shown. “Confirmed” applies to the quoted fields, not every requirement or personal eligibility.','<a class="btn" href="pages/accounts.html">All 12 entries →</a>')
    result+=notice(f'<strong>{len(flags)} items flagged for review.</strong> Missing rates, unresolved eligibility, conflicting disclosures and insurance constraints are published, not hidden. <a href="pages/flagged.html">Review the findings →</a>')
    result+='<div class="grid-two"><section class="card"><div class="number">01 / HIGHEST RETURN</div><h2>Promotions change the comparison.</h2><p>For an eligible new customer, Barclays’ $200 adds 0.80% of a $25,000 deposit, but only 0.08% of $250,000. Marcus’ boost is temporary and needs a qualifying referral. Compare conditions and time horizons, not headline rates alone.</p><p>Calculated ratios using the <a href="https://banking.us.barclays/tiered-savings.html">official Barclays offer</a>.</p><a href="pages/bonuses.html">Compare promotion scenarios →</a></section><section class="card"><div class="number">02 / PROTECTION FIRST</div><h2>A bank brand is not an insurance bucket.</h2><p>Same-bank deposits in the same ownership category aggregate. Capital One says newly opened Discover deposits count with Capital One deposits. Splitting across those brands does not create extra capacity.</p><p><a href="https://www.capitalone.com/bank/savings-accounts/online-performance-savings-account/">Capital One disclosure</a> · <a href="https://www.fdic.gov/resources/deposit-insurance/understanding-deposit-insurance">FDIC coverage rules</a></p><a href="pages/protection.html">Review security & opening rules →</a></section></div>'
    return result


def comparison():
    result=heading('THE FULL SHORTLIST','Account comparison','All 12 reviewed products, including unresolved entries. New York is a planning context from the approximate session location, not verified residence. No precise home ZIP or personal eligibility has been invented. “National” describes the study’s distribution scope, not bank charter status.')
    result+=notice('<strong>Blank means unverified, not zero.</strong> Missing values are intentionally empty; the status column and review page explain why. Current rates are not borrowed from competitors or third-party rankings.')
    toolbar='''<div class="toolbar"><label class="sr-only" for="search">Search bank or account</label><input id="search" data-filter="search" type="search" placeholder="Search bank or account…"><label class="sr-only" for="category">Bank category</label><select id="category" data-filter="category"><option value="">All categories</option><option>National digital</option><option>National branch + digital</option></select><label class="sr-only" for="status">Rate verification status</label><select id="status" data-filter="status"><option value="">All rate statuses</option><option value="confirmed">Rate confirmed</option><option value="unverified">Rate unverified</option></select><span class="count" data-count aria-live="polite">12 entries shown</span></div>'''
    r=[]
    for a in accounts:
        apy=blank() if a['apy'] is None else f'<span class="rate">{P(a["apy"])}</span><small>{a["rateAsOf"]}</small>'
        status='confirmed' if a['apy'] is not None else 'unverified'
        flaglinks=' · '.join(f'<a href="flagged.html#{E(i)}">{E(i)}</a>' for i in a['flags'])
        r.append(row([bank(a),f'{E(a["category"])}',apy,cell(a['minimum'],True),cell(a['monthlyFee'],True)+f'<small>{cell(a["waiver"])}</small>',cell(a['bonus'])+'<small>'+('Conditional; see promotion terms' if a['bonus'] else 'Promotion unverified')+'</small>',f'<span class="pill{ " warn" if status=="unverified" else ""}">Rate {status}</span><small>{flaglinks}</small>',links(a['sources']+a['bonusSources'])],f'data-search="{E((a["bank"]+" "+a["product"]).lower())}" data-category="{E(a["category"])}" data-status="{status}"'))
    result+=panel('Rates, fees & offers','APYs are variable. Fees shown are monthly maintenance fees before waivers, not an assertion that all services are free.',toolbar+table(['Bank / account','Category','Current base APY / publisher date','Minimum to open','Monthly fee / waiver','Confirmed offer','Review status','Official sources'],r,'All reviewed accounts and missing-field statuses')+'<div class="no-results" hidden>No accounts match your filters. Clear the search or select all categories.</div>','Every row was checked October 22, 2026. Barclays APY here is the below-$250,000 tier; its 3.65% top tier is not suitable for fully insured retained-interest modeling.')
    result+=notice('Scope is deliberately bounded: major US branch-bank brands and nationally available digital-bank brands. This is <strong>not a full census of every bank or a market-wide highest-rate claim</strong>. CDs, checking bundles, brokered sweeps, fintech platforms and local-only banks are not ranked. See <a href="sources.html">methodology</a>.',True)
    return result


def returns():
    result=heading('ILLUSTRATIONS, NOT PROMISES','Returns & FDIC headroom','Opening and funding scenario: October 22, 2026. No personal balances required. All calculations are pre-tax, constant-rate illustrations, clearly separated from verified bank facts.')
    result+=notice('<strong>Protect principal plus interest.</strong> The FDIC limit is not $250,000 of principal plus unlimited earnings. All same-bank, same-category deposits aggregate, including accrued interest. <a href="https://www.fdic.gov/resources/deposit-insurance/faq">Official FDIC explanation ↗</a>')
    date_rows=[row([f'{months} calendar months',OPENED.isoformat(),end.isoformat(),str((end-OPENED).days),'Our calendar calculation; input APYs are dated official quotes.',links(['marcus','barclays','amex','ally'])]) for months,end in HORIZONS]
    result+=panel('The dates behind the numbers','Opening date stays fixed to the research snapshot; browser time does not silently change it.',table(['Horizon','Opened & funded','End date','Actual days','Method','Official inputs'],date_rows,'Calendar horizons for return scenarios'))
    r=[]
    for a in MODELED:
        for deposit in [10000,25000,100000,240000,250000]:
            status='Above insurance limit after interest' if deposit==250000 else 'Below $250k at 12m under model'
            # Barclays $250k is intentionally excluded: it has a different tier.
            if a['id']=='barclays' and deposit==250000:
                r.append(row([bank(a),D(deposit),blank(),blank(),blank(),blank(),'<span class="pill warn">Excluded: top tier / no headroom</span>',links(['barclays','fdic-faq'])]));continue
            values=[bank(a),D(deposit)]+[M(interest(deposit,a['apy'],(end-OPENED).days)) for _,end in HORIZONS]+[M(deposit*factor(a['apy'],365)),f'<span class="pill{ " warn" if deposit==250000 else ""}">{status}</span>',links(a['sources'][:1]+['fdic-faq'])]
            r.append(row(values))
    result+=panel('Interest by deposit size','Interest earned only in the 3 / 6 / 12-month columns; final column is principal + interest. No bonuses included.',table(['Bank / account','Initial deposit','3m interest','6m interest','12m interest','12m balance','FDIC scenario','Official inputs'],r,'Illustrative interest at different deposits'),'Calculation: P × [(1 + APY/100)^(actual days/365) − 1]. No deposits, withdrawals, taxes or service fees. Daily/monthly posting conventions can cause differences from this APY-equivalent approximation. The $250k rows are stress tests, not recommendations.')
    r=[]
    for a in MODELED:
        for months,end in HORIZONS:
            days=(end-OPENED).days
            bonus=200 if a['id']=='barclays' else 0
            principal=headroom_principal(a['apy'],days,bonus)
            terminal=(principal+bonus)*factor(a['apy'],days)
            r.append(row([bank(a),f'{months}m / {days} days',f'<strong class="num">{M(principal)}</strong>',M(bonus),M(terminal),M(250000-terminal),links(a['sources'][:1]+['fdic-faq'])]))
    result+=panel('Modeled opening principal with retained-interest room','Single depositor, single ownership category, no other deposits at the same legal bank. $1 additional rounding reserve.',table(['Bank / account','Horizon','Modeled principal ceiling','Cash bonus reserve','Upper-bound modeled balance','Room to $250k','Official inputs'],r,'Conditional principal ceilings with interest headroom'),'P = floor-to-cents[(249,999 / growth factor) − cash bonus reserve]. Barclays reserves $200 as if credited on day zero, conservatively allowing growth on it for the entire horizon; this is NOT the actual payout timing. Marcus excludes an unconfirmed referral boost. These ceilings are conditional mathematical bounds, not guarantees; a rising APY or other deposits invalidate them.')
    split=[row(['$250,000','2','Marcus $125k + Barclays $125k',M(250000*1.035),'No bonuses; each $129,375 ending balance.',links(['marcus','barclays','fdic'])]),row(['$500,000','3','Marcus $240k + Barclays $240k + Amex $20k',M(480000*1.035+20000*1.032),'No bonuses; largest ending bank balance $248,400.',links(['marcus','barclays','amex','fdic'])]),row(['$1,000,000','5+ for retained-interest room','Four reviewed banks at $240k + $40k at a fifth distinct insured bank',blank(),'Not a completed allocation: fifth qualifying rate/bank not confirmed; no total return asserted.',links(['marcus','barclays','amex','ally','fdic-faq'])])]
    result+=panel('Larger balance scenarios','Illustrative split allocations, not an assertion about your funds or existing accounts.',table(['Total savings','Distinct banks','Example allocation','12m modeled total','Coverage / caveat','Official inputs'],split,'Illustrative multi-bank allocations'),'Do not treat Capital One and Discover as two independent coverage buckets for newly opened deposits. Four banks at exactly $250,000 each leave no retained-interest room. Ownership categories can change limits, but no joint or trust structure is assumed.')
    r=[]
    for apy,label in [(2.5,'Hypothetical −1 percentage point'),(3.5,'Current confirmed base'),(4.5,'Hypothetical +1 percentage point')]:
        r.append(row([label,P(apy),M(interest(240000,apy,365)),M(240000*factor(apy,365)),links(['marcus','fdic-faq'])]))
    result+=panel('Rate sensitivity — not a forecast','A constant-rate 12-month illustration on $240,000. Only the middle rate is the confirmed Marcus base quote.',table(['Scenario','Assumed APY','Modeled interest','Ending balance','Input / coverage sources'],r,'Hypothetical rate sensitivity'),'Rates may also change part-way through the year; these simple scenarios are not bank offers. At 4.50%, $240k grows beyond the $250k limit. Keep a practical buffer or move accrued earnings to another distinct insured bank; transfers and holds must be considered.')
    result+=notice('Competitive context: the direct FDIC national savings rate is <strong>0.38% as of October 19, 2026</strong>, a deposit-weighted benchmark rather than a best-market APY. Confirmed quotes here are 2.72–3.12 percentage points above that benchmark. <a href="https://www.fdic.gov/national-rates-and-rate-caps">Official benchmark ↗</a> · <a href="sources.html">Calculation assumptions →</a>',True)
    return result


def bonuses():
    result=heading('READ THE RULES, NOT JUST THE REWARD','Bonuses & promotions','Two offers were confirmed in inspected official content. No bonus is assumed to be available to you personally. Other offers remain blank and unverified—not “none.”')
    r=[row(['Barclays Tiered Savings','<strong>$200 cash</strong>','$25,000 from other institution(s)','Open through 2026-10-31; fund within first 30 days; hold at least $25,000 for 120 consecutive days starting when threshold is met.','New customers only; current and previous Barclays Savings/CD customers excluded. Bonus approximately 60 days after hold. Withdrawals below threshold can disqualify; offer subject to change/cancellation.','Taxable interest; no exact payment date promised.',links(['barclays'])]),row(['Marcus Online Savings','<strong>+1.00 percentage point APY</strong> for 3 months',blank(),'New customers need a unique referral link and no Marcus OSA/CD in last 12 months. Start within 1 business day of qualifying opening.','Base APY remains variable. Existing customer may earn boosts via successful new-customer referrals. One active boost, four may queue; not simultaneous stacking. No link has been obtained.','Conditional current boosted APY = 4.50% (3.50 + 1.00); returns to then-current base after 3 months. Not a cash bonus.',links(['marcus-bonus'])])]
    result+=panel('Confirmed offer terms','The numerical deposit requirement for the Marcus referral promotion was not established in the inspected terms; it remains blank.',table(['Account','Reward','Offer deposit threshold','Timing','Eligibility / exclusions','Rate or tax treatment','Official terms'],r,'Verified promotional offer terms','long-table'))
    result+=notice('<strong>Barclays timeline if opened October 22:</strong> 30 days later is November 21, 2026 (calendar arithmetic, not an extension). If $25,000 qualifies on opening day, the 120-day interval ends February 19, 2027; the bank says payout is approximately 60 days after that. Do not treat April 20 as a guaranteed payment date. If funding is delayed, the hold and payout move later. <a href="https://banking.us.barclays/tiered-savings.html">Official timing terms ↗</a>')
    r=[]
    for deposit in [25000,100000,240000]:
        base=interest(deposit,3.5,365)
        cash=base+200
        boosted=deposit*(referral_factor(365)-1)
        r.append(row([D(deposit),M(base),M(cash),P(cash/deposit*100),M(boosted),P(boosted/deposit*100),links(['barclays','marcus','marcus-bonus'])]))
    result+=panel('12-month conditional outcome comparison','Opening/funding October 22, 2026 → October 22, 2027 (365 days). These are OUR calculations, not official yield quotes.',table(['Deposit','3.50% base interest','Barclays interest + $200','Simple total / deposit','Marcus one-boost interest','Modeled annual return','Official inputs'],r,'Conditional annual promotion comparisons'),'Barclays assumes eligible and bonus received by year-end; excludes any interest on the bonus and assumes 3.50% throughout. The displayed percentage is total gain divided by initial deposit, not an official APY. Marcus scenario assumes successful referral, one day at 3.50%, 92 days at 4.50% from Oct 23–Jan 23, remaining days at 3.50%. Actual activation dates and compounding may differ; no referral is assumed in the base rankings.')
    r=[]
    for months,end in HORIZONS:
        days=(end-OPENED).days
        r.append(row([f'{months}m / {days} days',M(interest(25000,3.5,days)),M(25000*(referral_factor(days)-1)),('$200, only if paid by this horizon' if months==12 else blank()),('Do not assume cash received yet' if months<12 else 'Conditional, not a promised payment date'),links(['barclays','marcus-bonus'])]))
    result+=panel('Shorter horizons on $25,000','Shows why temporary boosts and delayed cash offers should not be annualized as permanent savings rates.',table(['Horizon','Base interest','Marcus referral scenario','Barclays cash counted','Payout caveat','Official inputs'],r,'Promotion horizon comparison'),'At 3 and 6 months, no Barclays cash bonus is included because payout is not guaranteed by those dates. No early closure is recommended before qualification and payment terms are satisfied.')
    r=[row([E(a['bank']),E(a['product']),blank(),'<span class="pill warn">Promotion unverified</span>',links(a['sources'][:1])]) for a in accounts if not a['bonus']]
    result+=panel('Remaining promotion checks','No public savings-specific offer confirmed in the inspected material. This is not proof no targeted offer exists.',table(['Bank','Account','Confirmed bonus','Status','Official page inspected'],r,'Unverified promotions'))
    result+=notice('Decision rule for this shortlist: <strong>Barclays is a candidate for the verified cash offer if you meet every condition.</strong> Marcus is a tied base-rate candidate and its referral scenario can be more valuable at larger balances, but a qualifying link and eligibility are unresolved. Amex and Ally have lower confirmed base quotes, not guaranteed lower future returns.',True)
    return result


def protection():
    result=heading('SECURITY, COVERAGE & ELIGIBILITY','Protect the balance. Know the rules.','FDIC coverage protects eligible deposits in a bank failure; it is not the same as fraud protection. Security controls below are bank-published representations, not an independent security audit.')
    coverage=[row(['Standard limit','$250,000 per depositor, per FDIC-insured bank, per ownership category.','Includes principal and accrued interest; same-bank checking, savings and CDs in same category aggregate.',links(['fdic','fdic-faq'])]),row(['Multiple banks','Separate insured banks can provide separate limits.','Confirm the legal bank, not just brand or app name. Newly opened Capital One/Discover deposits count together.',links(['fdic','capital'])]),row(['Joint / trust categories','Different qualifying ownership categories may create different coverage.','No personal joint/trust arrangement assumed; no claim your personal maximum is exactly $250,000 overall.',links(['fdic'])]),row(['Existing deposits','No existing deposits is an explicit modeling assumption only.','Subtract all existing same-bank, same-category deposits plus expected accrued interest before applying headroom numbers.',links(['fdic-faq','marcus-fdic'])])]
    result+=panel('The insurance rules used in the models','Single-owner single-category examples are intentionally conservative and do not invent a household structure.',table(['Rule','Verified fact','Practical implication','Official source'],coverage,'FDIC coverage rules'))
    r=[]
    for a in accounts:
        r.append(row([bank(a),cell(a['app']),cell(a['security']),cell(a['fdic']),'<span class="pill warn">Published features only</span><small>Not a security score or approval</small>',links(a['sources'])]))
    result+=panel('Mobile access & documented protections','Blank authentication cells mean specific controls were not established, even if an app is available.',table(['Bank / account','Mobile app','Verified security features','FDIC / aggregation note','Assessment boundary','Official evidence'],r,'Apps, security evidence and deposit insurance','long-table'),'No claim that a bank is “safe” solely because it has an app or FDIC insurance. Confirm device support, enable available MFA/alerts, secure your email and report suspected unauthorized transactions promptly.')
    r=[row([bank(a),cell(a['opening']),cell(a['minimum'],True),cell(a['access']),'<a href="flagged.html">Review incomplete eligibility / geography</a>',links(a['sources'])]) for a in accounts]
    result+=panel('Opening rules & access constraints','Only facts present in inspected official content appear here. Full account agreements control and banks may decline applications.',table(['Bank / account','Confirmed opening rules','Opening minimum','Access & operational constraints','Review','Official sources'],r,'Opening and account access requirements','long-table'))
    result+=notice('This project required no manual input from you. It did not—and cannot—verify your personal approval, existing balances or ownership category without information you have not provided. No credentials, applications, transfers or account openings were initiated.',True)
    return result


def flagged():
    result=heading('TRANSPARENCY REGISTER','Flagged for Review','Unresolved facts are visible and do not block publication. Numerical values that cannot be confirmed remain blank in the comparison. Every review item links back to official evidence.')
    r=[]
    for f in flags:
        r.append(row([f'<span class="pill warn">{E(f["severity"])}</span>',f'<strong>{E(f["title"])}</strong><small>{E(f["id"])}</small>',E(f['detail']),'<span class="pill neutral">Needs review</span><small>Checked 2026-10-22</small>',links(f['sources'])],f'id="{E(f["id"])}"'))
    result+=panel(f'{len(flags)} published review items','No missing number has been replaced with zero or an estimate.',table(['Type','Finding','What was found / treatment','Status','Official evidence'],r,'Published irregularities and unresolved facts'),'Needs review means published for later inspection, not a hidden build failure.')
    return result


def methodology():
    result=heading('A TRACEABLE RESEARCH SNAPSHOT','Sources & methodology','Checked October 22, 2026 (UTC). Evidence selections, publisher dates, calculation assumptions and limitations are published for manual review. No third-party ranking is used as a bank-origin rate quote.')
    result+='<div class="grid-two"><section class="card"><h2>What “verified” means here</h2><p>A field was read on the linked official bank or FDIC page. Publisher dates are kept distinct from the date checked. This is a manual, field-level research snapshot—not independent certification, a security audit, a signed bank quote or real-time data.</p><p>Evidence excerpts are selected passages/transcriptions, not complete archived pages. Official content can change, be personalized, be stale, or fail to render.</p></section><section class="card"><h2>What this shortlist includes</h2><p>12 products across 11 major bank groups, covering national branch brands and national digital savings brands. No local-only banks, fintech pass-throughs or brokerage sweeps. Distribution categories are editorial groupings, not bank charter classifications.</p><p>Not an exhaustive census. “Highest confirmed” always refers to unambiguous quotes in this reviewed shortlist, not the entire market.</p></section></div>'
    result+=panel('Calculation contract','Modeled returns are intentionally labeled, so they cannot be confused with verified financial facts.','<div class="card"><div class="formula">growth = (1 + APY / 100) ^ (actual elapsed days / 365)<br>interest = principal × (growth − 1)<br>headroom principal = floor_to_cents[(249,999 / growth) − reserved cash bonus]</div><ul><li>Opening and immediate full funding are assumed October 22, 2026. Horizons are January 22, April 22 and October 22, 2027: 92, 182 and 365 days. These are calendar calculations, not bank deadlines.</li><li>APY already reflects compounding. Do not divide APY by 365 and compound again. Fractional-year APY powers are an approximation; bank day-count, posting, funding holds and rounding can change actual earnings.</li><li>APYs stay constant only for illustration. No new deposits, withdrawals or taxes; no unverified bonuses included in base returns. Confirmed modeled products have no monthly maintenance fee; optional service fees are not modeled.</li><li>FDIC example: one depositor, one ownership category, no other same-bank deposits, no assumed beneficiaries. $1 reserve beyond flooring reduces rounding risk; it does not protect against rate changes or unknown deposits.</li><li>Barclays uses 3.50% below $250,000. The $250,000+ tier cannot be retained-interest fully insured under this scenario. Headroom table conservatively reserves $200 at day zero; actual bonus payment is delayed and conditional.</li><li>Marcus referral model is a separate hypothetical successful-referral scenario: Oct 22 at 3.50%, Oct 23–Jan 23 (92 days) at 4.50%, then 3.50%. Assumes one-day activation; actual timing can differ. Base models do not assume a referral.</li><li>Barclays 12-month offer comparison adds $200 only if paid by then, with no modeled interest on the cash. Total gain / deposit is a simple scenario return, not a quoted APY.</li><li>Benchmark uses the direct FDIC October 19 savings national rate of 0.38%. It is deposit-weighted, not an offer available to open or the regulatory rate cap. Percentage-point spreads are calculations, not bank marketing claims.</li><li>Missing values remain null in JSON and empty in numeric cells, with accessible labels and review status. No exact ZIP, personal eligibility or existing banking relationship is assumed.</li></ul><p class="source-note">Official inputs and coverage guidance:</p>'+links(['marcus','barclays','amex','ally','fdic','fdic-faq','benchmark'])+'</div>')
    r=[]
    for s in sources:
        r.append(row([f'<strong>{E(s["id"])}</strong><small>Checked {s["checked"]}</small>',E(s['asOf']) if s['asOf'] else blank(),f'<strong>{E(s["title"])}</strong><p>{E(s["excerpt"])}</p>'+ (f'<p class="source-note">Review note: {E(s["note"])}</p>' if s['note'] else ''),f'<a class="source-url" href="{E(s["url"])}" target="_blank" rel="noopener noreferrer">Official source ↗</a>'],f'id="{E(s["id"])}"'))
    result+=panel(f'{len(sources)} official evidence records','Publisher date blank = no relevant effective date established. Not all sources state a rate; some document missing or conflicting values.',table(['Evidence ID / read date','Publisher date','Selected evidence / treatment','Manual review'],r,'Official source evidence ledger','sources-table'))
    result+='<div class="grid-two"><section class="card"><h2>Reproducible data</h2><p><a href="../data/accounts.csv" download>Account comparison CSV ↓</a><br><a href="../data/accounts.json">Account JSON</a> · <a href="../data/sources.json">Source JSON</a> · <a href="../data/flags.json">Review JSON</a><br><a href="../research/VERIFICATION.md">Row-by-row verification notes</a></p><p>One set of structured inputs drives every page. No account information or user data is collected or transmitted by the site.</p></section><section class="card"><h2>Maintaining the snapshot</h2><p>Recheck official pages, resolve region-dependent disclosures, update evidence with read and effective dates, and run the build and tests before publishing a new snapshot. The site never changes rate dates without source review.</p><p>Use the coordination board to claim non-overlapping work. A failed or unresolved source remains flagged rather than silently replaced.</p></section></div>'
    return result


def build():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    shutil.copytree(ROOT/'data',OUT/'data',dirs_exist_ok=True)
    shutil.copytree(ROOT/'research',OUT/'research',dirs_exist_ok=True)
    with (OUT/'data/accounts.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['bank','account','category','apy_percent','rate_as_of','checked','opening_minimum_usd','monthly_fee_usd','fee_waiver','confirmed_offer','app','security','fdic_note','opening_rules','access','review_flags','official_sources'])
        for a in accounts:
            writer.writerow([a['bank'],a['product'],a['category'],a['apy'],a['rateAsOf'],'2026-10-22',a['minimum'],a['monthlyFee'],a['waiver'],a['bonus'],a['app'],a['security'],a['fdic'],a['opening'],a['access'],'; '.join(a['flags']),' | '.join(S[x]['url'] for x in dict.fromkeys(a['sources']+a['bonusSources']))])
    for path,title,fn in [('index.html','Overview',overview),('pages/accounts.html','Account comparison',comparison),('pages/returns.html','Returns & FDIC plan',returns),('pages/bonuses.html','Bonuses & promotions',bonuses),('pages/protection.html','Security & opening',protection),('pages/flagged.html','Flagged for Review',flagged),('pages/sources.html','Sources & methodology',methodology)]:
        page(path,title,fn())
    (OUT/'.nojekyll').write_text('')
    print(f'Built 7 pages, {len(accounts)} products, {len(sources)} evidence records, {len(flags)} review items in {OUT}')

if __name__=='__main__':
    build()
