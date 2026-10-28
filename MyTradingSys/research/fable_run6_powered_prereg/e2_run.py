"""E2: run the frozen Krown S8 4h pre-registration (PRE_REG.md section 2) ONCE: BTC+ETH+SOL pooled, DEV stage 2020-01-01..2024-06-30.

Events = counts_only.py's loader and the repo's krown_events.setup_s8 (imported, not copied). Trades on 4h OHLC per PRE_REG items 6-8:
market entry at the next bar's open (taker + slip), stop = far side of the last 10 bars incl. the signal bar (floor 0.56 % of the fill),
target 2R from the fill (maker, touch = fill), time stop at the close of the 100th bar (entry bar + 99, taker + slip), stop wins on the
same bar, one position per symbol. Pooled day-block bootstrap (2,000 resamples, seed 20261028, FORMULAS 18.7). Freeze bar (events 807 +-1 %,
days 539 +-1 %) is checked before any outcome is computed; otherwise BLOCKED.md and exit 2. No bar >= 2024-07-01 is ever loaded.

    python MyTradingSys/research/fable_run6_powered_prereg/e2_run.py            # runs once and writes RESULT.md + 9 trial rows
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import counts_only as co  # noqa: E402
import krown_core as kc   # noqa: E402  (counts_only put backtest/layers/krown on sys.path)
import krown_events as ke  # noqa: E402

DAY, H4 = co.DAY, 4 * 3600 * 1000
LO_MS = co.day_ms('2020-01-01')
HI_MS = co.CUT_MS                          # DEV stage ends 2024-06-30 24:00Z
SPLIT_MS = co.day_ms('2022-01-01')         # DEV_EXT | DEV
TAKER, MAKER, SLIP = 0.0005, 0.0002, 0.0002     # SOURCED backtest/fees.py:27-28; slip OURS (sim_desk/studies/_bars.py SLIP_DEFAULT 0.02 %)
FLOOR = 0.0056                             # OURS: 4 x 14 bp of the fill
TARGET_R, STOP_BARS, HOLD_BARS = 2.0, 10, 100     # OURS (sim_desk/studies/krown.py)
RESAMPLES, SEED = 2000, 20261028
Z_HOLM, DAYS_NEEDED, EV_EXPECT, DAYS_EXPECT = 3.364, 439, 807, 539
KILL = ('FAIL means stop: no detector, chart, layer or management work on the Krown S8 squeeze-break family on 4h BTC, ETH or SOL '
        'with this 10-bar stop; and, this being the last powered family of R1 E1, the R1 section 5 STOP list applies to the BTC trading-edge program.')


def assert_no_sealed(rows, what):
    co.guard(rows, what)


def load_bars(sym):
    rows, _ = co.load(sym, '4h', lambda *_: None)
    assert_no_sealed(rows, sym)
    return rows


def signals(bars):
    """[(bar index, +1 long / -1 short)] for every S8 event, whole history (warm-up included); window filter is the caller's."""
    h, l, c = ([float(b[k]) for b in bars] for k in (2, 3, 4))
    p = kc.load_params()
    ev = ke.setup_s8(kc.bbwp(c, p['bbwp_basis'], p['bbwp_lookback'], p['bbwp_mult']), h, l, c, p)
    return [(e['i'], 1 if e['side'] == 'long' else -1) for e in ev if e['i'] >= STOP_BARS]


def stop_for(bars, i, side):
    win = bars[i - STOP_BARS + 1:i + 1]
    return min(b[3] for b in win) if side > 0 else max(b[2] for b in win)


def run_trade(side, bars, e, stop):
    """One trade entered at the open of bars[e]. None when the stop is under the floor (skipped and counted by the caller)."""
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
        if hit_stop:                                  # stop wins on the same bar; at the open when the bar opens beyond it
            nominal = (min(bo, stop) if side > 0 else max(bo, stop)) if j > e else stop
            px, fee, kind = nominal * (1 - side * SLIP), TAKER, 'stop'
        elif hit_tgt:
            nominal = px = target
            fee, kind = MAKER, 'target'
        elif j == last:                               # time stop (or data end) at the close, taker
            nominal, px, fee, kind = bc, bc * (1 - side * SLIP), TAKER, 'time'
        else:
            continue
        net = (side * (px - fill) - TAKER * fill - fee * px) / risk
        gross = side * (nominal - o) / risk
        return dict(kind=kind, exit_i=j, net_r=net, gross_r=gross, fee_r=gross - net, risk_pct=risk / fill * 100)
    raise AssertionError('unreachable')


def simulate_symbol(bars, sigs, lo_ms=LO_MS, hi_ms=HI_MS):
    """Signals in [lo, hi) -> trades with one position at a time. Returns (trades, skipped_busy, skipped_floor)."""
    trades, busy, floor, free_from = [], 0, 0, -1
    for i, side in sigs:
        t = bars[i][0]
        if not lo_ms <= t < hi_ms or i + 1 >= len(bars):
            continue
        if i < free_from:                              # position still open when the signal bar closed
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
    """Day-block bootstrap (FORMULAS 18.7): statistic = sum of R over resampled days / events in them. Returns mean, se, t, days."""
    if not trades:
        return dict(n=0, days=0, mean=float('nan'), se=float('nan'), t=float('nan'))
    by = {}
    for t in trades:
        by.setdefault(t['day'], []).append(t[key])
    s = np.array([sum(v) for v in by.values()])
    k = np.array([len(v) for v in by.values()], dtype=float)
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(s), size=(RESAMPLES, len(s)))
    boots = s[idx].sum(axis=1) / k[idx].sum(axis=1)
    mean = float(s.sum() / k.sum())
    se = float(boots.std(ddof=1))
    return dict(n=int(k.sum()), days=len(by), mean=mean, se=se, t=mean / se if se > 0 else float('nan'))


def arm_stats(trades):
    st = bootstrap(trades)
    n = len(trades)
    st['gross'] = sum(t['gross_r'] for t in trades) / n if n else float('nan')
    st['fee'] = sum(t['fee_r'] for t in trades) / n if n else float('nan')
    return st


def verdict(c0):
    if c0['days'] < DAYS_NEEDED:
        return 'INCONCLUSIVE'
    ok = c0['mean'] > 0 and c0['t'] >= Z_HOLM and c0['gross'] >= 4 * c0['fee']
    return 'PASS_DEV' if ok else 'FAIL'


def comparator(data, sig_t):
    """Descriptive, no verdict: the same bracket at the open of every non-signal 4h bar (both sides, overlapping allowed), n and mean."""
    nets, n = 0.0, 0
    for sym, bars in data.items():
        for j in range(STOP_BARS + 1, len(bars)):
            if not LO_MS <= bars[j][0] < HI_MS or bars[j - 1][0] in sig_t[sym]:
                continue
            for side in (1, -1):
                tr = run_trade(side, bars, j, stop_for(bars, j - 1, side))
                if tr:
                    nets += tr['net_r']
                    n += 1
    return n, (nets / n if n else float('nan'))


def f(x, d=3):
    return 'nan' if x != x else f'{x:+.{d}f}'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--no-write', action='store_true', help='print only; do not write RESULT.md / trial rows')
    a = ap.parse_args(argv)
    data = {s: load_bars(s) for s in co.SYMBOLS}
    sigs = {s: signals(b) for s, b in data.items()}
    # ---- freeze bar, before any outcome ----
    ev_t = [(s, data[s][i][0]) for s in co.SYMBOLS for i, _ in sigs[s] if LO_MS <= data[s][i][0] < HI_MS]
    n_ev, n_days = len(ev_t), len({t // DAY for _, t in ev_t})
    if abs(n_ev - EV_EXPECT) > EV_EXPECT * 0.01 or abs(n_days - DAYS_EXPECT) > DAYS_EXPECT * 0.01:
        (HERE / 'BLOCKED.md').write_text(f'# BLOCKED: freeze bar failed\n\nevents {n_ev} (expect {EV_EXPECT} +-1 %), days {n_days} (expect {DAYS_EXPECT} +-1 %). No outcome computed.\n',
                                         encoding='utf-8', newline='\n')
        print(f'BLOCKED: events {n_ev}, days {n_days}')
        return 2
    print(f'freeze bar OK: {n_ev} events on {n_days} days')
    per = {}
    skipped = dict(busy=0, floor=0)
    for s in co.SYMBOLS:
        tr, busy, floor = simulate_symbol(data[s], sigs[s])
        for t in tr:
            t['sym'] = s
        per[s] = tr
        skipped['busy'] += busy
        skipped['floor'] += floor
    allt = [t for s in co.SYMBOLS for t in per[s]]
    cells = [('C0', 'pooled BTC+ETH+SOL, both sides, 2020-01..2024-06', allt)]
    for k, s in enumerate(co.SYMBOLS, 1):
        cells.append((f'C{k}', f'{s} only', per[s]))
    cells.append(('C4', 'long only', [t for t in allt if t['side'] > 0]))
    cells.append(('C5', 'short only', [t for t in allt if t['side'] < 0]))
    cells.append(('C6', 'DEV_EXT 2020-01..2021-12', [t for t in allt if t['signal_t'] < SPLIT_MS]))
    cells.append(('C7', 'DEV 2022-01..2024-06', [t for t in allt if t['signal_t'] >= SPLIT_MS]))
    cells.append(('C8', 'BTCUSDT x DEV 2022-01..2024-06', [t for t in per['BTCUSDT'] if t['signal_t'] >= SPLIT_MS]))
    stats = {cid: arm_stats(tr) for cid, _, tr in cells}
    c0 = stats['C0']
    word = verdict(c0)
    years = {}
    for t in allt:
        y = dt.datetime.fromtimestamp(t['signal_t'] / 1000, dt.timezone.utc).year
        years.setdefault(y, []).append(t['net_r'])
    kinds = {k: sum(1 for t in allt if t['kind'] == k) for k in ('stop', 'target', 'time')}
    cmp_n, cmp_mean = comparator(data, {s: {data[s][i][0] for i, _ in sigs[s]} for s in co.SYMBOLS})
    print(f'C0 n {c0["n"]} days {c0["days"]} mean net {c0["mean"]:+.4f} se {c0["se"]:.4f} t {c0["t"]:.3f} gross {c0["gross"]:+.4f} fee {c0["fee"]:.4f} -> {word}')
    if a.no_write:
        return 0
    write_outputs(cells, stats, word, years, kinds, skipped, cmp_n, cmp_mean, n_ev, n_days)
    return 0


def write_outputs(cells, stats, word, years, kinds, skipped, cmp_n, cmp_mean, n_ev, n_days):
    c0 = stats['C0']
    today = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
    arms = '\n'.join(f'| {cid} {desc} | {stats[cid]["n"]} | {f(stats[cid]["mean"], 4)} | {stats[cid]["se"]:.4f} | {word if cid == "C0" else "-"} |'
                     for cid, desc, _ in cells)
    detail = '\n'.join(f'| {cid} | {stats[cid]["n"]} | {stats[cid]["days"]} | {f(stats[cid]["gross"], 4)} | {stats[cid]["fee"]:.4f} | '
                       f'{f(stats[cid]["mean"], 4)} | {f(stats[cid]["t"], 2)} |' for cid, _, _ in cells)
    yrs = '\n'.join(f'| {y} | {len(v)} | {f(sum(v) / len(v), 4)} |' for y, v in sorted(years.items()))
    res = f'''# RESULT: E2, Krown S8 squeeze break on 4h, BTC+ETH+SOL pooled, DEV stage 2020-01-01..2024-06-30 (run once {today})

**Verdict: {word}. C0 n {c0["n"]} trades on {c0["days"]} entry days (need >= {DAYS_NEEDED}), mean net R {f(c0["mean"], 4)}, SE {c0["se"]:.4f}, t {f(c0["t"], 2)} (need >= {Z_HOLM}), mean gross R {f(c0["gross"], 4)} vs 4 x mean fee R {4 * c0["fee"]:.4f}.**

PRE_REG.md (same folder) precedes this file and is unchanged. Code: `e2_run.py` (tests `test_e2_run.py`), one run, seed {SEED}, {RESAMPLES} day-block resamples. VALIDATION 2024-07-01.. and HOLDOUT were not loaded (the loader drops them; tested). Label: NO-RECALL-CLEARANCE (detector recall 3 of 12, `krown_ta101_2026-10-13/RECALL.md`): a hypothesis, never a core. Parameters: fees SOURCED `backtest/fees.py:27-28`; slippage 0.02 %, stop floor 0.56 %, 10-bar stop, 2R target, 100-bar time stop, seed OURS (PRE_REG s2 items 6-8). Net R = side x (exit - fill) minus entry and exit fees, over risk |fill - stop|; fee R = gross R - net R (fees plus slippage).

Freeze bar passed before any outcome: {n_ev} events on {n_days} days (expected {EV_EXPECT} / {DAYS_EXPECT} +-1 %). Signals skipped: {skipped["busy"]} while a position was open, {skipped["floor"]} under the 0.56 % floor. Exits: {kinds["stop"]} stop, {kinds["target"]} target, {kinds["time"]} time.

## Verdict arms

| arm | n | mean net R | SE | verdict |
|---|---|---|---|---|
{arms}

{KILL}

Strata (C1-C8) carry no verdict word and can neither rescue nor kill C0.

## Cell detail

| cell | n | entry days | mean gross R | mean fee R | mean net R | t |
|---|---|---|---|---|---|---|
{detail}

## Year table (descriptive: signal year; n, mean net R; no t, no verdict)

| year | n | mean net R |
|---|---|---|
{yrs}

## Descriptive comparator (no verdict)

The same bracket at the open of every 4h bar that is not a signal bar (both sides, stop = far side of the 10 bars before it, overlapping allowed, same symbols and window): n {cmp_n}, mean net R {f(cmp_mean, 4)}.
'''
    (HERE / 'RESULT.md').write_text(res, encoding='utf-8', newline='\n')
    ms = REPO / 'MyTradingSys' / 'research'
    cmd = '`python MyTradingSys/research/fable_run6_powered_prereg/e2_run.py`'
    rows_md, rows_csv = [], []
    for cid, desc, _ in cells:
        s = stats[cid]
        res_txt = (f'n {s["n"]}, entry days {s["days"]}, mean net R {f(s["mean"], 4)}, t {f(s["t"], 2)}'
                   + (f'; verdict {word}' if cid == 'C0' else '; stratum, no verdict'))
        rows_md.append(f'| {today} | krown S8 4h E2 {cid} {desc} (target 2R, stop 10 bars, taker 0.05 % + slip 0.02 %, maker 0.02 %) | {cmd} | '
                       f'DEV stage 2020-01-01..2024-06-30; VALIDATION/HOLDOUT never loaded | {res_txt} |')
        rows_csv.append(f'fable_run6_powered_prereg,E2_{cid},{today},DEV,data.binance.vision USD-M 4h klines (F:/MTS/data/fable_run6_klines),'
                        f'"krown S8 4h {desc}; {res_txt}",run-once')
    with open(ms / 'layer_lab' / 'TRIALS.md', 'a', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(rows_md) + '\n')
    with open(ms / 'TRIAL_LEDGER.csv', 'a', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(rows_csv) + '\n')
    print(f'wrote RESULT.md and 9 trial rows; verdict {word}')


if __name__ == '__main__':
    sys.exit(main())
