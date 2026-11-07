# -*- coding: utf-8 -*-
"""
Add a "Styles we produce" section to the homepage so the six SKU pages are
reachable from the front door, not only from the category pages.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()

STYLES = [
    ("custom-wide-leg-jeans", "style-wide-leg", "Wide-leg jeans",
     "10.5–13 oz rigid or stretch · baggy and palazzo blocks", "13.97–19.12"),
    ("custom-straight-leg-jeans", "style-straight", "Straight-leg jeans",
     "Asymmetric patchwork panels · panel colour matching", "13.97–19.12"),
    ("custom-cargo-jeans", "style-cargo", "Cargo & utility jeans",
     "Bellows, flap and zip pockets · webbing and hardware", "13.97–19.12"),
    ("custom-denim-shorts", "style-shorts", "Denim shorts",
     "3–7 in inseam · clean, frayed or raw hem", "12.50–14.50"),
    ("long-denim-coat", "style-long-coat", "Long denim coat",
     "Duster and trench blocks · lined or unlined", "17.65–23.53"),
    ("maxi-denim-skirt", "style-maxiskirt", "Maxi denim skirt",
     "Belt, slit and tiered blocks · 8–12 oz", "13.97–19.12"),
]

SECTION = """  <section id="styles">
    <div class="wrap">
      <div class="section-head">
        <span class="kicker">01b — Styles we produce</span>
        <h2>Six styles you can order at 150 pieces</h2>
        <p>Each of these is a real production style, not a stock photo: the price band is the FOB band we quote for that construction. Every one is 150 pieces per style per colour, sampled in 10–15 days.</p>
      </div>
      <div class="grid grid-3">
%s
      </div>
      <p class="note" style="margin-top:1.5rem">Looking for something not listed? <a href="/contact/">Send a reference</a> — custom blocks are the normal case, not the exception.</p>
    </div>
  </section>

"""

CARD = """        <article class="card">
          <a class="card-img" href="/%s/"><img decoding="async" src="/assets/img/%s.jpg" srcset="/assets/img/%s-760.jpg 760w, /assets/img/%s.jpg 1200w" sizes="(max-width: 700px) 100vw, 33vw" alt="%s" loading="lazy" width="1200" height="1200"></a>
          <span class="kicker">Style</span>
          <h3><a href="/%s/">%s</a></h3>
          <p class="spec">%s</p>
          <p class="spec"><b>From USD %s / pc</b> · MOQ 150</p>
          <div class="card-foot"><a href="/%s/">See the specification</a></div>
        </article>"""


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def main():
    idx = os.path.join(ROOT, "index.html")
    s = rd(idx)
    if 'id="styles"' in s:
        print("homepage already has the styles section")
        return 0

    cards = "\n".join(
        CARD % (slug, img, img, img, name, slug, name, spec, price, slug)
        for slug, img, name, spec, price in STYLES)
    block = SECTION % cards

    anchor = '  <section class="sand">'
    if anchor not in s:
        print("ERROR: anchor for the styles section not found")
        return 1
    s = s.replace(anchor, block + anchor, 1)
    wr(idx, s)
    print("homepage: styles section added with", len(STYLES), "cards")

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
