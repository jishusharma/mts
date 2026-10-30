"""Build the operator's setup-review page from SETUP_REVIEW.md + examples/*.png.

Usage: python make_review_page.py [out.html]   (default: review_page.html next to this file; not committed)
The page is read-only material plus a verdict picker that lives in the viewer's browser only; the operator
says his verdicts in chat, the coordinator writes them into SETUP_REVIEW.md.
"""
import base64, html, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MD = (HERE / "SETUP_REVIEW.md").read_text(encoding="utf-8")
EX = HERE / "examples"
EXJ = json.loads((HERE / "examples.json").read_text(encoding="utf-8")) if (HERE / "examples.json").exists() else []
EXNOTE = {e["id"]: e for e in EXJ}

# ---------- parse ----------
def table_rows(block):
    rows = []
    for ln in block.splitlines():
        if ln.startswith("|") and not re.match(r"^\|\s*-", ln):
            rows.append([c.strip() for c in ln.strip("|").split("|")])
    return rows

ov = re.search(r"## Overview table\n\n(.*?)\n\n", MD, re.S).group(1)
OVERVIEW = table_rows(ov)[1:]
gaps = re.search(r"## Gaps status\n\n.*?\n\n(\|.*?)\n\n---", MD, re.S).group(1)
GAPS = table_rows(gaps)[1:]

SECTIONS = re.findall(r"### ((?:TOM|FAB)-\w+) (.*?) \((Tom|Fabio)\)\n(.*?)(?=\n### |\n---|\Z)", MD, re.S)

def field(body, name):
    m = re.search(r"^- " + re.escape(name) + r":\s*(.*?)(?=^- |\Z)", body, re.S | re.M)
    return m.group(1).strip() if m else ""

def bullets(text):
    return [b.strip() for b in re.findall(r"^\s+- (.*)$", text, re.M)]

def md_inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\b(SOURCED)\b", r'<b class="src">\1</b>', s)
    s = re.sub(r"\b(OURS)\b", r'<b class="ours">\1</b>', s)
    s = re.sub(r"\b(NOT STATED)\b", r'<b class="ns">\1</b>', s)
    return s

def img_tag(sid):
    p = EX / f"{sid}.png"
    if not p.exists():
        note = EXNOTE.get(sid, {}).get("note", "no chart")
        return f'<div class="nochart">No BTC example chart. {html.escape(note)}</div>'
    b64 = base64.b64encode(p.read_bytes()).decode()
    e = EXNOTE.get(sid, {})
    cap = " | ".join(x for x in [e.get("date_utc", ""), e.get("window", ""), e.get("note", "")] if x)
    rule = e.get("selection_rule", "")
    return (f'<figure><img src="data:image/png;base64,{b64}" alt="{sid} BTC example" loading="lazy">'
            f'<figcaption>{html.escape(cap)}<br><span class="ours">OURS</span> picked this day by rule: {html.escape(rule)}</figcaption></figure>')

# ---------- render ----------
def card(sid, name, trader, body):
    see = field(body, "What you see on the chart")
    rule = field(body, "Rule in one breath")
    words = bullets(field(body, "His exact words"))
    btc = field(body, "What BTC can show")
    ev = field(body, "Evidence so far")
    gaps_ = bullets(field(body, "Open gaps"))
    # split the rule on WHEN / THEN / STOP / TARGET for scanning
    parts = re.split(r"\b(WHEN|THEN|STOP|TARGET)\b", rule)
    steps = []
    for i in range(1, len(parts) - 1, 2):
        steps.append((parts[i], parts[i + 1].strip()))
    tail = parts[0].strip() if len(parts) == 1 else ""
    rule_html = "".join(f'<div class="step"><span class="k">{k}</span><span>{md_inline(v)}</span></div>' for k, v in steps)
    if tail:
        rule_html = f"<p>{md_inline(tail)}</p>"
    q = "".join(f"<blockquote>{md_inline(w)}</blockquote>" for w in words)
    g = "".join(f"<li>{md_inline(x)}</li>" for x in gaps_)
    ovrow = next((r for r in OVERVIEW if r[0] == sid), None)
    pill = ovrow[3] if ovrow else ""
    pcls = "yes" if pill.startswith("YES") else "no" if pill.startswith("NO") else "part"
    return f"""
<section class="setup" id="{sid}" data-id="{sid}">
  <header class="sh">
    <div><span class="sid">{sid}</span> <span class="trader {trader.lower()}">{trader}</span></div>
    <h2>{html.escape(name)}</h2>
    <div class="meta"><span class="pill {pcls}">BTC: {html.escape(pill)}</span><span class="pill">his examples: {html.escape(ovrow[4] if ovrow else '')}</span><span class="pill">stop stated: {html.escape(ovrow[5] if ovrow else '')}</span></div>
  </header>
  <div class="grid">
    <div class="txt">
      <h3>What you see</h3><p>{md_inline(see)}</p>
      <h3>Rule in one breath</h3><div class="rule">{rule_html}</div>
      <h3>His words</h3>{q}
      <h3>What BTC can show</h3><p>{md_inline(btc)}</p>
      <h3>Evidence so far</h3><p>{md_inline(ev)}</p>
      <h3>Open gaps</h3><ul>{g}</ul>
    </div>
    <div class="chart">{img_tag(sid)}</div>
  </div>
  <footer class="verdict">
    <span class="vl">Your verdict</span>
    <div class="vb" role="group" aria-label="verdict for {sid}">
      <button type="button" data-v="keep" id="{sid}-keep">keep</button>
      <button type="button" data-v="rewrite" id="{sid}-rewrite">rewrite</button>
      <button type="button" data-v="reject" id="{sid}-reject">reject</button>
    </div>
    <label class="pick"><input type="checkbox" id="{sid}-pick"> test this one first (max 3)</label>
  </footer>
</section>"""

ov_html = "".join(
    f'<tr><td><a href="#{r[0]}">{r[0]}</a></td><td>{html.escape(r[1])}</td><td>{r[2]}</td>'
    f'<td><span class="pill {"yes" if r[3].startswith("YES") else "no" if r[3].startswith("NO") else "part"}">{html.escape(r[3])}</span></td>'
    f'<td>{html.escape(r[4])}</td><td>{html.escape(r[5])}</td><td class="vcell" data-for="{r[0]}">-</td></tr>'
    for r in OVERVIEW)
gaps_html = "".join(f"<tr><td>{md_inline(r[0])}</td><td>{md_inline(r[1])}</td><td>{md_inline(r[2])}</td></tr>" for r in GAPS)
cards = "".join(card(*s) for s in SECTIONS)

PAGE = f"""<title>Tom and Fabio Setup Review</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* layout: one reading column, each setup = text left, chart right; verdict strip under each */
:root {{
  --bg:#f6f4ee; --paper:#fffdf8; --fg:#1d2126; --mute:#5c6470; --line:#d9d4c7;
  --accent:#b4651a; --accent-ink:#fff; --src:#1f6f4a; --ours:#8a4b08; --ns:#8b2d2d;
  --yes:#dff1e4; --part:#fbecc8; --no:#f6d9d9; --tom:#24507a; --fab:#6a3d8f;
  --sans:"IBM Plex Sans",system-ui,sans-serif; --mono:"IBM Plex Mono",ui-monospace,monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#15181c; --paper:#1d2126; --fg:#e8e4da; --mute:#a3a89f; --line:#343a42;
  --accent:#e0893a; --accent-ink:#15181c; --src:#6fcf97; --ours:#f0b06a; --ns:#f08a8a;
  --yes:#1f3b2c; --part:#4a3a14; --no:#4a2222; --tom:#8fb8e8; --fab:#c7a4e8; color-scheme:dark }} }}
:root[data-theme="dark"] {{
  --bg:#15181c; --paper:#1d2126; --fg:#e8e4da; --mute:#a3a89f; --line:#343a42;
  --accent:#e0893a; --accent-ink:#15181c; --src:#6fcf97; --ours:#f0b06a; --ns:#f08a8a;
  --yes:#1f3b2c; --part:#4a3a14; --no:#4a2222; --tom:#8fb8e8; --fab:#c7a4e8; color-scheme:dark }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.5 var(--sans); padding-block:24px 60px;
  padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); }}
.wrap {{ max-width:1180px; margin:0 auto; }}
h1 {{ font-size:1.7rem; font-weight:600; margin:0 0 .3rem; text-wrap:balance; }}
h2 {{ font-size:1.25rem; font-weight:600; margin:.2rem 0 .4rem; text-wrap:balance; }}
h3 {{ font-size:.78rem; text-transform:uppercase; letter-spacing:.06em; color:var(--mute); margin:1rem 0 .25rem; }}
p {{ margin:0 0 .5rem; max-width:68ch; }}
code {{ font-family:var(--mono); font-size:.88em; }}
.intro {{ display:grid; gap:.3rem; max-width:72ch; color:var(--mute); margin-bottom:1.2rem; }}
.intro b {{ color:var(--fg); }}
.sticky {{ position:sticky; top:env(safe-area-inset-top,0px); z-index:5; background:var(--bg); border-bottom:1px solid var(--line); padding:.5rem 0; display:flex; gap:.6rem; flex-wrap:wrap; align-items:center; font-size:.9rem; }}
.sticky .count {{ font-family:var(--mono); }}
button {{ font:inherit; cursor:pointer; border:1px solid var(--line); background:var(--paper); color:var(--fg); border-radius:6px; padding:.35rem .7rem; }}
button:focus-visible, input:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
button.primary {{ background:var(--accent); color:var(--accent-ink); border-color:var(--accent); }}
button[aria-pressed="true"] {{ background:var(--accent); color:var(--accent-ink); border-color:var(--accent); }}
table {{ border-collapse:collapse; width:100%; font-size:.9rem; }}
.tw {{ overflow-x:auto; margin:.5rem 0 1.5rem; }}
th, td {{ text-align:left; padding:.35rem .5rem; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ font-size:.75rem; text-transform:uppercase; letter-spacing:.05em; color:var(--mute); }}
td a {{ color:var(--accent); font-family:var(--mono); text-decoration:none; }}
.pill {{ display:inline-block; padding:.05rem .5rem; border-radius:999px; font-size:.78rem; border:1px solid var(--line); background:var(--paper); }}
.pill.yes {{ background:var(--yes); }} .pill.part {{ background:var(--part); }} .pill.no {{ background:var(--no); }}
.setup {{ background:var(--paper); border:1px solid var(--line); border-radius:10px; padding:1rem 1.2rem; margin:1.2rem 0; scroll-margin-top:70px; }}
.sh .sid {{ font-family:var(--mono); font-weight:500; color:var(--accent); }}
.trader {{ font-size:.78rem; text-transform:uppercase; letter-spacing:.06em; font-weight:600; }}
.trader.tom {{ color:var(--tom); }} .trader.fabio {{ color:var(--fab); }}
.meta {{ display:flex; gap:.4rem; flex-wrap:wrap; }}
.grid {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:1.2rem; margin-top:.6rem; }}
.grid > * {{ min-width:0; }}
@media (max-width:860px) {{ .grid {{ grid-template-columns:1fr; }} }}
.rule {{ display:grid; gap:.3rem; }}
.step {{ display:grid; grid-template-columns:4.5rem 1fr; gap:.5rem; }}
.step .k {{ font-family:var(--mono); font-size:.8rem; color:var(--accent); padding-top:.15rem; }}
b.src {{ color:var(--src); font-weight:600; }} b.ours {{ color:var(--ours); font-weight:600; }} b.ns {{ color:var(--ns); font-weight:600; }}
blockquote {{ margin:.3rem 0; padding:.3rem .8rem; border-left:3px solid var(--line); color:var(--fg); font-style:italic; }}
ul {{ margin:0 0 .5rem 1.1rem; padding:0; }} li {{ margin:.15rem 0; }}
figure {{ margin:0; }} figure img {{ width:100%; height:auto; border:1px solid var(--line); border-radius:6px; background:#fff; }}
figcaption {{ font-size:.8rem; color:var(--mute); margin-top:.3rem; }}
.nochart {{ border:1px dashed var(--line); border-radius:6px; padding:1.5rem; color:var(--mute); text-align:center; }}
.verdict {{ display:flex; gap:.8rem; flex-wrap:wrap; align-items:center; border-top:1px solid var(--line); margin-top:1rem; padding-top:.8rem; }}
.vl {{ font-size:.78rem; text-transform:uppercase; letter-spacing:.06em; color:var(--mute); }}
.vb {{ display:flex; gap:.3rem; }}
.pick {{ display:flex; gap:.4rem; align-items:center; font-size:.9rem; }}
.out {{ font-family:var(--mono); font-size:.85rem; white-space:pre-wrap; background:var(--paper); border:1px solid var(--line); border-radius:6px; padding:.6rem; min-height:2.4rem; }}
@media (prefers-reduced-motion: no-preference) {{ .setup {{ transition:box-shadow .2s; }} }}
</style>
<div class="wrap">
<h1>Tom and Fabio setup review</h1>
<div class="intro">
  <span><b>22 setups</b> from the catalogue of 2026-10-15, in plain words. Nothing here is tested; no result is claimed.</span>
  <span><b>How you answer:</b> read 3-4 at a sitting. Click keep / rewrite / reject under each, tick up to 3 to test first, then press <b>Copy my answers</b> and paste the line into chat. Or just say the names in chat.</span>
  <span><b>Colours:</b> <b class="src">SOURCED</b> = his own words (video id given). <b class="ours">OURS</b> = a number or rule we added, never his. <b class="ns">NOT STATED</b> = he points at the chart instead of saying it.</span>
  <span><b>Charts:</b> each example day was picked by a rule we wrote (OURS), on Binance BTCUSDT data. It shows the conditions, not a trade.</span>
</div>
<div class="sticky">
  <span class="count" id="count">0 of 22 answered, 0 picked</span>
  <button type="button" class="primary" id="copy">Copy my answers</button>
  <button type="button" id="clear">Clear</button>
  <span id="copied" hidden>copied</span>
</div>
<div class="out" id="out">(your answers appear here)</div>
<h3>Overview</h3>
<div class="tw"><table><thead><tr><th>id</th><th>plain name</th><th>trader</th><th>BTC can show</th><th>his examples</th><th>stop stated</th><th>your verdict</th></tr></thead><tbody>{ov_html}</tbody></table></div>
<h3>Extraction gaps (from the 2026-10-18 audit)</h3>
<div class="tw"><table><thead><tr><th>gap</th><th>status</th><th>evidence</th></tr></thead><tbody>{gaps_html}</tbody></table></div>
{cards}
</div>
<script>
(function(){{
  var KEY='setup_review_2026_10_v1', state={{}};
  try{{ state=JSON.parse(localStorage.getItem(KEY)||'{{}}')||{{}}; }}catch(e){{ state={{}}; }}
  function save(){{ try{{ localStorage.setItem(KEY, JSON.stringify(state)); }}catch(e){{}} }}
  function render(){{
    var answered=0, picked=0, lines=[];
    document.querySelectorAll('.setup').forEach(function(s){{
      var id=s.dataset.id, st=state[id]||{{}};
      s.querySelectorAll('.vb button').forEach(function(b){{ b.setAttribute('aria-pressed', String(st.v===b.dataset.v)); }});
      var cb=s.querySelector('.pick input'); cb.checked=!!st.pick;
      var cell=document.querySelector('.vcell[data-for="'+id+'"]'); if(cell) cell.textContent=(st.v||'-')+(st.pick?' + test':'');
      if(st.v){{ answered++; lines.push(id+': '+st.v+(st.pick?' (test first)':'')); }}
      else if(st.pick){{ picked++; lines.push(id+': (test first)'); }}
      if(st.v&&st.pick) picked++;
    }});
    document.getElementById('count').textContent=answered+' of 22 answered, '+picked+' picked';
    document.getElementById('out').textContent=lines.length?('Setup review verdicts: '+lines.join('; ')):'(your answers appear here)';
  }}
  document.querySelectorAll('.vb button').forEach(function(b){{
    b.addEventListener('click', function(){{
      var id=b.closest('.setup').dataset.id; state[id]=state[id]||{{}};
      state[id].v = (state[id].v===b.dataset.v)? null : b.dataset.v; save(); render();
    }});
  }});
  document.querySelectorAll('.pick input').forEach(function(cb){{
    cb.addEventListener('change', function(){{
      var id=cb.closest('.setup').dataset.id; var n=Object.keys(state).filter(function(k){{return state[k].pick;}}).length;
      if(cb.checked && n>=3){{ cb.checked=false; return; }}
      state[id]=state[id]||{{}}; state[id].pick=cb.checked; save(); render();
    }});
  }});
  document.getElementById('clear').addEventListener('click', function(){{ state={{}}; save(); render(); }});
  document.getElementById('copy').addEventListener('click', function(){{
    var t=document.getElementById('out').textContent, ok=document.getElementById('copied');
    function done(){{ ok.hidden=false; setTimeout(function(){{ ok.hidden=true; }},1500); }}
    if(navigator.clipboard&&navigator.clipboard.writeText){{ navigator.clipboard.writeText(t).then(done, function(){{ sel(); }}); }} else sel();
    function sel(){{ var r=document.createRange(); r.selectNodeContents(document.getElementById('out')); var s=window.getSelection(); s.removeAllRanges(); s.addRange(r); }}
  }});
  render();
}})();
</script>
"""

out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "review_page.html"
out.write_text(PAGE, encoding="utf-8", newline="\n")
print(f"wrote {out} ({out.stat().st_size/1e6:.1f} MB), setups {len(SECTIONS)}, charts {sum(1 for s in SECTIONS if (EX / (s[0]+'.png')).exists())}")
