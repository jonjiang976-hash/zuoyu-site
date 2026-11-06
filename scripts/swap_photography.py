# -*- coding: utf-8 -*-
"""
Photography pass #2.

Final state of the workshop photos:
  replaced (1500x843, new):   factory-sewing-1, factory-sewing-2, factory-samples
  kept old  (800x450):        factory-cutting, factory-sewing-3
                              (the old cutting shot is cleaner than the new one,
                               and the pressing station still needs a reshoot)
All five get ?v=3 so browsers and the CDN drop any earlier copy.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()

REPLACED = ["factory-sewing-1", "factory-sewing-2", "factory-samples"]
KEPT_OLD = ["factory-cutting", "factory-sewing-3"]
ALL = REPLACED + KEPT_OLD

URL_V3 = re.compile(r"(/assets/img/(?:%s)(?:-760)?\.jpg)(?:\?v=\d+)?(?=[\"\s])" % "|".join(ALL))

ALT_FIXES = [
    # cutting photo goes back to the old (clean) shot, so its alt goes back too
    ('alt="Fabric spread on the cutting table at the Zuoyu Garment denim factory"',
     'alt="Cutting room at the Zuoyu Garment denim factory: markers laid out and fabric layered"'),
    ('alt="Fabric spread on the cutting table before cutting"',
     'alt="Cutting room at the Zuoyu Garment denim factory"'),
    ('alt="Fabric spread on the cutting table before jeans panels are cut"',
     'alt="Cutting room where jeans panels are cut"'),
    ('alt="Fabric spread on the cutting table"',
     'alt="Cutting room at the Zuoyu Garment denim factory"'),
    # factory-sewing-3 is the pressing station, not a sewing machine
    ('alt="Operator at a computerised sewing machine"',
     'alt="Pressing station where finished garments are ironed before packing"'),
    ('alt="Sewing operators at work in the Zuoyu Garment denim factory"',
     'alt="Pressing station where finished jeans are ironed before packing"'),
]


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def fix_tag(tag):
    if not any(n in tag for n in ALL):
        return tag
    if any(n in tag for n in REPLACED):
        tag = tag.replace('width="800"', 'width="1500"').replace('height="450"', 'height="843"')
    else:
        tag = tag.replace('width="1500"', 'width="800"').replace('height="843"', 'height="450"')
    return URL_V3.sub(r"\1?v=3", tag)


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
