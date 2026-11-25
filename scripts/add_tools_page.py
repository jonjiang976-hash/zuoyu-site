# -*- coding: utf-8 -*-
"""
Build /tools/ - three denim costing calculators - and wire it into the site.

  * fabric consumption, cost per garment and per order (with the mill lot-minimum warning)
  * oz/yd2 <-> g/m2 with denim weight classes
  * carton CBM, pieces per container, freight per piece

Also: nav link on every page, links from three articles, sitemap entry, llms.txt line.
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
SITE = "https://zuoyugarment.com"
CHROME = os.path.join(ROOT, "jeans", "index.html")

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Denim Costing Tools: Consumption, oz to GSM, Cartons | Zuoyu</title>
<meta name="description" content="Three free calculators for denim buyers: fabric consumption and cost, oz to gsm with weight classes, and carton/container loading with freight per piece.">
<meta name="theme-color" content="#12283f">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Zuoyu Garment">
<meta property="og:title" content="Denim Costing Tools: Consumption, oz to GSM, Cartons">
<meta property="og:description" content="Three free calculators for denim buyers: fabric consumption and cost, oz to gsm with weight classes, carton and container loading.">
<meta property="og:url" content="https://zuoyugarment.com/tools/">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://zuoyugarment.com/tools/">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@graph": [
  {
   "@type": "WebApplication",
   "name": "Denim Costing Toolkit",
   "url": "https://zuoyugarment.com/tools/",
   "applicationCategory": "BusinessApplication",
   "operatingSystem": "Any",
   "description": "Free calculators for denim buyers: fabric consumption and cost, oz to gsm conversion with denim weight classes, and carton CBM with container loading and freight per piece.",
   "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
   "publisher": {"@id": "https://zuoyugarment.com/#organization"}
  },
  {
   "@type": "BreadcrumbList",
   "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://zuoyugarment.com/"},
    {"@type": "ListItem", "position": 2, "name": "Tools", "item": "https://zuoyugarment.com/tools/"}
   ]
  }
 ]
}
</script>
<style>
  .toolgrid{display:grid;grid-template-columns:1fr 1fr;gap:1.6rem;align-items:start;margin:1.2rem 0}
  @media(max-width:760px){.toolgrid{grid-template-columns:1fr}}
  .toolbox{background:var(--canvas-2);border:1px solid #e3e3dd;border-radius:6px;padding:1.1rem 1.2rem}
  .toolbox h3{margin-top:0}
  .toolbox label{display:block;font-size:.82rem;letter-spacing:.04em;text-transform:uppercase;color:#666;margin:.7rem 0 .2rem}
  .toolbox input[type=number],.toolbox select{width:100%;padding:.5rem .6rem;border:1px solid #cfcfc7;border-radius:4px;font:inherit;background:#fff}
  .toolbox input[type=range]{width:100%}
  .out{margin-top:1rem;border-top:1px solid #dcdcd4;padding-top:.8rem}
  .out div{display:flex;justify-content:space-between;gap:1rem;padding:.28rem 0;font-size:.95rem}
  .out b{font-variant-numeric:tabular-nums}
  .warn{margin-top:.8rem;padding:.6rem .7rem;border-left:3px solid #b4552b;background:#fdf4ef;font-size:.88rem;color:#7a3a1d}
  .cls{width:100%;border-collapse:collapse;margin-top:.6rem;font-size:.9rem}
  .cls th,.cls td{border-bottom:1px solid #e3e3dd;padding:.35rem .2rem;text-align:left}
  .cls tr.hit{background:#f2f6f8;font-weight:600}
  .tabs{display:flex;gap:.5rem;flex-wrap:wrap;margin:1.6rem 0 0}
  .tabs a{padding:.5rem .9rem;border:1px solid #cfcfc7;border-radius:4px;text-decoration:none;font-size:.9rem}
  .tabs a:hover{background:var(--canvas-2)}
  .toolgrid,.toolbox,.out{min-width:0}
  .toolbox input,.toolbox select{box-sizing:border-box;max-width:100%%}
  h1,h2{overflow-wrap:anywhere}
  .row3{display:flex;gap:.5rem}
  .row3 input{flex:1 1 0;min-width:0}
</style>
</head>
<body>
__HEADER__

<main>
  <div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span>Tools</nav></div>

  <div class="page-head"><div class="wrap">
    <p class="eyebrow">Tools</p>
    <h1>Denim Costing Toolkit</h1>
    <p class="lede" style="max-width:70ch">Three calculators buyers and merchandisers use before a quotation: fabric consumption and cost, ounce-to-gram weight with the garment each weight suits, and carton loading with freight per piece. Free, no signup.</p>
  </div></div>

  <div class="wrap tabs">
    <a href="#consumption">Fabric consumption &amp; cost</a>
    <a href="#weight">oz to gsm</a>
    <a href="#carton">Cartons &amp; containers</a>
  </div>

  <section id="consumption"><div class="wrap">
    <h2>1. Fabric consumption and cost</h2>
    <p>The production method: net panel area divided by usable fabric width times marker efficiency, plus end loss and defect allowance. Pick a garment to load its panel area, then adjust.</p>
    <div class="toolgrid">
      <div class="toolbox">
        <label for="garment">Garment</label>
        <select id="garment">
          <option value="1.00" selected>5-pocket jeans</option>
          <option value="1.55">Denim jacket</option>
          <option value="0.85">Denim skirt</option>
          <option value="0.62">Denim shorts</option>
        </select>
        <label for="size">Size (adjusts panel area)</label>
        <select id="size">
          <option value="0.88">XS</option>
          <option value="0.94">S</option>
          <option value="1.00" selected>M</option>
          <option value="1.06">L</option>
          <option value="1.13">XL</option>
          <option value="1.20">XXL</option>
        </select>
        <label for="area">Net panel area (m&sup2; per garment)</label>
        <input id="area" type="number" step="0.01" value="1.00">
        <label for="width">Usable fabric width (m)</label>
        <input id="width" type="number" step="0.01" value="1.50">
        <label for="eff">Marker efficiency: <span id="effv">84%</span></label>
        <input id="eff" type="range" min="70" max="95" value="84">
        <label for="allow">End loss + defect allowance: <span id="allowv">10%</span></label>
        <input id="allow" type="range" min="0" max="15" value="10">
        <label for="price">Fabric price (USD per metre)</label>
        <input id="price" type="number" step="0.05" value="4.00">
        <label for="qty">Quantity (pieces)</label>
        <input id="qty" type="number" step="1" value="150">
      </div>
      <div class="toolbox">
        <h3>Result</h3>
        <div class="out">
          <div><span>Consumption per garment</span><b id="r-cons">-</b></div>
          <div><span>Fabric cost per garment</span><b id="r-cost">-</b></div>
          <div><span>Fabric for the order</span><b id="r-order">-</b></div>
          <div><span>Total fabric cost</span><b id="r-total">-</b></div>
        </div>
        <div id="r-warn" class="warn" hidden></div>
        <p style="font-size:.85rem;color:#666;margin-top:.9rem">Marker efficiency: one size alone runs 78-81%, three sizes nested 83-86%, six sizes 86-89%. Narrower fabric and better nesting both cut consumption.</p>
      </div>
    </div>
  </div></section>

  <section id="weight"><div class="wrap">
    <h2>2. Denim weight: oz/yd&sup2; to g/m&sup2;</h2>
    <p>One ounce per square yard is 33.906 g/m&sup2;. Convert either way; the table shows what each weight is actually used for.</p>
    <div class="toolgrid">
      <div class="toolbox">
        <label for="oz">Ounces per square yard (oz/yd&sup2;)</label>
        <input id="oz" type="number" step="0.1" value="12">
        <label for="gsm">Grams per square metre (g/m&sup2;)</label>
        <input id="gsm" type="number" step="1" value="407">
        <p style="font-size:.85rem;color:#666;margin-top:.9rem">Typical denim sits between 8 and 16 oz. The same 12 oz fabric feels softer after a heavy wash &mdash; weight sets the starting stiffness, not the finish.</p>
      </div>
      <div class="toolbox">
        <h3>What that weight is for</h3>
        <table class="cls" id="cls-table">
          <thead><tr><th>oz/yd&sup2;</th><th>g/m&sup2;</th><th>Usual use</th></tr></thead>
          <tbody>
            <tr data-min="0" data-max="8"><td>up to 8</td><td>up to 271</td><td>Shirts, light tops</td></tr>
            <tr data-min="9" data-max="11"><td>9-11</td><td>305-373</td><td>Women's jeans, shirt-jackets</td></tr>
            <tr data-min="12" data-max="13"><td>12-13</td><td>407-441</td><td>Classic men's jeans</td></tr>
            <tr data-min="14" data-max="15"><td>14-15</td><td>475-509</td><td>Rigid raw denim, workwear</td></tr>
            <tr data-min="16" data-max="99"><td>16 and up</td><td>543 and up</td><td>Heavyweight raw denim, jackets</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div></section>

  <section id="carton"><div class="wrap">
    <h2>3. Cartons, containers and freight per piece</h2>
    <p>Carton volume, how many pieces fit a container, and what the ocean freight adds to each piece. Container capacity is the usual industry figure; confirm the usable volume with your forwarder.</p>
    <div class="toolgrid">
      <div class="toolbox">
        <label>Carton size (cm)</label>
        <div class="row3">
          <input id="cl" type="number" step="0.5" value="60" aria-label="Carton length cm">
          <input id="cw" type="number" step="0.5" value="40" aria-label="Carton width cm">
          <input id="ch" type="number" step="0.5" value="38" aria-label="Carton height cm">
        </div>
        <label for="pcs">Pieces per carton</label>
        <input id="pcs" type="number" step="1" value="20">
        <label for="cont">Container</label>
        <select id="cont">
          <option value="28">20GP (about 28 CBM)</option>
          <option value="58" selected>40GP (about 58 CBM)</option>
          <option value="68">40HQ (about 68 CBM)</option>
        </select>
        <label for="qty2">Order quantity (pieces)</label>
        <input id="qty2" type="number" step="1" value="1500">
        <label for="freight">Ocean freight per container (USD)</label>
        <input id="freight" type="number" step="50" value="2800">
      </div>
      <div class="toolbox">
        <h3>Result</h3>
        <div class="out">
          <div><span>Volume per carton</span><b id="c-cbm">-</b></div>
          <div><span>Pieces per container (85% load)</span><b id="c-percont">-</b></div>
          <div><span>Cartons for the order</span><b id="c-cartons">-</b></div>
          <div><span>Containers needed</span><b id="c-conts">-</b></div>
          <div><span>Freight per piece</span><b id="c-freight">-</b></div>
        </div>
        <p style="font-size:.85rem;color:#666;margin-top:.9rem">Usable volume assumes 85% fill. Real loads depend on carton size, stacking and the line's stowage plan.</p>
      </div>
    </div>
  </div></section>

  <section class="tight"><div class="wrap">
    <h2>How these numbers are defined</h2>
    <p><strong>Consumption</strong> is net panel area divided by (usable width &times; marker efficiency), multiplied by one plus the end-loss and defect allowance. It is the same method we use when quoting small orders, so the output is comparable with a quotation rather than a textbook figure.</p>
    <p><strong>Weight</strong> uses the standard conversion of 1 oz/yd&sup2; = 33.906 g/m&sup2;. Denim class ranges are the ones we see across the styles we run, not a formal standard.</p>
    <p><strong>Container capacity</strong> is the commonly quoted usable volume (20GP 28 CBM, 40GP 58 CBM, 40HQ 68 CBM) at 85% fill. Confirm with your forwarder before booking; we are not a freight forwarder.</p>
    <p class="note">These calculators are indicative. A quotation against your tech pack or reference garment is the only number that holds.</p>
  </div></section>

  <section class="cta-strip"><div class="wrap">
    <div><h2>Want these numbers against your own style?</h2><p>Send the tech pack or a reference garment and we will quote consumption, wash and FOB separately.</p></div>
    <a class="btn btn-ghost" href="/contact/">Start a brief</a>
  </div></section>

  <section class="tight"><div class="wrap">
    <h2>Where to go next</h2>
    <p><a href="/blog/low-moq-denim-manufacturing-150-pieces/">What 150 pieces buys</a> &middot; <a href="/blog/denim-weight-guide/">Denim weight explained</a> &middot; <a href="/blog/denim-factory-quote-line-items/">How to read a factory quote</a> &middot; <a href="/capabilities/">What we do in-house</a> &middot; <a href="/contact/">Request a quote</a></p>
  </div></section>
</main>

__FOOTER__

<script>
(function(){
  "use strict";
  var nf = new Intl.NumberFormat("en-US");
  function num(id){ var v = parseFloat(document.getElementById(id).value); return isFinite(v) ? v : 0; }
  function money(v){ return "USD " + v.toLocaleString("en-US", {minimumFractionDigits: 2, maximumFractionDigits: 2}); }

  // --- tool 1 -------------------------------------------------------------
  var gEl = document.getElementById("garment"),
      sEl = document.getElementById("size"),
      aEl = document.getElementById("area");

  function syncArea(){
    var base = parseFloat(gEl.value) || 1,
        factor = parseFloat(sEl.value) || 1;
    aEl.value = (base * factor).toFixed(2);
    calcConsumption();
  }

  function calcConsumption(){
    var area = num("area"), width = num("width"),
        eff = num("eff") / 100, allow = num("allow") / 100,
        price = num("price"), qty = num("qty");
    document.getElementById("effv").textContent = Math.round(eff * 100) + "%";
    document.getElementById("allowv").textContent = Math.round(allow * 100) + "%";

    if (width <= 0 || eff <= 0) { return; }
    var cons = area / (width * eff) * (1 + allow),
        cost = cons * price,
        order = cons * qty,
        total = order * price;

    document.getElementById("r-cons").textContent = cons.toFixed(2) + " m";
    document.getElementById("r-cost").textContent = money(cost);
    document.getElementById("r-order").textContent = nf.format(Math.round(order)) + " m";
    document.getElementById("r-total").textContent = money(total);

    var warn = document.getElementById("r-warn");
    if (order > 0 && order < 400) {
      warn.hidden = false;
      warn.textContent = "This order needs " + Math.round(order) + " m of fabric, below the 300-500 m lot minimum most mills set for a specified article. Expect to buy the minimum and carry the balance, or take a stock fabric and accept the shade.";
    } else {
      warn.hidden = true;
    }
  }

  gEl.addEventListener("change", syncArea);
  sEl.addEventListener("change", syncArea);
  ["area","width","eff","allow","price","qty"].forEach(function(id){
    document.getElementById(id).addEventListener("input", function(){
      if (id === "eff" || id === "allow") { calcConsumption(); } else { calcConsumption(); }
    });
  });

  // --- tool 2 -------------------------------------------------------------
  var FACTOR = 33.906;
  var ozEl = document.getElementById("oz"), gsmEl = document.getElementById("gsm");

  function paintClass(oz){
    var rows = document.querySelectorAll("#cls-table tbody tr"), hit = null;
    rows.forEach(function(r){ r.classList.remove("hit"); });
    rows.forEach(function(r){
      var lo = parseFloat(r.getAttribute("data-min")), hi = parseFloat(r.getAttribute("data-max"));
      if (oz >= lo && oz <= hi) { r.classList.add("hit"); hit = r; }
    });
    return hit;
  }

  function fromOz(){
    var oz = parseFloat(ozEl.value);
    if (!isFinite(oz)) { return; }
    gsmEl.value = Math.round(oz * FACTOR);
    paintClass(oz);
  }
  function fromGsm(){
    var g = parseFloat(gsmEl.value);
    if (!isFinite(g)) { return; }
    ozEl.value = (g / FACTOR).toFixed(1);
    paintClass(parseFloat(ozEl.value));
  }
  ozEl.addEventListener("input", fromOz);
  gsmEl.addEventListener("input", fromGsm);

  // --- tool 3 -------------------------------------------------------------
  function calcCarton(){
    var L = num("cl") / 100, W = num("cw") / 100, H = num("ch") / 100,
        pcs = num("pcs"), vol = parseFloat(document.getElementById("cont").value),
        qty = num("qty2"), freight = num("freight");
    var cbm = L * W * H;
    if (cbm <= 0 || pcs <= 0) { return; }
    var perCont = Math.floor((vol * 0.85) / cbm) * pcs,
        cartons = Math.ceil(qty / pcs),
        conts = Math.ceil(cartons / Math.max(1, Math.floor((vol * 0.85) / cbm))),
        fpp = qty > 0 ? (conts * freight) / qty : 0;

    document.getElementById("c-cbm").textContent = cbm.toFixed(4) + " CBM";
    document.getElementById("c-percont").textContent = nf.format(perCont) + " pcs";
    document.getElementById("c-cartons").textContent = nf.format(cartons);
    document.getElementById("c-conts").textContent = conts;
    document.getElementById("c-freight").textContent = money(fpp);
  }

  ["cl","cw","ch","pcs","qty2","freight"].forEach(function(id){
    document.getElementById(id).addEventListener("input", calcCarton);
  });
  document.getElementById("cont").addEventListener("change", calcCarton);

  syncArea();
  fromOz();
  calcCarton();
})();
</script>
</body>
</html>
"""


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


def chrome():
    src = rd(CHROME)
    return (re.search(r'<header class="site-head">.*?</header>', src, re.S).group(0),
            re.search(r'<footer class="site-foot">.*?</footer>', src, re.S).group(0))


def main():
    header, footer = chrome()

    # 1. the tools page
    out = os.path.join(ROOT, "tools", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    wr(out, PAGE.replace("__HEADER__", header).replace("__FOOTER__", footer))
    print("wrote tools/index.html")

    # 2. nav link on every page (after the FAQ link)
    nav_added = 0
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp.replace("\\", "/"):
            continue
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            s = rd(p)
            if 'href="/tools/"' in s:
                continue
            if 'href="/faq/"' not in s:
                continue
            s2 = s.replace('<a href="/faq/">FAQ</a>',
                           '<a href="/faq/">FAQ</a>\n          <a href="/tools/">Tools</a>', 1)
            if s2 != s:
                wr(p, s2)
                nav_added += 1
    print("nav link added on", nav_added, "pages")

    # 3. links from three articles
    link_map = {
        "blog/low-moq-denim-manufacturing-150-pieces/index.html":
            "- [Denim costing toolkit: consumption, oz to gsm, cartons](/tools/)\n",
        "blog/denim-weight-guide/index.html":
            "- [Denim costing toolkit: consumption, oz to gsm, cartons](/tools/)\n",
        "blog/denim-factory-quote-line-items/index.html":
            "- [Denim costing toolkit: consumption, oz to gsm, cartons](/tools/)\n",
    }
    for rel, line in link_map.items():
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            print("  missing:", rel)
            continue
        s = rd(p)
        if 'Denim costing toolkit' in s:
            continue
        # append as a list item inside the "Where to go next" list
        m = re.search(r'(<h2>Where to go next</h2>\s*<p>|<h2>Where to go next</h2>)', s)
        if m:
            # find the list that follows and append at its end
            after = s[m.end():]
            lm = re.search(r'(<ul>)(.*?)(</ul>)', after, re.S)
            if lm:
                pos = m.end() + lm.end(2)
                s = s[:pos] + '\n<li><a href="/tools/">Denim costing toolkit: consumption, oz to gsm, cartons</a></li>' + s[pos:]
                wr(p, s)
                print("  article link added:", rel)
                continue
        print("  could not place link in:", rel)

    # 4. homepage guides footer line
    idx = os.path.join(ROOT, "index.html")
    s = rd(idx)
    if 'href="/tools/"' not in s:
        s = s.replace('<a href="/faq/">Buyer FAQ</a>', '<a href="/tools/">Costing tools</a> &middot; <a href="/faq/">Buyer FAQ</a>', 1)
        wr(idx, s)
        print("homepage: tools link added")

    # 5. sitemap
    sm_path = os.path.join(ROOT, "sitemap.xml")
    sm = rd(sm_path)
    loc = SITE + "/tools/"
    if loc not in sm:
        sm = sm.replace("</urlset>",
                        '  <url><loc>%s</loc><lastmod>2026-11-25</lastmod>'
                        '<changefreq>monthly</changefreq><priority>0.8</priority></url>\n</urlset>' % loc)
        wr(sm_path, sm)
    print("sitemap urls:", sm.count("<loc>"))

    # 6. llms.txt
    llms = os.path.join(ROOT, "llms.txt")
    if os.path.isfile(llms):
        t = rd(llms)
        if "/tools/" not in t:
            t = t.replace("## Blog", "## Tools\n- [Denim costing toolkit](%s/tools/) - fabric consumption and cost, oz to gsm, carton and container loading\n\n## Blog" % SITE)
            if "/tools/" not in t:
                t = t.rstrip() + "\n\n## Tools\n- [Denim costing toolkit](%s/tools/)\n" % SITE
            wr(llms, t)
            print("llms.txt updated")

    # verify
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
