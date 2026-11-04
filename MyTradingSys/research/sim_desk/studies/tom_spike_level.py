"""Tom spike fade (TOM-1a): fade a rushed push that made a new session extreme, back to where the push started, BTCUSDT or ETHUSDT.

Why: the setup most of his real trades sit in (research/tom_fabio_review_2026-10-31/SETUP_REVIEW.md section 2.1) had no per-trade replay on the
desk; the old Java encodings were run outside DEV or never scored (SETUP_REVIEW.md:77-81).
SOURCED (SETUP_REVIEW.md:65-69): the idea "there's no liquidity left" after a push at the session top (k0zm5NYn0IQ:21-22); stop "above the bell"
(n7ZSkjb7JXs:299-301); target "the entire distance below the start of the impulse" (T6hDJcHrVBM:170-172). The level is the session extreme.
NOT STATED by him: how big a push is, the proof count (zQTbdEweG3c:23-26), the exact entry candle.
OURS: the UTC day as the session (his is 08:30/09:00-17:35 Berlin cash, BTC has none); 5-minute bars; a push = the last N 5m bars span at least K x ATR14
(5m, simple mean of true range) and the bar makes a new high (low) of the day; the "completed auction" proof = a close beyond the spike bar's far side
(below its low for a short) within 3 bars, cancelled if a new extreme prints first; market entry at the next 5m open; stop at the spike extreme, no
buffer, widened to at least 0.40 % of entry (SpikeFadeDetector BTC minimum, TOM_LAYER_V2_SPEC.md:312-324, ours); target the low (high) of the push
window; a trade is closed at the end of the UTC day; Binance fees (fees.py) instead of Deribit.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bars  # noqa: E402

ID = 'tom_spike_level'
TITLE = 'Tom spike fade: a rushed push to a new day extreme, faded back to where it started, BTCUSDT or ETHUSDT'
BAR = 5             # signal bars, minutes (ours)
CONFIRM = 3         # bars allowed for the close back through the spike bar (ours)
MIN_STOP = 0.4      # stop at least this % of entry (ours: SpikeFadeDetector BTC minimum)
SIDES = {'BOTH': 'fade spikes up and spikes down (trader: shorts at the top, longs at the bottom)',
         'SHORT': 'fade spikes up only (trader: his examples are mostly shorts at the session top)',
         'LONG': 'fade spikes down only (ours: the mirror)'}
DEFAULT = {'symbol': 'BTCUSDT', 'sides': 'BOTH', 'n_push': 6, 'k_atr': 4.0, **_bars.FEE_DEFAULT, 'start': '2022-04-01', 'end': '2024-06-30'}


def params():
    return [_bars.SYMBOL_PARAM,
            {'name': 'sides', 'label': 'Which spikes', 'choices': SIDES},
            {'name': 'n_push', 'label': 'Push window, 5m candles (ours: he does not size the push)', 'number': True, 'min': 2, 'max': 24, 'step': 1},
            {'name': 'k_atr', 'label': 'Push size, x ATR14 of 5m candles (ours)', 'number': True, 'min': 1, 'max': 12, 'step': 0.5},
            *_bars.FEE_PARAMS,
            {'name': 'start', 'label': 'From', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'},
            {'name': 'end', 'label': 'To', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'}]


def normalize(p):
    import desk
    q = dict(DEFAULT)
    q.update({k: v for k, v in (p or {}).items() if k in DEFAULT and v not in (None, '')})
    if q['sides'] not in SIDES:
        raise ValueError(f"sides: unknown choice {q['sides']!r}")
    _bars.symbol_of(q)
    for f in params():
        if f.get('number'):
            try:
                v = float(q[f['name']])
            except (TypeError, ValueError):
                raise ValueError(f"{f['label']}: please type a number")
            if not (f['min'] <= v <= f['max']):
                raise ValueError(f"{f['label']}: {v:g} is outside {f['min']}..{f['max']}")
            q[f['name']] = round(v, 6)
    q['n_push'] = int(q['n_push'])
    q['start'], q['end'] = desk.check_dates(str(q['start']), str(q['end']))
    return q


def label(q):
    return (f"{_bars.coin_tag(q)}{q['sides']} push {q['n_push']}x5m >= {q['k_atr']:g} ATR fees {q['maker_pct']:g}/{q['taker_pct']:g}% "
            f"slip {q['slip_pct']:g}% {q['start']}..{q['end']}")


def describe(q):
    return (f"{q['symbol']}, 5m candles, UTC day as the session: when the last {q['n_push']} candles span at least {q['k_atr']:g} x ATR14 and the candle makes "
            f"a new high (low) of the day, wait up to {CONFIRM} candles for a close beyond the spike candle's far side; enter against the push at the next "
            f"candle open, stop at the spike extreme (at least {MIN_STOP:g} % away), target where the push started, out at the end of the UTC day; "
            f"fees {q['maker_pct']:g} % limit / {q['taker_pct']:g} % market, plus {q['slip_pct']:g} % slippage on market and stop fills; "
            f"{q['start']} to {q['end']}, development window only.")


def atr5(a5, n=14):
    """ATR14 of 5m bars, simple mean of true range (FORMULAS 12 style); value at i uses bars up to i."""
    h, l, c = a5[:, 2], a5[:, 3], a5[:, 4]
    pc = np.concatenate([[np.nan], c[:-1]])
    tr = np.fmax(h - l, np.fmax(np.abs(h - pc), np.abs(l - pc)))
    out = np.full(len(a5), np.nan)
    cs = np.cumsum(np.nan_to_num(tr))
    out[n:] = (cs[n:] - cs[:-n]) / n               # bars i-n+1..i, never bar 0 (no previous close)
    return out


def signals(a5, n_push, k_atr, sides):
    """Causal: a signal at bar j uses bars up to j only. {j, side, extreme, start}: side -1 fades a spike up."""
    atr = atr5(a5)
    day = a5[:, 0] // _bars.DAY
    h, l, c = a5[:, 2], a5[:, 3], a5[:, 4]
    want = {'BOTH': (-1, 1), 'SHORT': (-1,), 'LONG': (1,)}[sides]
    out, busy = [], -1
    hi, lo = h[0], l[0]
    for i in range(1, len(a5)):
        if day[i] != day[i - 1]:
            hi, lo = h[i], l[i]
            continue
        new_hi, new_lo = h[i] > hi, l[i] < lo
        hi, lo = max(hi, h[i]), min(lo, l[i])
        w0 = i - n_push + 1
        if i <= busy or w0 < 0 or day[w0] != day[i] or not np.isfinite(atr[i - 1]):
            continue
        for side, new in ((-1, new_hi), (1, new_lo)):
            if not new or side not in want:
                continue
            ext = h[i] if side < 0 else l[i]
            start = l[w0:i + 1].min() if side < 0 else h[w0:i + 1].max()
            if abs(ext - start) < k_atr * atr[i - 1]:
                continue
            far = l[i] if side < 0 else h[i]
            for j in range(i + 1, min(i + CONFIRM, len(a5) - 1) + 1):
                if day[j] != day[i] or (h[j] > ext if side < 0 else l[j] < ext):
                    break                              # a new extreme first: the push is not done
                if side * (c[j] - far) > 0:
                    if side * (start - c[j]) > 0:
                        out.append({'j': j, 'side': side, 'extreme': float(ext), 'start': float(start)})
                        busy = j
                    break
    return out


def run(q, progress=print):
    a = _bars.load_1m(progress, _bars.symbol_of(q))
    a5 = _bars.resample(a, BAR)
    progress('finding spikes on 5m bars')
    sigs = signals(a5, q['n_push'], q['k_atr'], q['sides'])
    bar_ms = BAR * _bars.MIN

    def make(s):
        j, side = s['j'], s['side']
        t0 = int(a5[j, 0]) + bar_ms
        k = int(np.searchsorted(a[:, 0], t0))
        if k >= len(a):
            return None
        entry = float(a[k, 1])                         # the fill run_trade will use
        stop = s['extreme']
        floor = entry * (1 - side * MIN_STOP / 100)
        stop = min(stop, floor) if side > 0 else max(stop, floor)
        if side * (s['start'] - entry) <= 0:
            return None
        t_hold = (t0 // _bars.DAY + 1) * _bars.DAY
        return [side, t0, None, float(stop), float(s['start']), t0 + bar_ms, None, t_hold, s['extreme']]

    progress(f'simulating {len(sigs)} ideas on 1m bars')
    return _bars.collect(sigs, a, q, make)


def chart_trade(ref, q):
    a = _bars.load_1m(symbol=_bars.symbol_of(q))
    tr = _bars.replay(a, ref, q)
    if tr is None or not tr['filled']:
        return None
    out = _bars.chart(a, ref, tr, ref[8])
    out['note'] = ('Spike fade: a rushed push made a new day extreme and closed back through the spike candle; entry against it at the next 5m open; '
                   'stop at the spike extreme (at least 0.4 %); target where the push started')
    return out
