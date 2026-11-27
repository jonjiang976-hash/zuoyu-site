# -*- coding: utf-8 -*-
"""
Make the size finder visibly react when the category changes.

Reported problem: switching Women -> Men changed only the small "Match" line; the
tables below did not move, so it looked broken.

Fix:
  * choosing a category now hides the other tables and highlights the chosen one
  * a "Show all tables" button returns to the full view
  * the match line is larger and no longer repeats the header ("W size W28")
  * the chosen table scrolls into view
  * with JavaScript disabled, every table is still visible (no content hidden for crawlers)
"""
import io
import json
import os
import re
import sys

ROOT = os.getcwd()
PAGES = [
    os.path.join(ROOT, "tools", "index.html"),
    os.path.join(ROOT, "tools", "denim-size-chart", "index.html"),
]

CSS = """  .size-table{transition:opacity .15s}
  .size-table.is-hidden{display:none}
  .size-table.is-active{outline:2px solid #12283f;outline-offset:6px;border-radius:2px}
  #sz-match{font-size:1.02rem;line-height:1.5}
  #sz-showall{margin:.6rem 0 .2rem;padding:.45rem .9rem;border:1px solid #cfcfc7;background:#fff;border-radius:4px;font:inherit;font-size:.85rem;cursor:pointer}
  #sz-showall:hover{background:var(--canvas-2)}
"""

BUTTON = '      <button id="sz-showall" type="button">Show all tables</button>\n'

NEW_JS = """<script>
(function(){
  "use strict";
  var cat = document.getElementById("sz-cat"),
      q = document.getElementById("sz-q"),
      matchEl = document.getElementById("sz-match"),
      showAll = document.getElementById("sz-showall");
  if (!cat || !q) { return; }

  var tables = Array.prototype.slice.call(document.querySelectorAll("table.size-table"));
  var KEYWORDS = {topsw:"Women tops", trouserw:"Women trousers", shortsw:"Women shorts",
                  skirtw:"Women skirts", topsm:"Men tops", denimm:"Men jeans"};

  function tableFor(id){ return document.getElementById("tbl-" + id); }

  function showOnly(id){
    tables.forEach(function(t){
      t.classList.remove("is-active");
      if (t.id === "tbl-" + id) { t.classList.remove("is-hidden"); }
      else { t.classList.add("is-hidden"); }
      var wrap = t.parentElement;
      if (wrap && wrap.classList.contains("table-scroll")) {
        wrap.style.display = (t.id === "tbl-" + id) ? "" : "none";
      }
    });
    var t = tableFor(id);
    if (t) {
      t.classList.add("is-active");
      var box = (t.parentElement && t.parentElement.classList.contains("table-scroll")) ? t.parentElement : t;
      var y = box.getBoundingClientRect().top + window.pageYOffset - 90;
      window.scrollTo({top: y, behavior: "smooth"});
    }
  }

  function showEveryTable(){
    tables.forEach(function(t){ t.classList.remove("is-hidden"); t.classList.remove("is-active"); });
    Array.prototype.forEach.call(document.querySelectorAll(".table-scroll"), function(w){ w.style.display = ""; });
  }

  function run(){
    var id = cat.value, table = tableFor(id);
    if (!table) { return; }
    Array.prototype.forEach.call(table.querySelectorAll("tbody tr"), function(tr){ tr.classList.remove("hit"); });

    var v = q.value.trim().toUpperCase().replace(/^W/, "").replace(/\\s+/g, "");
    if (!v) {
      matchEl.textContent = "Type a size to see the full conversion, or scroll to the " + (KEYWORDS[id] || "") + " table.";
      showOnly(id);
      return;
    }
    var hit = null;
    Array.prototype.forEach.call(table.querySelectorAll("tbody tr"), function(tr){
      if (hit) { return; }
      ["eu","us","uk","jp","letter","w"].forEach(function(k){
        if (hit) { return; }
        var dv = tr.getAttribute("data-" + k);
        if (dv && dv.toUpperCase() === v) { hit = tr; }
      });
    });
    if (!hit) {
      matchEl.textContent = "No " + v + " in the " + (KEYWORDS[id] || "chosen") + " table - try another category or another size system.";
      showOnly(id);
      return;
    }
    hit.classList.add("hit");
    var head = Array.prototype.map.call(table.querySelectorAll("tbody tr:first-child th"), function(c){ return c.textContent.trim(); });
    var cells = Array.prototype.map.call(hit.children, function(c){ return c.textContent.trim(); });
    var pairs = [];
    for (var i = 0; i < cells.length && i < head.length; i++) {
      if (!cells[i]) { continue; }
      pairs.push((head[i] === "W size" ? "" : head[i] + " ") + cells[i]);
    }
    matchEl.textContent = pairs.join("  \\u00b7  ");
    showOnly(id);
  }

  cat.addEventListener("change", run);
  q.addEventListener("input", run);
  if (showAll) {
    showAll.addEventListener("click", function(){
      showEveryTable();
      matchEl.textContent = "\\u2014";
      q.value = "";
    });
  }
})();
</script>
"""


def main():
    total = 0
    for path in PAGES:
        if not os.path.isfile(path):
            print("missing:", os.path.relpath(path, ROOT))
            continue
        s = io.open(path, encoding="utf-8").read()
        orig = s

        # 1. styles
        if ".size-table.is-active" not in s:
            s = s.replace("  .size-table tr.hit{background:#f2f6f8}",
                          "  .size-table tr.hit{background:#f2f6f8}\n" + CSS, 1)

        # 2. show-all button after the finder box
        if 'id="sz-showall"' not in s:
            anchor = '<div id="sz-out" class="out">'
            if anchor in s:
                s = s.replace(anchor, BUTTON + anchor, 1)
            else:
                print("button anchor missing in", os.path.relpath(path, ROOT))

        # 3. replace the old sz- script block
        m = re.search(r'<script>\s*\(function\(\)\{\s*var cat = document\.getElementById\("sz-cat"\).*?</script>',
                      s, re.S)
        if m:
            s = s[:m.start()] + NEW_JS + s[m.end():]
        else:
            print("old sz script not found in", os.path.relpath(path, ROOT))

        if s != orig:
            io.open(path, "w", encoding="utf-8", newline="\n").write(s)
            total += 1
            print("patched:", os.path.relpath(path, ROOT), "| bytes:", len(s))
        else:
            print("unchanged:", os.path.relpath(path, ROOT))

    print("pages patched:", total)

    # json-ld sanity
    bad = []
    for p in PAGES:
        if not os.path.isfile(p):
            continue
        for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                              io.open(p, encoding="utf-8").read(), re.S):
            try:
                json.loads(blk)
            except Exception as exc:                            # noqa: BLE001
                bad.append(str(exc)[:50])
    print("invalid JSON-LD:", bad if bad else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
