"""Build artifact/index.html from the precomputed LC3 ladder DEV results.

Read-only inputs (standard DEV 2022-04-01..2024-06-30 only; VALIDATION and
HOLDOUT are never read):
  research/levels_confluence_2026-10-14/frozen_rule.json
  research/levels_confluence_2026-10-14/ladder_ideas_dev.csv
No price levels are written to the page: every trade is stored as percent
distances from its first entry, so no price data is committed.

Usage: python build_artifact.py [--src DIR] [--out FILE]
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
    sel = [r for r in rows if r["E1"] == "True" and _num(r[FROZEN_COL]) is not None]
    sel.sort(key=lambda r: int(r["touch_t"]))
    trades, cum, c = [], [], 0.0
    for r in sel:
        d = dt.date(1970, 1, 1) + dt.timedelta(days=int(r["day"]))
        if not (DEV_START <= d <= DEV_END):
            raise ValueError("row outside the DEV window: %s" % d)
        l1, l2, t1 = (float(r[k]) for k in ("L1", "L2", "T1"))
        t2 = _num(r["T2"])
        if t2 is None:  # ladder rule: T2 = T1 + (T1 - L1) when no second level
            t2 = t1 + (t1 - l1)
        side = int(r["side"])
        pct = lambda p: round((p - l1) / l1 * 100 * side, 3)  # + = in favour
        net = round(float(r[FROZEN_COL]), 3)
        c += net
        cum.append(round(c, 2))
        trades.append({"d": d.isoformat(), "s": side, "f": r["families"].replace("_", " "),
                       "l2": pct(l2), "t1": pct(t1), "t2": pct(t2), "r": net})
    stops = []
    for col in STOP_COLS:
        v = [float(r[col]) for r in rows if _num(r[col]) is not None]
        stops.append({"k": col.split("_")[1], "n": len(v), "m": round(statistics.mean(v), 3)})
    nets = [t["r"] for t in trades]
    return {
        "rule": rule["rule"], "dev": rule["dev"], "power": rule["power"],
        "verdict": rule["verdict"], "n": len(trades),
        "wins": sum(1 for x in nets if x > 0),
        "best": max(nets), "worst": min(nets),
        "trades": trades, "cum": cum, "stops": stops,
        "ideas_total": len(rows),
    }


TEMPLATE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Levels Ladder Desk</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1b2430;--mute:#5b6675;--line:#dde1e8;--good:#157a4b;--bad:#b3261e;--acc:#2456c5;--warn:#9a6700}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#10141a;--card:#181e27;--ink:#e6eaf0;--mute:#9aa6b6;--line:#2a3340;--good:#4cc38a;--bad:#ff7b72;--acc:#7aa2ff;--warn:#e3b341}}
:root[data-theme="dark"]{--bg:#10141a;--card:#181e27;--ink:#e6eaf0;--mute:#9aa6b6;--line:#2a3340;--good:#4cc38a;--bad:#ff7b72;--acc:#7aa2ff;--warn:#e3b341}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:baseline;padding:12px 16px;border-bottom:1px solid var(--line)}
h1{font-size:18px;margin:0}
.pill{font-size:12px;padding:2px 10px;border-radius:99px;border:1px solid var(--bad);color:var(--bad)}
.sub{color:var(--mute);font-size:12px}
main{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;padding:12px 16px}
@media(min-width:1000px){main{grid-template-columns:300px minmax(0,1.5fr) minmax(0,1fr);height:calc(100vh - 62px)}main>section{overflow:auto}}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);margin:0 0 8px}
dl{margin:0}dt{font-weight:600;margin-top:8px}dd{margin:0;color:var(--mute)}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:8px}
.kpi{border:1px solid var(--line);border-radius:8px;padding:6px 8px}.kpi b{display:block;font-size:18px}.kpi span{font-size:11px;color:var(--mute)}
.neg{color:var(--bad)}.pos{color:var(--good)}
svg{width:100%;height:auto;display:block}
.ctl{display:flex;gap:8px;align-items:center;margin:8px 0;flex-wrap:wrap}
.ctl input[type=range]{flex:1;min-width:120px}
button{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--acc)}
select{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:4px}
table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:3px 4px;border-bottom:1px solid var(--line);text-align:right}th:first-child,td:first-child{text-align:left}
.note{font-size:12px;color:var(--mute);margin-top:8px}
</style></head><body>
<header><h1>Levels ladder desk</h1><span class="pill" id="verdict"></span>
<span class="sub">Past results on the DEV window 2022-04-01 to 2024-06-30 only. Sealed windows unread. Percent distances only, no prices.</span></header>
<main>
<section id="params"><h2>Parameters in plain words</h2>
<dl>
<dt>Idea</dt><dd>When price first touches a key level in a day (4h swing highs and lows, untested volume peaks, yesterday's high, low and volume peak, last week's high, round thousands), bet that it bounces.</dd>
<dt>Entry filter E1: RSI holds</dt><dd>Only take it if the 14-period RSI on 5-minute candles still reads above 40 for a long, below 60 for a short.</dd>
<dt>Entry S2: wait deeper</dt><dd>Do not buy at the touched level. Place the whole order at the next level beyond it, against the trade, and skip the idea if price never gets there.</dd>
<dt>Stop K5</dt><dd>Exit if price goes 0.10 % past the day's extreme so far (pushed past the deeper level if needed).</dd>
<dt>Exit X0 2R</dt><dd>Take profit at the first level in favour (target 1), or at twice the stop distance, whichever the rule picks.</dd>
<dt>Costs</dt><dd>Real Binance fees: 0.02 % for resting orders, 0.05 % for stops and market exits. No slippage.</dd>
<dt>Where the numbers come from</dt><dd>OURS: chosen as the best of 240 variants on DEV, so the result is flattering by construction. Fee rates are SOURCED from the fee table.</dd>
</dl></section>
<section id="replay"><h2>Trade replay</h2>
<div class="kpis" id="kpis"></div>
<svg id="curve" viewBox="0 0 600 200" role="img" aria-label="Cumulative net R over the trades, in order"></svg>
<div class="ctl"><button id="prev" aria-label="Previous trade">&lt;</button><button id="play">Play</button><button id="next" aria-label="Next trade">&gt;</button>
<input id="slider" type="range" min="0" value="0" aria-label="Trade number"><select id="pick" aria-label="Jump to example"></select></div>
<svg id="ladder" viewBox="0 0 600 190" role="img" aria-label="Planned ladder of the selected trade"></svg>
<div id="tinfo" class="sub" aria-live="polite"></div></section>
<section id="why"><h2>Why it failed</h2>
<div id="whytxt"></div>
<h3 style="font-size:13px;margin:12px 0 4px">Stop choice alone (all ideas, single entry)</h3>
<table id="stops"><tr><th>Stop</th><th>Ideas</th><th>Mean net R</th></tr></table>
<p class="note">R means one planned loss. Every stop type loses on average before any filter is added.</p></section>
</main>
<script>
const D=/*__DATA__*/null;
const $=id=>document.getElementById(id), f2=x=>(x>=0?"+":"")+x.toFixed(3);
$("verdict").textContent=D.verdict.indexOf("FAIL")>=0?"Does not pay: FAIL / INCONCLUSIVE":D.verdict;
$("kpis").innerHTML=[[D.n,"trades filled"],[(D.wins/D.n*100).toFixed(1)+"%","win rate"],[f2(D.dev.mean),"mean net R per trade"],
[D.dev.maxdd.toFixed(1)+" R","worst drawdown"],[f2(D.dev.mean_gross_r),"mean R before fees"],["-"+D.dev.mean_fee_r.toFixed(3),"mean fee R"]]
.map(k=>'<div class="kpi"><b>'+k[0]+'</b><span>'+k[1]+'</span></div>').join("");
const W=600,H=200,P=28,cum=D.cum,mn=Math.min(0,...cum),mx=Math.max(0,...cum);
const X=i=>P+i*(W-P-8)/(cum.length-1),Y=v=>H-P-(v-mn)/(mx-mn||1)*(H-P-10);
$("curve").innerHTML='<line x1="'+P+'" x2="'+(W-8)+'" y1="'+Y(0)+'" y2="'+Y(0)+'" stroke="var(--line)"/>'+
'<polyline fill="none" stroke="var(--acc)" stroke-width="1.5" points="'+cum.map((v,i)=>X(i).toFixed(1)+","+Y(v).toFixed(1)).join(" ")+'"/>'+
'<circle id="dot" r="4" fill="var(--bad)"/><text x="'+P+'" y="12" font-size="11" fill="var(--mute)">Running total of net R, trade by trade (high '+mx.toFixed(1)+', low '+mn.toFixed(1)+', end '+cum[cum.length-1].toFixed(1)+')</text>';
const sl=$("slider");sl.max=D.n-1;
const ex=[];const idx=D.trades.map((t,i)=>i);
[...idx].sort((a,b)=>D.trades[b].r-D.trades[a].r).slice(0,3).forEach(i=>ex.push(["Big win",i]));
[...idx].sort((a,b)=>D.trades[a].r-D.trades[b].r).slice(0,3).forEach(i=>ex.push(["Big loss",i]));
[...idx].sort((a,b)=>Math.abs(D.trades[a].r)-Math.abs(D.trades[b].r)).slice(0,2).forEach(i=>ex.push(["Flat",i]));
$("pick").innerHTML='<option value="">Examples</option>'+ex.map(e=>'<option value="'+e[1]+'">'+e[0]+' #'+(e[1]+1)+' ('+f2(D.trades[e[1]].r)+' R)</option>').join("");
function show(i){i=Math.max(0,Math.min(D.n-1,+i));sl.value=i;const t=D.trades[i];
$("dot").setAttribute("cx",X(i));$("dot").setAttribute("cy",Y(cum[i]));
const ys=[0,t.l2,t.t1,t.t2],lo=Math.min(...ys),hi=Math.max(...ys),sp=(hi-lo)||1,y=v=>170-(v-lo)/sp*150;
const row=(v,l,c)=>'<line x1="150" x2="560" y1="'+y(v)+'" y2="'+y(v)+'" stroke="'+c+'" stroke-dasharray="4 3"/><text x="146" y="'+(y(v)+4)+'" text-anchor="end" font-size="11" fill="var(--ink)">'+l+'</text><text x="564" y="'+(y(v)+4)+'" font-size="11" fill="var(--mute)">'+(v>=0?"+":"")+v.toFixed(2)+"%</text>";
$("ladder").innerHTML=row(t.t2,"Target 2","var(--good)")+row(t.t1,"Target 1","var(--good)")+row(0,"Touched level","var(--acc)")+row(t.l2,"Deeper entry (filled here)","var(--warn)")+
'<text x="150" y="186" font-size="11" fill="var(--mute)">Distance from the touched level; up is in favour of the trade</text>';
$("tinfo").innerHTML="Trade "+(i+1)+" of "+D.n+": "+t.d+", "+(t.s>0?"long":"short")+" at "+t.f+". Result <b class=\""+(t.r<0?"neg":"pos")+"\">"+f2(t.r)+" R</b> after fees.";}
sl.oninput=()=>show(sl.value);$("prev").onclick=()=>show(+sl.value-1);$("next").onclick=()=>show(+sl.value+1);
$("pick").onchange=e=>{if(e.target.value!=="")show(e.target.value)};
let tm=null;$("play").onclick=()=>{if(tm){clearInterval(tm);tm=null;$("play").textContent="Play";return}
$("play").textContent="Pause";tm=setInterval(()=>{if(+sl.value>=D.n-1){$("play").onclick();return}show(+sl.value+1)},120)};
show(0);
const d=D.dev,p=D.power;
$("whytxt").innerHTML='<p><b>1. Fees eat the edge.</b> Before fees the rule earns '+f2(d.mean_gross_r)+' R per trade; fees cost '+d.mean_fee_r.toFixed(3)+' R. Net: <b class="neg">'+f2(d.mean)+' R</b> (95% range '+f2(d.lo)+' to '+f2(d.hi)+'). It would need fees about 0.6 times the current ones to break even.</p>'+
'<p><b>2. It wins rarely.</b> Only '+D.wins+' of '+D.n+' trades won ('+(D.wins/D.n*100).toFixed(1)+'%). A few big wins (best '+f2(D.best)+' R) carry the total; the worst loss is '+f2(D.worst)+' R, and the deepest losing run is '+d.maxdd.toFixed(1)+' R.</p>'+
'<p><b>3. The best of 240 is still negative.</b> This rule was picked as the highest of 240 tries on DEV. Picking the best of many flatters the number, yet it is still below zero.</p>'+
'<p><b>4. Too few trades to be sure.</b> The stricter test says power '+Math.round(p.power_mde.power*100)+'% (below 50%), so the card rule reads INCONCLUSIVE; the looser test (power '+Math.round(p["power_plausible_0.10R"]*100)+'%) says a +0.10 R edge is ruled out. Either way: no edge shown. Default: park the idea; nothing is read on VALIDATION.</p>';
D.stops.forEach(s=>{const r=$("stops").insertRow();r.innerHTML="<td>"+s.k+"</td><td>"+s.n+'</td><td class="neg">'+f2(s.m)+"</td>"});
</script></body></html>
'''


def render(data):
    tpl = TEMPLATE
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<" + chr(92) + "/")
    return tpl.replace("/*__DATA__*/null", blob)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--out", default=os.path.join(HERE, "index.html"))
    a = ap.parse_args(argv)
    rule, rows = load(a.src)
    html = render(build_data(rule, rows))
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return a.out


if __name__ == "__main__":
    print(main())
