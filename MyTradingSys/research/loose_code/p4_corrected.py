#!/usr/bin/env python
"""P4 corrected: quarter-hour opening imbalance (Kim & Hansen), per PRE_REG_P4_CORRECTED_2026-10-06.md.

Reproduces the numbers in P4_QUARTER_HOUR_IMBALANCE_CORRECTED_2026-10-08.md.  Run: python MyTradingSys/research/loose_code/p4_corrected.py

Interpretation where the pre-registration is silent (fixed before the first run, no tuning):
  - Opens: every 1m bar whose start minute is :00/:15/:30/:45 UTC (96 per day).
  - Imbalance: (buy_vol - sell_vol) / (buy_vol + sell_vol) of that 1m bar. Signal = sign(imbalance); zero -> skipped.
  - Entry at the CLOSE of the open bar (the imbalance is only known once that bar is complete); exit at the close of the bar
    W minutes later, W in {240, 480, 720}. Both bars must exist (no gap filling).
  - Gross return (bp) = sign * (exit/entry - 1) * 1e4 ; net = gross - 10 (pre-registered fee, round trip).
  - Sign stability: sign of mean gross per calendar year must agree across ALL years present (2024 = December only,
    2026 = to September; counts are printed).
  - CI95: day-block bootstrap of mean net, seed 12345, 2000 draws, percentile 2.5/97.5.
  - Placebo: imbalance signs shuffled across opens (seed 12345), same CI on net. Reported, not part of the decision.
  - PASS = stable gross sign AND net CI95 excludes zero *on the positive side* (lower bound > 0); anything else = NO
    REPLICATION. The pre-reg wording 'excludes zero' also admits a CI wholly below zero, i.e. a strategy that reliably loses the
    10 bp fee; that is not a replication, and the old run's 8h 'PASS' is consistent with exactly that flaw.
"""
import csv
import glob
import gzip
import sys
from datetime import datetime, timezone

import numpy as np

DATA = 'F:/MTS/data/orderflow_1m'
FEE_BP = 10.0
WINDOWS = {'4h': 240, '8h': 480, '12h': 720}
SEED = 12345
DRAWS = 2000
MIN_MS = 60_000
DAY_MS = 86_400_000


def load(data_dir=DATA):
    """Sorted, de-duplicated arrays t (ms), close, buy_vol, sell_vol."""
    rows = []
    for p in sorted(glob.glob(f'{data_dir}/????-??-??.csv.gz')):
        with gzip.open(p, 'rt', newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                rows.append((int(r['t']), float(r['c']), float(r['buy_vol']), float(r['sell_vol'])))
    a = np.array(rows, dtype=float)
    _, first = np.unique(a[:, 0], return_index=True)
    a = a[first]  # np.unique sorts by t
    return dict(t=a[:, 0].astype(np.int64), c=a[:, 1], buy=a[:, 2], sell=a[:, 3])


def year_of(t_ms):
    return np.array([datetime.fromtimestamp(x / 1000, tz=timezone.utc).year for x in t_ms])


def trades(d, window_min):
    """One row per quarter-hour open with a known exit bar: dict of day, year, gross (signed bp), imb."""
    t, c = d['t'], d['c']
    tot = d['buy'] + d['sell']
    imb = np.where(tot > 0, (d['buy'] - d['sell']) / np.where(tot > 0, tot, 1.0), 0.0)
    is_open = ((t // MIN_MS) % 15 == 0) & (imb != 0)
    i = np.nonzero(is_open)[0]
    exit_t = t[i] + window_min * MIN_MS
    j = np.searchsorted(t, exit_t)
    ok = (j < len(t))
    ok[ok] = t[j[ok]] == exit_t[ok]  # exit bar must exist exactly (no gap filling)
    i, j = i[ok], j[ok]
    gross = np.sign(imb[i]) * (c[j] / c[i] - 1.0) * 1e4
    return dict(t=t[i], day=t[i] // DAY_MS, year=year_of(t[i]), gross=gross, imb=imb[i])


def day_block_ci(day, x, seed=SEED, draws=DRAWS):
    """Day-block bootstrap of the mean of x: resample whole days, mean of pooled observations."""
    u, inv = np.unique(day, return_inverse=True)
    s = np.bincount(inv, weights=x)
    n = np.bincount(inv).astype(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(u), size=(draws, len(u)))
    means = s[idx].sum(axis=1) / n[idx].sum(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)), float(s.sum() / n.sum())


def summarize(r):
    """Verdict numbers for one window from its trades dict (day, year, gross, imb); shared with T093."""
    by_year = {int(y): (float(r['gross'][r['year'] == y].mean()), int((r['year'] == y).sum()))
               for y in np.unique(r['year'])}
    signs = {np.sign(m) for m, _ in by_year.values()}
    stable = len(signs) == 1 and 0 not in signs
    net = r['gross'] - FEE_BP
    lo, hi, mean_net = day_block_ci(r['day'], net)
    rng = np.random.default_rng(SEED)
    raw = r['gross'] / np.sign(r['imb'])  # unsigned forward return
    pg = np.sign(rng.permutation(r['imb'])) * raw
    plo, phi, pmean = day_block_ci(r['day'], pg - FEE_BP)
    excl = lo > 0  # positive edge only: a CI wholly below zero is fee drag, not replication
    return dict(n=len(net), by_year=by_year, gross_mean=float(r['gross'].mean()), net_mean=mean_net,
                ci=(lo, hi), placebo_net=pmean, placebo_ci=(plo, phi), stable=stable, excludes_zero=excl,
                verdict='PASS' if (stable and excl) else 'NO REPLICATION')


def analyse(d):
    return {name: summarize(trades(d, w)) for name, w in WINDOWS.items()}


def report(out):
    for name, o in out.items():
        print(f'## {name}: n={o["n"]}  gross mean {o["gross_mean"]:+.2f} bp  net mean {o["net_mean"]:+.2f} bp  '
              f'net CI95 [{o["ci"][0]:+.2f}, {o["ci"][1]:+.2f}]')
        for y, (m, n) in o['by_year'].items():
            print(f'   {y}: gross mean {m:+.2f} bp  n={n}')
        print(f'   sign stable across years: {o["stable"]}   CI above zero: {o["excludes_zero"]}   '
              f'placebo net {o["placebo_net"]:+.2f} bp CI [{o["placebo_ci"][0]:+.2f}, {o["placebo_ci"][1]:+.2f}]')
        print(f'   VERDICT {name}: {o["verdict"]}')


if __name__ == '__main__':
    d = load(sys.argv[1] if len(sys.argv) > 1 else DATA)
    fmt = lambda x: datetime.fromtimestamp(x / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')
    print(f'bars {len(d["t"])}  {fmt(d["t"][0])} .. {fmt(d["t"][-1])}')
    report(analyse(d))
