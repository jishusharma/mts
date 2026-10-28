"""O2: independent recount of the E2 Krown S8 4h pooled C0, re-derived from the frozen PRE_REG.md s2, not from e2_run.py.

Data = public Binance USD-M 4h klines for BTCUSDT/ETHUSDT/SOLUSDT, 2020-01..2024-06 (warm-up only from 2019-09, which
is NOT_IN_DATA upstream), fetched into a gitignored cache (O2_KLINE_CACHE, default F:/MTS/data/fable_run6_klines_o2).
Any bar with open_time >= 2024-07-01 00:00Z is dropped at load and asserted absent before any computation; no outcome
column and no sealed bar is ever read. The S8 event rule is the repo's own krown_events.setup_s8 (imported, not copied).

Trade model is frozen in PRE_REG s2 items 6-8 (OURS defaults): market entry at the open of the bar after the signal
(taker + slip), stop = far side of the last 10 bars incl. the signal bar (floor 0.56 % of the fill), target 2R from the
fill (maker, touch = fill), time stop at the close of the 100th bar (taker + slip), stop wins on the same bar, one
position per symbol (the busy rule). C0 is pooled across the three symbols, both sides, 2020-01..2024-06; SE by day-block
bootstrap (2,000 resamples, seed 20261028, FORMULAS 18.7).

Expected, from RESULT.md (E2, run once): C0 n 420 on 332 entry days, mean net R +0.1312, SE 0.0760, t +1.73,
mean gross R +0.1527, mean fee R 0.0861 (4 x fee 0.0861 vs gross 0.1527 -> gross < 4x fee). This recount matches to
those within 1 % or names each mismatch.

    python MyTradingSys/research/fable_run6_powered_prereg/recount_o2.py            # prints the C0 block
    python MyTradingSys/research/fable_run6_powered_prereg/recount_o2.py --check    # also assert the E2 published numbers
"""
import argparse
import csv
import datetime as dt
import io
import math
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'MyTradingSys' / 'backtest' / 'layers' / 'krown'))
import krown_core as kc          # noqa: E402
import krown_events as ke        # noqa: E402

# ---- frozen constants (PRE_REG s2 items 6-8; cross-checked against e2_run.py) ----------------------------------
DAY = 86400000
H4 = 4 * 3600 * 1000
LO_MS = (dt.date(2020, 1, 1) - dt.date(1970, 1, 1)).days * DAY                 # DEV+DEV_EXT start
CUT_MS = (dt.date(2024, 7, 1) - dt.date(1970, 1, 1)).days * DAY              # sealed cut: first VALIDATION millisecond
WARMUP_FROM, LAST_MONTH = '2019-09', '2024-06'
SYMBOLS = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT')
TAKER, MAKER, SLIP = 0.0005, 0.0002, 0.0002        # SOURCED backtest/fees.py:27-28; slippage OURS (sim_desk SLIP_DEFAULT)
FLOOR = 0.0056                                     # OURS: 4 x 14 bp of the fill
TARGET_R, STOP_BARS, HOLD_BARS = 2.0, 10, 100      # OURS (sim_desk/studies/krown.py)
RESAMPLES, SEED = 2000, 20261028
DAYS_NEEDED, Z_HOLM = 439, 3.364                   # PRE_REG s1 (m = 65)


def _default_cache():
    """O2_KLINE_CACHE override, else the O2 cache, else the E2 run's own cache (same {sym}-4h-{ym}.csv layout)."""
    for d in ('F:/MTS/data/fable_run6_klines_o2', 'F:/MTS/data/fable_run6_klines'):
        if Path(d).exists():
            return Path(d)
    return Path('F:/MTS/data/fable_run6_klines_o2')


DATA = Path(os.environ.get('O2_KLINE_CACHE', _default_cache()))
KEEP = ('open_time', 'open', 'high', 'low', 'close')

# E2 published C0 (RESULT.md), for --check; compared, never the source of the recount itself.
# RESULT.md headline: "mean gross R +0.1527 vs 4 x mean fee R 0.0861" -> mean fee R = 0.0861/4 = 0.0215 (cell detail table).
PUBLISHED = dict(n=420, days=332, mean=0.1312, se=0.0760, t=1.73, gross=0.1527, fee=0.0215, fee4x=0.0861)


def months(first, last):
    y, m = map(int, first.split('-'))
    out = []
    while f'{y:04d}-{m:02d}' <= last:
        out.append(f'{y:04d}-{m:02d}')
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def fetch_month(sym, ym):
    """Cached csv path, or None when the month does not exist upstream (NOT_IN_DATA)."""
    DATA.mkdir(parents=True, exist_ok=True)
    f = DATA / f'{sym}-4h-{ym}.csv'
    miss = DATA / f'{sym}-4h-{ym}.missing'
    if f.exists():
        return f
    if miss.exists():
        return None
    url = f'https://data.binance.vision/data/futures/um/monthly/klines/{sym}/4h/{sym}-4h-{ym}.zip'
    try:
        raw = urllib.request.urlopen(url, timeout=40).read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            miss.write_text('404\n')
            return None
        raise
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        f.write_bytes(z.read(z.namelist()[0]))
    return f


def guard(rows, what):
    """Raise if any bar at/after the sealed cut survived the load (the O2 test plants one and expects this to fail)."""
    if rows and max(r[0] for r in rows) >= CUT_MS:
        raise ValueError(f'{what}: a bar at or after the sealed cut 2024-07-01 survived the load; refusing')


def assert_no_sealed(rows, what):
    guard(rows, what)


def load(sym, log=print):
    """[(open_time ms, o, h, l, c)] over 2019-09..2024-06; sealed bars dropped at load; only the five OHLC columns kept."""
    rows, missing = [], []
    for ym in months(WARMUP_FROM, LAST_MONTH):
        f = fetch_month(sym, ym)
        if f is None:
            missing.append(ym)
            continue
        with open(f, encoding='utf-8') as fh:
            rd = csv.reader(fh)
            first = next(rd)
            if first and first[0].isdigit():
                header = list(KEEP)
                fh.seek(0)
                rd = csv.reader(fh)
            else:
                header = [h.strip().lower() for h in first]
            idx = [header.index(k) if k in header else i for i, k in enumerate(KEEP)]
            for parts in rd:
                if not parts or not parts[0].isdigit():
                    continue
                t = int(parts[idx[0]])
                if t >= CUT_MS:                            # dropped at load, before any computation
                    continue
                rows.append((t, float(parts[idx[1]]), float(parts[idx[2]]), float(parts[idx[3]]), float(parts[idx[4]])))
    rows.sort()
    rows = [r for i, r in enumerate(rows) if i == 0 or r[0] != rows[i - 1][0]]
    guard(rows, f'{sym} 4h')
    log(f'{sym} 4h: {len(rows)} bars; months NOT_IN_DATA: {len(missing)}')
    return rows


# ---- trade model (re-derived from PRE_REG s2 items 6-8) ---------------------------------------------------------

def signals(bars):
    """[(bar index, +1 long / -1 short)] for every S8 event, whole history; the window filter is the caller's."""
    h, l, c = ([float(b[k]) for b in bars] for k in (2, 3, 4))
    p = kc.load_params()
    ev = ke.setup_s8(kc.bbwp(c, p['bbwp_basis'], p['bbwp_lookback'], p['bbwp_mult']), h, l, c, p)
    return [(e['i'], 1 if e['side'] == 'long' else -1) for e in ev if e['i'] >= STOP_BARS]


def stop_for(bars, i, side):
    win = bars[i - STOP_BARS + 1:i + 1]
    return min(b[3] for b in win) if side > 0 else max(b[2] for b in win)


def run_trade(side, bars, e, stop):
    """One trade entered at the open of bars[e]; None when the stop is under the floor."""
    o = bars[e][1]
    fill = o * (1 + SLIP) if side > 0 else o * (1 - SLIP)
    risk = (fill - stop) * side
    if risk <= 0 or risk / fill < FLOOR:
        return None
    target = fill + side * TARGET_R * risk
    last = min(e + HOLD_BARS - 1, len(bars) - 1)
    for j in range(e, last + 1):
        _, bo, bh, bl, bc = bars[j]
        hit_stop = bl <= stop if side > 0 else bh >= stop
        hit_tgt = bh >= target if side > 0 else bl <= target
        if hit_stop:
            nominal = (min(bo, stop) if side > 0 else max(bo, stop)) if j > e else stop
            px, fee, kind = nominal * (1 - side * SLIP), TAKER, 'stop'
        elif hit_tgt:
            nominal = px = target
            fee, kind = MAKER, 'target'
        elif j == last:
            nominal, px, fee, kind = bc, bc * (1 - side * SLIP), TAKER, 'time'
        else:
            continue
        net = (side * (px - fill) - TAKER * fill - fee * px) / risk
        gross = side * (nominal - o) / risk
        return dict(kind=kind, exit_i=j, net_r=net, gross_r=gross, fee_r=gross - net)
    raise AssertionError('unreachable')


def simulate_symbol(bars, sigs):
    """Signals in [LO_MS, CUT_MS) -> trades with one position at a time. Returns (trades, busy, floor)."""
    trades, busy, floor, free_from = [], 0, 0, -1
    for i, side in sigs:
        t = bars[i][0]
        if not LO_MS <= t < CUT_MS or i + 1 >= len(bars):
            continue
        if i < free_from:                                 # busy rule: a position is still open when the signal bar closed
            busy += 1
            continue
        tr = run_trade(side, bars, i + 1, stop_for(bars, i, side))
        if tr is None:
            floor += 1
            continue
        tr.update(side=side, signal_t=t, entry_t=bars[i + 1][0], day=bars[i + 1][0] // DAY)
        free_from = tr['exit_i']
        trades.append(tr)
    return trades, busy, floor


def bootstrap(trades, key='net_r'):
    """Day-block bootstrap (FORMULAS 18.7): statistic = sum of R over resampled days / events in them."""
    by = {}
    for t in trades:
        by.setdefault(t['day'], []).append(t[key])
    s = np.array([sum(v) for v in by.values()])
    k = np.array([len(v) for v in by.values()], dtype=float)
    idx = np.random.default_rng(SEED).integers(0, len(s), size=(RESAMPLES, len(s)))
    boots = s[idx].sum(axis=1) / k[idx].sum(axis=1)
    mean = float(s.sum() / k.sum())
    se = float(boots.std(ddof=1))
    return dict(n=int(k.sum()), days=len(by), mean=mean, se=se, t=mean / se if se > 0 else float('nan'))


def load_data():
    return {s: load(s) for s in SYMBOLS}


def c0_block(data=None):
    data = data or load_data()
    allt, busy, floor = [], 0, 0
    for s in SYMBOLS:
        tr, b, f = simulate_symbol(data[s], signals(data[s]))
        for t in tr:
            t['sym'] = s
        allt += tr
        busy += b
        floor += f
    st = bootstrap(allt)
    n = len(allt)
    st['gross'] = sum(t['gross_r'] for t in allt) / n
    st['fee'] = sum(t['fee_r'] for t in allt) / n
    st['fee4x'] = 4 * st['fee']
    st.update(busy=busy, floor=floor)
    return st, allt


def freeze_bar_counts(data):
    """The sealed-bar precondition (PRE_REG s2 item 5): all S8 events and distinct UTC days in [LO_MS, CUT_MS),
    checked BEFORE any outcome. E2 expected 807 events on 539 days (+-1 %)."""
    ev, days = 0, set()
    for s in SYMBOLS:
        bars = data[s]
        for i, side in signals(bars):
            t = bars[i][0]
            if LO_MS <= t < CUT_MS:
                ev += 1
                days.add(t // DAY)
    return ev, len(days)


def verdict(c0):
    if c0['days'] < DAYS_NEEDED:
        return 'INCONCLUSIVE'
    ok = c0['mean'] > 0 and c0['t'] >= Z_HOLM and c0['gross'] >= 4 * c0['fee']
    return 'PASS_DEV' if ok else 'FAIL'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--check', action='store_true', help='assert the recount matches the E2 published C0 within 1pct and the freeze bar')
    a = ap.parse_args(argv)
    data = load_data()
    ev, days_ev = freeze_bar_counts(data)
    print(f'freeze bar: {ev} S8 events on {days_ev} days (E2 expected 807 / 539 +-1 %)')
    c0, _ = c0_block(data)
    word = verdict(c0)
    print(f"C0 n {c0['n']} days {c0['days']} mean net {c0['mean']:+.4f} se {c0['se']:.4f} t {c0['t']:+.3f} "
          f"gross {c0['gross']:+.4f} fee {c0['fee']:.4f} (4x fee {4*c0['fee']:.4f}) -> {word}")
    print(f"signals skipped: busy {c0['busy']} floor {c0['floor']}")
    if a.check:
        if not (abs(ev - 807) <= 8 and abs(days_ev - 539) <= 5):
            print(f'  freeze bar MISMATCH: {ev} events / {days_ev} days vs expected 807 / 539')
            return 1
        for key, want in PUBLISHED.items():
            got = c0[key]
            ok = abs(got - want) <= abs(want) * 0.01 if want else got == want
            print(f"  {key}: recount {got} vs published {want} {'OK' if ok else 'MISMATCH'}")
            if not ok:
                print(f'  RECOUNT MISMATCH on {key}: {got} vs {want}')
                return 1
        print('recount matches E2: freeze bar 807/539 and C0 within 1 %')
    return 0


if __name__ == '__main__':
    sys.exit(main())
