# -*- coding: utf-8 -*-
"""
Trim the three page titles Bing flagged as too long, plus the descriptions that
run past 160 characters. Keeps the JSON-LD untouched (it carries the article
headline, which is separate from the SEO title).
"""
import io
import os
import re
import sys

ROOT = os.getcwd()

TITLES = {
    "index.html": ("Custom Denim Manufacturer: MOQ 150, Samples 10-15 Days | Zuoyu",
                   "Denim Manufacturer: MOQ 150, 10-15 Day Samples | Zuoyu"),
    "factory-certifications/index.html": (
        "Factory &amp; Certifications: SMETA, GCC, RoHS | Zuoyu Garment",
        "Factory Certifications: SMETA, GCC, RoHS | Zuoyu"),
    "blog/custom-denim-jacket-moq/index.html": (
        "Custom Denim Jacket Manufacturer: What MOQ 150 Actually Means",
        "Denim Jacket MOQ 150: What It Actually Means | Zuoyu"),
}

DESCRIPTIONS = {
    "cases/index.html": 158,
    "blog/denim-weight-guide/index.html": 158,
    "privacy-policy/index.html": 158,
    "blog/custom-denim-jacket-moq/index.html": 158,
}


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


def main():
    changed = 0

    for rel, (old, new) in TITLES.items():
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            print("missing", rel)
            continue
        s = rd(p)
        if old not in s:
            print("  title not found (already changed?):", rel)
            continue
        s = s.replace(old, new, 1)
        # keep the social title in step with the page title
        s = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                   r'\g<1>' + new.replace("&amp;", "&amp;") + r'\g<2>', s, count=1)
        wr(p, s)
        changed += 1
        print("title trimmed: %-40s %d -> %d chars" % (rel, len(old), len(new)))

    # shorten over-long meta descriptions by cutting at a sentence boundary
    for rel, limit in DESCRIPTIONS.items():
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            continue
        s = rd(p)
        m = re.search(r'<meta name="description" content="(.*?)">', s)
        if not m:
            print("  no description:", rel)
            continue
        old = m.group(1)
        if len(old) <= limit:
            print("  description fine:", rel, len(old))
            continue
        cut = old[:limit]
        # prefer to end on a full stop or a comma
        for sep in (". ", "; ", ", "):
            idx = cut.rfind(sep)
            if idx > limit * 0.6:
                cut = cut[:idx].rstrip() + "."
                break
        else:
            cut = cut.rsplit(" ", 1)[0] + "."
        s = s[:m.start(1)] + cut + s[m.end(1):]
        wr(p, s)
        changed += 1
        print("description trimmed: %-38s %d -> %d chars" % (rel, len(old), len(cut)))

    print("files changed:", changed)

    # verify
    over_t = over_d = 0
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            h = rd(os.path.join(dp, f))
            t = re.search(r"<title>(.*?)</title>", h)
            d = re.search(r'<meta name="description" content="(.*?)">', h)
            if t and len(t.group(1)) > 60:
                over_t += 1
                print("  still long title:", f, len(t.group(1)))
            if d and len(d.group(1)) > 160:
                over_d += 1
    print("titles over 60:", over_t, "| descriptions over 160:", over_d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
