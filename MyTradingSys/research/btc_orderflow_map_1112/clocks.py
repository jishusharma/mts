"""Card 2/4 btc-of-map-clocks-1112: BTC own clocks from 1m taker delta. DEV ONLY (PREREG.md frozen).
Definitions (SOURCED = PREREG/card, OURS = chosen here):
- Data: Binance USD-M BTCUSDT 1m klines, DEV = 2022-02-01 .. 2024-05-31 UTC (PREREG Splits; SOURCED). VALIDATION, GAP, RESERVE,
  HOLDOUT files are never opened: the loader only takes months 2022-01 .. 2024-05 and refuses any other split.
  2022-01 is read for the regime trailing window only (PREREG warm-up).
- delta = 2 * taker_buy_volume - volume per 1m bar (SOURCED cvd_u7_u8.py).
- Instance = one clock entry. Hour/weekday tables: one entry per (UTC day, hour) at the hour's first 1m open (OURS), 60 min hold,
  so instances never overlap. Funding table: one entry per settlement 00/08/16Z at the open of the 1m bar one minute after
  the timestamp (SOURCED PREREG A3 entry); the concentration window is the 8h block centred on the settlement
  (20-04, 04-12, 12-20Z = nearest settlement; SOURCED PREREG funding clock).
- Per instance: delta share = sum(delta)/sum(volume) over the block, mean |1m return| bp over the block, forward return in bp
  from entry open to the close of the 1m bar 15 / 60 min later (close[e+h-1]/open[e]-1). Net = gross - 10 bp round trip
  (SOURCED PREREG fee); long net = gross-10, short net = -gross-10.
- Placebo (SOURCED card; label draw OURS): 1,000 permutations (seed 1112) of the bucket labels over instances; z = (observed
  bucket mean - placebo mean) / placebo sd. Cells with |z| < 2 are marked noise (~).
- Regime mix (OURS, PREREG asks for it): trailing 90 daily-close return > +20 % bull, < -20 % bear, else range; first 90 days n/a.
"""
import argparse
import csv
import glob
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KLINES = 'F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv'
DEV_START = '2022-02-01'
DEV_END = '2024-05-31'
FIRST_MONTH, LAST_MONTH = '2022-01', '2024-05'
FEE_BP, SEED, NPERM, ZNOISE = 10.0, 1112, 1000, 2.0
DAY_MIN = 1440


def _ts_ms(x):
    x = int(x)
    return x // 1000 if x > 10 ** 14 else x


def load_dev(pattern=KLINES, last_month=LAST_MONTH):
    """Return (t0_ms, o, c, v, taker_buy) on a 1m grid from 2022-01-01 to the last DEV minute; missing bars = NaN."""
    files = []
    for f in sorted(glob.glob(pattern)):
        tag = os.path.basename(f)[len('BTCUSDT-1m-'):-4][:7]
        if FIRST_MONTH <= tag <= last_month:
            files.append(f)
    rows = []
    for f in files:
        with open(f) as fh:
            for r in csv.reader(fh):
                if r[0] == 'open_time':
                    continue
                rows.append((_ts_ms(r[0]), float(r[1]), float(r[4]), float(r[5]), float(r[9])))
    a = np.array(rows, dtype=float)
    t0 = int(np.datetime64('2022-01-01T00:00', 'ms').astype('int64'))
    tend = int(np.datetime64(DEV_END + 'T23:59', 'ms').astype('int64'))
    a = a[(a[:, 0] >= t0) & (a[:, 0] <= tend)]
    n = (tend - t0) // 60000 + 1
    out = np.full((4, n), np.nan)
    idx = ((a[:, 0] - t0) // 60000).astype(int)
    for k, col in enumerate(a[:, 1:5].T):
        out[k, idx] = col
    return t0, out[0], out[1], out[2], out[3]


def build_instances(o, c, v, tb, start_min, n_days):
    """start_min = grid index of the first DEV midnight. Returns {'hour','fund'} -> array rows
    (label, day_index, delta_share, absret_bp, fwd15_bp, fwd60_bp)."""
    d = 2 * tb - v
    ret = np.abs(c / o - 1) * 1e4

    def block(e0, e1):
        if e0 < 0 or e1 > len(o):
            return None
        vv = v[e0:e1]
        if np.isnan(vv).any() or np.isnan(ret[e0:e1]).any():
            return None
        return d[e0:e1].sum() / vv.sum(), ret[e0:e1].mean()

    def fwd(e, h):
        j = e + h - 1
        if e < 0 or j >= len(o) or np.isnan(o[e]) or np.isnan(c[j]):
            return None
        return (c[j] / o[e] - 1) * 1e4

    res = {'hour': [], 'fund': []}
    for day in range(n_days):
        base = start_min + day * DAY_MIN
        for h in range(24):
            e = base + h * 60
            b = block(e, e + 60)
            f15, f60 = fwd(e, 15), fwd(e, 60)
            if b is None or f15 is None or f60 is None:
                continue
            res['hour'].append((h, day, b[0], b[1], f15, f60))
        for k, s in enumerate((0, 8, 16)):
            sm = base + s * 60
            b = block(sm - 240, sm + 240)
            e = sm + 1
            f15, f60 = fwd(e, 15), fwd(e, 60)
            if b is None or f15 is None or f60 is None:
                continue
            res['fund'].append((k, day, b[0], b[1], f15, f60))
    return {k: np.array(x, dtype=float).reshape(-1, 6) for k, x in res.items()}


def bucket_means(labels, vals, nb):
    cnt = np.bincount(labels, minlength=nb).astype(float)
    out = np.empty((nb, vals.shape[1]))
    for j in range(vals.shape[1]):
        out[:, j] = np.bincount(labels, weights=vals[:, j], minlength=nb) / np.maximum(cnt, 1)
    return cnt, out


def placebo_z(labels, vals, nb, nperm=NPERM, seed=SEED, shuffle_obs=False):
    """Observed bucket means and z vs label-permutation placebo; shuffle_obs shuffles the labels once first (null check)."""
    rng = np.random.default_rng(seed)
    lab = labels.copy()
    if shuffle_obs:
        rng.shuffle(lab)
    cnt, obs = bucket_means(lab, vals, nb)
    sims = np.empty((nperm, nb, vals.shape[1]))
    for i in range(nperm):
        sims[i] = bucket_means(rng.permutation(lab), vals, nb)[1]
    z = (obs - sims.mean(0)) / np.maximum(sims.std(0), 1e-12)
    return cnt, obs, z


def fmt_cell(x, z, fmt):
    return (fmt % x) + ('~' if abs(z) < ZNOISE else '')


def render(inst, wd0):
    wn = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    groups = [('hour', 24, ['h%02d' % i for i in range(24)]),
              ('fund', 3, ['fund 00Z (20-04)', 'fund 08Z (04-12)', 'fund 16Z (12-20)']),
              ('wday', 7, wn)]
    lines = ['| Bucket | n | delta share | abs ret bp | fwd15 gross bp | fwd60 gross bp | long net60 bp | short net60 bp |',
             '|---|---|---|---|---|---|---|---|']
    js = {}
    for key, nb, names in groups:
        if key == 'wday':
            arr = inst['hour'].copy()
            arr[:, 0] = (arr[:, 1] + wd0) % 7
        else:
            arr = inst[key]
        cnt, obs, z = placebo_z(arr[:, 0].astype(int), arr[:, 2:], nb)
        for i in range(nb):
            ds, ab, f15, f60 = obs[i]
            zd, za, z15, z60 = z[i]
            lines.append('| %s | %d | %s | %s | %s | %s | %s | %s |' % (
                names[i], cnt[i], fmt_cell(ds, zd, '%+.4f'), fmt_cell(ab, za, '%.2f'), fmt_cell(f15, z15, '%+.2f'),
                fmt_cell(f60, z60, '%+.2f'), fmt_cell(f60 - FEE_BP, z60, '%+.2f'), fmt_cell(-f60 - FEE_BP, z60, '%+.2f')))
            js['%s:%s' % (key, names[i])] = dict(
                n=int(cnt[i]), delta_share=ds, z_delta=zd, abs_ret_bp=ab, z_abs=za, fwd15_bp=f15, z_fwd15=z15,
                fwd60_bp=f60, z_fwd60=z60, long_net60_bp=f60 - FEE_BP, short_net60_bp=-f60 - FEE_BP)
    return '\n'.join(lines), js


def regime_mix(c, n_days):
    cnt = {'bull': 0, 'bear': 0, 'range': 0, 'n/a': 0}
    for d in range(31, 31 + n_days):  # DEV day 0 = 2022-02-01 = grid day 31
        j, j0 = d * DAY_MIN + DAY_MIN - 1, (d - 90) * DAY_MIN + DAY_MIN - 1
        if j0 < 0 or j >= len(c) or np.isnan(c[j]) or np.isnan(c[j0]):
            cnt['n/a'] += 1
            continue
        r = c[j] / c[j0] - 1
        cnt['bull' if r > .2 else 'bear' if r < -.2 else 'range'] += 1
    return cnt, max(sum(cnt.values()), 1)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--split', required=True)
    ap.add_argument('--pattern', default=KLINES)
    a = ap.parse_args(argv)
    if a.split != 'dev':
        raise SystemExit('only --split dev is allowed (PREREG: VALIDATION/HOLDOUT not opened by this card)')
    t0, o, c, v, tb = load_dev(a.pattern)
    n_days = int((np.datetime64(DEV_END) - np.datetime64(DEV_START)).astype(int)) + 1
    start_min = 31 * DAY_MIN
    wd0 = int((np.datetime64(DEV_START).astype('datetime64[D]').astype(int) + 3) % 7)  # 1970-01-01 = Thu; Mon = 0
    inst = build_instances(o, c, v, tb, start_min, n_days)
    dev_bars = int(np.isfinite(v[start_min:]).sum())
    missing = n_days * DAY_MIN - dev_bars
    table, js = render(inst, wd0)
    rc, tot = regime_mix(c, n_days)
    regime = 'Regime mix: ' + ', '.join('%s %.0f%%' % (k, 100 * x / tot) for k, x in rc.items()) + ' of %d DEV days' % tot
    md = ['# CLOCKS: BTC own clocks from 1m taker delta (card btc-of-map-clocks-1112), DEV only', '',
          'DEV = %s .. %s UTC (PREREG split), %d days, %d 1m bars present, %d missing (reported, not filled). Fee 10 bp round trip.'
          % (DEV_START, DEV_END, n_days, dev_bars, missing),
          'Instances: hour/weekday = one entry per (day, hour) open, 60 min hold; fund = one per settlement at +1 min, window = 8h block centred on it.',
          'delta share = sum(2*taker_buy-volume)/sum(volume); `~` = |z| < 2 vs 1,000 label-shuffle placebos (seed 1112) = noise. '
          'fwd/net in bp; long net = gross-10, short net = -gross-10.',
          '', table, '', regime, '',
          'VALIDATION: NOT RUN (instruction for this card: DEV only, no VALIDATION or HOLDOUT file opened). Second table pending.']
    with open(os.path.join(HERE, 'CLOCKS.md'), 'w') as fh:
        fh.write('\n'.join(md) + '\n')
    with open(os.path.join(HERE, 'results_clocks.json'), 'w') as fh:
        json.dump(dict(split='dev', start=DEV_START, end=DEV_END, bars_present=dev_bars, bars_missing=missing,
                       regime=rc, cells=js), fh, indent=1)
    print(table)
    print(regime)
    print('missing bars', missing)


if __name__ == '__main__':
    main()
