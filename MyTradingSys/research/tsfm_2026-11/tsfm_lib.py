"""Pure helpers for the TSFM study (no torch). See PRE_REG.md."""
import glob
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
sys.path.insert(0, ROOT)
from MyTradingSys.backtest import fees, splits  # noqa: E402

RT_COST_LOG = 2 * fees.BINANCE_TAKER * 1.4  # 14 bp round trip (PRE_REG), derived from fees.py taker


def pinball(y, q, levels):
    y = np.asarray(y, float)[:, None]
    q = np.asarray(q, float)
    tau = np.asarray(levels, float)[None, :]
    d = y - q
    return float(np.mean(np.maximum(tau * d, (tau - 1) * d)))


def coverage(y, lo, hi):
    y = np.asarray(y, float)
    return float(np.mean((y >= lo) & (y <= hi)))


def guard_dev(ts):
    ts = pd.DatetimeIndex(ts)
    splits.assert_dev_only(ts.min(), ts.max())


def load_1m(folder):
    frames = []
    for f in sorted(glob.glob(os.path.join(folder, '*.csv'))):
        d = pd.read_csv(f, header=None, usecols=[0, 1, 2, 3, 4], names=['t', 'open', 'high', 'low', 'close'],
                        comment=None)
        d = d[pd.to_numeric(d['t'], errors='coerce').notna()].astype(float)
        frames.append(d)
    d = pd.concat(frames)
    d.index = pd.to_datetime(d['t'].astype('int64'), unit='ms')
    d = d.drop(columns='t').sort_index()
    return d[~d.index.duplicated()]


def build_bars(df, rule):
    g = df.resample(rule, closed='left', label='left')
    b = pd.DataFrame({'open': g['open'].first(), 'high': g['high'].max(), 'low': g['low'].min(),
                      'close': g['close'].last(), 'n': g['close'].count()})
    need = int(pd.Timedelta(rule).total_seconds() // 60)
    return b[b['n'] == need].drop(columns='n')


def week_boot(r, weeks, n=2000, seed=1):
    r = np.asarray(r, float)
    weeks = np.asarray(weeks)
    uw = np.unique(weeks)
    groups = [r[weeks == w] for w in uw]
    rng = np.random.default_rng(seed)
    means = np.empty(n)
    for i in range(n):
        pick = rng.integers(0, len(groups), len(groups))
        means[i] = np.concatenate([groups[j] for j in pick]).mean()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))
