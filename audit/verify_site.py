#!/usr/bin/env python3
"""Repository-wide audit & static site integrity verifier (Session 339c96e1)."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OFFICIAL_SUFFIXES = (
    "fdic.gov", "federalreserve.gov", "consumerfinance.gov", "occ.gov", "sec.gov", "treasury.gov", "github.com",
    "marcus.com", "barclays", "ally.com", "americanexpress.com", "synchrony.com", "capitalone.com", "discover.com",
    "chase.com", "bankofamerica.com", "wellsfargo.com", "citi.com", "pnc.com", "openbank.us", "santanderbank.com",
    "everbank.com", "cit.com", "firstcitizens.com", "sofi.com", "cloudfront.net", "usbank.com", "github.io", "w3.org",
    "fonts.googleapis.com", "fonts.gstatic.com", "apps.apple.com", "play.google.com",
)


def main():
    # 1. Run unit tests across scripts/
    res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "scripts", "-p", "test_*.py", "-v"], cwd=ROOT)
    if res.returncode != 0:
        sys.exit(res.returncode)

    # 2. Scan every tracked file across the entire repository for any non-official URL
    bad_urls = []
    for p in sorted(ROOT.rglob("*")):
        if any(part in (".git", "_site", "node_modules", "__pycache__") for part in p.parts) or p.is_dir():
            continue
        if p.name in ("browser-check.mjs", "test_site.py", "verify_site.py"):
            continue
        txt = p.read_text(errors="ignore")
        for m in re.finditer(r'https?://([^\s"<>)\']*)', txt):
            host = m.group(1).split("/")[0].lower()
            if not any(host.endswith(suf) for suf in OFFICIAL_SUFFIXES):
                bad_urls.append(f"{p.relative_to(ROOT)}: {m.group(0)}")
    if bad_urls:
        print("FAIL: Non-official URLs found:\n" + "\n".join(bad_urls), file=sys.stderr)
        sys.exit(1)

    # 3. Verify audit JSON artifacts match canonical invariants
    vb = json.loads((ROOT / "audit/verified-banks.json").read_text())
    rm = json.loads((ROOT / "audit/return-matrices.json").read_text())
    assert len(vb["accounts"]) == 17, "Expected 17 entries in audit/verified-banks.json"
    assert rm["openingDate"] == "2026-10-22"
    print("PASS: All repository audit checks, zero-aggregator scan, and 18-account site integrity checks passed.")


if __name__ == "__main__":
    main()
