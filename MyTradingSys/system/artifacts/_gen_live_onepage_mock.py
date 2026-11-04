"""Builds LIVE_ONEPAGE_MOCK_2026-11-04.html from repo data. Mock only; not a live generator.

v2 (operator style, memory mts-artifact-design-dense-symbols): one screen, tabs, base font 16px,
3-4 KPI tiles, a delta box per tab, date x symbol heatmaps, mono price ladder with a "now" row,
trailing 1m | 5m legend. Every number is read from a repo file at build time; rows that are
hand-copied or invented are marked in the md (SAMPLE badges).
Run: python MyTradingSys/system/artifacts/_gen_live_onepage_mock.py [--fragment OUT]
"""
import collections
import csv
import datetime as dt
import html
import json
import pathlib
import re
import sys

R = pathlib.Path(__file__).resolve().parents[2]
OUT = R / 'system/artifacts/LIVE_ONEPAGE_MOCK_2026-11-04.html'
NOW = dt.datetime.now(dt.timezone.utc)
E = html.escape

# ---------- data ----------
OF = R / 'runtime/orderflow_live'
DAYS = sorted(p.stem for p in OF.glob('20*.csv'))
BARS = {d: list(csv.DictReader(open(OF / f'{d}.csv'))) for d in DAYS}
LAST_DAY = DAYS[-1]
rows = BARS[LAST_DAY]
last = rows[-1]
LAST_PX = float(last['c'])
LAST_TS = dt.datetime.fromtimestamp(int(last['t']) / 1000, dt.timezone.utc)
AGE_D = (NOW - LAST_TS).days


def fnum(x, d=0):
    return f'{x:,.{d}f}'


def sgn(x, d=0):
    return f'{x:+,.{d}f}'


def hour_delta(bars):
    h = collections.defaultdict(float)
    for b in bars:
        h[(int(b['t']) // 3600000) % 24] += float(b['delta'])
    return h


HD = {d: hour_delta(BARS[d]) for d in DAYS}
DAY_CLOSE = {d: float(BARS[d][-1]['c']) for d in DAYS}
DAY_OPEN = {d: float(BARS[d][0]['o']) for d in DAYS}
DAY_CVD = {d: float(BARS[d][-1]['cvd_day']) for d in DAYS}
DAY_HI = {d: max(float(b['h']) for b in BARS[d]) for d in DAYS}
DAY_LO = {d: min(float(b['l']) for b in BARS[d]) for d in DAYS}
poc = collections.Counter()
for b in rows:
    poc[float(b['poc_price'])] += float(b['poc_vol'])
POC = poc.most_common(1)[0][0]
last5 = rows[-5:]
D1 = float(last['delta'])
D5 = sum(float(b['delta']) for b in last5)
C5 = (float(last5[-1]['c']) / float(last5[0]['o']) - 1) * 100

C30 = json.load(open(R / 'research/eagle_eyes_picture_2026-10-28/c30_validation_verdict.json'))
LEDGER = list(csv.DictReader(open(R / 'research/habib_plan_imbalance_2026-10-20/PLAN_LEDGER.csv')))
VERD = json.load(open(R.parent / 'scripts/dev/market_guide_verdicts.json'))
STATUS = (R / 'research/STATUS.md').read_text(encoding='utf-8')
LAYERS_MD = (R / 'system/LAYERS.md').read_text(encoding='utf-8')


def st(pattern, default='n/a'):
    m = re.search(pattern, STATUS, re.M)
    return m.group(1) if m else default


CI_SHA = st(r'^CI green: (\w+)')
CI_STATE = 'green' if CI_SHA != 'n/a' else 'red'
LAYER_PASS = st(r'^Layer pass: (\d+ of \d+)')
PAGES_STALE = st(r'^Pages stale: (\d+)')
LESSONS = 'STALE' if re.search(r'^LESSONS: digest STALE', STATUS, re.M) else 'ok'
GO_PRIV = st(r'^GO-PRIVATE: (A=\d+ B=\d+)')
COMMITS = st(r'^commits 24h: (\d+)')
RESEARCH_PCT = st(r'research (\d+)%')
NEW_FILES = len(re.findall(r'^- MyTradingSys/.*\.new \(', STATUS, re.M))
STATUS_AT = st(r'^Generated: (.+)$')
STATUS_AGE_H = int((NOW.replace(tzinfo=None) - dt.datetime.fromisoformat(STATUS_AT) + dt.timedelta(hours=5, minutes=30)).total_seconds() // 3600) if STATUS_AT != 'n/a' else -1  # STATUS.md stamps IST
STALE_H = STATUS_AGE_H < 0 or STATUS_AGE_H > 6  # readings older than 6 h are called stale
GATES = re.findall(r'^(tom|fabio|malkan|krown)\s+G(\d)\s+proof (?:changed (\d+)h ago|(not on trunk))', STATUS, re.M)

# layer verdict lines from LAYERS.md
LAYER_ROWS = collections.OrderedDict()
cur = None
for line in LAYERS_MD.splitlines():
    m = re.match(r'- Layer `([^`]+)`: ([^|]*)', line)
    if m:
        cur = m.group(1)
        LAYER_ROWS[cur] = {'head': m.group(2).strip(), 'dated': []}
        continue
    m = re.match(r'\s+- (20\d\d-\d\d-\d\d) `([^`]+)`: ([^|]*)', line)
    if m and cur:
        LAYER_ROWS[cur]['dated'].append((m.group(1), m.group(2), m.group(3).strip()))
N_LAYERS = len(LAYER_ROWS)
N_VERD = sum(len(v['dated']) for v in LAYER_ROWS.values())


def vsym(text):
    t = text.lower()
    if 'withdrawn' in t or 'not real' in t or 'unproven' in t:
        return '↩', 'warn', 'PASS withdrawn'
    if 'blocked' in t:
        return '⏸', 'warn', 'blocked'
    if re.search(r'\bpass\b', t) and 'parity' not in t:
        return '✓', 'up', 'pass'
    if any(k in t for k in ('no edge', 'negative', 'fail', 'no anchor', 'no level', 'not reproduced',
                            'no surviving', 'no cell', '0 pass', 'not supported', 'below buy')):
        return '✗', 'down', 'no edge'
    return '●', 'mute', 'descriptive'


# ---------- html helpers ----------
def kpi(label, value, sub='', cls=''):
    return (f'<div class="kpi"><span class="lab">{E(label)}</span><span class="val {cls}">{value}</span>'
            f'<span class="sub">{E(sub)}</span></div>')


def kpis(*items):
    return '<div class="kpis">' + ''.join(items) + '</div>'


def delta_box(title, lines):
    li = ''.join(f'<li><span class="when">{E(a)}</span><span class="sym {c}">{s}</span>{E(b)}</li>' for a, s, c, b in lines)
    return f'<div class="box delta"><h3>Δ {E(title)}</h3><ul>{li}</ul></div>'


def ladder(title, levels):
    """levels: (label, price, cls); a 'now' row is inserted at LAST_PX."""
    allrows = sorted(levels + [(f'last bar {LAST_TS:%m-%d %H:%M}Z', LAST_PX, 'now')], key=lambda x: -x[1])
    tr = ''.join(f'<tr class="{c}"><td>{E(n)}</td><td>{fnum(p)}</td><td>{"" if c == "now" else sgn((p / LAST_PX - 1) * 100, 2) + "%"}</td></tr>'
                 for n, p, c in allrows)
    return f'<div class="box"><h3>{E(title)}</h3><table class="ladder"><tbody>{tr}</tbody></table></div>'


def shade(v, mx):
    side = 'up' if v >= 0 else 'down'
    pct = 12 + 78 * min(1, abs(v) / (mx or 1))
    return f'color-mix(in srgb,var(--{side}) {pct:.0f}%,var(--cell))'


def heat(title, row_labels, col_labels, cells, legend):
    """cells[r][c] = (value or None, text, title, ring)."""
    k = max(1, -(-sum(1 for c in col_labels if c) // 6))
    seen = [i for i, c in enumerate(col_labels) if c]
    show = {i for n, i in enumerate(seen) if n % k == 0}
    head = '<span></span>' + ''.join(f'<span class="ch">{E(c) if i in show else ""}</span>' for i, c in enumerate(col_labels))
    body = ''
    for r, lab in enumerate(row_labels):
        body += f'<span class="rh">{E(lab)}</span>'
        for c in range(len(col_labels)):
            v, txt, tip, ring = cells[r][c]
            st_ = '' if v is None else f' style="background:{v}"'
            body += f'<button class="hc{" ring" if ring else ""}"{st_} data-tip="{E(tip)}">{txt}</button>'
    cols = len(col_labels)
    return (f'<div class="box heat"><h3>{E(title)}</h3><div class="hg" style="grid-template-columns:minmax(3.2rem,auto) repeat({cols},minmax(0,1fr))">'
            f'{head}{body}</div><div class="tip" aria-live="polite">{E(legend)}</div></div>')


def panel(pid, badge, body, active=False):
    b = f'<div class="badge" data-sample="{badge}">{badge} · invented numbers, layout only</div>' if badge else ''
    return (f'<section id="panel-{pid}" class="panel{" on" if active else ""}" role="tabpanel" aria-labelledby="tab-{pid}">{b}'
            f'<div class="pbody">{body}</div>'
            f'<div class="note"><input id="c-{pid}" maxlength="140" placeholder="one-line comment on this tab" aria-label="comment">'
            f'<button data-save="{pid}">Save</button><button data-copy title="copies the note of every tab, to paste into chat">Copy notes</button><span id="s-{pid}" class="saved"></span></div></section>')


def price_line(title, pts):
    w, h, pad = 600, 120, 6
    lo, hi = min(pts), max(pts)
    xy = [(i * (w - 2 * pad) / (len(pts) - 1) + pad, h - pad - (v - lo) / ((hi - lo) or 1) * (h - 2 * pad)) for i, v in enumerate(pts)]
    line = ' '.join(f'{x:.1f},{y:.1f}' for x, y in xy)
    area = f'{pad},{h - pad} {line} {xy[-1][0]:.1f},{h - pad}'
    grid = ''.join(f'<line x1="0" x2="{w}" y1="{y}" y2="{y}" stroke="var(--line)" stroke-width="1"/>' for y in (pad, h / 2, h - pad))
    ex, ey = xy[-1]
    return (f'<div class="box"><h3>{E(title)}</h3><svg class="pl" viewBox="0 0 {w} {h}" role="img" aria-label="{E(title)}">{grid}'
            f'<polygon points="{area}" fill="var(--accent)" fill-opacity=".12"/>'
            f'<polyline points="{line}" fill="none" stroke="var(--accent)" stroke-width="2"/>'
            f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="var(--accent)"/></svg>'
            f'<div class="plx"><span>{fnum(lo)} low</span><span>{fnum(hi)} high</span></div></div>')


HOURLY = [float(b['c']) for d in DAYS for i, b in enumerate(BARS[d]) if i % 60 == 59 or i == len(BARS[d]) - 1]

# ---------- Market ----------
chg = (LAST_PX / DAY_OPEN[LAST_DAY] - 1) * 100
hours = list(range(24))
PARTIAL = len(rows) < 1440  # the newest file can stop mid-day
FIRST_TS = dt.datetime.fromtimestamp(int(rows[0]['t']) / 1000, dt.timezone.utc)
SPAN = f'{FIRST_TS:%H:%M}→{LAST_TS:%H:%M}Z' if PARTIAL else 'full day'


def day_read(pm, cvd):
    """Plain read of one day: did price and net buying agree? (context only: price/CVD divergence tested NEGATIVE 2026-10-14)."""
    if pm >= 0 and cvd >= 0:
        return '▲', 'up', 'buyers pushed it up'
    if pm < 0 and cvd < 0:
        return '▼', 'down', 'sellers pushed it down'
    if pm >= 0:
        return '◇', 'warn', 'rose on net selling'
    return '◇', 'warn', 'fell despite net buying'


trs = ''
for d in DAYS:
    pm = (DAY_CLOSE[d] / DAY_OPEN[d] - 1) * 100
    sym, cls, txt = day_read(pm, DAY_CVD[d])
    part = ' *' if len(BARS[d]) < 1440 else ''
    trs += (f'<tr><td>{d[5:]}{part}</td><td class="{"up" if pm >= 0 else "down"}">{"▲" if pm >= 0 else "▼"} {sgn(pm, 2)}%</td>'
            f'<td class="{"up" if DAY_CVD[d] >= 0 else "down"}">{sgn(DAY_CVD[d])}</td><td class="{cls}"><span class="sym">{sym}</span> {txt}</td></tr>')
days_tbl = ('<div class="box"><h3>Who won each day</h3><table class="dtab"><thead><tr><th>day</th><th>price</th><th>net BTC bought</th><th>read</th></tr></thead>'
            f'<tbody>{trs}</tbody></table><p class="how">◇ = price and buying disagree: watch, not a trade on its own (tested 10-14, no edge).'
            + (f' * {LAST_DAY[5:]} is partial: {SPAN}.' if PARTIAL else '') + '</p></div>')
prev_day = DAYS[-2]
big_h = max(HD[LAST_DAY], key=lambda h: abs(HD[LAST_DAY][h]))
m_delta = [
    (LAST_DAY[5:], '▲' if DAY_CLOSE[LAST_DAY] >= DAY_CLOSE[prev_day] else '▼', 'up' if DAY_CLOSE[LAST_DAY] >= DAY_CLOSE[prev_day] else 'down',
     f'last {fnum(DAY_CLOSE[LAST_DAY])} vs {fnum(DAY_CLOSE[prev_day])} close'),
    (LAST_DAY[5:], '▲' if DAY_CVD[LAST_DAY] >= 0 else '▼', 'up' if DAY_CVD[LAST_DAY] >= 0 else 'down',
     f'net bought {sgn(DAY_CVD[LAST_DAY])} vs {sgn(DAY_CVD[prev_day])} BTC'),
    (f'{big_h:02d}Z', '◆', 'warn', f'biggest hour {sgn(HD[LAST_DAY][big_h])} BTC'),
]
market = (kpis(kpi('BTC last bar', fnum(LAST_PX), f'Binance futures · {LAST_TS:%m-%d %H:%M}Z'),
               kpi('Move ' + ('so far' if PARTIAL else 'day'), f'{"▲" if chg >= 0 else "▼"} {sgn(chg, 2)}%', SPAN, 'up' if chg >= 0 else 'down'),
               kpi('Net BTC bought', f'{"▲" if DAY_CVD[LAST_DAY] >= 0 else "▼"} {sgn(DAY_CVD[LAST_DAY])}', 'buys minus sells, ' + SPAN, 'up' if DAY_CVD[LAST_DAY] >= 0 else 'down'),
               kpi('Range', fnum(DAY_HI[LAST_DAY] - DAY_LO[LAST_DAY]), f'{fnum(DAY_LO[LAST_DAY])} → {fnum(DAY_HI[LAST_DAY])}'))
          + '<div class="cols"><div class="stack">' + days_tbl
          + price_line(f'Price, {DAYS[0][5:]} → {LAST_DAY[5:]} (1h closes)', HOURLY) + '</div>'
          + '<div class="stack">' + delta_box(f'since {prev_day[5:]}', m_delta)
          + ladder('Levels vs last bar', [(f'{LAST_DAY[5:]} high', DAY_HI[LAST_DAY], ''), (f'{LAST_DAY[5:]} low', DAY_LO[LAST_DAY], ''),
                                         ('most traded price', POC, 'poc'), ('5-day high', max(DAY_HI.values()), ''), ('5-day low', min(DAY_LO.values()), '')])
          + '</div></div>')

# ---------- Signals (backtest, real) ----------
months = []
y, m = 2024, 7
for _ in range(12):
    months.append(f'{y}-{m:02d}')
    m += 1
    if m == 13:
        y, m = y + 1, 1
NAMES = {'H1': '30m rule', 'H2': '15m + 2h up'}  # PRE_REG_C30.md section 0: H1 = 30m chart, H2 = 15m chart with 2h trend up
scells, srows = [], []
for hk in ('H1', 'H2'):
    tr = C30[hk]['trades']
    by = collections.defaultdict(list)
    for t in tr:
        by[t[0][:7]].append(t[1])
    worst_m = min(by, key=lambda k: sum(by[k])) if by else None
    row = []
    for mo in months:
        v = by.get(mo)
        if not v:
            row.append((None, '·', f'{NAMES[hk]} {mo}: no trade', False))
            continue
        s = sum(v)
        sym = '✓' if s > 0 else '✗'
        row.append((shade(s, 6), sym, f'{NAMES[hk]} {mo}: {len(v)} trades, {sgn(s, 2)}% after fees', mo == worst_m))
    scells.append(row)
    srows.append(NAMES[hk])
h1, h2 = C30['H1'], C30['H2']
s_delta = [(t[0][2:10], '✓' if t[1] > 0 else '✗', 'up' if t[1] > 0 else 'down', f'{sgn(t[1], 2)}%, held {t[2] / 2:g} h')
           for t in reversed(h1['trades'][-5:])]


def vcls(v):
    return 'down' if v == 'FAIL' else 'warn'


signals = (kpis(kpi('30m rule trades', f'{h1["n"]}', f'{h1["win"]:.0f}% of them won'),
                kpi('Avg per trade', f'{sgn(h1["mean"], 2)}%', f'after fees · worst {h1["worst"]:.1f}%', 'down' if h1['mean'] < 0 else 'up'),
                kpi('30m rule', '✗ loses', 'do not trade it alone', vcls(h1['verdict'])),
                kpi('15m + 2h up', '? unproven', f'{sgn(h2["mean"], 2)}%/trade, {h2["n"]} trades', vcls(h2['verdict'])))
           + '<div class="cols">'
           + '<div class="stack">'
           + heat('Buy the dip: WaveTrend low + RSI divergence, test year 2024-07 → 2025-06', srows, [mo[5:] for mo in months], scells,
                  '✓ month made money after fees · ✗ lost · ring = worst month · past test, not a live signal')
           + '<div class="box"><h3>What it means for you</h3><ul class="means">'
           + f'<li><span class="sym down">✗</span>30m rule: {h1["win"]:.0f}% wins but big losers eat them ({h1["worst"]:.1f}% worst). Not a trade on its own.</li>'
           + '<li><span class="sym warn">?</span>15m buy only when 2h trend is up: small gain, could be luck. Watch only.</li>'
           + '<li><span class="sym mute">●</span>Why 30m: your swing chart; Eagle_Eyes study C30 (10-31).</li></ul></div></div>'
           + '<div class="stack">' + delta_box('last 5 trades, 30m rule', s_delta)
           + '<div class="box"><h3>Timeframe flips now</h3><p class="big mute">not on this page yet</p><p class="sub">needs live candles; proposed next</p></div>'
           + '</div></div>')

# ---------- Positions (SAMPLE) ----------
positions = (kpis(kpi('Open trades', '2', 'long 1 · short 1'), kpi('Testnet P&L', '▲ +0.4%', 'since reset', 'up'),
                  kpi('Stops set', '✓ 2/2', 'all protected', 'up'), kpi('HALT', '○ off', 'no halt file'))
             + '<div class="cols">'
             + ladder('Trade A (long) levels', [('target', LAST_PX * 1.012, 'up'), ('entry', LAST_PX * 0.997, ''), ('stop', LAST_PX * 0.991, 'down')])
             + '<div class="stack">' + delta_box('today', [('09:12', '▲', 'up', 'A opened long'), ('11:40', '▼', 'down', 'B opened short'),
                                                           ('12:05', '◆', 'warn', 'A stop moved to entry')])
             + '</div></div>')

# ---------- News & calls ----------
calls = sorted(LEDGER, key=lambda c: c['posted_utc'])
call_dates = [c['posted_utc'][5:10] for c in calls]
ccells = [[(f'var(--{"down" if c["direction"] == "short" else "up"}-bg)', '▼' if c['direction'] == 'short' else '▲',
            f'{c["posted_utc"][:10]} {c["direction"]} entry {c["entry"]} → {c["target1"]} · {c["status"].lower().replace("_", " ")}',
            i > 0 and c['direction'] != calls[i - 1]['direction']) for i, c in enumerate(calls)]]
last_call = dt.datetime.fromisoformat(calls[-1]['posted_utc'].replace('Z', '+00:00'))
NEWS = [  # hand-copied from research/news_feeds_2026-10-30/REPORT.md section 2 (2026-10-29, UTC)
    ('20:24', '⛓', 'warn', 'on-chain: 167k ETH leave Binance'),
    ('20:39', '⚡', 'down', 'Tree News: potential Binance hack'),
    ('20:40', '▼', 'down', 'main leg low 78,199, 10x volume'),
    ('21:12', '✉', 'mute', 'CoinDesk RSS, after the low'),
    ('21:15', '◎', 'mute', 'CZ: looks like a hack'),
]
news = (kpis(kpi('Habib calls', f'{len(calls)}', 'in the plan ledger'),
             kpi('Scored', f'{sum(1 for c in calls if c["status"].startswith("SCORED"))}/{len(calls)}', 'all in holdout window', 'warn'),
             kpi('Habib spoke last', f'{(NOW - last_call).days} d', f'{last_call:%m-%d} {calls[-1]["direction"]}'),
             kpi('News lead', '15 min', 'headline before main leg', 'up'))
        + '<div class="cols">'
        + '<div class="stack">'
        + heat('Habib calls by date', ['Habib'], call_dates, ccells, '▲ long · ▼ short · ring = direction flipped · tap a cell')
        + ladder('Habib levels vs last price', [(f'{c["posted_utc"][5:10]} {c["direction"][0].upper()} entry', float(c['entry']), '') for c in calls[-4:]]
                 + [('target 73,000', 73000.0, 'down')])
        + '</div>'
        + delta_box('2026-10-29 Binance hack, UTC', NEWS)
        + '</div>')

# ---------- Layers ----------
start = dt.date(2026, 9, 21)
weeks = [start + dt.timedelta(days=7 * i) for i in range(((NOW.date() - start).days // 7) + 1)]
lnames = [n for n, v in LAYER_ROWS.items() if v['dated']]
lcells = []
for n in lnames:
    row = []
    for w in weeks:
        hits = [x for x in LAYER_ROWS[n]['dated'] if w <= dt.date.fromisoformat(x[0]) < w + dt.timedelta(days=7)]
        if not hits:
            row.append((None, '', f'{n} week {w:%m-%d}: nothing', False))
            continue
        syms = [vsym(x[2]) for x in hits]
        pick = next((s for s in syms if s[0] in '↩✓⏸'), next((s for s in syms if s[0] == '✗'), syms[0]))
        tip = f'{n} · ' + ' | '.join(f'{x[0][5:]} {x[1]}: {" ".join(x[2].split()[:8])}' for x in hits)
        row.append((f'var(--{pick[1]}-bg)', pick[0], tip, pick[0] == '↩'))
    lcells.append(row)
recent = sorted({(x[0], n, x[2]) for n, v in LAYER_ROWS.items() for x in v['dated']}, reverse=True)[:5]
l_delta = [(d[5:], vsym(t)[0], vsym(t)[1], f'{n}: {" ".join(t.split()[:5])}') for d, n, t in recent]
tags = ''.join(f'<span class="chip {"down" if v["tag"] == "NO-EDGE" else "warn"}">{"✗" if v["tag"] == "NO-EDGE" else "?"} {E(k)}</span>' for k, v in VERD.items())
layers = (kpis(kpi('Fee-net PASS', LAYER_PASS.replace(' of ', '/'), 'surviving rows', 'down'),
               kpi('Layers', f'{N_LAYERS}', f'{len(lnames)} with dated verdicts'),
               kpi('Verdicts', f'{N_VERD}', 'dated lines in LAYERS.md'),
               kpi('Newest', recent[0][0][5:], recent[0][1][:16]))
          + '<div class="cols">'
          + heat('Layer verdicts by week', [n[:16] for n in lnames], [f'{w:%m-%d}' for w in weeks], lcells,
                 '✗ no edge · ● descriptive · ↩ PASS withdrawn (ringed) · ⏸ blocked · tap a cell')
          + '<div class="stack">' + delta_box('newest verdicts', l_delta)
          + f'<div class="box"><h3>Market guide tags</h3><div class="chips">{tags}</div></div>'
          + '</div></div>')

# ---------- Health ----------
V1 = {'CI': 'green', 'Pages stale': '3', 'Lessons': 'STALE', '.new files': '2', 'Commits 24h': '186'}  # what mock v1 showed
NOWH = {'CI': CI_STATE, 'Pages stale': PAGES_STALE, 'Lessons': LESSONS, '.new files': str(NEW_FILES), 'Commits 24h': COMMITS}
h_delta = [(k, '=' if V1[k] == NOWH[k] else '→', 'mute' if V1[k] == NOWH[k] else 'warn', f'{V1[k]} → {NOWH[k]}' if V1[k] != NOWH[k] else f'{NOWH[k]} (same)')
           for k in V1]
gcells = [[(f'var(--{"up" if int(g) > lvl else "cell"})', '●' if int(g) > lvl else '○',
            f'{n} G{g}' + (f', proof changed {hrs}h ago' if hrs else ', proof not on trunk'), False) for lvl in range(3)]
          for n, g, hrs, _ in GATES]
health = (kpis(kpi('CI trunk', f'{"✓" if CI_STATE == "green" else "✗"} {CI_STATE}' + ('?' if STALE_H else ''), f'{CI_SHA[:9]} · read {STATUS_AGE_H} h ago' + (' · STALE' if STALE_H else ''),
                   'warn' if STALE_H else 'up' if CI_STATE == 'green' else 'down'),
               kpi('Pages stale', PAGES_STALE, 'need republish', 'warn' if PAGES_STALE != '0' else 'up'),
               kpi('Lesson digest', LESSONS, 'rules file', 'warn' if LESSONS != 'ok' else 'up'),
               kpi('Commits 24h', COMMITS, f'research {RESEARCH_PCT}%'))
          + '<div class="cols">'
          + heat('Analyst gates G1 → G3', [g[0] for g in GATES], ['G1', 'G2', 'G3'], gcells, '● reached · ○ not yet · tap a cell')
          + '<div class="stack">' + delta_box('since mock v1', h_delta)
          + f'<div class="box"><h3>Other</h3><p class="sub">GO-PRIVATE {E(GO_PRIV)} · .new files {NEW_FILES} · STATUS.md {E(STATUS_AT)}</p></div>'
          + '</div></div>')

# ---------- page ----------
TABS = [('market', 'Market now', '◉', 'warn', None, market), ('signals', 'Signals', '⚑', 'down', None, signals),
        ('positions', 'Positions/testnet', '◧', 'mute', 'SAMPLE-POS', positions), ('news', 'News & calls', '✉', 'warn', None, news),
        ('layers', 'Layers', '▤', 'down', None, layers), ('health', 'Health', '✚', 'warn' if STALE_H else 'up' if CI_STATE == 'green' else 'down', None, health)]
bar = ''.join(f'<button role="tab" id="tab-{t[0]}" data-tab="{t[0]}" aria-controls="panel-{t[0]}" class="{"on" if i == 0 else ""}">'
              f'<span class="ti">{t[2]}</span>{E(t[1])}<i class="dot {t[3]}"></i></button>' for i, t in enumerate(TABS))
panels = ''.join(panel(t[0], t[4], t[5], i == 0) for i, t in enumerate(TABS))
legend = (f'<b>1m</b> {fnum(LAST_PX)} Δ{sgn(D1)} · <b>5m</b> {sgn(C5, 2)}% Δ{sgn(D5)} · '
          f'<b>POC</b> {fnum(POC)} ({sgn((POC / LAST_PX - 1) * 100, 2)}%)')

CSS = """
/* layout: header (name, data-age chip, tabs) / one panel = KPI row, then heatmap | delta box + ladder / comment row / 1m|5m legend */
:root{--bg:#eef1f4;--card:#ffffff;--cell:#e3e8ee;--ink:#121820;--mute:#5b6675;--line:#d3dae3;--accent:#1f5fbf;
--up:#13804a;--down:#c42b2b;--warn:#b26a00;--up-bg:#cfeedd;--down-bg:#f6d3d3;--warn-bg:#f5e3c4;--mute-bg:#e3e8ee;
--f-ui:"Archivo",system-ui,sans-serif;--f-num:"JetBrains Mono",ui-monospace,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0d1117;--card:#151b23;--cell:#1f2731;--ink:#e7ebf0;--mute:#8d99a8;--line:#27303b;--accent:#6ea8ff;
--up:#46c983;--down:#ff6b6b;--warn:#f0b44c;--up-bg:#173d2a;--down-bg:#4a1f22;--warn-bg:#46351a;--mute-bg:#1f2731;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0d1117;--card:#151b23;--cell:#1f2731;--ink:#e7ebf0;--mute:#8d99a8;--line:#27303b;--accent:#6ea8ff;
--up:#46c983;--down:#ff6b6b;--warn:#f0b44c;--up-bg:#173d2a;--down-bg:#4a1f22;--warn-bg:#46351a;--mute-bg:#1f2731;color-scheme:dark}
*{box-sizing:border-box}
html,body{height:100%;margin:0;overflow:hidden}
body{background:var(--bg);color:var(--ink);font:16px/1.35 var(--f-ui);display:flex;flex-direction:column;max-width:100%;
padding-left:max(12px,env(safe-area-inset-left,0px));padding-right:max(12px,env(safe-area-inset-right,0px))}
header{flex:none;display:flex;flex-direction:column;gap:6px;padding-block:8px 6px}
.top{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.top h1{font-size:1.05rem;margin:0;font-weight:700;letter-spacing:.01em}
.age{font:700 .8rem var(--f-num);padding:2px 8px;border-radius:999px;background:var(--warn-bg);color:var(--warn)}.age.old{background:var(--down);color:var(--card)}
.dtab{width:100%;border-collapse:collapse;font:.9rem var(--f-num);font-variant-numeric:tabular-nums}
.dtab th{font:600 .72rem var(--f-ui);text-transform:uppercase;letter-spacing:.05em;color:var(--mute);text-align:left;padding:2px 4px}
.dtab td{padding:3px 4px;border-bottom:1px solid var(--line);white-space:nowrap}.dtab td:nth-child(2),.dtab td:nth-child(3){text-align:right}
.how{margin:6px 0 0;font-size:.82rem;color:var(--mute)}
.means{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px;font-size:.92rem}
.means li{display:grid;grid-template-columns:1.6rem 1fr;align-items:baseline}
.tabs{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none}
.tabs button{flex:none;display:flex;align-items:center;gap:6px;background:var(--card);color:var(--ink);border:1px solid var(--line);
border-radius:8px;padding:7px 11px;font:600 .95rem var(--f-ui);cursor:pointer;white-space:nowrap}
.tabs button.on{background:var(--accent);border-color:var(--accent);color:var(--card)}
.tabs button:focus-visible,.hc:focus-visible,.note button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.ti{font-size:1.1rem;line-height:1}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;background:var(--mute)}
.dot.up{background:var(--up)}.dot.down{background:var(--down)}.dot.warn{background:var(--warn)}
main{flex:1;min-height:0;position:relative}
.panel{display:none;height:100%;flex-direction:column;gap:8px;position:relative}.panel.on{display:flex}
.pbody{flex:1;min-height:0;overflow:auto;display:flex;flex-direction:column;gap:8px}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 10px;display:flex;flex-direction:column;min-width:0}
.lab{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);font-weight:600}
.val{font:700 1.6rem/1.15 var(--f-num);font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sub{font-size:.85rem;color:var(--mute);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cols{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:8px;align-items:start}
.stack{display:flex;flex-direction:column;gap:8px;min-width:0}
.box{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 10px;min-width:0}
.box h3{margin:0 0 6px;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--mute)}
.delta ul{list-style:none;margin:0;padding:0;font:.9rem/1.5 var(--f-num)}
.delta li{display:grid;grid-template-columns:minmax(3.4rem,max-content) 1.5rem 1fr;column-gap:4px;align-items:baseline;border-bottom:1px dashed var(--line)}
.delta li:last-child{border-bottom:0}
.when{color:var(--mute)}.sym{font-size:1.15rem;text-align:center}
.hg{display:grid;gap:2px;align-items:center}
.ch{font:.72rem var(--f-num);color:var(--mute);text-align:center;overflow:visible;white-space:nowrap}
.rh{font:.8rem var(--f-num);color:var(--mute);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-right:4px}
.hc{min-height:1.7rem;border:0;border-radius:3px;background:var(--cell);color:var(--ink);font:1.05rem/1 var(--f-ui);padding:0;cursor:pointer;min-width:0}
.hc.ring{box-shadow:inset 0 0 0 2px var(--ink)}
.tip{margin-top:6px;font:.82rem var(--f-num);color:var(--mute);min-height:1.2em}
.ladder{width:100%;border-collapse:collapse;font:.9rem var(--f-num);font-variant-numeric:tabular-nums}
.ladder td{padding:2px 4px;border-bottom:1px solid var(--line)}
.ladder td:nth-child(2),.ladder td:nth-child(3){text-align:right}
.ladder tr.now td{background:var(--accent);color:var(--card);font-weight:700}
.ladder tr.poc td:first-child,.ladder tr.up td:first-child{color:var(--up)}.ladder tr.down td:first-child{color:var(--down)}
.pl{width:100%;height:auto;display:block}.plx{display:flex;justify-content:space-between;font:.78rem var(--f-num);color:var(--mute)}
.chips{display:flex;flex-wrap:wrap;gap:4px}
.chip{font:.82rem var(--f-num);padding:2px 7px;border-radius:999px;background:var(--cell)}
.up{color:var(--up)}.down{color:var(--down)}.warn{color:var(--warn)}.mute{color:var(--mute)}
.big{font-size:1.1rem;margin:0}
.badge{flex:none;background:var(--warn-bg);color:var(--warn);font:700 .8rem var(--f-num);padding:3px 8px;border-radius:6px}
.note{display:flex;gap:6px;flex:none;align-items:center}
.note input{flex:1;min-width:0;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:6px 8px;font:inherit;font-size:.9rem}
.note button{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:6px 10px;cursor:pointer;font:600 .85rem var(--f-ui)}
.saved{font-size:.8rem;color:var(--up)}
footer{flex:none;font:.85rem var(--f-num);color:var(--mute);padding-block:6px 8px;border-top:1px solid var(--line);margin-top:6px;white-space:nowrap;overflow-x:auto}
footer b{color:var(--ink)}
@media (max-width:760px){.cols{grid-template-columns:minmax(0,1fr)}.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.val{font-size:1.35rem}}
@media (prefers-reduced-motion:no-preference){.hc{transition:transform .08s}.hc:hover{transform:scale(1.15)}}
"""
JS = """
var K='mts_onepage_mock_comments',T='mts_onepage_mock_tab';
function ld(){try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return {}}}
function sv(o){try{localStorage.setItem(K,JSON.stringify(o))}catch(e){}}
var m=ld();document.querySelectorAll('input[id^=c-]').forEach(function(i){i.value=m[i.id.slice(2)]||''});
var tabs=[].slice.call(document.querySelectorAll('[data-tab]'));
function show(id){var b=document.getElementById('tab-'+id);if(!b)return;
 tabs.forEach(function(x){x.classList.remove('on');x.setAttribute('aria-selected','false')});
 document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('on')});
 b.classList.add('on');b.setAttribute('aria-selected','true');document.getElementById('panel-'+id).classList.add('on');
 try{localStorage.setItem(T,id)}catch(e){}}
tabs.forEach(function(b,i){b.onclick=function(){show(b.dataset.tab)};
 b.onkeydown=function(e){var d=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0;if(d){var n=tabs[(i+d+tabs.length)%tabs.length];n.focus();show(n.dataset.tab)}}});
var start=(location.hash||'').slice(1);if(!document.getElementById('tab-'+start)){try{start=localStorage.getItem(T)||''}catch(e){start=''}}
if(start)show(start);
document.querySelectorAll('.hc').forEach(function(c){c.onclick=function(){c.closest('.heat').querySelector('.tip').textContent=c.dataset.tip}});
document.querySelectorAll('[data-save]').forEach(function(b){b.onclick=function(){
 var p=b.dataset.save,o=ld();o[p]=document.getElementById('c-'+p).value;sv(o);document.getElementById('s-'+p).textContent='saved'}});
document.querySelectorAll('[data-copy]').forEach(function(b){b.onclick=function(){
 var o=ld(),t=Object.keys(o).map(function(k){return k+': '+o[k]}).join(String.fromCharCode(10));
 var done=function(){b.textContent='Copied'};
 var fb=function(){var i=b.parentNode.querySelector('input');var v=i.value;i.value=t;i.select();i.value=v;b.textContent='Select + copy'};
 try{navigator.clipboard.writeText(t).then(done,fb)}catch(e){fb()}}});
"""
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap">'
TITLE = 'Live feed one page'
age_chip = (f'<span class="age{" old" if AGE_D >= 1 else ""}" title="newest bar in the repo; not live">'
            f'data {LAST_TS:%Y-%m-%d %H:%M}Z · {AGE_D} d old</span>')
inner = (f'<header><div class="top"><h1>MTS live</h1>{age_chip}<span class="sub">built {NOW:%m-%d %H:%M}Z</span></div>'
         f'<nav class="tabs" role="tablist">{bar}</nav></header><main>{panels}</main><footer>{legend}</footer>'
         f'<script>{JS}</script>')
head = f'<title>{TITLE}</title>{FONTS}<style>{CSS}</style>'
page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        f'{head}</head><body>{inner}</body></html>')
OUT.write_text(page, encoding='utf-8', newline='\n')
if '--fragment' in sys.argv:  # artifact publish copy: the host adds the doctype/head/body skeleton
    frag = f'<meta name="claude:viewport-fit-sides" content="cover">{head}{inner}'
    pathlib.Path(sys.argv[sys.argv.index('--fragment') + 1]).write_text(frag, encoding='utf-8', newline='\n')
print(len(page))
