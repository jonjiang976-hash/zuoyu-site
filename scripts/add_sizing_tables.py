# -*- coding: utf-8 -*-
"""
Add a sizing tab to /tools/: EU / US / UK / Japan / letter sizes, split by garment
type (tops and jackets, trousers, shorts, skirts, men's tops, men's denim).

Everything is framed as the base blocks we grade from, not as an international
standard, because letter sizes and cross-market equivalences are brand-specific.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
TOOLS = os.path.join(ROOT, "tools", "index.html")

TAB_LINK = '    <a href="#sizing">Size conversion</a>\n'

R = lambda cells: "".join("<td>%s</td>" % c for c in cells)


def row(cells, attrs):
    a = " ".join('%s="%s"' % (k, v) for k, v in attrs.items())
    return '            <tr %s><th>%s</th>%s</tr>\n' % (a, cells[0], R(cells[1:]))


# women: eu, us, uk, jp, letter
W = [("34", "2", "6", "7", "XS"), ("36", "4", "8", "9", "S"), ("38", "6", "10", "11", "M"),
     ("40", "8", "12", "13", "M/L"), ("42", "10", "14", "15", "L"), ("44", "12", "16", "17", "XL"),
     ("46", "14", "18", "19", "XXL")]


def wattr(eu, us, uk, jp, letter):
    return {"data-eu": eu, "data-us": us, "data-uk": uk, "data-jp": jp, "data-letter": letter}


# body measurements per size (bust/waist/hip for tops; waist/hip/thigh/inseam for bottoms)
WOMEN_TOPS = {
    "34": ("80-82", "62-64", "36.5-37", "58"), "36": ("84-86", "66-68", "37.5-38", "59"),
    "38": ("88-90", "70-72", "38.5-39", "60"), "40": ("92-94", "74-76", "39.5-40", "61"),
    "42": ("96-98", "78-80", "40.5-41", "62"), "44": ("100-102", "82-84", "41.5-42", "63"),
    "46": ("104-106", "86-88", "42.5-43", "64"),
}
WOMEN_TROUSERS = {
    "34": ("62-64", "88-90", "52-54", "78"), "36": ("66-68", "92-94", "54-56", "78"),
    "38": ("70-72", "96-98", "56-58", "79"), "40": ("74-76", "100-102", "58-60", "79"),
    "42": ("78-80", "104-106", "60-62", "80"), "44": ("82-84", "108-110", "62-64", "80"),
    "46": ("86-88", "112-114", "64-66", "81"),
}
WOMEN_SHORTS = {
    "34": ("62-64", "88-90", "8 / 13 / 18"), "36": ("66-68", "92-94", "8 / 13 / 18"),
    "38": ("70-72", "96-98", "8 / 13 / 18"), "40": ("74-76", "100-102", "8 / 13 / 18"),
    "42": ("78-80", "104-106", "8 / 13 / 18"), "44": ("82-84", "108-110", "8 / 13 / 18"),
    "46": ("86-88", "112-114", "8 / 13 / 18"),
}
WOMEN_SKIRTS = {
    "34": ("62-64", "88-90", "40 / 55 / 75 / 95"), "36": ("66-68", "92-94", "40 / 55 / 75 / 95"),
    "38": ("70-72", "96-98", "40 / 55 / 75 / 95"), "40": ("74-76", "100-102", "40 / 55 / 75 / 95"),
    "42": ("78-80", "104-106", "40 / 55 / 75 / 95"), "44": ("82-84", "108-110", "40 / 55 / 75 / 95"),
    "46": ("86-88", "112-114", "40 / 55 / 75 / 95"),
}

# men: letter, eu, chest, waist, shoulder, back length
MEN_TOPS = [
    ("S", "44-46", "88-92", "74-78", "43-44", "70"),
    ("M", "48", "96-100", "82-86", "45-46", "72"),
    ("L", "50", "104-108", "90-94", "47-48", "74"),
    ("XL", "52", "112-116", "98-102", "49-50", "76"),
    ("XXL", "54", "120-124", "106-110", "51-52", "78"),
    ("3XL", "56", "128-132", "114-118", "53-54", "80"),
]

# men's denim: W code, waist cm, hip cm, EU, JP
MEN_DENIM = [
    ("28", "71-73", "90-92", "44", "S"),
    ("30", "76-78", "95-97", "46", "M"),
    ("32", "81-83", "100-102", "48", "L"),
    ("34", "86-88", "105-107", "50", "XL"),
    ("36", "91-93", "110-112", "52", "2XL"),
    ("38", "96-98", "115-117", "54", "3XL"),
    ("40", "101-103", "120-122", "56", "4XL"),
]

SECTION = """  <section id="sizing"><div class="wrap">
    <h2>4. Size conversion, as we grade it</h2>
    <p>These are the body measurements our base blocks are graded from &mdash; EU, US, UK, Japan and letter sizes side by side. They are not an international standard: letter sizes have no official definition, and retail brands shift the same label by several centimetres. Treat this as the factory baseline, and your own size chart as the override.</p>

    <div class="toolbox" style="max-width:640px;margin:1.2rem 0">
      <label for="sz-cat">Find a size</label>
      <select id="sz-cat">
        <option value="topsw" selected>Women &mdash; tops and jackets</option>
        <option value="trouserw">Women &mdash; trousers and jeans</option>
        <option value="shortsw">Women &mdash; shorts</option>
        <option value="skirtw">Women &mdash; skirts</option>
        <option value="topsm">Men &mdash; tops and jackets</option>
        <option value="denimm">Men &mdash; jeans (W sizes)</option>
      </select>
      <label for="sz-q">Size in any system (e.g. 38, 6, M, W32, 11)</label>
      <input id="sz-q" type="text" placeholder="38">
      <div id="sz-out" class="out"><div><span>Match</span><b id="sz-match">&mdash;</b></div></div>
    </div>

    <h3>Women &mdash; tops and jackets</h3>
    <table class="fact-table size-table" id="tbl-topsw">
      <caption>Body measurements in cm. Bust, waist, shoulder width and back length.</caption>
      <tbody>
        <tr><th>EU</th><th>US</th><th>UK</th><th>JP</th><th>Letter</th><th>Bust</th><th>Waist</th><th>Shoulder</th><th>Back length</th></tr>
%(topsw)s      </tbody>
    </table>

    <h3>Women &mdash; trousers and jeans</h3>
    <table class="fact-table size-table" id="tbl-trouserw">
      <caption>Body measurements in cm. Inseam is the regular/long split we grade to.</caption>
      <tbody>
        <tr><th>EU</th><th>US</th><th>UK</th><th>JP</th><th>Letter</th><th>Waist</th><th>Hip</th><th>Thigh</th><th>Inseam</th></tr>
%(trouserw)s      </tbody>
    </table>

    <h3>Women &mdash; shorts</h3>
    <table class="fact-table size-table" id="tbl-shortsw">
      <caption>Waist and hip in cm; inseam options 3 / 5 / 7 inch (8 / 13 / 18 cm).</caption>
      <tbody>
        <tr><th>EU</th><th>US</th><th>UK</th><th>JP</th><th>Letter</th><th>Waist</th><th>Hip</th><th>Inseam options</th></tr>
%(shortsw)s      </tbody>
    </table>

    <h3>Women &mdash; skirts</h3>
    <table class="fact-table size-table" id="tbl-skirtw">
      <caption>Waist and hip in cm; lengths for mini / above knee / midi / maxi.</caption>
      <tbody>
        <tr><th>EU</th><th>US</th><th>UK</th><th>JP</th><th>Letter</th><th>Waist</th><th>Hip</th><th>Lengths (cm)</th></tr>
%(skirtw)s      </tbody>
    </table>

    <h3>Men &mdash; tops and jackets</h3>
    <table class="fact-table size-table" id="tbl-topsm">
      <caption>Body measurements in cm. Chest, waist, shoulder width and back length.</caption>
      <tbody>
        <tr><th>Letter</th><th>EU</th><th>Chest</th><th>Waist</th><th>Shoulder</th><th>Back length</th></tr>
%(topsm)s      </tbody>
    </table>

    <h3>Men &mdash; jeans (W sizes)</h3>
    <table class="fact-table size-table" id="tbl-denimm">
      <caption>Waist and hip in cm against the W code on the label.</caption>
      <tbody>
        <tr><th>W size</th><th>Waist</th><th>Hip</th><th>EU</th><th>JP</th></tr>
%(denimm)s      </tbody>
    </table>

    <p class="note"><strong>How we grade:</strong> we cut to your size chart, not to ours. These tables are the starting point we quote from and the range we can grade across without re-blocking. If your chart sits between two rows, we grade to yours &mdash; the tables simply say what the base block covers.</p>
  </div></section>

"""


def build_section():
    topsw = "".join(
        row(["", "", "", "", "", *WOMEN_TOPS[eu]], wattr(*s)) for s in W for eu in [s[0]])
    # row() puts the first cell in <th>; for women tables the EU value is the key
    topsw = "".join(
        '            <tr %s><th>%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n'
        % (" ".join('%s="%s"' % kv for kv in wattr(*s).items()), s[0], s[1], s[2], s[3], s[4],
           *[dash(x) for x in WOMEN_TOPS[s[0]]])
        for s in W)
    trouserw = "".join(
        '            <tr %s><th>%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n'
        % (" ".join('%s="%s"' % kv for kv in wattr(*s).items()), s[0], s[1], s[2], s[3], s[4],
           *[dash(x) for x in WOMEN_TROUSERS[s[0]]])
        for s in W)
    shortsw = "".join(
        '            <tr %s><th>%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n'
        % (" ".join('%s="%s"' % kv for kv in wattr(*s).items()), s[0], s[1], s[2], s[3], s[4],
           *[dash(x) for x in WOMEN_SHORTS[s[0]]])
        for s in W)
    skirtw = "".join(
        '            <tr %s><th>%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n'
        % (" ".join('%s="%s"' % kv for kv in wattr(*s).items()), s[0], s[1], s[2], s[3], s[4],
           *[dash(x) for x in WOMEN_SKIRTS[s[0]]])
        for s in W)
    topsm = "".join(
        '            <tr data-letter="%s" data-eu="%s"><th>%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n'
        % (t[0], t[1], t[0], t[1], dash(t[2]), dash(t[3]), dash(t[4]), dash(t[5])) for t in MEN_TOPS)
    denimm = "".join(
        '            <tr data-w="%s" data-eu="%s" data-jp="%s"><th>W%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n'
        % (d[0], d[3], d[4], d[0], dash(d[1]), dash(d[2]), d[3], d[4]) for d in MEN_DENIM)

    return SECTION % {"topsw": topsw, "trouserw": trouserw, "shortsw": shortsw,
                      "skirtw": skirtw, "topsm": topsm, "denimm": denimm}


SCRIPT = """
<script>
(function(){
  var cat = document.getElementById("sz-cat"), q = document.getElementById("sz-q"),
      out = document.getElementById("sz-out"), matchEl = document.getElementById("sz-match");
  if (!cat || !q) { return; }
  var labels = {eu:"EU", us:"US", uk:"UK", jp:"JP", letter:"Letter", w:"W"};
  function run(){
    var table = document.getElementById("tbl-" + cat.value);
    if (!table) { return; }
    Array.prototype.forEach.call(table.querySelectorAll("tbody tr"), function(tr){ tr.classList.remove("hit"); });
    var v = q.value.trim().toUpperCase().replace(/^W/, "").replace(/\\s+/g, "");
    if (!v) { matchEl.textContent = "\\u2014"; return; }
    var hit = null, hitKey = "";
    Array.prototype.forEach.call(table.querySelectorAll("tbody tr"), function(tr){
      if (hit) { return; }
      ["eu","us","uk","jp","letter","w"].forEach(function(k){
        if (hit) { return; }
        var dv = tr.getAttribute("data-" + k);
        if (dv && dv.toUpperCase() === v) { hit = tr; hitKey = k; }
      });
    });
    if (!hit) { matchEl.textContent = "no match in this table"; return; }
    hit.classList.add("hit");
    var cells = Array.prototype.map.call(hit.children, function(c){ return c.textContent.trim(); });
    var head = Array.prototype.map.call(table.querySelectorAll("tbody tr:first-child th"), function(c){ return c.textContent.trim(); });
    var pairs = [];
    for (var i = 0; i < cells.length && i < head.length; i++) {
      if (cells[i]) { pairs.push(head[i] + " " + cells[i]); }
    }
    matchEl.textContent = pairs.join("  \\u00b7  ");
  }
  cat.addEventListener("change", run);
  q.addEventListener("input", run);
})();
</script>
</body>"""

EXTRA_CSS = """  .size-table{width:auto;max-width:100%;border-collapse:collapse;table-layout:auto;margin:.4rem 0 1.2rem}
  .size-table caption{caption-side:top;text-align:left;text-transform:none;letter-spacing:0;font-size:.82rem;color:#666;padding:.2rem 0 .55rem}
  .size-table th,.size-table td{padding:.42rem .5rem;border-bottom:1px solid #e3e3dd;font-size:.88rem;text-align:left;white-space:nowrap;font-variant-numeric:tabular-nums}
  .size-table tbody th{font-weight:600}
  .size-table tr.hit{background:#f2f6f8}
  .size-table tr.hit th{font-weight:700}
  .table-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
"""


def dash(v):
    """Use an en dash inside measurement ranges so they never look like minus signs."""
    return v.replace(" - ", "\u2013").replace("-", "\u2013")



def main():
    s = io.open(TOOLS, encoding="utf-8").read()
    if 'id="sizing"' in s:
        print("sizing tab already present")
        return 0

    # tab link after the cartons tab
    s = s.replace('    <a href="#carton">Cartons &amp; containers</a>\n',
                  '    <a href="#carton">Cartons &amp; containers</a>\n' + TAB_LINK, 1)

    # styles: hit row + caption
    s = s.replace("  .tabs a:hover{background:var(--canvas-2)}",
                  "  .tabs a:hover{background:var(--canvas-2)}\n" + EXTRA_CSS, 1)

    # section before the "How these numbers are defined" part
    anchor = '  <section class="tight"><div class="wrap">\n    <h2>How these numbers are defined</h2>'
    if anchor not in s:
        print("ERROR: anchor for the sizing section not found")
        return 1
    _sec = build_section()
    _sec = re.sub(r'(<table class="fact-table size-table".*?</table>)',
                  lambda m: '<div class="table-scroll">' + m.group(1) + '</div>',
                  _sec, flags=re.S)
    s = s.replace(anchor, _sec + anchor, 1)

    # script: inject before </body>
    s = s.replace("</body>", SCRIPT.strip() + "\n", 1)

    # meta + title mention sizing
    s = s.replace("<title>Denim Costing Tools: Consumption, oz to GSM, Cartons | Zuoyu</title>",
                  "<title>Denim Tools: Costing, oz to GSM, Cartons, Sizes | Zuoyu</title>", 1)
    s = s.replace('content="Three free calculators for denim buyers: fabric consumption and cost, oz to gsm with weight classes, and carton/container loading with freight per piece."',
                  'content="Four free tools for denim buyers: fabric consumption and cost, oz to gsm, carton and container loading, and EU/US/UK/Japan size conversion."', 1)

    io.open(TOOLS, "w", encoding="utf-8", newline="\n").write(s)
    print("sizing tab added, page bytes:", len(s))

    # lastmod bump for /tools/
    import datetime
    sm_path = os.path.join(ROOT, "sitemap.xml")
    if os.path.isfile(sm_path):
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        sm = io.open(sm_path, encoding="utf-8").read()
        sm2 = re.sub(r'(<loc>https://zuoyugarment\.com/tools/</loc>\s*<lastmod>)([^<]*)(</lastmod>)',
                     lambda m: m.group(1) + today + m.group(3), sm, count=1)
        if sm2 != sm:
            io.open(sm_path, "w", encoding="utf-8", newline="\n").write(sm2)
            print("lastmod bumped for /tools/ ->", today)

    # verify JSON-LD still parses
    bad = []
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            json.loads(blk)
        except Exception as exc:                                # noqa: BLE001
            bad.append(str(exc)[:60])
    print("invalid JSON-LD:", bad if bad else "none")
    print("tables:", s.count("size-table"), "| tab links:", s.count('href="#sizing"'))
    return 0


if __name__ == "__main__":
    sys.exit(main())
