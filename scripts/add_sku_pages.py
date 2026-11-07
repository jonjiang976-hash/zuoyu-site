# -*- coding: utf-8 -*-
"""
Create six style (SKU) pages from real storefront listings.

Each page: hero photo, short answer, spec table with the real FOB band from the
listing, customisation options, three FAQs (with FAQPage schema), Product schema
with AggregateOffer, breadcrumb, and links to the category page and siblings.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
SITE = "https://zuoyugarment.com"
CHROME = os.path.join(ROOT, "jeans", "index.html")

STYLES = [
    {
        "slug": "custom-wide-leg-jeans",
        "crumb": "Wide-leg jeans",
        "h1": "Custom wide-leg jeans",
        "title": "Custom Wide-Leg Jeans Manufacturer: MOQ 150 | Zuoyu",
        "desc": "Custom wide-leg and baggy jeans from USD 13.97-19.12 FOB Shenzhen. MOQ 150 pcs per style per colour, sample in 10-15 days, wash development in-house.",
        "img": "style-wide-leg",
        "img_alt": "Custom women's wide-leg baggy denim jeans in a vintage wash",
        "lede": "Wide-leg and baggy blocks are the fastest-moving part of the women's denim market, and the silhouette lives or dies on fabric weight: a 10.5 oz denim falls close to the leg, a 13 oz denim stands away from it. We develop the block around the weight you want, then wash it. 150 pieces per style per colour, from USD 13.97-19.12 FOB Shenzhen.",
        "answer": "send a reference garment or a tech pack with the leg opening and rise you want; we confirm the fabric weight, quote in 2 working days, and cut a first sample in 10-15 days.",
        "specs": [
            ("Constructions", "Wide leg, baggy, palazzo, flare and barrel blocks. High, mid and low rise; full and cropped length."),
            ("Fabrics", "Rigid denim 10-14 oz; comfort stretch 9.5-12 oz; cotton and cotton-elastane blends. Weight is confirmed against the reference before cutting."),
            ("Wash programme", "Stone, enzyme, laser whiskers and ozone bleaching; vintage and faded effects developed in our own laundry."),
            ("Sizes", "Women's W24-W34 and EU 34-46 base run; men's W28-W44 on the same blocks. Grading to your size chart."),
            ("Price band", "USD 13.97-19.12 per piece, FOB Shenzhen, for the listed women's wide-leg styles."),
            ("Minimum order", "150 pcs per style per colour."),
            ("Sampling", "10-15 days. Sampling fee USD 100 per style, credited against the bulk invoice."),
            ("Bulk lead time", "30-35 days after sample approval and deposit."),
        ],
        "custom": "Leg opening width, rise, panel splits, patchwork, distressing placement, hardware, labels and the wash standard can all be specified.",
        "faq": [
            ("What denim weight suits a wide-leg jean?",
             "Most wide-leg briefs sit in 10.5-12.5 oz: light enough to drape close, heavy enough to hold the silhouette. A 13-14 oz rigid denim gives a stiffer, more architectural leg and needs a wear-in period."),
            ("Can you copy a baggy fit I already sell?",
             "Yes - send the garment plus your size chart. A physical sample is faster than photographs for leg opening, rise and hip placement."),
            ("Is the wash included in the price?",
             "No. The band above is the garment; wash is quoted as its own line because its cost depends on how many process steps the finish needs."),
        ],
        "related": [("/jeans/", "all jeans"), ("/custom-straight-leg-jeans/", "straight-leg jeans"),
                    ("/custom-cargo-jeans/", "cargo jeans"), ("/how-to-order/", "how ordering works")],
    },
    {
        "slug": "custom-straight-leg-jeans",
        "crumb": "Straight-leg jeans",
        "h1": "Custom straight-leg jeans with patchwork panels",
        "title": "Custom Straight-Leg Jeans with Patchwork: MOQ 150 | Zuoyu",
        "desc": "Custom straight-leg jeans with asymmetric patchwork panels, USD 13.97-19.12 FOB Shenzhen. MOQ 150 pcs per style per colour, 10-15 day samples.",
        "img": "style-straight",
        "img_alt": "Custom women's straight-leg jeans with asymmetric patchwork panels",
        "lede": "Straight-leg is the volume block, and patchwork is what makes a straight jean worth a second look. The hard part is not the pattern, it is matching the panels after wash: two fabrics that read the same in the cutting room can separate after 30 minutes in the drum. We develop the wash across the assembled garment, not on a flat swatch.",
        "answer": "send the panel layout (or the garment), the fabric for each panel and your size chart; we quote in 2 working days and build the first sample in 10-15 days with the wash already developed on the assembled jean.",
        "specs": [
            ("Constructions", "Straight, slim-straight, tube and crop; single or multi-panel patchwork, asymmetric seams, split hems."),
            ("Fabrics", "Rigid 11-14 oz; stretch 9.5-12 oz. Contrast panels can use a second weight or shade; each fabric is pre-tested for shrinkage so panels stay aligned."),
            ("Wash programme", "Stone, enzyme, laser whiskers, ozone; contrast-wash panel effects quoted per placement."),
            ("Sizes", "Women's W24-W34; men's W28-W44; EU 34-46. Grading confirmed before sampling."),
            ("Price band", "USD 13.97-19.12 per piece, FOB Shenzhen, for the listed straight-leg styles."),
            ("Minimum order", "150 pcs per style per colour. Patchwork does not change the minimum."),
            ("Sampling", "10-15 days. Sampling fee USD 100 per style, credited against the bulk invoice."),
            ("Bulk lead time", "30-35 days after sample approval and deposit."),
        ],
        "custom": "Panel layout, seam placement, contrast fabric, wash contrast, hardware and labels are all specified per style.",
        "faq": [
            ("Will patchwork panels align after washing?",
             "They will if each fabric is pre-tested for shrinkage and the wash is developed on the assembled garment. That is why we ask for the panel layout before quoting rather than after."),
            ("Can the panels be different denim weights?",
             "Yes, but expect a separate shrinkage test and a second wash trial. Mixing weights is a design decision with a cost, and we quote it as one."),
            ("What is the minimum for a patchwork style?",
             "150 pieces per style per colour, the same as any other style. The construction does not raise the minimum."),
        ],
        "related": [("/jeans/", "all jeans"), ("/custom-wide-leg-jeans/", "wide-leg jeans"),
                    ("/custom-cargo-jeans/", "cargo jeans"), ("/how-to-order/", "how ordering works")],
    },
    {
        "slug": "custom-cargo-jeans",
        "crumb": "Cargo jeans",
        "h1": "Custom cargo and utility jeans",
        "title": "Custom Cargo Jeans Manufacturer: MOQ 150 | Zuoyu",
        "desc": "Custom cargo and utility jeans with functional pockets, USD 13.97-19.12 FOB Shenzhen. MOQ 150 pcs per style per colour, in-house wash, 10-15 day samples.",
        "img": "style-cargo",
        "img_alt": "Custom women's wide-leg cargo jeans with functional pockets",
        "lede": "Cargo denim adds cost in a place buyers do not expect: pockets. Each pocket is a separate pattern piece, a separate sewing operation and a place where the wash can catch. A utility jean with four pockets is not a jean with two extra bits of fabric - it is a different labour quote.",
        "answer": "send the pocket layout and the hardware you want; we quote the pocket work separately from the base jean so you can see what the utility detail costs.",
        "specs": [
            ("Constructions", "Cargo, utility, parachute and multi-pocket blocks; wide or straight leg; high or mid rise."),
            ("Fabrics", "Rigid 11-14 oz, cotton twill and cotton-nylon blends; heavier weights hold pocket structure better."),
            ("Pockets and trims", "Bellows, flap, zip and welt pockets; webbing, buckles, D-rings and snaps quoted per placement."),
            ("Wash programme", "Stone, enzyme, laser, ozone; vintage and monkey-wash effects developed in-house."),
            ("Sizes", "Women's W24-W34, men's W28-W44; EU 34-46."),
            ("Price band", "USD 13.97-19.12 per piece, FOB Shenzhen, for the listed women's cargo styles."),
            ("Minimum order", "150 pcs per style per colour."),
            ("Sampling", "10-15 days. Sampling fee USD 100 per style, credited against the bulk invoice."),
            ("Bulk lead time", "30-35 days after approval and deposit."),
        ],
        "custom": "Pocket count and layout, webbing colour, hardware finish, leg volume, waist rise and the wash standard.",
        "faq": [
            ("Do cargo pockets raise the minimum order?",
             "No. The minimum stays at 150 pieces per style per colour; the pocket work changes the unit price, not the minimum."),
            ("Can you match a utility fabric that is not denim?",
             "Yes - cotton twill and cotton-nylon blends are common on cargo styles. Send the swatch and we confirm the mill before quoting."),
            ("Which wash works best on cargo denim?",
             "A vintage or monkey wash on 12-14 oz rigid denim holds structure and makes the pocket shading read. Very light washes tend to flatten the utility look."),
        ],
        "related": [("/jeans/", "all jeans"), ("/custom-wide-leg-jeans/", "wide-leg jeans"),
                    ("/capabilities/", "in-house wash"), ("/how-to-order/", "how ordering works")],
    },
    {
        "slug": "custom-denim-shorts",
        "crumb": "Denim shorts",
        "h1": "Custom denim shorts",
        "title": "Custom Denim Shorts Manufacturer: MOQ 150 | Zuoyu",
        "desc": "Custom denim shorts with high rise, frayed hem and vintage wash options, from USD 12.50-14.50 FOB Shenzhen. MOQ 150 pcs per style per colour.",
        "img": "style-shorts",
        "img_alt": "Custom high-rise women's denim shorts in a medium wash",
        "lede": "Shorts are the lowest-cost denim product per piece and the fastest to sell out - which makes them the right first style for a new brand. The two decisions that matter are the inseam (it moves more than buyers expect between sizes) and the hem: a clean hem and a frayed hem are different operations, not a toggle.",
        "answer": "send the reference short or a tech pack with the inseam and hem finish; we quote in 2 working days and cut a first sample in 10-15 days.",
        "specs": [
            ("Constructions", "High, mid and low rise; straight, relaxed and wide leg; 3-7 inch inseam; clean, frayed or raw hem."),
            ("Fabrics", "Rigid 10-12 oz, comfort stretch 9.5-11.5 oz; cotton and cotton-elastane blends."),
            ("Wash programme", "Light, medium and dark washes; stone, enzyme, laser whiskers, ozone; fraying by hand or laser."),
            ("Sizes", "Women's W24-W34 and EU 34-46; men's W28-W44."),
            ("Price band", "USD 12.50-14.50 per piece, FOB Shenzhen, for the listed women's shorts. The lowest band in our range."),
            ("Minimum order", "150 pcs per style per colour."),
            ("Sampling", "10-15 days. Sampling fee USD 100 per style, credited against the bulk invoice."),
            ("Bulk lead time", "30-35 days after approval and deposit."),
        ],
        "custom": "Inseam, rise, hem finish, fraying level, pocket shape, hardware and the wash standard.",
        "faq": [
            ("How much does a custom denim short cost?",
             "USD 12.50-14.50 per piece FOB Shenzhen for the listed women's styles, depending on fabric, wash and hem finish. It is the lowest price band in our range."),
            ("Can you make a frayed hem that does not keep fraying?",
             "Yes. Fraying is controlled by the cut, the wash and a lock-stitch bar; we agree the level of fray against a physical sample so bulk matches it."),
            ("What is the simplest first order?",
             "One short, one wash, 150 pieces. It is the cheapest way to test a fit and a supplier before committing a full collection."),
        ],
        "related": [("/jeans/", "all jeans"), ("/denim-jackets/", "denim jackets"),
                    ("/custom-wide-leg-jeans/", "wide-leg jeans"), ("/how-to-order/", "how ordering works")],
    },
    {
        "slug": "long-denim-coat",
        "crumb": "Long denim coat",
        "h1": "Custom long denim coat",
        "title": "Custom Long Denim Coat Manufacturer: MOQ 150 | Zuoyu",
        "desc": "Custom long denim coats and longline jackets, USD 17.65-23.53 FOB Shenzhen. MOQ 150 pcs per style per colour, in-house wash, 10-15 day samples.",
        "img": "style-long-coat",
        "img_alt": "Custom long denim coat with a loose silhouette",
        "lede": "A long coat is the most fabric-hungry denim item we make: length adds weight, and weight changes how a wash behaves down the body. The two things to settle before sampling are the lining (or the absence of it) and where the wash gradient sits, because both are visible from across a room.",
        "answer": "send the length and silhouette you want plus a reference for the wash; we confirm fabric weight and lining, quote in 2 working days, and sample in 10-15 days.",
        "specs": [
            ("Constructions", "Longline coat, duster, trench-inspired and oversized shirt-coat blocks; lined or unlined."),
            ("Fabrics", "Rigid denim 11-14 oz; cotton-twill and cotton-linen blends for a softer drape; lining options quoted separately."),
            ("Wash programme", "Stone, enzyme, laser, ozone; gradient and vintage effects developed on the assembled coat."),
            ("Sizes", "Women's XS-XL and EU 34-46; men's S-XXL; grading to your size chart."),
            ("Price band", "USD 17.65-23.53 per piece, FOB Shenzhen, for the listed women's coat and long-jacket styles."),
            ("Minimum order", "150 pcs per style per colour."),
            ("Sampling", "10-15 days. Sampling fee USD 100 per style, credited against the bulk invoice."),
            ("Bulk lead time", "30-35 days after approval and deposit; longer when a lining is added."),
        ],
        "custom": "Length, shoulder drop, lining, pocket style, belt, hardware and the wash gradient.",
        "faq": [
            ("Why does a long coat cost more than a jacket?",
             "Fabric consumption. A long coat uses roughly twice the metreage of a cropped jacket, and the wash cycle handles more weight per piece. The price band above reflects that."),
            ("Can the coat be lined?",
             "Yes - cotton, viscose or a lightweight thermal lining. Lining is quoted as a separate line and adds bulk lead time."),
            ("Can you keep the wash even over a long panel?",
             "That is the main technical risk on a coat. We develop the wash on the assembled garment and keep a sealed standard, so bulk is checked against the whole coat, not a swatch."),
        ],
        "related": [("/denim-jackets/", "denim jackets"), ("/jeans/", "all jeans"),
                    ("/capabilities/", "in-house wash"), ("/how-to-order/", "how ordering works")],
    },
    {
        "slug": "maxi-denim-skirt",
        "crumb": "Maxi denim skirt",
        "h1": "Custom maxi and long denim skirt",
        "title": "Custom Maxi Denim Skirt Manufacturer: MOQ 150 | Zuoyu",
        "desc": "Custom maxi and long denim skirts with belt and slit options, USD 13.97-19.12 FOB Shenzhen. MOQ 150 pcs per style per colour, 10-15 day samples.",
        "img": "style-maxiskirt",
        "img_alt": "Custom maxi-length denim skirt with belt and vintage wash",
        "lede": "A maxi skirt is a denim dress problem in a skirt shape: long panels, a heavy hem and a wash that has to stay even from waist to floor. It is also one of the few denim categories where a single style can carry a whole summer range, so the first sample matters more than the price.",
        "answer": "send the length, slit position and belt detail you want; we confirm the fabric weight and lining, quote in 2 working days, and sample in 10-15 days.",
        "specs": [
            ("Constructions", "A-line, straight, tiered, wrap and asymmetric blocks; front or side slit; belt or self-tie."),
            ("Fabrics", "Rigid denim 8-12 oz; comfort and high-stretch 8-11 oz; cotton-Tencel and cotton-linen blends for drape."),
            ("Wash programme", "Stone, enzyme, laser, ozone; faded and vintage effects developed in-house."),
            ("Sizes", "Women's XS-XL and EU 34-46; extended and plus-size grading on request."),
            ("Price band", "USD 13.97-19.12 per piece, FOB Shenzhen, for the listed women's skirt styles."),
            ("Minimum order", "150 pcs per style per colour."),
            ("Sampling", "10-15 days. Sampling fee USD 100 per style, credited against the bulk invoice."),
            ("Bulk lead time", "30-35 days after approval and deposit."),
        ],
        "custom": "Length, slit, belt, waistband height, lining, hardware and the wash standard.",
        "faq": [
            ("How much does a custom maxi denim skirt cost?",
             "USD 13.97-19.12 per piece FOB Shenzhen for the listed styles, depending on fabric weight, lining and wash. MOQ is 150 pieces per style per colour."),
            ("Can a maxi skirt share a wash with my jeans?",
             "Yes - if both are cut from the same fabric lot and washed together. That is how a coordinated set stays matched instead of being matched after the fact."),
            ("Does a long skirt need a lining?",
             "For summer weights, usually not; for heavier 10-12 oz denim, a half-lining makes it wearable. We quote both so the choice is visible."),
        ],
        "related": [("/denim-jackets-and-skirts/", "jackets and skirts"), ("/denim-dresses/", "denim dresses"),
                    ("/jeans/", "all jeans"), ("/how-to-order/", "how ordering works")],
    },
]


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(s)


def chrome():
    src = rd(CHROME)
    header = re.search(r'<header class="site-head">.*?</header>', src, re.S).group(0)
    footer = re.search(r'<footer class="site-foot">.*?</footer>', src, re.S).group(0)
    return header, footer


def page(cfg, header, footer, canonical):
    low, high = re.search(r"USD ([\d.]+)-([\d.]+)", cfg["desc"]).groups()
    specs = "\n".join("          <tr><th>%s</th><td>%s</td></tr>" % (k, v) for k, v in cfg["specs"])
    faqs = "\n".join("        <details><summary>%s</summary>\n          <p>%s</p></details>" % (q, a)
                     for q, a in cfg["faq"])
    related = " · ".join('<a href="%s">%s</a>' % (u, t) for u, t in cfg["related"])
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Product", "name": cfg["title"].split(":")[0],
             "description": cfg["desc"], "image": SITE + "/assets/img/%s.jpg" % cfg["img"],
             "brand": {"@type": "Brand", "name": "Zuoyu Garment"},
             "manufacturer": {"@id": SITE + "/#organization"},
             "material": "Cotton denim",
             "offers": {"@type": "AggregateOffer", "priceCurrency": "USD",
                        "lowPrice": low, "highPrice": high,
                        "availability": "https://schema.org/InStock", "url": canonical,
                        "seller": {"@id": SITE + "/#organization"}}},
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
<meta property="og:image" content="%(site)s/assets/img/%(img)s.jpg">
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
    <div class="gallery gallery-2">
      <img decoding="async" src="/assets/img/%(img)s.jpg" srcset="/assets/img/%(img)s-760.jpg 760w, /assets/img/%(img)s.jpg 1200w" sizes="(max-width: 700px) 100vw, 50vw" alt="%(imgalt)s" loading="lazy" width="1200" height="1200">
      <img decoding="async" src="/assets/img/factory-sewing-1.jpg?v=3" srcset="/assets/img/factory-sewing-1-760.jpg?v=3 760w, /assets/img/factory-sewing-1.jpg?v=3 1500w" sizes="(max-width: 700px) 100vw, 50vw" alt="Sewing line producing denim at the Zuoyu Garment factory" loading="lazy" width="1500" height="843">
    </div>
    <p class="figure-note">The style we produce, and the sewing floor it comes from</p>
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
       "h1": cfg["h1"], "lede": cfg["lede"], "img": cfg["img"], "imgalt": cfg["img_alt"],
       "answer": cfg["answer"], "specs": specs, "custom": cfg["custom"],
       "faqs": faqs, "related": related}


def main():
    header, footer = chrome()
    for cfg in STYLES:
        canonical = "%s/%s/" % (SITE, cfg["slug"])
        wr(os.path.join(ROOT, cfg["slug"], "index.html"), page(cfg, header, footer, canonical))
        print("wrote", cfg["slug"])

    # sitemap
    sm_path = os.path.join(ROOT, "sitemap.xml")
    sm = rd(sm_path)
    for cfg in STYLES:
        loc = "%s/%s/" % (SITE, cfg["slug"])
        if loc not in sm:
            entry = ('  <url><loc>%s</loc><lastmod>2026-11-07</lastmod>'
                     '<changefreq>monthly</changefreq><priority>0.9</priority></url>\n' % loc)
            sm = sm.replace("</urlset>", entry + "</urlset>")
    wr(sm_path, sm)
    print("sitemap URLs:", sm.count("<loc>"))

    # link from the category pages
    LINK_BLOCKS = {
        "jeans/index.html": [("custom-wide-leg-jeans", "wide-leg jeans"),
                             ("custom-straight-leg-jeans", "straight-leg jeans with patchwork"),
                             ("custom-cargo-jeans", "cargo and utility jeans"),
                             ("custom-denim-shorts", "denim shorts")],
        "denim-jackets/index.html": [("long-denim-coat", "long denim coat")],
        "denim-jackets-and-skirts/index.html": [("maxi-denim-skirt", "maxi denim skirt"),
                                                ("long-denim-coat", "long denim coat")],
        "denim-dresses/index.html": [("maxi-denim-skirt", "maxi denim skirt")],
    }
    for rel, links in LINK_BLOCKS.items():
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            continue
        s = rd(p)
        if "Styles we produce for this category" in s:
            continue
        items = " · ".join('<a href="/%s/">%s</a>' % (slug, label) for slug, label in links)
        block = ('      <h2>Styles we produce for this category</h2>\n'
                 '      <p>%s</p>\n\n' % items)
        anchor = "      <div class=\"divider-label\">"
        if anchor in s:
            s = s.replace(anchor, block + anchor, 1)
            wr(p, s)
            print("linked from", rel)

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
                except Exception as exc:                       # noqa: BLE001
                    bad.append((os.path.relpath(fp, ROOT), str(exc)[:60]))
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
