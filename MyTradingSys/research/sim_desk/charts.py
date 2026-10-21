"""Six tiny example-trade charts per Run: the 3 winners and 3 losers closest to the median winner / loser.

A study gives chart_trade(ref, q) -> {'bars', 'side', 'level', 'entries', 'stop', 'target', 'exits', 'net_r'}
(bars = 1m dicts of the day; entries/exits = (t_ms, price[, reason])). Drawn as inline SVG 300x160: candles from
30 min before the first entry to 15 min after the last exit (5m, coarser when the trade is long), plus only the
level, entries, stop, target and exit. Built on the fly, never written to disk.
"""
import numpy as np

W, H, PAD_T, PAD_B = 300, 160, 6, 22
MAX_CANDLES = 64
SPANS = (5, 15, 30, 60, 120)
REASON = {'T1': 'hit target', 'X0': 'hit target', 'T2': 'hit second target', 'STOP': 'stopped', 'STOP_LATE': 'stopped after target',
          'TIME': 'closed at day end', 'CVD_AGAINST': 'order flow turned', 'BAND': 'reached opposite band', 'CVD_FLAT': 'order flow went flat'}
RULE = '3 winners and 3 losers closest to the typical (median) winner and loser'


def pick(net, k=3):
    """Indices of the k winners closest to the median winner and the k losers closest to the median loser."""
    net = np.asarray(net, float)
    out = []
    for mask in (net > 0, net < 0):
        idx = np.flatnonzero(mask)
        if idx.size == 0:
            out.append([]); continue
        med = np.median(net[idx])
        out.append([int(i) for i in idx[np.argsort(np.abs(net[idx] - med), kind='stable')][:k]])
    return out[0], out[1]


def _candles(bars, t0, t1):
    span = next((s for s in SPANS if (t1 - t0) / 60000 / s <= MAX_CANDLES), SPANS[-1])
    out = {}
    for b in bars:
        if t0 <= b['t'] <= t1:
            k = b['t'] // (span * 60000)
            c = out.get(k)
            if c is None:
                out[k] = [b['o'], b['h'], b['l'], b['c']]
            else:
                c[1] = max(c[1], b['h']); c[2] = min(c[2], b['l']); c[3] = b['c']
    return span, [out[k] for k in sorted(out)]


def svg(tr):
    t_first = min(t for t, *_ in tr['entries']) if tr['entries'] else tr['bars'][0]['t']
    t_last = max(t for t, *_ in tr['exits']) if tr['exits'] else t_first
    t0, t1 = t_first - 30 * 60000, t_last + 15 * 60000
    span, cs = _candles(tr['bars'], t0, t1)
    prices = [x for c in cs for x in c[1:3]] + [tr['stop'], tr['level']] + ([tr['target']] if tr['target'] else [])
    lo, hi = min(prices), max(prices)
    pad = (hi - lo) * .04 or 1
    lo, hi = lo - pad, hi + pad
    ph = H - PAD_T - PAD_B

    def y(p):
        return PAD_T + (hi - p) / (hi - lo) * ph

    n = max(len(cs), 1)
    cw = W / n

    def x_of(t):
        return (t - (t0 // (span * 60000)) * span * 60000) / (span * 60000) * cw + cw / 2

    wick, up, dn = [], [], []
    for k, (o, h, l_, c) in enumerate(cs):
        xc = k * cw + cw / 2
        wick.append(f'M{xc:.1f} {y(h):.1f}V{y(l_):.1f}')
        top, bot = y(max(o, c)), y(min(o, c))
        (up if c >= o else dn).append(f'M{xc - cw * .35:.1f} {top:.1f}h{cw * .7:.1f}V{max(bot, top + .6):.1f}h{-cw * .7:.1f}Z')
    ex_px, ex_reason = tr['exits'][-1][1], tr['exits'][-1][2]
    caption = f"{tr['net_r']:+.2f} R {'long' if tr['side'] > 0 else 'short'}, {REASON.get(ex_reason, ex_reason.lower())} ({span}m candles)"
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
             f'data-stop="{tr["stop"]!r}" data-exit="{ex_px!r}" data-target="{tr["target"]!r}" data-net="{tr["net_r"]:.4f}">',
             f'<path d="{"".join(wick)}" stroke="#8a8f98" stroke-width="1"/>',
             f'<path d="{"".join(up)}" fill="#9fb8a6"/>', f'<path d="{"".join(dn)}" fill="#c4a3a3"/>']

    def hline(p, color, dash, name):
        parts.append(f'<path d="M0 {y(p):.1f}H{W}" stroke="{color}" stroke-width="1.2"{dash}/>'
                     f'<text x="{W - 2}" y="{y(p) - 2:.1f}" text-anchor="end" font-size="9" fill="{color}">{name}</text>')

    hline(tr['level'], '#6b7280', ' stroke-dasharray="3 3"', 'level')
    hline(tr['stop'], '#c0392b', '', 'stop')
    if tr['target']:
        hline(tr['target'], '#1e8449', '', 'target')
    for t, p in tr['entries']:
        parts.append(f'<circle cx="{x_of(t):.1f}" cy="{y(p):.1f}" r="3.2" fill="#2563eb"/>')
    for t, p, _ in tr['exits']:
        xe, ye = x_of(t), y(p)
        parts.append(f'<path d="M{xe - 3:.1f} {ye - 3:.1f}l6 6m0 -6l-6 6" stroke="#111" stroke-width="1.6"/>')
    color = '#1e8449' if tr['net_r'] > 0 else '#c0392b'
    parts.append(f'<text x="4" y="{H - 7}" font-size="11" font-family="sans-serif" fill="{color}">{caption}</text></svg>')
    return ''.join(parts)


def make(study, q, res):
    """Six chart dicts for one Run (fewer when there are not 3 winners / 3 losers)."""
    if not hasattr(study, 'chart_trade') or not len(res['net']):
        return []
    wins, losses = pick(res['net'])
    out = []
    for kind, idx in (('winner', wins), ('loser', losses)):
        for k in idx:
            ref = res['refs'][k]
            tr = study.chart_trade(ref, q)
            if tr is None:
                continue
            out.append({'kind': kind, 'ref': ref, 'net_r': tr['net_r'], 'svg': svg(tr)})
    return out
