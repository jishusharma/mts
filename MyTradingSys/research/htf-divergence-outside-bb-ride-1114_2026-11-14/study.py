import json, time, os
import numpy as np, pandas as pd
from datetime import datetime, timezone
C0 = 'F:/MTS/data_cache/binance_spot_htf'
OUT = os.path.dirname(os.path.abspath(__file__))
SYMS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']
TFS = ['4h', '1d', '3d', '1w']
TFMS = {'4h': 4 * 3600e3, '1d': 86400e3, '3d': 3 * 86400e3, '1w': 7 * 86400e3}
LB = {'4h': 60, '1d': 60, '3d': 40, '1w': 30}
FEE = 0.0012
DEV_END = pd.Timestamp('2023-12-31 23:59:59', tz='UTC').value // 10 ** 6
rng = np.random.default_rng(7)
EXITS = ['opp', 'opp_stop', '2R', '3R', 'trail']
CONFS = ['none', 'backin', 'swing', 'macd']


def load_raw(sym, tf):
    base = '1d' if tf == '3d' else tf
    a = np.array(json.load(open(f'{C0}/{sym}_{base}.json')))
    df = pd.DataFrame(a, columns=['t', 'o', 'h', 'l', 'c', 'v'])
    df['t'] = df.t.astype('int64')
    if tf == '3d':
        g = (df.t // 86400000) // 3
        df = df.groupby(g).agg(t=('t', 'first'), o=('o', 'first'), h=('h', 'max'), l=('l', 'min'),
                               c=('c', 'last'), v=('v', 'sum')).reset_index(drop=True)
    return df


def closed(df, tf):
    return df[df.t + TFMS[tf] <= time.time() * 1000].reset_index(drop=True)


def ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False).mean().values


def indicators(df):
    c = df.c.values; h = df.h.values; l = df.l.values
    s = pd.Series(c); m = s.rolling(20).mean(); sd = s.rolling(20).std(ddof=0)
    d = s.diff(); up = d.clip(lower=0); dn = (-d).clip(lower=0)
    au = up.ewm(alpha=1 / 14, adjust=False).mean(); ad = dn.ewm(alpha=1 / 14, adjust=False).mean()
    rsi = (100 - 100 / (1 + au / ad)).values
    ap = (h + l + c) / 3; esa = ema(ap, 10); dd = ema(np.abs(ap - esa), 10)
    wt = ema((ap - esa) / (0.015 * dd), 21)
    macd = ema(c, 12) - ema(c, 26); sig = ema(macd, 9)
    return dict(ub=(m + 2 * sd).values, lb=(m - 2 * sd).values, rsi=rsi, wt=wt, md=macd - sig, sma=m.values)


def build(df, I, osc, direction):
    o = df.o.values; h = df.h.values; l = df.l.values; c = df.c.values
    if direction == 'short':
        return dict(O=o, H=h, L=l, C=c, UB=I['ub'], OS=I[osc], MD=I['md'], SM=I['sma'], T=df.t.values, sgn=1)
    return dict(O=-o, H=-l, L=-h, C=-c, UB=-I['lb'], OS=-I[osc], MD=-I['md'], SM=-I['sma'], T=df.t.values, sgn=-1)


def pivots(H):
    return [i for i in range(2, len(H) - 2)
            if H[i] > H[i - 1] and H[i] > H[i - 2] and H[i] > H[i + 1] and H[i] > H[i + 2]]


def signals(X, tf, variant='H'):
    H = X['H']; C = X['C']; UB = X['UB']; OS = X['OS']
    pv = [i for i in pivots(H) if i >= 60]
    sig = []
    for q, p in zip(pv[:-1], pv[1:]):
        if not (5 <= p - q <= LB[tf]): continue
        if np.isnan(OS[p]) or np.isnan(OS[q]) or np.isnan(UB[p]): continue
        if not (H[p] > H[q] and OS[p] < OS[q]): continue
        ref = H[p] if variant == 'H' else C[p]
        if not ref > UB[p]: continue
        sig.append(dict(p=p, q=q, c=p + 2))
    return sig


def confirm_bar(X, s, mode):
    n = len(X['H']); p, q = s['p'], s['q']; C = X['C']; UB = X['UB']
    if mode == 'none': return p + 2
    if mode == 'backin':
        for j in range(p + 2, min(p + 13, n)):
            if C[j] < UB[j]: return j
    if mode == 'swing':
        ll = X['L'][q:p + 1].min()
        for j in range(p + 2, min(p + 33, n)):
            if C[j] < ll: return j
    if mode == 'macd':
        D = X['MD']
        for j in range(p + 2, min(p + 13, n)):
            if D[j] < 0 and D[j - 1] >= 0: return j
    return None


def sim(X, e, entry, stop, mode, opp_c):
    O = X['O']; H = X['H']; L = X['L']; C = X['C']; SM = X['SM']; n = len(O)
    R = stop - entry
    use_stop = mode != 'opp'
    tgt = entry - 2 * R if mode == '2R' else (entry - 3 * R if mode == '3R' else None)
    for j in range(e, n):
        if use_stop:
            if j > e and O[j] >= stop: return j, O[j], False
            if H[j] >= stop: return j, stop, False
        if tgt is not None and L[j] <= tgt: return j, tgt, False
        if mode in ('opp', 'opp_stop') and opp_c is not None and j == opp_c:
            return (j + 1, O[j + 1], False) if j + 1 < n else (j, C[j], True)
        if mode == 'trail' and j > e and not np.isnan(SM[j - 1]) and C[j - 1] <= SM[j - 1] and C[j] > SM[j]:
            return (j + 1, O[j + 1], False) if j + 1 < n else (j, C[j], True)
    return n - 1, C[n - 1], True


def first_opp(opp_list, cb):
    for s in opp_list:
        if s['c'] >= cb: return s['c']
    return None


def run_trade(X, s, cb, mode, opp_list, fixed_stop=None):
    n = len(X['O']); e = cb + 1
    if e >= n: return None
    entry = X['O'][e]; stop = X['H'][s['p']] if fixed_stop is None else fixed_stop
    R = stop - entry
    if R <= 0 or R / abs(entry) < 0.005: return None
    oc = first_opp(opp_list, cb) if mode in ('opp', 'opp_stop') else None
    xi, xp, op = sim(X, e, entry, stop, mode, oc)
    return dict(e=e, xi=xi, R=(entry - xp) / R - FEE * abs(entry) / R, hold=xi - e, open=op, ret=(entry - xp) / abs(entry) - FEE)


def boot(x, k=2000):
    x = np.asarray(x)
    if len(x) < 5: return (np.nan, np.nan)
    m = rng.choice(x, (k, len(x))).mean(1)
    return (np.percentile(m, 2.5), np.percentile(m, 97.5))


def phase_series(sym):
    a = np.array(json.load(open(f'{C0}/{sym}_1d.json')))
    c = a[:, 4]; t = a[:, 0].astype('int64'); m = pd.Series(c).rolling(200).mean().values
    ph = np.full(len(c), 'n/a', dtype=object)
    for i in range(230, len(c)):
        if c[i] > m[i] and m[i] > m[i - 30]: ph[i] = 'bull'
        elif c[i] < m[i] and m[i] < m[i - 30]: ph[i] = 'bear'
        else: ph[i] = 'base'
    return t, ph


PH = {s: phase_series(s) for s in SYMS}


def phase_at(sym, tms):
    t, ph = PH[sym]; i = np.searchsorted(t, tms - 86400000, side='right') - 1
    return ph[i] if i >= 0 else 'n/a'


D = {}
for _s in SYMS:
    for _tf in TFS:
        _df = closed(load_raw(_s, _tf), _tf)
        D[(_s, _tf)] = (_df, indicators(_df))


def trades_for(sym, tf, osc, direction, conf, variant='H', exits=EXITS):
    df, I = D[(sym, tf)]
    X = build(df, I, osc, direction)
    Xo = build(df, I, osc, 'long' if direction == 'short' else 'short')
    sg = signals(X, tf, variant); opp = signals(Xo, tf, 'H')
    rows = []
    for s in sg:
        cb = confirm_bar(X, s, conf)
        if cb is None: continue
        r = dict(sym=sym, tf=tf, osc=osc, dir=direction, conf=conf, p=s['p'], cb=cb, pt=int(X['T'][s['p']]),
                 ct=int(X['T'][cb] + TFMS[tf]), pxp=float(abs(X['H'][s['p']])))
        r['phase'] = phase_at(sym, r['ct'])
        r['osc_p'] = float(X['OS'][s['p']] * X['sgn']); r['osc_q'] = float(X['OS'][s['q']] * X['sgn'])
        ok = False
        for ex in exits:
            tr = run_trade(X, s, cb, ex, opp)
            if tr is None: r[ex] = None; continue
            ok = True; tr['hold_d'] = tr['hold'] * TFMS[tf] / 86400e3; r[ex] = tr
        if ok: rows.append(r)
    return rows


def stat(vals, holds, rets=None):
    v = np.array(vals, dtype=float)
    if len(v) == 0: return dict(n=0)
    lo, hi = boot(v)
    return dict(n=len(v), win=float((v > 0).mean()), mean=float(v.mean()), lo=float(lo), hi=float(hi),
                med_hold=float(np.median(holds)), ret=float(np.mean(rets)) if rets is not None else 0.0)


def cell(rows, ex, split=None, phase=None):
    sel = [r for r in rows if r[ex] is not None]
    if split == 'DEV': sel = [r for r in sel if r['ct'] <= DEV_END]
    if split == 'VAL': sel = [r for r in sel if r['ct'] > DEV_END]
    if phase: sel = [r for r in sel if r['phase'] == phase]
    return stat([r[ex]['R'] for r in sel], [r[ex]['hold_d'] for r in sel], [r[ex]['ret'] for r in sel])


def placebo(sym, tf, osc, direction, n, ex, draws=100):
    df, I = D[(sym, tf)]; X = build(df, I, osc, direction)
    Xo = build(df, I, osc, 'long' if direction == 'short' else 'short'); opp = signals(Xo, tf, 'H')
    nn = len(df); means = []
    for _ in range(draws):
        rs = []
        for cb in rng.integers(80, nn - 3, size=n):
            tr = run_trade(X, dict(p=cb), cb, ex, opp, fixed_stop=X['H'][cb - 5:cb + 1].max())
            if tr: rs.append(tr['R'])
        if rs: means.append(np.mean(rs))
    return float(np.mean(means)) if means else float('nan')


def fmt(st):
    if st['n'] == 0: return '0'
    ci = '[%.2f,%.2f]' % (st['lo'], st['hi']) if not np.isnan(st['lo']) else 'n<5'
    return '%d / %.0f%% / %+.2f R / %s / %.0fd / %+.1f%% per trade' % (st['n'], 100 * st['win'], st['mean'], ci, st['med_hold'], 100 * st['ret'])


def short(st):
    return '0' if st['n'] == 0 else '%d / %.0f%% / %+.2f' % (st['n'], 100 * st['win'], st['mean'])


def dstr(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d')


def equity(df, I, osc, tf, mode):
    Xs = build(df, I, osc, 'short'); Xl = build(df, I, osc, 'long')
    ev = sorted([(s['c'], 'short') for s in signals(Xs, tf)] + [(s['c'], 'long') for s in signals(Xl, tf)])
    o = df.o.values; c = df.c.values; n = len(df)
    eq = np.ones(n); capital = 1.0; pos = None; evi = 0; ntr = 0; start = None
    for j in range(n):
        while evi < len(ev) and ev[evi][0] <= j - 1:
            d = ev[evi][1]; evi += 1
            if mode == 'flip': want = d
            elif mode == 'long_only': want = 'long' if d == 'long' else 'flat'
            else: want = 'short' if d == 'short' else 'flat'
            if (pos and want == pos[0]) or (pos is None and want == 'flat'): continue
            if pos:
                r = (o[j] / pos[1] - 1) if pos[0] == 'long' else (pos[1] / o[j] - 1)
                capital *= (1 + r) * (1 - FEE); ntr += 1; pos = None
            if want != 'flat':
                pos = (want, o[j])
                if start is None: start = j
        if pos:
            r = (c[j] / pos[1] - 1) if pos[0] == 'long' else (pos[1] / c[j] - 1)
            eq[j] = capital * (1 + r)
        else: eq[j] = capital
    return eq, ntr, start


if __name__ == '__main__':
    L = []; ALL = {}
    L.append('### Signal counts (confirm none)')
    L.append('|sym|tf|bear RSI high-out|bear RSI close-out|bear WT high-out|bull RSI high-out|bull RSI close-out|bull WT high-out|')
    L.append('|-|-|-|-|-|-|-|-|')
    for s in SYMS:
        for tf in TFS:
            df, I = D[(s, tf)]; cs = []
            for osc, d, v in [('rsi', 'short', 'H'), ('rsi', 'short', 'C'), ('wt', 'short', 'H'),
                              ('rsi', 'long', 'H'), ('rsi', 'long', 'C'), ('wt', 'long', 'H')]:
                cs.append(len(signals(build(df, I, osc, d), tf, v)))
            L.append('|%s|%s|%s|' % (s[:3], tf, '|'.join(map(str, cs))))
    for osc in ['rsi', 'wt']:
        for direction in ['short', 'long']:
            L.append(f'\n### BTC {osc.upper()} {direction}: cell = n / win / mean net R / 95% CI / median hold')
            L.append('|tf|confirm|' + '|'.join(EXITS) + '|'); L.append('|-|-|' + '-|' * len(EXITS))
            for tf in TFS:
                for conf in CONFS:
                    rows = trades_for('BTCUSDT', tf, osc, direction, conf)
                    ALL[f'BTC|{osc}|{direction}|{tf}|{conf}'] = rows
                    L.append(f'|{tf}|{conf}|' + '|'.join(fmt(cell(rows, e)) for e in EXITS) + '|')
    L.append('\n### BTC RSI, confirm none, by phase at signal: cell = n / win / mean net R')
    L.append('|dir|tf|phase|opp|opp_stop|3R|'); L.append('|-|-|-|-|-|-|')
    for direction in ['short', 'long']:
        for tf in TFS:
            rows = ALL[f'BTC|rsi|{direction}|{tf}|none']
            for ph in ['bear', 'base', 'bull']:
                L.append(f'|{direction}|{tf}|{ph}|' + '|'.join(short(cell(rows, e, phase=ph)) for e in ['opp', 'opp_stop', '3R']) + '|')
    L.append('\n### BTC RSI, confirm none: DEV (to 2023) vs VALIDATION (2024+)')
    L.append('|dir|tf|exit|DEV n|DEV mean R|VAL n|VAL mean R|'); L.append('|-|-|-|-|-|-|-|')
    for direction in ['short', 'long']:
        for tf in TFS:
            rows = ALL[f'BTC|rsi|{direction}|{tf}|none']
            for e in ['opp', 'opp_stop', '3R']:
                a = cell(rows, e, 'DEV'); b = cell(rows, e, 'VAL')
                f = lambda st: '%+.2f' % st['mean'] if st['n'] else '-'
                L.append(f'|{direction}|{tf}|{e}|{a["n"]}|{f(a)}|{b["n"]}|{f(b)}|')
    L.append('\n### Pooled BTC ETH SOL BNB XRP, RSI, confirm none: n / win / mean net R / CI / hold')
    L.append('|dir|tf|opp|opp_stop|3R|trail|'); L.append('|-|-|-|-|-|-|')
    for direction in ['short', 'long']:
        for tf in TFS:
            rows = []
            for s in SYMS: rows += trades_for(s, tf, 'rsi', direction, 'none')
            L.append(f'|{direction}|{tf}|' + '|'.join(fmt(cell(rows, e)) for e in ['opp', 'opp_stop', '3R', 'trail']) + '|')
    L.append('\n### Placebo: random entries, same n, same exit (100 draws), BTC RSI confirm none')
    L.append('|dir|tf|exit|n|real mean R|placebo mean R|'); L.append('|-|-|-|-|-|-|')
    for direction in ['short', 'long']:
        for tf in TFS:
            rows = ALL[f'BTC|rsi|{direction}|{tf}|none']
            for e in ['opp', 'opp_stop', '3R']:
                st = cell(rows, e)
                if st['n'] == 0: continue
                L.append(f'|{direction}|{tf}|{e}|{st["n"]}|{st["mean"]:+.2f}|{placebo("BTCUSDT", tf, "rsi", direction, st["n"], e):+.2f}|')
    L.append('\n### BTC full-cycle equity (start 1.0; 12 bp per trade; flips on opposite divergence, confirm none)')
    L.append('|osc|tf|mode|trades|final x|max DD (bar close)|buy&hold x same window|'); L.append('|-|-|-|-|-|-|-|')
    for osc in ['rsi', 'wt']:
        for tf in TFS:
            df, I = D[('BTCUSDT', tf)]
            for mode in ['flip', 'long_only', 'short_only']:
                eq, ntr, start = equity(df, I, osc, tf, mode)
                if start is None: continue
                seg = eq[start:]; dd = (seg / np.maximum.accumulate(seg) - 1).min()
                L.append(f'|{osc}|{tf}|{mode}|{ntr}|{eq[-1]:.2f}|{dd * 100:.0f}%|{df.c.values[-1] / df.o.values[start]:.2f}|')
    L.append('\n### BTC RSI equity at year end (x), by mode')
    yrs = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026']
    L.append('|tf|mode|' + '|'.join(yrs) + '|'); L.append('|-|-|' + '-|' * len(yrs))
    for tf in ['1d', '3d', '1w']:
        df, I = D[('BTCUSDT', tf)]
        dts = pd.to_datetime(df.t, unit='ms', utc=True)
        for mode in ['flip', 'long_only', 'short_only']:
            eq, _, _ = equity(df, I, 'rsi', tf, mode)
            v = []
            for y in yrs:
                m = np.where(dts.dt.year.values == int(y))[0]
                v.append('%.2f' % eq[m[-1]] if len(m) else '-')
            L.append(f'|{tf}|{mode}|' + '|'.join(v) + '|')
    L.append('\n### Forward return after signal (entry = next open; close after N bars; profit sign for signal direction); pooled 5 symbols, RSI, confirm none, high outside band')
    L.append('|dir|tf|n signals|+5 bars mean (hit%)|+20 bars|+60 bars|baseline all bars +5 / +20 / +60|'); L.append('|-|-|-|-|-|-|-|')
    for direction in ['short', 'long']:
        for tf in TFS:
            res = {5: [], 20: [], 60: []}; base = {5: [], 20: [], 60: []}
            for s_ in SYMS:
                df, I = D[(s_, tf)]; X = build(df, I, 'rsi', direction); sg = signals(X, tf)
                o = df.o.values; c = df.c.values
                sgn = -1 if direction == 'short' else 1
                for h_ in res:
                    for sgl in sg:
                        e = sgl['c'] + 1
                        if e + h_ < len(c): res[h_].append(sgn * (c[e + h_ - 1] / o[e] - 1))
                    ee = np.arange(61, len(c) - h_ - 1)
                    base[h_].append(sgn * (c[ee + h_ - 1] / o[ee] - 1))
            cells = []
            for h_ in res:
                v = np.array(res[h_])
                cells.append('%.1f%% (%.0f%%) n=%d' % (100 * v.mean(), 100 * (v > 0).mean(), len(v)) if len(v) else '-')
            bs = ' / '.join('%.1f%%' % (100 * np.concatenate(base[h_]).mean()) for h_ in res)
            L.append(f'|{direction}|{tf}|{len(res[5])}|' + '|'.join(cells) + f'|{bs}|')
    open(f'{OUT}/tables.md', 'w', encoding='utf-8').write('\n'.join(L))
    SL = ['date_confirmed,tf,dir,osc,pivot_date,pivot_px,osc_prev,osc_now,phase,R_opp,R_oppstop,R_2R,R_3R,R_trail,hold_opp_days,still_open']
    for tf in ['1d', '3d', '1w']:
        for osc in ['rsi', 'wt']:
            for d in ['short', 'long']:
                for r in trades_for('BTCUSDT', tf, osc, d, 'none'):
                    g = lambda ex: '%+.2f' % r[ex]['R'] if r[ex] else ''
                    SL.append(','.join([dstr(r['ct']), tf, d, osc, dstr(r['pt']), '%.0f' % r['pxp'], '%.1f' % r['osc_q'],
                                        '%.1f' % r['osc_p'], r['phase'], g('opp'), g('opp_stop'), g('2R'), g('3R'), g('trail'),
                                        '%.0f' % r['opp']['hold_d'] if r['opp'] else '', str(r['opp']['open']) if r['opp'] else '']))
    open(f'{OUT}/btc_signals_1d_3d_1w.csv', 'w').write('\n'.join(SL))
    N = ['### BTC now (descriptive). A = closed bars only; B = including the still-forming bar']
    for label in ['A', 'B']:
      for tf in TFS:
        if label == 'A': df, I = D[('BTCUSDT', tf)]
        else:
            df = load_raw('BTCUSDT', tf); I = indicators(df)
            if len(df) == len(D[('BTCUSDT', tf)][0]): continue
        n = len(df)
        c = df.c.values; l = df.l.values; h = df.h.values
        N.append(f'\n**{label} {tf}** last bar {dstr(int(df.t.values[-1]))}: close {c[-1]:.0f}, low {l[-1]:.0f}, RSI {I["rsi"][-1]:.1f}, WT {I["wt"][-1]:.1f}, lower BB {I["lb"][-1]:.0f}, SMA20 {I["sma"][-1]:.0f}, MACD-minus-signal {I["md"][-1]:+.0f}')
        for osc in ['rsi', 'wt']:
            X = build(df, I, osc, 'long'); sg = signals(X, tf)
            if sg:
                s_ = sg[-1]
                N.append(f'- last confirmed bullish {osc.upper()} divergence with low below lower BB: pivot {dstr(int(df.t.values[s_["p"]]))} low {l[s_["p"]]:.0f}, confirmed {dstr(int(df.t.values[s_["c"]]))}')
            k = int(np.argmin(l[-8:])); cand = n - 8 + k
            pv = [i for i in pivots(X['H']) if i <= cand - 3 and 5 <= cand - i <= LB[tf]]
            if pv:
                q = pv[-1]; osv = I[osc]
                res = 'YES' if (l[cand] < l[q] and osv[cand] > osv[q]) else 'no'
                outside = 'low below lower BB' if l[cand] < I['lb'][cand] else 'low inside lower BB'
                swing = h[q:cand + 1].max()
                N.append(f'- forming low {dstr(int(df.t.values[cand]))} {l[cand]:.0f} vs prior pivot low {dstr(int(df.t.values[q]))} {l[q]:.0f}: lower low={l[cand] < l[q]}, {osc.upper()} {osv[cand]:.1f} vs {osv[q]:.1f}; bullish divergence building: {res}; {outside}; confirm levels: close above lower BB {I["lb"][-1]:.0f} / above last swing high {swing:.0f} / above SMA20 {I["sma"][-1]:.0f}')
    open(f'{OUT}/btc_now.md', 'w', encoding='utf-8').write('\n'.join(N))
    print('done')
