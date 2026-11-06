# -*- coding: utf-8 -*-
"""
Finalise the workshop photography in one pass.

1. The old cutting photo is restored (it is cleaner than the reshoot).
2. factory-samples is really the packing department: rename the reference to
   factory-packing and fix the caption / alt text.
3. Replaced photos get 1500x843; photos still on the old 800x450 shot keep their
   real dimensions.
4. Every reference gets ?v=3 so no cached copy is reused.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()

NEW_LONG = ["factory-sewing-1", "factory-sewing-2", "factory-packing"]   # 1500x843
OLD_SHORT = ["factory-cutting", "factory-sewing-3"]                     # 800x450
ALL = NEW_LONG + OLD_SHORT

TEXT_FIXES = [
    # factory-samples is the packing department
    ("/assets/img/factory-samples-760.jpg", "/assets/img/factory-packing-760.jpg"),
    ("/assets/img/factory-samples.jpg", "/assets/img/factory-packing.jpg"),
    ('alt="Cut denim panels bundled and waiting for the sewing lines"',
     'alt="Packing department where finished denim garments are polybagged before cartoning"'),
    ('<figcaption><b>Pattern plotting</b>Markers printed in-house</figcaption>',
     '<figcaption><b>Packing &amp; dispatch</b>Finished garments bagged before cartoning</figcaption>'),
    # cutting photo is the old (clean) shot again
    ('alt="Fabric spread on the cutting table at the Zuoyu Garment denim factory"',
     'alt="Cutting room at the Zuoyu Garment denim factory: markers laid out and fabric layered"'),
    ('alt="Fabric spread on the cutting table before cutting"',
     'alt="Cutting room at the Zuoyu Garment denim factory"'),
    ('alt="Fabric spread on the cutting table before jeans panels are cut"',
     'alt="Cutting room where jeans panels are cut"'),
    ('alt="Fabric spread on the cutting table"',
     'alt="Cutting room at the Zuoyu Garment denim factory"'),
    # the pressing station was mislabelled as a sewing machine
    ('alt="Operator at a computerised sewing machine"',
     'alt="Pressing station where finished garments are ironed before packing"'),
    ('alt="Sewing operators at work in the Zuoyu Garment denim factory"',
     'alt="Pressing station where finished jeans are ironed before packing"'),
]

URL_RE = re.compile(r"(/assets/img/(?:%s)(?:-760)?\.jpg)(?:\?v=\d+)?(?=[\"\s])" % "|".join(ALL))


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def fix_tag(tag):
    if not any(n in tag for n in ALL):
        return tag
    if any(n in tag for n in NEW_LONG):
        tag = tag.replace('width="800"', 'width="1500"').replace('height="450"', 'height="843"')
    else:
        tag = tag.replace('width="1500"', 'width="800"').replace('height="843"', 'height="450"')
    return URL_RE.sub(r"\1?v=3", tag)


def fix_fabric(tag):
    if "factory-fabric" not in tag:
        return tag
    return tag.replace('width="800"', 'width="1500"').replace('height="450"', 'height="843"')


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
            for old, new in TEXT_FIXES:
                s = s.replace(old, new)
            s = re.sub(r"<img[^>]*>", lambda m: fix_fabric(fix_tag(m.group(0))), s)
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
