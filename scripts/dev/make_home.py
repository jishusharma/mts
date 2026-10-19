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
        if (ans and ans.group(1).strip() not in NO_ANSWER) or '"answer"' in body:
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
            "superPrompt": super_prompt(repo or af.REPO)}


TPL = r"""<title>MTS Home</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: one column like a station departures board. The rule first, then the pages (where you write, then read-only),
   then how to open them from another login, then the stale copies to delete. Tokens are the Research Map's. */
:root{
  --bg:#eef1f4; --surface:#ffffff; --sunk:#f6f8fa; --ink:#14202b; --muted:#566371; --line:#d6dde4;
  --accent:#2f43c4; --accent-soft:#e7eafb; --on-accent:#ffffff;
  --pass:#17734a; --pass-soft:#e2f3ea; --warn:#9a5700; --warn-soft:#fbf0dd; --fail:#b42318; --fail-soft:#fbe7e5;
  --f-display:"Archivo", "Arial Narrow", system-ui, sans-serif;
  --f-body:"Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --f-mono:"JetBrains Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
  --r:12px;
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
html{font-size:106.25%;-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{background:var(--bg);color:var(--ink);font:1rem/1.6 var(--f-body);margin:0}
.wrap{max-width:860px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 72px;display:grid;gap:36px}
h1,h2,h3{font-family:var(--f-display);font-stretch:88%;text-wrap:balance;margin:0;line-height:1.2}
h1{font-size:2rem;font-weight:800;font-stretch:80%}
h2{font-size:1.4rem;font-weight:750}
h3{font-size:1.15rem;font-weight:700}
p{margin:0;max-width:65ch}
a{color:var(--accent)}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
code{font-family:var(--f-mono);font-size:.84em;overflow-wrap:anywhere}
.eyebrow{font:700 .72rem var(--f-body);letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
header{display:grid;gap:10px}
.stamp{font-family:var(--f-mono);font-size:.75rem;color:var(--muted)}
.rule{background:var(--accent-soft);border:1px solid color-mix(in srgb,var(--accent) 40%,transparent);border-radius:var(--r);padding:20px 22px;display:grid;gap:10px}
.rule p{font-size:1.12rem;line-height:1.55}
.who{font-size:.95rem;color:var(--muted)}
.who b{color:var(--ink)}
section{display:grid;gap:16px}
.sub{color:var(--muted)}
.list{display:grid;gap:14px}
.page{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:18px 20px;display:grid;gap:10px;border-left:6px solid var(--tone,var(--line))}
.page.w{--tone:var(--accent)}
.ptop{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:baseline;justify-content:space-between}
.ptitle{font:750 1.2rem var(--f-display);font-stretch:90%;text-decoration:none}
.ptitle:hover{text-decoration:underline}
.pills{display:flex;flex-wrap:wrap;gap:6px}
.pill{font:700 .72rem var(--f-body);letter-spacing:.06em;text-transform:uppercase;padding:3px 10px;border-radius:999px;background:var(--sunk);color:var(--muted);border:1px solid var(--line);white-space:nowrap}
.pill.home{background:var(--accent-soft);color:var(--accent);border-color:transparent}
.pill.db{background:var(--pass-soft);color:var(--pass);border-color:transparent}
.pill.old{background:var(--warn-soft);color:var(--warn);border-color:transparent}
.kv{display:grid;grid-template-columns:7.5em minmax(0,1fr);gap:6px 14px;margin:0;font-size:.98rem}
.kv dt{font:700 .72rem var(--f-body);letter-spacing:.07em;text-transform:uppercase;color:var(--muted);padding-top:.35em}
.kv dd{margin:0;min-width:0;overflow-wrap:anywhere}
.url{font-family:var(--f-mono);font-size:.78rem;color:var(--muted);overflow-wrap:anywhere}
.box{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:20px 22px;display:grid;gap:14px}
ol.steps{margin:0;padding-left:1.4em;display:grid;gap:12px;max-width:65ch}
ol.steps li::marker{font-weight:700;color:var(--accent)}
.cases{display:grid;gap:0;border:1px solid var(--line);border-radius:10px;overflow:hidden}
.cases>div{display:grid;grid-template-columns:minmax(0,13em) minmax(0,1fr);gap:4px 18px;padding:14px 16px;border-bottom:1px solid var(--line)}
.cases>div:last-child{border-bottom:0}
.cases b{font-family:var(--f-display);font-stretch:92%}
.share{display:grid;gap:10px}
.share>div{background:var(--sunk);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:grid;gap:4px}
.rgroup{display:grid;gap:10px}
.ritem{display:grid;gap:2px;padding:12px 16px;background:var(--surface);border:1px solid var(--line);border-radius:10px}
.ritem .rt{font-weight:700}
.ritem .rw{font-size:.92rem;color:var(--muted)}
.wait{background:var(--surface);border:1px solid var(--line);border-left:6px solid var(--warn);border-radius:var(--r);padding:16px 20px;display:grid;gap:8px}
.wait .wq{font-weight:700;font-size:1.05rem}
.wait .wr{font-size:.95rem}
.wait .wr b{font:700 .72rem var(--f-body);letter-spacing:.07em;text-transform:uppercase;color:var(--muted);margin-right:6px}
.wmeta{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.where{background:var(--warn-soft);border-radius:var(--r);padding:16px 20px;display:grid;gap:8px}
.use{background:var(--surface);border:1px solid var(--line);border-top:6px solid var(--accent);border-radius:var(--r);padding:20px 22px;display:grid;gap:16px}
.today{font-size:1.08rem;line-height:1.55}
.recipes{margin:0;padding:0;list-style:none;display:grid;gap:12px;counter-reset:r}
.recipes>li{counter-increment:r;background:var(--sunk);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:grid;gap:6px}
.recipes>li>b{font:750 1.08rem var(--f-display);font-stretch:90%}
.recipes>li>b::before{content:counter(r) ". ";color:var(--accent)}
.recipes .when{font-size:.95rem;color:var(--muted)}
.paste{font-family:var(--f-mono);font-size:.86rem;background:var(--accent-soft);color:var(--ink);border-radius:6px;padding:2px 8px;overflow-wrap:anywhere}
.recipes .get{font-size:.95rem}
.recipes .get::before{content:"You get: ";font-weight:700}
details.prompt summary{cursor:pointer;font-weight:700;color:var(--accent)}
details.prompt pre{margin:8px 0 0;padding:12px;background:var(--surface);border:1px solid var(--line);border-radius:8px;font:.78rem/1.5 var(--f-mono);white-space:pre-wrap;overflow-wrap:anywhere}
button.copy{font:700 .8rem var(--f-body);padding:6px 12px;border-radius:999px;border:1px solid var(--accent);background:var(--accent);color:var(--on-accent);cursor:pointer;justify-self:start}
.foot{border-top:1px solid var(--line);padding-top:20px;color:var(--muted);font-size:.92rem;display:grid;gap:8px}
@media (max-width:560px){
  h1{font-size:1.7rem}
  .page,.box,.rule,.use{padding:16px}
  .kv{grid-template-columns:minmax(0,1fr);gap:0}
  .kv dd{margin-bottom:8px}
  .cases>div{grid-template-columns:minmax(0,1fr)}
}
</style>

<main class="wrap">
  <header>
    <span class="eyebrow">MyTradingSys</span>
    <h1>MTS Home</h1>
    <p class="sub">Every MTS page in one list. Bookmark or pin this page on each login you use.</p>
    <span class="stamp" id="stamp"></span>
  </header>

  <section aria-labelledby="h-use">
    <h2 id="h-use">How to use MTS</h2>
    <div class="use">
      <p class="today"><b>What do I do today?</b> Answer anything under <a href="#h-wait">Waiting for you</a>. Send chart screenshots to Eagle_Eyes. A backlog idea: paste <code>You are Admin_Guy.</code> plus the idea (recipe 6). If any login's meter says SPEND (Pipeliner shows all of them), start one super session (recipe 3). That is all: nothing runs by itself.</p>
      <p class="sub">Open a new session in the Claude Code app (model Sonnet), paste the line, add your words. Any role starts on any machine and any login; the "where" below is only what the role needs. The first reply must start with <code>ROLE LOADED</code>; if it does not, close that session and open a new one.</p>
      <ol class="recipes">
        <li><b>Ask a question or make a decision</b>
          <span class="when">Any time, any machine, any login.</span>
          <span>Paste <span class="paste">You are Admin_Guy.</span> then your question (Haiku, high effort; it records your words and passes judgement on as a card).</span>
          <span class="get">the answer from the repo, your decision written to the record, and what still waits on you.</span></li>
        <li><b>Read a chart screenshot</b>
          <span class="when">During market hours. On JIS-NB it reads the live files; on any other device it reads a copy marked <code>mirror@time</code> and says so.</span>
          <span>Paste <span class="paste">You are Eagle_Eyes.</span> then the screenshot.</span>
          <span class="get">a logged read against the engine, tagged NOTE or LAB-VERIFY, and a one-line flag if live money looks wrong.</span></li>
        <li><b>Spend spare budget: one super session</b>
          <span class="when">When the weekly meter says SPEND. Read the weekly bar in the Claude app's usage view (or ask any session for <code>get_usage</code>): SPEND = the weekly % used is 10+ points below the share of the week already gone (e.g. 40% used on day 4 of 7, 57% gone), or under 85% with less than a day to the reset. Any device and any login with budget works; ask <code>Start the Pipeliner.</code> in any session for the SPEND state of every login.</span>
          <span>Paste the line below with your login letter and tasks. It starts the Supervisor, which runs the Session_Planner and up to 4 workers itself: do not open those by hand.</span>
          <span class="get">hours of work on your goal, each ship checked on the trunk, and one line at the end.</span>
          <details class="prompt"><summary>Show the super-session prompt</summary><pre id="sprompt"></pre></details>
          <button class="copy" id="scopy" type="button">Copy the prompt</button></li>
        <li><b>Health check</b>
          <span class="when">Usually weekly, or when something feels off. Any machine; at most one a day.</span>
          <span>Paste <span class="paste">You are MTS_Doctor.</span></span>
          <span class="get">a dated report and one task card per defect.</span></li>
        <li><b>Lab work and routing</b>
          <span class="when">Lab_Guy: on JIS-NUC (the lab: GPT/Codex, Gemini) or over its SSH gate. Pipeliner: anywhere.</span>
          <span>Paste <span class="paste">You are Lab_Guy.</span> to review lab work, or <span class="paste">You are Pipeliner.</span> (on any device) to drain the desk queue and allocate every machine and login (one at a time; a second is refused). Inside any open session, not an Agent: <span class="paste">Start the Pipeliner.</span></span>
          <span class="get">a flow table or a drain table, and cards for what is wrong.</span></li>
        <li><b>Put an idea on the backlog</b>
          <span class="when">Any time, any device, any login.</span>
          <span>Paste <span class="paste">You are Admin_Guy.</span> followed by the idea, in a new session or an open Admin_Guy session.</span>
          <span class="get">one scoped card on the trunk with your words quoted, routed by Pipeliner and refined by Session_Planner.</span></li>
        <li><b>Only when something breaks</b>
          <span class="when">A page is stale or a link fails: on the jishusharma1985 login. A console window flashes or the network misbehaves: on that machine.</span>
          <span>Paste <span class="paste">You are 1985Artifacts_Guy.</span> or <span class="paste">You are Admin_Guy.</span> (old names Artifacts_Guy, Q&amp;A_Helper, Network_Admin_Guy still work)</span>
          <span class="get">a republished page, or a tested fix card (the live tree still changes only by a manual deploy).</span></li>
      </ol>
    </div>
  </section>

  <div class="rule" role="note">
    <span class="eyebrow">The one rule</span>
    <p id="rule"></p>
    <p class="who" id="who"></p>
  </div>

  <section aria-labelledby="h-how">
    <h2 id="h-how">Link fails? Why, and the one-time fix</h2>
    <div class="box">
      <p class="sub" id="whyfail"></p>
      <ol class="steps" id="steps"></ol>
      <h3>Do this once per login that owns pages</h3>
      <div class="share" id="share"></div>
    </div>
    <div class="box">
      <h3>What you see on the wrong login</h3>
      <div class="cases" id="cases"></div>
    </div>
  </section>

  <section aria-labelledby="h-wait">
    <h2 id="h-wait">Waiting for you</h2>
    <div class="where" id="where"></div>
    <div class="list" id="wait"></div>
  </section>

  <section aria-labelledby="h-pages">
    <h2 id="h-pages">Your pages</h2>
    <p class="sub">Blue edge: pages where you write. Each page exists once, at one link, so your notes land in the same place from any login.</p>
    <div class="list" id="pages"></div>
  </section>


  <section aria-labelledby="h-retire">
    <h2 id="h-retire">Old copies to delete</h2>
    <p class="sub">They are not updated and only cause confusion. Claude cannot delete artifacts: open each one on the login named and delete it from the page menu.</p>
    <div id="retire"></div>
  </section>

  <footer class="foot">
    <p><b>For Claude sessions:</b> the list comes from <code>MyTradingSys/system/artifacts/registry.json</code> (rules: <code>artifacts/README.md</code>, section "Which login, which page"). Republish a page only over its link, with the Artifact tool's <code>url</code>, and only from the owner login or a login with edit access. Never publish a second copy.</p>
  </footer>
</main>

<script>
const DATA = __DATA__;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]));
const $ = id => document.getElementById(id);
function ago(d){
  const t = Date.parse(d); if (isNaN(t)) return d || "unknown";
  const n = Math.floor((Date.now() - t) / 864e5);
  return d + (n <= 0 ? " (today)" : n === 1 ? " (yesterday)" : ` (${n} days ago)`);
}
$("stamp").textContent = "List built " + DATA.generated + " from registry.json";
$("sprompt").textContent = DATA.superPrompt || "Missing: see SUPER_SESSION.md, section \"Prompt: start a super session\".";
$("scopy").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(DATA.superPrompt || ""); $("scopy").textContent = "Copied"; }
  catch (e) { $("scopy").textContent = "Copy blocked: open the prompt and select it"; }
});
const others = DATA.logins.filter(a => a !== DATA.home);
$("rule").innerHTML = `Open every page from here. <b>${esc(DATA.home)}</b> is the home login: it owns this page, the Research Map and the Session Planner. `
  + `Your other logins (${others.map(esc).join(", ")}) open the <b>same links</b> once each page is shared with them. Never make a copy.`;
$("pages").innerHTML = DATA.pages.map(p => `
  <article class="page${p.write ? " w" : ""}">
    <div class="ptop">
      <a class="ptitle" href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.title)}</a>
      <span class="pills"><span class="pill${p.owner === DATA.home ? " home" : ""}">Owner ${esc(p.owner)}</span>${p.db ? `<span class="pill db">Saves your notes</span>` : ""}${p.behind ? `<span class="pill old">behind repo</span>` : ""}${p.owner !== DATA.home ? `<span class="pill old">Opens on ${esc(DATA.home)} only after ${esc(p.owner)} shares it</span>` : ""}</span>
    </div>
    <p>${esc(p.purpose)}</p>
    <dl class="kv">
      <dt>Your notes</dt><dd>${esc(p.notes)}</dd>
      <dt>Published</dt><dd>${esc(ago(p.pub))}${p.behind ? " - behind repo: the repo has a newer version, not yet published" : ""}; ${esc(p.refresh)}</dd>
    </dl>
    <span class="url">${esc(p.url)}</span>
  </article>`).join("");
$("whyfail").innerHTML = `claude.ai pages are private to the login that owns them. A link here to a page owned by another login fails (claude.ai says "not found") until that owner shares it with the login you are on. No page, Claude session or pin can change that: only the owner's <b>Share</b> does, once per page. After that every link works from every login.`;
$("steps").innerHTML = [
  `Any login works. Use <b>${esc(DATA.home)}</b> when you can: it owns this page and runs the super sessions.`,
  `Each page is owned by one login (the "Owner" tag above). Once per page, on that owner login: open the page, choose <b>Share</b>, invite the email of each other login you use, and give it <b>edit</b> access. Edit is what lets your notes save from that login and lets Claude sessions there update the same page instead of making a copy.`,
  `On each other login, accept the invitation once (look in claude.ai and in that login's email inbox). From then on the links here open on that login too.`,
  `Pin this page on every login. Pins are per login; the pages themselves are not copied.`
].map(s => `<li>${s}</li>`).join("");
$("share").innerHTML = DATA.share.map(s => `<div><b>On ${esc(s.owner)}</b><span>Share ${s.titles.map(esc).join(", ")} with ${s.invite.map(esc).join(" and ")} (edit access).</span></div>`).join("");
$("cases").innerHTML = [
  ["Not shared yet", "claude.ai says the artifact was not found, or asks for access. Nothing is wrong with the page: do the Share step above on the owner login."],
  ["Shared, read-only", "You see the page, but notes and answers do not save. Change that login's access to edit on the owner login."],
  ["Shared with edit", "Same page, same notes, same updates as on the owner login. This is the normal case."],
  ["An old copy", "A page titled \"This page moved\" or an older version. It is frozen: open MTS Home instead, and delete the copy (list below)."],
  ["A Claude session there", "It can update a page only if that login has edit access. Without it the session leaves the page alone and says so; it never publishes a second copy."]
].map(([a, b]) => `<div><b>${esc(a)}</b><span>${esc(b)}</span></div>`).join("");
const byLogin = {};
DATA.retire.forEach(r => (byLogin[r.login] = byLogin[r.login] || []).push(r));
$("retire").innerHTML = Object.keys(byLogin).length ? Object.entries(byLogin).map(([l, rows]) => `
  <div class="rgroup"><h3>On ${esc(l)} <span class="pill old">${rows.length} to delete</span></h3>
  ${rows.map(r => `<div class="ritem"><a class="rt" href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a><span class="rw">${esc(r.why)}</span><span class="url">${esc(r.url)}</span></div>`).join("")}</div>`).join("")
  : `<p class="sub">Nothing to delete.</p>`;
const A = DATA.answerAt;
$("where").innerHTML = (A ? `<p><b>Answer in the ${esc(A.title)}</b>: <a href="${esc(A.url)}" target="_blank" rel="noopener">${esc(A.url)}</a>, Decisions tab (pick an option, add a note). It is owned by <b>${esc(A.owner)}</b>: it opens on that login, or on another login once ${esc(A.owner)} has shared it with edit access. It is the one place answers are stored.</p>` : "")
  + `<p class="sub">Cannot open it on the login you are on? Tell any Claude session the id and your answer (for example "${esc((DATA.waiting[0] || {id: "q-id"}).id)}: yes"); it writes your words to the repo record, and the next Control Room pickup applies them.</p>`
  + `<p class="sub">This list is the repo record at build time (${esc(DATA.generated)}). An answer you gave on the page in the last hours shows here until a pickup copies it in.</p>`;
$("wait").innerHTML = DATA.waiting.length ? DATA.waiting.map(w => `
  <article class="wait">
    <div class="wmeta"><span class="pill">${esc(w.id)}</span>${w.topic ? `<span class="pill">${esc(w.topic)}</span>` : ""}${w.explicit ? `<span class="pill old">Needs your answer, no default</span>` : ""}<span class="url">asked ${esc(w.asked)}</span></div>
    <p class="wq">${esc(w.title)}</p>
    ${w.recommended ? `<p class="wr"><b>Recommended</b>${esc(w.recommended)}</p>` : ""}
  </article>`).join("") : `<p class="sub">Nothing is waiting for you.</p>`;
$("who").textContent = "";
(async () => {
  try {
    const user = window.claude && await window.claude.use("user");
    if (!user) return;
    $("who").innerHTML = user.isOwner()
      ? `You are on <b>${esc(DATA.home)}</b>, the home login.`
      : `You opened this from another login. That is fine: the links below open the same pages, as long as each is shared with this login.`;
  } catch (e) { /* the page reads the same without it */ }
})();
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
