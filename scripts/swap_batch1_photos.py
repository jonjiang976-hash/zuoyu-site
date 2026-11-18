# -*- coding: utf-8 -*-
"""
Batch 1 of the report photos: replace two low-resolution factory images with
the higher-resolution versions extracted from the supplier assessment report.

  factory-sewing-2  <- report-06  (2275x1279 sewing floor, symmetric wide shot)
  factory-fabric    <- report-11  (1820x1024 fabric rolls, brighter)

Both images keep their file names, so only the cache tag changes (?v=3 -> ?v=4,
and the fabric image gets its first tag) to force browsers and the CDN to fetch
the new bytes.
"""
import io
import os
import re
import sys

ROOT = os.getcwd()

REPLACEMENTS = [
    ("/assets/img/factory-sewing-2-760.jpg?v=3", "/assets/img/factory-sewing-2-760.jpg?v=4"),
    ("/assets/img/factory-sewing-2.jpg?v=3", "/assets/img/factory-sewing-2.jpg?v=4"),
    ("/assets/img/factory-fabric-760.jpg", "/assets/img/factory-fabric-760.jpg?v=1"),
    ("/assets/img/factory-fabric.jpg", "/assets/img/factory-fabric.jpg?v=1"),
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
            if s != o:
                wr(p, s)
                touched += 1
                print("updated:", os.path.relpath(p, ROOT))
    print("pages updated:", touched)

    # verify every reference now carries a version tag
    bad = []
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            h = rd(p)
            for img in ("factory-sewing-2", "factory-fabric"):
                for m in re.finditer(r'/assets/img/%s[^" ]*' % img, h):
                    ref = m.group(0)
                    if ".jpg?" not in ref:
                        bad.append((os.path.relpath(p, ROOT), ref))
    print("references without a version tag:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
