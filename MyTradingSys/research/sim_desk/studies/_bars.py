"""Shared parts for bar-based studies (rsi, wavetrend): 1m bars (BTCUSDT, ETHUSDT), resampling, and one trade on 1m bars.

Not a study (the leading _ keeps the desk from loading it). Bars are read from the 1m CSVs once and kept as .npy
under sim_desk/cache/bars/ (gitignored). Columns: open time ms, open, high, low, close.
"""
import datetime as dt
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]                     # sim_desk/
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.fees import BINANCE_MAKER, BINANCE_TAKER  # noqa: E402

ROOT = Path(os.environ.get('SIM_DESK_KLINES', 'F:/MTS/data/tom_raw/klines'))
BAR_CACHE = HERE / 'cache' / 'bars'
MIN, DAY = 60000, 86400000
WARMUP_FROM = '2022-01'       # indicator warm-up only; trades start inside the DEV window
LAST_MONTH = '2024-06'        # DEV ends 2024-06-30: nothing later is ever read
FEE_DEFAULT = {'maker_pct': BINANCE_MAKER * 100, 'taker_pct': BINANCE_TAKER * 100}
FEE_PARAMS = [{'name': 'maker_pct', 'label': 'Limit fee, %', 'number': True, 'min': 0.0, 'max': 1.0, 'step': 0.001},
              {'name': 'taker_pct', 'label': 'Market fee, %', 'number': True, 'min': 0.0, 'max': 1.0, 'step': 0.001}]


def _months(first, last):
    y, m = map(int, first.split('-'))
    out = []
    while f'{y:04d}-{m:02d}' <= last:
        out.append(f'{y:04d}-{m:02d}')
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


SYMBOLS = {'BTCUSDT': 'BTC / USDT (ours)', 'ETHUSDT': 'ETH / USDT (ours)'}
SYMBOL_PARAM = {'name': 'symbol', 'label': 'Coin', 'choices': SYMBOLS}


def data_ready(symbol='BTCUSDT'):
    return all((ROOT / f'{symbol}-1m-{m}.csv').exists() for m in _months(WARMUP_FROM, LAST_MONTH))


def symbol_of(q):
    s = (q or {}).get('symbol') or 'BTCUSDT'
    if s not in SYMBOLS:
        raise ValueError(f'symbol: unknown choice {s!r}')
    return s


def coin_tag(q):
    """Label suffix: empty for BTC so the existing ledger rows keep their names."""
    s = symbol_of(q)
    return '' if s == 'BTCUSDT' else f' {s}'


def _month(m, symbol='BTCUSDT'):
    f = BAR_CACHE / f'{symbol}-1m-{m}.npy'
    if f.exists():
        return np.load(f)
    src = ROOT / f'{symbol}-1m-{m}.csv'
    if not src.exists():
        raise FileNotFoundError(src)
    with open(src, encoding='utf-8') as fh:
        skip = 0 if fh.readline()[:1].isdigit() else 1
    a = np.loadtxt(src, delimiter=',', skiprows=skip, usecols=(0, 1, 2, 3, 4), ndmin=2)
    a = a[np.unique(a[:, 0], return_index=True)[1]]
    BAR_CACHE.mkdir(parents=True, exist_ok=True)
    np.save(f, a)
    return a


_ALL = {}


def load_1m(progress=None, symbol='BTCUSDT'):
    """All 1m bars from the warm-up month to the end of DEV, sorted, no duplicates."""
    if symbol not in SYMBOLS:
        raise ValueError(f'symbol: unknown choice {symbol!r}')
    if symbol not in _ALL:
        parts = []
        for m in _months(WARMUP_FROM, LAST_MONTH):
            if progress:
                progress(f'reading 1m bars {m}')
            parts.append(_month(m, symbol))
        a = np.concatenate(parts)
        a = a[np.argsort(a[:, 0], kind='stable')]
        assert a[-1, 0] < (dt.date(2024, 7, 1) - dt.date(1970, 1, 1)).days * DAY, 'read past DEV'
        _ALL[symbol] = a
    return _ALL[symbol]


def resample(a, tf_min):
    """UTC-aligned bars of tf_min minutes: (open time, open, high, low, close); missing minutes are simply absent."""
    k = (a[:, 0] // (tf_min * MIN)).astype(np.int64)
    starts = np.flatnonzero(np.r_[True, k[1:] != k[:-1]])
    ends = np.r_[starts[1:], len(a)] - 1
    return np.column_stack([k[starts] * tf_min * MIN, a[starts, 1], np.maximum.reduceat(a[:, 2], starts),
                            np.minimum.reduceat(a[:, 3], starts), a[ends, 4]])


def day_ms(iso):
    return (dt.date.fromisoformat(iso) - dt.date(1970, 1, 1)).days * DAY


def run_trade(a, side, t_from, trig, stop, target, t_window_end, t_exit, t_hold_end, taker, maker):
    """One trade on 1m bars `a` from time t_from.

    Entry: trig None = market at the open of the first bar at or after t_from; else a stop order at trig valid
    until t_window_end (fill = trig, or the bar open when price gaps through it). Exits, first one wins: stop (fills
    at the stop, or the open on a gap; on the fill bar only the stop is checked; stop before target on one bar),
    target (limit, maker fee), t_exit (signal exit at the close of the bar before it), t_hold_end (time-out, same).
    Returns None when the trade is still open at the end of the data; filled False when the entry never happened."""
    t = a[:, 0]
    i = int(np.searchsorted(t, t_from))
    nofill = {'filled': False, 'net_r': 0., 'gross_r': 0., 'fee_r': 0.}
    if i >= len(a):
        return None
    if trig is None:
        j, px = i, a[i, 1]
    else:
        w = int(np.searchsorted(t, t_window_end))
        seg = a[i:w]
        hit = np.flatnonzero(seg[:, 2] >= trig) if side > 0 else np.flatnonzero(seg[:, 3] <= trig)
        if not hit.size:
            return None if w >= len(a) else nofill
        j = i + int(hit[0])
        px = max(trig, a[j, 1]) if side > 0 else min(trig, a[j, 1])
    risk = side * (px - stop)
    if risk <= 0:
        return nofill                       # the stop would be on the wrong side of the fill: no trade
    t_end = min(x for x in (t_exit, t_hold_end) if x is not None)
    e = int(np.searchsorted(t, t_end))      # bars before t_end belong to the trade
    seg = a[j:e]
    stop_hit = (seg[:, 3] <= stop) if side > 0 else (seg[:, 2] >= stop)
    tgt_hit = np.zeros(len(seg), bool)
    if target is not None:
        tgt_hit = (seg[:, 2] >= target) if side > 0 else (seg[:, 3] <= target)
        tgt_hit[0] = False
    first = np.flatnonzero(stop_hit | tgt_hit)
    if first.size:
        k = int(first[0])
        if stop_hit[k]:
            o = seg[k, 1]
            ex = (o if (o < stop if side > 0 else o > stop) else stop, 'STOP', taker)
        else:
            ex = (target, 'T1', maker)
        ex_t = seg[k, 0]
    else:
        if e >= len(a) and a[-1, 0] < t_end - MIN:
            return None                     # the data ends before the trade does
        ex_t = a[e - 1, 0]
        ex = (a[e - 1, 4], 'SIGNAL' if t_exit is not None and t_exit <= t_hold_end else 'HOLD', taker)
    gross = side * (ex[0] - px) / risk
    fee = (taker * px + ex[2] * ex[0]) / risk
    return {'filled': True, 'entry': (int(a[j, 0]), float(px)), 'stop': float(stop), 'target': target,
            'exit': (int(ex_t), float(ex[0]), ex[1]), 'gross_r': float(gross), 'fee_r': float(fee),
            'net_r': float(gross - fee), 'side': side}


def chart(a, ref, tr, level):
    """The trade in the desk's chart shape (charts.svg)."""
    j0 = int(np.searchsorted(a[:, 0], tr['entry'][0] - 3 * DAY))
    j1 = int(np.searchsorted(a[:, 0], tr['exit'][0] + DAY))
    bars = [{'t': int(r[0]), 'o': r[1], 'h': r[2], 'l': r[3], 'c': r[4]} for r in a[j0:j1]]
    return {'bars': bars, 'side': tr['side'], 'level': level, 'entries': [tr['entry']], 'stop': tr['stop'],
            'target': tr['target'], 'exits': [tr['exit']], 'net_r': tr['net_r']}


def collect(signals, a, q, make):
    """Run signals in time order, one position at a time. make(sig) -> (side, t_from, trig, stop, target,
    t_window_end, t_exit, t_hold_end, level). Returns the desk's result dict; refs replay a trade exactly."""
    taker, maker = q['taker_pct'] / 100, q['maker_pct'] / 100
    lo, hi = day_ms(q['start']), day_ms(q['end']) + DAY
    out = {k: [] for k in ('day', 'touch_t', 'side', 'net', 'gross', 'fees', 'filled', 'refs')}
    busy_until = -1
    for s in signals:
        ref = make(s)
        if ref is None or not (lo <= ref[1] < hi) or ref[1] < busy_until:
            continue
        if ref[7] >= hi:
            ref = ref[:7] + [hi] + ref[8:]        # a trade never runs past the chosen end date
            if ref[6] is not None and ref[6] > hi:
                ref[6] = None
        r = run_trade(a, *ref[:8], taker, maker)
        if r is None:
            continue
        if r['filled']:
            busy_until = r['exit'][0] + MIN
        out['day'].append(ref[1] // DAY)
        out['touch_t'].append(ref[1])
        out['side'].append(int(ref[0]))
        out['net'].append(r['net_r']); out['gross'].append(r['gross_r']); out['fees'].append(r['fee_r'])
        out['filled'].append(r['filled'])
        out['refs'].append(ref)
    res = {k: np.array(v, dtype=np.int64 if k in ('day', 'touch_t', 'side') else bool if k == 'filled' else float)
           for k, v in out.items() if k != 'refs'}
    res['refs'] = out['refs']
    res['all_days'] = list(range(lo // DAY, hi // DAY))
    return res


def replay(a, ref, q):
    return run_trade(a, *ref[:8], q['taker_pct'] / 100, q['maker_pct'] / 100)
