"""MTS Home: the one page that links every MTS artifact, built from artifacts/registry.json.

  python scripts/dev/make_home.py                 # writes MyTradingSys/system/artifacts/mts_home.html
  python scripts/dev/make_home.py --out x.html
  (an ordinary smoke ship: the fast gate runs only the tests its import graph reaches)

Operator 2026-10-16: "all my artifacts available from one place, and how to access them explained". Each row says what the page is for,
which login owns it, where notes go and when it was last published; a box says how to open the pages from any login; a list names the
stale copies only Jis can delete. Operator 2026-10-17: "all my questions and the decisions waiting for me available there":
a "Waiting for you" list reads the open questions from the repo record (OPERATOR_DECISIONS.md: no answer yet; task cards: `asks`
set, not done) and says where to answer them (the Control Room, the one place for answers, q1/q21). Publish: Artifact tool, url = registry urls[home_login] of mts_home (never a second copy).
Operator 2026-10-19: "How to use MTS" at the top: seven recipes (when, where, the line to paste, what comes back) and the super-session
prompt, read from SUPER_SESSION.md at build time so the page never drifts from the doc.
Operator 2026-10-25: too big, duplicates, too much scrolling: compact page (needs-you strip, page tiles, one row per session role,
everything rare folded). Every page enters through registry.json (test_every_published_artifact_is_registered keeps it honest).
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artifacts as af  # noqa: E402

OUT = af.REPO / "MyTradingSys" / "system" / "artifacts" / "mts_home.html"
WRITE_FIRST = ("research_map", "mts_control_room", "session_planner")  # pages where Jis writes, shown first
DECISIONS = "MyTradingSys/system/OPERATOR_DECISIONS.md"
TASKS = "MyTradingSys/system/tasks"
NO_ANSWER = ("", "(none yet)")
SUPER = "MyTradingSys/system/SUPER_SESSION.md"
SUPER_HEAD = "## Prompt: start a super session"


def super_prompt(repo):
    """The fenced prompt under SUPER_HEAD in SUPER_SESSION.md, or "" when the file or the block is missing."""
    f = Path(repo) / SUPER
    text = f.read_text(encoding="utf-8") if f.is_file() else ""
    m = re.search(re.escape(SUPER_HEAD) + r"[^\n]*\n```[^\n]*\n(.*?)\n```", text, re.S)
    return m.group(1).strip() if m else ""


def waiting(repo):
    """Open questions for Jis: decisions in OPERATOR_DECISIONS.md with no answer, and task cards parked on an `asks` question."""
    repo, out = Path(repo), []
    dec = repo / DECISIONS
    text = dec.read_text(encoding="utf-8") if dec.is_file() else ""
    for sec in re.split(r"(?m)^## ", text)[1:]:
        head, _, body = sec.partition("\n")
        ans = re.search(r"(?m)^Answer: *(.*)$", body)
        if (ans and ans.group(1).strip() not in NO_ANSWER) or '"answer"' in body or '"status": "DECIDED"' in body:
            continue
        parts = [x.strip() for x in head.split("|")]
        title = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
        rec = re.search(r"(?m)^Recommended: *(.*)$", body)
        out.append({"id": parts[0], "kind": "decision", "title": title, "recommended": rec.group(1).strip() if rec else "",
                    "asked": parts[1].replace("asked", "").strip() if len(parts) > 1 else "",
                    "topic": parts[2] if len(parts) > 2 else "", "explicit": "NO AUTO-APPLY" in head})
    tdir = repo / TASKS
    for f in sorted(tdir.glob("*.json")) if tdir.is_dir() else []:
        try:
            c = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if c.get("asks") and c.get("state") not in ("done", "dropped"):
            out.append({"id": c.get("id", f.stem), "kind": "task", "title": c["asks"], "recommended": "",
                        "asked": str(c.get("created", ""))[:10], "topic": c.get("title", ""), "explicit": True})
    return out


RECIPES = [  # (name, when, line to paste, what comes back); the Lead covers question, decision and backlog idea in one row
    ("Ask, decide, add to backlog", "Any time, any machine or login.", "You are Lead.",
     "then your words (say think / pipeline / doctor / a decision): the answer from the repo, your decision recorded, or one scoped backlog card."),
    ("Read a chart screenshot", "Market hours; JIS-NB reads live files, other devices a mirror copy.", "You are Eagle_Eyes.",
     "then the screenshot: a logged read against the engine and a flag if live money looks wrong."),
    ("Spend spare budget", "Weekly meter says SPEND (used 10+ points below the share of week gone).", "You are Lead. Run pipeline mode.",
     "shows every login's state; then paste the super-session prompt below with your login letter and tasks."),
    ("Health check", "About weekly, or when something feels off.", "You are Lead. Run doctor mode.", "a dated report and one task card per defect."),
    ("Lab work and routing", "Lab_Guy on JIS-NUC; the Lead's pipeline mode anywhere.", "You are Lab_Guy.",
     "or the Lead in pipeline mode: a flow table or desk-queue drain table, cards for what is wrong."),
    ("Think: design, optimise, economise", "When a process feels heavy.", "You are Lead. Run think mode.",
     "then a topic: scan waste, budget, automation, tests, scale, speed, ideas, cut."),
    ("A page or link is wrong", "On the jishusharma1985 login.", "You are 1985Artifacts_Guy.", "a republished page or a fix card."),
]


def build(reg, now=None, repo=None):
    now = now or datetime.now(timezone.utc)
    home = reg["home_login"]
    pages, retire = [], []
    for pg in reg["pages"]:
        own = af.owner(pg)
        url = pg["urls"].get(own, "")
        if pg["status"] != "canonical" or not url or pg["slug"] == reg["home_slug"]:
            continue
        pages.append({"slug": pg["slug"], "title": pg["title"], "url": url, "owner": own, "purpose": pg.get("purpose", ""),
                      "notes": pg.get("notes_go_to", ""), "db": bool(pg.get("db")), "refresh": pg["refresh"],
                      "pub": str(pg["last_published"].get(own, ""))[:10], "write": pg["slug"] in WRITE_FIRST,
                      "behind": af.behind(reg, pg, repo or af.REPO) if pg.get("html") else False})
        if pg.get("single_owner"):
            for a, u in pg["urls"].items():
                if u and a != own:
                    retire.append({"login": a, "title": pg["title"], "url": u,
                                   "why": f"old copy or 'moved' page; the live one is on {own}"})
    for a, rows in reg.get("unpinned_old", {}).items():
        for r in rows if isinstance(rows, list) else []:
            retire.append({"login": a, "title": r["title"], "url": r["url"], "why": "old, unpinned, not updated since 5-6 Oct (Control Room q7)"})
    pages.sort(key=lambda p: (not p["write"], WRITE_FIRST.index(p["slug"]) if p["write"] else 0))
    owners = sorted({p["owner"] for p in pages} | {home})
    share = [{"owner": o, "titles": [p["title"] for p in pages if p["owner"] == o] + (["MTS Home"] if o == home else []),
              "invite": [a for a in reg["accounts"] if a != o]} for o in owners]
    cr = next((pg for pg in reg["pages"] if pg["slug"] == "mts_control_room"), None)
    answer = {"title": cr["title"], "url": cr["urls"].get(af.owner(cr), ""), "owner": af.owner(cr)} if cr else None
    return {"generated": now.strftime("%Y-%m-%d %H:%M UTC"), "home": home, "homeUrl": af.home_url(reg), "pages": pages,
            "retire": retire, "share": share, "logins": list(reg["accounts"]), "waiting": waiting(repo or af.REPO), "answerAt": answer,
            "superPrompt": super_prompt(repo or af.REPO),
            "recipes": [dict(zip(("name", "when", "line", "get"), r)) for r in RECIPES]}


TPL = r"""<title>MTS Home</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: one compact screen. Needs-you strip, a grid of page tiles, one row per session role; everything rare is folded.
   Operator 2026-10-25: "more compact, little scroll, intuitive". Tokens are the Research Map's. */
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
h1,h2,h3{font-family:var(--f-display);font-stretch:88%;text-wrap:balance;margin:0;line-height:1.2}
h1{font-size:1.7rem;font-weight:800;font-stretch:80%}
h2{font-size:1.1rem;font-weight:750}
p{margin:0}
a{color:var(--accent)}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
code{font-family:var(--f-mono);font-size:.84em;overflow-wrap:anywhere}
.sub{color:var(--muted)}
.small{font-size:.86rem}
header{display:flex;flex-wrap:wrap;gap:4px 16px;align-items:baseline;justify-content:space-between}
.stamp{font-family:var(--f-mono);font-size:.72rem;color:var(--muted)}
section{display:grid;gap:8px;min-width:0}
.sechead{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;justify-content:space-between}
.pill{font:700 .68rem var(--f-body);letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:999px;background:var(--sunk);color:var(--muted);border:1px solid var(--line);white-space:nowrap}
.pill.old{background:var(--warn-soft);color:var(--warn);border-color:transparent}
.pill.db{background:var(--pass-soft);color:var(--pass);border-color:transparent}
.need{background:var(--surface);border:1px solid var(--line);border-left:6px solid var(--warn);border-radius:var(--r);padding:12px 16px;display:grid;gap:6px}
.need.none{border-left-color:var(--pass)}
.q{display:grid;grid-template-columns:auto minmax(0,1fr);gap:2px 10px;align-items:baseline}
.q .id{font:600 .74rem var(--f-mono);color:var(--muted)}
.q .t{overflow-wrap:anywhere;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:11px 14px;display:grid;gap:4px;align-content:start;min-width:0;border-left:5px solid var(--line)}
.tile.w{border-left-color:var(--accent)}
.tile a.name{font:750 1.02rem var(--f-display);font-stretch:90%;text-decoration:none;overflow-wrap:anywhere}
.tile a.name:hover{text-decoration:underline}
.tile .why{font-size:.88rem;color:var(--muted)}
.tile .meta{display:flex;flex-wrap:wrap;gap:4px 6px;align-items:center;font-size:.76rem;color:var(--muted)}
.rows{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.row{display:grid;grid-template-columns:minmax(0,15em) minmax(0,1fr) auto;gap:2px 14px;align-items:center;padding:8px 14px;border-bottom:1px solid var(--line)}
.row:last-child{border-bottom:0}
.row b{font-family:var(--f-display);font-stretch:92%}
.row .when{font-size:.86rem;color:var(--muted);min-width:0}
.row .get{grid-column:1/-1;font-size:.86rem;color:var(--muted)}
.paste{font-family:var(--f-mono);font-size:.8rem;background:var(--accent-soft);color:var(--ink);border-radius:6px;padding:2px 8px;overflow-wrap:anywhere}
button.copy{font:700 .76rem var(--f-body);padding:4px 11px;border-radius:999px;border:1px solid var(--accent);background:var(--accent);color:var(--on-accent);cursor:pointer;white-space:nowrap}
details.fold{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:0 14px}
details.fold>summary{cursor:pointer;padding:9px 0;font:700 .95rem var(--f-display);font-stretch:92%;list-style:none;display:flex;justify-content:space-between;gap:10px}
details.fold>summary::-webkit-details-marker{display:none}
details.fold>summary::after{content:"Show";font:600 .76rem var(--f-body);color:var(--muted)}
details.fold[open]>summary::after{content:"Hide"}
details.fold .in{padding:0 0 12px;display:grid;gap:8px}
details.fold pre{margin:0;padding:10px;background:var(--sunk);border:1px solid var(--line);border-radius:8px;font:.76rem/1.5 var(--f-mono);white-space:pre-wrap;overflow-wrap:anywhere}
.ritem{display:flex;flex-wrap:wrap;gap:2px 10px;align-items:baseline;font-size:.88rem}
.ritem .url{font:.72rem var(--f-mono);color:var(--muted);overflow-wrap:anywhere}
@media (max-width:640px){
  .row{grid-template-columns:minmax(0,1fr) auto}
  .row .when{grid-column:1/-1}
}
</style>

<main class="wrap">
  <header>
    <h1>MTS Home</h1>
    <span class="stamp" id="stamp"></span>
  </header>

  <section aria-labelledby="h-wait">
    <div class="need" id="need"></div>
  </section>

  <section aria-labelledby="h-pages">
    <div class="sechead"><h2 id="h-pages">Pages</h2><span class="sub small">Blue edge: you write there. One link per page, all owned by <b id="homelogin"></b>.</span></div>
    <div class="grid" id="pages"></div>
  </section>

  <section aria-labelledby="h-use">
    <div class="sechead"><h2 id="h-use">Start a session</h2><span class="sub small">New session in the Claude Code app, model Sonnet. The reply must start with <code>ROLE LOADED</code>; if not, close it and open a new one.</span></div>
    <div class="rows" id="recipes"></div>
    <details class="fold" id="superbox"><summary>Super-session prompt (spend spare budget: your login letter and tasks)</summary>
      <div class="in"><pre id="sprompt"></pre><div><button class="copy" id="scopy" type="button">Copy the prompt</button></div></div></details>
  </section>

  <details class="fold" id="linkfix"><summary>A link fails, or you use another login</summary>
    <div class="in small">
      <p id="whyfail"></p>
      <div id="share"></div>
      <p class="sub">Not shared: "not found". Shared read-only: notes do not save. Shared with edit: the normal case. Pin MTS Home on every login.</p>
    </div></details>

  <details class="fold" id="retirebox"><summary>Old copies to delete (<span id="nretire"></span>)</summary>
    <div class="in small"><p class="sub">Claude cannot delete artifacts: open each on the login named and delete it from the page menu.</p><div id="retire"></div></div></details>

  <p class="sub small">For Claude sessions: this list is built from <code>MyTradingSys/system/artifacts/registry.json</code> (<code>artifacts/README.md</code>). A new page appears here only after it has a registry entry; republish only over its link, never a second copy.</p>
</main>

<script>
const DATA = __DATA__;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]));
const $ = id => document.getElementById(id);
const copyText = async (btn, text) => {
  try { await navigator.clipboard.writeText(text); btn.textContent = "Copied"; }
  catch (e) { btn.textContent = "Select it by hand"; }
};
$("stamp").textContent = "Built " + DATA.generated;
$("homelogin").textContent = DATA.home;
const W = DATA.waiting, A = DATA.answerAt;
const ans = A ? `<a href="${esc(A.url)}" target="_blank" rel="noopener">Answer in the ${esc(A.title)}</a>` : "";
const qrow = w => `<div class="q"><span class="id">${esc(w.id)}</span><span class="t">${esc(w.title)}</span></div>`;
$("need").className = "need" + (W.length ? "" : " none");
$("need").innerHTML = W.length
  ? `<div class="sechead"><h2 id="h-wait">${W.length} waiting for you</h2><span class="small">${ans}</span></div>`
    + W.slice(0, 3).map(qrow).join("")
    + (W.length > 3 ? `<details><summary class="small sub" style="cursor:pointer">${W.length - 3} more</summary>${W.slice(3).map(qrow).join("")}</details>` : "")
  : `<div class="sechead"><h2 id="h-wait">Nothing waiting for you</h2><span class="small">${ans}</span></div>`;
$("pages").innerHTML = DATA.pages.map(p => `
  <article class="tile${p.write ? " w" : ""}">
    <a class="name" href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.title)}</a>
    <span class="why">${esc(p.purpose)}</span>
    <span class="meta">${p.db ? `<span class="pill db">saves notes</span>` : ""}${p.behind ? `<span class="pill old">behind repo</span>` : ""}<span>${esc(p.pub)}</span><span>${esc(p.refresh.split(";")[0])}</span></span>
  </article>`).join("");
$("recipes").innerHTML = DATA.recipes.map((r, i) => `
  <div class="row"><b>${esc(r.name)}</b><span class="when">${esc(r.when)}</span><button class="copy" type="button" data-i="${i}">Copy line</button>
    <span class="get"><span class="paste">${esc(r.line)}</span> ${esc(r.get)}</span></div>`).join("");
document.querySelectorAll("#recipes button.copy").forEach(b => b.addEventListener("click", () => copyText(b, DATA.recipes[+b.dataset.i].line)));
$("sprompt").textContent = DATA.superPrompt || "Missing: see SUPER_SESSION.md, section \"Prompt: start a super session\".";
$("scopy").addEventListener("click", () => copyText($("scopy"), DATA.superPrompt || ""));
$("whyfail").innerHTML = `Pages are private to the login that owns them. Every page here is owned by <b>${esc(DATA.home)}</b>; another login opens a link only after the owner shares it (Share, edit access, once per page).`;
$("share").innerHTML = DATA.share.map(s => `<p><b>On ${esc(s.owner)}</b>: share ${s.titles.map(esc).join(", ")} with ${s.invite.map(esc).join(" and ")}.</p>`).join("");
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
    out.write_text(render(data), encoding="utf-8", newline="\n")
    print(f"wrote {out} ({len(data['pages'])} pages, {len(data['waiting'])} questions waiting, {len(data['retire'])} old copies to delete)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
