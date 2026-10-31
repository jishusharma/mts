"""Cowen band daily event study, 2017-08 .. 2024-06. Rules fixed in PRE-REG.md (committed before the first run).

Measures only: no rule, gate or layer. Costs come from MyTradingSys/backtest/fees.py (no cost constant here).
Data: event_study/data/ (gitignored), fetched by fetch_klines.py; nothing after 2024-06-30 is ever loaded.

    python MyTradingSys/research/cowen_q4_2026-10-31/event_study/run_event_study.py
"""
import datetime as dt
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'MyTradingSys' / 'research' / 'sim_desk' / 'studies'))
from MyTradingSys.backtest.fees import BINANCE_TAKER  # noqa: E402
import cowen_bmsb as cb  # noqa: E402  (band, signals: same functions as the desk study)

FEE = BINANCE_TAKER                      # all-taker on entry and exit (PRE-REG)
DAY = 86400000
DATA = HERE / 'data'
FIRST_MONTH, LAST_MONTH = '2017-08', '2024-06'
LAST_DAY_MS = int(np.datetime64('2024-06-30', 'ms').astype(np.int64))
STOP_R, TARGET_R, HOLD = 1.0, 2.0, 30
GAP_PCT = 3.0
PLACEBO_D = (-3, -2, -1, -0.5, 0.5, 1, 2, 3)
BOOT_N, BOOT_SEED, MIN_EVENTS = 2000, 20261009, 30
IDEAS = ('BOUNCE', 'LOSE', 'FAKEOUT', 'CATCHDOWN')


def months(first=FIRST_MONTH, last=LAST_MONTH):
    y, m = map(int, first.split('-'))
    out = []
    while f'{y:04d}-{m:02d}' <= last:
        out.append(f'{y:04d}-{m:02d}')
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


# ---- data ----
def parse_klines(text):
    """Binance kline csv text -> array (open time ms, o, h, l, c), bars after 2024-06-30 dropped, sorted, unique."""
    rows = []
    for ln in text.splitlines():
        p = ln.split(',')
        if len(p) < 5 or not p[0].strip().lstrip('-').isdigit():
            continue
        t = int(p[0])
        if t > LAST_DAY_MS:
            continue
        rows.append((t, float(p[1]), float(p[2]), float(p[3]), float(p[4])))
    a = np.array(sorted(set(rows)), float).reshape(-1, 5)
    return a


def load_daily(symbol, folder=DATA):
    parts = []
    for m in months():
        f = Path(folder) / f'{symbol}-1d-{m}.csv'
        if not f.exists():
            raise FileNotFoundError(f'{f}: run fetch_klines.py first')
        parts.append(parse_klines(f.read_text(encoding='utf-8')))
    a = np.vstack(parts)
    assert a[:, 0].max() <= LAST_DAY_MS, 'data after 2024-06-30 loaded'
    assert (np.diff(a[:, 0]) == DAY).all(), f'{symbol}: gap or duplicate in daily bars'
    return a


# ---- features ----
def week_index(t_ms):
    return cb.week_index(t_ms)


def atr14(d):
    """Mean true range of the 14 days ending at each bar; NaN before bar 14."""
    h, l, c = d[:, 2], d[:, 3], d[:, 4]
    tr = np.full(len(d), np.nan)
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    out = np.full(len(d), np.nan)
    if len(d) > 14:
        cs = np.cumsum(np.r_[0.0, tr[1:]])            # cs[k] = sum tr[1..k]
        out[14:] = (cs[14:] - cs[:len(d) - 14]) / 14.0
    return out


def features(d):
    d = np.asarray(d, float)
    top, bottom = cb.band(d[:, 0], d[:, 4])
    c = d[:, 4]
    sma50 = np.full(len(d), np.nan)
    if len(d) >= 50:
        cs = np.cumsum(np.r_[0.0, c])
        sma50[49:] = (cs[50:] - cs[:-50]) / 50.0
    return {'d': d, 'top': top, 'bottom': bottom, 'sma50': sma50, 'atr': atr14(d)}


def placebo_d(week):
    return PLACEBO_D[int(week) % 8]


def shifted(f):
    """Placebo: band top and bottom both moved by d x ATR14, d cycling by week index (FORMULAS 18.6)."""
    wk = week_index(f['d'][:, 0])
    off = np.array([placebo_d(w) for w in wk]) * f['atr']
    g = dict(f)
    g['top'], g['bottom'] = f['top'] + off, f['bottom'] + off
    return g


# ---- one trade ----
def net_r(side, entry, exit_, r):
    return (side * (exit_ - entry) - FEE * entry - FEE * exit_) / r


def simulate(d, e, side, r):
    """Entry at the open of bar e. Returns (exit bar, exit price, reason) or None when bar e+HOLD-1 is past the data."""
    last = e + HOLD - 1
    if last > len(d) - 1:
        return None
    entry = d[e, 1]
    stop, target = entry - side * STOP_R * r, entry + side * TARGET_R * r
    for k in range(e, last + 1):
        o, h, l = d[k, 1], d[k, 2], d[k, 3]
        if (o <= stop) if side > 0 else (o >= stop):
            return k, float(o), 'stop'
        if (l <= stop) if side > 0 else (h >= stop):
            return k, float(stop), 'stop'
        if (h >= target) if side > 0 else (l <= target):
            return k, float(target), 'target'
    return last, float(d[last, 4]), 'timeout'


def events(f, setup, other=None):
    d = f['d']
    sigs = cb.signals(f, setup, GAP_PCT, other)
    out, busy_until = [], -1
    for s in sigs:
        i, side = s['i'], s['side']
        e = i + 1
        r = f['atr'][i]
        if e >= len(d) or not np.isfinite(r) or r <= 0 or e <= busy_until:
            continue
        res = simulate(d, e, side, r)
        if res is None:
            continue
        xi, xp, why = res
        entry = float(d[e, 1])
        busy_until = xi
        t = int(d[e, 0])
        out.append({'i': i, 'e': e, 'side': side, 'entry': entry, 'exit_i': xi, 'exit': xp, 'reason': why,
                    'r': float(r), 'gross_r': side * (xp - entry) / r, 'net_r': net_r(side, entry, xp, r),
                    'day': t // DAY, 'year': dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).year})
    return out


# ---- statistics (FORMULAS 18.7) ----
def stats(ev):
    n = len(ev)
    if not n:
        return {'n': 0, 'wins': 0, 'hit': 0.0, 'stop': 0.0, 'timeout': 0.0, 'mean_net': float('nan'), 'mean_gross': float('nan')}
    share = lambda w: sum(1 for x in ev if x['reason'] == w) / n      # noqa: E731
    return {'n': n, 'wins': sum(1 for x in ev if x['net_r'] > 0), 'hit': share('target'), 'stop': share('stop'),
            'timeout': share('timeout'), 'mean_net': sum(x['net_r'] for x in ev) / n,
            'mean_gross': sum(x['gross_r'] for x in ev) / n}


def by_year(ev):
    out = {}
    for y in sorted({x['year'] for x in ev}):
        r = [x['net_r'] for x in ev if x['year'] == y]
        out[y] = (len(r), sum(r) / len(r))
    return out


def stat_of_picks(by_day, picks):
    """Sum of R over the resampled days / number of events in them."""
    tot = sum(by_day[k].sum() for k in picks)
    cnt = sum(len(by_day[k]) for k in picks)
    return tot / cnt if cnt else float('nan')


def _pct(vals):
    v = np.asarray(vals, float)
    v = v[np.isfinite(v)]
    return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) if len(v) else (float('nan'), float('nan'))


def _day_tables(streams):
    days = sorted({x['day'] for ev in streams for x in ev})
    pos = {dd: k for k, dd in enumerate(days)}
    sums = [np.zeros(len(days)) for _ in streams]
    cnts = [np.zeros(len(days)) for _ in streams]
    for s, ev in enumerate(streams):
        for x in ev:
            sums[s][pos[x['day']]] += x['net_r']
            cnts[s][pos[x['day']]] += 1
    return len(days), sums, cnts


def _boot(streams, combine):
    nd, sums, cnts = _day_tables(streams)
    if nd == 0:
        return float('nan'), float('nan')
    rng = np.random.default_rng(BOOT_SEED)
    picks = rng.integers(0, nd, size=(BOOT_N, nd))
    res = []
    for row in picks:
        w = np.bincount(row, minlength=nd)
        means = []
        for s in range(len(streams)):
            c = (w * cnts[s]).sum()
            means.append((w * sums[s]).sum() / c if c else float('nan'))
        res.append(combine(means))
    return _pct(res)


def boot_mean(ev):
    return _boot([ev], lambda m: m[0])


def boot_diff(real, placebo):
    return _boot([real, placebo], lambda m: m[0] - m[1])


def verdict(n, lo, hi, dlo, dhi):
    if n < MIN_EVENTS:
        return 'NOT ENOUGH DATA'
    if lo > 0 and dlo > 0:
        return 'BAND SIGNAL'
    if hi < 0:
        return 'NEGATIVE'
    return 'NO EDGE SHOWN'


# ---- the run ----
def run_all():
    fb, fe = features(load_daily('BTCUSDT')), features(load_daily('ETHUSDT'))
    res = {}
    for idea in IDEAS:
        other = fe if idea == 'CATCHDOWN' else None
        real = events(fb, idea, other)
        plc = events(shifted(fb), idea, other)
        lo, hi = boot_mean(real)
        dlo, dhi = boot_diff(real, plc)
        res[idea] = {'real': real, 'placebo': plc, 'stats': stats(real), 'pstats': stats(plc), 'range': (lo, hi), 'drange': (dlo, dhi),
                     'verdict': verdict(len(real), lo, hi, dlo, dhi)}
    return fb, res


def day_str(day):
    return dt.datetime.fromtimestamp(day * 86400, dt.timezone.utc).strftime('%Y-%m-%d')


def fmt(x, p=2):
    return 'n/a' if x != x else f'{x:+.{p}f}'


def write_result(fb, res):
    d = fb['d']
    L = ['# RESULT: Cowen band, daily event study, BTC 2017-08 .. 2024-06', '',
         'Single run of the rules in PRE-REG.md (committed before this run). Measurement only: no rule, gate or layer follows from it.',
         f'Data: Binance spot BTCUSDT and ETHUSDT daily bars, {day_str(int(d[0, 0]) // DAY)} to {day_str(int(d[-1, 0]) // DAY)} ({len(d)} bars); nothing after 2024-06-30.',
         f'Band: 20-week SMA and 21-week EMA of completed weekly closes; first band day {day_str(int(d[np.flatnonzero(np.isfinite(fb["top"]))[0], 0]) // DAY)}.',
         f'Trade: entry next open, stop {STOP_R:g} R, target {TARGET_R:g} R, R = ATR14 daily, hold {HOLD} bars, all-taker fee {FEE * 1e4:g} bp per side from fees.py (regime A-style, before slippage).',
         '95 % range: day-block bootstrap, 2000 resamples, seed 20261009 (FORMULAS 18.7). Placebo: band shifted by d x ATR14, d cycling over 8 values by week (18.6).', '',
         '## Summary', '',
         '| Idea | n | Hit | Stop | Timeout | Wins (net>0) | Mean gross R | Mean net R | 95 % range | Placebo n | Placebo mean net R | Difference | 95 % range | Verdict |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for idea in IDEAS:
        r = res[idea]
        s, p = r['stats'], r['pstats']
        diff = s['mean_net'] - p['mean_net']
        L.append(f"| {idea} | {s['n']} | {s['hit']:.0%} | {s['stop']:.0%} | {s['timeout']:.0%} | {s['wins']} ({s['wins'] / max(s['n'], 1):.0%}) | "
                 f"{fmt(s['mean_gross'])} | {fmt(s['mean_net'])} | {fmt(r['range'][0])} .. {fmt(r['range'][1])} | {p['n']} | {fmt(p['mean_net'])} | "
                 f"{fmt(diff)} | {fmt(r['drange'][0])} .. {fmt(r['drange'][1])} | {r['verdict']} |")
    L += ['', 'BOUNCE and LOSE needed about 25 events each to be testable (card); the 30-event floor decides the verdict column.', '', '## Per year (year of entry: n, mean net R)', '']
    years = sorted({y for idea in IDEAS for y in by_year(res[idea]['real'])})
    L += ['| Idea | ' + ' | '.join(str(y) for y in years) + ' |', '|---|' + '---|' * len(years)]
    for idea in IDEAS:
        by = by_year(res[idea]['real'])
        L.append(f'| {idea} | ' + ' | '.join(f'{by[y][0]}: {fmt(by[y][1])}' if y in by else '-' for y in years) + ' |')
    L += ['', '## Reading', '']
    for idea in IDEAS:
        r = res[idea]
        s = r['stats']
        L.append(f"- {idea}: n = {s['n']}, mean net R {fmt(s['mean_net'])} (range {fmt(r['range'][0])} .. {fmt(r['range'][1])}), "
                 f"{s['wins']} wins; placebo difference {fmt(s['mean_net'] - r['pstats']['mean_net'])} (range {fmt(r['drange'][0])} .. {fmt(r['drange'][1])}). {r['verdict']}.")
    L += ['', 'Every event is listed in EVENTS.csv for a hand check against weekly closes.', '']
    (HERE / 'RESULT.md').write_text('\n'.join(L), encoding='utf-8', newline='\n')
    rows = ['idea,signal_date,entry_date,side,entry,exit_date,exit,reason,R,gross_R,net_R']
    for idea in IDEAS:
        for x in res[idea]['real']:
            rows.append(f"{idea},{day_str(int(d[x['i'], 0]) // DAY)},{day_str(x['day'])},{x['side']},{x['entry']:.2f},"
                        f"{day_str(int(d[x['exit_i'], 0]) // DAY)},{x['exit']:.2f},{x['reason']},{x['r']:.2f},{x['gross_r']:.4f},{x['net_r']:.4f}")
    (HERE / 'EVENTS.csv').write_text('\n'.join(rows) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    fb_, res_ = run_all()
    write_result(fb_, res_)
    for k, v in res_.items():
        print(k, v['stats']['n'], round(v['stats']['mean_net'], 3), v['range'], v['verdict'])
