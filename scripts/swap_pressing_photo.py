# -*- coding: utf-8 -*-
"""
Put the real pressing-station photo in place of the last old stock image.

factory-sewing-3 (800x450, still the old photo) is used on the homepage hero
frame and on /capabilities/. Replace it with factory-pressing (1500x843) and
bump the cache version so the browser does not keep the old file.
"""
import io
import os
import re
import sys

ROOT = os.getcwd()

REPLACEMENTS = [
    ("/assets/img/factory-sewing-3-760.jpg?v=3", "/assets/img/factory-pressing-760.jpg?v=1"),
    ("/assets/img/factory-sewing-3.jpg?v=3", "/assets/img/factory-pressing.jpg?v=1"),
    ("/assets/img/factory-sewing-3-760.jpg", "/assets/img/factory-pressing-760.jpg?v=1"),
    ("/assets/img/factory-sewing-3.jpg", "/assets/img/factory-pressing.jpg?v=1"),
]

CAPTIONS = [
    # homepage "inside the workshop" tile
    ("<b>Finishing and assembly</b> · same site as cutting, sample room and QC",
     "<b>Pressing and finishing</b> · jeans ironed, checked and folded before packing"),
    # capabilities gallery note
    ("Cutting, sewing and final inspection — same site, same team",
     "Cutting, pressing and final inspection — same site, same team"),
]


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


def main():
    touched = 0
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            s = rd(p)
            o = s
            for a, b in REPLACEMENTS:
                s = s.replace(a, b)
            for a, b in CAPTIONS:
                s = s.replace(a, b)
            if s == o:
                continue
            # correct the intrinsic size on every swapped img tag
            def fix(m):
                tag = m.group(0)
                tag = re.sub(r'width="\d+"', 'width="1500"', tag, count=1)
                tag = re.sub(r'height="\d+"', 'height="843"', tag, count=1)
                return tag
            s = re.sub(r'<img[^>]*factory-pressing\.jpg[^>]*>', fix, s)
            wr(p, s)
            touched += 1
            print("updated:", os.path.relpath(p, ROOT))

    print("pages updated:", touched)

    # verify
    left = []
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if f.endswith(".html") and "factory-sewing-3" in rd(os.path.join(dp, f)):
                left.append(f)
    print("pages still referencing the old photo:", left if left else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
