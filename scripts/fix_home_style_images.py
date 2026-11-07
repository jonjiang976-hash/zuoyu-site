# -*- coding: utf-8 -*-
"""
Point the homepage style cards at the new exact product photos.

The four cards were still using the placeholder file names (style-<slug>.jpg)
while the refreshed SKU pages use the two-angle files (style-<slug>-1.jpg).
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()

CARDS = {
    "style-wide-leg": (662, 662, "Custom light-wash wide-leg jeans with a clean hem"),
    "style-straight": (1100, 1100, "Custom straight-leg jeans with a patchwork panel across the leg"),
    "style-cargo": (750, 750, "Custom cargo jeans with side utility pockets"),
    "style-shorts": (1069, 1100, "Custom dark-wash denim shorts with a frayed hem"),
}

NEW_TAG = ('<img decoding="async" src="/assets/img/%(img)s-1.jpg" '
           'srcset="/assets/img/%(img)s-1.jpg %(w)dw" '
           'sizes="(max-width: 700px) 100vw, 33vw" alt="%(alt)s" loading="lazy" '
           'width="%(w)d" height="%(h)d" '
           'style="width:100%%;aspect-ratio:1/1;object-fit:cover">')


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def main():
    p = os.path.join(ROOT, "index.html")
    s = rd(p)
    changed = 0
    for img, (w, h, alt) in CARDS.items():
        pattern = re.compile(r'<img[^>]*src="/assets/img/%s\.jpg"[^>]*>' % re.escape(img))
        m = pattern.search(s)
        if not m:
            print("  not found:", img)
            continue
        tag = NEW_TAG % {"img": img, "w": w, "h": h, "alt": alt}
        s = s[:m.start()] + tag + s[m.end():]
        changed += 1
        print("  card updated:", img)
    if changed:
        wr(p, s)
    print("cards changed:", changed)

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
