# -*- coding: utf-8 -*-
"""
Point three existing pages at the new /tools/denim-size-chart/ page.

The size chart page is new, so it has no inbound links from the older pages yet.
These are the pages where a reader is most likely to want measurements:
  * the denim weight guide (weight -> what it fits -> sizes)
  * the denim shirts category page
  * the jeans category page
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
URL = "/tools/denim-size-chart/"

LINK_TEXT = "denim size chart"
ARTICLE_ITEM = '<li><a href="%s">Denim size chart: EU, US, UK and Japan measurements</a></li>' % URL


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


def main():
    changed = []

    # 1. weight guide: add a list item after the toolkit link in "Where to go next"
    p = os.path.join(ROOT, "blog", "denim-weight-guide", "index.html")
    if os.path.isfile(p):
        s = rd(p)
        if URL not in s:
            anchor = '<li><a href="/tools/">Denim costing toolkit: consumption, oz to gsm, cartons</a></li>'
            if anchor in s:
                s = s.replace(anchor, anchor + ARTICLE_ITEM, 1)
                wr(p, s)
                changed.append("blog/denim-weight-guide/")
            else:
                print("weight guide: toolkit list item not found")

    # 2 + 3. category pages: extend the "Related:" line
    for rel, needle in (("denim-shirts", "/denim-dresses/"), ("jeans", "/denim-jackets-and-skirts/")):
        p = os.path.join(ROOT, rel, "index.html")
        if not os.path.isfile(p):
            print("missing", rel)
            continue
        s = rd(p)
        if URL in s:
            continue
        m = re.search(r'(<p style="margin-top:2rem">Related:.*?)(</p>)', s, re.S)
        if not m:
            print(rel, ": Related line not found")
            continue
        block = m.group(1)
        s = s[:m.start(1)] + block + ' &middot; <a href="%s">%s</a> ' % (URL, LINK_TEXT) + s[m.start(2):]
        wr(p, s)
        changed.append("%s/" % rel)

    print("pages changed:", changed)

    # lastmod bump
    import datetime
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    sm_path = os.path.join(ROOT, "sitemap.xml")
    if os.path.isfile(sm_path):
        sm = rd(sm_path)
        for rel in ("/blog/denim-weight-guide/", "/denim-shirts/", "/jeans/"):
            sm, n = re.subn(r'(<loc>https://zuoyugarment\.com%s</loc>\s*<lastmod>)([^<]*)(</lastmod>)' % re.escape(rel),
                            lambda m: m.group(1) + today + m.group(3), sm, count=1)
            if n:
                print("lastmod bumped:", rel)
        wr(sm_path, sm)

    # sanity: json-ld still valid, links present
    bad = []
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            fp = os.path.join(dp, f)
            for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', rd(fp), re.S):
                try:
                    json.loads(blk)
                except Exception as exc:                        # noqa: BLE001
                    bad.append((os.path.relpath(fp, ROOT), str(exc)[:50]))
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
