"""LC3 DEV run (standard DEV 2022-04-01..2024-06-30, Q79 ruling): first touches of KEEP levels, every pre-registered
arm (E0/E1/E4 x S0-S3 x K1-K5 x X0_1R/X0_2R/X1/X2 = 240 variants) plus arm P and the K0 measurement.
Writes ladder_dev.md, frozen_rule.json, ladder_ideas_dev.csv and one row per variant in layer_lab/TRIALS.md
(earlier lc-ladder-dev rows are replaced, so a rerun does not duplicate them).

  python MyTradingSys/research/levels_confluence_2026-10-14/ladder_run.py [--months N] [--root F:/MTS/data/tom_raw/klines]
"""
import argparse
import csv
import datetime as dt
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
import ladder as ld  # noqa: E402
import event_table as et  # noqa: E402
from levels import levels_by_day  # noqa: E402
from MyTradingSys.backtest.power_mde import power_mde  # noqa: E402

UTC = dt.timezone.utc
DEV_START = dt.datetime(2022, 4, 1, tzinfo=UTC)
DEV_END = dt.datetime(2024, 7, 1, tzinfo=UTC)          # exclusive; nothing at or after it is read
LOOKBACK_DAYS, LEVEL_LOOKBACK_DAYS = 70, 18
SEED, BOOT, PLAUSIBLE_R, MIN_N = 20261020, 2000, 0.10, 200
DAY = 86400000
ARMS = [(S, K, X) for S in ld.S_ARMS for K in ld.K_ARMS for X in ld.X_ARMS]
E_ARMS = ('E0', 'E1', 'E4')
STATUS = {'NOT_STOPPED': 0, 'BAD': 1, 'GOOD': 2, 'NEUTRAL': 3, 'NO_FILL': 4, 'AFTER_TARGET': 5}
BIAS_COLS = ['B1_value_area'] + [f'B2_swing_{tf}' for tf in et.TF] + [f'B3_ema20_{tf}' for tf in et.TF]
Z975, Z80 = NormalDist().inv_cdf(.975), NormalDist().inv_cdf(.80)
NL = chr(10)


def ms(d):
    return int(d.timestamp() * 1000)


def load_range(root, start_ms, end_ms):
    """1m bars with start_ms <= t < end_ms from the monthly Binance CSVs (only the months needed are read)."""
    root = Path(root)
    bars = []
    m = dt.datetime.fromtimestamp(start_ms / 1000, UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    while ms(m) < end_ms:
        p = root / f'BTCUSDT-1m-{m:%Y-%m}.csv'
        if p.exists():
            with p.open(newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if not row or not row[0].isdigit():
                        continue
                    t = int(row[0])
                    if start_ms <= t < end_ms:
                        bars.append({'t': t, 'o': float(row[1]), 'h': float(row[2]), 'l': float(row[3]), 'c': float(row[4]),
                                     'v': float(row[5]), 'tbv': float(row[9])})
        m = (m.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    bars.sort(key=lambda b: b['t'])
    return bars


def months(limit=None):
    out = []
    m = DEV_START
    while m < DEV_END:
        nxt = (m.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
        out.append((ms(m), ms(min(nxt, DEV_END))))
        m = nxt
    return out[:limit] if limit else out


def ideas_for_month(root, m_start, m_end):
    bars = load_range(root, m_start - LOOKBACK_DAYS * DAY, m_end)
    assert bars and bars[-1]['t'] < ms(DEV_END), 'read past DEV'
    lev = levels_by_day([b for b in bars if b['t'] >= m_start - LEVEL_LOOKBACK_DAYS * DAY])
    bias_idx, atr_idx = ld.BiasIndex(bars), ld.ATRIndex(bars)
    byday = defaultdict(list)
    for b in bars:
        if b['t'] >= m_start:
            byday[b['t'] // DAY].append(b)
    out = []
    for d in sorted(byday):
        daybars = byday[d]
        ctx = ld.DayCtx(daybars)
        rng = np.random.default_rng(SEED + d)
        rows = lev.get(d, [])
        fam = defaultdict(set)
        for x in rows:
            if x['family'] in et.KEEP:
                fam[float(x['price'])].add(x['family'])
        prices = sorted(fam)
        vah = next((float(x['price']) for x in rows if x['family'] == 'prior_day_vah'), None)
        val = next((float(x['price']) for x in rows if x['family'] == 'prior_day_val'), None)
        pd = None if vah is None or val is None else {'vah': vah, 'val': val}
        for px in prices:
            cond = (ctx.lo <= px) & (ctx.hi >= px)
            i = int(cond.argmax())
            if not cond[i]:
                continue
            ref = float(ctx.cl[i - 1]) if i else float(ctx.op[i])
            side = 1 if ref >= px else -1
            adverse = [p for p in prices if side * (p - px) < 0]
            favor = sorted([p for p in prices if side * (p - px) > 0], key=lambda p: abs(p - px))
            L2 = (max(adverse) if side > 0 else min(adverse)) if adverse else None
            T1 = favor[0] if favor else None
            T2 = favor[1] if len(favor) > 1 else None
            touch_t = int(daybars[i]['t'])
            feats = et._features(daybars, i, side)
            idea = {'side': side, 'L1': px, 'L2': L2, 'T1': T1, 'T2': T2, 'atr1h': atr_idx.at(touch_t)}
            rec = {'day': d, 'touch_t': touch_t, 'touch_i': i, 'side': side, 'L1': px, 'L2': L2, 'T1': T1, 'T2': T2,
                   'families': '+'.join(sorted(fam[px])), 'atr1h': idea['atr1h'],
                   'E1': feats['E1_rsi_holds_40_60'], 'E4': feats['E4_outer_band'], 'E1_rsi14': feats['E1_rsi14'],
                   **bias_idx.at(touch_t, pd, ref)}
            net = np.full(len(ARMS), np.nan); gross = net.copy(); fees = net.copy(); pfs = net.copy(); dist = net.copy()
            st = np.full(len(ARMS), -1, dtype=np.int8)
            for a, (S, K, X) in enumerate(ARMS):
                r = ld.simulate(daybars, i, idea, S, K, X, ld.FEES_MAIN, ctx)
                if r is None:
                    continue
                net[a], gross[a], fees[a], pfs[a] = r['net_r'], r['gross_r'], r['fees_r'], r['planned_fee_share']
                dist[a] = r['R_price'] / r['avg_planned'] * 100
                st[a] = STATUS[r['stop_status']]
            p = ld.arm_p(daybars, i, idea, ctx=ctx)
            rec['P'] = None if p is None else {'net_r': p['net_r'], 'status': p['status'], 'lev': p['leverage_max'],
                                                'liq': p['liquidated'], 'stop_to_liq_pct': p['stop_to_liq_pct'],
                                                'pfs': p['planned_fee_share'], 'fills': len(p['fills'])}
            # random-entry control (OURS): same day, same side, same level geometry shifted to the open of a random bar
            j = int(rng.integers(0, ctx.n))
            off = float(ctx.op[j]) - px
            ridea = {'side': side, 'L1': px + off, 'L2': None if L2 is None else L2 + off, 'T1': None if T1 is None else T1 + off,
                     'T2': None if T2 is None else T2 + off, 'atr1h': idea['atr1h']}
            pr = ld.arm_p(daybars, j, ridea, ctx=ctx)
            rec['P_rand'] = None if pr is None else pr['net_r']
            rr = ld.simulate(daybars, j, ridea, 'S0', 'K1', 'X1', ld.FEES_MAIN, ctx)
            rec['ref_rand'] = None if rr is None else rr['net_r']
            t1 = ctx.first_favorable(side, T1, i + 1) if T1 is not None else None
            if t1 is not None:
                seg = ctx.lo[i:t1 + 1] if side > 0 else ctx.hi[i:t1 + 1]
                rec['k0_winner_mae_pct'] = float((side * (px - seg)).max() / px * 100)
            else:
                rec['k0_winner_mae_pct'] = None
            rec['arr'] = (net, gross, fees, pfs, dist, st)
            out.append(rec)
    return out


class Boot:
    def __init__(self, days, seed=SEED, reps=BOOT):
        self.days = sorted(set(days)); self.D = len(self.days)
        self.pos = {d: k for k, d in enumerate(self.days)}
        rng = np.random.default_rng(seed)
        self.idx = rng.integers(0, self.D, size=(reps, self.D))

    def ci(self, values, day_idx):
        v = np.asarray(values, float); ok = ~np.isnan(v)
        if ok.sum() == 0:
            return (math.nan, math.nan)
        sums = np.bincount(day_idx[ok], weights=v[ok], minlength=self.D)
        cnts = np.bincount(day_idx[ok], minlength=self.D).astype(float)
        s = sums[self.idx].sum(1); c = cnts[self.idx].sum(1)
        with np.errstate(invalid='ignore', divide='ignore'):
            m = s / c
        m = m[np.isfinite(m)]
        return (float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))) if m.size else (math.nan, math.nan)


def cell(values, gross, fees, day_idx, order, boot, with_power=False):
    v = np.asarray(values, float); ok = ~np.isnan(v)
    n = int(ok.sum())
    if n == 0:
        return {'n': 0}
    lo, hi = boot.ci(v, day_idx)
    cum = np.cumsum(v[order][~np.isnan(v[order])])
    dd = float((np.maximum.accumulate(cum) - cum).max()) if cum.size else 0.
    out = {'n': n, 'mean': float(v[ok].mean()), 'lo': lo, 'hi': hi, 'maxdd': dd, 'sd': float(v[ok].std(ddof=1)) if n > 1 else math.nan}
    if with_power:
        g = np.asarray(gross, float)[ok]; f = np.asarray(fees, float)[ok]
        wins, losses = g[g > 0], -g[g <= 0]
        out['win_rate'] = float((g > 0).mean()); out['mean_fee_r'] = float(f.mean()); out['mean_gross_r'] = float(g.mean())
        if wins.size and losses.size and losses.mean() > 0:
            rr = wins.mean() / losses.mean()
            try:
                pm = power_mde(min(max(out['win_rate'], 1e-6), 1 - 1e-6), rr, f.mean() / losses.mean(), n)
                out['power_mde'] = {'rr': rr, **pm}
            except ValueError:
                pass
        sd = out['sd']
        if sd and sd > 0:
            out['mde_sd'] = (Z975 + Z80) * sd / math.sqrt(n)
            out['power_plausible'] = NormalDist().cdf(PLAUSIBLE_R * math.sqrt(n) / sd - Z975)
    return out


def fmt(c, extra=''):
    if not c or c.get('n', 0) == 0:
        return '| 0 | - |'
    return f"| {c['n']} | {c['mean']:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}]{extra} |"


def n_mean(c):
    """'n | mean [CI]' or '0 | -' for a table that shows both cells."""
    return fmt(c)[2:-2]


def run(root, limit=None):
    t0 = time.time()
    recs = []
    for m_start, m_end in months(limit):
        recs += ideas_for_month(root, m_start, m_end)
        print(f'{dt.datetime.fromtimestamp(m_start / 1000, UTC):%Y-%m}: ideas so far {len(recs)} ({time.time() - t0:.0f} s)', flush=True)
    N = len(recs)
    net = np.array([r['arr'][0] for r in recs]); gross = np.array([r['arr'][1] for r in recs]); fees = np.array([r['arr'][2] for r in recs])
    pfs = np.array([r['arr'][3] for r in recs]); dist = np.array([r['arr'][4] for r in recs]); st = np.array([r['arr'][5] for r in recs])
    days = [r['day'] for r in recs]; boot = Boot(days)
    day_idx = np.array([boot.pos[d] for d in days]); order = np.argsort([r['touch_t'] for r in recs], kind='stable')
    sides = np.array([r['side'] for r in recs])
    masks = {'E0': np.ones(N, bool), 'E1': np.array([r['E1'] is True for r in recs]), 'E4': np.array([r['E4'] is True for r in recs])}
    nan2 = ([math.nan] * N, [math.nan] * N)

    def C(col, mask, power=False):
        v = net[:, col].copy(); v[~mask] = np.nan
        return cell(v, gross[:, col], fees[:, col], day_idx, order, boot, power)

    # 1. the grid: 240 variants
    grid = {}
    for e in E_ARMS:
        for a, arm in enumerate(ARMS):
            grid[(e,) + arm] = C(a, masks[e], power=True)
    eligible = [(k, c) for k, c in grid.items() if c.get('n', 0) >= MIN_N]
    best = max(eligible, key=lambda kc: kc[1]['mean']) if eligible else None
    best_lo = max(eligible, key=lambda kc: kc[1]['lo']) if eligible else None
    bk, bc = best
    ba = ARMS.index(bk[1:]); bmask = masks[bk[0]]
    pm = bc.get('power_mde', {})
    card_power = pm.get('power', math.nan)
    # verdict (rules written before the run; see ladder_dev.md)
    sd_fail = bc['hi'] < PLAUSIBLE_R and bc.get('power_plausible', 0) >= .5
    if bc['lo'] > 0:
        verdict = 'PASS to LC4 (lower 95 % CI above zero on DEV)'
    elif not card_power >= .5:
        verdict = f'INCONCLUSIVE by the card rule (power_mde.py power {card_power:.0%} < 50 %)'
        if sd_fail:
            verdict += f"; FAIL by the sample-sd rule (+{PLAUSIBLE_R:.2f} R excluded, power {bc['power_plausible']:.0%})"
    elif sd_fail:
        verdict = f'FAIL (a +{PLAUSIBLE_R:.2f} R effect is excluded with power >= 50 %)'
    else:
        verdict = 'INCONCLUSIVE'
    L = []
    W = L.append
    W('# LC3 ladder simulator: DEV result (standard DEV 2022-04-01..2024-06-30)')
    W('')
    W(f'Run {dt.datetime.now(UTC):%Y-%m-%d %H:%M}Z on JIS-NB, `python MyTradingSys/research/levels_confluence_2026-10-14/ladder_run.py`, {time.time() - t0:.0f} s. '
      f'Tests: `python -m pytest MyTradingSys/research/levels_confluence_2026-10-14/test_ladder.py` (9 hand paths, red before ladder.py existed).')
    W('')
    W('## Verdict')
    W('')
    W(f"**{verdict}.** Frozen rule (max mean net R among the {len(eligible)} variants with n >= {MIN_N}; selection = one trial, the VALIDATION read is the answer): "
      f"`{bk[0]} {bk[1]} {bk[2]} {bk[3]}`: n {bc['n']}, mean net R {bc['mean']:+.3f} [{bc['lo']:+.3f}, {bc['hi']:+.3f}], "
      f"max drawdown {bc['maxdd']:.1f} R, win rate {bc['win_rate']:.1%}, mean fee {bc['mean_fee_r']:.3f} R, "
      f"MDE (sample sd) {bc.get('mde_sd', math.nan):.3f} R, power for +{PLAUSIBLE_R:.2f} R {bc.get('power_plausible', math.nan):.0%}; "
      f"power_mde.py (two-point payoff model, rr {pm.get('rr', math.nan):.1f}): power {card_power:.0%}, MDE {pm.get('mde_net_r', math.nan):.3f} R.")
    if best_lo and best_lo[0] != bk:
        k2, c2 = best_lo
        W(f"Robustness: the variant with the highest lower CI is `{' '.join(k2)}`: n {c2['n']}, {c2['mean']:+.3f} [{c2['lo']:+.3f}, {c2['hi']:+.3f}].")
    W('')
    W('EXPECT (D4_LAYER_DECISION.md, written before this run): fee-net mean R per idea above 0 with the lower 95 % CI above 0 on at least one '
      'level class. Verdict rules, written before the run: PASS = frozen rule lower CI > 0; FAIL = upper CI < +0.10 R with power >= 50 % '
      'for a +0.10 R effect (OURS plausible effect); otherwise INCONCLUSIVE. Card step 4 (written 2026-10-13, governs): power from backtest/power_mde.py '
      '< 50 % reads INCONCLUSIVE; that model assumes a two-point payoff (+rr or -1), which overstates the variance of a many-outcome exit, so the sample-sd '
      'figures are given beside it. The frozen rule is read ONCE on VALIDATION by card lc-validation only on PASS; on FAIL or INCONCLUSIVE the operator decides.')
    W('')
    W('## Data, windows, parameters')
    W('')
    W('- Bars: `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-YYYY-MM.csv` (Binance USDT-M perpetual 1m; taker-buy volume = CVD proxy). '
      'Decisions 2022-04-01..2024-06-30 (standard DEV, Q79 addendum in levels_hold.md); 70 days of seed bars before each month for '
      'bias EMAs/fractals (OURS), 18 days for levels; `load_range(end_ms = 2024-07-01)` asserted. VALIDATION and HOLDOUT unread. '
      'event_table.csv / separation.md were NOT used (STALE per Q79 D4: built on VALIDATION-window bars); touches are regenerated here.')
    W('- Ideas: first touch per KEEP level per UTC day (8 KEEP families, levels_hold.md; duplicate prices merged), side = previous close vs level (Q79). '
      'L2 = next KEEP level beyond L1 against the trade; T1 = first KEEP level in favour; T2 = the second (arm P), else T1 + (T1 - L1).')
    W('- Entry filters, pre-registered in separation.md: E0 none, E1 RSI(14) on 5m closes holds 40 (long) / 60 (short), E4 price at the outer '
      'Bollinger band (20, 2); both from `event_table._features` (5m bars closed before the touch, from the day start). Note: E1/E4 were '
      'selected on the stale VALIDATION-window table; they are kept as pre-registered (no re-selection) and that selection is a known '
      'contamination of the VALIDATION read for these two filters.')
    W(f'- Fees SOURCED fees.py: maker {ld.MAKER:.4f} (limit fills: entries, L2, targets), taker {ld.TAKER:.4f} (stops, ladder exits, time stop). '
      'Stop-first inside a bar; no slippage; time stop = last 1m close of the UTC day.')
    W('- Stops OURS: K1 beyond the deepest planned entry by max(0.10 %, 0.20 % maker floor; card step 1); K2 0.10 % beyond L2; K3 0.5 x ATR(14) of 1h '
      'bars (plain SMA, FORMULAS.md s12) beyond L2; K4 a 15m close beyond L2 (exit at that close, R as K2); K5 0.10 % beyond the day extreme up to '
      'the touch bar, pushed beyond L2 when the extreme is inside. R = planned average entry minus stop; full planned size = 1.')
    W(f'- Ladder X2 OURS: half at T1; then per closed 5m bar: exit all on CVD against the trade or the opposite band (BB position >= 1 long / <= 0 short); '
      f'half of the rest once on a flat bar (|delta| <= {ld.FLAT_FRAC} x median |delta| of the prior 20 bars); stop keeps running.')
    W(f'- Bootstrap: {BOOT} resamples of UTC days, seed {SEED} (OURS). Max drawdown on ideas in touch order (ideas may overlap in time: per-idea, not a portfolio).')
    W(f'- Variants: {len(E_ARMS)} entry x {len(ld.S_ARMS)} scale-in x {len(ld.K_ARMS)} stops x {len(ld.X_ARMS)} exits = {len(grid)}, plus arm P and K0; all pre-registered in PLAN.md. '
      f'Best-of-{len(grid)} on DEV is optimistic by construction.')
    W('')
    # counts
    nL2 = sum(r['L2'] is not None for r in recs); nT1 = sum(r['T1'] is not None for r in recs)
    W('## Counts')
    W('')
    W('| ideas | with L2 | with T1 | long | short | E1 true | E4 true | days |')
    W('|---:|---:|---:|---:|---:|---:|---:|---:|')
    W(f"| {N} | {nL2} | {nT1} | {(sides > 0).sum()} | {(sides < 0).sum()} | {masks['E1'].sum()} | {masks['E4'].sum()} | {boot.D} |")
    famc = defaultdict(int)
    for r in recs:
        for f in r['families'].split('+'):
            famc[f] += 1
    W('')
    W('Touches by family (a merged price counts for each family): ' + ', '.join(f'{k} {v}' for k, v in sorted(famc.items())) + '.')
    W('')
    # K table
    W('## Stops (E0, S0, X1: single entry at L1, all out at the first opposing level)')
    W('')
    W('| stop | n | mean net R [95 % CI] | stop dist % (median) | stopped | BAD | GOOD | NEUTRAL | fee share of R (median planned) |')
    W('|---|---:|---|---:|---:|---:|---:|---:|---:|')
    for K in ld.K_ARMS:
        a = ARMS.index(('S0', K, 'X1')); c = C(a, masks['E0'])
        s = st[:, a]; ok = s >= 0; stopped = np.isin(s, [1, 2, 3])
        nst = int(stopped.sum())
        W(f"| {K} | {n_mean(c)} | {np.nanmedian(dist[:, a]):.2f} | {nst / max(ok.sum(), 1):.1%} | {(s == 1).sum() / max(nst, 1):.1%} | {(s == 2).sum() / max(nst, 1):.1%} | "
          f"{(s == 3).sum() / max(nst, 1):.1%} | {np.nanmedian(pfs[:, a]):.1%} |")
    mae = np.array([r['k0_winner_mae_pct'] for r in recs if r['k0_winner_mae_pct'] is not None])
    if mae.size:
        W('')
        W(f'K0 (no stop, measurement): {mae.size} ideas reached T1 by day end; their maximum adverse excursion from L1: median {np.median(mae):.2f} %, '
          f'90th percentile {np.percentile(mae, 90):.2f} % (= the winner-safe stop distance), 95th {np.percentile(mae, 95):.2f} %. '
          f'BAD = stopped, then T1 reached before 1 more R against; GOOD = 1 more R against first; NEUTRAL = neither by day end. The stop is chosen on net R; '
          'the bad-stop rate is a diagnostic.')
    W('')
    # S table
    W('## Scale-in (E0, X1): mean net R [CI] per stop, and paired difference against S0 on the same ideas')
    W('')
    W('| stop | S0 n | S0 L1 full | S1 n | S1 half L1 + half L2 | S2 n | S2 L2 only | S3 n | S3 1/3 L1 + 2/3 L2 | S1 - S0 | S2 - S0 | S3 - S0 |')
    W('|---|---:|---|---:|---|---:|---|---:|---|---|---|---|')
    for K in ld.K_ARMS:
        cells = [n_mean(C(ARMS.index((S, K, 'X1')), masks['E0'])) for S in ld.S_ARMS]
        diffs = []
        a0 = ARMS.index(('S0', K, 'X1'))
        for S in ('S1', 'S2', 'S3'):
            a1 = ARMS.index((S, K, 'X1'))
            both = ~np.isnan(net[:, a0]) & ~np.isnan(net[:, a1])
            if both.sum() == 0:
                diffs.append('-'); continue
            d = np.where(both, net[:, a1] - net[:, a0], np.nan)
            lo, hi = boot.ci(d, day_idx)
            diffs.append(f'{np.nanmean(d):+.3f} [{lo:+.3f}, {hi:+.3f}] (n {int(both.sum())})')
        W(f"| {K} | {' | '.join(cells)} | {' | '.join(diffs)} |")
    W('')
    # full grid
    W('## All variants: n, mean net R [95 % CI] per entry filter')
    W('')
    W('| S | K | X | E0 n | E0 all | E1 n | E1 RSI holds 40/60 | E4 n | E4 outer band |')
    W('|---|---|---|---:|---|---:|---|---:|---|')
    for arm in ARMS:
        W(f"| {arm[0]} | {arm[1]} | {arm[2]} | " + ' | '.join(n_mean(grid[(e,) + arm]) for e in E_ARMS) + ' |')
    W('')
    # bias cuts for the frozen rule
    W(f'## Cuts of the frozen rule `{" ".join(bk)}` by HTF bias and by the other entry filter')
    W('')
    W('| cut | agree n | agree mean [CI] | disagree n | disagree mean [CI] | neutral/none n | neutral mean [CI] |')
    W('|---|---:|---|---:|---|---:|---|')
    for col in BIAS_COLS:
        vals = [r.get(col) for r in recs]
        agree = np.array([(v == 'UP' and s > 0) or (v == 'DOWN' and s < 0) for v, s in zip(vals, sides)])
        dis = np.array([(v == 'DOWN' and s > 0) or (v == 'UP' and s < 0) for v, s in zip(vals, sides)])
        neu = ~agree & ~dis
        W(f'| {col} | ' + ' | '.join(n_mean(C(ba, bmask & m)) for m in (agree, dis, neu)) + ' |')
    for e, name in (('E1', 'E1 RSI holds 40/60'), ('E4', 'E4 outer band')):
        yes = np.array([r[e] is True for r in recs]); no = np.array([r[e] is False for r in recs]); none = ~yes & ~no
        W(f'| {name} (yes / no / unknown) | ' + ' | '.join(n_mean(C(ba, bmask & m)) for m in (yes, no, none)) + ' |')
    W('')
    # fee stress for the frozen rule
    W('## Fee stress (frozen rule): ideas whose planned fee share of R is at most the cut')
    W('')
    W('| cut | n | mean net R [CI] | mean gross R | mean fee R |')
    W('|---|---:|---|---:|---:|')
    for cut in (.10, .25, .50, 1.0):
        m = bmask & (pfs[:, ba] <= cut)
        c = C(ba, m, power=True)
        W(f"| <= {cut:.0%} | {n_mean(c)} | {c.get('mean_gross_r', math.nan):+.3f} | {c.get('mean_fee_r', math.nan):.3f} |")
    be = bc['mean_gross_r'] / bc['mean_fee_r'] if bc['mean_fee_r'] else math.nan
    W('')
    W(f"Break-even: mean gross R {bc['mean_gross_r']:+.3f} against mean fee {bc['mean_fee_r']:.3f} R = the rule pays {be:.1f} x today's fees "
      f"(break-even fee share of R = {bc['mean_gross_r']:.3f} R{'; negative gross: no fee level pays' if bc['mean_gross_r'] <= 0 else ''}). "
      f"All-taker stress: every fee leg at {ld.TAKER:.4f} raises the mean fee to about {bc['mean_fee_r'] * ld.TAKER / ((ld.MAKER + ld.TAKER) / 2):.3f} R.")
    W('')
    # arm P
    P = [r['P'] for r in recs]
    pn = np.array([math.nan if p is None else p['net_r'] for p in P]); pok = ~np.isnan(pn)
    a_ref = ARMS.index(('S0', 'K1', 'X1'))
    both = pok & ~np.isnan(net[:, a_ref])
    d = np.where(both, pn - net[:, a_ref], np.nan); dlo, dhi = boot.ci(d, day_idx)
    cP = cell(pn, *nan2, day_idx, order, boot)
    levs = [p['lev'] for p in P if p]; liqs = sum(1 for p in P if p and p['liq']); s2l = [p['stop_to_liq_pct'] for p in P if p and p['stop_to_liq_pct'] is not None]
    fills3 = sum(1 for p in P if p and p['fills'] == 3)
    W('## Arm P (levels_sizing METHOD.md: one loss budget 0.5 % of 10,000, capped 1:2:3 adds at 0.25/0.5 of a 0.4 % stop, staged exits)')
    W('')
    W(f"n {cP['n']}, mean net R (R = the 50 USD budget) {cP['mean']:+.3f} [{cP['lo']:+.3f}, {cP['hi']:+.3f}], max drawdown {cP['maxdd']:.1f} R; "
      f"full 1:2:3 build in {fills3} ideas. Paired against S0 K1 X1 on the same ideas: {np.nanmean(d):+.3f} [{dlo:+.3f}, {dhi:+.3f}] (n {int(both.sum())}).")
    W(f"Liquidation check (isolated margin, mark = bar low/high, maintenance 0.5 % OURS): max leverage {max(levs) if levs else math.nan:.2f} x, "
      f"liquidations {liqs} (must be 0), stop-to-liquidation distance median {np.median(s2l) if s2l else math.nan:.1f} % of price.")
    W('Probe baseline (levels_sizing REPORT.md: -0.216 / -0.195 / -0.210 R, n 117) was measured on 2024-12..2025-03 first-minute-rejection signals, '
      'which is VALIDATION-window data under Q79; it is not the same signal set and is not paired here.')
    W('')
    W('| arm P cut | n | mean net R [CI] |')
    W('|---|---:|---|')
    ppfs = np.array([math.nan if p is None else p['pfs'] for p in P])
    for cut in (.10, .25, .50):
        v = pn.copy(); v[~(ppfs <= cut)] = np.nan
        W(f"| fee share <= {cut:.0%} | {n_mean(cell(v, *nan2, day_idx, order, boot))} |")
    for e in ('E1', 'E4'):
        for flag, name in ((True, 'yes'), (False, 'no')):
            v = pn.copy(); v[~np.array([r[e] is flag for r in recs])] = np.nan
            W(f"| {e} {name} | {n_mean(cell(v, *nan2, day_idx, order, boot))} |")
    prand = np.array([math.nan if r['P_rand'] is None else r['P_rand'] for r in recs])
    rrand = np.array([math.nan if r['ref_rand'] is None else r['ref_rand'] for r in recs])
    W(f"| random entry, arm P | {n_mean(cell(prand, *nan2, day_idx, order, boot))} |")
    W(f"| random entry, S0 K1 X1 | {n_mean(cell(rrand, *nan2, day_idx, order, boot))} |")
    bothr = pok & ~np.isnan(prand); dr = np.where(bothr, pn - prand, np.nan); rlo, rhi = boot.ci(dr, day_idx)
    W(f"| arm P minus its random-entry control (paired) | {int(bothr.sum())} | {np.nanmean(dr):+.3f} [{rlo:+.3f}, {rhi:+.3f}] |")
    W('')
    W('Random-entry control (OURS): the same day, side and level geometry shifted so that L1 is the open of one random 1m bar of the day '
      f'(seed {SEED} + day); it measures what the level adds over entering anywhere.')
    W('')
    W('## Files')
    W('')
    W('- `frozen_rule.json`: the frozen DEV rule (no edits after); `ladder_ideas_dev.csv`: one row per idea (meta, bias, E flags, net R of the 20 S x K arms at X1, '
      'the 4 exits at the frozen S x K, arm P); `research/layer_lab/TRIALS.md`: one row per variant.')
    W('- Code: `ladder.py` (simulator, arm P, bias/ATR indices), `ladder_run.py` (this run), `test_ladder.py`.')
    W('')
    (HERE / 'ladder_dev.md').write_text(NL.join(L) + NL, encoding='utf-8', newline=NL)
    # frozen rule
    frozen = {'frozen_at': f'{dt.datetime.now(UTC):%Y-%m-%dT%H:%MZ}', 'rule': {'entry_filter': bk[0], 'scale_in': bk[1], 'stop': bk[2], 'exit': bk[3]},
              'selection': f'max mean net R among {len(eligible)} variants with n >= {MIN_N} on standard DEV 2022-04-01..2024-06-30',
              'dev': {k: bc[k] for k in ('n', 'mean', 'lo', 'hi', 'maxdd', 'win_rate', 'mean_fee_r', 'mean_gross_r') if k in bc},
              'power': {'mde_sd': bc.get('mde_sd'), 'power_plausible_0.10R': bc.get('power_plausible'), 'power_mde': pm},
              'verdict': verdict, 'parameters': {'fees': 'fees.py BINANCE maker/taker', 'margin_pct': ld.MARGIN * 100, 'flat_frac': ld.FLAT_FRAC,
                                                 'bb': [ld.BB_N, ld.BB_W], 'rsi': [14, '5m closes from day start', '40/60'],
                                                 'keep_families': sorted(et.KEEP), 'seed': SEED, 'bootstrap': BOOT},
              'validation_card': 'lc-validation: one run on VALIDATION 2024-07-01..2025-06-30, read once, no edits; only on PASS'}
    (HERE / 'frozen_rule.json').write_text(json.dumps(frozen, indent=1) + NL, encoding='utf-8', newline=NL)
    # ideas csv
    cols = ['day', 'touch_t', 'side', 'L1', 'L2', 'T1', 'T2', 'families', 'atr1h', 'E1', 'E4', 'E1_rsi14', 'k0_winner_mae_pct'] + BIAS_COLS
    arm_cols = [(S, K) for S in ld.S_ARMS for K in ld.K_ARMS]
    with (HERE / 'ladder_ideas_dev.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(cols + [f'{S}_{K}_X1' for S, K in arm_cols] + [f'{bk[1]}_{bk[2]}_{X}' for X in ld.X_ARMS] + ['P_net_r', 'P_status'])
        for k, r in enumerate(recs):
            row = [r.get(c) for c in cols]
            row = [f'{x:.4f}' if isinstance(x, float) else x for x in row]
            row += ['' if np.isnan(net[k, ARMS.index((S, K, 'X1'))]) else f'{net[k, ARMS.index((S, K, "X1"))]:.3f}' for S, K in arm_cols]
            row += ['' if np.isnan(net[k, ARMS.index((bk[1], bk[2], X))]) else f'{net[k, ARMS.index((bk[1], bk[2], X))]:.3f}' for X in ld.X_ARMS]
            row += ['' if r['P'] is None else f"{r['P']['net_r']:.3f}", '' if r['P'] is None else r['P']['status']]
            w.writerow(row)
    # trials
    cmd = '`python MyTradingSys/research/levels_confluence_2026-10-14/ladder_run.py`'
    win = 'standard DEV 2022-04-01..2024-06-30 (Q79); VALIDATION/HOLDOUT unread; fees.py maker/taker; stop-first in bar'
    today = f'{dt.date.today():%Y-%m-%d}'
    rows = []
    for key, c in grid.items():
        res = f"n {c['n']}, mean net R {c['mean']:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}]" if c.get('n') else 'n 0'
        rows.append(f"| {today} | lc-ladder-dev {' '.join(key)} | {cmd} | {win} | {res} |")
    rows.append(f"| {today} | lc-ladder-dev arm P | {cmd} | {win}; METHOD.md 1:2:3 capped, 0.4 % stop, staged exits | n {cP['n']}, mean net R {cP['mean']:+.3f} [{cP['lo']:+.3f}, {cP['hi']:+.3f}], liquidations {liqs} |")
    rows.append(f"| {today} | lc-ladder-dev K0 | {cmd} | {win}; no stop, winners to T1 | n {mae.size}, winner MAE 90th pct {np.percentile(mae, 90) if mae.size else math.nan:.2f} % |")
    rows.append(f"| {today} | lc-ladder-dev FROZEN | {cmd} | {win}; selection max mean among n >= {MIN_N} | {' '.join(bk)}: {bc['mean']:+.3f} [{bc['lo']:+.3f}, {bc['hi']:+.3f}] n {bc['n']}; {verdict} |")
    tp = HERE.parents[0] / 'layer_lab' / 'TRIALS.md'
    if not limit:
        kept = [ln for ln in tp.read_text(encoding='utf-8').split(NL) if '| lc-ladder-dev ' not in ln]
        while kept and kept[-1] == '':
            kept.pop()
        tp.write_text(NL.join(kept) + NL + NL.join(rows) + NL, encoding='utf-8', newline=NL)
    print(NL.join(L[:12]))
    print(f'ideas {N}, variants {len(grid)}, frozen {bk} {bc["mean"]:+.3f} [{bc["lo"]:+.3f}, {bc["hi"]:+.3f}] n {bc["n"]}; {verdict}; {time.time() - t0:.0f} s')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--months', type=int, default=None, help='smoke: only the first N DEV months (no TRIALS.md rows)')
    ap.add_argument('--root', default='F:/MTS/data/tom_raw/klines')
    a = ap.parse_args()
    run(a.root, a.months)
