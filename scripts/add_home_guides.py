# -*- coding: utf-8 -*-
"""
Add a "Buyer guides" block to the homepage.

Why: Bing has only ever crawled the homepage (last crawl 2026-11-02, zero inner
pages). The homepage currently links to the category and style pages but to none
of the twelve articles, so the crawler has no path into the blog. This block puts
every guide one click from the one page that is already indexed.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()

GUIDES = [
    ("first-denim-collection-capsule", "Your first collection",
     "A six-style capsule at 900 pieces: which styles to start with and how to test them."),
    ("low-moq-denim-manufacturing-150-pieces", "What 150 pieces buys",
     "Size curve, colour splitting and where the money goes at the smallest order we take."),
    ("custom-denim-jacket-moq", "What MOQ 150 means",
     "The per-style meaning of the minimum: what it covers and what it blocks."),
    ("denim-factory-quote-line-items", "Reading a factory quote",
     "The twelve line items a real denim quotation contains, and three questions to ask."),
    ("denim-sampling-timeline", "Sampling timeline",
     "What a sample costs, how long it takes and the three input failures that delay it."),
    ("denim-weight-guide", "Denim weight",
     "What 10 oz, 12 oz and 14 oz change in drape, shrinkage, wash and price."),
    ("denim-shrinkage-explained", "Shrinkage",
     "Why the sample fits and the bulk does not, and the three numbers to put in a tech pack."),
    ("denim-washing-costs", "Washing costs",
     "Stone, enzyme, laser and ozone compared: what each finish costs and why wash is its own line."),
    ("denim-finishing-guide", "Choosing a finish",
     "How to pick between stone, enzyme, laser and ozone for a target look and price."),
    ("fob-vs-full-package-denim", "FOB vs full package",
     "One is a shipping term, the other is a service scope. What each covers, and which fits your team."),
    ("private-label-oem-odm", "OEM, ODM or private label",
     "Who designs the garment, who owns the pattern, and whose name goes on it."),
    ("oeko-tex-standard-100-denim", "OEKO-TEX, plainly",
     "What the certificate covers, what we hold instead, and how to check any supplier's claim."),
]

SECTION = """  <section id="guides" class="tight">
    <div class="wrap">
      <div class="section-head">
        <span class="kicker">01c — Buyer guides</span>
        <h2>Twelve guides, written by the people who quote the work</h2>
        <p>Every page below answers a question buyers actually ask us in the first three emails: what the minimum buys, how a quote is built, how a wash is priced, and what to put in a tech pack. No forms, no gate.</p>
      </div>
      <div class="grid grid-3">
%s
      </div>
      <p class="note" style="margin-top:1.5rem"><a href="/blog/">All guides</a> · <a href="/how-to-order/">How ordering works</a> · <a href="/faq/">Buyer FAQ</a></p>
    </div>
  </section>

"""

CARD = """        <article class="card">
          <span class="kicker">Guide</span>
          <h3><a href="/blog/%s/">%s</a></h3>
          <p>%s</p>
          <div class="card-foot"><a href="/blog/%s/">Read the guide</a></div>
        </article>"""


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


def main():
    idx = os.path.join(ROOT, "index.html")
    s = rd(idx)
    if 'id="guides"' in s:
        print("homepage already has the guides block")
        return 0

    cards = "\n".join(CARD % (slug, title, desc, slug) for slug, title, desc in GUIDES)
    block = SECTION % cards

    # insert straight after the "six styles" section
    m = re.search(r'(<section id="styles">.*?</section>\s*)', s, re.S)
    if not m:
        print("ERROR: could not find the styles section")
        return 1
    s = s[:m.end()] + block + s[m.end():]
    wr(idx, s)
    print("guides block added with %d cards" % len(GUIDES))

    # verify
    h = rd(idx)
    missing = [slug for slug, _t, _d in GUIDES if ('href="/blog/%s/"' % slug) not in h]
    print("missing links:", missing if missing else "none")
    bad = []
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            json.loads(blk)
        except Exception as exc:                              # noqa: BLE001
            bad.append(str(exc)[:60])
    print("invalid JSON-LD:", bad if bad else "none")
    print("total /blog/ links on homepage:", h.count('href="/blog/'))
    return 0


if __name__ == "__main__":
    sys.exit(main())
