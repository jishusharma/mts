"""Entry-time layer features for the meta-label test (PRE_REG.md section 2). Causal: a feature at entry time t0 uses only bars
whose close time (open + length) is <= t0, and funding settlements with calc_time <= t0.

Existing MTS layer code, unchanged: krown_core.bbwp, rsi_core, wavetrend.compute, cowen_bmsb.features. DEV months only (2022-01..2024-06).
Input 1m array columns: open time ms, open, high, low, close, volume.
"""
import csv
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SIM = HERE.parent / 'sim_desk'
sys.path.insert(0, str(SIM))
sys.path.insert(0, str(SIM / 'studies'))
import _bars  # noqa: E402
import cowen_bmsb  # noqa: E402
from MyTradingSys.backtest.layers.krown.krown_core import bbwp  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402
from MyTradingSys.backtest.layers.wavetrend import wavetrend as wt  # noqa: E402

H1, D1 = 60 * 60000, 24 * 60 * 60000
FUND_DIR = Path(os.environ.get('MTS_FUNDING_DIR', 'F:/MTS/Dumps/backtest/raw/fundingRate'))
FUND_FIRST, FUND_LAST = '2022-01', '2024-06'          # DEV only; nothing later is ever read
WT_ZONE = {'os2': -2, 'os1': -1, 'mid': 0, 'ob1': 1, 'ob2': 2}
NAMES = ['bbwp', 'd1', 'cowen', 'fund', 'hour', 'rsi', 'wt', 'relvol']      # raw readings (8 layer features)
MODEL_COLS = ['side', 'bbwp', 'd1_al', 'cowen_al', 'fund_al', 'sess_eu', 'sess_us', 'rsi_al', 'wt_al', 'relvol']


def last_closed(opens, tf_ms, t, leak=False):
    """Index of the last bar with open + tf_ms <= t (closed at or before t); -1 if none. leak=True is the WRONG rule
    (a bar counts once it has opened) kept only so the test can prove it detects look-ahead."""
    opens = np.asarray(opens)
    t = np.asarray(t)
    return np.searchsorted(opens, t, side='right') - 1 if leak else np.searchsorted(opens + tf_ms, t, side='right') - 1


def load_funding(first=FUND_FIRST, last=FUND_LAST, folder=None):
    """Sorted (calc_time_ms, rate) arrays from the monthly files first..last only."""
    folder = Path(folder or FUND_DIR)
    ts, rs = [], []
    for m in _bars._months(first, last):
        f = folder / f'BTCUSDT-fundingRate-{m}.csv'
        if not f.exists():
            raise FileNotFoundError(f)
        with open(f, newline='', encoding='utf-8') as fh:
            rd = csv.reader(fh)
            for row in rd:
                if not row or not row[0].isdigit():
                    continue
                ts.append(int(row[0]))
                rs.append(float(row[2]))
    o = np.argsort(ts, kind='stable')
    return np.array(ts, np.int64)[o], np.array(rs, float)[o]


def agg_1h(a):
    """1h bars from 1m (UTC aligned): open time, high, low, close, volume sum."""
    k = (a[:, 0] // H1).astype(np.int64)
    s = np.flatnonzero(np.r_[True, k[1:] != k[:-1]])
    e = np.r_[s[1:], len(a)] - 1
    return (k[s] * H1, np.maximum.reduceat(a[:, 2], s), np.minimum.reduceat(a[:, 3], s), a[e, 4], np.add.reduceat(a[:, 5], s))


def build_context(a, funding=None):
    """All indicator series once (each value at bar index i uses bars <= i of its own timeframe only)."""
    t1, h, l, c, v = agg_1h(a)
    bw = bbwp(c.tolist(), 7, 100)
    rsi = rsi_core(c.tolist(), 14)
    rows = wt.compute([(int(t), float(x), float(y), float(z)) for t, x, y, z in zip(t1, h, l, c)], H1)
    relvol = np.full(len(v), np.nan)
    for i in range(24, len(v)):
        m = v[i - 24:i].mean()
        if m > 0 and v[i] > 0:
            relvol[i] = math.log(v[i] / m)
    cw = cowen_bmsb.features(a[:, :5])
    return {'t1': t1,
            'bbwp': np.array([np.nan if x is None else x for x in bw]),
            'rsi': np.array([np.nan if x is None else x for x in rsi]),
            'wt': np.array([np.nan if r.zone is None else WT_ZONE[r.zone] for r in rows], float),
            'relvol': relvol, 'td': cw['d'][:, 0], 'dclose': cw['d'][:, 4], 'sma50': cw['sma50'], 'top': cw['top'], 'bottom': cw['bottom'],
            'f_t': None if funding is None else funding[0], 'f_r': None if funding is None else funding[1]}


def raw_features(ctx, t0, leak=False):
    """{name: array} of raw readings at the entry times t0 (NaN = not available)."""
    t0 = np.asarray(t0, np.int64)
    i1 = last_closed(ctx['t1'], H1, t0, leak)
    i1c = np.where(i1 >= 0, i1, 0)
    pick = lambda arr: np.where(i1 >= 0, arr[i1c], np.nan)          # noqa: E731
    iD = last_closed(ctx['td'], D1, t0, leak)
    iDc = np.where(iD >= 0, iD, 0)
    dc, top, bot, sma = (np.where(iD >= 0, ctx[k][iDc], np.nan) for k in ('dclose', 'top', 'bottom', 'sma50'))
    cow = np.where(np.isnan(top) | np.isnan(bot), np.nan, np.where(dc > top, 1.0, np.where(dc < bot, -1.0, 0.0)))
    d1 = np.where(np.isnan(sma) | np.isnan(dc), np.nan, np.sign(dc - sma))
    if ctx['f_t'] is None:
        fund = np.full(len(t0), np.nan)
    else:
        j = np.searchsorted(ctx['f_t'], t0, side='right') - 1       # calc_time <= t0
        fund = np.where(j >= 0, np.sign(ctx['f_r'][np.where(j >= 0, j, 0)]), np.nan)
    return {'bbwp': pick(ctx['bbwp']), 'd1': d1, 'cowen': cow, 'fund': fund, 'hour': ((t0 // H1) % 24).astype(float),
            'rsi': pick(ctx['rsi']), 'wt': pick(ctx['wt']), 'relvol': pick(ctx['relvol'])}


def model_matrix(raw, side):
    """(n, 10) model columns in MODEL_COLS order (PRE_REG section 2); side = +1 / -1 array."""
    side = np.asarray(side, float)
    hr = raw['hour']
    eu = ((hr >= 7) & (hr < 13)).astype(float)
    us = ((hr >= 13) & (hr < 21)).astype(float)
    rsi = np.where(np.isnan(raw['rsi']), np.nan, np.where(raw['rsi'] >= 60, 1.0, np.where(raw['rsi'] <= 40, -1.0, 0.0)))
    return np.column_stack([side, raw['bbwp'] / 100.0, raw['d1'] * side, raw['cowen'] * side, raw['fund'] * side, eu, us,
                            rsi * side, raw['wt'] * side, raw['relvol']])
