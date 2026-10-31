"""Meta-label and early-exit test on the tf_break events (PRE_REG.md, frozen first). Every rule here is in PRE_REG.md.
Stages: build (events + features F1-F15 + outcomes -> table.csv outside the repo), dev (verdict-bearing DEV run -> dev.json),
val (VALIDATION read, only for cells PRE_REG lets through -> val.json).
Usage: python meta.py build|dev|val [out_dir]   (default F:/MTS/runs/meta_label_breaks)"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
MTS = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(MTS, 'research', 'tf_break_event_study_2026-10-30'))
sys.path.insert(0, MTS)
import study as S  # noqa: E402
from backtest import fees  # noqa: E402
from backtest.layers.krown import krown_core as KC  # noqa: E402

TFS = ('15m', '1h', '4h')
RT = 2 * fees.BINANCE_TAKER
DAY, WEEK = 86400, 604800
DEV_END = pd.Timestamp('2024-07-01', tz='UTC').timestamp()
HALF = pd.Timestamp('2023-01-01', tz='UTC').timestamp()
DEFAULT_OUT = 'F:/MTS/runs/meta_label_breaks'
FEATS = ['bbwp', 'bbwp_4h', 'trend_d', 'rsi_e', 'flow_e', 'relvol_e', 'dist_atr', 'move_e', 'rv',
         's_eu', 's_us', 's_late', 'c_R', 'c_W1', 'hi_side']
SGN = {'H': 1, 'R': -1, 'W1': -1}
LAM, NBLK, PURGE, NPLAC, NBOOT = 1.0, 6, 7 * DAY, 200, 1000


# ---- features: only bars <= e ---------------------------------------------------------------------------------

def htf_last_closed(htf, htf_min, t_entry):
    """index of the last HTF bar with open + tf <= t_entry, or -1."""
    closes = htf['t'].to_numpy() + htf_min * 60
    return int(np.searchsorted(closes, t_entry, side='right')) - 1


def series(b):
    """per-bar arrays used by features; every value at index j uses bars <= j only."""
    h, l, c, v, tbv = (b[k].to_numpy(float) for k in ('h', 'l', 'c', 'v', 'tbv'))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    bw = KC.bbwp(list(c), 7, 100)
    return dict(c=c, v=v, t=b['t'].to_numpy(np.int64), atr=pd.Series(tr).rolling(14).mean().to_numpy(), rsi=S.rsi(c),
                flow=(2 * tbv - v) / np.where(v == 0, 1, v), bbwp=np.array([np.nan if x is None else x for x in bw]))


def htf_series(b):
    c = b['c'].to_numpy(float)
    bw = KC.bbwp(list(c), 7, 100)
    return dict(b=b, bbwp=np.array([np.nan if x is None else x for x in bw]),
                sma200=pd.Series(c).rolling(200).mean().to_numpy(), c=c)


def features_at(s, i, e, d, cls, side, dist_atr, t_entry, h4, dd, tv):
    """F1-F15 for one trade; reads s[...] at indices <= e and HTF bars closed by t_entry."""
    c, atr = s['c'], s['atr']
    j4 = htf_last_closed(h4['b'], 240, t_entry)
    jd = htf_last_closed(dd['b'], 1440, t_entry)
    hist = [tv.get(int(s['t'][e]) - k * WEEK) for k in range(1, 9)]
    hist = [x for x in hist if x is not None]
    hour = pd.Timestamp(t_entry, unit='s', tz='UTC').hour
    return dict(
        bbwp=s['bbwp'][e],
        bbwp_4h=h4['bbwp'][j4] if j4 >= 0 else np.nan,
        trend_d=d * (dd['c'][jd] / dd['sma200'][jd] - 1) if jd >= 0 else np.nan,
        rsi_e=s['rsi'][e] if d > 0 else 100 - s['rsi'][e],
        flow_e=d * s['flow'][e - 4:e + 1].mean(),
        relvol_e=s['v'][e] / np.median(hist) if len(hist) >= 4 and np.median(hist) > 0 else np.nan,
        dist_atr=dist_atr,
        move_e=0.0 if cls == 'W1' else d * (c[e] / c[i] - 1) / (atr[i] / c[i]),
        rv=100 * atr[e] / c[e],
        s_eu=float(8 <= hour <= 12), s_us=float(13 <= hour <= 20), s_late=float(hour >= 21),
        c_R=float(cls == 'R'), c_W1=float(cls == 'W1'), hi_side=float(side == 'high'))


def fwd_outcomes(b, e, d):
    """after the entry, by design: entry at open e+1, closes of e+1, e+2, e+4 (trade P&L as a fraction, before fees)."""
    o, c = b['o'].to_numpy(float), b['c'].to_numpy(float)
    entry = o[e + 1]
    return dict(fwd_gross=d * (c[e + 4] / entry - 1), fwd_p1=d * (c[e + 1] / entry - 1), fwd_p2=d * (c[e + 2] / entry - 1))


def build(df):
    rows = []
    h4 = htf_series(S.bars(df, 240))
    dd = htf_series(S.bars(df, 1440))
    for tfn in TFS:
        tf, _L, N, _M = S.CFG[tfn]
        b = S.bars(df, tf)
        s = series(b)
        idx = {int(t): k for k, t in enumerate(s['t'])}
        tv = dict(zip(s['t'].tolist(), s['v'].tolist()))
        for side in (-1, 1):
            for ev in S.events(b, tfn, side, False, None):
                i = idx[int(ev['t'])]
                e = i if ev['cls'] == 'W1' else i + N
                d = side * SGN[ev['cls']]
                t_entry = int(s['t'][e]) + tf * 60
                r = dict(tf=tfn, cls=ev['cls'], side=ev['side'], t=t_entry, split=ev['split'], cont4=ev['cont4'] * SGN[ev['cls']])
                r.update(features_at(s, i, e, d, ev['cls'], ev['side'], ev['dist_atr'], t_entry, h4, dd, tv))
                r.update(fwd_outcomes(b, e, d))
                rows.append(r)
        print(tfn, 'events', sum(1 for r in rows if r['tf'] == tfn), file=sys.stderr)
    return pd.DataFrame(rows)


# ---- model and statistics -------------------------------------------------------------------------------------

def fit_logit(X, y, lam=LAM, iters=30):
    n, p = X.shape
    Xb = np.c_[np.ones(n), X]
    w = np.zeros(p + 1)
    pen = np.r_[0.0, np.full(p, lam)]
    for _ in range(iters):
        pr = 1 / (1 + np.exp(-np.clip(Xb @ w, -30, 30)))
        g = Xb.T @ (pr - y) + pen * w
        H = Xb.T @ (Xb * (pr * (1 - pr))[:, None]) + np.diag(pen)
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-8:
            break
    return w


def score(w, X):
    return np.c_[np.ones(len(X)), X] @ w


def blocks(t, start, end, k=NBLK):
    """k equal-time contiguous blocks over [start, end); returns (lo, hi) edges."""
    ed = np.linspace(start, end, k + 1)
    return list(zip(ed[:-1], ed[1:]))


def oof_buckets(X, y, t, start, end):
    """6-block purged CV. Returns bucket per event: 2 top, 1 middle, 0 bottom (cuts from the training fold's scores)."""
    out = np.full(len(y), -1)
    for lo, hi in blocks(t, start, end):
        te = (t >= lo) & (t < hi)
        tr = (t < lo - PURGE) | (t >= hi + PURGE)
        if te.sum() == 0 or tr.sum() < 50:
            continue
        mu, sd = X[tr].mean(0), X[tr].std(0)
        sd[sd == 0] = 1
        w = fit_logit((X[tr] - mu) / sd, y[tr])
        s_tr, s_te = score(w, (X[tr] - mu) / sd), score(w, (X[te] - mu) / sd)
        c1, c2 = np.quantile(s_tr, [1 / 3, 2 / 3])
        out[te] = np.where(s_te >= c2, 2, np.where(s_te < c1, 0, 1))
    return out


def wk_boot(vals, t, nb=NBOOT, seed=1):
    if len(vals) < 10:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    wk = (t // WEEK).astype(np.int64)
    groups = [vals[wk == w] for w in np.unique(wk)]
    ms = [np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))]).mean() for _ in range(nb)]
    return tuple(np.percentile(ms, [2.5, 97.5]))


def holm(ps):
    ps = np.asarray(ps, float)
    order = np.argsort(ps)
    adj = np.empty_like(ps)
    run = 0.0
    for r, k in enumerate(order):
        run = max(run, (len(ps) - r) * ps[k])
        adj[k] = min(1.0, run)
    return adj


def bh(ps):
    ps = np.asarray(ps, float)
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty_like(ps)
    run = 1.0
    for r in range(m - 1, -1, -1):
        k = order[r]
        run = min(run, ps[k] * m / (r + 1))
        adj[k] = run
    return adj


def early_gross(p_k, gross):
    """exit at the close of bar e+k when not in profit there, else hold to e+4."""
    return np.where(p_k <= 0, p_k, gross)


def bucket_stats(g, t):
    lo, hi = wk_boot(g - RT, t)
    return dict(n=int(len(g)), gross=100 * g.mean(), fee=100 * RT, net=100 * (g.mean() - RT), lo=100 * lo, hi=100 * hi)


def dev(out):
    T = pd.read_csv(os.path.join(out, 'table.csv'))
    T = T[T.split == 'DEV'].dropna(subset=FEATS).reset_index(drop=True)
    start = pd.Timestamp('2022-01-01', tz='UTC').timestamp()
    res = {'rt_pct': 100 * RT, 'meta': {}, 'early': {}, 'features': {}}
    pvals = []
    for tfn in TFS:
        D = T[T.tf == tfn].reset_index(drop=True)
        feats = [f for f in FEATS if not (tfn == '4h' and f == 'bbwp_4h')]
        X, g, t = D[feats].to_numpy(float), D.fwd_gross.to_numpy(float), D.t.to_numpy(np.int64)
        y = (g - RT > 0).astype(float)
        bk = oof_buckets(X, y, t, start, DEV_END)
        m = bk >= 0
        top = (bk == 2)
        real = (g[top] - RT).mean() - (g[m] - RT).mean()
        rng = np.random.default_rng(31)
        plac = []
        for _ in range(NPLAC):
            perm = rng.permutation(len(g))
            gp, yp = g[perm], y[perm]
            bp = oof_buckets(X, yp, t, start, DEV_END)
            plac.append((gp[bp == 2] - RT).mean() - (gp[bp >= 0] - RT).mean())
        p = (1 + sum(x >= real for x in plac)) / (NPLAC + 1)
        pvals.append(p)
        sd = (g[m] - RT).std()
        n3 = int(top.sum())
        cell = dict(n_all=int(m.sum()), all=bucket_stats(g[m], t[m]), top=bucket_stats(g[top], t[top]),
                    mid=bucket_stats(g[bk == 1], t[bk == 1]), bottom=bucket_stats(g[bk == 0], t[bk == 0]),
                    lift=100 * real, placebo_p=p, placebo_mean=100 * float(np.mean(plac)), placebo_p95=100 * float(np.percentile(plac, 95)),
                    top_net_2022=100 * ((g[top & (t < HALF)] - RT).mean()), top_net_2023=100 * ((g[top & (t >= HALF)] - RT).mean()),
                    n_top_2022=int((top & (t < HALF)).sum()), n_top_2023=int((top & (t >= HALF)).sum()),
                    sd_net=100 * sd, detectable_lift=100 * sd * np.sqrt(7.849 / max(n3, 1)), feats=feats)
        # descriptive: per feature, net in DEV thirds; winners vs losers median
        fd = {}
        for f in feats:
            x = D[f].to_numpy(float)
            if len(np.unique(x)) <= 2:
                rows = [(f'{f}={int(v)}', x == v) for v in np.unique(x)]
            else:
                q1, q2 = np.quantile(x, [1 / 3, 2 / 3])
                rows = [('low', x < q1), ('mid', (x >= q1) & (x < q2)), ('high', x >= q2)]
            fd[f] = dict(win_median=float(np.median(x[y == 1])), loss_median=float(np.median(x[y == 0])),
                         thirds=[dict(k=k, n=int(s.sum()), net=100 * ((g[s] - RT).mean()) if s.sum() else None) for k, s in rows])
        res['features'][tfn] = fd
        res['meta'][tfn] = cell
        # early-exit arm
        ec = {}
        winners = (g - RT) > 0
        for k, pk in ((1, D.fwd_p1.to_numpy(float)), (2, D.fwd_p2.to_numpy(float))):
            eg = early_gross(pk, g)
            diff = eg - g
            lo, hi = wk_boot(diff, t)
            elo, ehi = wk_boot(eg - RT, t)
            ec[f'k{k}'] = dict(n=int(len(g)), hold_net=100 * (g.mean() - RT), early_net=100 * (eg.mean() - RT), early_lo=100 * elo, early_hi=100 * ehi,
                               diff=100 * diff.mean(), diff_lo=100 * lo, diff_hi=100 * hi,
                               diff_2022=100 * diff[t < HALF].mean(), diff_2023=100 * diff[t >= HALF].mean(),
                               exited_share=float((pk <= 0).mean()), winners_underwater=float((pk[winners] <= 0).mean()),
                               losers_underwater=float((pk[~winners] <= 0).mean()))
        res['early'][tfn] = ec
        print(tfn, 'done', file=sys.stderr)
    ha, ba = holm(pvals), bh(pvals)
    for k, tfn in enumerate(TFS):
        c = res['meta'][tfn]
        c['holm_p'], c['bh_p'] = float(ha[k]), float(ba[k])
        same = c['top_net_2022'] > 0 and c['top_net_2023'] > 0
        if c['top']['n'] < 100:
            v = 'NOT ENOUGH DATA'
        elif c['top']['lo'] > 0 and c['holm_p'] <= 0.05 and same:
            v = 'PASS'
        elif c['placebo_p'] > 0.05 or c['top']['hi'] < 0:
            v = 'FAIL'
        else:
            v = 'INCONCLUSIVE'
        c['verdict'] = v
        for kk, e in res['early'][tfn].items():
            beats = e['diff_lo'] > 0 and e['diff_2022'] > 0 and e['diff_2023'] > 0
            e['verdict'] = ('BEATS HOLD, PROFITABLE' if beats and e['early_lo'] > 0 else 'BEATS HOLD, STILL LOSES' if beats
                            else 'WORSE THAN HOLD' if e['diff_hi'] < 0 else 'NO DIFFERENCE SHOWN')
    json.dump(res, open(os.path.join(out, 'dev.json'), 'w', newline='\n'), indent=1, default=float)
    return res


def main():
    stage = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    os.makedirs(out, exist_ok=True)
    if stage == 'build':
        df = S.load()
        build(df[df.t < S.END]).to_csv(os.path.join(out, 'table.csv'), index=False, lineterminator='\n')
    elif stage == 'dev':
        dev(out)
    else:
        raise SystemExit('val stage runs only for a DEV PASS (PRE_REG 3, 4); see RESULT.md')


if __name__ == '__main__':
    main()
