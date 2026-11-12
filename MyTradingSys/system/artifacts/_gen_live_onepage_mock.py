"""Builds LIVE_ONEPAGE_MOCK_2026-11-04.html: the one-screen live feed mock, for operator review.

v4 (operator review 2026-11-04): numbers come from where they are fresh at build time.
- Price, timeframe readings: public Binance spot BTCUSDT klines (data-api.binance.vision, no key).
- Analyst views and levels: the CBP store (cbp.py; rows + verdicts.json beside it), Habib Discord reader log
  (research/analysts/watch/POSTS_LOG.csv).
- Layers: system/LAYERS.md + research/STATUS.md; plain wording from PLAIN below (OURS, one line per layer).
- Backtest box: research/eagle_eyes_picture_2026-10-28/c30_validation_verdict.json.
Readings are context: none of RSI / WaveTrend / trend / price-vs-buying passed a fee-net test alone (STATUS layer pass).
Run: python MyTradingSys/system/artifacts/_gen_live_onepage_mock.py [--fragment OUT] [--offline]
"""
import collections
import csv
import datetime as dt
import html
import json
import pathlib
import re
import sys
import urllib.request

R = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R.parent), str(R)]  # repo root (MyTradingSys.* imports), MyTradingSys (cbp)
OUT = R / 'system/artifacts/LIVE_ONEPAGE_MOCK_2026-11-04.html'
NOW = dt.datetime.now(dt.timezone.utc)
E = html.escape
OFFLINE = '--offline' in sys.argv


def fnum(x, d=0):
    return f'{x:,.{d}f}'


def sgn(x, d=0):
    return f'{x:+,.{d}f}'


def ago(t):
    s = (NOW - t).total_seconds()
    return f'{s / 60:.0f} min' if s < 3600 else f'{s / 3600:.0f} h' if s < 172800 else f'{s / 86400:.0f} d'


def iso(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))


# ---------- live price (public klines) ----------
TFS = [('15m', 200), ('30m', 200), ('1h', 200), ('2h', 200), ('4h', 200), ('1d', 200)]


def klines(interval, limit):
    url = f'https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval={interval}&limit={limit}'
    with urllib.request.urlopen(url, timeout=15) as f:
        raw = json.load(f)
    out = []
    for k in raw:
        close_t = dt.datetime.fromtimestamp(k[6] / 1000, dt.timezone.utc)
        v, tb = float(k[5]), float(k[9])
        out.append({'t': dt.datetime.fromtimestamp(k[0] / 1000, dt.timezone.utc), 'o': float(k[1]), 'h': float(k[2]),
                    'l': float(k[3]), 'c': float(k[4]), 'net': 2 * tb - v, 'closed': close_t <= NOW})
    return out


K = {}
if not OFFLINE:
    try:
        for tf, n in TFS + [('1m', 10), ('5m', 3)]:
            K[tf] = klines(tf, n)
    except Exception as ex:  # no network: the page says so instead of showing old numbers
        K, OFFLINE = {}, True
        print('offline:', ex)
LIVE = bool(K)
if LIVE:
    PX = K['1m'][-1]['c']
    PX_T = min(K['1m'][-1]['t'] + dt.timedelta(minutes=1), NOW)


# ---------- indicators (context only) ----------
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402  (FORMULAS s1, Wilder)


def ema(xs, n):
    a, out = 2 / (n + 1), []
    for x in xs:
        out.append(x if not out else out[-1] + a * (x - out[-1]))
    return out


def wavetrend(bars):
    """PRE_REG_C30.md s1 (LazyBear): hlc3, esa EMA10, d EMA10 |ap-esa|, ci, wt1 EMA21, wt2 SMA4."""
    ap = [(b['h'] + b['l'] + b['c']) / 3 for b in bars]
    esa = ema(ap, 10)
    d = ema([abs(a - e) for a, e in zip(ap, esa)], 10)
    ci = [(a - e) / (0.015 * dd) if dd else 0 for a, e, dd in zip(ap, esa, d)]
    wt1 = ema(ci, 21)
    wt2 = [sum(wt1[max(0, i - 3):i + 1]) / len(wt1[max(0, i - 3):i + 1]) for i in range(len(wt1))]
    return wt1, wt2


def zone(r):
    return 'bull' if r >= 60 else 'bear' if r <= 40 else 'mid'


def tf_read(tf):
    bars = [b for b in K[tf] if b['closed']]
    closes = [b['c'] for b in bars]
    rsi = rsi_core(closes, 14)
    wt1, wt2 = wavetrend(bars)
    e21 = ema(closes, 21)
    z = zone(rsi[-1])
    flip = next((i for i in range(len(rsi) - 2, 14, -1) if rsi[i] is not None and zone(rsi[i]) != z), None)
    side = closes[-1] > e21[-1]
    tflip = next((i for i in range(len(closes) - 2, 21, -1) if (closes[i] > e21[i]) != side), None)
    dot = next((i for i in range(len(wt1) - 1, len(wt1) - 9, -1)
                if wt1[i] > wt2[i] and wt1[i - 1] <= wt2[i - 1] and wt1[i] <= -53), None)
    end = bars[-1]['t']
    return {'tf': tf, 'rsi': rsi[-1], 'zone': z, 'zone_since': bars[flip + 1]['t'] if flip is not None else None,
            'wt': wt1[-1], 'trend_up': side, 'trend_since': bars[tflip + 1]['t'] if tflip is not None else None,
            'dot': bars[dot]['t'] if dot is not None else None, 'bar_end': end}


TF = [tf_read(tf) for tf, _ in TFS] if LIVE else []

# ---------- CBP analysts ----------
import importlib  # noqa: E402
sys.path.insert(0, str(R))
cbp = importlib.import_module('cbp')
try:
    STORE = pathlib.Path(cbp.store_path())
    CBP_ROWS = json.loads(STORE.read_text(encoding='utf-8')).get('rows', [])
    VERDICTS = json.loads((STORE.parent / 'verdicts.json').read_text(encoding='utf-8'))
    STAMP = json.loads((STORE.parent / 'stamp.json').read_text(encoding='utf-8'))
    LOG = (STORE.parent / 'ingestion.log').read_text(encoding='utf-8', errors='replace')
except Exception:
    CBP_ROWS, VERDICTS, STAMP, LOG = [], {}, {}, ''
RUNS = re.findall(r'^cbp: (FAILED|\+\d+ rows)', LOG, re.M)[-8:]
RUN_FAIL = sum(1 for r in RUNS if r == 'FAILED')
CBP_LAST = iso(STAMP['last_run']) if STAMP.get('last_run') else None
VIEWS = {}
for vid, v in VERDICTS.items():
    VIEWS[vid] = {'analyst': v.get('analyst'), 'date': v.get('published'), 'bias': v.get('bias'), 'note': v.get('bottom_summary') or v.get('title', '')}
for r in CBP_ROWS:
    VIEWS[r['video_id']] = {'analyst': r['analyst'], 'date': r['published'], 'bias': r['bias'],
                            'note': (r.get('pointers') or [''])[0]}
POSTS = list(csv.DictReader(open(R / 'research/analysts/watch/POSTS_LOG.csv', encoding='utf-8')))
HABIB_DC = [p for p in POSTS if p['analyst'] == 'Habib' and p['source'] == 'discord']
HABIB_READ = max((iso(p['seen_utc']) for p in HABIB_DC), default=None)


def bias_sym(b):
    b = (b or '').upper()
    return ('▲', 'up') if b.startswith('BULL') else ('▼', 'down') if b.startswith('BEAR') else ('●', 'mute')


# ---------- layers ----------
STATUS = (R / 'research/STATUS.md').read_text(encoding='utf-8')
LAYERS_MD = (R / 'system/LAYERS.md').read_text(encoding='utf-8')
C30 = json.load(open(R / 'research/eagle_eyes_picture_2026-10-28/c30_validation_verdict.json'))


def st(pattern, default='n/a'):
    m = re.search(pattern, STATUS, re.M)
    return m.group(1) if m else default


LAYER_PASS = st(r'^Layer pass: (\d+ of \d+)')
CI_LINE = st(r'^CI green: (.+)$', '')
CI_SHA = CI_LINE.split()[0] if CI_LINE else 'n/a'
STATUS_AT = st(r'^Generated: (.+)$')
STATUS_T = (dt.datetime.fromisoformat(STATUS_AT) - dt.timedelta(hours=5, minutes=30)).replace(tzinfo=dt.timezone.utc) if STATUS_AT != 'n/a' else None  # IST stamp
PAGES_STALE = st(r'^Pages stale: (\d+)')
GATES = re.findall(r'^(tom|fabio|malkan|krown)\s+G(\d)\s+proof [^|]*\| next: ([^(|]+)', STATUS, re.M)
NO_GATE = 'NO GATE MOVED IN 24h' in STATUS
LAYER = collections.OrderedDict()
cur = None
for line in LAYERS_MD.splitlines():
    m = re.match(r'- Layer `([^`]+)`: ([^|]*)', line)
    if m:
        cur = m.group(1)
        LAYER[cur] = {'head': m.group(2).strip(), 'dated': []}
        continue
    m = re.match(r'\s+- (20\d\d-\d\d-\d\d)[^`]*`([^`]+)`: ([^|]*)', line)
    if m and cur:
        LAYER[cur]['dated'].append((m.group(1), m.group(2), m.group(3).strip()))


def vsym(text):
    t = text.lower()
    if 'withdrawn' in t or 'not real' in t or 'unproven' in t:
        return '↩', 'warn'
    if any(k in t for k in ('no edge', 'negative', 'fail', 'no anchor', 'no level', 'not reproduced', 'no validated',
                            'no surviving', 'no cell', '0 pass', 'not supported', 'below buy', 'stop:', 'closed')):
        return '✗', 'down'
    if 'blocked' in t or 'insufficient' in t:
        return '⏸', 'warn'
    if re.search(r'\bpass\b', t) and 'parity' not in t:
        return '✓', 'up'
    return '●', 'mute'


# plain wording, OURS: (whose idea, what it asks in his words-ish, <= 8 words each)
PLAIN = {  # OURS plain wording: layer -> (whose, the idea, why we tested it); results come from LAYERS.md at build
    'tom_core': ('Tom', 'Order-flow setups on BTC 1m', "Tom's main method"),
    'tom_vp_pivot': ('Tom', 'Price returns to volume levels', 'Tom: price comes back to value'),
    'fabio_of': ('Fabio', 'Absorption and CVD entries', 'Fabio trades absorption at levels'),
    'fabio_v3': ('Fabio', 'His full model, version 3', 'test his whole playbook at once'),
    'bb_lvn_triggers': ('Tom+Fabio', 'Bollinger edge + thin-volume level', 'combine both of their triggers'),
    'rsi_levels': ('Malkan', 'RSI 40/60 zones', 'RSI flips mark trend changes'),
    'rsi_divergence': ('Malkan', 'RSI divergence at lows', 'divergence marks bottoms'),
    'cryptocred': ('CryptoCred', 'Range and level rules', 'his range-trading course'),
    'funding_cvd_fade': ('MTS', 'Fade extreme funding', 'crowded funding often reverses'),
    'oi_delta': ('MTS', 'Open interest vs price', 'new positions show who pushes'),
    'session_momentum': ('MTS', 'Follow the session open', 'sessions often trend from open'),
    'session_levels': ('MTS', 'Europe low swept in US', 'common intraday pattern'),
    'volume': ('MTS', 'Volume spikes and direction', 'does big volume pick a side?'),
    'bigtrade_fires': ('MTS', 'Follow very large trades', 'do whales lead price?'),
    'candle_patterns': ('MTS', 'Classic candle patterns', 'textbook signals, checked once'),
    'pitchfork_swing': ('Pizzino', 'Pitchfork swing levels', 'his 4h/1d pitchforks'),
}
RESULT = {'✗': 'no edge', '↩': 'pass taken back', '⏸': 'too little data', '✓': 'passed', '●': 'not profit-tested'}
GATE_NEXT = {}

# ---------- html helpers ----------


def kpi(label, value, sub='', cls=''):
    return (f'<div class="kpi"><span class="lab">{E(label)}</span><span class="val {cls}">{value}</span>'
            f'<span class="sub">{sub}</span></div>')


def kpis(*items):
    return '<div class="kpis">' + ''.join(items) + '</div>'


def act(text, cls='warn'):
    return f'<p class="act {cls}">{text}</p>'


def delta_box(title, lines):
    li = ''.join(f'<li><span class="when">{E(a)}</span><span class="sym {c}">{s}</span><span>{E(b)}</span></li>' for a, s, c, b in lines)
    return f'<div class="box delta"><h3>Δ {E(title)}</h3><ul>{li}</ul></div>'


def ladder(title, levels, ref, ref_label):
    rows_ = sorted(levels + [(ref_label, ref, 'now', '')], key=lambda x: -x[1])
    tr = ''.join(f'<tr class="{c}"><td>{n}</td><td>{fnum(p)}</td><td>{"" if c == "now" else sgn((p / ref - 1) * 100, 2) + "%"}</td></tr>'
                 for n, p, c, _ in rows_)
    return f'<div class="box"><h3>{E(title)}</h3><table class="ladder"><tbody>{tr}</tbody></table></div>'


def table(title, head, rows_, note='', wrap=False):
    th = ''.join(f'<th>{E(h)}</th>' for h in head)
    tr = ''.join('<tr>' + ''.join(f'<td class="{c}">{v}</td>' for v, c in r) + '</tr>' for r in rows_)
    return (f'<div class="box"><h3>{E(title)}</h3><div class="tw"><table class="dtab{" wrap" if wrap else ""}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
            + (f'<p class="how">{note}</p>' if note else '') + '</div>')


def price_line(title, pts):
    w, h, pad = 600, 110, 6
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


def panel(pid, src, body, active=False):
    return (f'<section id="panel-{pid}" class="panel{" on" if active else ""}" role="tabpanel" aria-labelledby="tab-{pid}" data-src="{E(src)}">'
            f'<div class="pbody">{body}</div>'
            f'<div class="note"><input id="c-{pid}" maxlength="140" placeholder="one-line note on this tab" aria-label="note">'
            f'<button data-save="{pid}">Save</button><button data-copy title="copies the note of every tab, to paste into chat">Copy notes</button>'
            f'<span id="s-{pid}" class="saved"></span></div></section>')


def offline_box(what):
    return f'<div class="box"><h3>{E(what)}</h3><p class="big down">No live price at build time</p><p class="sub">re-run the builder online</p></div>'


# ---------- Market now ----------
if LIVE:
    h1 = [b for b in K['1h'] if b['closed']]
    last24 = h1[-24:]
    move24 = (PX / last24[0]['o'] - 1) * 100
    net24 = sum(b['net'] for b in last24)
    lo24 = min(min(b['l'] for b in last24), K['1m'][-1]['l'])
    hi24 = max(max(b['h'] for b in last24), K['1m'][-1]['h'])
    low_bar = min(last24, key=lambda b: b['l'])
    high_before = max((b for b in last24 if b['t'] <= low_bar['t']), key=lambda b: b['h'])
    prior5 = h1[-24 * 6:-24]
    prior5_lo = min(b['l'] for b in prior5)
    drop = (low_bar['l'] / high_before['h'] - 1) * 100
    back = (PX - low_bar['l']) / ((high_before['h'] - low_bar['l']) or 1) * 100
    swept = low_bar['l'] < prior5_lo
    happened = [
        (f'{high_before["t"]:%H}Z', '▼', 'down', f'fell {abs(drop):.1f}% from {fnum(high_before["h"])} to {fnum(low_bar["l"])}'),
        (f'{low_bar["t"]:%H}Z', '⚡' if swept else '●', 'warn' if swept else 'mute',
         f'took out the 5-day low {fnum(prior5_lo)}' if swept else f'held above 5-day low {fnum(prior5_lo)}'),
        ('now', '▲' if back >= 50 else '●', 'up' if back >= 50 else 'mute', f'won back {back:.0f}% of the fall'),
        ('24h', '▲' if net24 >= 0 else '▼', 'up' if net24 >= 0 else 'down', f'net {"bought" if net24 >= 0 else "sold"} {abs(net24):,.0f} BTC'),
    ]
    days = [b for b in K['1d']][-5:]
    drows = []
    for b in days:
        pm = (b['c'] / b['o'] - 1) * 100
        agree = (pm >= 0) == (b['net'] >= 0)
        read = (('▲ buyers pushed it up', 'up') if pm >= 0 else ('▼ sellers pushed it down', 'down')) if agree else \
               (('◇ rose on net selling', 'warn') if pm >= 0 else ('◇ fell despite buying', 'warn'))
        drows.append([(f'{b["t"]:%m-%d}' + (' *' if not b['closed'] else ''), ''),
                      (f'{"▲" if pm >= 0 else "▼"} {sgn(pm, 2)}%', 'up' if pm >= 0 else 'down'),
                      (sgn(b['net']), 'up' if b['net'] >= 0 else 'down'), read])
    d1 = [b for b in K['1d'] if b['closed']]
    monday = (NOW - dt.timedelta(days=NOW.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    wopen = next((b['o'] for b in h1 if b['t'] == monday), None)
    lv = [(f'today high', max(b['h'] for b in h1 if b['t'].date() == NOW.date()), '', ''),
          ('today low', min(b['l'] for b in h1 if b['t'].date() == NOW.date()), '', ''),
          (f'yesterday high {d1[-1]["t"]:%m-%d}', d1[-1]['h'], '', ''), (f'yesterday low', d1[-1]['l'], '', ''),
          ('5-day low (before 24h)', prior5_lo, 'down', '')] + ([('week open (Mon 00:00Z)', wopen, 'poc', '')] if wopen else [])
    market = (kpis(kpi('BTC now', fnum(PX), f'Binance spot · <span data-ts="{PX_T.isoformat()}">{PX_T:%H:%M}Z</span>'),
                   kpi('24h move', f'{"▲" if move24 >= 0 else "▼"} {sgn(move24, 2)}%', f'from {fnum(last24[0]["o"])}', 'up' if move24 >= 0 else 'down'),
                   kpi('24h net bought', f'{"▲" if net24 >= 0 else "▼"} {sgn(net24)}', 'BTC, buys minus sells', 'up' if net24 >= 0 else 'down'),
                   kpi('24h range', fnum(hi24 - lo24), f'{fnum(lo24)} → {fnum(hi24)}'))
              + act(f'{"⚡ Lows swept, then " if swept else ""}{"V-recovery: " if swept and back >= 50 else ""}price won back {back:.0f}% of a {abs(drop):.1f}% fall. '
                    'Open Timeframes to see which charts flipped. Context only, not a trade.')
              + '<div class="cols"><div class="stack">' + delta_box('what just happened (UTC)', happened)
              + price_line('Price, last 5 days (1h closes)', [b['c'] for b in h1[-120:]] + [PX]) + '</div>'
              + '<div class="stack">'
              + table('Who won each day', ['day', 'price', 'net BTC bought', 'read'], drows,
                      '◇ = price and buying disagree: a warning, not a trade (tested alone: no edge). * = today so far.')
              + ladder('Levels vs now', lv, PX, 'now') + '</div></div>')
else:
    market = kpis(kpi('BTC now', '—', 'offline'), kpi('24h move', '—'), kpi('24h net bought', '—'), kpi('24h range', '—')) + delta_box('what just happened', [('—', '○', 'mute', 'no live price at build time')]) + offline_box('Market')

# ---------- Signals: timeframe flips ----------
if LIVE:
    trows = []
    for r in TF:
        zs, zc = {'bull': ('▲ above 60', 'up'), 'bear': ('▼ below 40', 'down'), 'mid': ('● 40-60', 'mute')}[r['zone']]
        wt = r['wt']
        wts, wtc = ('▼ deep low', 'warn') if wt <= -53 else ('▲ stretched high', 'down') if wt >= 53 else ('● middle', 'mute')
        trows.append([(f'<b>{r["tf"]}</b>', ''), (f'{r["rsi"]:.0f} {zs}', zc),
                      (ago(r['zone_since']) if r['zone_since'] else '—', 'mute'),
                      (f'{wt:.0f} {wts}' + (' · buy dot' if r['dot'] else ''), wtc),
                      ('▲ above' if r['trend_up'] else '▼ below', 'up' if r['trend_up'] else 'down'),
                      (ago(r['trend_since']) if r['trend_since'] else '—', 'mute')])
    n_up = sum(r['trend_up'] for r in TF)
    flips = sorted([(r['trend_since'], r['tf'], 'trend', r['trend_up']) for r in TF if r['trend_since']] +
                   [(r['zone_since'], r['tf'], 'RSI ' + r['zone'], r['zone'] == 'bull') for r in TF if r['zone_since']], reverse=True)[:5]
    flip_lines = [(f'{t:%m-%d %H}Z', '▲' if up else '▼', 'up' if up else 'down',
                   f'{tf} {"price crossed above trend line" if kind == "trend" and up else "price crossed below trend line" if kind == "trend" else kind.replace("RSI bull", "RSI went above 60").replace("RSI bear", "RSI went below 40").replace("RSI mid", "RSI back to 40-60")}')
                  for t, tf, kind, up in flips]
    dots = [r['tf'] for r in TF if r['dot']]
    h1c = C30['H1']
    signals = (kpis(kpi('Above trend line', f'{n_up}/{len(TF)}', 'timeframes, 21-bar average', 'up' if n_up * 2 > len(TF) else 'down'),
                    kpi('RSI above 60', f'{sum(r["zone"] == "bull" for r in TF)}/{len(TF)}', 'bull zone (Malkan)', 'up'),
                    kpi('RSI below 40', f'{sum(r["zone"] == "bear" for r in TF)}/{len(TF)}', 'bear zone (Malkan)', 'down'),
                    kpi('Dip-buy dots', ', '.join(dots) if dots else 'none', 'WaveTrend low cross, last 8 bars', 'warn' if dots else 'mute'))
               + act(f'{n_up} of {len(TF)} timeframes are above their trend line. '
                     + ('Short charts turned up first: lower timeframes lead, higher ones confirm later.' if TF[0]['trend_up'] and not TF[-1]['trend_up'] else
                        'All aligned up.' if n_up == len(TF) else 'All aligned down.' if n_up == 0 else 'Mixed: wait for the 2h/4h to agree.')
                     + ' None of these passed a profit test alone.')
               + '<div class="cols"><div class="stack">'
               + table('Timeframes now (closed candles)', ['chart', 'RSI 14', 'zone since', 'WaveTrend', 'vs trend', 'since'], trows,
                       'Trend line = 21-candle average. WaveTrend ≤ -53 = deep low, where the dip-buy rule looks.')
               + '</div><div class="stack">' + delta_box('latest flips', flip_lines)
               + '<div class="box"><h3>Dip-buy rule, past test</h3><ul class="means">'
               + f'<li><span class="sym down">✗</span>30m dip-buy (WaveTrend low + RSI divergence): {h1c["n"]} trades in 2024-07→2025-06, {h1c["win"]:.0f}% won, avg {sgn(h1c["mean"], 2)}% after fees. Loses alone.</li>'
               + f'<li><span class="sym warn">?</span>Same on 15m when 2h trend is up: avg {sgn(C30["H2"]["mean"], 2)}%, {C30["H2"]["n"]} trades. Not proven.</li>'
               + '</ul></div></div></div>')
else:
    signals = kpis(kpi('Above trend line', '—'), kpi('RSI above 60', '—'), kpi('RSI below 40', '—')) + delta_box('latest flips', [('—', '○', 'mute', 'offline')]) + offline_box('Timeframes')

# ---------- Positions (testnet) ----------
positions = (kpis(kpi('Open trades', '—', 'not visible here'), kpi('Testnet P&L', '—', 'not visible here'), kpi('Stops set', '—', 'not visible here'))
             + act('Testnet trades run on the Lenovo laptop (desktop-f7iu69n). This page has no copy of them yet, so it shows nothing rather than guess.', 'mute')
             + '<div class="cols"><div class="stack">' + delta_box('what will show here once wired', [
                 ('entry', '▲', 'up', 'each new trade, side, size, price'),
                 ('stop', '◆', 'warn', 'every stop move, distance from price'),
                 ('exit', '✓', 'mute', 'result after fees, why it closed')])
             + '</div><div class="stack"><div class="box"><h3>To wire it</h3><p class="sub">live_mirror.py brief on the laptop, copied here read-only (LIVE_MIRROR.md). No order data enters the public repo.</p></div></div></div>')

# ---------- News & calls ----------
by_an = collections.defaultdict(list)
for v in VIEWS.values():
    if v['analyst'] and v['date']:
        by_an['Habib' if v['analyst'] == 'Qriptal' else v['analyst']].append(v)
dates = sorted({v['date'] for v in VIEWS.values() if v['date']})[-8:]
grid_rows = []
for an in sorted(by_an, key=lambda a: max(v['date'] for v in by_an[a]), reverse=True):
    cells = []
    for d in dates:
        vs = [v for v in by_an[an] if v['date'] == d]
        if vs:
            s, c = bias_sym(vs[-1]['bias'])
            cells.append((f'<span title="{E(vs[-1]["note"][:120])}">{s}</span>', c))
        else:
            cells.append(('·', 'mute'))
    last_d = max(v['date'] for v in by_an[an])
    grid_rows.append([(f'<b>{E(an)}</b>', '')] + cells + [(f'{(NOW.date() - dt.date.fromisoformat(last_d)).days} d', 'mute')])
n_bear = sum(1 for a in by_an if bias_sym(sorted(by_an[a], key=lambda v: v['date'])[-1]['bias'])[1] == 'down')
n_bull = sum(1 for a in by_an if bias_sym(sorted(by_an[a], key=lambda v: v['date'])[-1]['bias'])[1] == 'up')
newest = sorted(VIEWS.values(), key=lambda v: v['date'] or '', reverse=True)[:4]
an_lines = [(v['date'][5:], *bias_sym(v['bias']), f'{v["analyst"]}: {" ".join((v["note"] or "").split()[:9])}') for v in newest]
LV = []
if LIVE:
    for r in CBP_ROWS:
        exp = r.get('expires_at')
        if exp and iso(exp) < NOW:
            continue
        for p in r.get('pointers') or []:
            for m in re.finditer(r'\$?(\d{2,3}(?:,\d{3})|\d{2,3}(?:\.\d)?\s?[kK]\b)', p):
                raw = m.group(1).replace(',', '').replace(' ', '')
                val = float(raw[:-1]) * 1000 if raw[-1] in 'kK' else float(raw)
                if 40000 < val < 200000 and abs(val / PX - 1) < 0.12:
                    s, c = bias_sym(r['bias'])
                    LV.append((f'{s} {E(r["analyst"])} {r["published"][5:]}', val, c, ''))
    LV = sorted({(n, v): (n, v, c, x) for n, v, c, x in LV}.values(), key=lambda x: abs(x[1] - PX))[:8]
news = (kpis(kpi('Analysts heard', f'{len(by_an)}', f'CBP, last {len(dates)} video days'),
             kpi('Leaning down', f'▼ {n_bear}', f'▲ {n_bull} up · rest neutral', 'down' if n_bear > n_bull else 'up'),
             kpi('CBP last sync', ago(CBP_LAST) if CBP_LAST else '—', f'{RUN_FAIL} of {len(RUNS)} runs failed', 'down' if RUN_FAIL else 'up'),
             kpi('Habib Discord', ago(HABIB_READ) + ' ago' if HABIB_READ else '—', f'last read · {len(HABIB_DC)} posts logged', 'down' if HABIB_READ and (NOW - HABIB_READ).days >= 1 else 'up'))
        + act(f'Most analysts lean {"down" if n_bear > n_bull else "up"}. Their levels near price are in the ladder. '
              + ('Habib posts are not being read: the Discord reader last ran ' + ago(HABIB_READ) + ' ago.' if HABIB_READ and (NOW - HABIB_READ).days >= 1 else ''))
        + '<div class="cols"><div class="stack">'
        + table('Analyst bias by video day', ['analyst'] + [d[5:] for d in dates] + ['last'], grid_rows,
                '▲ bullish · ▼ bearish · ● neutral or no view · hover a symbol for what he said')
        + '<div class="box"><h3>How we judge Habib</h3><ul class="means">'
        + '<li><span class="sym up">✓</span>10-18 plan: sweep the low, then push up. It happened (checked on Binance 15m).</li>'
        + '<li><span class="sym warn">?</span>9 older plan calls (07-14 → 09-22) are kept sealed for a fair test; opening them needs your OK.</li>'
        + '<li><span class="sym mute">●</span>We score his plans, not his trades: your view is good ideas, weak execution.</li>'
        + '</ul></div></div><div class="stack">' + delta_box('newest views', an_lines)
        + (ladder('Analyst levels near price', LV, PX, 'now') if LV else '')
        + '</div></div>')

# ---------- Layers ----------
lrows = []
for n_, g_, nx_ in GATES:
    GATE_NEXT[n_] = 'live check (G3)' if 'live validation' in nx_.lower() else ' '.join(nx_.split()[:4])
FAM = {'Tom': 'tom', 'Fabio': 'fabio', 'Malkan': 'malkan', 'Tom+Fabio': 'tom'}
for name, (who, what, why) in PLAIN.items():
    if name not in LAYER:
        continue
    L = LAYER[name]
    newest_ = max(L['dated'], default=None)
    s_, c_ = vsym(L['head'] + ' ' + (newest_[2] if newest_ else ''))
    raw = re.sub(r'[`*"]', '', L['head'] + (' | ' + newest_[0] + ' ' + newest_[2] if newest_ else ''))
    nxt = GATE_NEXT.get(FAM.get(who), 'parked') if s_ != '↩' else 'retest needed'
    lrows.append([(E(who), 'mute'), (E(what), ''), (E(why), 'mute'),
                  (f'<span title="{E(raw[:200])}">{s_} {RESULT[s_]}</span>', c_), ((newest_[0][5:] if newest_ else '—'), 'mute'), (E(nxt), 'mute')])
gate_lines = [(f'{n} G{g}/3', '●', 'warn', 'next: ' + ' '.join(nx.split()[:6])) for n, g, nx in GATES]
recent = sorted({(x[0], n, x[2]) for n, v in LAYER.items() for x in v['dated']}, reverse=True)[:4]
rl = [(d[5:], *vsym(t), f'{PLAIN.get(n, (n, n, n))[1]}: {RESULT[vsym(t)[0]]}') for d, n, t in recent]
layers = (kpis(kpi('Ideas tested', f'{len(LAYER)}', 'one per layer'),
               kpi('Profitable after fees', LAYER_PASS.replace(' of ', ' / '), 'rows standing', 'down'),
               kpi('Analysts at proof level', f'G{min(int(g) for _, g, _ in GATES)}' if GATES else '—', 'of 3 (G3 = live check)', 'warn'))
          + act('No idea has made money after fees on its own yet. Next step is the same for all four analysts: '
                'check their setups live, drawn on the chart (G3).')
          + '<div class="cols"><div class="stack">'
          + table('What we tested, why, and what happened', ['whose', 'the idea', 'why we tested it', 'result', 'last', 'next'], lrows,
                  'No edge = lost money or no gain after fees. Hover a result for the full verdict. Parked = nothing planned.', wrap=True)
          + '</div><div class="stack">' + delta_box('analyst proof level and next step', gate_lines)
          + delta_box('newest results', rl) + '</div></div>')

# ---------- Health ----------
feeds = []
if LIVE:
    feeds.append(('Binance price', PX_T, 1))
feeds += [('CBP YouTube sync', CBP_LAST, 13), ('Habib Discord reader', HABIB_READ, 13)]
try:
    of_last = max((R / 'runtime/orderflow_live').glob('20*.csv'))
    feeds.append(('Order-flow file (this PC)', dt.datetime.fromisoformat(of_last.stem).replace(tzinfo=dt.timezone.utc) + dt.timedelta(days=1), 24))
except ValueError:
    pass
if STATUS_T:
    feeds.append(('Dev status report', STATUS_T, 6))
frows = [[(E(n), ''), (('✓ fresh' if t and (NOW - t).total_seconds() < h * 3600 else '✗ stale'), 'up' if t and (NOW - t).total_seconds() < h * 3600 else 'down'),
          (ago(t) if t else '—', 'mute'), (f'≤ {h} h', 'mute')] for n, t, h in feeds]
stale_n = sum(1 for r in frows if r[1][1] == 'down')
health = (kpis(kpi('Data feeds stale', f'{stale_n}/{len(frows)}', 'see table', 'down' if stale_n else 'up'),
               kpi('CBP runs failed', f'{RUN_FAIL}/{len(RUNS)}', 'last 8 sync runs', 'down' if RUN_FAIL else 'up'),
               kpi('Code tests (CI)', 'green?' if CI_SHA != 'n/a' else 'red', f'{CI_SHA[:9]} · report {ago(STATUS_T) if STATUS_T else "?"} old', 'warn'),
               kpi('Pages out of date', PAGES_STALE, 'need republish', 'warn' if PAGES_STALE != '0' else 'up'))
          + act(f'{stale_n} feed(s) stale. CBP sync fails often and the Habib Discord reader has not run since '
                f'{HABIB_READ:%m-%d}.' if HABIB_READ else f'{stale_n} feed(s) stale.', 'down' if stale_n else 'up')
          + '<div class="cols"><div class="stack">' + table('Is each feed running?', ['feed', 'state', 'last', 'expected'], frows) + '</div>'
          + '<div class="stack">' + delta_box('work state', [('24h', '✗' if NO_GATE else '✓', 'down' if NO_GATE else 'up',
                                                                'no analyst moved a proof level' if NO_GATE else 'an analyst proof level moved'),
                                                               ('CI', '●', 'warn', (CI_LINE.split(':')[-1].strip() or 'see STATUS')[:48])])
          + '</div></div>')

# ---------- page ----------
TABS = [('market', 'Market now', '◉', 'up' if LIVE else 'down', 'Binance public klines', market),
        ('signals', 'Timeframes', '⚑', 'warn', 'Binance klines + c30 json', signals),
        ('positions', 'Positions/testnet', '◧', 'mute', 'none on this PC', positions),
        ('news', 'Analysts & calls', '✉', 'down' if RUN_FAIL else 'up', 'CBP store + POSTS_LOG.csv', news),
        ('layers', 'Layers', '▤', 'down', 'LAYERS.md + STATUS.md', layers),
        ('health', 'Health', '✚', 'down' if stale_n else 'up', 'feeds + STATUS.md', health)]
bar = ''.join(f'<button role="tab" id="tab-{t[0]}" data-tab="{t[0]}" aria-controls="panel-{t[0]}" class="{"on" if i == 0 else ""}">'
              f'<span class="ti">{t[2]}</span>{E(t[1])}<i class="dot {t[3]}"></i></button>' for i, t in enumerate(TABS))
panels = ''.join(panel(t[0], t[4], t[5], i == 0) for i, t in enumerate(TABS))
if LIVE:
    m1 = K['1m'][-2]
    m5 = K['5m'][-2]
    near = min((lv for lv in (LV or [])), key=lambda x: abs(x[1] - PX), default=None)
    legend = (f'<b>1m</b> {fnum(m1["c"])} {sgn((m1["c"] / m1["o"] - 1) * 100, 2)}% net {sgn(m1["net"], 1)} · '
              f'<b>5m</b> {sgn((m5["c"] / m5["o"] - 1) * 100, 2)}% net {sgn(m5["net"])} BTC'
              + (f' · <b>level</b> {fnum(near[1])} ({sgn((near[1] / PX - 1) * 100, 2)}%)' if near else ''))
    age = f'<span class="age" data-ts="{PX_T.isoformat()}">price {PX_T:%m-%d %H:%M}Z</span>'
else:
    legend = '<b>1m</b> — · <b>5m</b> — (offline at build)'
    age = '<span class="age old">offline: no live price</span>'

CSS = """
/* layout: header (name, data-age chip, tabs) / one panel = KPI row, action line, then two columns / note row / 1m|5m legend */
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
.top h1{font-size:1.05rem;margin:0;font-weight:700}
.age{font:700 .8rem var(--f-num);padding:2px 8px;border-radius:999px;background:var(--up-bg);color:var(--up)}
.age.old{background:var(--down);color:var(--card)}
.tabs{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none}
.tabs button{flex:none;display:flex;align-items:center;gap:6px;background:var(--card);color:var(--ink);border:1px solid var(--line);
border-radius:8px;padding:7px 11px;font:600 .95rem var(--f-ui);cursor:pointer;white-space:nowrap}
.tabs button.on{background:var(--accent);border-color:var(--accent);color:var(--card)}
.tabs button:focus-visible,.note button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.ti{font-size:1.1rem;line-height:1}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;background:var(--mute)}
.dot.up{background:var(--up)}.dot.down{background:var(--down)}.dot.warn{background:var(--warn)}
main{flex:1;min-height:0;position:relative}
.panel{display:none;height:100%;flex-direction:column;gap:8px}.panel.on{display:flex}
.pbody{flex:1;min-height:0;overflow:auto;display:flex;flex-direction:column;gap:8px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(10rem,1fr));gap:8px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 10px;display:flex;flex-direction:column;min-width:0}
.lab{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);font-weight:600}
.val{font:700 1.6rem/1.15 var(--f-num);font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sub{font-size:.85rem;color:var(--mute);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.act{margin:0;padding:8px 12px;border-radius:10px;font-weight:600;font-size:.98rem;background:var(--warn-bg)}
.act.up{background:var(--up-bg);color:var(--ink)}.act.down{background:var(--down-bg);color:var(--ink)}.act.warn{color:var(--ink)}.act.mute{background:var(--cell);color:var(--ink)}
.cols{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:8px;align-items:start}
.stack{display:flex;flex-direction:column;gap:8px;min-width:0}
.box{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 10px;min-width:0}
.box h3{margin:0 0 6px;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--mute)}
.delta ul{list-style:none;margin:0;padding:0;font:.9rem/1.5 var(--f-num)}
.delta li{display:grid;grid-template-columns:minmax(3.4rem,max-content) 1.5rem 1fr;column-gap:4px;align-items:baseline;border-bottom:1px dashed var(--line)}
.delta li:last-child{border-bottom:0}
.when{color:var(--mute)}.sym{font-size:1.15rem;text-align:center}
.tw{overflow-x:auto}
.dtab{width:100%;border-collapse:collapse;font:.9rem var(--f-num);font-variant-numeric:tabular-nums}
.dtab th{font:600 .72rem var(--f-ui);text-transform:uppercase;letter-spacing:.05em;color:var(--mute);text-align:left;padding:2px 4px;white-space:nowrap}
.dtab td{padding:3px 4px;border-bottom:1px solid var(--line);white-space:nowrap}
.dtab.wrap td:nth-child(2),.dtab.wrap td:nth-child(3){white-space:normal}.dtab.wrap td{padding-block:2px}
.how{margin:6px 0 0;font-size:.82rem;color:var(--mute)}
.means{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px;font-size:.92rem}
.means li{display:grid;grid-template-columns:1.6rem 1fr;align-items:baseline}
.ladder{width:100%;border-collapse:collapse;font:.9rem var(--f-num);font-variant-numeric:tabular-nums}
.ladder td{padding:2px 4px;border-bottom:1px solid var(--line)}
.ladder td:nth-child(2),.ladder td:nth-child(3){text-align:right}
.ladder tr.now td{background:var(--accent);color:var(--card);font-weight:700}
.ladder tr.poc td:first-child,.ladder tr.up td:first-child{color:var(--up)}.ladder tr.down td:first-child{color:var(--down)}
.pl{width:100%;height:auto;display:block}.plx{display:flex;justify-content:space-between;font:.78rem var(--f-num);color:var(--mute)}
.up{color:var(--up)}.down{color:var(--down)}.warn{color:var(--warn)}.mute{color:var(--mute)}
.big{font-size:1.1rem;margin:0}
.note{display:flex;gap:6px;flex:none;align-items:center}
.note input{flex:1;min-width:0;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:6px 8px;font:inherit;font-size:.9rem}
.note button{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:6px 10px;cursor:pointer;font:600 .85rem var(--f-ui)}
.saved{font-size:.8rem;color:var(--up)}
footer{flex:none;font:.85rem var(--f-num);color:var(--mute);padding-block:6px 8px;border-top:1px solid var(--line);margin-top:6px;white-space:nowrap;overflow-x:auto}
footer b{color:var(--ink)}
@media (max-width:760px){.cols{grid-template-columns:minmax(0,1fr)}.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.val{font-size:1.35rem}}
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
function age(){document.querySelectorAll('.age[data-ts]').forEach(function(a){var mins=Math.round((Date.now()-Date.parse(a.dataset.ts))/60000);
 var txt=mins<90?mins+' min old':mins<2880?Math.round(mins/60)+' h old':Math.round(mins/1440)+' d old';
 a.textContent='price '+a.dataset.ts.slice(5,16).replace('T',' ')+'Z · '+txt;a.classList.toggle('old',mins>60)})}
age();setInterval(age,60000);
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
inner = (f'<header><div class="top"><h1>MTS live</h1>{age}<span class="sub">built {NOW:%m-%d %H:%M}Z · snapshot, re-run to refresh</span></div>'
         f'<nav class="tabs" role="tablist">{bar}</nav></header><main>{panels}</main><footer>{legend}</footer>'
         f'<script>{JS}</script>')
head = f'<title>{TITLE}</title>{FONTS}<style>{CSS}</style>'
page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        f'{head}</head><body>{inner}</body></html>')
OUT.write_text(page, encoding='utf-8', newline='\n')
if '--fragment' in sys.argv:  # artifact publish copy: the host adds the doctype/head/body skeleton
    frag = f'<meta name="claude:viewport-fit-sides" content="cover">{head}{inner}'
    pathlib.Path(sys.argv[sys.argv.index('--fragment') + 1]).write_text(frag, encoding='utf-8', newline='\n')
print(len(page), 'live' if LIVE else 'offline')
try:  # name the page this build feeds (registry producer 'live_onepage'): a session republishes it
    sys.path.insert(0, str(R.parent / 'scripts' / 'dev'))
    import artifacts
    for _l in artifacts.producer_lines(artifacts.load(), 'live_onepage'):
        print(_l)
except Exception as _e:  # noqa: BLE001
    print('republish note failed:', _e)
