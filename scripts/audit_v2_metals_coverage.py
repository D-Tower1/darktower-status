#!/usr/bin/env python3
"""Audit public V2 HTML for truthful metals coverage."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "v2"

METALS = ("XAU_USD", "XAG_USD", "XPT_USD", "XPD_USD")
METAL_LINK_RE = re.compile(
    r"""href\s*=\s*["']?/data/(?:%s)\.html["']?""" % "|".join(METALS),
    re.IGNORECASE,
)

REQUIRED_ACTIVE_LINKS = {
    "forex": "/data/EUR_USD.html",
    "crypto": "/data/BTC_USD.html",
    "stocks": "/data/SPY.html",
}


def read(path):
    return path.read_text(encoding="utf-8")


def fail(message):
    print(f"FAIL: {message}")
    return False


def main():
    ok = True
    v2_html = sorted(V2.glob("*.html"))

    for path in v2_html:
        text = read(path)
        if METAL_LINK_RE.search(text):
            ok = fail(f"active metals chart link found in {path.relative_to(ROOT)}")

    metals_page = read(V2 / "metals.html").lower()
    for word in ("planned", "pending", "parked"):
        if word not in metals_page:
            ok = fail(f"v2/metals.html is missing {word!r} coverage language")

    for market, link in REQUIRED_ACTIVE_LINKS.items():
        found = any(link in read(path) for path in v2_html)
        if not found:
            ok = fail(f"missing active {market} chart link {link} in V2 HTML")

    if ok:
        print("PASS: V2 metals coverage audit")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
