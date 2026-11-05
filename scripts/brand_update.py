# -*- coding: utf-8 -*-
"""
Brand pass: put the ZUOYU logo in the header/footer of every page and add a
brand story to /about/.

Runs from the repo root; the publish workflow calls it for a "[Patch] ...
brand" issue.
"""
import io
import os
import re
import sys

ROOT = os.getcwd()
LOGO = "/assets/img/logo-zuoyu.png"
LOGO_MARK = "/assets/img/logo-zuoyu-mark.png"
STACKED = "/assets/img/logo-zuoyu-stacked.png"

HEADER_OLD = '<span class="brand-mark">Zuoyu</span>'
HEADER_NEW = (
    '<span class="brand-mark" style="display:block">'
    '<img src="%s" alt="Zuoyu Garment — denim OEM manufacturer" width="487" height="96" '
    'style="display:block;height:1.95rem;width:auto" decoding="async"></span>' % LOGO)

STORY = """  <section class="tight">
    <div class="wrap">
      <div class="story">
        <figure class="story-figure">
          <img src="%s" alt="Zuoyu Denim logo" width="360" height="397" loading="lazy" decoding="async" class="story-logo">
        </figure>
        <div>
          <p class="kicker">Our story</p>
          <h2>A factory built around one fabric, not a catalogue of everything</h2>
          <p>Zuoyu Garment was registered in Zhongshan on 16 April 2019, in Dayong — a town in Guangdong that has been washing and sewing denim for decades. The name was chosen for a simple reason: the label inside a garment is the one thing a brand cannot outsource, and we wanted to be the company that makes the thing behind that label.</p>
          <p>We made one deliberate decision early on and have kept it: <strong>denim only</strong>. Not denim plus knitwear, not denim plus accessories. Four categories — jeans, jackets, shirts and dresses — and the wash development that holds them together. Staying inside a single fabric is why a wash trial here takes days rather than an overseas round trip, and why the person who approves your sample can walk to the laundry instead of emailing a third party.</p>
          <p>The second decision was about size. Our minimum is 150 pieces per style per colour because that is where fabric minimums, cutting markers and a wash batch start to behave predictably. It is a number built for first collections and small brands, not for container orders — those we can still run, but they are not who the factory was designed for.</p>
          <p>The third decision is the one buyers notice last and rely on most: we publish what we do <em>not</em> hold. No OEKO-TEX Standard 100, no GRS, no amfori BSCI, no ISO 9001. What we do hold is a SMETA audit (Sedex reference ZAA600231250), a US CPSIA General Certificate of Conformity (BYT26080342) and a RoHS certificate (MTL24120600306R01). A supplier page that lists everything is easy to write and impossible to verify; a short list that survives a vendor questionnaire is worth more to both sides.</p>
          <blockquote>We would rather lose a quotation at the first email than lose a buyer at the inspection.</blockquote>
          <p>Today the site runs 2,300 m² of production and warehouse space with four sewing lines, an in-house laundry for stone, enzyme, laser and ozone finishing, two QC staff and two people in sampling and pattern development. Buyers reach us through this site or through our two Alibaba storefronts, and they get the same answer from the same team on either channel.</p>
        </div>
      </div>

      <h3 style="margin-top:2.6rem">Zuoyu at a glance</h3>
      <table class="fact-table">
        <tbody>
          <tr><th>Founded</th><td>16 April 2019, Zhongshan, Guangdong, China</td></tr>
          <tr><th>Focus</th><td>Denim only: jeans, jackets, shirts, dresses — OEM and ODM</td></tr>
          <tr><th>Site</th><td>2,300 m² production and warehouse, Dayong Town, Zhongshan</td></tr>
          <tr><th>Capacity</th><td>Four sewing lines; in-house laundry for stone, enzyme, laser and ozone wash</td></tr>
          <tr><th>Team</th><td>Four merchandisers working in English, two QC, two in sampling and pattern development</td></tr>
          <tr><th>Minimum order</th><td>150 pieces per style per colour</td></tr>
          <tr><th>Sampling</th><td>10–15 days; USD 100 per style, credited against the bulk invoice</td></tr>
          <tr><th>Bulk lead time</th><td>30–35 days after sample approval and deposit</td></tr>
          <tr><th>Certificates held</th><td>SMETA audit ZAA600231250 · US CPSIA GCC BYT26080342 · RoHS MTL24120600306R01</td></tr>
          <tr><th>Not held</th><td>OEKO-TEX Standard 100, GRS/RCS, amfori BSCI, ISO 9001 — we do not claim them</td></tr>
          <tr><th>Storefronts</th><td><a href="https://zuoyufashion.en.alibaba.com/" rel="noopener">Womenswear on Alibaba</a> · <a href="https://zuoyumen.en.alibaba.com/" rel="noopener">Menswear on Alibaba</a></td></tr>
        </tbody>
      </table>
    </div>
  </section>

""" % STACKED

ORG_JSONLD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://zuoyugarment.com/#organization",
  "name": "Zhongshan Zuoyu Garment Co., Ltd.",
  "alternateName": "Zuoyu Garment",
  "url": "https://zuoyugarment.com/",
  "logo": "https://zuoyugarment.com/assets/img/logo-zuoyu.png",
  "image": "https://zuoyugarment.com/assets/img/og-image.jpg",
  "foundingDate": "2019-04-16",
  "foundingLocation": { "@type": "Place", "name": "Zhongshan, Guangdong, China" },
  "description": "Denim OEM/ODM manufacturer in Dayong, Zhongshan, Guangdong, producing custom jeans, denim jackets, denim shirts and denim dresses from 150 pieces per style per colour.",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "6/F, No. 168, Yongheng Road, Qinggang Community, Dayong Town",
    "addressLocality": "Zhongshan",
    "addressRegion": "Guangdong",
    "addressCountry": "CN"
  },
  "email": "sales2zuoyu@aliyun.com",
  "telephone": "+86 138 2700 5889",
  "sameAs": [
    "https://zuoyufashion.en.alibaba.com/",
    "https://zuoyumen.en.alibaba.com/"
  ]
}
</script>
"""

CSS = """
/* --- brand: logo in header/footer and the about-page story --- */
.brand-mark img{display:block}
.story{display:grid;grid-template-columns:210px 1fr;gap:clamp(1.4rem,3vw,3rem);align-items:start}
.story-logo{width:100%;max-width:210px;height:auto;margin:0}
.story blockquote{margin:1.6rem 0 1.2rem;padding:.2rem 0 .2rem 1rem;border-left:2px solid var(--copper);
  font-family:var(--serif);font-size:1.12rem;line-height:1.45;color:var(--ink)}
@media (max-width:760px){
  .story{grid-template-columns:1fr}
  .story-figure{max-width:150px;margin:0}
}
"""


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def main():
    pages = []
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if f.endswith(".html"):
                pages.append(os.path.join(dp, f))

    replaced = 0
    for p in pages:
        s = rd(p)
        if HEADER_OLD in s:
            wr(p, s.replace(HEADER_OLD, HEADER_NEW))
            replaced += 1
    print("brand mark replaced on", replaced, "pages")

    # about page: story section + organization schema
    about = os.path.join(ROOT, "about", "index.html")
    s = rd(about)
    if "Our story" not in s:
        anchor = """  </div></div>

  <section>
    <div class="wrap">
      <div class="answer">"""
        if anchor not in s:
            print("ERROR: about-page anchor not found")
            return 1
        s = s.replace(anchor, "  </div></div>\n\n" + STORY + "  <section>\n    <div class=\"wrap\">\n      <div class=\"answer\">", 1)
        print("about: story section inserted")
    else:
        print("about: story already present")

    if '"foundingDate"' not in s:
        s = s.replace("</head>", ORG_JSONLD + "</head>", 1)
        print("about: Organization schema added")
    wr(about, s)

    # css additions
    css_path = os.path.join(ROOT, "assets", "style.css")
    css = rd(css_path)
    if "--- brand: logo in header" not in css:
        wr(css_path, css + CSS)
        print("style.css: brand styles appended")

    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
