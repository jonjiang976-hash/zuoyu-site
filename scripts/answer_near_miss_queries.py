# -*- coding: utf-8 -*-
"""
Answer the near-miss queries that Google already shows us.

Search Console (28 days) shows the site at:
  do denim shirts shrink           position 11.0
  denim shrinkage percentage       position 76
  how much does denim shrink       position 45
  weight of a pair of jeans        position 72
  how heavy is 10oz                position 94
  how much do jeans weigh          position 98

All three pages already rank; they just answer the question indirectly. This patch
adds direct answers on the pages that already earn the impressions - no URL, title
or H1 changes.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()

# ---------------------------------------------------------------- content

SHRINK_INTRO = """      <h2>Do denim shirts shrink?</h2>
      <p>Yes, and on the first wash a denim shirt usually moves more than a pair of jeans. A sanforized shirting denim (4-8 oz) typically shrinks 2-3% in length and 1-2% in width, so a 74 cm shirt body can lose 1.5-2 cm after one domestic wash. Unsanforized or raw shirting moves 4-5% in length, which is why a raw denim shirt can lose a full 3 cm off the body if the pattern was not compensated.</p>
      <p>Two things make it worse: a hot first wash, and a tumble dry. Two things make it better: a pre-washed fabric, and a pattern cut with the measured shrinkage already added. We wash-test the shirt body before bulk and cut the pattern to the after-wash measurement, so what arrives fits the size chart rather than the greige body.</p>
      <p>If shrinkage on a shirt is critical to you - a uniform programme, for example - say so in the brief. Pre-shrunk fabric or a garment-wash before cutting costs more per piece, but it removes the problem instead of managing it.</p>
"""

SHRINK_TABLE_LEAD = """      <p><strong>The short answer on percentages:</strong> 2-3% in length for sanforized, garment-washed denim; 3-5% when the wash programme is heavy; 5-8% for raw or unsanforized fabric; and 2-4% in length with 3-5% in width on stretch denim. The table below is what those numbers mean by fabric type.</p>
"""

WEIGHT_INTRO = """      <h2>How much does a pair of jeans weigh?</h2>
      <p>A pair of jeans in 12-14 oz denim weighs roughly <strong>600-800 g (1.3-1.8 lb)</strong> at a 32-inch waist. A 10 oz pair sits nearer 500-600 g, and a heavyweight 16 oz raw pair can pass 900 g. The weight of the fabric, not the style, drives that number: the same cut in 10 oz and 14 oz differs by roughly a third.</p>
      <p>If your question is "how heavy is 10 oz", the answer is about 339 g/m&sup2;. Ten ounces per square yard is a mid-weight shirting or a light jean; 12 oz is about 407 g/m&sup2; and is the classic jean weight; 14 oz is about 475 g/m&sup2; and reads as rigid workwear. Freight and carton weight follow directly from this - a 1,500-piece order of 14 oz jeans weighs noticeably more than the same order in 10 oz, and that difference is on your freight invoice.</p>
"""

SHIRT_SENTENCE = """      <p style="margin-top:.9rem;font-size:.95rem;color:#444"><strong>Do denim shirts shrink?</strong> Yes - sanforized shirting denim moves 2-3% in length on the first wash, and raw shirting 4-5%, so we wash-test the body length before bulk and cut the pattern to the after-wash measurement. <a href="/blog/denim-shrinkage-explained/">Full explanation</a>.</p>
"""


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


def main():
    changed = 0

    # 1. shrinkage article: add the shirts section + percentage lead
    p = os.path.join(ROOT, "blog", "denim-shrinkage-explained", "index.html")
    if os.path.isfile(p):
        s = rd(p)
        o = s
        if "Do denim shirts shrink?" not in s:
            s = s.replace('<h2>Why denim shrinks at all</h2>',
                          SHRINK_INTRO + '<h2>Why denim shrinks at all</h2>', 1)
        if "The short answer on percentages" not in s:
            s = s.replace('<h2>The numbers worth putting in a tech pack</h2>',
                          '      <h2>The numbers worth putting in a tech pack</h2>\n' + SHRINK_TABLE_LEAD, 1)
        if s != o:
            wr(p, s)
            changed += 1
            print("updated: blog/denim-shrinkage-explained/")
    else:
        print("missing shrinkage page")

    # 2. weight article: add the "how much does a pair of jeans weigh" section
    p = os.path.join(ROOT, "blog", "denim-weight-guide", "index.html")
    if os.path.isfile(p):
        s = rd(p)
        o = s
        if "How much does a pair of jeans weigh?" not in s:
            s = s.replace('<h2>The weights we run, and what they are for</h2>',
                          WEIGHT_INTRO + '<h2>The weights we run, and what they are for</h2>', 1)
        if s != o:
            wr(p, s)
            changed += 1
            print("updated: blog/denim-weight-guide/")
    else:
        print("missing weight page")

    # 3. shirts category page: one direct-answer line under the answer box
    p = os.path.join(ROOT, "denim-shirts", "index.html")
    if os.path.isfile(p):
        s = rd(p)
        if "Do denim shirts shrink?" not in s:
            anchor = 'against your size chart.</p>\n      </div>'
            if anchor in s:
                s = s.replace(anchor, 'against your size chart.</p>\n' + SHIRT_SENTENCE + '      </div>', 1)
                wr(p, s)
                changed += 1
                print("updated: denim-shirts/")
            else:
                print("anchor not found on shirts page")
    else:
        print("missing shirts page")

    print("pages changed:", changed)

    # 4. bump lastmod for the three edited URLs so crawlers re-read them
    import datetime
    sm_path = os.path.join(ROOT, "sitemap.xml")
    if os.path.isfile(sm_path):
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        sm = rd(sm_path)
        for rel in ("/blog/denim-shrinkage-explained/", "/blog/denim-weight-guide/", "/denim-shirts/"):
            pattern = re.compile(
                r'(<loc>https://zuoyugarment\.com%s</loc>\s*<lastmod>)([^<]*)(</lastmod>)'
                % re.escape(rel))
            sm, n = pattern.subn(lambda m: m.group(1) + today + m.group(3), sm, count=1)
            if n:
                print("lastmod bumped:", rel, "->", today)
        wr(sm_path, sm)

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
                except Exception as exc:                        # noqa: BLE001
                    bad.append((os.path.relpath(fp, ROOT), str(exc)[:60]))
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
