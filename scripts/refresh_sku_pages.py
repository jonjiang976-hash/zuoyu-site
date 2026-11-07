# -*- coding: utf-8 -*-
"""
Swap in the six exact product photos and re-theme the two pages whose real
product differs from the placeholder style:

  long-denim-coat  -> custom-eyelet-denim-jacket   (eyelet + lace-up + raw hem)
  maxi-denim-skirt -> custom-long-denim-skirt      (dark wash, front slit)

Each SKU page gets two product angles plus a factory photo.
"""
import io
import json
import os
import re
import shutil
import sys

ROOT = os.getcwd()
SITE = "https://zuoyugarment.com"
CHROME = os.path.join(ROOT, "jeans", "index.html")

EXISTING = ["custom-wide-leg-jeans", "custom-straight-leg-jeans",
            "custom-cargo-jeans", "custom-denim-shorts"]

IMG = {
    "custom-wide-leg-jeans": ("style-wide-leg", 662, 662, "style-wide-leg", 662, 1000),
    "custom-straight-leg-jeans": ("style-straight", 1100, 1100, "style-straight", 1100, 1100),
    "custom-cargo-jeans": ("style-cargo", 750, 750, "style-cargo", 616, 822),
    "custom-denim-shorts": ("style-shorts", 1069, 1100, "style-shorts", 1100, 790),
}

ALTS = {
    "custom-wide-leg-jeans": ("Custom light-wash wide-leg jeans with a clean hem",
                              "Side view of the same wide-leg jeans"),
    "custom-straight-leg-jeans": ("Custom straight-leg jeans with a patchwork panel across the leg",
                                  "Side view of the patchwork straight-leg jeans"),
    "custom-cargo-jeans": ("Custom cargo jeans with side utility pockets",
                           "Side view of the cargo jeans"),
    "custom-denim-shorts": ("Custom dark-wash denim shorts with a frayed hem",
                            "Close-up of the frayed hem and front pocket"),
}

NEW = [
    {
        "slug": "custom-eyelet-denim-jacket",
        "crumb": "Eyelet jacket",
        "h1": "Custom eyelet lace-up denim jacket",
        "title": "Custom Eyelet Lace-Up Denim Jacket: MOQ 150 | Zuoyu",
        "desc": "Custom eyelet and lace-up denim jackets with bow ties and raw hem, USD 17.65-23.53 FOB Shenzhen. MOQ 150 pcs per style per colour, 10-15 day samples.",
        "imgs": [("style-eyelet-jacket-1.jpg", 450, 450,
                  "Custom denim jacket with eyelet lace-up back detail and bow ties"),
                 ("style-eyelet-jacket-2.jpg", 450, 450,
                  "Front view of the eyelet lace-up denim jacket")],
        "lede": "Eyelet and lace-up detail is hand work, not a print: every eyelet is punched and set, every tie is cut and finished, and the wash has to run without tearing a single one. That is why this style is quoted from the detailed spec rather than from the basic jacket band alone.",
        "answer": "send the placement map for the eyelets (or the garment) and the lace colour you want; we quote the hand work as its own line, then sample in 10-15 days.",
        "specs": [
            ("Constructions", "Cropped, regular and oversized jacket blocks; eyelet panels at the back, sleeves or front; raw or clean hem."),
            ("Eyelet and lace", "Brass or painted eyelets, 6-12 mm; cotton or satin lace in a matched or contrast colour. Placement is confirmed on a paper mock before punching."),
            ("Fabrics", "Rigid denim 10-14 oz; comfort stretch 9.5-12 oz. Softer weights take eyelets more cleanly."),
            ("Wash programme", "Stone, enzyme, laser, ozone; vintage and faded effects developed in our own laundry and checked around every eyelet."),
            ("Sizes", "Women's XS-XL and EU 34-46; men's S-XXL; grading to your size chart."),
            ("Price band", "USD 17.65-23.53 per piece, FOB Shenzhen, for jacket constructions at this level of hand work."),
            ("Minimum order", "150 pcs per style per colour."),
            ("Sampling", "10-15 days. Sampling fee USD 100 per style, credited against the bulk invoice."),
            ("Bulk lead time", "30-35 days after approval and deposit; longer when the eyelet count is high."),
        ],
        "custom": "Eyelet count, size and finish, lace material and colour, placement, hem finish, hardware and the wash standard.",
        "faq": [
            ("Does eyelet work add to the unit price?",
             "Yes. Every eyelet is a punched hole, a set fitting and a hand-checked edge, so the hand work is quoted separately from the base jacket. The band above is the jacket including a typical eyelet programme."),
            ("Can the eyelets rust after washing?",
             "Brass or properly plated eyelets do not, but the finish matters. We specify the eyelet material per order and wash-test the assembled garment before bulk."),
            ("Can the laces be a different colour?",
             "Yes - matched or contrast, in cotton or satin. Send the reference; the lace is a separate line in the quotation."),
        ],
        "related": [("/denim-jackets/", "denim jackets"), ("/custom-denim-shorts/", "denim shorts"),
                    ("/capabilities/", "in-house wash"), ("/how-to-order/", "how ordering works")],
    },
    {
        "slug": "custom-long-denim-skirt",
        "crumb": "Long denim skirt",
        "h1": "Custom long straight denim skirt",
        "title": "Custom Long Denim Skirt Manufacturer: MOQ 150 | Zuoyu",
        "desc": "Custom long straight denim skirts with a front slit, dark and black washes, USD 13.97-19.12 FOB Shenzhen. MOQ 150 pcs per style per colour.",
        "imgs": [("style-long-skirt-1.jpg", 768, 768,
                  "Custom long straight denim skirt in a dark wash"),
                 ("style-long-skirt-2.jpg", 768, 1024,
                  "Front slit detail of the long denim skirt")],
        "lede": "A long straight skirt is a pattern and wash problem more than a sewing problem: the slit has to sit where the leg moves, and a dark wash has to stay even from waistband to hem. Get those two right and the style sells for several seasons without a change.",
        "answer": "send the slit position and length you want plus a wash reference; we confirm fabric weight and lining, quote in 2 working days, and sample in 10-15 days.",
        "specs": [
            ("Constructions", "Long straight, A-line and column blocks; front, side or back slit; high or mid rise; zip or button fly."),
            ("Fabrics", "Rigid denim 10-12 oz; comfort stretch 9-11 oz; dark indigo, black and over-dyed shades."),
            ("Wash programme", "Dark and black washes, stone and enzyme softening, ozone shade control; colour consistency checked between panels."),
            ("Sizes", "Women's XS-XL and EU 34-46; extended grading on request."),
            ("Price band", "USD 13.97-19.12 per piece, FOB Shenzhen, for long skirt constructions."),
            ("Minimum order", "150 pcs per style per colour."),
            ("Sampling", "10-15 days. Sampling fee USD 100 per style, credited against the bulk invoice."),
            ("Bulk lead time", "30-35 days after approval and deposit."),
        ],
        "custom": "Length, slit position and height, rise, waistband, lining, hardware and the wash standard.",
        "faq": [
            ("Where should the slit sit on a long denim skirt?",
             "Where the leg actually moves: front-centre for walking, side for a straighter line. We agree the slit height against a physical sample because two centimetres changes how the skirt walks."),
            ("Can the skirt be unlined?",
             "For 9-10 oz denim, usually yes. For heavier 11-12 oz, a half-lining makes it wearable in summer. Both are quoted so the choice is visible."),
            ("Can a long skirt share a wash with my jeans?",
             "Yes, if both are cut from the same fabric lot and washed together - that is how a matched set stays matched."),
        ],
        "related": [("/denim-jackets-and-skirts/", "jackets and skirts"), ("/denim-dresses/", "denim dresses"),
                    ("/custom-denim-shorts/", "denim shorts"), ("/how-to-order/", "how ordering works")],
    },
]


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(s)


def chrome():
    src = rd(CHROME)
    return (re.search(r'<header class="site-head">.*?</header>', src, re.S).group(0),
            re.search(r'<footer class="site-foot">.*?</footer>', src, re.S).group(0))


GALLERY = """<div class="gallery">
      <img decoding="async" src="/assets/img/%s" alt="%s" loading="lazy" width="%d" height="%d" style="width:100%%;aspect-ratio:1/1;object-fit:cover">
      <img decoding="async" src="/assets/img/%s" alt="%s" loading="lazy" width="%d" height="%d" style="width:100%%;aspect-ratio:1/1;object-fit:cover">
      <img decoding="async" src="/assets/img/factory-sewing-1.jpg?v=3" alt="Sewing line producing denim at the Zuoyu Garment factory" loading="lazy" width="1500" height="843" style="width:100%%;aspect-ratio:1/1;object-fit:cover">
    </div>"""


def build_new(cfg, header, footer):
    canonical = "%s/%s/" % (SITE, cfg["slug"])
    low, high = re.search(r"USD ([\d.]+)-([\d.]+)", cfg["desc"]).groups()
    gallery = GALLERY % (cfg["imgs"][0][0], cfg["imgs"][0][3], cfg["imgs"][0][1], cfg["imgs"][0][2],
                         cfg["imgs"][1][0], cfg["imgs"][1][3], cfg["imgs"][1][1], cfg["imgs"][1][2])
    specs = "\n".join("          <tr><th>%s</th><td>%s</td></tr>" % (k, v) for k, v in cfg["specs"])
    faqs = "\n".join("        <details><summary>%s</summary>\n          <p>%s</p></details>" % (q, a)
                     for q, a in cfg["faq"])
    related = " · ".join('<a href="%s">%s</a>' % (u, t) for u, t in cfg["related"])
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Product", "name": cfg["h1"], "description": cfg["desc"],
             "image": SITE + "/assets/img/" + cfg["imgs"][0][0],
             "brand": {"@type": "Brand", "name": "Zuoyu Garment"},
             "manufacturer": {"@id": SITE + "/#organization"}, "material": "Cotton denim",
             "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": low,
                        "highPrice": high, "availability": "https://schema.org/InStock",
                        "url": canonical, "seller": {"@id": SITE + "/#organization"}}},
            {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in cfg["faq"]]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Products", "item": SITE + "/#products"},
                {"@type": "ListItem", "position": 3, "name": cfg["crumb"], "item": canonical}]},
        ]}, ensure_ascii=False, indent=2)
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="theme-color" content="#12283f">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<meta property="og:type" content="product">
<meta property="og:site_name" content="Zuoyu Garment">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(canonical)s">
<meta property="og:image" content="%(site)s/assets/img/%(img)s">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="%(canonical)s">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">
%(jsonld)s
</script>
</head>
<body>
%(header)s

<main>
  <div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span>Products<span>/</span>%(crumb)s</nav></div>

  <div class="page-head"><div class="wrap">
    <p class="eyebrow">Style</p>
    <h1>%(h1)s</h1>
    <p class="lede" style="max-width:70ch">%(lede)s</p>
  </div></div>

  <section class="tight"><div class="wrap">
    %(gallery)s
    <p class="figure-note">Both angles of the style we produce, and the sewing floor it comes from</p>
  </div></section>

  <section><div class="wrap">
      <div class="answer">
        <p><strong>Short answer for buyers:</strong> %(answer)s</p>
      </div>
      <h2>Specification and price</h2>
      <table class="fact-table">
        <caption>%(h1)s — production specification</caption>
        <tbody>
%(specs)s
        </tbody>
      </table>
      <p class="note"><strong>What can be changed:</strong> %(custom)s</p>
      <div class="divider-label">Buyer questions</div>
      <div class="faq">
%(faqs)s
      </div>
      <p style="margin-top:2rem">Related: %(related)s</p>
  </div></section>

  <section class="cta-strip"><div class="wrap">
    <div><h2>Send a reference for this style</h2><p>A garment or a tech pack with the silhouette and wash you want is enough for a first quotation.</p></div>
    <a class="btn btn-ghost" href="/contact/">Start a brief</a>
  </div></section>
</main>

%(footer)s
</body>
</html>
""" % {"site": SITE, "title": cfg["title"], "desc": cfg["desc"], "canonical": canonical,
       "jsonld": jsonld, "header": header, "footer": footer, "crumb": cfg["crumb"],
       "h1": cfg["h1"], "lede": cfg["lede"], "img": cfg["imgs"][0][0], "gallery": gallery,
       "answer": cfg["answer"], "specs": specs, "custom": cfg["custom"],
       "faqs": faqs, "related": related}


def main():
    header, footer = chrome()

    # 1. refresh the four existing SKU pages
    for slug in EXISTING:
        p = os.path.join(ROOT, slug, "index.html")
        if not os.path.isfile(p):
            print("missing", slug)
            continue
        s = rd(p)
        img1, w1, h1, img2, w2, h2 = IMG[slug]
        alt1, alt2 = ALTS[slug]
        gallery = GALLERY % (img1 + "-1.jpg", alt1, w1, h1,
                             img1 + "-2.jpg", alt2, w2, h2)
        s2 = re.sub(r'<div class="gallery gallery-2">.*?</div>', gallery, s, count=1, flags=re.S)
        if s2 == s:
            print("  WARNING: gallery not replaced on", slug)
        else:
            wr(p, s2)
            print("gallery refreshed:", slug)

    # 2. new pages for the two re-themed styles
    for cfg in NEW:
        wr(os.path.join(ROOT, cfg["slug"], "index.html"), build_new(cfg, header, footer))
        print("wrote", cfg["slug"])

    # 3. remove the placeholder pages and redirect them
    for old in ["long-denim-coat", "maxi-denim-skirt"]:
        d = os.path.join(ROOT, old)
        if os.path.isdir(d):
            shutil.rmtree(d, ignore_errors=True)
            print("removed", old)

    redirects = [
        ("/long-denim-coat/", "/custom-eyelet-denim-jacket/"),
        ("/maxi-denim-skirt/", "/custom-long-denim-skirt/"),
    ]
    rp = os.path.join(ROOT, "_redirects")
    rd_txt = rd(rp) if os.path.isfile(rp) else ""
    for src, dst in redirects:
        if src not in rd_txt:
            rd_txt = rd_txt.rstrip("\n") + "\n%s %s 301\n" % (src, dst)
    wr(rp, rd_txt)
    print("redirects updated")

    # 4. sitemap
    sm_path = os.path.join(ROOT, "sitemap.xml")
    sm = rd(sm_path)
    for old_url in ["%s/long-denim-coat/" % SITE, "%s/maxi-denim-skirt/" % SITE]:
        sm = re.sub(r'\s*<url><loc>%s</loc>.*?</url>' % re.escape(old_url), "", sm, flags=re.S)
    for cfg in NEW:
        loc = "%s/%s/" % (SITE, cfg["slug"])
        if loc not in sm:
            sm = sm.replace("</urlset>",
                            '  <url><loc>%s</loc><lastmod>2026-11-07</lastmod>'
                            '<changefreq>monthly</changefreq><priority>0.9</priority></url>\n</urlset>' % loc)
    wr(sm_path, sm)
    print("sitemap URLs:", sm.count("<loc>"))

    # 5. fix internal links everywhere
    swaps = [("/long-denim-coat/", "/custom-eyelet-denim-jacket/"),
             ("/maxi-denim-skirt/", "/custom-long-denim-skirt/"),
             (">Long denim coat<", ">Eyelet lace-up denim jacket<"),
             ("Duster and trench blocks · lined or unlined", "Eyelet and lace-up detail · raw hem"),
             (">Maxi denim skirt<", ">Long denim skirt<"),
             ("Belt, slit and tiered blocks · 8–12 oz", "Front slit · dark and black washes"),
             ("long denim coat</a>", "eyelet lace-up denim jacket</a>"),
             ("maxi denim skirt</a>", "long denim skirt</a>"),
             ("style-long-coat-760.jpg", "style-eyelet-jacket-1.jpg"),
             ("style-long-coat.jpg", "style-eyelet-jacket-1.jpg"),
             ("style-maxiskirt-760.jpg", "style-long-skirt-1.jpg"),
             ("style-maxiskirt.jpg", "style-long-skirt-1.jpg"),
             ('alt="Long denim coat"', 'alt="Eyelet lace-up denim jacket"'),
             ('alt="Maxi denim skirt"', 'alt="Long denim skirt"')]
    touched = 0
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            fp = os.path.join(dp, f)
            s = rd(fp)
            o = s
            for a, b in swaps:
                s = s.replace(a, b)
            if s != o:
                wr(fp, s)
                touched += 1
    print("pages with link updates:", touched)

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
