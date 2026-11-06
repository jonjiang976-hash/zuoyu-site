# -*- coding: utf-8 -*-
"""
Swap in the new workshop photos: fix the intrinsic dimensions, refresh the alt
text, and add a cache-busting version so browsers/CDN fetch the new files.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
NAMES = ["factory-cutting", "factory-sewing-1", "factory-sewing-2",
         "factory-sewing-3", "factory-samples"]
URL_RE = re.compile(r"(/assets/img/(?:%s)(?:-760)?\.jpg)(?=[\"\s])" % "|".join(NAMES))

ALT_FIXES = [
    ('alt="Cutting room at the Zuoyu Garment denim factory: markers laid out and fabric layered"',
     'alt="Fabric spread on the cutting table at the Zuoyu Garment denim factory"'),
    ('alt="Cutting table and marker making"',
     'alt="Fabric spread on the cutting table before cutting"'),
    ('alt="Cutting room where jeans panels are cut"',
     'alt="Fabric spread on the cutting table before jeans panels are cut"'),
    ('alt="Cutting table"', 'alt="Fabric spread on the cutting table"'),
    ('alt="CAD pattern plotter printing markers in the factory"',
     'alt="Cut denim panels bundled and waiting for the sewing lines"'),
    ('alt="Sewing line"', 'alt="Operator at a computerised sewing machine"'),
]


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def fix_tag(tag):
    if not any(n in tag for n in NAMES):
        return tag
    tag = tag.replace('width="800"', 'width="1500"').replace('height="450"', 'height="843"')
    tag = URL_RE.sub(r"\1?v=2", tag)
    return tag


def main():
    changed = 0
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            s = rd(p)
            original = s
            s = re.sub(r"<img[^>]*>", lambda m: fix_tag(m.group(0)), s)
            for old, new in ALT_FIXES:
                s = s.replace(old, new)
            if s != original:
                wr(p, s)
                changed += 1
                print("updated", os.path.relpath(p, ROOT).replace("\\", "/"))
    print("pages changed:", changed)

    # sanity: every html still parses its JSON-LD
    bad = []
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', rd(p), re.S):
                try:
                    json.loads(block)
                except Exception as exc:                      # noqa: BLE001
                    bad.append((os.path.relpath(p, ROOT), str(exc)[:60]))
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
