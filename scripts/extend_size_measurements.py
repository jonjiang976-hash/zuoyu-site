# -*- coding: utf-8 -*-
"""
Extend the two jeans tables on /tools/denim-size-chart/ with the measurements
buyers actually ask for.

Men's denim gains: thigh, knee, leg opening, front rise and inseam options.
Women's trousers gain: front rise and leg opening.

Increments follow the factory: thigh +2 cm in full circumference per size (1 cm per
half), waist +5 cm per W code, rise and leg opening +1 cm, knee +1 cm.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
PAGE = os.path.join(ROOT, "tools", "denim-size-chart", "index.html")

# W code -> (waist, hip, thigh, knee, leg opening, front rise, inseam options)
MEN = {
    "28": ("71–73", "90–92", "52–54", "38–40", "34–36", "26–27", "76 / 81 / 86"),
    "30": ("76–78", "95–97", "54–56", "39–41", "35–37", "27–28", "76 / 81 / 86"),
    "32": ("81–83", "100–102", "56–58", "40–42", "36–38", "28–29", "76 / 81 / 86"),
    "34": ("86–88", "105–107", "58–60", "41–43", "37–39", "29–30", "76 / 81 / 86"),
    "36": ("91–93", "110–112", "60–62", "42–44", "38–40", "30–31", "76 / 81 / 86"),
    "38": ("96–98", "115–117", "62–64", "43–45", "39–41", "31–32", "76 / 81 / 86"),
    "40": ("101–103", "120–122", "64–66", "44–46", "40–42", "32–33", "76 / 81 / 86"),
}

# EU size -> (front rise, leg opening)
WOMEN = {
    "34": ("22–23", "28–30"), "36": ("23–24", "29–31"), "38": ("24–25", "30–32"),
    "40": ("25–26", "31–33"), "42": ("26–27", "32–34"), "44": ("27–28", "33–35"),
    "46": ("28–29", "34–36"),
}

MEN_CAPTION = ("Body measurements in cm. Thigh, knee and leg opening are garment "
               "measurements taken flat and doubled; inseam options are 30 / 32 / 34 inch.")
WOMEN_CAPTION = ("Body measurements in cm. Inseam is the regular/long split we grade to; "
                 "front rise is measured from the crotch seam to the top of the waistband.")

MEN_NOTE = ('<p class="note" style="margin-top:.8rem">Denim has almost no stretch unless '
            'elastane is added, so our jeans carry 1&ndash;2 cm of ease at the waist and '
            '2&ndash;3 cm at the hip over the body measurements above. If you sit between two '
            'W codes, take the smaller one for a close fit &mdash; the waist can be let out, '
            'the hip cannot.</p>')

WOMEN_NOTE = ('<p class="note" style="margin-top:.8rem">Between two EU sizes? The smaller one '
              'gives a close fit and the waistband has 1&ndash;2 cm of seam allowance to let '
              'out; the hip has none.</p>')


def main():
    if not os.path.isfile(PAGE):
        print("missing tools/denim-size-chart/index.html")
        return 1
    s = io.open(PAGE, encoding="utf-8").read()
    orig = s

    # ---------------- men's denim: header ----------------
    old_head = ("<tr><th>W size</th><th>Waist</th><th>Hip</th><th>EU</th><th>JP</th></tr>")
    new_head = ("<tr><th>W size</th><th>Waist</th><th>Hip</th><th>Thigh</th><th>Knee</th>"
                "<th>Leg opening</th><th>Front rise</th><th>Inseam (cm)</th><th>EU</th><th>JP</th></tr>")
    if old_head in s:
        s = s.replace(old_head, new_head, 1)
        print("men's header extended")
    elif new_head in s:
        print("men's header already extended")
    else:
        print("WARNING: men's header not found")

    # ---------------- men's denim: rows ----------------
    def men_row(m):
        w, eu, jp = m.group(1), m.group(2), m.group(3)
        data = MEN.get(w)
        if not data:
            return m.group(0)
        waist, hip, thigh, knee, opening, rise, inseam = data
        return ('<tr data-w="%s" data-eu="%s" data-jp="%s"><th>W%s</th><td>%s</td><td>%s</td>'
                '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                % (w, eu, jp, w, waist, hip, thigh, knee, opening, rise, inseam, eu, jp))

    row_re = re.compile(
        r'<tr data-w="(\d+)" data-eu="(\d+)" data-jp="([^"]+)"><th>W\d+</th>'
        r'<td>[^<]*</td><td>[^<]*</td>(?:<td>[^<]*</td><td>[^<]*</td>)*<td>\d+</td><td>[^<]*</td></tr>')
    s, n = row_re.subn(men_row, s)
    print("men's rows rewritten:", n)

    s = s.replace("<caption>Waist and hip in cm against the W code on the label.</caption>",
                  "<caption>%s</caption>" % MEN_CAPTION, 1)

    # ---------------- women's trousers: header ----------------
    old_whead = ("<tr><th>EU</th><th>US</th><th>UK</th><th>JP</th><th>Letter</th>"
                 "<th>Waist</th><th>Hip</th><th>Thigh</th><th>Inseam</th></tr>")
    new_whead = ("<tr><th>EU</th><th>US</th><th>UK</th><th>JP</th><th>Letter</th>"
                 "<th>Waist</th><th>Hip</th><th>Thigh</th><th>Front rise</th>"
                 "<th>Leg opening</th><th>Inseam</th></tr>")
    if old_whead in s:
        s = s.replace(old_whead, new_whead, 1)
        print("women's header extended")
    elif new_whead in s:
        print("women's header already extended")

    def women_row(m):
        row, eu = m.group(0), m.group(1)
        data = WOMEN.get(eu)
        if not data or "<th>Front rise</th>" in row:
            return row
        rise, opening = data
        # insert rise + opening before the final inseam cell
        return row.replace("</tr>", "<td>%s</td><td>%s</td></tr>" % (0, 0)).replace(
            "<td>0</td><td>0</td>", "")

    # ---------------- women's trousers: rows (scoped to that table only) ----------------
    def women_table(m):
        block = m.group(0)

        def women_row2(mm):
            g0 = mm.group(0)
            cells = mm.group(2)
            eu = mm.group(1)
            data = WOMEN.get(eu)
            if not data:
                return g0
            rise, opening = data
            pos = g0.find(cells)
            if pos < 0:
                return g0
            idx = cells.rfind("<td>")
            if idx < 0:
                return g0
            new_cells = cells[:idx] + "<td>%s</td><td>%s</td>" % (rise, opening) + cells[idx:]
            return g0[:pos] + new_cells + g0[pos + len(cells):]

        block = re.sub(r'<tr data-eu="(\d+)"[^>]*><th>\d+</th>(.*?)</tr>', women_row2, block, flags=re.S)
        block = block.replace("<caption>Body measurements in cm. Inseam is the regular/long split we grade to.</caption>",
                              "<caption>%s</caption>" % WOMEN_CAPTION, 1)
        return block

    s = re.sub(r'<table[^>]*id="tbl-trouserw".*?</table>', women_table, s, flags=re.S)

    # ---------------- notes ----------------
    if "Denim has almost no stretch unless" not in s:
        m = re.search(r'(<table[^>]*id="tbl-denimm".*?</table>)', s, re.S)
        if m:
            s = s[:m.end(1)] + "\n" + MEN_NOTE + s[m.end(1):]
            print("men's note added")
    if "Between two EU sizes?" not in s:
        m = re.search(r'(<table[^>]*id="tbl-trouserw".*?</table>)', s, re.S)
        if m:
            s = s[:m.end(1)] + "\n" + WOMEN_NOTE + s[m.end(1):]
            print("women's note added")

    if s != orig:
        io.open(PAGE, "w", encoding="utf-8", newline="\n").write(s)
        print("page updated | bytes:", len(s))
    else:
        print("page unchanged")

    # verify
    t = io.open(PAGE, encoding="utf-8").read()
    for tid in ("tbl-denimm", "tbl-trouserw"):
        m = re.search(r'<table[^>]*id="%s".*?</table>' % tid, t, re.S)
        head = re.search(r'<tr[^>]*>(.*?)</tr>', m.group(0), re.S)
        cols = [re.sub('<[^>]+>', '', c).strip()
                for c in re.findall(r'<t[hd][^>]*>.*?</t[hd]>', head.group(1), re.S)]
        rows = len(re.findall(r'<tr\b', m.group(0))) - 1
        print("%-14s rows=%d cols=%d %s" % (tid, rows, len(cols), cols))

    bad = []
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            json.loads(blk)
        except Exception as exc:                                # noqa: BLE001
            bad.append(str(exc)[:50])
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
