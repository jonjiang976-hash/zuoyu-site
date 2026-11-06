# -*- coding: utf-8 -*-
"""
Add an AggregateOffer to every Product JSON-LD block.

Google's product-snippet report requires one of offers / review / aggregateRating.
We publish real FOB price bands on the pages, so the offer uses the same range.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
ORG_ID = "https://zuoyugarment.com/#organization"
SITE = "https://zuoyugarment.com"


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def price_range(props):
    for item in props:
        if item.get("name") == "Price range (FOB)":
            m = re.search(r"([\d.]+)\s*[–-]\s*([\d.]+)", item.get("value", ""))
            if m:
                return m.group(1), m.group(2)
    return None


def patch_block(block, canonical):
    d = json.loads(block)
    if not isinstance(d, dict) or d.get("@type") != "Product":
        return None
    if "offers" in d:            # already done
        return None
    pr = price_range(d.get("additionalProperty", []))
    if not pr:
        return None
    low, high = pr
    d["offers"] = {
        "@type": "AggregateOffer",
        "priceCurrency": "USD",
        "lowPrice": "%.2f" % float(low),
        "highPrice": "%.2f" % float(high),
        "availability": "https://schema.org/InStock",
        "url": canonical,
        "seller": {"@id": ORG_ID},
    }
    d.setdefault("image", SITE + "/assets/img/og-image.jpg")
    return json.dumps(d, ensure_ascii=False, indent=2)


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
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            canonical = SITE + "/" + (rel[: -len("/index.html")] + "/" if rel.endswith("/index.html") else rel)
            out, made = [], False
            def repl(m):
                nonlocal made
                new = patch_block(m.group(2), canonical)
                if new is None:
                    return m.group(0)
                made = True
                return m.group(1) + "\n" + new + "\n" + m.group(3)
            s2 = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)', repl, s, flags=re.S)
            if made and s2 != s:
                wr(p, s2)
                changed += 1
                print("offers added:", rel)
    print("pages updated:", changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
