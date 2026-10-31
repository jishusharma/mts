"""Usage: python run_reclaim.py DEV|VAL  -> results_<split>.csv + table on stdout.
Fetches public monthly 4h/1d klines (data.binance.vision) to a cache outside the repo."""
import io
import os
import sys
import tempfile
import urllib.request
import zipfile

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..')))
import reclaim  # noqa: E402
from backtest import splits  # noqa: E402

BASE = 'https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT'
CACHE = os.path.join(tempfile.gettempdir(), 'mts_reclaim_klines')
INTERVAL = {'4h': '4h', '1D': '1d'}
RANGE = {'DEV': ('2021-12', '2024-06'), 'VAL': ('2024-07', '2025-06')}  # DEV starts one month early as indicator warm-up only
TRADE_FROM = {'DEV': '2022-01-01', 'VAL': '2024-07-01'}
SEED = 1


def month_file(interval, ym):
    p = os.path.join(CACHE, f'BTCUSDT-{interval}-{ym}.csv')
    if not os.path.exists(p):
        os.makedirs(CACHE, exist_ok=True)
        raw = urllib.request.urlopen(f'{BASE}/{interval}/BTCUSDT-{interval}-{ym}.zip', timeout=120).read()
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            with open(p, 'wb') as f:
                f.write(z.read(z.namelist()[0]))
    return p


def load(tfn, split):
    a, z = RANGE[split]
    parts = []
    for ym in pd.period_range(a, z, freq='M').strftime('%Y-%m'):
        p = month_file(INTERVAL[tfn], ym)
        with open(p) as f:
            hdr = f.readline().lower().startswith('open_time')
        part = pd.read_csv(p, header=0 if hdr else None, usecols=[0, 1, 2, 3, 4])
        part.columns = ['t', 'o', 'h', 'l', 'c']
        parts.append(part)
    d = pd.concat(parts, ignore_index=True)
    d['t'] = np.where(d.t > 1e14, d.t // 1000, d.t) // 1000
    return d.drop_duplicates('t').sort_values('t').reset_index(drop=True)


def wk_ci(t, x, nb=1000):
    wk = (np.asarray(t) // 604800).astype(int)
    x = np.asarray(x)
    if len(x) < 10:
        return np.nan, np.nan
    u = np.unique(wk)
    idx = {w: np.where(wk == w)[0] for w in u}
    rng = np.random.default_rng(SEED)
    m = [x[np.concatenate([idx[w] for w in rng.choice(u, len(u))])].mean() for _ in range(nb)]
    return tuple(np.percentile(m, [2.5, 97.5]))


def verdict(n, lo, hi):
    if n < 100 or np.isnan(lo):
        return 'INCONCLUSIVE'
    return 'FAIL' if hi < 0 else 'PASS' if lo > 0 else 'INCONCLUSIVE'


def main(split):
    rows = []
    t0 = pd.Timestamp(TRADE_FROM[split]).timestamp()
    for tfn in ('4h', '1D'):
        b = load(tfn, split)
        last = pd.Timestamp(b.t.iloc[-1], unit='s')
        if split == 'DEV':
            splits.assert_dev_only(pd.Timestamp('2022-01-01'), last)
        ev = pd.DataFrame(reclaim.events(b, tfn), columns=['tf', 'side', 't', 'gross', 'net', 'hold', 'exit'])
        ev = ev[ev.t >= t0]
        for name in ('all', 'low', 'high'):
            sub = ev if name == 'all' else ev[ev.side == name]
            n = len(sub)
            if n == 0:
                rows.append(dict(tf=tfn, arm=name, n=0))
                continue
            lo, hi = wk_ci(sub.t, sub.net)
            rows.append(dict(tf=tfn, arm=name, n=n, gross_pct=100 * sub.gross.mean(), net_pct=100 * sub.net.mean(),
                             ci_lo=100 * lo, ci_hi=100 * hi, win_pct=100 * (sub.net > 0).mean(),
                             stop_share=(sub.exit == 'stop').mean(), mean_hold=sub.hold.mean(),
                             verdict=verdict(n, lo, hi) if name == 'all' else 'descriptive'))
    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(HERE, f'results_{split}.csv'), index=False, lineterminator='\n', float_format='%.4f')
    print(r.round(3).to_string(index=False))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'DEV')
