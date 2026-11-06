# -*- coding: utf-8 -*-
"""
Correct the published price bands so every number can be traced to a live
Alibaba listing.

Store reality (scraped 2026-11-06, 32 products across both storefronts):
  men's jeans       USD 18.00 - 26.00   (15 listings)
  women's jeans     USD 13.99            (1 listing)
  denim jackets     USD 16.57 - 18.67   (1 listing, light unisex jacket)
  denim shirts/tops USD 17.65 - 23.53   (3 listings)
  dresses / skirts  USD 13.97 - 19.12   (10 listings)

The published jacket band (16.50-23.50) had an upper bound with no listing
behind it, so it is replaced by the real range.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()

SWAPS = [
    # jacket band, all dash variants and both edge forms
    ("USD 16.50–23.50", "USD 16.57–18.67"),
    ("USD 16.50-23.50", "USD 16.57-18.67"),
    ("16.50–23.50", "16.57–18.67"),
    ("16.50-23.50", "16.57-18.67"),
    ("From USD 16.50 to 23.50", "From USD 16.57 to 18.67"),
    ('"lowPrice": "16.50"', '"lowPrice": "16.57"'),
    ('"highPrice": "23.50"', '"highPrice": "18.67"'),
    ('"value": "USD 16.50 per piece"', '"value": "USD 16.57 per piece"'),
    # remaining single low bound
    ("from USD 16.50.", "from USD 16.57."),
    ("from USD 16.50 FOB", "from USD 16.57 FOB"),
    ("start at USD 16.50", "start at USD 16.57"),
]

EXPLAIN = ('      <p class="note"><strong>Why a pair of jeans can cost more than a jacket:</strong> '
           'our jacket listings are lightweight (10&ndash;12 oz) unisex styles at USD 16.57&ndash;18.67, '
           'while the standard men&rsquo;s jeans are 12&ndash;14 oz rigid denim with a full wash programme, '
           'which carries more fabric, more laundry time and more panel matching. Heavier or lined jackets '
           'are quoted separately.</p>')


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def main():
    changed = 0
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            s = rd(p)
            original = s
            for old, new in SWAPS:
                s = s.replace(old, new)
            if s != original:
                wr(p, s)
                changed += 1
                print("prices updated:", os.path.relpath(p, ROOT).replace("\\", "/"))
    print("pages changed:", changed)

    # explanation on the jacket page and the jeans page
    for rel, anchor in [
        ("denim-jackets/index.html", '      <h2>Why jackets cost more than their fabric</h2>'),
        ("jeans/index.html", '      <h2>Wash development, not wash guessing</h2>'),
    ]:
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            continue
        s = rd(p)
        if "Why a pair of jeans can cost more than a jacket" in s:
            continue
        if anchor in s:
            s = s.replace(anchor, EXPLAIN + "\n\n" + anchor, 1)
            wr(p, s)
            print("explainer added:", rel)

    # women's jeans note on the jeans page
    p = os.path.join(ROOT, "jeans", "index.html")
    if os.path.isfile(p):
        s = rd(p)
        old = "<tr><th>Price band</th><td>USD 18–26 per piece, FOB Shenzhen, depending on fabric, wash and trim.</td></tr>"
        if old in s and "Women's jeans from" not in s:
            s = s.replace(old, old + "\n          <tr><th>Women's jeans</th><td>From USD 13.99 per piece FOB Shenzhen for the listed women's styles.</td></tr>", 1)
            wr(p, s)
            print("women's jeans note added")

    bad = []
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', rd(p), re.S):
                try:
                    json.loads(block)
                except Exception as exc:                          # noqa: BLE001
                    bad.append((os.path.relpath(p, ROOT), str(exc)[:60]))
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
