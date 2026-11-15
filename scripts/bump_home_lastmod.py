# -*- coding: utf-8 -*-
"""
Bump the homepage lastmod in sitemap.xml.

The homepage was edited today (Buyer guides block) but its sitemap entry still
says 2026-10-31. Bing and Google both use lastmod as a re-crawl hint, so a page
that changed without a lastmod bump can sit in the queue for weeks.
"""
import datetime
import io
import os
import re
import sys

ROOT = os.getcwd()
SITEMAP = os.path.join(ROOT, "sitemap.xml")
HOME = "https://zuoyugarment.com/"


def main():
    if not os.path.isfile(SITEMAP):
        print("ERROR: sitemap.xml not found")
        return 1
    s = io.open(SITEMAP, encoding="utf-8").read()
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    changed = 0
    for target in [HOME, HOME.rstrip("/")]:
        pattern = re.compile(
            r'(<loc>%s</loc>\s*<lastmod>)([^<]*)(</lastmod>)' % re.escape(target))
        if pattern.search(s):
            s, n = pattern.subn(lambda m: m.group(1) + today + m.group(3), s, count=1)
            changed += n
            print("lastmod set to %s for %s" % (today, target))
            break

    if not changed:
        print("WARNING: homepage entry not found in the expected shape")
        # fall back: insert lastmod after the loc if missing
        pattern = re.compile(r'(<loc>%s</loc>)(?!\s*<lastmod>)' % re.escape(HOME))
        if pattern.search(s):
            s = pattern.sub(r'\g<1><lastmod>%s</lastmod>' % today, s, count=1)
            changed = 1
            print("lastmod inserted for", HOME)

    if changed:
        io.open(SITEMAP, "w", encoding="utf-8", newline="\n").write(s)

    # report the homepage entry and the URL count
    m = re.search(r'<loc>%s</loc>\s*<lastmod>([^<]+)</lastmod>' % re.escape(HOME), s)
    print("homepage lastmod now:", m.group(1) if m else "MISSING")
    print("sitemap urls:", s.count("<loc>"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
