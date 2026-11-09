# -*- coding: utf-8 -*-
"""
Close the internal-link loop: each style page links back to the capsule guide
(and the quote guide), so authority flows both ways instead of one way.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()

SKUS = ["custom-wide-leg-jeans", "custom-straight-leg-jeans", "custom-cargo-jeans",
        "custom-denim-shorts", "custom-eyelet-denim-jacket", "custom-long-denim-skirt"]

BLOCK = """
      <div class="divider-label">Related reading</div>
      <p class="related-reading">
        <a href="/blog/first-denim-collection-capsule/">Your first denim collection: a six-style capsule at 900 pieces</a> ·
        <a href="/blog/denim-factory-quote-line-items/">How to read a denim factory quote</a> ·
        <a href="/how-to-order/">How ordering works</a>
      </p>
"""


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def main():
    changed = 0
    for slug in SKUS:
        p = os.path.join(ROOT, slug, "index.html")
        if not os.path.isfile(p):
            print("missing", slug)
            continue
        s = rd(p)
        if "first-denim-collection-capsule" in s:
            print("already linked:", slug)
            continue
        anchor = re.search(r'<p style="margin-top:2rem">Related:.*?</p>\s*', s, re.S)
        if not anchor:
            print("  WARNING: related paragraph not found on", slug)
            continue
        s = s[:anchor.end()] + BLOCK.lstrip("\n") + s[anchor.end():]
        wr(p, s)
        changed += 1
        print("related reading added:", slug)
    print("pages changed:", changed)

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
