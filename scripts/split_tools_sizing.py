# -*- coding: utf-8 -*-
"""
Stop /tools/ and /tools/denim-size-chart/ from duplicating the same six tables.

Problem: both pages carried the full size-chart block, so the same content competes
against itself ("denim size chart" has two candidate URLs), and the finder had to be
maintained twice.

Result after this patch:
  /tools/                  three calculators + a card that links to the size chart
  /tools/denim-size-chart/ the single sizing page (untouched, already working)
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
TOOLS = os.path.join(ROOT, "tools", "index.html")
SIZE_URL = "/tools/denim-size-chart/"

CARD = """  <section id="sizing"><div class="wrap">
    <h2>4. Size conversion</h2>
    <p>EU, US, UK, Japan and letter sizes for women's tops, trousers, shorts and skirts, and for men's tops and jeans &mdash; with the body measurements we grade from. It lives on its own page so the tables stay readable on a phone.</p>
    <p style="margin-top:1.2rem"><a class="btn btn-ghost" href="%s">Open the denim size chart &rarr;</a></p>
  </div></section>
""" % SIZE_URL


def main():
    if not os.path.isfile(TOOLS):
        print("missing tools/index.html")
        return 1
    s = io.open(TOOLS, encoding="utf-8").read()
    orig = s

    # 1. remove the duplicated sizing section (six tables + finder)
    m = re.search(r'  <section id="sizing">.*?</section>\n', s, re.S)
    if m:
        s = s[:m.start()] + CARD + s[m.end():]
        print("sizing section replaced with a link card")
    elif 'id="sizing"' in s:
        print("WARNING: sizing section found but not matched; leaving untouched")
    else:
        print("sizing section already removed")

    # 2. the tab now points at the standalone page
    s = s.replace('<a href="#sizing">Size conversion</a>',
                  '<a href="%s">Size conversion</a>' % SIZE_URL, 1)

    # 3. drop the finder script (it belongs to the size-chart page now)
    m = re.search(r'<script>\s*\(function\(\)\{\s*"use strict";\s*var cat = document\.getElementById\("sz-cat"\).*?</script>\n?',
                  s, re.S)
    if m:
        s = s[:m.start()] + s[m.end():]
        print("size-finder script removed")

    # 4. title + description: keep the size chart mentioned as a link, not a tool
    s = s.replace("<title>Denim Tools: Costing, oz/GSM, Cartons & Size Chart | Zuoyu</title>",
                  "<title>Denim Tools: Costing, oz/GSM and Cartons | Zuoyu</title>", 1)
    s = s.replace("<title>Denim Tools: Costing, oz to GSM, Cartons, Sizes | Zuoyu</title>",
                  "<title>Denim Tools: Costing, oz/GSM and Cartons | Zuoyu</title>", 1)
    s = re.sub(r'content="Four free tools for denim buyers:[^"]*"',
               'content="Three free calculators for denim buyers: fabric consumption and cost, oz to gsm, and carton/container loading, plus a separate denim size chart."', s, count=1)
    s = re.sub(r'content="Three free tools for denim buyers:[^"]*"',
               'content="Three free calculators for denim buyers: fabric consumption and cost, oz to gsm, and carton/container loading, plus a separate denim size chart."', s, count=1)

    # 5. lede: say what is here and where the sizes went
    s = re.sub(r'(<p class="lede" style="max-width:70ch">)Three calculators buyers and merchandisers use before a quotation: fabric consumption and cost, ounce-to-gram weight with the garment each weight suits, and carton loading with freight per piece\. Free, no signup\.(</p>)',
               r'\1Three calculators buyers and merchandisers use before a quotation: fabric consumption and cost, ounce-to-gram weight with the garment each weight suits, and carton loading with freight per piece. Size tables live on the <a href="/tools/denim-size-chart/">denim size chart</a> page. Free, no signup.\2', s, count=1)

    # 6. schema: the page is still a web app; keep the tools list honest
    s = s.replace('"description": "Free calculators for denim buyers: fabric consumption and cost, oz to gsm conversion with denim weight classes, and carton CBM with container loading and freight per piece."',
                  '"description": "Free calculators for denim buyers: fabric consumption and cost, oz to gsm conversion with denim weight classes, and carton CBM with container loading and freight per piece. Size conversion tables are on a separate page."')

    if s != orig:
        io.open(TOOLS, "w", encoding="utf-8", newline="\n").write(s)
        print("tools/index.html updated | bytes:", len(s))
    else:
        print("tools/index.html unchanged")

    # 7. sitemap lastmod
    import datetime
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    sm_path = os.path.join(ROOT, "sitemap.xml")
    if os.path.isfile(sm_path):
        sm = io.open(sm_path, encoding="utf-8").read()
        sm2, n = re.subn(r'(<loc>https://zuoyugarment\.com/tools/</loc>\s*<lastmod>)([^<]*)(</lastmod>)',
                         lambda m: m.group(1) + today + m.group(3), sm, count=1)
        if n:
            io.open(sm_path, "w", encoding="utf-8", newline="\n").write(sm2)
            print("lastmod bumped for /tools/")

    # 8. verify
    t = io.open(TOOLS, encoding="utf-8").read()
    print("checks -> sz-cat:", t.count('id="sz-cat"'),
          "| size tables:", len(re.findall(r'table class="fact-table size-table"', t)),
          "| size card:", 'Open the denim size chart' in t,
          "| calculators:", t.count('<section id="consumption"') + t.count('<section id="weight"') + t.count('<section id="carton"'))
    bad = []
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            json.loads(blk)
        except Exception as exc:                                # noqa: BLE001
            bad.append(str(exc)[:50])
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
