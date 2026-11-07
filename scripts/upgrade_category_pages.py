# -*- coding: utf-8 -*-
"""
Bring the four category pages up to the level of the best local competitor:

 * FAQPage schema generated from the FAQ blocks that are already on the page
   (the content existed, the markup did not)
 * a "Buyer project snapshot" box at the top of each page: styles, fabric, wash,
   MOQ, price, sampling, bulk — the format an AI or a buyer can read at a glance
 * a laundry section on /capabilities/ with the two new equipment photos
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
SITE = "https://zuoyugarment.com"

SNAPSHOTS = {
    "jeans": [
        ("Styles", "Five-pocket, straight, slim, relaxed, wide-leg, mom, barrel, utility"),
        ("Fabrics", "Rigid 12-14 oz · comfort stretch 10.5-12 oz · high stretch 9-11 oz"),
        ("Wash", "Stone, enzyme, laser whiskers, ozone bleaching"),
        ("Sizes", "Men's W28-W44 · women's W24-W34 · plus-size grading on request"),
        ("MOQ", "150 pcs per style per colour"),
        ("Price", "USD 18-26 per piece FOB Shenzhen · women's listed styles from USD 13.99"),
        ("Sampling", "10-15 days · USD 100 per style, credited against the bulk invoice"),
        ("Bulk", "30-35 days after approval and deposit"),
    ],
    "denim-jackets": [
        ("Styles", "Trucker, overshirt, chore, biker, shacket, cropped"),
        ("Fabrics", "Rigid 10-14 oz · comfort stretch 9.5-12 oz · lined or unlined"),
        ("Hardware", "Custom shank buttons and rivets · tooling 15-25 days"),
        ("Sizes", "Men's S-XXL · women's XS-XL · plus-size blocks available"),
        ("MOQ", "150 pcs per style per colour (hardware tooling is separate)"),
        ("Price", "USD 16.57-18.67 per piece FOB Shenzhen"),
        ("Sampling", "10-15 days · USD 100 per style, credited against the bulk invoice"),
        ("Bulk", "30-35 days; 35-45 days when custom hardware tooling is involved"),
    ],
    "denim-shirts": [
        ("Styles", "Button-down overshirt, work shirt, pullover/smock, shirt-jacket"),
        ("Fabrics", "Shirting denim 4-8 oz · chambray 3.5-5 oz · cotton and cotton-Tencel"),
        ("Collar and cuff", "One-piece, two-piece, band and camp collar · single or double-button cuff"),
        ("Sizes", "Men's S-XXL · women's XS-XL and EU 34-46"),
        ("MOQ", "150 pcs per style per colour"),
        ("Price", "USD 17.65-23.53 per piece FOB Shenzhen"),
        ("Sampling", "10-15 days · USD 100 per style, credited against the bulk invoice"),
        ("Bulk", "30-35 days after approval and deposit"),
    ],
    "denim-dresses": [
        ("Styles", "Shirt dress, pinafore, slip-bib, tiered, column, wrap, tailored"),
        ("Fabrics", "Rigid 8-12 oz · stretch 8-11 oz · Tencel-cotton and cotton-linen blends"),
        ("Wash", "Stone, enzyme, laser whiskers, ozone bleaching"),
        ("Sizes", "EU 34-46 / US 2-16 base run · extended and plus-size grading on request"),
        ("MOQ", "150 pcs per style per colour"),
        ("Price", "USD 14-19 per piece FOB Shenzhen"),
        ("Sampling", "10-15 days · USD 100 per style, credited against the bulk invoice"),
        ("Bulk", "30-35 days after approval and deposit"),
    ],
}

CSS = """
/* --- buyer project snapshot + two-up photo grid --- */
.snapshot{border:1px solid var(--line);background:#fbfaf8;padding:1.05rem 1.15rem;margin:1.7rem 0 2.1rem}
.snapshot-title{font-size:.66rem;letter-spacing:.18em;text-transform:uppercase;color:var(--copper);margin:0 0 .55rem}
.snapshot table{width:100%;border-collapse:collapse;font-size:.85rem}
.snapshot th{text-align:left;width:30%;padding:.32rem .7rem .32rem 0;font-weight:600;color:var(--ink);vertical-align:top}
.snapshot td{padding:.32rem 0;color:var(--ink-2);vertical-align:top}
.gallery-2{grid-template-columns:repeat(2,1fr)}
@media (max-width:700px){
  .snapshot th{width:40%}
  .gallery-2{grid-template-columns:1fr}
}
"""

LAUNDRY = """  <section>
    <div class="wrap">
      <h2>Laundry on site</h2>
      <p>Stone, enzyme, laser and ozone work runs in our own laundry, a short walk from the sewing floor. That is what makes a wash trial a matter of days instead of a round trip: the person who approves your sample can stand next to the machine that runs it. It also means the sealed standard we keep for bulk is a sample we washed ourselves, not one we received from a third party.</p>
      <div class="gallery gallery-2">
        <img decoding="async" src="/assets/img/factory-wash-machines.jpg" srcset="/assets/img/factory-wash-machines-640.jpg 640w, /assets/img/factory-wash-machines.jpg 1080w" sizes="(max-width: 700px) 100vw, 50vw" alt="In-house laundry: industrial washing machines used for stone and enzyme washes" loading="lazy" width="1080" height="1350">
        <img decoding="async" src="/assets/img/factory-ozone.jpg" srcset="/assets/img/factory-ozone-640.jpg 640w, /assets/img/factory-ozone.jpg 1080w" sizes="(max-width: 700px) 100vw, 50vw" alt="Ozone washing machine used to lift shade with less water" loading="lazy" width="1080" height="1350">
      </div>
      <p class="figure-note">Our own laundry: washing machines and the ozone unit used for shade lifting</p>
    </div>
  </section>

"""


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def faq_jsonld(html):
    pairs = []
    for m in re.finditer(r"<details><summary>(.*?)</summary>(.*?)</details>", html, re.S):
        q = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        paras = re.findall(r"<p>(.*?)</p>", m.group(2), re.S)
        a = re.sub(r"<[^>]+>", " ", " ".join(paras))
        a = re.sub(r"\s+", " ", a).strip()
        if q and a:
            pairs.append((q, a))
    if not pairs:
        return None
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def snapshot_block(rows):
    body = "\n".join("            <tr><th>%s</th><td>%s</td></tr>" % (k, v) for k, v in rows)
    return """      <div class="snapshot">
        <p class="snapshot-title">Buyer project snapshot</p>
        <table>
          <tbody>
%s
          </tbody>
        </table>
      </div>

""" % body


def main():
    for slug, rows in SNAPSHOTS.items():
        p = os.path.join(ROOT, slug, "index.html")
        if not os.path.isfile(p):
            print("missing", slug)
            continue
        s = rd(p)
        original = s

        # 1. snapshot right after the short-answer box
        if "Buyer project snapshot" not in s:
            anchor = '      <h2>Specifications we run most often</h2>'
            if anchor in s:
                s = s.replace(anchor, snapshot_block(rows) + anchor, 1)
            else:
                print("  WARNING: specs heading not found on", slug)

        # 2. FAQPage schema built from the page's own FAQ blocks
        if '"@type": "FAQPage"' not in s:
            block = faq_jsonld(s)
            if block:
                s = s.replace("</head>", '<script type="application/ld+json">\n%s\n</script>\n</head>' % block, 1)
            else:
                print("  WARNING: no FAQ blocks on", slug)

        if s != original:
            wr(p, s)
            print("updated", slug)

    # 3. laundry section on capabilities
    cap = os.path.join(ROOT, "capabilities", "index.html")
    if os.path.isfile(cap):
        s = rd(cap)
        if "Laundry on site" not in s:
            anchor = '  <section class="cta-strip">'
            if anchor in s:
                s = s.replace(anchor, LAUNDRY + anchor, 1)
                wr(cap, s)
                print("capabilities: laundry section added")
            else:
                print("WARNING: cta anchor not found on capabilities")

    # 4. css
    css_path = os.path.join(ROOT, "assets", "style.css")
    css = rd(css_path)
    if "buyer project snapshot" not in css:
        wr(css_path, css + CSS)
        print("style.css: snapshot styles added")

    # validate
    bad = []
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            fp = os.path.join(dp, f)
            for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', rd(fp), re.S):
                try:
                    json.loads(block)
                except Exception as exc:                      # noqa: BLE001
                    bad.append((os.path.relpath(fp, ROOT), str(exc)[:60]))
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
