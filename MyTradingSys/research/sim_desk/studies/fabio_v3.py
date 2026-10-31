"""Fabio v3, the price-only parts: Model C (IVB, first-30-minute range breakout) and Model B (failed breakout back into a balance), BTCUSDT.

Why a separate study: the real v3 run needs order-flow bars (delta, big trades, footprint) that start 2024-12-02, after the DEV window,
so it cannot go on the desk. This study runs the same models on 1m klines (price + volume) in the NY window (13:30 or 14:30 UTC + 390 min).
Used UNCHANGED from backtest/layers/fabio/v3: signals.balance (S1 balance: ATR test + POC band, signals.py:183), models.d_and_stop
(D = max(f x entry, structural), cap Dmax; models.py:38), day_gates.ny_open_utc / WINDOW_BARS / ENTRY_CUTOFF (day_gates.py:12-13, :60), costs.TICK.
Rewritten here without order flow (the v3 originals need delta / big-trade fields the klines do not have): the Model B probe and reclaim
(models.py:121-135 with the absorbed-bar test removed) and the Model C breakout bar (models.py:383-421 with S4 off or a candle proxy).
LEFT OUT and shown on the page: Models A and D (they need S2 pressure / S3 absorption = delta, and A also S4 big trades), the S4 big-trade push
(only a candle-direction stand-in, ours), the S3 absorption test inside Model B, S8 order-flow exits, break-even moves (manage.py), the day gate g,
and the resting-limit entry mode (the desk fills market orders at the next bar open: v3's "confirm" mode, models.py:408-421).
A kline POC stands in for the footprint POC: each 1m bar's volume sits at its typical price (OURS), fed to the real signals.balance as a fake fp string.
Model B is scored with a real stop and target on 1m bars (_bars.run_trade); run_v3_l3.py:108-109 scores B as 0 R "unmanaged", which this study does not copy.
SOURCED (research/tom_fabio_review_2026-10-31/SETUP_REVIEW.md section 3): IB is the first 30 minutes of the US open, "the bottom of the first 30 minutes
is giving a lot of value in the direction of the day" (LQvv5xgy_ik, CAT:1396; SETUP_REVIEW.md:178-180); the failed breakout back into value targets
"the other side of the range" and enters on a close back inside (9IliXww64uM, CAT:1252-1285; :161-166). His stop is not stated for either (:179, :164).
OURS (v3 numbers with 0 of 8 grid rows sourced, SETUP_REVIEW.md:134): stop at the IB mid (C) / the probe extreme (B) + 1 tick, floor f (run_v3_l3.py:41 grid
0.3 / 0.5 %), Dmax 1 % (engine.py:17), balance N in {60,120,240} and k_bal 0.8 (run_v3_l3.py:41, signals.py:27), reclaim within 5 candles (models.py:32),
S4 window m in {5,15} (engine.py:19), one try per day, entries until open+329 (day_gates.py:13), time stop at the end of the window, exit by target multiple or
nothing (C) / opposite balance edge (B), BTC instead of NQ/ES, Binance fees and slippage (fees.py) instead of Deribit.
NY holidays: the v3 calendar lists only 2024-12 onward, so every DEV weekday is treated as open (BTC trades through them).
"""
import datetime as dt
import importlib
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bars  # noqa: E402
from MyTradingSys.backtest.layers.fabio.v3.costs import TICK  # noqa: E402
from MyTradingSys.backtest.layers.fabio.v3.day_gates import ENTRY_CUTOFF, MAX_MISSING, WINDOW_BARS, ny_open_utc  # noqa: E402
from MyTradingSys.backtest.layers.fabio.v3.models import RECLAIM_BARS, d_and_stop  # noqa: E402
from MyTradingSys.backtest.layers.fabio.v3.signals import B_PROF, K_BAL, balance  # noqa: E402

ID = 'fabio_v3'
TITLE = 'Fabio v3, price-only parts: Model C (first-30-minute breakout) and Model B (failed breakout), BTCUSDT, NY window'
DMAX = 0.01     # Dmax 1 % of entry (ours, engine.py:17)
IB_LEN = 30     # first 30 minutes (trader, SETUP_REVIEW.md:178)
MODEL = {'C': 'Model C: close beyond the first-30-minute range, trade on in that direction (trader: IVB; stop, target, entry not stated)',
         'B': 'Model B: close outside a balance box, back inside within 5 candles, trade back across it (trader: failed breakout back into value; box is ours)'}
PUSH = {'OFF': 'no push test (ours: big-trade data starts 2024-12, after DEV)',
        'CANDLES': 'most of the last m 1m candles go the same way (ours: stand-in for the big-trade push)'}
EXIT = {'RULE': 'Model B: target the opposite edge of the box (trader: the other side of the range); Model C: no target, hold to window end (v3)',
        'R': 'target at a chosen multiple of risk (ours)'}
DEFAULT = {'model': 'C', 'n_bal': 120, 'm': 15, 'push': 'OFF', 'f_pct': 0.5, 'exit': 'RULE', 'target_r': 2.0,
           **_bars.FEE_DEFAULT, 'start': '2022-04-01', 'end': '2024-06-30'}
N_CHOICES = (60, 120, 240)
M_CHOICES = (5, 15)
_IDEAS = {}
_tv = None


def params():
    return [{'name': 'model', 'label': 'Model', 'choices': MODEL},
            {'name': 'n_bal', 'label': 'Model B: balance window, 1m candles, 60 / 120 / 240 (ours: v3 grid, not his words)', 'number': True, 'min': 60, 'max': 240, 'step': 60},
            {'name': 'm', 'label': 'Model C push window m, 1m candles, 5 or 15 (ours: v3 grid)', 'number': True, 'min': 5, 'max': 15, 'step': 10},
            {'name': 'push', 'label': 'Model C push test', 'choices': PUSH},
            {'name': 'f_pct', 'label': 'Stop floor f, % of entry (ours: v3 grid 0.3 or 0.5)', 'number': True, 'min': 0.1, 'max': 1.0, 'step': 0.1},
            {'name': 'exit', 'label': 'Exit', 'choices': EXIT},
            {'name': 'target_r', 'label': 'Target, x risk, when the exit is a multiple of risk (ours)', 'number': True, 'min': 0.5, 'max': 10, 'step': 0.1},
            *_bars.FEE_PARAMS,
            {'name': 'start', 'label': 'From', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'},
            {'name': 'end', 'label': 'To', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'}]


def normalize(p):
    import desk
    q = dict(DEFAULT)
    q.update({k: v for k, v in (p or {}).items() if k in DEFAULT and v not in (None, '')})
    for k, table in (('model', MODEL), ('push', PUSH), ('exit', EXIT)):
        if q[k] not in table:
            raise ValueError(f'{k}: unknown choice {q[k]!r}')
    for f in params():
        if f.get('number') and not (f['name'] == 'target_r' and q['exit'] != 'R'):
            try:
                v = float(q[f['name']])
            except (TypeError, ValueError):
                raise ValueError(f"{f['label']}: please type a number")
            if not (f['min'] <= v <= f['max']):
                raise ValueError(f"{f['label']}: {v:g} is outside {f['min']}..{f['max']}")
            q[f['name']] = round(v, 6)
    q['n_bal'], q['m'] = int(q['n_bal']), int(q['m'])
    if q['n_bal'] not in N_CHOICES:
        raise ValueError(f"balance window: {q['n_bal']} is not one of {N_CHOICES}")
    if q['m'] not in M_CHOICES:
        raise ValueError(f"push window m: {q['m']} is not one of {M_CHOICES}")
    if q['exit'] != 'R':
        q['target_r'] = None
    q['start'], q['end'] = desk.check_dates(str(q['start']), str(q['end']))
    return q


def label(q):
    ex = f"target {q['target_r']:g}R" if q['exit'] == 'R' else 'rule exit'
    core = f"B N{q['n_bal']}" if q['model'] == 'B' else f"C m{q['m']} push {q['push']}"
    return (f"{core} f{q['f_pct']:g}% {ex} fees {q['maker_pct']:g}/{q['taker_pct']:g}% slip {q['slip_pct']:g}% "
            f"{q['start']}..{q['end']}")


def describe(q):
    ex = f"a target at {q['target_r']:g} x risk" if q['exit'] == 'R' else \
        ('the opposite edge of the balance box' if q['model'] == 'B' else 'no target (held to the end of the window)')
    if q['model'] == 'C':
        idea = (f"in the 390-minute window from the New York open the range of the first {IB_LEN} minutes is the box; at the first 1-minute close beyond its edge "
                f"(push test: {q['push'].lower()}, m {q['m']}) go that way, market entry at the next candle, one try per day, no entry after open+329 min, "
                f"stop at the box middle (floor {q['f_pct']:g} % of entry, dropped if wider than 1 %)")
    else:
        idea = (f"on 1m candles in the same window, find a balance box over the last {q['n_bal']} candles (real v3 test: range under 0.8 x sqrt(N) x ATR and close near the volume peak); "
                f"a close outside it that comes back inside within {RECLAIM_BARS} candles is a failed breakout: trade back the other way at the next candle, "
                f"stop beyond the probe extreme (floor {q['f_pct']:g} % of entry, dropped if wider than 1 %); the order-flow absorption test is left out")
    return (f"BTC / USDT, Fabio v3 price-only: {idea}; exit at {ex}, or at the end of the window; "
            f"fees {q['maker_pct']:g} % limit / {q['taker_pct']:g} % market, plus {q['slip_pct']:g} % slippage on market and stop fills; {q['start']} to {q['end']}, development window only. "
            f"Models A and D, the big-trade push, absorption and order-flow exits need data that starts 2024-12 and are not here.")


# ---- ideas ----
def _volume():
    global _tv
    if _tv is None:
        _tv = importlib.import_module('tom_vp')
    return _tv


def _day_bars(a, o_ms, pre):
    """v3-style bar dicts: `pre` minutes before the open (for the balance look-back) then the 390-minute window; None if the window is short."""
    t = a[:, 0]
    i0 = int(np.searchsorted(t, o_ms))
    i1 = int(np.searchsorted(t, o_ms + WINDOW_BARS * _bars.MIN))
    if i0 >= len(a) or a[i0, 0] != o_ms or (i1 - i0) < WINDOW_BARS - MAX_MISSING:
        return None
    ib = int(np.searchsorted(t, o_ms - pre * _bars.MIN))
    bars = []
    for r in a[ib:i1]:
        tp = (r[2] + r[3] + r[4]) / 3.0
        bars.append({'t': int(r[0]), 'o': float(r[1]), 'h': float(r[2]), 'l': float(r[3]), 'c': float(r[4]),
                     'fp': '%d:%.6f:0.0' % (math.floor(tp / 10.0) * 10, r[5])})   # all volume at the typical price (ours)
    return bars, i0 - ib


def _probe(bars, i0, sb, E, end):
    """('reclaim', j, Xp) | ('timeout', last, Xp) | ('open', end, Xp): models.py:121-135 without the absorbed-bar test."""
    key = 'h' if sb > 0 else 'l'
    Xp = bars[i0][key]
    last = min(i0 + RECLAIM_BARS, end)
    for j in range(i0 + 1, last + 1):
        Xp = max(Xp, bars[j][key]) if sb > 0 else min(Xp, bars[j][key])
        if sb * (bars[j]['c'] - E) < 0:
            return 'reclaim', j, Xp
    if i0 + RECLAIM_BARS <= end:
        return 'timeout', i0 + RECLAIM_BARS, Xp
    return 'open', end, Xp


def _ideas_b(bars, o, n):
    """Every reclaim of the day in time order (the first one whose stop fits Dmax is traded, see run); scan of models.py:325-380."""
    end, cut, out, b = len(bars) - 1, o + ENTRY_CUTOFF - 1, [], o
    while b <= end:
        bal = balance(bars, b - 1, n, K_BAL, B_PROF) if b >= 1 else None
        if bal is None:
            b += 1
            continue
        c = bars[b]['c']
        sb = 1 if c > bal['H'] else (-1 if c < bal['L'] else 0)
        if sb == 0:
            b += 1
            continue
        kind, j, Xp = _probe(bars, b, sb, bal['H'] if sb > 0 else bal['L'], end)
        if kind == 'open':
            break
        if kind == 'timeout':
            b = j + 1
            continue
        if j > cut or j + 1 > end or bars[j + 1]['t'] - bars[j]['t'] != _bars.MIN:
            break
        s = -sb
        entry = bars[j + 1]['o']
        out.append({'t': bars[j]['t'], 'side': s, 'entry': entry, 'struct': abs(Xp - entry) + TICK,
                    'level': bal['H'] if sb > 0 else bal['L'], 'far': bal['H'] if s > 0 else bal['L']})
        b = j + 1
    return out


def _ideas_c(bars, o, m, push):
    """The one Model C attempt of the day (models.py:383-421, confirm mode)."""
    ib = bars[o:o + IB_LEN]
    if len(ib) < IB_LEN:
        return []
    ibh, ibl = max(x['h'] for x in ib), min(x['l'] for x in ib)
    mid = (ibh + ibl) / 2.0
    for b in range(o + IB_LEN, min(o + ENTRY_CUTOFF, len(bars) - 1)):
        for s in (1, -1):
            edge = ibh if s > 0 else ibl
            if not s * (bars[b]['c'] - edge) > 0:
                continue
            if push == 'CANDLES':
                if b - m + 1 < 0 or sum((x['c'] > x['o']) - (x['c'] < x['o']) for x in bars[b - m + 1:b + 1]) * s <= 0:
                    continue
            if bars[b + 1]['t'] - bars[b]['t'] != _bars.MIN:
                return []
            entry = bars[b + 1]['o']
            return [{'t': bars[b]['t'], 'side': s, 'entry': entry, 'struct': s * (entry - mid) + TICK, 'level': edge, 'far': None}]
    return []


def ideas(a, q):
    """[(open_ms, [idea, ...])] for every NY window in DEV, cached per signal setting (the fee, floor and exit boxes do not change signals)."""
    key = (q['model'], q['n_bal'] if q['model'] == 'B' else (q['m'], q['push']))
    if key not in _IDEAS:
        pre = q['n_bal'] + 2 if q['model'] == 'B' else 0
        out = []
        for d in range(_bars.day_ms('2022-04-01') // _bars.DAY, _bars.day_ms('2024-06-30') // _bars.DAY + 1):
            o = ny_open_utc(dt.date(1970, 1, 1) + dt.timedelta(days=d))
            if o is None:
                continue
            o_ms = int(o.timestamp() * 1000)
            got = _day_bars(a, o_ms, pre)
            if got is None:
                continue
            bars, oi = got
            c = _ideas_b(bars, oi, q['n_bal']) if q['model'] == 'B' else _ideas_c(bars, oi, q['m'], q['push'])
            if c:
                out.append((o_ms, c))
        _IDEAS[key] = out
    return _IDEAS[key]


def run(q, progress=print):
    a = _bars.load_1m(progress)
    av = _volume().load_1m_vol(progress)             # volume column for the balance's POC; same bars, one more column
    progress('finding Fabio v3 setups on 1m bars')
    days = ideas(av, q)
    f = q['f_pct'] / 100.0
    sigs = []
    for o_ms, cands in days:
        for c in cands:
            plan = d_and_stop(c['side'], c['entry'], c['struct'], f, DMAX)
            if plan is not None:
                sigs.append(dict(c, o_ms=o_ms, D=plan[0], stop=plan[1]))
                break                                    # one try per day: the first idea whose stop fits
    bar_ms = _bars.MIN

    def make(s):
        side, entry, D = s['side'], s['entry'], s['D']
        if q['exit'] == 'R':
            target = entry + side * q['target_r'] * D
        elif q['model'] == 'B':
            target = s['far']
            if side * (target - entry) <= 0:
                return None
        else:
            target = None
        t0 = s['t'] + bar_ms
        t_hold = s['o_ms'] + WINDOW_BARS * bar_ms
        return [side, t0, None, float(s['stop']), None if target is None else float(target), t0 + bar_ms, None, t_hold, float(s['level'])]

    progress(f'simulating {len(sigs)} ideas on 1m bars')
    return _bars.collect(sigs, a, q, make)


def chart_trade(ref, q):
    a = _bars.load_1m()
    tr = _bars.replay(a, ref, q)
    if tr is None or not tr['filled']:
        return None
    out = _bars.chart(a, ref, tr, ref[8])
    out['note'] = ('Model C: first 1m close beyond the first-30-minute range after the NY open; market entry at the next candle; stop at the range middle'
                   if q['model'] == 'C' else
                   'Model B: close outside the balance box, back inside within 5 candles; market entry at the next candle; stop beyond the probe extreme; target the far edge of the box')
    return out
