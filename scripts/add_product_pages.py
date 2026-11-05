# -*- coding: utf-8 -*-
"""
Add two product pages that match the three categories buyers actually ask about:
  /denim-jackets/   — jackets deserve their own page instead of sharing one
  /denim-shirts/    — shirts had no page at all

Also wires them in: sitemap, home product card, footer product lists, cross links.
Runs from the repo root (the publish workflow calls it for a "[Patch]" issue).
"""
import io
import os
import re
import sys

ROOT = os.getcwd()
CHROME = os.path.join(ROOT, "jeans", "index.html")


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    os.makedirs(os.path.dirname(p) or ROOT, exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(s)


def chrome():
    src = rd(CHROME)
    header = re.search(r'<header class="site-head">.*?</header>', src, re.S).group(0)
    footer = re.search(r'<footer class="site-foot">.*?</footer>', src, re.S).group(0)
    return header, footer


def page(cfg, header, footer):
    ld = """{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "%s",
  "description": "%s",
  "brand": { "@type": "Brand", "name": "Zuoyu Garment" },
  "manufacturer": { "@type": "Organization", "name": "Zuoyu Garment", "url": "https://zuoyugarment.com/" },
  "material": "%s",
  "category": "Apparel > Denim > %s",
  "image": "https://zuoyugarment.com/assets/img/%s",
  "additionalProperty": [
    { "@type": "PropertyValue", "name": "Minimum order quantity", "value": "150 pieces per style per colour" },
    { "@type": "PropertyValue", "name": "Price range (FOB)", "value": "%s" },
    { "@type": "PropertyValue", "name": "Sample lead time", "value": "10–15 days" },
    { "@type": "PropertyValue", "name": "Bulk lead time", "value": "30–35 days" }
  ]
}""" % (cfg["schema_name"], cfg["schema_desc"], cfg["material"], cfg["category"],
        cfg["hero_img"], cfg["price"])

    imgs = "\n".join(
        '        <img decoding="async" src="/assets/img/%s" srcset="/assets/img/%s 760w, /assets/img/%s %dw" '
        'sizes="(max-width: 700px) 100vw, 50vw" alt="%s" loading="lazy" width="%d" height="%d">'
        % (full, small, full, w, alt, w, h)
        for full, small, w, h, alt in cfg["gallery"])

    rows = "\n".join("          <tr><th>%s</th><td>%s</td></tr>" % (k, v) for k, v in cfg["specs"])
    faqs = "\n".join("        <details><summary>%s</summary>\n          <p>%s</p></details>" % (q, a)
                     for q, a in cfg["faq"])
    related = " · ".join('<a href="%s">%s</a>' % (u, t) for u, t in cfg["related"])

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta name="theme-color" content="#12283f">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Zuoyu Garment">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="https://zuoyugarment.com/%s/">
<meta property="og:image" content="https://zuoyugarment.com/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">

<link rel="canonical" href="https://zuoyugarment.com/%s/">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">
%s
</script>
</head>
<body>
%s

<main>
  <div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span>Products<span>/</span>%s</nav></div>

  <div class="page-head"><div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="lede" style="max-width:70ch">%s</p>
  </div></div>

  <section class="tight">
    <div class="wrap">
      <div class="gallery gallery-wide">
%s
      </div>
      <p class="figure-note">%s</p>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="answer">
        <p><strong>Short answer for buyers:</strong> %s</p>
      </div>

      <h2>Specifications we run most often</h2>
      <table class="fact-table">
        <caption>%s — production specification</caption>
        <tbody>
%s
        </tbody>
      </table>
      <p class="note"><strong>What we need from you to quote:</strong> flat sketches or a reference sample, a measurement sheet, fabric direction (rigid or stretch) and weight, wash reference photos, trim and label requirements, and your delivery window.</p>

      <h2>%s</h2>
      <p>%s</p>
      <p>%s</p>

      <div class="divider-label">Buyer questions on %s</div>
      <div class="faq">
%s
      </div>

      <p style="margin-top:2rem">Related: %s</p>
    </div>
  </section>

  <section class="cta-strip"><div class="wrap">
    <div><h2>%s</h2><p>%s</p></div>
    <a class="btn btn-ghost" href="/contact/">Start a brief</a>
  </div></section>
</main>

%s
</body>
</html>
""" % (cfg["title"], cfg["desc"], cfg["title"], cfg["desc"], cfg["slug"], cfg["slug"], ld,
       header, cfg["crumb"], cfg["eyebrow"], cfg["h1"], cfg["lede"], imgs, cfg["figure_note"],
       cfg["answer"], cfg["h1"].replace(" manufacturing", ""), rows,
       cfg["section_title"], cfg["section_p1"], cfg["section_p2"],
       cfg["faq_label"], faqs, related, cfg["cta_h"], cfg["cta_p"], footer)


JACKETS = {
    "slug": "denim-jackets",
    "crumb": "Denim jackets",
    "eyebrow": "Category 02",
    "title": "Custom Denim Jacket Manufacturer, OEM &amp; ODM | Zuoyu Garment, Zhongshan",
    "desc": "Custom denim jackets: trucker, overshirt, chore and biker blocks. MOQ 150 pcs per style per colour, from USD 16.50–23.50 FOB Shenzhen, samples 10–15 days.",
    "schema_name": "Custom denim jackets — OEM/ODM manufacturing",
    "schema_desc": "Trucker, overshirt, chore and biker denim jackets produced to order in 10-14 oz rigid and stretch denim.",
    "material": "Cotton denim 10-14 oz, cotton-elastane stretch denim",
    "category": "Jackets",
    "price": "USD 16.50–23.50 per piece",
    "hero_img": "product-jacket-1.jpg",
    "h1": "Custom denim jacket manufacturing",
    "lede": "Trucker, overshirt, chore and biker blocks. Jackets are the category where hardware and panel matching decide whether a style sells, so the first sample carries the detail work: yoke shape, chest pocket placement, button tooling and the wash across the shoulder seam. 150 pieces per style per colour, from USD 16.50–23.50 per piece FOB Shenzhen, samples in 10–15 days.",
    "gallery": [
        ("product-jacket-1.jpg", "product-jacket-1-760.jpg", 1280, 1280,
         "Custom black denim work jacket produced by Zuoyu Garment"),
        ("factory-cutting.jpg", "factory-cutting-760.jpg", 800, 450,
         "Cutting room where jacket panels are cut"),
        ("factory-fabric.jpg", "factory-fabric-760.jpg", 1500, 843,
         "Fabric store where denim rolls are checked before cutting"),
    ],
    "figure_note": "A jacket from our own production, the cutting room where its panels are cut, and the fabric store where rolls are checked first",
    "answer": "send a reference jacket or a tech pack; we quote in 2 working days with hardware and wash priced as separate lines, then cut a first sample in 10–15 days against your size chart.",
    "specs": [
        ("Constructions", "Trucker, overshirt, chore, biker, shacket and cropped blocks. Unisex, men's and women's fits; lined or unlined."),
        ("Fabrics", "Rigid denim 10–14 oz, comfort stretch 9.5–12 oz. Cotton, cotton-elastane (98/2, 92/8) and cotton-polyester blends; Tencel and viscose blends on request."),
        ("Wash programme", "stone wash, enzyme wash, laser whiskers and ozone bleaching. Contrast panels and 3D effects quoted per placement."),
        ("Hardware", "Shank buttons, snap buttons, rivets, zips and labels matched to your reference. Custom-branded hardware is tooled to order; tooling lead time runs 15–25 days and is quoted separately."),
        ("Sizes", "Men's S–XXL and women's XS–XL as standard; graded to your size chart, plus-size blocks available."),
        ("Minimum order", "150 pcs per style per colour. Hardware tooling does not count toward the garment minimum."),
        ("Price band", "USD 16.50–23.50 per piece FOB Shenzhen, depending on fabric weight, lining and wash."),
        ("Sampling", "10–15 days. Sampling fee USD 100 per style, credited against the bulk invoice."),
        ("Bulk lead time", "30–35 days after sample approval and deposit; 35–45 days when custom hardware tooling is involved."),
        ("Inspection", "Final AQL inspection with a written report, plus a hardware pull test on buttons and rivets."),
    ],
    "section_title": "Why jackets cost more than their fabric",
    "section_p1": "A jacket has more pattern pieces than a pair of jeans, and the two front panels have to read as one garment after washing. The wash pulls the fabric differently across a shoulder seam than across a leg seam, so the sealed standard is checked at the yoke and the pocket flap, not only on a flat swatch.",
    "section_p2": "Hardware is the second cost driver. If you want a branded shank button, that is a tooling order before it is a garment order; if the design can use a stock button with a custom logo plate, the tooling cost drops and the lead time shortens. We quote both routes so the difference is visible before you commit.",
    "faq_label": "jackets",
    "faq": [
        ("Can you copy a jacket I already sell?",
         "Yes, usually — send the jacket plus your size chart. A physical sample is faster and more accurate than photographs, especially for the yoke shape and the chest pocket placement."),
        ("Do you make custom-branded buttons and rivets?",
         "Yes. Branded shank buttons, snap buttons and rivets are tooled to order: expect 15–25 days of tooling lead time and a separate tooling cost, quoted before sampling. Stock hardware with a custom logo plate is the faster route."),
        ("Can you produce a jacket and skirt set in the same wash?",
         "Yes. Sets are cut and washed as a pair so the two pieces match; see the <a href=\"/denim-jackets-and-skirts/\">jacket and skirt sets page</a> for how the approval works."),
    ],
    "related": [
        ("/jeans/", "denim jeans"),
        ("/denim-shirts/", "denim shirts &amp; overshirts"),
        ("/denim-jackets-and-skirts/", "jacket and skirt sets"),
        ("/capabilities/", "full capabilities"),
        ("/blog/denim-finishing-guide/", "how to choose a wash"),
        ("/faq/", "all buyer FAQ"),
    ],
    "cta_h": "Send a jacket tech pack",
    "cta_p": "Photos of the yoke, the chest pocket and the button profile are enough for a first quotation.",
}

SHIRTS = {
    "slug": "denim-shirts",
    "crumb": "Denim shirts",
    "eyebrow": "Category 04",
    "title": "Custom Denim Shirt Manufacturer, OEM &amp; ODM | Zuoyu Garment, Zhongshan",
    "desc": "Custom denim shirts and overshirts to your spec: button-down, pullover, shirt-jacket and denim tops. MOQ 150 pcs per style per colour, from USD 17.65–23.53 FOB Shenzhen.",
    "schema_name": "Custom denim shirts — OEM/ODM manufacturing",
    "schema_desc": "Button-down overshirts, work shirts, pullover tops and shirt-jackets produced to order in 4-8 oz shirting denim.",
    "material": "Shirting denim 4-8 oz, cotton and cotton-Tencel blends",
    "category": "Shirts",
    "price": "USD 17.65–23.53 per piece",
    "hero_img": "product-shirt-1.jpg",
    "h1": "Custom denim shirt manufacturing",
    "lede": "Overshirts, work shirts, pullover tops and shirt-jackets. Shirting denim is a different discipline from jeans: lighter weight, more drape, and a collar and cuff that either sit cleanly or do not. 150 pieces per style per colour, from USD 17.65–23.53 per piece FOB Shenzhen, samples in 10–15 days.",
    "gallery": [
        ("product-shirt-1.jpg", "product-shirt-1-760.jpg", 1280, 1280,
         "Custom denim overshirt produced by Zuoyu Garment"),
        ("product-shirt-2.jpg", "product-shirt-2-760.jpg", 1280, 1280,
         "Women's denim shirt with custom wash and buttons"),
        ("product-shirt-3.jpg", "product-shirt-3-760.jpg", 1024, 1024,
         "Denim top with contrast stitching and chest pockets"),
    ],
    "figure_note": "Shirts and overshirts from our own production, photographed in the same light as the rest of the range",
    "answer": "send a reference shirt or a tech pack with the collar and cuff called out; we quote in 2 working days with the wash as a separate line, then cut a first sample in 10–15 days against your size chart.",
    "specs": [
        ("Constructions", "Button-down overshirt, work shirt, pullover/smock top, shirt-jacket, short-sleeve and sleeveless tops. Unisex, men's and women's blocks."),
        ("Fabrics", "Shirting denim 4–8 oz, cotton and cotton-Tencel blends, plus lighter 3.5–5 oz chambray on request. Rigid and low-stretch options."),
        ("Collar and cuff", "One-piece, two-piece, band and camp collar; single or double-button cuff. Collar interlining is specified per order because it decides whether the collar stands or rolls."),
        ("Wash programme", "stone wash, enzyme wash, laser whiskers and ozone bleaching, matched to your reference. Garment-dye and over-dye available on request."),
        ("Sizes", "Men's S–XXL, women's XS–XL and EU 34–46; graded to your size chart."),
        ("Trims", "Buttons, snaps, labels and embroidery matched to your tech pack. Custom buttons quoted as a separate tooling line."),
        ("Minimum order", "150 pcs per style per colour."),
        ("Price band", "USD 17.65–23.53 per piece FOB Shenzhen, depending on fabric weight, wash and trims."),
        ("Sampling", "10–15 days. Sampling fee USD 100 per style, credited against the bulk invoice."),
        ("Bulk lead time", "30–35 days after sample approval and deposit."),
        ("Inspection", "Final AQL inspection with a written report; collar symmetry and button alignment are checked on every carton sample."),
    ],
    "section_title": "Shirting denim is a different discipline",
    "section_p1": "A 5 oz shirting denim does not behave like a 13 oz jean. It shrinks differently through the wash, the collar needs an interlining chosen for the drape you want, and a sleeve that is 1 cm off is visible on a shirt in a way it is not on a jacket. That is why we try the shirt on a body form before it reaches your buyers.",
    "section_p2": "The second difference is colour consistency. On a shirt, the collar, cuffs and front placket sit next to each other, so a wash that is uneven across panels is immediately obvious. We develop the wash on the whole garment rather than on a flat swatch, then keep the sealed sample as the reference for bulk.",
    "faq_label": "shirts",
    "faq": [
        ("Can an overshirt be made heavy enough to wear as a jacket?",
         "Yes. Overshirts are usually 6–8 oz with a boxier block and larger buttons; a shirt-jacket moves to 8–10 oz with a lining option. Tell us which of the two you mean, because the block and the wash programme differ."),
        ("Can you match a shirt to a denim dress or skirt I already order?",
         "Yes, if the fabric is still available or you send a swatch. Matching across two garments means washing them together, so both pieces are sampled as a set and approved as a set."),
        ("Do you make women's denim tops and blouses?",
         "Yes — pullover tops, smock tops, blouse-weight shirting and cropped overshirts. Those styles are usually 3.5–6 oz and need a softer hand-feel, so the wash programme is lighter than on a work shirt."),
    ],
    "related": [
        ("/jeans/", "denim jeans"),
        ("/denim-jackets/", "denim jackets"),
        ("/denim-dresses/", "denim dresses"),
        ("/capabilities/", "full capabilities"),
        ("/blog/denim-finishing-guide/", "how to choose a wash"),
        ("/faq/", "all buyer FAQ"),
    ],
    "cta_h": "Send a shirt tech pack",
    "cta_p": "Photos of the collar, cuff and placket, plus the fabric weight you want, are enough for a first quotation.",
}


def main():
    header, footer = chrome()
    created = []
    for cfg in (JACKETS, SHIRTS):
        path = os.path.join(ROOT, cfg["slug"], "index.html")
        wr(path, page(cfg, header, footer))
        created.append(cfg["slug"])
        print("wrote %s/index.html (%d bytes)" % (cfg["slug"], os.path.getsize(path)))

    # sitemap
    sm_path = os.path.join(ROOT, "sitemap.xml")
    sm = rd(sm_path)
    for cfg in (JACKETS, SHIRTS):
        loc = "https://zuoyugarment.com/%s/" % cfg["slug"]
        if loc not in sm:
            entry = ('  <url><loc>%s</loc><lastmod>2026-11-05</lastmod>'
                     '<changefreq>monthly</changefreq><priority>0.9</priority></url>\n' % loc)
            sm = sm.replace("</urlset>", entry + "</urlset>")
            print("sitemap += %s" % cfg["slug"])
    wr(sm_path, sm)

    # footer product lists: add the two new pages where the old entries are
    changed = 0
    for dp, _, fs in os.walk(ROOT):
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            if "/.git/" in p.replace("\\", "/"):
                continue
            s = rd(p)
            original = s
            s = s.replace('<li><a href="/denim-jackets-and-skirts/">Denim jackets &amp; skirts</a></li>',
                          '<li><a href="/denim-jackets/">Denim jackets</a></li>\n    '
                          '<li><a href="/denim-jackets-and-skirts/">Jacket &amp; skirt sets</a></li>',
                          1)
            s = s.replace('<li><a href="/denim-dresses/">Denim dresses</a></li>',
                          '<li><a href="/denim-dresses/">Denim dresses</a></li>\n    '
                          '<li><a href="/denim-shirts/">Denim shirts</a></li>', 1)
            if s != original:
                wr(p, s)
                changed += 1
    print("footer product lists updated on", changed, "pages")

    # home page: point the jacket card at the new jacket page, add a shirts card
    idx = os.path.join(ROOT, "index.html")
    s = rd(idx)
    s = s.replace('<h3>Denim jackets &amp; skirts</h3>', '<h3>Denim jackets</h3>', 1)
    s = s.replace('<p class="spec">Trucker · overshirt · chore<br>Matched sets</p>',
                  '<p class="spec">Trucker · overshirt · chore<br>Matched sets on request</p>', 1)
    s = s.replace('<a href="/denim-jackets-and-skirts/">Jackets &amp; skirts</a>',
                  '<a href="/denim-jackets/">Denim jackets</a>', 1)
    if "<h3>Denim shirts</h3>" not in s:
        card = ('        <article class="card">\n'
                '          <div class="card-img"><img decoding="async" src="/assets/img/product-shirt-2.jpg" '
                'srcset="/assets/img/product-shirt-2-760.jpg 760w, /assets/img/product-shirt-2.jpg 1280w" '
                'sizes="(max-width: 700px) 100vw, 50vw" alt="Custom denim shirts and overshirts produced by '
                'Zuoyu Garment" loading="lazy" width="1280" height="1280"></div>\n'
                '          <span class="kicker">Category 04</span>\n'
                '          <h3>Denim shirts</h3>\n'
                '          <p class="spec">Overshirt · work shirt · pullover<br>S–XXL</p>\n'
                '          <p>Button-down overshirts, work shirts, pullover tops and shirt-jackets in 4–8 oz '
                'shirting denim, washed against one sealed standard.</p>\n'
                '          <p class="spec"><b>From USD 17.65–23.53 / pc</b> · MOQ 150</p>\n'
                '          <div class="card-foot"><a href="/denim-shirts/">Denim shirts</a></div>\n'
                '        </article>\n')
        anchor = ('          <div class="card-foot"><a href="/denim-dresses/">Denim dresses</a></div>\n'
                  '        </article>\n')
        if anchor in s:
            s = s.replace(anchor, anchor + card, 1)
            wr(idx, s)
            print("home page: shirts card added")
        else:
            print("WARNING: home card anchor not found")
    else:
        print("home page: shirts card already present")

    # every page gets the Guides link in the header nav and the footer list —
    # it was only ever added to index.html, so inner pages had no way in.
    nav_added = 0
    foot_added = 0
    for dp, _, fs in os.walk(ROOT):
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            if "/.git/" in p.replace("\\", "/"):
                continue
            s = rd(p)
            original = s

            m = re.search(r'(<nav class="nav"[^>]*>)(.*?)(</nav>)', s, re.S)
            if m and "/blog/" not in m.group(2):
                inner = m.group(2)
                faq = re.search(r'(\n[ \t]*)(<a href="/faq/"[^>]*>FAQ</a>)', inner)
                if faq:
                    inner = inner.replace(
                        faq.group(2),
                        faq.group(2) + faq.group(1) + '<a href="/blog/">Guides</a>', 1)
                else:
                    inner = inner.rstrip() + '\n    <a href="/blog/">Guides</a>\n  '
                s = s[:m.start(2)] + inner + s[m.end(2):]
                nav_added += 1

            if '<li><a href="/blog/">Guides</a></li>' not in s:
                before = s
                s = s.replace('<li><a href="/faq/">Buyer FAQ</a></li>',
                              '<li><a href="/faq/">Buyer FAQ</a></li>\n    '
                              '<li><a href="/blog/">Guides</a></li>', 1)
                if s != before:
                    foot_added += 1
            if s != original:
                wr(p, s)
    print("nav Guides added on", nav_added, "pages | footer Guides added on", foot_added, "pages")

    print("done:", ", ".join(created))
    return 0


if __name__ == "__main__":
    sys.exit(main())
