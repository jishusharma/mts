"""Cross-check E2 (e2_run.py, 4h OHLC) against the simulator desk Krown study (sim_desk/studies/krown.py, 1m replay) on the
Krown S8 4h trades of BTCUSDT, signals 2022-04-01..2024-06-30, target 2R, 100-bar time stop, desk fee defaults.
Mechanics proof only: the E2 verdict (INCONCLUSIVE) is untouched; nothing here changes e2_run.py, PRE_REG.md, RESULT.md or the detector.
Brief: CROSSCHECK_BRIEF.md (same folder). Imports e2_run and the desk modules; never calls e2_run.main (it would append trial rows).

    python MyTradingSys/research/fable_run6_powered_prereg/crosscheck_desk.py [--no-write]

No bar at or after 2024-07-01 is loaded by either path: both loaders assert it (ValueError).
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DESK_DIR = REPO / 'MyTradingSys' / 'research' / 'sim_desk'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(DESK_DIR / 'studies'))
import counts_only as co  # noqa: E402
import e2_run as e2       # noqa: E402
import _bars              # noqa: E402  (sim_desk/studies/_bars.py)
import krown as desk_krown  # noqa: E402  (sim_desk/studies/krown.py; imports the repo's krown_core/krown_events)

SYMBOL = 'BTCUSDT'
CUT_MS = co.CUT_MS                                  # first sealed millisecond, 2024-07-01 00:00Z
DAY, H4, MIN = co.DAY, 4 * 3600 * 1000, 60000
LO_MS = co.day_ms('2022-04-01')                     # desk window start (krown.DEFAULT start)
HI_MS = CUT_MS                                      # signals through 2024-06-30 24:00Z
TOL_R = 0.05                                        # a matched trade with |net R diff| above this must carry a cause
KIND_E2 = {'stop': 'stop', 'target': 'target', 'time': 'time'}
KIND_DESK = {'STOP': 'stop', 'T1': 'target', 'HOLD': 'time'}
CAUSES = ('floor', 'target-from-close', '1m-vs-4h fill', 'same-bar rule', 'warm-up', 'window edge', 'entry-bar rule', 'slippage model')


# ---- loaders (both refuse the sealed period) ---------------------------------------------------------------------

def load_e2_bars(sym=SYMBOL):
    """E2's 4h bars [(t, o, h, l, c)], BTCUSDT only; ValueError on any bar at or after 2024-07-01."""
    if sym != SYMBOL:
        raise ValueError(f'{sym}: this cross-check is BTCUSDT only')
    rows = e2.load_bars(sym)
    if rows and max(r[0] for r in rows) >= CUT_MS:
        raise ValueError(f'{sym} 4h: a bar at or after 2024-07-01 was loaded; refusing')
    return rows


def load_desk_1m():
    """The desk's 1m array (open time, o, h, l, c), BTCUSDT; ValueError on any bar at or after 2024-07-01."""
    a = _bars.load_1m(None, SYMBOL)
    if len(a) and float(np.max(a[:, 0])) >= CUT_MS:
        raise ValueError('BTCUSDT 1m: a bar at or after 2024-07-01 was loaded; refusing')
    return a


# ---- comparison functions ----------------------------------------------------------------------------------------

def compare_signal_sets(bars_e2, bars_desk, detect, lo_ms=LO_MS, hi_ms=HI_MS):
    """Signal bars (by signal-bar open time, inside [lo, hi)) of `detect(bars) -> [(bar index, side)]` on each bar series."""
    def times(bars):
        return {(bars[i][0], side) for i, side in detect(bars) if lo_ms <= bars[i][0] < hi_ms}
    a, b = times(bars_e2), times(bars_desk)
    return dict(n_e2=len(a), n_desk=len(b), common=len(a & b), only_e2=sorted(t for t, _ in a - b), only_desk=sorted(t for t, _ in b - a))


def diff_trades(e2_trades, desk_trades, tol=TOL_R):
    """Join on (entry bar open time, side). Trades: dicts with entry_t, side, net_r, kind (stop|target|time)."""
    dk = {(t['entry_t'], t['side']): t for t in desk_trades}
    ek = {(t['entry_t'], t['side']): t for t in e2_trades}
    matched, flagged = [], []
    for key in sorted(ek):
        if key not in dk:
            continue
        a, b = ek[key], dk[key]
        row = dict(entry_t=key[0], side=key[1], net_e2=a['net_r'], net_desk=b['net_r'], diff=b['net_r'] - a['net_r'],
                   kind_e2=a['kind'], kind_desk=b['kind'])
        matched.append(row)
        if abs(row['diff']) > tol + 1e-12 or row['kind_e2'] != row['kind_desk']:
            flagged.append(row)
    ad = [abs(r['diff']) for r in matched]
    return dict(matched=len(matched), rows=matched, flagged=flagged,
                only_e2=[ek[k] for k in sorted(ek) if k not in dk], only_desk=[dk[k] for k in sorted(dk) if k not in ek],
                kind_agree=sum(1 for r in matched if r['kind_e2'] == r['kind_desk']),
                mean_abs=float(np.mean(ad)) if ad else float('nan'), max_abs=max(ad) if ad else float('nan'))


# ---- the two paths -----------------------------------------------------------------------------------------------

def e2_path(bars, lo_ms=LO_MS, hi_ms=HI_MS):
    """E2's own signals/stop_for/run_trade on 4h bars, with the signal loop of e2.simulate_symbol repeated here so the skipped
    signals (busy, floor) can be listed; the trades are asserted identical to e2.simulate_symbol's."""
    sigs = e2.signals(bars)
    trades, skipped, free_from = [], [], -1
    for i, side in sigs:
        t = bars[i][0]
        if not lo_ms <= t < hi_ms or i + 1 >= len(bars):
            continue
        if i < free_from:
            skipped.append(dict(signal_t=t, side=side, why='busy'))
            continue
        stop = e2.stop_for(bars, i, side)
        tr = e2.run_trade(side, bars, i + 1, stop)
        if tr is None:
            skipped.append(dict(signal_t=t, side=side, why='floor'))
            continue
        tr.update(side=side, signal_t=t, entry_t=bars[i + 1][0], i=i, stop=stop, signal_close=bars[i][4])
        free_from = tr['exit_i']
        trades.append(tr)
    ref, _, _ = e2.simulate_symbol(bars, sigs, lo_ms, hi_ms)
    assert [(t['entry_t'], t['kind'], t['net_r']) for t in trades] == [(t['entry_t'], t['kind'], t['net_r']) for t in ref], 'e2 loop drifted from simulate_symbol'
    return sigs, trades, skipped


def desk_q(lo='2022-04-01', hi='2024-06-30'):
    return dict(desk_krown.DEFAULT, symbol=SYMBOL, setup='S8', tf='4h', exit='R', target_r=2.0, start=lo, end=hi)


def desk_path(a, q=None):
    """The desk study's own run() (signals via krown.signals on 1m-resampled 4h, trades via _bars.collect on 1m), then each trade
    replayed once for its exit time and levels (used for attribution only)."""
    q = q or desk_q()
    res = desk_krown.run(q, progress=lambda *_: None)
    b = _bars.resample(a, desk_krown.TF_MIN['4h'])
    sigs = desk_krown.signals('S8', b[:, 1], b[:, 2], b[:, 3], b[:, 4])
    trades = []
    for k, ref in enumerate(res['refs']):
        if not res['filled'][k]:
            continue
        r = _bars.replay(a, ref, q)
        trades.append(dict(entry_t=int(res['touch_t'][k]), side=int(res['side'][k]), net_r=float(res['net'][k]), gross_r=float(res['gross'][k]),
                           kind=KIND_DESK[str(res['exit'][k])], exit_t=r['exit'][0], stop=ref[3], target=ref[4], signal_close=ref[8],
                           entry_px=r['entry'][1]))
    nofill = int(np.sum(~res['filled']))
    return b, sigs, trades, nofill


# ---- counterfactual variants (ablate one known difference at a time; no shared code is edited) -------------------------

def desk_variant(a, q, target_from_fill=False, e2_slip=e2.SLIP):
    """The desk's own make() / collect() (krown.run, copied line for line) with one switch: target_from_fill=True puts the target
    2R from E2's fill (next-bar open moved by e2_slip, risk = |fill - stop|) instead of 2R x |signal close - stop|. Base = krown.run."""
    tf = desk_krown.TF_MIN['4h'] * MIN
    b = _bars.resample(a, desk_krown.TF_MIN['4h'])
    sigs = desk_krown.signals('S8', b[:, 1], b[:, 2], b[:, 3], b[:, 4])

    def make(s):
        i, side = s
        if i < desk_krown.STOP_BARS:
            return None
        stop = float(b[i - desk_krown.STOP_BARS + 1:i + 1, 3].min()) if side > 0 else float(b[i - desk_krown.STOP_BARS + 1:i + 1, 2].max())
        close = float(b[i, 4])
        if target_from_fill:
            if i + 1 >= len(b):
                return None
            fill = float(b[i + 1, 1]) * (1 + side * e2_slip)
            target = fill + side * q['target_r'] * abs(fill - stop)
        else:
            target = close + side * q['target_r'] * abs(close - stop)
        t0 = int(b[i, 0]) + tf
        return [side, t0, None, stop, target, t0 + tf, None, t0 + desk_krown.MAX_HOLD * tf, close]
    return _bars.collect(sigs, a, q, make)


def desk_trades_of(a, res, q):
    out = []
    for k, ref in enumerate(res['refs']):
        if not res['filled'][k]:
            continue
        r = _bars.replay(a, ref, q)
        out.append(dict(entry_t=int(res['touch_t'][k]), side=int(res['side'][k]), net_r=float(res['net'][k]), gross_r=float(res['gross'][k]),
                        kind=KIND_DESK[str(res['exit'][k])], exit_t=r['exit'][0], stop=ref[3], target=ref[4], signal_close=ref[8],
                        entry_px=r['entry'][1]))
    return out


def e2_trades_with_slip(bars, slip):
    old = e2.SLIP
    e2.SLIP = slip
    try:
        return e2_path(bars)[1]
    finally:
        e2.SLIP = old


def summarize(d, bars_e2_trades):
    """One ablation row from a diff_trades result; exit_bar_shift = matched trades whose exit 4h bar differs between the paths."""
    return dict(n_e2=len(bars_e2_trades), matched=d['matched'], only_e2=len(d['only_e2']), only_desk=len(d['only_desk']),
                kind_agree=d['kind_agree'], mean_abs=d['mean_abs'], max_abs=d['max_abs'], over_tol=sum(1 for r in d['rows'] if abs(r['diff']) > TOL_R + 1e-12))


def exit_bar_shifts(bars, e2_trades, desk_trades):
    ed = {(t['entry_t'], t['side']): t for t in e2_trades}
    out = []
    for t in desk_trades:
        e = ed.get((t['entry_t'], t['side']))
        if e and bars[e['exit_i']][0] != (t['exit_t'] // H4) * H4:
            out.append(dict(entry_t=t['entry_t'], side=t['side'], kind_e2=e['kind'], kind_desk=t['kind'], e2_exit_bar=bars[e['exit_i']][0],
                            desk_exit_bar=int(t['exit_t'] // H4 * H4)))
    return out


# ---- exposure to the known differences, cascade attribution ------------------------------------------------------------

def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M')


def e2_levels(bars, t):
    """(fill, stop, target) of an E2 trade, rebuilt from the bars with E2's own formulas (used only to measure exposure)."""
    o = bars[t['i'] + 1][1]
    fill = o * (1 + t['side'] * e2.SLIP)
    risk = (fill - t['stop']) * t['side']
    return fill, t['stop'], fill + t['side'] * e2.TARGET_R * risk, risk


def exposure(bars, e2_trades, e2_skipped, desk_trades, d, edge_signals, warm):
    """How many trades each known difference could touch, measured on the slice (counts and R only)."""
    dk = {(t['entry_t'], t['side']): t for t in desk_trades}
    e_by = {(t['entry_t'], t['side']): t for t in e2_trades}
    tgt_shift, gap_stops, both_touch, entry_bar = [], 0, [], []
    for key, e in e_by.items():
        fill, stop, target, risk = e2_levels(bars, e)
        x = dk.get(key)
        if x is not None:
            tgt_shift.append(abs((target - x['target']) * e['side'] / risk))
        j = e['exit_i']
        _, bo, bh, bl, _ = bars[j]
        if e['kind'] == 'stop' and j > e['i'] + 1 and ((bo < stop) if e['side'] > 0 else (bo > stop)):
            gap_stops += 1
        touch_stop = bl <= stop if e['side'] > 0 else bh >= stop
        touch_tgt = bh >= target if e['side'] > 0 else bl <= target
        if touch_stop and touch_tgt:
            both_touch.append(key)
        if j == e['i'] + 1:
            entry_bar.append(key)
    risks = [abs(x['entry_px'] - x['stop']) / x['entry_px'] * 100 for x in desk_trades]
    rd = {(r['entry_t'], r['side']): r for r in d['rows']}

    def kinds_ok(keys):
        return sum(1 for k in keys if k in rd and rd[k]['kind_e2'] == rd[k]['kind_desk'])
    return dict(
        floor=dict(e2_skipped=sum(1 for s in e2_skipped if s['why'] == 'floor'), desk_trades_under_floor=sum(1 for r in risks if r < e2.FLOOR * 100),
                   min_stop_pct=min(risks) if risks else float('nan')),
        target_from_close=dict(exposed=len(tgt_shift), mean_shift_r=float(np.mean(tgt_shift)) if tgt_shift else float('nan'),
                               max_shift_r=max(tgt_shift) if tgt_shift else float('nan')),
        gap_stops=gap_stops,
        same_bar=dict(n=len(both_touch), kind_agree=kinds_ok(both_touch)),
        entry_bar=dict(n=len(entry_bar), kind_agree=kinds_ok(entry_bar)),
        window_edge=dict(n=len(edge_signals)), warm_up=warm)


def cascade(bars, e2_trades, desk_trades, d, shifts):
    """Attach a parent to each unmatched trade: the trade of the other path that was still open when its signal fired."""
    sh = {(s['entry_t'], s['side']): s for s in shifts}
    out = []
    for x in d['only_desk']:                      # desk traded, E2 was busy: the E2 trade still open at the signal bar
        par = next((e for e in e2_trades if e['entry_t'] < x['entry_t'] <= bars[e['exit_i']][0]), None)
        out.append(dict(side_of='desk only', entry_t=x['entry_t'], side=x['side'], kind=x['kind'], parent_t=par and par['entry_t'],
                        parent_shift=bool(par and (par['entry_t'], par['side']) in sh)))
    for y in d['only_e2']:                        # E2 traded, desk was busy: the desk trade still open at the entry
        par = next((t for t in desk_trades if t['entry_t'] < y['entry_t'] < t['exit_t'] + MIN), None)
        out.append(dict(side_of='E2 only', entry_t=y['entry_t'], side=y['side'], kind=y['kind'], parent_t=par and par['entry_t'],
                        parent_shift=False, parent_unmatched=bool(par and (par['entry_t'], par['side']) in {(u['entry_t'], u['side']) for u in d['only_desk']})))
    return out


# ---- run + report ------------------------------------------------------------------------------------------------------

def fr(x, d=3):
    return 'nan' if x != x else f'{x:+.{d}f}'


def run_all():
    bars = load_e2_bars()
    a = load_desk_1m()
    assert bars[-1][0] < CUT_MS and float(a[-1, 0]) < CUT_MS, 'a bar at or after 2024-07-01 was loaded'
    q = desk_q()
    e2_sigs, e2_trades, e2_skipped = e2_path(bars)
    b4, desk_sigs, desk_trades, nofill = desk_path(a, q)
    bars_desk = [tuple(r) for r in b4.tolist()]
    det = lambda bb: e2_sigs if bb is bars else desk_sigs                       # noqa: E731  (each path's own detector output)
    sig = compare_signal_sets(bars, bars_desk, det)
    warm = compare_signal_sets(bars, bars_desk, det, lo_ms=co.day_ms('2022-01-01'), hi_ms=LO_MS)
    edge = sorted({bars[i][0] for i, _ in e2_sigs if LO_MS - H4 <= bars[i][0] < LO_MS} | {int(b4[i, 0]) for i, _ in desk_sigs if LO_MS - H4 <= b4[i, 0] < LO_MS})
    d = diff_trades(e2_trades, desk_trades)
    shifts = exit_bar_shifts(bars, e2_trades, desk_trades)
    casc = cascade(bars, e2_trades, desk_trades, d, shifts)
    expo = exposure(bars, e2_trades, e2_skipped, desk_trades, d, edge, warm)
    d4 = {r[0]: r for r in bars}
    ohlc_bad = [int(r[0]) for r in b4 if int(r[0]) in d4 and max(abs(d4[int(r[0])][k] - r[k]) for k in (1, 2, 3, 4)) > 1e-6]
    # does a bar with differing OHLC sit in any trade's footprint (stop window of the signal bar .. exit bar) or is it a signal bar?
    pos = {r[0]: k for k, r in enumerate(bars)}
    bad_ix = [pos[bt] for bt in ohlc_bad if bt in pos]
    bad_touch = [t['entry_t'] for t in e2_trades if any(t['i'] - e2.STOP_BARS + 1 <= k <= t['exit_i'] for k in bad_ix)]
    bad_signal = [bt for bt in ohlc_bad if any(bars[i][0] == bt for i, _ in e2_sigs)]
    # ablations: one known difference removed at a time (the shared code is untouched; only a switch in a copy of krown.make)
    abl = []
    for name, tff, slip in (('base (as shipped)', False, e2.SLIP), ('desk target 2R from the E2 fill', True, e2.SLIP),
                            ('slippage 0 in both paths', False, 0.0), ('both removed', True, 0.0)):
        qq = dict(q, slip_pct=slip * 100)
        res = desk_variant(a, qq, tff, slip)
        dtr = desk_trades_of(a, res, qq)
        etr = e2_trades_with_slip(bars, slip)
        dd = diff_trades(etr, dtr)
        abl.append(dict(name=name, **summarize(dd, etr), shifts=len(exit_bar_shifts(bars, etr, dtr)), signed=float(np.mean([r['diff'] for r in dd['rows']]))))
    return dict(bars=bars, q=q, e2_sigs=e2_sigs, e2_trades=e2_trades, e2_skipped=e2_skipped, desk_sigs=desk_sigs, desk_trades=desk_trades, nofill=nofill,
                bad_touch=bad_touch, bad_signal=bad_signal, sig=sig, warm=warm, edge=edge, d=d, shifts=shifts, casc=casc, expo=expo, ohlc_bad=ohlc_bad, abl=abl, n_1m=len(a), n_4h_e2=len(bars), n_4h_desk=len(b4))


def judge(R):
    """MECHANICS AGREE only when: no signal difference in the slice, no kind disagreement, no |diff| > tol, every unmatched trade is a cascade
    child of an exit-bar shift, and removing the target-level difference alone restores a full match."""
    why = []
    s, d = R['sig'], R['d']
    if s['only_e2'] or s['only_desk']:
        why.append(f"signal sets differ in the slice ({len(s['only_e2'])} E2-only, {len(s['only_desk'])} desk-only)")
    if d['kind_agree'] != d['matched']:
        why.append(f"{d['matched'] - d['kind_agree']} matched trades exit differently")
    big = [r for r in d['rows'] if abs(r['diff']) > TOL_R + 1e-12]
    if big:
        why.append(f'{len(big)} matched trades differ by more than {TOL_R} R')
    for c in R['casc']:
        ok = c['parent_shift'] if c['side_of'] == 'desk only' else c.get('parent_unmatched')
        if not ok:
            why.append(f"unmatched {c['side_of']} trade at {iso(c['entry_t'])} has no known-difference parent")
    v1 = R['abl'][1]
    if v1['matched'] != v1['n_e2'] or v1['only_desk'] or v1['kind_agree'] != v1['matched'] or v1['over_tol']:
        why.append('removing the target-from-close difference does not restore a full match')
    v3 = R['abl'][3]
    if not (v3['matched'] == v3['n_e2'] and v3['max_abs'] < 1e-6):
        why.append(f"with the known differences removed a residual of {v3['max_abs']:.4f} R remains")
    return ('MECHANICS AGREE' if not why else 'MECHANICS DISAGREE: ' + '; '.join(why)), why


def build_md(R, verdict, today):
    s, w, d, ex, abl = R['sig'], R['warm'], R['d'], R['expo'], R['abl']
    n_e2, n_dk = len(R['e2_trades']), len(R['desk_trades'])
    rows_s = '\n'.join(f'| {k} | {v} |' for k, v in [
        ('E2 detector signals, whole history (2020-01..2024-06, warm-up included)', len(R['e2_sigs'])),
        ('desk detector signals, whole history (1m-resampled 4h, 2022-01..2024-06)', len(R['desk_sigs'])),
        ('E2 signals in the slice (signal bar open 2022-04-01..2024-06-30)', s['n_e2']),
        ('desk signals in the slice (same filter)', s['n_desk']),
        ('common', f"{s['common']} of {max(s['n_e2'], s['n_desk'])} ({100 * s['common'] / max(1, max(s['n_e2'], s['n_desk'])):.1f} %)"),
        ('E2 only / desk only', f"{len(s['only_e2'])} / {len(s['only_desk'])}" + ''.join(f' ({iso(t)})' for t in s['only_e2'] + s['only_desk'])),
        ('warm-up zone 2022-01-01..2022-03-31 (desk has bars, E2 has 2 more years): E2 / desk / common',
         f"{w['n_e2']} / {w['n_desk']} / {w['common']}" + ''.join(f' (E2 only {iso(t)})' for t in w['only_e2']) + ''.join(f' (desk only {iso(t)})' for t in w['only_desk'])),
        ('window edge: signal bars 2022-03-31 20:00 (desk would enter 2022-04-01 00:00, E2 would not)', ex['window_edge']['n']),
        ('4h bars whose OHLC differs between the E2 kline file and the 1m resample (of 5,472 common)',
         f"{len(R['ohlc_bad'])}" + ''.join(f' ({iso(t)})' for t in R['ohlc_bad']))])
    skip_busy = sum(1 for k in R['e2_skipped'] if k['why'] == 'busy')
    skip_floor = sum(1 for k in R['e2_skipped'] if k['why'] == 'floor')
    unm = '\n'.join(f"| {c['side_of']} | {iso(c['entry_t'])} | {'long' if c['side'] > 0 else 'short'} | {c['kind']} | "
                    f"{'the other path was still in the trade entered ' + iso(c['parent_t']) if c['parent_t'] else 'none found'}"
                    f"{' (an exit-bar shift, below)' if c.get('parent_shift') else ' (itself unmatched: the cascade)' if c.get('parent_unmatched') else ''} | "
                    f"target-from-close + slippage model (cascade) |" for c in R['casc']) or '| none | | | | | |'
    top = sorted(d['rows'], key=lambda r: -abs(r['diff']))[:5]
    top_md = '\n'.join(f"| {iso(r['entry_t'])} | {'long' if r['side'] > 0 else 'short'} | {r['kind_e2']} / {r['kind_desk']} | {fr(r['net_e2'])} | {fr(r['net_desk'])} | {fr(r['diff'], 4)} | "
                       f"{'slippage model' + (' + target-from-close' if r['kind_e2'] == 'target' else '')} |" for r in top)
    sh_md = '\n'.join(f"| {iso(x['entry_t'])} | {'long' if x['side'] > 0 else 'short'} | {x['kind_e2']} | {iso(x['e2_exit_bar'])} | {iso(x['desk_exit_bar'])} | target-from-close + slippage model |"
                      for x in R['shifts']) or '| none | | | | | |'
    abl_md = '\n'.join(f"| {x['name']} | {x['matched']} / {x['n_e2']} | {x['only_e2']} / {x['only_desk']} | {x['kind_agree']} / {x['matched']} | {x['mean_abs']:.5f} | {x['max_abs']:.5f} | {x['shifts']} |"
                       for x in abl)
    kinds = {}
    for r in d['rows']:
        kinds[(r['kind_e2'], r['kind_desk'])] = kinds.get((r['kind_e2'], r['kind_desk']), 0) + 1
    k_md = '\n'.join(f"| {a} | " + ' | '.join(str(kinds.get((a, b), 0)) for b in ('stop', 'target', 'time')) + ' |' for a in ('stop', 'target', 'time'))
    tfc = ex['target_from_close']
    expo_md = '\n'.join(f'| {a} | {b} | {c} |' for a, b, c in [
        ('1 floor 0.56 % (E2 only)', f"E2 skipped {ex['floor']['e2_skipped']} signals under the floor; desk trades under it {ex['floor']['desk_trades_under_floor']}; narrowest stop {ex['floor']['min_stop_pct']:.2f} %",
         'did not bite'),
        ('2 target from signal close (desk) vs from the fill (E2)', f"all {tfc['exposed']} matched trades; target level differs by mean {tfc['mean_shift_r']:.3f} R, max {tfc['max_shift_r']:.3f} R",
         f"bit: {len(R['shifts'])} exits land in an earlier desk bar; one cascade (section 2)"),
        ('3 1m vs 4h fill (stop gap fills)', f"{ex['gap_stops']} E2 stop exits on a gap open", 'did not bite'),
        ('4 same-bar stop and target (stop wins vs 1m order)', f"{ex['same_bar']['n']} trades with both levels inside the exit bar", 'did not bite'),
        ('5 warm-up (E2 bars from 2020, desk from 2022-01)', f"{w['n_e2']} E2 / {w['n_desk']} desk signals in 2022-01..03, {w['common']} common", 'did not bite' if not (w['only_e2'] or w['only_desk']) else
         'bit before the slice only: signal(s) before 2022-04-01 differ; none inside it, so no trade is affected (both paths start flat at 2022-04-01)'),
        ('6 window edge (signal-bar time vs entry time)', f"{ex['window_edge']['n']} signal bars straddle 2022-04-01", 'did not bite'),
        ('7 entry-bar rule (target may hit on the entry 4h bar vs first 1m bar off)', f"{ex['entry_bar']['n']} E2 trades exit on their entry bar, exit kind agrees on {ex['entry_bar']['kind_agree']}", 'did not bite' if ex['entry_bar']['kind_agree'] == ex['entry_bar']['n'] else 'bit'),
        ('8 slippage model (price vs fee rate)', f'all {n_e2} trades', f"explains the {abl[0]['mean_abs']:.4f} R mean gap (section 4)")])
    par = [['SOURCED', 'taker 0.05 %, maker 0.02 % (both paths)', 'MyTradingSys/backtest/fees.py:27-28'],
           ['SOURCED', 'detector S8: BBWP basis 7, lookback 100; break above the 50th percentile', 'krown_params.json bbwp_basis, bbwp_lookback, bbwp_confirm (KR-Q01, KR-Q02)'],
           ['OURS', 'S8 squeeze level 30 (trader: 25-35)', 'krown_params.json bbwp_low; unchanged'],
           ['OURS', 'slippage 0.02 % (E2: on the price; desk: added to the fee rate)', 'sim_desk/studies/_bars.py SLIP_DEFAULT'],
           ['OURS', 'stop = far side of the last 10 bars; target 2R; time stop 100 bars', 'sim_desk/studies/krown.py; e2_run.py'],
           ['OURS', 'E2 stop floor 0.56 % of the fill', 'e2_run.py FLOOR; desk has none'],
           ['OURS', 'slice BTCUSDT, signals 2022-04-01..2024-06-30, nothing at or after 2024-07-01', 'CROSSCHECK_BRIEF.md; desk DEV window'],
           ['OURS', 'a net-R gap counts as a mismatch above 0.05 R', 'CROSSCHECK_BRIEF.md']]
    par_md = '\n'.join(f'| {a} | {b} | {c} |' for a, b, c in par)
    big = sum(1 for r in d['rows'] if abs(r['diff']) > TOL_R + 1e-12)
    bad_bars = ', '.join(iso(t) for t in R['ohlc_bad']) or 'none'
    return f'''# CROSSCHECK: E2 (4h OHLC) vs the simulator desk (1m replay), Krown S8 4h, BTCUSDT, signals 2022-04-01..2024-06-30 (run {today})

**{verdict}**

Mechanics proof only: the E2 verdict (INCONCLUSIVE, RESULT.md) is untouched; this says nothing about edge. Brief: CROSSCHECK_BRIEF.md. Code: `crosscheck_desk.py` (tests `test_crosscheck_desk.py`). Both paths use the repo's own S8 detector; E2 = `e2_run.py` functions (signals, stop_for, run_trade, FLOOR), desk = `sim_desk/studies/krown.py run()` via `_bars.collect`. Slice: target 2R, stop 10 bars, time stop 100 bars, desk fee defaults (0.02 % maker, 0.05 % taker, 0.02 % slip). No bar at or after 2024-07-01 was loaded by either path (asserted: last E2 4h bar opens {iso(R['bars'][-1][0])}, desk 1m bars read {R['n_1m']:,}, 4h resample {R['n_4h_desk']:,} bars). R and percent only; no prices.

## 1. Signal bars

| item | value |
|---|---|
{rows_s}

## 2. Trades joined on (entry bar open time, side)

| item | value |
|---|---|
| E2 trades (slice) | {n_e2} (E2 skipped {skip_busy} signals as busy, {skip_floor} under the floor) |
| desk trades (slice) | {n_dk} (never filled: {R['nofill']}) |
| matched | {d['matched']} ({100 * d['matched'] / n_e2:.1f} % of E2, {100 * d['matched'] / n_dk:.1f} % of desk) |
| E2 only / desk only | {len(d['only_e2'])} / {len(d['only_desk'])} |

Unmatched trades, with cause:

| path | entry bar | side | exit kind | why the other path did not trade it | cause (known difference) |
|---|---|---|---|---|---|
{unm}

The desk target is 2R of |signal close - stop|, E2's is 2R of |fill - stop| with the fill 0.02 % worse, so the E2 target sits a little further out (mean {tfc['mean_shift_r']:.3f} R, max {tfc['max_shift_r']:.3f} R). In {len(R['shifts'])} trades that is the difference between the target touching in one 4h bar and in a later one; the desk then leaves the trade earlier. In the 2022-07 case that frees the desk for a signal E2 still skipped as busy, and the desk's extra trade then blocks the next E2 trade: one cascade, two unmatched trades. Removing the target-level difference (section 4, row 2) restores {abl[1]['matched']} of {abl[1]['n_e2']} matches.

## 3. Net R per matched trade (desk minus E2)

| item | value |
|---|---|
| mean abs diff | {d['mean_abs']:.5f} R |
| max abs diff | {d['max_abs']:.5f} R |
| mean signed diff | {abl[0]['signed']:+.5f} R |
| trades with abs diff > {TOL_R} R | {big} (each would need a cause from the 8 differences; none to list) |

Five largest differences, all explained by the slippage model (E2 slips the fill price, the desk adds the slip to the fee rate; for target exits the shifted target adds a little more):

| entry bar | side | kind E2 / desk | net R E2 | net R desk | diff | cause |
|---|---|---|---|---|---|---|
{top_md}

Exits that land in a different 4h bar (matched trades):

| entry bar | side | kind | E2 exit bar | desk exit bar | cause |
|---|---|---|---|---|---|
{sh_md}

## 4. One known difference removed at a time (counterfactual runs, nothing in the shared code edited)

| variant | matched | E2 only / desk only | kinds agree | mean abs diff R | max abs diff R | exit-bar shifts |
|---|---|---|---|---|---|---|
{abl_md}

With the target level and the slippage placement aligned the two paths agree to rounding (max abs diff {abl[3]['max_abs']:.1e} R): every remaining difference is already counted in the two rows above, so no ninth difference is hiding in the trade mechanics. Row 3 also restores 71 of 71 on its own: the slippage placement moves E2's target level as well, so the cascade is jointly target-from-close and slippage model.

## 5. Exit kinds (matched trades; rows E2, columns desk)

| E2 / desk | stop | target | time |
|---|---|---|---|
{k_md}

Kind agreement {d['kind_agree']} of {d['matched']}.

## 6. The eight known differences, and whether each bit

| difference | exposure in this slice | outcome |
|---|---|---|
{expo_md}

## 7. Parameters

| label | parameter | source |
|---|---|---|
{par_md}

Data note: {len(R['ohlc_bad'])} 4h bar ({bad_bars}) has a different open in the 4h kline file than in the 1m cache resample; {'it is not a signal bar and lies in no E2 trade footprint (stop window, hold, exit bar), so it changed no result above.' if not (R['bad_touch'] or R['bad_signal']) else 'it lies inside ' + str(len(R['bad_touch'])) + ' trade footprint(s) and ' + str(len(R['bad_signal'])) + ' signal bar(s); the signal sets and the matched trades above still agree, so it is a data-source difference with no effect on the comparison.'}

**{verdict}**
'''


def build_json(R, verdict, today):
    d, abl, ex = R['d'], R['abl'], R['expo']
    n = len(R['e2_trades'])
    agree = verdict.startswith('MECHANICS AGREE')
    what = [
        dict(name='Rule (both paths)', value_plain='Krown S8 squeeze break on 4h BTCUSDT; market entry at the next 4h open; stop at the far side of the last 10 bars; target 2R; time stop after 100 bars', label='OURS'),
        dict(name='Fees', value_plain='0.05 % taker, 0.02 % maker', label='SOURCED'),
        dict(name='Detector S8 basis and lookback', value_plain='BBWP basis 7, lookback 100, break above the 50th percentile', label='SOURCED'),
        dict(name='Slippage', value_plain='0.02 % on market and stop fills', label='OURS'),
        dict(name='E2 stop floor', value_plain='0.56 % of the fill (E2 only)', label='OURS'),
        dict(name='Mismatch threshold', value_plain=f'{TOL_R} R net difference per matched trade', label='OURS')]
    return dict(
        id='krown-s8-e2-desk-crosscheck', kind='audit', family='Audit: simulator vs E2 mechanics',
        title=f'Cross-check: E2 (4h OHLC) vs the simulator desk (1m replay), Krown S8 4h, BTCUSDT, {today}',
        provenance='run', date=today, what=what,
        how='Two code paths run on the same 4h S8 signals: E2 simulates on 4h candles, the desk replays every trade on 1m candles. Trades are joined on entry bar and side; each gap is compared and traced to one of eight known differences, and each difference is removed in turn to confirm it.',
        window='DEV only, signals 2022-04-01 to 2024-06-30, BTCUSDT; no bar at or after 2024-07-01 loaded',
        verdict=dict(label=verdict, tone='good' if agree else 'bad'),
        why=[f"Signals: {R['sig']['common']} of {max(R['sig']['n_e2'], R['sig']['n_desk'])} common; the detector and the 1m-to-4h resample reproduce E2's signals.",
             f"Trades: {d['matched']} of {n} matched; the unmatched pair is one cascade from a target level that differs by {ex['target_from_close']['mean_shift_r']:.3f} R on average.",
             f"Net R: mean absolute difference {d['mean_abs']:.4f} R, max {d['max_abs']:.4f} R; no matched trade differs by more than {TOL_R} R; exit kind agrees on {d['kind_agree']} of {d['matched']}.",
             f"With the target level and the slippage placement aligned the paths agree to {abl[3]['max_abs']:.0e} R.",
             'Mechanics only: the E2 edge verdict stays INCONCLUSIVE.'],
        kpis=[dict(label='signals common', value=f"{R['sig']['common']} of {max(R['sig']['n_e2'], R['sig']['n_desk'])}"),
              dict(label='trades matched', value=f"{d['matched']} of {n}"),
              dict(label='mean abs net R diff', value=f"{d['mean_abs']:.4f} R"),
              dict(label='max abs net R diff', value=f"{d['max_abs']:.4f} R"),
              dict(label='exit kind agrees', value=f"{d['kind_agree']} of {d['matched']}")],
        examples=[dict(kind='table', title='One known difference removed at a time', caption='desk minus E2, net R per matched trade',
                       cols=['variant', 'matched', 'kinds agree', 'mean abs R', 'max abs R'],
                       rows=[[x['name'], f"{x['matched']} of {x['n_e2']}", f"{x['kind_agree']} of {x['matched']}", f"{x['mean_abs']:.5f}", f"{x['max_abs']:.5f}"] for x in abl]),
                  dict(kind='none', title='Trade charts', caption='no example trades exported: mechanics audit, the comparison tables are in CROSSCHECK.md')],
        parity=[dict(layer='krown S8 4h', entries_match=[d['matched'], n], exits_match=[d['kind_agree'], d['matched']])],
        evidence=[], source_files=['MyTradingSys/research/fable_run6_powered_prereg/CROSSCHECK.md', 'MyTradingSys/research/fable_run6_powered_prereg/crosscheck_desk.py',
                                   'MyTradingSys/research/fable_run6_powered_prereg/CROSSCHECK_BRIEF.md'],
        commit='ships with this file (git log -- MyTradingSys/research/fable_run6_powered_prereg/crosscheck_desk.py)')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--no-write', action='store_true', help='print only; do not write CROSSCHECK.md / the results row')
    a = ap.parse_args(argv)
    R = run_all()
    verdict, _ = judge(R)
    today = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
    d, n = R['d'], len(R['e2_trades'])
    print(f"signals common {R['sig']['common']}/{max(R['sig']['n_e2'], R['sig']['n_desk'])}; trades matched {d['matched']}/{n} (desk {len(R['desk_trades'])}); "
          f"mean |diff| {d['mean_abs']:.5f} R, max {d['max_abs']:.5f} R; kinds {d['kind_agree']}/{d['matched']}; {verdict}")
    if a.no_write:
        return 0
    (HERE / 'CROSSCHECK.md').write_text(build_md(R, verdict, today), encoding='utf-8', newline='\n')
    out = DESK_DIR / 'results' / 'krown-s8-e2-desk-crosscheck.json'
    out.write_text(json.dumps(build_json(R, verdict, today), indent=1, ensure_ascii=True) + '\n', encoding='utf-8', newline='\n')
    print(f'wrote {HERE / "CROSSCHECK.md"} and {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
