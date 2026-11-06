# -*- coding: utf-8 -*-
"""
Add /how-to-order/ and lead every key page's title/description with the numbers
buyers actually search for: MOQ, sample fee credited, lead times.

Runs from the repo root (publish workflow, [Patch] issue with SCRIPT: marker).
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
SITE = "https://zuoyugarment.com"
CHROME = os.path.join(ROOT, "jeans", "index.html")

TITLES = {
    "index.html": (
        "Custom Denim Manufacturer: MOQ 150, Samples 10-15 Days | Zuoyu",
        "Denim OEM/ODM in Dayong, Zhongshan. 150 pcs per style per colour, sample USD 100 credited, samples 10-15 days, bulk 30-35 days. SMETA audited, CPSIA GCC, RoHS.",
    ),
    "jeans/index.html": (
        "Custom Jeans Manufacturer: MOQ 150, USD 18-26 FOB | Zuoyu",
        "Custom five-pocket jeans, USD 18-26 FOB Shenzhen. MOQ 150 pcs per style per colour, sample USD 100 credited, 10-15 days sampling, 30-35 days bulk.",
    ),
    "denim-jackets/index.html": (
        "Custom Denim Jackets: MOQ 150, From USD 16.57 | Zuoyu",
        "Custom denim jackets, USD 16.57-18.67 FOB Shenzhen. MOQ 150 pcs per style per colour, sample USD 100 credited, 10-15 days sampling, 30-35 days bulk.",
    ),
    "denim-shirts/index.html": (
        "Custom Denim Shirts: MOQ 150, From USD 17.65 | Zuoyu",
        "Custom denim shirts and overshirts, USD 17.65-23.53 FOB Shenzhen. MOQ 150 pcs per style per colour, sample USD 100 credited, 10-15 days sampling.",
    ),
    "denim-dresses/index.html": (
        "Custom Denim Dresses: MOQ 150, From USD 14 | Zuoyu",
        "Custom denim dresses, USD 14-19 FOB Shenzhen. MOQ 150 pcs per style per colour, sample USD 100 credited, 10-15 days sampling, 30-35 days bulk.",
    ),
    "denim-jackets-and-skirts/index.html": (
        "Custom Denim Jackets & Skirts: MOQ 150 | Zuoyu",
        "Custom denim jackets USD 16.57-18.67 and skirts USD 13.97-19.12, FOB Shenzhen. MOQ 150 pcs per style per colour, sample USD 100 credited, sets washed together.",
    ),
}

# old title -> new title (both the <title> and og:title use the same string)
TITLE_SWAPS = {
    "Custom Denim Manufacturer in Dayong, Zhongshan | Zuoyu Garment": TITLES["index.html"][0],
    "Custom Jeans Manufacturer, OEM &amp; ODM | Zuoyu Garment, Zhongshan": TITLES["jeans/index.html"][0],
    "Custom Denim Jacket Manufacturer, OEM &amp; ODM | Zuoyu Garment, Zhongshan": TITLES["denim-jackets/index.html"][0],
    "Custom Denim Shirt Manufacturer, OEM &amp; ODM | Zuoyu Garment, Zhongshan": TITLES["denim-shirts/index.html"][0],
    "Custom Denim Dress Manufacturer — OEM/ODM | Zuoyu Garment": TITLES["denim-dresses/index.html"][0],
    "Custom Denim Jackets &amp; Denim Skirts Manufacturer | Zuoyu Garment": TITLES["denim-jackets-and-skirts/index.html"][0],
}

OLD_DESCS = {
    "Denim OEM/ODM factory in Dayong, Zhongshan: custom jeans, jackets, skirts and dresses. MOQ 150 pcs, samples in 10-15 days. SMETA audited, US CPSIA GCC and RoHS.": TITLES["index.html"][1],
    "Custom jeans manufacturing in Dayong, Zhongshan: rigid, comfort-stretch and high-stretch denim, MOQ 150 pcs, from USD 18-26 FOB Shenzhen.": TITLES["jeans/index.html"][1],
    "Custom denim jackets: trucker, overshirt, chore and biker blocks. MOQ 150 pcs per style per colour, from USD 16.50–23.50 FOB Shenzhen, samples 10–15 days.": TITLES["denim-jackets/index.html"][1],
    "Custom denim shirts and overshirts to your spec: button-down, pullover, shirt-jacket and denim tops. MOQ 150 pcs per style per colour, from USD 17.65–23.53 FOB Shenzhen.": TITLES["denim-shirts/index.html"][1],
    "Custom denim dresses: shirt dresses, pinafores and slip-bib styles. In-house wash development, MOQ 150 pcs, from USD 14 FOB Shenzhen.": TITLES["denim-dresses/index.html"][1],
    "OEM/ODM denim jackets, overshirts and skirts from our Dayong factory - coordinated sets washed together, MOQ 150 pcs, from USD 16.50.": TITLES["denim-jackets-and-skirts/index.html"][1],
}


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


STEPS = [
    ("Step 01 — Brief", "Send what you have",
     "A tech pack, a reference garment, or photographs with a written description. Flat sketches, a size chart and any wash reference you like. Missing pieces are fine — we will tell you what we need before quoting rather than guessing."),
    ("Step 02 — Quote", "Costed quotation in 2 working days",
     "We quote per style with the wash priced as its own line, the hardware tooling (if any) as its own line, and FOB Shenzhen as the default term. You see what each part of the garment costs before committing to a quantity."),
    ("Step 03 — Sample", "10-15 days, USD 100 per style",
     "Pattern making, grading, one sample garment, wash development and a measurement report. The fee is credited against the bulk invoice. You approve against the physical sample; we keep it as the sealed standard."),
    ("Step 04 — Bulk", "30-35 days after approval and deposit",
     "Production runs against the sealed standard and your size chart, with a final AQL inspection, a written report and carton marking per your packing list."),
]

TERMS = [
    ("Minimum order", "150 pcs per style per colour. Adding a colour to an existing style does not reset the style minimum."),
    ("Sampling", "USD 100 per style, credited against the bulk invoice for the same style. 10-15 days."),
    ("Bulk lead time", "30-35 days after sample approval and deposit; 35-45 days when custom hardware tooling is involved."),
    ("Payment", "30% deposit with the order, 70% before shipment, against the inspection report. Terms confirmed on the proforma invoice."),
    ("Incoterm", "FOB Shenzhen by default. EXW and CIF quoted on request; buyer's forwarder welcome."),
    ("Inspection", "Final AQL inspection with a written report and photographs; third-party inspection can be arranged at your cost."),
    ("Packing", "Polybag, hangtag and carton marking per your packing list. Carton drop test report available."),
]

FAQ = [
    ("How do I start an order?",
     "Send a tech pack, a reference garment or photographs plus a size chart to sales2zuoyu@aliyun.com or via the contact form. We reply with what is missing and a first quotation in about 2 working days."),
    ("Can I order one sample before committing to bulk?",
     "Yes. Sampling is USD 100 per style and the fee is credited against the bulk invoice. A sample is the cheapest verification available: it resolves fit, wash and workmanship before bulk money is committed."),
    ("Do you accept small first orders?",
     "Our minimum is 150 pieces per style per colour, which is set by fabric minimums, cutting markers and the wash batch. It is built for first collections, not for container orders."),
    ("What are the payment terms?",
     "30% deposit with the order and 70% before shipment, against the final inspection report. We do not ask for payment before you have seen the quotation broken down line by line."),
    ("Do you arrange shipping?",
     "FOB Shenzhen is the default: we deliver to the port and your forwarder takes over. We can quote CIF or work with your forwarder, and we prepare the export documents."),
    ("What if the sample is wrong?",
     "Comment on measurements rather than impressions — \"waist 2 cm wide, back rise 1.5 cm short\" is a correction we can make. A sample can be right everywhere except one detail and still be unusable, so tell us which feature matters most."),
]


def page_html(header, footer):
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "HowTo", "name": "How to order custom denim from Zuoyu Garment",
             "description": "Four steps from brief to bulk: quotation in 2 working days, sample in 10-15 days for USD 100 credited, bulk in 30-35 days.",
             "totalTime": "P45D",
             "step": [{"@type": "HowToStep", "position": i + 1, "name": head, "text": text}
                      for i, (_kicker, head, text) in enumerate(STEPS)],
             "publisher": {"@id": SITE + "/#organization"}},
            {"@type": "FAQPage",
             "mainEntity": [{"@type": "Question", "name": q,
                             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "How to order", "item": SITE + "/how-to-order/"}]},
        ],
    }

    steps_html = "\n".join(
        '        <article class="card">\n'
        '          <span class="kicker">%s</span>\n'
        '          <h3>%s</h3>\n'
        '          <p>%s</p>\n'
        '        </article>' % (k, h, p) for k, h, p in STEPS)

    terms_html = "\n".join("          <tr><th>%s</th><td>%s</td></tr>" % (k, v) for k, v in TERMS)
    faq_html = "\n".join('        <details><summary>%s</summary>\n          <p>%s</p></details>' % (q, a)
                         for q, a in FAQ)

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>How to Order Custom Denim: Timelines, Samples and Payment | Zuoyu</title>
<meta name="description" content="Four steps from brief to bulk: costed quote in 2 working days, sample in 10-15 days for USD 100 credited against the invoice, bulk in 30-35 days. MOQ 150 pcs.">
<meta name="theme-color" content="#12283f">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Zuoyu Garment">
<meta property="og:title" content="How to Order Custom Denim: Timelines, Samples and Payment | Zuoyu">
<meta property="og:description" content="Four steps from brief to bulk: quote in 2 working days, sample 10-15 days (USD 100 credited), bulk 30-35 days, MOQ 150 pcs per style per colour.">
<meta property="og:url" content="%(site)s/how-to-order/">
<meta property="og:image" content="%(site)s/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="%(site)s/how-to-order/">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">
%(jsonld)s
</script>
</head>
<body>
%(header)s

<main>
  <div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span>How to order</nav></div>

  <div class="page-head"><div class="wrap">
    <p class="eyebrow">How to order</p>
    <h1>How to order custom denim, step by step</h1>
    <p class="lede" style="max-width:70ch">Four steps from brief to bulk: a costed quotation in 2 working days, a first sample in 10-15 days for USD 100 per style (credited against the invoice), and bulk in 30-35 days after approval and deposit. Minimum order is 150 pieces per style per colour.</p>
  </div></div>

  <section>
    <div class="wrap">
      <div class="answer">
        <p><strong>Short answer:</strong> send a tech pack or a reference garment with a size chart; we return a costed quotation in 2 working days with the wash priced separately; you approve a sample in 10-15 days; bulk ships 30-35 days after approval and deposit. No payment is requested before you have seen the itemised quotation.</p>
      </div>

      <h2>The four steps</h2>
      <div class="grid grid-2">
%(steps)s
      </div>

      <h2>What we need from you to quote</h2>
      <p>You do not need a perfect tech pack to start. Send what exists and we will list the gaps before quoting:</p>
      <ul>
        <li>Flat sketches or a reference garment (a physical sample is faster than photographs)</li>
        <li>A measurement sheet, or a size chart to grade from</li>
        <li>Fabric direction: rigid or stretch, and the weight if you know it (10.5-14 oz is typical)</li>
        <li>Wash reference: a garment, a swatch, or photographs plus a described effect</li>
        <li>Trims and labels: buttons, rivets, zips, woven labels, hangtags</li>
        <li>Delivery window and destination port</li>
      </ul>

      <h2>Terms at a glance</h2>
      <table class="fact-table">
        <caption>Order terms — production and payment</caption>
        <tbody>
%(terms)s
        </tbody>
      </table>

      <div class="divider-label">Buyer questions about ordering</div>
      <div class="faq">
%(faq)s
      </div>

      <p style="margin-top:2rem">Related: <a href="/jeans/">denim jeans</a> · <a href="/denim-jackets/">denim jackets</a> · <a href="/denim-shirts/">denim shirts</a> · <a href="/denim-dresses/">denim dresses</a> · <a href="/factory-certifications/">certifications we hold</a> · <a href="/faq/">all buyer FAQ</a></p>
    </div>
  </section>

  <section class="cta-strip"><div class="wrap">
    <div><h2>Start with a brief</h2><p>Photos of the waistband interior, the back pocket and the wash detail are enough for a first quotation.</p></div>
    <a class="btn btn-ghost" href="/contact/">Request a quote</a>
  </div></section>
</main>

%(footer)s
</body>
</html>
""" % {"site": SITE, "jsonld": json.dumps(jsonld, ensure_ascii=False, indent=2),
       "header": header, "footer": footer, "steps": steps_html, "terms": terms_html, "faq": faq_html}


def main():
    header, footer = chrome()
    target = os.path.join(ROOT, "how-to-order", "index.html")
    wr(target, page_html(header, footer))
    print("wrote how-to-order/index.html", os.path.getsize(target), "bytes")

    # sitemap
    sm_path = os.path.join(ROOT, "sitemap.xml")
    sm = rd(sm_path)
    loc = SITE + "/how-to-order/"
    if loc not in sm:
        entry = ('  <url><loc>%s</loc><lastmod>2026-11-06</lastmod>'
                 '<changefreq>monthly</changefreq><priority>0.9</priority></url>\n' % loc)
        wr(sm_path, sm.replace("</urlset>", entry + "</urlset>"))
        print("sitemap: how-to-order added")

    # internal links: footer company list + CTA strips
    pages = []
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if f.endswith(".html"):
                pages.append(os.path.join(dp, f))

    linked = 0
    for p in pages:
        s = rd(p)
        original = s
        s = s.replace('<li><a href="/faq/">Buyer FAQ</a></li>',
                      '<li><a href="/faq/">Buyer FAQ</a></li>\n    '
                      '<li><a href="/how-to-order/">How to order</a></li>', 1)
        if '<a class="btn btn-ghost" href="/contact/">' in s and 'See how ordering works' not in s:
            s = s.replace('<a class="btn btn-ghost" href="/contact/">',
                          '<a class="btn btn-ghost" href="/contact/">', 1)
        if s != original:
            wr(p, s)
            linked += 1
    print("footer links added on", linked, "pages")

    # home: a visible link under the hero buttons
    idx = os.path.join(ROOT, "index.html")
    s = rd(idx)
    if 'How ordering works' not in s:
        anchor = ('          <a class="btn btn-ghost" href="/capabilities/">See wash &amp; sampling</a>\n'
                  '        </div>')
        if anchor in s:
            s = s.replace(anchor, anchor + '\n        <p style="margin-top:.9rem">'
                          '<a href="/how-to-order/">How ordering works, step by step →</a></p>', 1)
            wr(idx, s)
            print("home: how-to-order link added")
        else:
            print("WARNING: home hero anchor not found")

    # titles + descriptions
    changed = 0
    for p in pages:
        s = rd(p)
        original = s
        for old, new in TITLE_SWAPS.items():
            s = s.replace(old, new)
        for old, new in OLD_DESCS.items():
            s = s.replace(old, new)
        if s != original:
            wr(p, s)
            changed += 1
    print("titles/descriptions updated on", changed, "pages")

    bad = []
    for p in pages:
        if not os.path.isfile(p):
            continue
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', rd(p), re.S):
            try:
                json.loads(block)
            except Exception as exc:                          # noqa: BLE001
                bad.append((os.path.relpath(p, ROOT), str(exc)[:60]))
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
