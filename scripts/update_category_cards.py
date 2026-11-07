# -*- coding: utf-8 -*-
"""
Replace the four homepage category cards with model photos of the actual
best-selling styles, and align the copy with what the photo shows.

  jeans    -> light-wash wide-leg jeans on a model
  jackets  -> eyelet lace-up denim jacket
  dresses  -> black denim pinafore / overall dress
  shirts   -> men's dark denim work shirt
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()

CARDS = [
    {
        "old_img": "product-jeans-2.jpg",
        "img": "cat-jeans", "w": 1000, "h": 1000,
        "alt": "Light-wash wide-leg custom denim jeans produced by Zuoyu Garment",
        "spec_old": "Rigid · comfort-stretch · high-stretch<br>Waist 24–44",
        "spec_new": "Wide-leg · straight · baggy<br>Waist 24–44",
        "para_old": "Custom 5-pocket jeans in men's, women's and unisex fits — straight, slim, relaxed, wide-leg, mom, barrel and utility blocks.",
        "para_new": "Custom 5-pocket jeans in men's, women's and unisex fits — wide-leg, straight, baggy, mom, barrel and utility blocks, in rigid and stretch denim.",
    },
    {
        "old_img": "product-jacket-1.jpg",
        "img": "cat-jackets", "w": 450, "h": 450,
        "alt": "Custom eyelet lace-up denim jacket produced by Zuoyu Garment",
        "spec_old": "Trucker · overshirt · chore<br>Matched sets on request",
        "spec_new": "Trucker · overshirt · eyelet lace-up<br>Matched sets on request",
        "para_old": "Trucker jackets, overshirts, chore jackets and denim skirts — including coordinated jacket-and-skirt sets washed against one standard.",
        "para_new": "Trucker jackets, overshirts, chore jackets and eyelet lace-up styles — including coordinated jacket-and-skirt sets washed against one standard.",
    },
    {
        "old_img": "product-dress-1.jpg",
        "img": "cat-dresses", "w": 1000, "h": 1000,
        "alt": "Custom black denim pinafore dress produced by Zuoyu Garment",
        "spec_old": "Shirt · pinafore · slip-bib<br>EU 34–46",
        "spec_new": "Pinafore · overall · shirt dress<br>EU 34–46",
        "para_old": "Shirt dresses, pinafores, slip-bib and tailored denim dresses, with wash and hardware programmes developed in-house.",
        "para_new": "Denim pinafore and overall dresses, shirt dresses, slip-bib and tailored styles, with wash and hardware programmes developed in-house.",
    },
    {
        "old_img": "product-shirt-2.jpg",
        "img": "cat-shirts", "w": 1000, "h": 1000,
        "alt": "Men's dark denim work shirt produced by Zuoyu Garment",
        "spec_old": "Overshirt · work shirt · pullover<br>S–XXL",
        "spec_new": "Work shirt · overshirt · shirt-jacket<br>S–XXL",
        "para_old": "Button-down overshirts, work shirts, pullover tops and shirt-jackets in 4–8 oz shirting denim, washed against one sealed standard.",
        "para_new": "Men's and women's denim shirts: work shirts, button-down overshirts, pull-over tops and shirt-jackets in 4–8 oz shirting denim.",
    },
]


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def main():
    p = os.path.join(ROOT, "index.html")
    s = rd(p)
    changed = 0
    for c in CARDS:
        # 1. the image block
        img_re = re.compile(
            r'<div class="card-img"><img[^>]*src="/assets/img/%s"[^>]*></div>' % re.escape(c["old_img"]))
        m = img_re.search(s)
        if not m:
            print("  image block not found:", c["old_img"])
            continue
        new_img = ('<div class="card-img"><img decoding="async" src="/assets/img/%s.jpg" '
                   'alt="%s" loading="lazy" width="%d" height="%d" '
                   'style="width:100%%;aspect-ratio:1/1;object-fit:cover"></div>'
                   % (c["img"], c["alt"], c["w"], c["h"]))
        s = s[:m.start()] + new_img + s[m.end():]
        changed += 1
        # 2. the two text lines
        if c["spec_old"] in s:
            s = s.replace(c["spec_old"], c["spec_new"], 1)
        else:
            print("  spec not found for", c["img"])
        if c["para_old"] in s:
            s = s.replace(c["para_old"], c["para_new"], 1)
        else:
            print("  paragraph not found for", c["img"])
        print("  card updated:", c["img"])

    if changed:
        wr(p, s)
    print("cards changed:", changed)

    # the section still says "three" categories but there are four cards
    s = rd(p)
    if "Three denim categories" in s:
        wr(p, s.replace("Three denim categories", "Four denim categories", 1))
        print("heading updated: Four denim categories")

    bad = []
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', rd(p), re.S):
        try:
            json.loads(blk)
        except Exception as exc:                              # noqa: BLE001
            bad.append(str(exc)[:60])
    print("invalid JSON-LD on homepage:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
