"""MTS Home: the one page that links every MTS artifact, built from artifacts/registry.json.

  python scripts/dev/make_home.py                 # writes MyTradingSys/system/artifacts/mts_home.html
  python scripts/dev/make_home.py --out x.html
  (an ordinary smoke ship: the fast gate runs only the tests its import graph reaches)

Operator 2026-10-16: all artifacts from one place. 2026-11-13 cleanup: Home is only the page list now. Removed as stale or duplicated
elsewhere: Waiting-for-you (decisions are answered in chat, recorded in OPERATOR_DECISIONS.md), Road to profitability (research status),
session recipes and the super-session prompt (ROLES.md, SUPER_SESSION.md), link-fix help (one login owns every page). Each tile shows when its
page was last published in UTC and IST (same clock as the page stamp, af.stamp_text) and a colour: green current, amber behind the repo or
older than 14 days, red behind the repo for 3+ days. Every page enters through registry.json (test_every_published_artifact_is_registered).
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artifacts as af  # noqa: E402

OUT = af.REPO / "MyTradingSys" / "system" / "artifacts" / "mts_home.html"
WRITE_FIRST = ("research_map",)  # pages where Jis writes, shown first
AMBER_DAYS, RED_BEHIND_DAYS = 14, 3  # OURS: age at which a published page turns amber; a page behind its repo this long turns red


def health(behind, age_days):
    """green / amber / red for a page tile: red = behind the repo for RED_BEHIND_DAYS+, amber = behind, unknown or older than AMBER_DAYS, else green."""
    if behind and age_days is not None and age_days >= RED_BEHIND_DAYS:
        return "red"
    return "amber" if behind or age_days is None or age_days > AMBER_DAYS else "green"


def build(reg, now=None, repo=None):
    now = now or datetime.now(timezone.utc)
    home = reg["home_login"]
    pages, retire = [], []
    for pg in reg["pages"]:
        own = af.owner(pg)
        url = pg["urls"].get(own, "")
        if pg["status"] == "retire":
            for a, u in pg["urls"].items():
                if u and a not in (pg.get("deleted") or {}):   # `deleted`: {login: date} the operator removed it there
                    retire.append({"login": a, "title": pg["title"], "url": u})
        if pg["status"] != "canonical" or not url or pg["slug"] == reg["home_slug"]:
            continue
        when = af.published_at(pg)
        age = (now - when).total_seconds() / 86400 if when else None
        behind = (af.behind(reg, pg, repo or af.REPO) if pg.get("html") else False) or bool(af.feed_reasons(pg, now, repo or af.REPO))  # repo html or a feed moved on
        pages.append({"slug": pg["slug"], "title": pg["title"], "url": url, "owner": own, "purpose": pg.get("purpose", ""),
                      "db": bool(pg.get("db")), "write": pg["slug"] in WRITE_FIRST, "behind": behind, "health": health(behind, age),
                      "pub": af.stamp_text(when) if when else "never published", "ageH": round(age * 24) if age is not None else None})
        if pg.get("single_owner"):
            for a, u in pg["urls"].items():
                if u and a != own and a not in (pg.get("deleted") or {}):
                    retire.append({"login": a, "title": pg["title"], "url": u})
    for a, rows in reg.get("unpinned_old", {}).items():
        for r in rows if isinstance(rows, list) else []:
            retire.append({"login": a, "title": r["title"], "url": r["url"]})
    pages.sort(key=lambda p: (not p["write"], WRITE_FIRST.index(p["slug"]) if p["write"] else 0))
    return {"generated": af.stamp_text(now), "home": home, "pages": pages, "retire": retire,
            "counts": {h: sum(p["health"] == h for p in pages) for h in ("green", "amber", "red")}}


TPL = r"""<title>MTS Home</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* One compact screen: a grid of colour-coded page tiles, old copies folded. Tokens are the Research Map's. */
:root{
  --bg:#eef1f4; --surface:#ffffff; --sunk:#f6f8fa; --ink:#14202b; --muted:#566371; --line:#d6dde4;
  --accent:#2f43c4; --accent-soft:#e7eafb; --on-accent:#ffffff;
  --pass:#17734a; --pass-soft:#e2f3ea; --warn:#9a5700; --warn-soft:#fbf0dd; --fail:#b42318; --fail-soft:#fbe7e5;
  --f-display:"Archivo", "Arial Narrow", system-ui, sans-serif;
  --f-body:"Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --f-mono:"JetBrains Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
  --r:10px;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0e1318; --surface:#161d24; --sunk:#121820; --ink:#e4e9ee; --muted:#9aa6b2; --line:#29323c;
  --accent:#93a2ff; --accent-soft:#232a4d; --on-accent:#0e1318;
  --pass:#5fcf95; --pass-soft:#16301f; --warn:#f2b54f; --warn-soft:#382a12; --fail:#ff8a7d; --fail-soft:#3a1a17;
  color-scheme:dark }}
:root[data-theme="dark"]{
  --bg:#0e1318; --surface:#161d24; --sunk:#121820; --ink:#e4e9ee; --muted:#9aa6b2; --line:#29323c;
  --accent:#93a2ff; --accent-soft:#232a4d; --on-accent:#0e1318;
  --pass:#5fcf95; --pass-soft:#16301f; --warn:#f2b54f; --warn-soft:#382a12; --fail:#ff8a7d; --fail-soft:#3a1a17;
  color-scheme:dark }
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:15px/1.5 var(--f-body);margin:0}
.wrap{max-width:980px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:20px 48px;display:grid;gap:18px}
h1,h2{font-family:var(--f-display);font-stretch:88%;text-wrap:balance;margin:0;line-height:1.2}
h1{font-size:1.7rem;font-weight:800;font-stretch:80%}
h2{font-size:1.1rem;font-weight:750}
p{margin:0}
a{color:var(--accent)}
a:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
code{font-family:var(--f-mono);font-size:.84em;overflow-wrap:anywhere}
.sub{color:var(--muted)}
.small{font-size:.86rem}
header{display:flex;flex-wrap:wrap;gap:4px 16px;align-items:baseline;justify-content:space-between}
.stamp{font-family:var(--f-mono);font-size:.72rem;color:var(--muted)}
section{display:grid;gap:8px;min-width:0}
.sechead{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;justify-content:space-between}
.pill{font:700 .68rem var(--f-body);letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:999px;background:var(--sunk);color:var(--muted);border:1px solid var(--line);white-space:nowrap}
.pill.old{background:var(--warn-soft);color:var(--warn);border-color:transparent}
.pill.db{background:var(--accent-soft);color:var(--accent);border-color:transparent}
.pill.green{background:var(--pass-soft);color:var(--pass);border-color:transparent}
.pill.red{background:var(--fail-soft);color:var(--fail);border-color:transparent}
.sum{display:flex;flex-wrap:wrap;gap:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:11px 14px;display:grid;gap:4px;align-content:start;min-width:0;border-left:5px solid var(--line)}
.tile.green{border-left-color:var(--pass)}
.tile.amber{border-left-color:var(--warn)}
.tile.red{border-left-color:var(--fail)}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px;background:var(--line)}
.green .dot{background:var(--pass)} .amber .dot{background:var(--warn)} .red .dot{background:var(--fail)}
.tile a.name{font:750 1.02rem var(--f-display);font-stretch:90%;text-decoration:none;overflow-wrap:anywhere}
.tile a.name:hover{text-decoration:underline}
.tile .why{font-size:.88rem;color:var(--muted)}
.tile .meta{display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center;font:.72rem var(--f-mono);color:var(--muted)}
details.fold{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:0 14px}
details.fold>summary{cursor:pointer;padding:9px 0;font:700 .95rem var(--f-display);font-stretch:92%;list-style:none;display:flex;justify-content:space-between;gap:10px}
details.fold>summary::-webkit-details-marker{display:none}
details.fold>summary::after{content:"Show";font:600 .76rem var(--f-body);color:var(--muted)}
details.fold[open]>summary::after{content:"Hide"}
details.fold .in{padding:0 0 12px;display:grid;gap:8px}
.ritem{display:flex;flex-wrap:wrap;gap:2px 10px;align-items:baseline;font-size:.88rem}
.ritem .url{font:.72rem var(--f-mono);color:var(--muted);overflow-wrap:anywhere}
</style>

<main class="wrap" id="main">
  <header>
    <h1>MTS Home</h1>
    <span class="stamp" id="stamp"></span>
  </header>

  <section aria-labelledby="h-pages">
    <div class="sechead"><h2 id="h-pages">Pages</h2><div class="sum" id="sum"></div></div>
    <p class="sub small">Green: current. Amber: behind the repo or published over 14 days ago. Red: behind the repo for 3+ days. Time shown is the last publish (UTC and IST). "Saves notes": you write there.</p>
    <div class="grid" id="pages"></div>
  </section>

  <details class="fold" id="retirebox"><summary>Old copies to delete (<span id="nretire"></span>)</summary>
    <div class="in small"><p class="sub">Claude cannot delete artifacts: open each on the login named and delete it from the page menu.</p><div id="retire"></div></div></details>

  <p class="sub small">For Claude sessions: this list is built from <code>MyTradingSys/system/artifacts/registry.json</code> (<code>artifacts/README.md</code>). A new page appears here only after it has a registry entry; republish only over its link, never a second copy.</p>
</main>

<script>
const DATA = __DATA__;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]));
const $ = id => document.getElementById(id);
$("stamp").textContent = "Built " + DATA.generated;
const C = DATA.counts;
$("sum").innerHTML = `<span class="pill green">${C.green} current</span><span class="pill old">${C.amber} amber</span><span class="pill red">${C.red} red</span>`;
const ago = h => h == null ? "" : h < 48 ? h + "h ago" : Math.round(h / 24) + "d ago";
$("pages").innerHTML = DATA.pages.map(p => `
  <article class="tile ${p.health}">
    <a class="name" href="${esc(p.url)}" target="_blank" rel="noopener"><span class="dot"></span>${esc(p.title)}</a>
    <span class="why">${esc(p.purpose)}</span>
    <span class="meta">${p.db ? `<span class="pill db">saves notes</span>` : ""}${p.behind ? `<span class="pill old">behind repo</span>` : ""}<span>${esc(p.pub)}</span><span>${ago(p.ageH)}</span></span>
  </article>`).join("");
$("nretire").textContent = DATA.retire.length;
$("retire").innerHTML = DATA.retire.length ? DATA.retire.map(r => `<div class="ritem"><span>${esc(r.login)}</span><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a><span class="url">${esc(r.url)}</span></div>`).join("") : `<p class="sub">Nothing to delete.</p>`;
</script>
"""


def render(data):
    return TPL.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    data = build(af.load())
    out = Path(a.out)
    af.write_stamped(out, render(data))
    print(f"wrote {out} ({len(data['pages'])} pages {data['counts']}, {len(data['retire'])} old copies to delete)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
