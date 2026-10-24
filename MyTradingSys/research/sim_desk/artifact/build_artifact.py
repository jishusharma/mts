"""Build artifact/index.html: the test simulator page, from every sim_desk/results/<id>.json.

One page, many tests: a new test appears by adding one JSON file (schema in sim_desk/DESIGN.md). Nothing is
computed in the page. The levels-ladder numbers (build_data below) are exported to results/ by
export_results.py from the precomputed LC3 ladder DEV results (standard DEV 2022-04-01..2024-06-30 only;
VALIDATION and HOLDOUT are never read). No price levels are written: trades are percent distances.

Usage: python build_artifact.py [--results DIR] [--out FILE]
"""
import argparse
import csv
import datetime as dt
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.normpath(os.path.join(HERE, "..", "..", "levels_confluence_2026-10-14"))
FROZEN_COL = "S2_K5_X0_2R"
STOP_COLS = ["S0_K1_X1", "S0_K2_X1", "S0_K3_X1", "S0_K4_X1", "S0_K5_X1"]
DEV_START, DEV_END = dt.date(2022, 4, 1), dt.date(2024, 6, 30)


def _num(s):
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if v == v else None


def load(src):
    with open(os.path.join(src, "frozen_rule.json"), encoding="utf-8") as f:
        rule = json.load(f)
    with open(os.path.join(src, "ladder_ideas_dev.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return rule, rows


def build_data(rule, rows):
    """Levels-ladder numbers over FILLED trades only.

    An idea whose deeper entry was never reached has net R exactly 0.0 in the csv: it is not a trade, so it is
    left out of n, mean, win rate and the running total, and counted as `unfilled` instead.
    """
    sel = [r for r in rows if r["E1"] == "True" and _num(r[FROZEN_COL]) is not None]
    sel.sort(key=lambda r: int(r["touch_t"]))
    trades, cum, c = [], [], 0.0
    for r in sel:
        d = dt.date(1970, 1, 1) + dt.timedelta(days=int(r["day"]))
        if not (DEV_START <= d <= DEV_END):
            raise ValueError("row outside the DEV window: %s" % d)
        net = round(float(r[FROZEN_COL]), 3)
        if net == 0.0:
            continue  # never filled
        l1, l2, t1 = (float(r[k]) for k in ("L1", "L2", "T1"))
        t2 = _num(r["T2"])
        if t2 is None:  # ladder rule: T2 = T1 + (T1 - L1) when no second level
            t2 = t1 + (t1 - l1)
        side = int(r["side"])
        pct = lambda p: round((p - l1) / l1 * 100 * side, 3)  # + = in favour
        c += net
        cum.append(round(c, 2))
        trades.append({"d": d.isoformat(), "s": side, "f": r["families"].replace("_", " "),
                       "l2": pct(l2), "t1": pct(t1), "t2": pct(t2), "r": net})
    stops = []
    for col in STOP_COLS:
        v = [float(r[col]) for r in rows if _num(r[col]) is not None]
        stops.append({"k": col.split("_")[1], "n": len(v), "m": round(statistics.mean(v), 3)})
    nets = [t["r"] for t in trades]
    n = len(trades)
    # the frozen file averaged over all selected ideas (incl. unfilled); rescale its gross/fee means to filled trades
    k = len(sel) / n
    dev = dict(rule["dev"])
    dev.update({"n": n, "mean": statistics.mean(nets),
                "mean_gross_r": rule["dev"]["mean_gross_r"] * k, "mean_fee_r": rule["dev"]["mean_fee_r"] * k})
    return {
        "rule": rule["rule"], "dev": dev, "power": rule["power"],
        "verdict": rule["verdict"], "n": n,
        "wins": sum(1 for x in nets if x > 0),
        "best": max(nets), "worst": min(nets),
        "ideas_selected": len(sel), "unfilled": len(sel) - n,
        "trades": trades, "cum": cum, "stops": stops,
        "ideas_total": len(rows),
    }


RESULTS_DIR = os.path.normpath(os.path.join(HERE, "..", "results"))
REQUIRED = ("id", "family", "title", "what", "how", "window", "verdict", "why", "kpis", "examples", "source_files", "commit")


def collect(results_dir):
    """Every results/*.json (standard schema, DESIGN.md) in file-name order; a malformed file stops the build."""
    out = []
    for fn in sorted(os.listdir(results_dir)):
        if not fn.endswith(".json") or fn.startswith("_"):
            continue
        with open(os.path.join(results_dir, fn), encoding="utf-8") as f:
            r = json.load(f)
        miss = [k for k in REQUIRED if k not in r]
        if miss:
            raise ValueError("%s is missing %s" % (fn, ", ".join(miss)))
        for w in r["what"]:
            if w.get("label") not in ("SOURCED", "OURS"):
                raise ValueError("%s: parameter %r needs label SOURCED or OURS" % (fn, w.get("name")))
        out.append(r)
    return out


TEMPLATE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Test Simulator</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1b2430;--mute:#5b6675;--line:#dde1e8;--good:#157a4b;--bad:#b3261e;--acc:#2456c5;--warn:#9a6700}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#10141a;--card:#181e27;--ink:#e6eaf0;--mute:#9aa6b6;--line:#2a3340;--good:#4cc38a;--bad:#ff7b72;--acc:#7aa2ff;--warn:#e3b341}}
:root[data-theme="dark"]{--bg:#10141a;--card:#181e27;--ink:#e6eaf0;--mute:#9aa6b6;--line:#2a3340;--good:#4cc38a;--bad:#ff7b72;--acc:#7aa2ff;--warn:#e3b341}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{padding:12px 16px;border-bottom:1px solid var(--line)}
h1{font-size:18px;margin:0}
#lst{max-height:calc(100vh - 150px);overflow:auto}
.sub{color:var(--mute);font-size:12px;margin-top:2px}
main{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;padding:12px 16px}
@media(min-width:900px){main{grid-template-columns:280px minmax(0,1fr);align-items:start}nav{position:sticky;top:12px;max-height:calc(100vh - 24px);overflow:auto}}
nav,article{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
nav h2{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);margin:10px 0 4px}
nav h2:first-child{margin-top:0}
nav button{display:block;width:100%;text-align:left;margin:2px 0;padding:6px 8px;border:1px solid transparent;border-radius:6px;background:none;color:var(--ink);cursor:pointer;font:inherit}
nav button[aria-current=true]{border-color:var(--acc);background:var(--bg)}
nav input[type=search]{width:100%;padding:6px;margin-bottom:6px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink);font:inherit}
nav button small{display:block;color:var(--mute)}
h2.s{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);margin:18px 0 6px}
h3{font-size:14px;margin:14px 0 4px}
.pill{display:inline-block;font-size:12px;padding:2px 10px;border-radius:99px;border:1px solid var(--mute);color:var(--mute)}
.pill.bad{border-color:var(--bad);color:var(--bad)}.pill.good{border-color:var(--good);color:var(--good)}.pill.warn{border-color:var(--warn);color:var(--warn)}
.tag{font-size:11px;padding:0 6px;border-radius:4px;border:1px solid var(--line);color:var(--mute);white-space:nowrap}
.tag.SOURCED{border-color:var(--good);color:var(--good)}.tag.OURS{border-color:var(--warn);color:var(--warn)}
dl{margin:0}dt{font-weight:600;margin-top:8px}dd{margin:0;color:var(--mute)}
.kpis{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin:8px 0}
.kpi{border:1px solid var(--line);border-radius:8px;padding:6px 8px}.kpi b{display:block;font-size:18px}.kpi span{font-size:11px;color:var(--mute)}
.bad{color:var(--bad)}.good{color:var(--good)}.warn{color:var(--warn)}
svg{width:100%;height:auto;display:block}
.ctl{display:flex;gap:8px;align-items:center;margin:8px 0;flex-wrap:wrap}
.ctl input[type=range]{flex:1;min-width:120px}
button{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--acc)}
select{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:4px}
.tw{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:3px 6px;border-bottom:1px solid var(--line);text-align:right}th:first-child,td:first-child{text-align:left}
.note{font-size:12px;color:var(--mute);margin:4px 0}
.ex{border-top:1px solid var(--line);padding-top:4px}
ul{margin:4px 0;padding-left:20px}li{margin:3px 0}
.src{font-size:12px;color:var(--mute);word-break:break-all}
</style></head><body>
<header><h1>Test simulator</h1><div class="sub">Every test, what it did, what it found and why. Past results on DEV data only; sealed windows unread. Percent distances and timestamps only, no prices.</div></header>
<main><nav id="nav" aria-label="Tests"></nav><article id="view" aria-live="polite"></article></main>
<script>
const TESTS=/*__DATA__*/null;
const CAT=/*__CAT__*/[];
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const f2=x=>(x>=0?"+":"")+x.toFixed(3);
const tone=t=>t==="bad"||t==="good"||t==="warn"?t:"";
const COL={bad:"var(--bad)",good:"var(--good)",mute:"var(--line)",warn:"var(--warn)"};
let tm=null;
const KIND={backtest:"backtest",audit:"audit",thought_experiment:"thought experiment"};
function buildNav(){const q=($("q")?$("q").value:"").toLowerCase(),only=$("onlyx")&&$("onlyx").checked,fam={};
CAT.filter(r=>(!only||r.exported)&&(!q||(r.title+" "+r.family+" "+r.verdict+" "+r.kind).toLowerCase().includes(q))).forEach(r=>(fam[r.family]=fam[r.family]||[]).push(r));
const fl=Object.keys(fam).sort((a,b)=>(fam[b].some(r=>r.exported)-fam[a].some(r=>r.exported))||a.localeCompare(b));
const list=fl.map(f=>"<h2>"+esc(f)+"</h2>"+fam[f].sort((a,b)=>(b.status==="FAILED")-(a.status==="FAILED")||b.exported-a.exported).map(r=>'<button data-id="'+esc(r.exported?r.result_id:r.id)+'">'+(r.status==="FAILED"?'<span class="bad">&#9679;</span> ':"")+esc(r.title)+"<small>"+esc(KIND[r.kind]||r.kind)+(r.exported?"":" · charts not exported yet")+"</small></button>").join("")).join("");
$("nav").innerHTML='<input id="q" type="search" placeholder="Search '+CAT.length+' tests" aria-label="Search tests" value="'+esc(q)+'"><label class="note"><input id="onlyx" type="checkbox"'+(only?" checked":"")+'> with charts only ('+CAT.filter(r=>r.exported).length+")</label><div id=\"lst\">"+list+"</div>";
$("q").oninput=refilter;$("onlyx").onchange=refilter;
$("nav").onclick=e=>{const b=e.target.closest("button");if(b){location.hash=b.dataset.id}};}
function refilter(){const q=$("q").value,o=$("onlyx").checked;buildNav();$("q").value=q;$("onlyx").checked=o;$("q").focus();}
function stub(r){return '<h1 style="font-size:20px;margin:0 0 6px">'+esc(r.title)+'</h1><span class="pill '+(r.status==="FAILED"?"bad":"")+'">'+esc(KIND[r.kind]||r.kind)+"</span> <span class=\"pill\">charts not exported yet</span>"+
'<h2 class="s">Verdict as written</h2><p>'+esc(r.verdict)+'</p><h2 class="s">Where it lives</h2><p class="src">'+esc(r.source)+'</p><p class="note">Family: '+esc(r.family)+". The kind ("+esc(r.kind_source||"")+") and the verdict line were read from the file automatically, so check them against the source. No numbers or examples are shown until this test is exported to sim_desk/results/.</p>";}
function table(x){return '<div class="tw"><table><tr>'+x.cols.map(c=>"<th>"+esc(c)+"</th>").join("")+"</tr>"+x.rows.map(r=>"<tr>"+r.map(c=>"<td>"+esc(c)+"</td>").join("")+"</tr>").join("")+"</table></div>";}
function stack(x){const W=600,rh=30;let s='<svg viewBox="0 0 '+W+" "+(x.rows.length*rh+34)+'" role="img" aria-label="'+esc(x.title)+'">';
x.rows.forEach((r,i)=>{const y=i*rh+4;s+='<text x="0" y="'+(y+14)+'" font-size="11" fill="var(--ink)">'+esc(r.label)+"</text>";let cx=190;const sc=(W-196)/100;
r.parts.forEach(p=>{const w=p.value*sc;s+='<rect x="'+cx+'" y="'+y+'" width="'+w.toFixed(1)+'" height="20" fill="'+(COL[p.tone]||"var(--acc)")+'" opacity=".8"/>';if(p.value>=6)s+='<text x="'+(cx+w/2)+'" y="'+(y+14)+'" font-size="10" text-anchor="middle" fill="var(--ink)">'+p.value+"%</text>";cx+=w;});});
const ly=x.rows.length*rh+14;let lx=190;x.rows[0].parts.forEach(p=>{s+='<rect x="'+lx+'" y="'+ly+'" width="10" height="10" fill="'+(COL[p.tone]||"var(--acc)")+'" opacity=".8"/><text x="'+(lx+14)+'" y="'+(ly+9)+'" font-size="11" fill="var(--mute)">'+esc(p.name)+"</text>";lx+=90;});
return s+"</svg>";}
function arrow(cx,side,label,col){if(side==null)return '<text x="'+cx+'" y="46" font-size="11" text-anchor="middle" fill="var(--mute)">'+label+": none</text>";
const up=side==="long"||side==="reference";const y1=up?58:22,y2=up?22:58;
return '<line x1="'+cx+'" x2="'+cx+'" y1="'+y1+'" y2="'+y2+'" stroke="'+col+'" stroke-width="3"/><path d="M'+(cx-6)+","+(y2+(up?8:-8))+" L"+cx+","+y2+" L"+(cx+6)+","+(y2+(up?8:-8))+'" fill="none" stroke="'+col+'" stroke-width="3"/><text x="'+cx+'" y="76" font-size="11" text-anchor="middle" fill="var(--mute)">'+label+(side==="opposite"||side==="reference"?"":": "+side)+"</text>";}
function sides(x){if(!x.rows.length)return '<p class="note">no example trades exported</p>';
return '<div class="kpis">'+x.rows.map(r=>{const opp=r.live==="opposite";
return '<div class="kpi"><svg viewBox="0 0 200 84" role="img" aria-label="'+esc(r.when)+'"><rect x="92" y="30" width="16" height="22" fill="var(--mute)" opacity=".5"/>'+
arrow(50,opp?"opposite":r.live,"live","var(--bad)")+arrow(150,r.backtest,"backtest","var(--acc)")+"</svg><span>"+esc(r.when)+"</span></div>"}).join("")+"</div>";}
function replay(x,id){const tr=x.trades,cum=x.cum,n=tr.length,W=600,H=200,P=28,mn=Math.min(0,...cum),mx=Math.max(0,...cum);
const X=i=>P+i*(W-P-8)/(n-1||1),Y=v=>H-P-(v-mn)/(mx-mn||1)*(H-P-10);
let h='<svg viewBox="0 0 600 200" role="img" aria-label="Running total of net R"><line x1="'+P+'" x2="'+(W-8)+'" y1="'+Y(0)+'" y2="'+Y(0)+'" stroke="var(--line)"/><polyline fill="none" stroke="var(--acc)" stroke-width="1.5" points="'+cum.map((v,i)=>X(i).toFixed(1)+","+Y(v).toFixed(1)).join(" ")+'"/><circle id="dot" r="4" fill="var(--bad)"/><text x="'+P+'" y="12" font-size="11" fill="var(--mute)">Running total of net R (high '+mx.toFixed(1)+", low "+mn.toFixed(1)+", end "+cum[n-1].toFixed(1)+")</text></svg>";
h+='<div class="ctl"><button id="prev" aria-label="Previous trade">&lt;</button><button id="play">Play</button><button id="next" aria-label="Next trade">&gt;</button><input id="slider" type="range" min="0" max="'+(n-1)+'" value="0" aria-label="Trade number"><select id="pick" aria-label="Jump to example"></select></div><svg id="ladder" viewBox="0 0 600 190" role="img" aria-label="Planned ladder of the selected trade"></svg><div id="tinfo" class="note"></div>';
return {html:h,init:()=>{const sl=$("slider"),idx=tr.map((t,i)=>i),ex=[];
[...idx].sort((a,b)=>tr[b].r-tr[a].r).slice(0,3).forEach(i=>ex.push(["Big win",i]));
[...idx].sort((a,b)=>tr[a].r-tr[b].r).slice(0,3).forEach(i=>ex.push(["Big loss",i]));
[...idx].sort((a,b)=>Math.abs(tr[a].r)-Math.abs(tr[b].r)).slice(0,2).forEach(i=>ex.push(["Flat",i]));
$("pick").innerHTML='<option value="">Examples</option>'+ex.map(e=>'<option value="'+e[1]+'">'+e[0]+" #"+(e[1]+1)+" ("+f2(tr[e[1]].r)+" R)</option>").join("");
function show(i){i=Math.max(0,Math.min(n-1,+i));sl.value=i;const t=tr[i];$("dot").setAttribute("cx",X(i));$("dot").setAttribute("cy",Y(cum[i]));
const ys=[0,t.l2,t.t1,t.t2],lo=Math.min(...ys),hi=Math.max(...ys),sp=(hi-lo)||1,y=v=>170-(v-lo)/sp*150;
const row=(v,l,c)=>'<line x1="150" x2="560" y1="'+y(v)+'" y2="'+y(v)+'" stroke="'+c+'" stroke-dasharray="4 3"/><text x="146" y="'+(y(v)+4)+'" text-anchor="end" font-size="11" fill="var(--ink)">'+l+'</text><text x="564" y="'+(y(v)+4)+'" font-size="11" fill="var(--mute)">'+(v>=0?"+":"")+v.toFixed(2)+"%</text>";
$("ladder").innerHTML=row(t.t2,"Target 2","var(--good)")+row(t.t1,"Target 1","var(--good)")+row(0,"Touched level","var(--acc)")+row(t.l2,"Deeper entry (filled here)","var(--warn)")+'<text x="150" y="186" font-size="11" fill="var(--mute)">Distance from the touched level; up is in favour of the trade</text>';
$("tinfo").innerHTML="Trade "+(i+1)+" of "+n+": "+esc(t.d)+", "+(t.s>0?"long":"short")+" at "+esc(t.f)+'. Result <b class="'+(t.r<0?"bad":"good")+'">'+f2(t.r)+" R</b> after fees.";}
sl.oninput=()=>show(sl.value);$("prev").onclick=()=>show(+sl.value-1);$("next").onclick=()=>show(+sl.value+1);
$("pick").onchange=e=>{if(e.target.value!=="")show(e.target.value)};
$("play").onclick=()=>{if(tm){clearInterval(tm);tm=null;$("play").textContent="Play";return}$("play").textContent="Pause";tm=setInterval(()=>{if(+sl.value>=n-1){$("play").onclick();return}show(+sl.value+1)},120)};
show(0);}};}
function example(x){const inits=[];let h='<div class="ex"><h3>'+esc(x.title||"Example")+"</h3>";
if(x.kind==="table")h+=table(x);else if(x.kind==="stack")h+=stack(x);else if(x.kind==="sides")h+=sides(x);
else if(x.kind==="replay"){const r=replay(x);h+=r.html;inits.push(r.init);}
else h+='<p class="note">no example trades exported</p>';
if(x.caption)h+='<p class="note">'+esc(x.caption)+"</p>";return {html:h+"</div>",inits};}
function render(id){if(tm){clearInterval(tm);tm=null}const t=TESTS.find(x=>x.id===id);
if(!t){const r=CAT.find(x=>x.id===id);if(r){document.querySelectorAll("nav button").forEach(b=>b.setAttribute("aria-current",b.dataset.id===id));$("view").innerHTML=stub(r);return}}
if(!t){render(TESTS[0].id);return}
document.querySelectorAll("nav button").forEach(b=>b.setAttribute("aria-current",b.dataset.id===t.id));
let h='<h1 style="font-size:20px;margin:0 0 6px">'+esc(t.title)+'</h1><span class="pill '+tone(t.verdict.tone)+'">'+esc(t.verdict.label)+"</span>";
h+='<div class="kpis">'+t.kpis.map(k=>'<div class="kpi"><b class="'+tone(k.tone)+'">'+esc(k.value)+"</b><span>"+esc(k.label)+"</span></div>").join("")+"</div>";
h+='<h2 class="s">What was tested</h2><dl>'+t.what.map(w=>"<dt>"+esc(w.name)+' <span class="tag '+esc(w.label)+'">'+esc(w.label)+"</span></dt><dd>"+esc(w.value_plain)+"</dd>").join("")+"</dl>";
h+='<p class="note"><b>Window:</b> '+esc(t.window)+"</p><p class=\"note\">SOURCED = taken from a named source (the trader's words or a fee table). OURS = our own judgement or tuned on DEV data.</p>";
h+='<h2 class="s">How</h2><p>'+esc(t.how)+"</p>";
const inits=[];h+='<h2 class="s">Examples</h2>';t.examples.forEach(x=>{const e=example(x);h+=e.html;inits.push(...e.inits)});
h+='<h2 class="s">Verdict and why</h2><span class="pill '+tone(t.verdict.tone)+'">'+esc(t.verdict.label)+"</span><ul>"+t.why.map(w=>"<li>"+esc(w)+"</li>").join("")+"</ul>";
h+='<h2 class="s">Where the numbers come from</h2><p class="src">'+t.source_files.map(esc).join("<br>")+"<br>commit "+esc(t.commit)+"</p>";
$("view").innerHTML=h;inits.forEach(f=>f());}
buildNav();window.onhashchange=()=>render(location.hash.slice(1));render(location.hash.slice(1));
</script></body></html>
'''


def load_catalogue(results_dir):
    p = os.path.join(results_dir, "_catalogue.json")
    if not os.path.isfile(p):
        return {"count": 0, "exported": 0, "rows": []}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def render(tests, catalogue=None):
    def blob(o):
        return json.dumps(o, separators=(",", ":"), ensure_ascii=False).replace("</", "<" + chr(92) + "/")
    cat = (catalogue or {}).get("rows", [])
    ids = {r.get("result_id") for r in cat}
    for t in tests:  # an exported result missing from the catalogue still gets a row
        if t["id"] not in ids:
            cat.append({"id": t["id"], "family": t["family"], "title": t["title"], "kind": t.get("kind", "backtest"),
                        "verdict": t["verdict"]["label"], "source": t["source_files"][0], "exported": True, "result_id": t["id"],
                        "status": "FAILED" if t["verdict"].get("tone") == "bad" else "SEE_VERDICT"})
    return TEMPLATE.replace("/*__DATA__*/null", blob(tests)).replace("/*__CAT__*/[]", blob(cat))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=RESULTS_DIR)
    ap.add_argument("--out", default=os.path.join(HERE, "index.html"))
    a = ap.parse_args(argv)
    tests = collect(a.results)
    if not tests:
        raise ValueError("no result files in %s" % a.results)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(tests, load_catalogue(a.results)))
    return a.out


if __name__ == "__main__":
    print(main())
