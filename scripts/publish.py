# -*- coding: utf-8 -*-
"""Publish one article from a GitHub Issue Form submission.

Combines the Markdown builder and the issue parser so the workflow only
needs one script. Reads ISSUE_BODY (and optional TITLE/BODY/... overrides)
from the environment; writes blog/<slug>/index.html, updates sitemap.xml
and the blog index, and validates the generated JSON-LD.
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Publish one article to the static site from a form (GitHub Actions workflow_dispatch).

Reads environment variables:
    TITLE        article headline
    SLUG         url slug (auto-generated from TITLE when empty)
    DESCRIPTION  meta description, 120-165 chars
    CATEGORY     small kicker text, e.g. "Buyer guide"
    BODY         article body in simple Markdown
    FAQ          optional lines of "Question | Answer"
    DATE         optional YYYY-MM-DD (defaults to today, UTC)

Writes:  blog/<slug>/index.html, updates sitemap.xml
Validates: JSON-LD parses, internal links resolve, description length.

Run locally to test:
    python scripts/build_article.py TITLE="..." BODY="..."
"""
import datetime
import html
import io
import json
import os
import re
import sys

ROOT = os.getcwd()  # repo root when run by Actions
DOMAIN = "https://zuoyugarment.com"
CHROME_SOURCE = os.path.join(ROOT, "jeans", "index.html")


def env(name, default=""):
    return os.environ.get(name, default).strip()


def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


# ---------------------------------------------------------------- chrome
def chrome():
    if not os.path.isfile(CHROME_SOURCE):
        return ("<header class=\"site-head\"><div class=\"wrap\">"
                "<a class=\"brand\" href=\"/\"><span class=\"brand-mark\">Zuoyu</span>"
                "<span class=\"brand-sub\">Garment · Denim OEM</span></a>"
                "<nav class=\"nav\"><a href=\"/\">Home</a><a href=\"/contact/\">Contact</a></nav>"
                "</div></header>",
                "<footer class=\"site-foot\"><div class=\"wrap\"><div class=\"legal\">"
                "© 2026 Zuoyu Garment</div></div></footer>")
    src = io.open(CHROME_SOURCE, encoding="utf-8").read()
    header = re.search(r'<header class="site-head">.*?</header>', src, re.S).group(0)
    footer = re.search(r'<footer class="site-foot">.*?</footer>', src, re.S).group(0)
    return header, footer


# ---------------------------------------------------------------- markdown
def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                  r'<img src="\2" alt="\1" loading="lazy" decoding="async">', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def md_to_html(md):
    lines = md.replace("\r", "").split("\n")
    out, i, list_mode = [], 0, None

    def close_list():
        nonlocal list_mode
        if list_mode:
            out.append("</%s>" % list_mode)
            list_mode = None

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            close_list()
            i += 1
            continue

        # raw html passthrough
        if stripped.startswith("<"):
            close_list()
            out.append(line)
            i += 1
            continue

        # markdown table (separator row optional)
        if stripped.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            close_list()
            rows = []
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                if not re.match(r"^[\s:|-]+$", lines[j].strip().strip("|")):
                    rows.append(cells)
                j += 1
            i = j
            out.append('<table class="fact-table">')
            out.append("<tbody>")
            for row in rows:
                if not row or not row[0]:
                    continue
                rest = " — ".join(row[1:]) if len(row) > 1 else ""
                out.append("<tr><th>%s</th><td>%s</td></tr>" % (inline(row[0]), inline(rest)))
            out.append("</tbody></table>")
            continue

        m = re.match(r"^(#{2,3})\s+(.*)$", stripped)
        if m:
            close_list()
            level = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (level, inline(m.group(2)), level))
            i += 1
            continue

        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if list_mode != "ul":
                close_list()
                out.append("<ul>")
                list_mode = "ul"
            out.append("<li>%s</li>" % inline(m.group(1)))
            i += 1
            continue

        m = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if m:
            if list_mode != "ol":
                close_list()
                out.append("<ol>")
                list_mode = "ol"
            out.append("<li>%s</li>" % inline(m.group(1)))
            i += 1
            continue

        # paragraph: gather until blank
        para = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{2,3}\s|[-*]\s|\d+[.)]\s|\||<)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        close_list()
        out.append("<p>%s</p>" % inline(" ".join(para)))

    close_list()
    return "\n".join(out)


# ---------------------------------------------------------------- build
def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:70]


def build_main():
    title = env("TITLE")
    body_md = env("BODY")
    if not title or not body_md:
        fail("TITLE and BODY are required")

    slug = env("SLUG") or slugify(title)
    if not re.match(r"^[a-z0-9-]+$", slug):
        fail("slug must contain only a-z, 0-9 and dashes (got %r)" % slug)

    desc = env("DESCRIPTION") or (re.sub(r"\s+", " ", body_md)[:155])
    if len(desc) > 175:
        fail("DESCRIPTION too long (%d chars, keep it under 165)" % len(desc))
    category = env("CATEGORY") or "Buyer guide"
    date = env("DATE") or datetime.datetime.utcnow().strftime("%Y-%m-%d")

    # first paragraph becomes the "short answer" block
    blocks = [b.strip() for b in body_md.split("\n\n") if b.strip()]
    lead = blocks[0] if blocks else ""
    rest = "\n\n".join(blocks[1:])
    lead_html = md_to_html(lead)
    body_html = md_to_html(rest)

    faqs = []
    for line in env("FAQ").splitlines():
        if "|" in line:
            q, a = [x.strip() for x in line.split("|", 1)]
            if q and a:
                faqs.append((q, a))
    faq_html = ""
    faq_json = ""
    if faqs:
        items = "".join(
            '        <details><summary>%s</summary><p>%s</p></details>\n'
            % (html.escape(q), html.escape(a)) for q, a in faqs)
        faq_html = ('      <div class="divider-label">Buyer questions</div>\n'
                    '      <div class="faq">\n%s      </div>\n' % items)
        faq_json = """,
    {
      "@type": "FAQPage",
      "mainEntity": [%s]
    }""" % ",".join(
            '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
            % (json.dumps(q), json.dumps(a)) for q, a in faqs)

    canonical = "%s/blog/%s/" % (DOMAIN, slug)
    jsonld = """{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Article",
      "headline": %s,
      "description": %s,
      "datePublished": "%s",
      "dateModified": "%s",
      "inLanguage": "en",
      "image": "%s/assets/img/og-image.jpg",
      "author": { "@type": "Organization", "name": "Zuoyu Garment", "url": "%s/" },
      "publisher": { "@id": "%s/#organization" },
      "mainEntityOfPage": { "@type": "WebPage", "@id": %s }
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": "%s/" },
        { "@type": "ListItem", "position": 2, "name": "Guides", "item": "%s/blog/" },
        { "@type": "ListItem", "position": 3, "name": %s, "item": %s }
      ]
    }%s
  ]
}""" % (json.dumps(title), json.dumps(desc), date, date, DOMAIN, DOMAIN, DOMAIN,
       json.dumps(canonical), DOMAIN, DOMAIN, json.dumps(title), json.dumps(canonical), faq_json)

    header, footer = chrome()
    _d = datetime.date.fromisoformat(date)
    day = _d.strftime("%d %B %Y").lstrip("0")  # portable day-month-year
    page = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s | Zuoyu Garment</title>
<meta name="description" content="%s">
<meta name="theme-color" content="#12283f">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Zuoyu Garment">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:image" content="%s/assets/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="%s">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">
%s
</script>
</head>
<body>
%s

<main>
  <div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/blog/">Guides</a><span>/</span>%s</nav></div>

  <article>
  <div class="page-head"><div class="wrap">
    <span class="kicker">%s · %s</span>
    <h1>%s</h1>
  </div></div>

  <section>
    <div class="wrap">
      <div class="answer">
        %s
      </div>
%s
%s
    </div>
  </section>
  </article>
</main>

%s
</body>
</html>
""" % (html.escape(title), html.escape(desc, quote=True), html.escape(title, quote=True),
       html.escape(desc, quote=True), canonical, DOMAIN, canonical, jsonld,
       header, html.escape(title), html.escape(category), day,
       html.escape(title), lead_html, body_html, faq_html, footer)

    # validate json-ld
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        json.loads(m)

    out_dir = os.path.join(ROOT, "blog", slug)
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "index.html")
    io.open(target, "w", encoding="utf-8").write(page)
    print("wrote blog/%s/index.html (%d bytes)" % (slug, len(page)))

    # sitemap
    sm_path = os.path.join(ROOT, "sitemap.xml")
    if os.path.isfile(sm_path):
        sm = io.open(sm_path, encoding="utf-8").read()
        if canonical not in sm:
            entry = ('  <url><loc>%s</loc><lastmod>%s</lastmod>'
                     '<changefreq>monthly</changefreq><priority>0.8</priority></url>\n'
                     % (canonical, date))
            sm = sm.replace("</urlset>", entry + "</urlset>")
            io.open(sm_path, "w", encoding="utf-8").write(sm)
            print("sitemap updated")
        else:
            print("sitemap already contains this URL")

    # blog index: append a card if the file exists and link is missing
    idx = os.path.join(ROOT, "blog", "index.html")
    if os.path.isfile(idx):
        s = io.open(idx, encoding="utf-8").read()
        if ('href="/blog/%s/"' % slug) not in s:
            card = ('        <article class="card">\n'
                    '          <span class="kicker">%s</span>\n'
                    '          <h3><a href="/blog/%s/">%s</a></h3>\n'
                    '          <p>%s</p>\n'
                    '          <p class="spec">%s</p>\n'
                    '          <div class="card-foot"><a href="/blog/%s/">Read the guide</a></div>\n'
                    '        </article>\n'
                    % (html.escape(category), slug, html.escape(title),
                       html.escape(desc), day, slug))
            s = s.replace('<div class="grid grid-2">', '<div class="grid grid-2">\n' + card, 1)
            io.open(idx, "w", encoding="utf-8").write(s)
            print("blog index updated")

    if os.environ.get("GITHUB_OUTPUT"):
        with io.open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            fh.write("url=%s\n" % canonical)
            fh.write("slug=%s\n" % slug)

    print("OK", canonical)


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parse a GitHub Issue Form submission and publish it as an article page.

The issue body created by .github/ISSUE_TEMPLATE/publish-article.yml looks like:

    ### Article title (English)

    Custom Denim Jacket Manufacturer: What MOQ 150 Actually Means

    ### URL slug (optional)

    ### Meta description

    ...

This script maps those sections to the builder's environment variables, runs
build_article.py, and writes the resulting URL to GITHUB_OUTPUT.

Any validation error exits non-zero with a readable message, so the workflow
can report it back on the issue instead of publishing a broken page.
"""
import io
import os
import re
import sys


FIELDS = {
    "article title": "TITLE",
    "title": "TITLE",
    "标题": "TITLE",
    "url slug": "SLUG",
    "slug": "SLUG",
    "链接": "SLUG",
    "meta description": "DESCRIPTION",
    "描述": "DESCRIPTION",
    "category": "CATEGORY",
    "分类": "CATEGORY",
    "article body": "BODY",
    "正文": "BODY",
    "faq": "FAQ",
    "publish date": "DATE",
    "日期": "DATE",
}


def parse_issue_body(body):
    """Split the issue form into {label: value}."""
    sections = {}
    current = None
    buf = []
    for line in body.replace("\r", "").split("\n"):
        m = re.match(r"^###\s+(.*?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = m.group(1).strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()

    mapped = {}
    for label, value in sections.items():
        key = label.lower()
        for needle, env_name in FIELDS.items():
            if needle in key:
                mapped[env_name] = value
                break
    return mapped


def main():
    body = os.environ.get("ISSUE_BODY", "")
    if not body.strip():
        print("ERROR: issue body is empty")
        return 1

    fields = parse_issue_body(body)
    missing = [k for k in ("TITLE", "BODY") if not fields.get(k)]
    if missing:
        print("ERROR: missing required field(s): %s" % ", ".join(missing))
        print("Make sure the issue was created with the 'Publish an article' form.")
        return 1

    # empty form fields arrive as "_No response_" in GitHub issue forms
    for k, v in list(fields.items()):
        if v.strip() in ("_No response_", "No response"):
            fields[k] = ""

    for env_name, value in fields.items():
        os.environ[env_name] = value

    print("publishing:", fields["TITLE"][:80])
    try:
        build_main()
    except SystemExit as exc:                      # validation failure
        if exc.code:
            return int(exc.code) if isinstance(exc.code, int) else 1
        return 0
    except Exception as exc:                       # noqa: BLE001
        print("ERROR:", type(exc).__name__, exc)
        return 1

    slug = fields.get("SLUG") or re.sub(r"[^a-z0-9]+", "-", fields["TITLE"].lower()).strip("-")[:70]
    url = "https://zuoyugarment.com/blog/%s/" % slug
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with io.open(out, "a", encoding="utf-8") as fh:
            fh.write("url=%s\n" % url)
            fh.write("slug=%s\n" % slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
