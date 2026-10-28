"""Fable run R6: counts-only power screen of the 4h-and-up families (no outcome column, no bar >= 2024-07-01).

Families x timeframes (event rules = the repo's own layer code, unchanged):
  krown_S5 4h   21/55 EMA cross with close on the 200 SMA side        backtest/layers/krown/krown_events.py setup_s5
  krown_S8 4h   BBWP squeeze (<= 30 in last 5 bars) then first bar above the 50th pct, close beyond prior 10 bars  setup_s8
  malkan_rsi 1d, 1w   RSI 14 support at 40 in a BULL regime on a green candle (mirror 60 / BEAR / red)
                backtest/layers/rsi/malkan_40_60.py (tolerance 2, lookback 20 = sim_desk/studies/rsi.py defaults)
  pitchfork 1d  three alternating confirmed ZigZag pivots (lookback 3, 4 % swing), event = P2 confirmation bar
                backtest/layers/pitchfork/pitchfork_detector.py find_pivots_zigzag, as research/pitchfork_2026-10-19/run_pitchfork_event_study.py:134-152
Windows: DEV 2022-01-01..2024-06-30 (D3), DEV_EXT 2020-01-01..2021-12-31 (OPERATOR_DECISIONS D3-dev-ext). Symbols: BTCUSDT, ETHUSDT, SOLUSDT.
Data: public Binance USD-M futures monthly kline zips (data.binance.vision), 4h and 1d; 1w is resampled from 1d (Monday 00:00 UTC weeks).
Cached outside the repo under F:/MTS/data/fable_run6_klines/ (set FABLE_RUN6_DATA to move it). A month that cannot be fetched is
NOT_IN_DATA for that cell; nothing is estimated.
Guards: every bar with open time >= 2024-07-01 00:00Z is dropped at load and asserted absent before any computation; only
open_time/open/high/low/close are ever read (the loader asserts no outcome-like column name is kept).

Per cell: events, distinct UTC days, mean stop width (%), cost_R = mean over events of 14 bp / stop_i (R1 sec. 3: C = 14 bp round trip),
n_needed = ((z_holm(m) + 0.84) * sd / (0.30 - cost_R))^2 in UTC days (same formula as scripts/dev/prereg_gate.py; sd 1.37 R from
R1 sec. 3; plausible 0.30 R, OURS), POWERED = pooled days >= n_needed. m = verdicts.py count --split DEV (--m-base) + new cells per family.

    python MyTradingSys/research/fable_run6_powered_prereg/counts_only.py --m-base 56 [--out COUNTS.csv]
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
from statistics import NormalDist

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'MyTradingSys' / 'backtest' / 'layers' / 'krown'))
import krown_core as kc  # noqa: E402
import krown_events as ke  # noqa: E402
from MyTradingSys.backtest.layers.pitchfork.pitchfork_detector import find_pivots_zigzag  # noqa: E402
from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime, malkan_setup_bear, malkan_setup_bull  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402

DAY = 86400000
CUT_MS = (dt.date(2024, 7, 1) - dt.date(1970, 1, 1)).days * DAY        # first sealed millisecond (VALIDATION starts)
DATA = Path(os.environ.get('FABLE_RUN6_DATA', 'F:/MTS/data/fable_run6_klines'))
BASE = 'https://data.binance.vision/data/futures/um/monthly/klines/{sym}/{tf}/{sym}-{tf}-{ym}.zip'
SYMBOLS = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT')
WARMUP_FROM = '2019-09'            # warm-up only (200 SMA on 4h, RSI 14 + regime 20 on 1w need history before 2020-01)
LAST_MONTH = '2024-06'
WINDOWS = {'DEV': ('2022-01-01', '2024-06-30'), 'DEV_EXT': ('2020-01-01', '2021-12-31')}
FORBIDDEN = ('ret', 'return', 'pnl', 'net', 'gross', 'r', 'outcome', 'mfe', 'mae', 'fwd', 'forward', 'profit', 'label')
KEEP = ('open_time', 'open', 'high', 'low', 'close')
COST_BP = 14.0                     # R1 sec. 3 (SOURCED gross_effect_screen_2026-10-15/PRE_REG.md:28-32): 5+5 taker + 2+2 slippage
SD_R = 1.37                        # R1 sec. 3 (OURS there, from the Krown S5 CI)
PLAUSIBLE_R = 0.30                 # prereg_gate.py MAX_PLAUSIBLE_GROSS (OURS)
POWER_Z = 0.84                     # prereg_gate.py POWER_Z (80 % power)
PF_STOP_PCT = 1.5                  # research/pitchfork_2026-10-19/run_pitchfork_event_study.py:238 "1.5% stop out" (OURS there)
KROWN_STOP_BARS = 10               # sim_desk/studies/krown.py STOP_BARS (OURS there)
NEW_CELLS = {'krown': 2, 'malkan_rsi': 2, 'pitchfork': 1}   # cells this screen would freeze per family (one Holm m per family)


def months(first, last):
    y, m = map(int, first.split('-'))
    out = []
    while f'{y:04d}-{m:02d}' <= last:
        out.append(f'{y:04d}-{m:02d}')
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def day_ms(iso):
    return (dt.date.fromisoformat(iso) - dt.date(1970, 1, 1)).days * DAY


def fetch_month(sym, tf, ym):
    """Monthly zip -> cached csv path, or None when the month does not exist upstream (NOT_IN_DATA)."""
    DATA.mkdir(parents=True, exist_ok=True)
    f = DATA / f'{sym}-{tf}-{ym}.csv'
    miss = DATA / f'{sym}-{tf}-{ym}.missing'
    if f.exists():
        return f
    if miss.exists():
        return None
    url = BASE.format(sym=sym, tf=tf, ym=ym)
    try:
        raw = urllib.request.urlopen(url, timeout=30).read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            miss.write_text('404\n')
            return None
        raise
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = z.namelist()[0]
        f.write_bytes(z.read(name))
    return f


def guard(rows, what):
    if rows and not (max(r[0] for r in rows) < CUT_MS):
        raise ValueError(f'{what}: a bar at or after the sealed cut 2024-07-01 survived the load; refusing')


def load(sym, tf, log):
    """[(open_time ms, o, h, l, c)] from WARMUP_FROM to LAST_MONTH; sealed bars dropped at load; months missing upstream listed."""
    rows, missing = [], []
    for ym in months(WARMUP_FROM, LAST_MONTH):
        f = fetch_month(sym, tf, ym)
        if f is None:
            missing.append(ym)
            continue
        with open(f, encoding='utf-8') as fh:
            rd = csv.reader(fh)
            first = next(rd)
            if first and first[0].isdigit():
                header = ['open_time', 'open', 'high', 'low', 'close']
                fh.seek(0)
                rd = csv.reader(fh)
            else:
                header = [h.strip().lower() for h in first]
            idx = [header.index(k) if k in header else i for i, k in enumerate(KEEP)]
            kept = [header[i] for i in idx]
            assert not any(k in FORBIDDEN for k in kept), f'outcome-like column kept: {kept}'
            for parts in rd:
                if not parts or not parts[0].isdigit():
                    continue
                t = int(parts[idx[0]])
                if t >= CUT_MS:                                  # dropped at load, before any computation
                    continue
                rows.append((t, float(parts[idx[1]]), float(parts[idx[2]]), float(parts[idx[3]]), float(parts[idx[4]])))
    rows.sort()
    rows = [r for i, r in enumerate(rows) if i == 0 or r[0] != rows[i - 1][0]]
    guard(rows, f'{sym} {tf}')
    log(f'{sym} {tf}: {len(rows)} bars {iso(rows[0][0]) if rows else "-"}..{iso(rows[-1][0]) if rows else "-"}; months missing upstream: {len(missing)}')
    return rows, missing


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%Y-%m-%d')


def resample_1w(d1):
    """Monday-aligned UTC weeks from daily bars (1970-01-01 was a Thursday, so week key = (day + 3) // 7)."""
    out = {}
    for t, o, h, l, c in d1:
        k = (t // DAY + 3) // 7
        if k not in out:
            out[k] = [(k * 7 - 3) * DAY, o, h, l, c]
        else:
            b = out[k]
            b[2], b[3], b[4] = max(b[2], h), min(b[3], l), c
    rows = [tuple(out[k]) for k in sorted(out)]
    guard(rows, '1w resample')
    return rows


# ---- event rules (signal time, stop width %) --------------------------------------------------------------------

def krown_events(bars, setup):
    o, h, l, c = ([float(b[i]) for b in bars] for i in (1, 2, 3, 4))
    p = kc.load_params()
    if setup == 'S5':
        ev = ke.setup_s5(kc.crosses(kc.ema(c, p['ma_fast']), kc.ema(c, p['ma_slow'])), c, kc.sma(c, p['ma_long']))
    else:
        ev = ke.setup_s8(kc.bbwp(c, p['bbwp_basis'], p['bbwp_lookback'], p['bbwp_mult']), h, l, c, p)
    out = []
    for e in ev:
        i = e['i']
        if i < KROWN_STOP_BARS:
            continue
        stop = min(l[i - KROWN_STOP_BARS + 1:i + 1]) if e['side'] == 'long' else max(h[i - KROWN_STOP_BARS + 1:i + 1])
        out.append((bars[i][0], abs(c[i] - stop) / c[i] * 100))
    return out


def malkan_events(bars):
    bb = [{'t': b[0], 'o': b[1], 'h': b[2], 'l': b[3], 'c': b[4]} for b in bars]
    rsi = rsi_core([x['c'] for x in bb], 14)
    regime = malkan_regime(rsi, lookback=20)
    sigs = malkan_setup_bull(bb, rsi, regime, tolerance=2.0) + malkan_setup_bear(bb, rsi, regime, tolerance=2.0)
    by_t = {b['t']: b for b in bb}
    out = []
    for s in sigs:
        b = by_t[s['t']]
        entry = b['h'] if s['side'] == 'long' else b['l']           # BREAK entry (trader), stop past the signal candle
        out.append((s['t'], (b['h'] - b['l']) / entry * 100))
    return out


def pitchfork_events(bars):
    highs, lows = [b[2] for b in bars], [b[3] for b in bars]
    piv = find_pivots_zigzag(highs, lows, lookback=3, min_change_pct=0.04)
    out = []
    for i in range(len(piv) - 2):
        p0, p1, p2 = piv[i], piv[i + 1], piv[i + 2]
        if p0.is_high == p1.is_high or p1.is_high == p2.is_high:
            continue
        k = p2.index + 3
        if k >= len(bars):
            continue
        out.append((bars[k][0], PF_STOP_PCT))
    return out


CELLS = [('krown', 'S5', '4h'), ('krown', 'S8', '4h'), ('malkan_rsi', 'rsi40_60', '1d'), ('malkan_rsi', 'rsi40_60', '1w'),
         ('pitchfork', 'triplet', '1d')]


def z_holm(m):
    return NormalDist().inv_cdf(1 - 0.05 / (2 * m))


def n_needed(cost_r, m):
    if PLAUSIBLE_R <= cost_r:
        return float('inf')
    return ((z_holm(m) + POWER_Z) * SD_R / (PLAUSIBLE_R - cost_r)) ** 2


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--m-base', type=int, required=True, help='verdicts.py count --split DEV')
    ap.add_argument('--out', default=str(HERE / 'COUNTS.csv'))
    a = ap.parse_args(argv)
    log = print
    frames = {}
    missing = {}
    for sym in SYMBOLS:
        for tf in ('4h', '1d'):
            frames[sym, tf], missing[sym, tf] = load(sym, tf, log)
        frames[sym, '1w'] = resample_1w(frames[sym, '1d'])
        missing[sym, '1w'] = missing[sym, '1d']
    for key, rows in frames.items():
        guard(rows, f'{key} before computation')
    rows_out = []
    pooled = {}      # (family, rule, tf, window) -> set of UTC days across symbols; (family, rule, tf, 'ALL') too
    stops = {}
    for fam, rule, tf in CELLS:
        for sym in SYMBOLS:
            bars = frames[sym, tf]
            if fam == 'krown':
                ev = krown_events(bars, rule)
            elif fam == 'malkan_rsi':
                ev = malkan_events(bars)
            else:
                ev = pitchfork_events(bars)
            for win, (w0, w1) in WINDOWS.items():
                lo, hi = day_ms(w0), day_ms(w1) + DAY
                miss = [ym for ym in missing[sym, tf] if w0[:7] <= ym <= w1[:7]]
                in_win = [(t, s) for t, s in ev if lo <= t < hi]
                data_from = next((iso(b[0]) for b in bars if lo <= b[0] < hi), None)
                if data_from is None:
                    rows_out.append(dict(family=fam, rule=rule, timeframe=tf, symbol=sym, window=win, events='NOT_IN_DATA', days='NOT_IN_DATA',
                                         mean_stop_pct='', cost_r='', data_from='', months_missing=len(miss), note='no bars in window'))
                    continue
                days = {t // DAY for t, _ in in_win}
                for k in ((fam, rule, tf, win), (fam, rule, tf, 'ALL')):
                    pooled.setdefault(k, set()).update(days)
                    stops.setdefault(k, []).extend(s for _, s in in_win)
                ms = sum(s for _, s in in_win) / len(in_win) if in_win else float('nan')
                cr = sum(COST_BP / (s * 100) for _, s in in_win) / len(in_win) if in_win else float('nan')
                rows_out.append(dict(family=fam, rule=rule, timeframe=tf, symbol=sym, window=win, events=len(in_win), days=len(days),
                                     mean_stop_pct=f'{ms:.3f}', cost_r=f'{cr:.4f}', data_from=data_from, months_missing=len(miss),
                                     note='partial: months missing upstream' if miss else ''))
    # pooled rows: one cluster per UTC day across symbols; family m = m_base + new cells
    for fam, rule, tf in CELLS:
        m = a.m_base + NEW_CELLS[fam]
        for win in ('DEV', 'DEV_EXT', 'ALL'):
            k = (fam, rule, tf, win)
            days = pooled.get(k, set())
            ss = stops.get(k, [])
            cr = sum(COST_BP / (s * 100) for s in ss) / len(ss) if ss else float('nan')
            need = n_needed(cr, m) if ss else float('nan')
            rows_out.append(dict(family=fam, rule=rule, timeframe=tf, symbol='POOLED', window=win if win != 'ALL' else 'DEV+DEV_EXT',
                                 events=len(ss), days=len(days), mean_stop_pct=f'{(sum(ss) / len(ss)) if ss else float("nan"):.3f}',
                                 cost_r=f'{cr:.4f}', data_from='', months_missing='', note=f'm={m} z_holm={z_holm(m):.3f} n_needed={need:.0f} '
                                 f'{"POWERED" if ss and len(days) >= need else "NOT POWERED"}'))
    with open(a.out, 'w', newline='\n', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_out[0].keys()), lineterminator='
')
        w.writeheader()
        w.writerows(rows_out)
    for r in rows_out:
        print(' | '.join(str(r[k]) for k in ('family', 'rule', 'timeframe', 'symbol', 'window', 'events', 'days', 'mean_stop_pct', 'cost_r', 'note')))
    print(f'wrote {a.out} ({len(rows_out)} rows); sealed cut asserted on every frame; columns read: {KEEP}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
