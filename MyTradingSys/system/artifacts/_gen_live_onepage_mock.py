"""Builds LIVE_ONEPAGE_MOCK_2026-11-04.html from repo data. Mock only; not a live generator."""
import csv
import pathlib

R = pathlib.Path(__file__).resolve().parents[2]
rows = list(csv.DictReader(open(R / 'runtime/orderflow_live/2026-10-03.csv')))


def spark(vals, w=300, h=44, color='var(--accent)'):
    lo, hi = min(vals), max(vals)
    n = len(vals)
    pts = ' '.join(f'{i*w/(n-1):.1f},{h-(v-lo)/((hi-lo) or 1)*(h-4)-2:.1f}' for i, v in enumerate(vals))
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" class="spark">'
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.6"/></svg>')


def shade(v, mx, lo=10, span=80):
    side = 'up' if v >= 0 else 'down'
    return f'color-mix(in srgb,var(--{side}) {abs(v)/mx*span+lo:.0f}%,var(--card))'


close = [float(r['c']) for r in rows]
cvd = [float(r['cvd_day']) for r in rows]
step = max(1, len(rows) // 60)
px = spark(close[::step])
cv = spark(cvd[::step], color='var(--warn)')
hrs = {}
for r in rows:
    h = (int(r['t']) // 3600000) % 24
    hrs[h] = hrs.get(h, 0) + float(r['delta'])
mx = max(abs(v) for v in hrs.values())
heat = ''.join(f'<div class="cell" style="background:{shade(hrs[h], mx)}" title="{h:02d}Z delta {hrs[h]:.0f}">{h:02d}<b>{hrs[h]:+.0f}</b></div>' for h in sorted(hrs))
bursts = []
for i in range(0, len(rows), 15):
    bursts.append(sum(int(x['b99_buy_n']) - int(x['b99_sell_n']) for x in rows[i:i + 15]))
bm = max(abs(b) for b in bursts) or 1
burst = ''.join(f'<div class="cell sm" style="background:{shade(b, bm)}" title="{b:+d}">{b:+d}</div>' for b in bursts[:32])
lo = min(float(r['l']) for r in rows)
hi = max(float(r['h']) for r in rows)
last, first = rows[-1], rows[0]
chg = (float(last['c']) / float(first['o']) - 1) * 100


def panel(pid, badge, body, active=False):
    b = f'<span class="badge" data-sample="{badge}">SAMPLE {badge}</span>' if badge else ''
    on = ' on' if active else ''
    return (f'<section id="panel-{pid}" class="panel{on}" role="tabpanel">{b}<div class="grid">{body}</div>'
            f'<div class="note"><input id="c-{pid}" maxlength="140" placeholder="one-line comment">'
            f'<button data-save="{pid}">Save</button><button data-copy>Copy all</button><span id="s-{pid}" class="saved"></span></div></section>')


def card(t, v, s=''):
    return f'<div class="card"><h4>{t}</h4><div class="big">{v}</div><div class="sub">{s}</div></div>'


def tile(t, inner):
    return f'<div class="card wide"><h4>{t}</h4>{inner}</div>'


cls = 'up' if chg >= 0 else 'down'
market = (card('BTC last', f'{float(last["c"]):,.0f}', 'Deribit perp, 2026-10-03 17:05Z')
          + card('Session move', f'<span class="{cls}">{chg:+.2f}%</span>', f'range {lo:,.0f}..{hi:,.0f}')
          + card('CVD day', f'<span class="up">{float(last["cvd_day"]):+.0f}</span> BTC', 'buy minus sell volume')
          + card('Bars', f'{len(rows)}', '1m, 03:01..17:05Z')
          + tile('Price (1m closes)', px) + tile('CVD (cumulative delta)', cv)
          + tile('Delta by hour (Z), red sell / green buy', f'<div class="row">{heat}</div>'))
signals = (tile('Big-trade bursts per 15m (99th pct buys minus sells)', f'<div class="row">{burst}</div>')
           + card('Source', 'orderflow CSV', 'bursts derived, not setup flags')
           + card('Setups promoted', '0 of 37', 'STATUS.md Layer pass')
           + card('Open flags now', 'n/a', 'live feed not on this machine'))
positions = (card('Open trades', '2', 'long 1 / short 1') + card('Testnet equity', '+0.4%', 'since reset')
             + card('Stops set', '2 of 2', 'all protected') + card('HALT', 'off', 'no halt file')
             + tile('Open trade R', spark([0, .2, .1, .5, .4, .8, .6, .9, .7, 1.1])))
CALLS = [('2026-09-22', 'short', '82800', '73000'), ('2026-09-21', 'short', '82200', '73000'),
         ('2026-09-21', 'short', '79500', '73000'), ('2026-09-15', 'short', '80000', '75500'),
         ('2026-08-27', 'long', '72000', '100000'), ('2026-08-27', 'long', '76600', '81000')]
news = ''.join(f'<div class="card"><h4>{c[0]}</h4><div class="big {"down" if c[1] == "short" else "up"}">'
               f'{"▼" if c[1] == "short" else "▲"} {c[1]}</div><div class="sub">entry {c[2]} → {c[3]}</div></div>' for c in CALLS)
news += card('Scored calls', '0 of 9', 'all in holdout window') + card('News feed', 'not built', '2 asks, 0 shipped')


def lr(n, v, c):
    return f'<div class="card"><h4>{n}</h4><div class="big {c}">{v}</div></div>'


layers = ''.join([lr('tom_core', 'STOP', 'down'), lr('tom_vp_pivot', 'closed', 'down'), lr('fabio_v3', 'redefine', 'warn'),
                  lr('fabio_escalation', 'no edge', 'down'), lr('fabio_cvd_absorp', 'no edge', 'down'),
                  lr('fabio_volume_fvg', 'no edge', 'down'), lr('malkan RSI', 'G2', 'warn'), lr('krown', 'G2', 'warn'),
                  card('Gate board', '4 at G2', 'tom fabio malkan krown'), card('Fee-net PASS', '0 of 37', 'STATUS.md')])
health = ''.join([card('CI trunk', '<span class="up">green</span>', '3f39b0f7f, 0.4 h old'),
                  card('Pages stale', '<span class="warn">3</span>', 'layer map, sim desk, home'),
                  card('Lab queue', '2 ready', 'Codex week 30% used'),
                  card('Lesson digest', '<span class="warn">STALE</span>', 'synced c5767610'),
                  card('Stray .new files', '2', 'htf_context_live (581 h)'),
                  card('Commits 24h', '186', 'research 33% (cap 30%)'),
                  card('GO-PRIVATE', 'B=1', 'carry_basis_2026-10-18'),
                  card('Live owner', 'desktop', 'mirror refused on NB')])
tabs = [('market', 'Market now', '📈', None, market), ('signals', 'Signals', '🚩', 'SAMPLE-SIG', signals),
        ('positions', 'Positions/testnet', '💼', 'SAMPLE-POS', positions), ('news', 'News & calls', '📰', None, news),
        ('layers', 'Layers', '🧱', None, layers), ('health', 'Health', '❤', None, health)]
bar = ''.join(f'<button role="tab" id="tab-{t[0]}" data-tab="{t[0]}" class="{"on" if i == 0 else ""}">{t[2]} {t[1]}</button>'
              for i, t in enumerate(tabs))
panels = ''.join(panel(t[0], t[3], t[4], i == 0) for i, t in enumerate(tabs))

CSS = """
:root{--bg:#f4f5f7;--card:#fff;--ink:#14181f;--mute:#667085;--line:#dfe3ea;--accent:#2563eb;--up:#16a34a;--down:#dc2626;--warn:#d97706}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0e1116;--card:#171b22;--ink:#e6e9ef;--mute:#8b95a5;--line:#262c36;--accent:#60a5fa;--up:#4ade80;--down:#f87171;--warn:#fbbf24}}
:root[data-theme="dark"]{--bg:#0e1116;--card:#171b22;--ink:#e6e9ef;--mute:#8b95a5;--line:#262c36;--accent:#60a5fa;--up:#4ade80;--down:#f87171;--warn:#fbbf24}
*{box-sizing:border-box}html,body{height:100%;margin:0;overflow:hidden}
body{background:var(--bg);color:var(--ink);font:13px/1.3 system-ui,sans-serif;display:flex;flex-direction:column;max-width:100%}
header{display:flex;gap:4px;padding:6px 8px;border-bottom:1px solid var(--line);overflow-x:auto;flex:none}
header button{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:6px 10px;font:inherit;cursor:pointer;white-space:nowrap}
header button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
main{flex:1;min-height:0;position:relative}
.panel{display:none;height:100%;flex-direction:column;padding:8px;gap:6px;position:relative}.panel.on{display:flex}
.grid{flex:1;min-height:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));grid-auto-rows:min-content;gap:6px;overflow:hidden;align-content:start}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px 8px;min-width:0}.card.wide{grid-column:1/-1}
h4{margin:0 0 2px;font-size:11px;font-weight:600;color:var(--mute)}.big{font-size:18px;font-weight:700}.sub{font-size:11px;color:var(--mute)}
.up{color:var(--up)}.down{color:var(--down)}.warn{color:var(--warn)}.spark{width:100%;height:44px;display:block}
.row{display:flex;gap:2px;flex-wrap:wrap}.cell{flex:1 1 34px;min-width:30px;border-radius:4px;padding:2px;text-align:center;font-size:10px;color:var(--ink)}
.cell b{display:block;font-size:10px}.cell.sm{flex:1 1 26px}
.badge{position:absolute;top:2px;right:8px;background:var(--warn);color:#000;font-size:10px;padding:1px 6px;border-radius:0 0 6px 6px;z-index:2}
.note{display:flex;gap:4px;flex:none;align-items:center}
.note input{flex:1;min-width:0;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:5px}
.note button{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:5px 8px;cursor:pointer}.saved{font-size:10px;color:var(--up)}
@media (max-width:480px){.big{font-size:15px}.grid{grid-template-columns:repeat(2,1fr)}}
"""
JS = """
var K='mts_onepage_mock_comments';
function ld(){try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return {}}}
function sv(o){try{localStorage.setItem(K,JSON.stringify(o))}catch(e){}}
var m=ld();document.querySelectorAll('input[id^=c-]').forEach(function(i){i.value=m[i.id.slice(2)]||''});
document.querySelectorAll('[data-tab]').forEach(function(b){b.onclick=function(){
 document.querySelectorAll('.panel,[data-tab]').forEach(function(e){e.classList.remove('on')});
 b.classList.add('on');document.getElementById('panel-'+b.dataset.tab).classList.add('on')}});
document.querySelectorAll('[data-save]').forEach(function(b){b.onclick=function(){
 var p=b.dataset.save,o=ld();o[p]=document.getElementById('c-'+p).value;sv(o);document.getElementById('s-'+p).textContent='saved'}});
document.querySelectorAll('[data-copy]').forEach(function(b){b.onclick=function(){
 var o=ld(),t=Object.keys(o).map(function(k){return k+': '+o[k]}).join(String.fromCharCode(10));
 try{navigator.clipboard.writeText(t)}catch(e){}}});
"""
html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>MTS Live One Page</title>'
        f'<style>{CSS}</style></head><body><header role="tablist">{bar}</header><main>{panels}</main>'
        f'<script>{JS}</script></body></html>')
open(R / 'system/artifacts/LIVE_ONEPAGE_MOCK_2026-11-04.html', 'w', encoding='utf-8', newline='\n').write(html)
print(len(html))
