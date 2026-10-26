#!/usr/bin/env python
"""T093: turn-of-candle order imbalance, 4/8/12 h horizon, BTCUSDT 2022-2026 from 1m klines (spec: items/T093_toc_imbalance_klines.md).

The original idea (Kim and Hansen; TURN_OF_CANDLE_ORIGIN_2026-10-09.md section 2) is that the order imbalance of the opening window of
each quarter-hour predicts returns over 4-12 h. P4 corrected tested it on 2024-12..2026-09 (NO REPLICATION). This run extends the
sample back to 2022 using klines only: buy = taker_buy_volume, sell = volume - taker_buy_volume. Same rules as p4_corrected.py
(it supplies trades/summarize): opens at :00/:15/:30/:45, entry at that bar's close, exit W minutes later, fee 10 bp round trip
(taker 0.0005 x 2 legs, backtest/fees.py), PASS needs stable gross sign across years AND net CI95 lower bound > 0. Nothing tuned.

Usage (each step is far below 300 s, so a desk task can run one year at a time):
  python MyTradingSys/research/loose_code/t093_toc_imbalance_klines.py part --year 2023 [--klines DIR] [--out DIR]
  python MyTradingSys/research/loose_code/t093_toc_imbalance_klines.py combine [--out DIR]     # needs part_<year>.npz files
Defaults: --klines F:/MTS/data/tom_raw/klines, --out F:/MTS/data/t093.
"""
import argparse
import csv
import glob
import os
import re
import sys
from datetime import datetime, timezone

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_corrected as p4  # noqa: E402

FEE_BP = p4.FEE_BP
WINDOWS = p4.WINDOWS
KLINES = 'F:/MTS/data/tom_raw/klines'
OUT = 'F:/MTS/data/t093'
_NAME = re.compile(r'BTCUSDT-1m-(\d{4})-(\d{2})(?:-(\d{2}))?\.csv$')


def buy_sell(volume, taker_buy):
    """Klines carry the taker-buy part of the volume; the rest is taker-sell."""
    return np.asarray(taker_buy, dtype=float), np.asarray(volume, dtype=float) - np.asarray(taker_buy, dtype=float)


def arrays(rows):
    """rows: (open_time_ms, close, volume, taker_buy_volume) -> sorted, de-duplicated dict(t, c, buy, sell)."""
    a = np.array(rows, dtype=float)
    _, first = np.unique(a[:, 0], return_index=True)
    a = a[first]
    buy, sell = buy_sell(a[:, 2], a[:, 3])
    return dict(t=a[:, 0].astype(np.int64), c=a[:, 1], buy=buy, sell=sell)


def _files_for(klines_dir, years):
    """Files of the requested years plus the following January (exit bars of December opens)."""
    want = set(years) | {(y + 1, 1) for y in years}
    out = []
    for p in sorted(glob.glob(os.path.join(klines_dir, 'BTCUSDT-1m-*.csv'))):
        m = _NAME.search(os.path.basename(p))
        if not m:
            continue
        y, mo = int(m.group(1)), int(m.group(2))
        if y in years or (y, mo) in want:
            out.append(p)
    return out


def load_klines(klines_dir, years):
    rows = []
    for p in _files_for(klines_dir, set(years)):
        with open(p, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                rows.append((int(r['open_time']), float(r['close']), float(r['volume']), float(r['taker_buy_volume'])))
    if not rows:
        raise SystemExit(f'no klines for {sorted(years)} in {klines_dir}')
    return arrays(rows)


def year_trades(d, window_min, year):
    """p4's trades for one window, limited to opens inside `year` (the exit bar may be in the next year)."""
    r = p4.trades(d, window_min)
    keep = r['year'] == year
    return {k: v[keep] for k, v in r.items()}


def part_arrays(d, year):
    """Per-window trades of one year as a flat dict of arrays (savez-able)."""
    out = {}
    for name, w in WINDOWS.items():
        r = year_trades(d, w, year)
        for k, v in r.items():
            out[f'{name}_{k}'] = v
    return out


def analyse_parts(parts):
    res = {}
    for name in WINDOWS:
        cat = {k: np.concatenate([p[f'{name}_{k}'] for p in parts]) for k in ('t', 'day', 'year', 'gross', 'imb')}
        res[name] = p4.summarize(cat)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('cmd', choices=['part', 'combine'])
    ap.add_argument('--year', type=int)
    ap.add_argument('--klines', default=KLINES)
    ap.add_argument('--out', default=OUT)
    a = ap.parse_args(argv)
    if a.cmd == 'part':
        if not a.year:
            ap.error('part needs --year')
        d = load_klines(a.klines, {a.year})
        os.makedirs(a.out, exist_ok=True)
        path = os.path.join(a.out, f'part_{a.year}.npz')
        np.savez_compressed(path, **part_arrays(d, a.year))
        print(f'year {a.year}: bars {len(d["t"])} -> {path}')
        return 0
    paths = sorted(glob.glob(os.path.join(a.out, 'part_*.npz')))
    if not paths:
        print(f'no part_*.npz in {a.out}')
        return 1
    parts = [dict(np.load(p)) for p in paths]
    years = sorted({int(y) for pt in parts for y in np.unique(pt['4h_year'])})
    print(f'parts {len(paths)}, years {years}')
    p4.report(analyse_parts(parts))
    return 0


if __name__ == '__main__':
    sys.exit(main())
