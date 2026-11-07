# -*- coding: utf-8 -*-
"""
Bring the four category pages in line with the homepage cards: three photos of
the actual styles per category (model + detail / flat), instead of the old
mixed product-and-factory strip.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()

PAGES = {
    "jeans/index.html": {
        "imgs": ["cat-jeans-1.jpg", "cat-jeans-2.jpg", "cat-jeans-3.jpg"],
        "alts": ["Light-wash wide-leg custom jeans on a model",
                 "Front view of the wide-leg jeans, showing rise and leg opening",
                 "Back view of the wide-leg jeans with clean pocket detailing"],
        "note": "Wide-leg jeans from our womenswear line — front, leg opening and back detail",
    },
    "denim-jackets/index.html": {
        "imgs": ["cat-jackets-1.jpg", "cat-jackets-2.jpg", "cat-jackets-3.jpg"],
        "alts": ["Custom eyelet lace-up denim jacket on a model",
                 "Side view of the eyelet lace-up jacket showing the tie detail",
                 "Front view of the eyelet lace-up denim jacket"],
        "note": "An eyelet lace-up denim jacket from our own production — front, tie detail and back",
    },
    "denim-dresses/index.html": {
        "imgs": ["cat-dresses-1.jpg", "cat-dresses-2.jpg", "cat-dresses-3.jpg"],
        "alts": ["Black denim pinafore dress on a model",
                 "Full-length view of the pinafore dress",
                 "Back view of the pinafore dress with cross straps"],
        "note": "A denim pinafore from our womenswear line — front, full length and back straps",
    },
    "denim-shirts/index.html": {
        "imgs": ["cat-shirts-1.jpg", "cat-shirts-2.jpg", "cat-shirts-3.jpg"],
        "alts": ["Men's dark denim work shirt on a model",
                 "Men's mid-wash denim shirt, buttoned",
                 "Flat view of the men's denim work shirt"],
        "note": "Men's and women's denim shirts from our own production — worn, buttoned and flat",
    },
}

LEDE_FIXES = [
    ("Overshirts, work shirts, pullover tops and shirt-jackets. Shirting denim is a different discipline",
     "Men's and women's denim shirts: work shirts, overshirts, pullover tops and shirt-jackets. Shirting denim is a different discipline"),
    ("Trucker, overshirt, chore and biker blocks. Jackets are the category",
     "Trucker, overshirt, chore and biker blocks, plus eyelet lace-up detail. Jackets are the category"),
]

GALLERY = """<div class="gallery">
        <img decoding="async" src="/assets/img/%s" alt="%s" loading="lazy" width="1000" height="1000">
        <img decoding="async" src="/assets/img/%s" alt="%s" loading="lazy" width="1000" height="1000">
        <img decoding="async" src="/assets/img/%s" alt="%s" loading="lazy" width="1000" height="1000">
      </div>"""


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def main():
    changed = 0
    for rel, cfg in PAGES.items():
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            print("missing", rel)
            continue
        s = rd(p)
        o = s
        gallery = GALLERY % (cfg["imgs"][0], cfg["alts"][0],
                             cfg["imgs"][1], cfg["alts"][1],
                             cfg["imgs"][2], cfg["alts"][2])
        s = re.sub(r'<div class="gallery gallery-wide">.*?</div>', gallery, s, count=1, flags=re.S)
        if s == o:
            print("  WARNING: gallery not replaced on", rel)
        # figure note
        s = re.sub(r'(<p class="figure-note">)[^<]*(</p>)', r'\g<1>' + cfg["note"] + r'\g<2>', s, count=1)
        if s != o:
            wr(p, s)
            changed += 1
            print("gallery updated:", rel)

    for rel in ["denim-shirts/index.html", "denim-jackets/index.html"]:
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            continue
        s = rd(p)
        o = s
        for a, b in LEDE_FIXES:
            s = s.replace(a, b)
        if s != o:
            wr(p, s)
            print("copy updated:", rel)

    print("pages changed:", changed)

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
                except Exception as exc:                    # noqa: BLE001
                    bad.append((os.path.relpath(fp, ROOT), str(exc)[:60]))
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
