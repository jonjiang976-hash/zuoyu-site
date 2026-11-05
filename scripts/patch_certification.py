# -*- coding: utf-8 -*-
"""
One-off correction: the company does NOT hold OEKO-TEX Standard 100.

Run by the publish workflow when an issue titled "[Patch] ..." is opened.
It rewrites every page that claimed the certificate, regenerates the OEKO-TEX
article with an honest angle (same URL), and exits non-zero on any surprise.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.getcwd()

OLD_FOOTER = ("OEKO-TEX Standard 100 certified; SMETA audited. "
              "We do not hold GRS, BSCI or ISO 9001.")
NEW_FOOTER = ("SMETA audited (Sedex ZAA600231250) · US CPSIA GCC · RoHS. "
              "We do not hold OEKO-TEX, GRS, BSCI or ISO 9001.")

PAGES = [
    "index.html", "about/index.html", "capabilities/index.html", "cases/index.html",
    "contact/index.html", "faq/index.html", "factory-certifications/index.html",
    "denim-glossary/index.html", "privacy-policy/index.html", "terms/index.html",
    "jeans/index.html", "denim-jackets-and-skirts/index.html", "denim-dresses/index.html",
    "404.html", "blog/index.html", "blog/custom-denim-jacket-moq/index.html",
    "blog/denim-finishing-guide/index.html",
]

EXTRA = {
    "index.html": [
        ("MOQ 150 pcs, samples in 10-15 days. OEKO-TEX 100, SMETA audited.",
         "MOQ 150 pcs, samples in 10-15 days. SMETA audited, US CPSIA GCC and RoHS.", 2),
        ('        { "@type": "Certification", "name": "OEKO-TEX Standard 100", '
         '"certificationIdentification": "shared on request" },\n', "", 1),
        ("<div>Compliance<b>OEKO-TEX 100 · SMETA audited</b></div>",
         "<div>Compliance<b>SMETA audited · GCC · RoHS</b></div>", 1),
        ("No. We hold OEKO-TEX Standard 100 and we are SMETA audited.",
         "No. We do not hold OEKO-TEX Standard 100. We are SMETA audited and hold "
         "US CPSIA GCC and RoHS certificates.", 1),
        ("""<tr>
            <th>OEKO-TEX Standard 100</th>
            <td><strong>Held.</strong> Certificate number and current validity are shared on request. Applies to the articles and materials listed on the certificate — ask us for the covered article list before you cite it in your own product copy.</td>
          </tr>""",
         """<tr>
            <th>OEKO-TEX Standard 100</th>
            <td><strong>Not held.</strong> We do not hold OEKO-TEX Standard 100. What we can evidence instead: SMETA audit (ZAA600231250), US CPSIA GCC (BYT26080342) and RoHS (MTL24120600306R01).</td>
          </tr>""", 1),
    ],
    "factory-certifications/index.html": [
        ("Factory &amp; Certifications: OEKO-TEX, SMETA, GCC, RoHS | Zuoyu Garment",
         "Factory &amp; Certifications: SMETA, GCC, RoHS | Zuoyu Garment", 2),
        ("OEKO-TEX 100, SMETA audit ZAA600231250, US CPSIA GCC BYT26080342 and RoHS "
         "certificate MTL24120600306R01. No GRS, BSCI or ISO 9001.",
         "SMETA audit ZAA600231250, US CPSIA GCC BYT26080342 and RoHS certificate "
         "MTL24120600306R01. No OEKO-TEX, GRS, BSCI or ISO 9001.", 2),
        ("We hold OEKO-TEX Standard 100, are SMETA audited (Sedex reference ZAA600231250), "
         "and hold US CPSIA GCC and RoHS certificates for our denim.",
         "We are SMETA audited (Sedex reference ZAA600231250) and hold US CPSIA GCC and "
         "RoHS certificates for our denim. We do not hold OEKO-TEX Standard 100.", 1),
        ("<tr><th>OEKO-TEX Standard 100</th><td><strong>Held.</strong> Certificate number and "
         "current validity are shared on request. It certifies the articles and materials listed "
         "on the certificate — request the covered article list before quoting our certificate in "
         "your own product pages.</td></tr>",
         "<tr><th>OEKO-TEX Standard 100</th><td><strong>Not held.</strong> We do not hold this "
         "certificate, and we do not describe any article as OEKO-TEX certified. Buyers who need "
         "it should source from a supplier that lists the specific articles on a valid "
         "certificate.</td></tr>", 1),
        ("We will send the OEKO-TEX certificate, the SMETA report (ZAA600231250), the GCC and "
         "RoHS certificates, the business licence and bank details in one package.",
         "We will send the SMETA report (ZAA600231250), the GCC and RoHS certificates, the "
         "business licence and bank details in one package.", 1),
    ],
    "faq/index.html": [
        ("MOQ 150 pcs, samples 10-15 days, bulk 30-35 days, OEKO-TEX and SMETA status, "
         "FOB Shenzhen and payment terms",
         "MOQ 150 pcs, samples 10-15 days, bulk 30-35 days, SMETA/GCC/RoHS status, "
         "FOB Shenzhen and payment terms", 2),
        ("No. We hold OEKO-TEX Standard 100 and we are SMETA 4-pillar audited.",
         "No. We do not hold OEKO-TEX Standard 100. We are SMETA audited and hold "
         "US CPSIA GCC and RoHS certificates.", 2),
        ("and we hold OEKO-TEX 100 and SMETA — not GRS or BSCI.",
         "and we are SMETA audited with GCC and RoHS — we do not hold OEKO-TEX, GRS or BSCI.", 1),
        ("Is your denim OEKO-TEX certified?", "Do you hold OEKO-TEX certification?", 2),
        ("OEKO-TEX Standard 100 certificate number and validity shared on request. The "
         "certificate covers the articles and materials listed on it, so request the covered "
         "article list before citing it in your own product copy.",
         "No. We do not hold OEKO-TEX Standard 100, and we will not describe denim as OEKO-TEX "
         "certified. We are SMETA audited (ZAA600231250) and hold US CPSIA GCC (BYT26080342) and "
         "RoHS (MTL24120600306R01). If your programme requires OEKO-TEX, tell us before "
         "quotation.", 2),
    ],
    "terms/index.html": [
        ("We hold OEKO-TEX Standard 100 certified and are SMETA audited. We do not hold GRS, "
         "amfori BSCI or ISO 9001.",
         "We are SMETA audited and hold US CPSIA GCC and RoHS certificates. We do not hold "
         "OEKO-TEX Standard 100, GRS, amfori BSCI or ISO 9001.", 1),
    ],
    "llms.txt": [
        ("OEKO-TEX Standard 100 certificate {{CERT_OEKO_NO}}; SMETA 4-pillar audited. Does not "
         "hold GRS, amfori BSCI or ISO 9001 and does not claim them.",
         "SMETA audited (Sedex reference ZAA600231250), US CPSIA GCC (BYT26080342) and RoHS "
         "(MTL24120600306R01). Does not hold OEKO-TEX, GRS, amfori BSCI or ISO 9001 and does "
         "not claim them.", 1),
        ("location, capacity, OEKO-TEX and SMETA references, and the list of certifications not held.",
         "location, capacity, SMETA/GCC/RoHS references, and the list of certifications not held.", 1),
    ],
    "blog/index.html": [
        ("OEKO-TEX Standard 100 for denim: what it covers and what it does not",
         "OEKO-TEX Standard 100: what it covers, and what we do not claim", 1),
        ("What the certificate actually certifies, which scheme answers which question, and how "
         "to verify a supplier certificate in 60 seconds.",
         "We do not hold OEKO-TEX. What the certificate actually certifies, how to verify a "
         "supplier's, and what we can evidence instead.", 1),
    ],
}

ART_TITLE = "OEKO-TEX Standard 100: What It Covers, and What We Do Not Claim"
ART_SLUG = "oeko-tex-standard-100-denim"
ART_DESC = ("We do not hold OEKO-TEX Standard 100. What the certificate actually covers, how to "
            "verify a supplier's, and what we can evidence instead.")
ART_BODY = """We do not hold OEKO-TEX Standard 100. Saying that in the first sentence costs us enquiries and saves buyers a wasted vendor-onboarding cycle, so this page explains what the certificate actually covers, how to verify one, and what we can evidence instead.

## What OEKO-TEX Standard 100 certifies

It is a product-level certificate. The certificate names an applicant, lists the article groups and materials it applies to, and carries a validity date. Testing is aimed at harmful substances in the finished textile.

Two consequences matter to a buyer:

- **It is article-specific.** Being "OEKO-TEX certified" means the listed articles are certified, not everything a factory can make.
- **It expires.** A certificate that lapsed last year is evidence about last year, not about the order you are placing now.

## What it does not cover

| Question | Scheme that answers it |
| Harmful substances in the garment | OEKO-TEX Standard 100 |
| Recycled content and chain of custody | GRS / RCS |
| Labour conditions, health and safety, ethics | SMETA (Sedex) or amfori BSCI |
| Quality management system | ISO 9001 |
| US consumer product safety documentation | CPSIA, including a General Certificate of Conformity (GCC) |

So "we are OEKO-TEX certified" is not an answer to a labour-standards question. It is an answer to a different question, and a compliance team will notice.

## How to verify a supplier's certificate in 60 seconds

1. Ask for the certificate itself, not a logo image on a website.
2. Check the applicant name against the company on your invoice and contract.
3. Check the validity date and that the article group covers what you are buying.
4. Ask what is not covered — a supplier who can list their gaps is easier to verify than one who claims everything.

## What we hold, and what we do not

| Certificate or audit | Status |
| SMETA (Sedex) | Audited. Report reference ZAA600231250 on file, shared on request |
| US CPSIA General Certificate of Conformity | Held. Report BYT26080342, denim jeans models ZY001-ZY030, manufacture date 20 August 2026 |
| RoHS 2.0 | Held. Certificate MTL24120600306R01 for denim jeans, model ZY2480, issued 16 December 2024 |
| OEKO-TEX Standard 100 | **Not held.** We do not claim it for any article |
| GRS / RCS | **Not held.** We do not claim recycled content |
| amfori BSCI | **Not held.** We are SMETA audited instead |
| ISO 9001 | **Not held.** Quality control is documented per order with AQL inspection reports |

If your programme requires OEKO-TEX, GRS or BSCI, tell us at the first email. We would rather lose the quotation than have you discover the gap after sampling, when the season is already running late.

## Why we publish the gap

Supplier pages usually list everything a buyer might want to see. Buyers have learned to discount that, which makes the claims worthless to the honest suppliers too.

Writing "not held" does three things we can measure: it shortens vendor questionnaires, it removes the risk of a claim collapsing at inspection, and it makes the certificates we do hold easier to believe.

## Where to go next

- [Factory and certification evidence, including the certificate scans](/factory-certifications/)
- [What MOQ 150 actually means for a first order](/blog/custom-denim-jacket-moq/)
- [A buyer's guide to denim finishing](/blog/denim-finishing-guide/)
- [Buyer FAQ: MOQ, lead times and what we do not hold](/faq/)
"""
ART_FAQ = """Do you hold OEKO-TEX Standard 100? | No. We do not hold it and we will not describe our denim as OEKO-TEX certified. We are SMETA audited and hold US CPSIA GCC and RoHS certificates.
Is OEKO-TEX the same as GRS or BSCI? | No. OEKO-TEX Standard 100 tests articles for restricted substances; GRS certifies recycled content and chain of custody; SMETA and BSCI are social audits. They answer different questions and one does not replace another.
What should I ask a supplier for? | The certificate number, the validity date, the list of covered articles, and confirmation that the applicant name matches the company on your invoice — plus an honest list of what they do not hold.
"""


def main():
    changed = 0
    # 1. footer everywhere it still exists
    for rel in PAGES:
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            continue
        s = io.open(p, encoding="utf-8").read()
        if OLD_FOOTER in s:
            io.open(p, "w", encoding="utf-8").write(s.replace(OLD_FOOTER, NEW_FOOTER))
            changed += 1

    # 2. page-specific text
    problems = []
    for rel, rules in EXTRA.items():
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            problems.append("missing " + rel)
            continue
        s = io.open(p, encoding="utf-8").read()
        for old, new, expect in rules:
            n = s.count(old)
            if n != expect:
                problems.append("%s: %d/%d for %r" % (rel, n, expect, old[:50]))
                continue
            s = s.replace(old, new)
        io.open(p, "w", encoding="utf-8").write(s)

    # 3. regenerate the article from markdown
    os.environ.update({
        "TITLE": ART_TITLE, "SLUG": ART_SLUG, "DESCRIPTION": ART_DESC,
        "CATEGORY": "Certification guide", "BODY": ART_BODY, "FAQ": ART_FAQ,
        "DATE": "2026-11-05",
    })
    import publish
    try:
        publish.build_main()
    except SystemExit as exc:
        if exc.code:
            problems.append("article rebuild failed")
    except Exception as exc:                          # noqa: BLE001
        problems.append("article rebuild error: %s" % exc)

    # 4. blog index card text
    idx = os.path.join(ROOT, "blog", "index.html")
    if os.path.isfile(idx):
        s = io.open(idx, encoding="utf-8").read()
        s = s.replace('href="/blog/oeko-tex-standard-100-denim/">OEKO-TEX Standard 100 for denim: '
                      'what it covers and what it does not',
                      'href="/blog/oeko-tex-standard-100-denim/">OEKO-TEX Standard 100: what it '
                      'covers, and what we do not claim')
        io.open(idx, "w", encoding="utf-8").write(s)

    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  -", p)
        return 1
    print("certification correction applied; files touched:", changed + len(EXTRA) + 1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
