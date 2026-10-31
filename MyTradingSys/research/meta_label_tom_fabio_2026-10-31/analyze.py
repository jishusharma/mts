"""Meta-label test on the Tom VP and Fabio Model C sim-desk trades (PRE_REG.md). DEV only; VALIDATION is not read here.

Usage: python analyze.py [--trades DIR] [--placebo N] [--no-export]
Needs gen_trades.py output (default F:/MTS/runs/meta_label_tom_fabio_2026-10-31). Writes numbers.json and output.md next to this file and,
unless --no-export, the two sim-desk result files results/desk-meta_label_*.json (+ their catalogue rows).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import features as F  # noqa: E402

SEED, K_FOLDS, LAM, B_BOOT, MIN_TOP = 20261031, 6, 1.0, 2000, 100
TRADES = Path('F:/MTS/runs/meta_label_tom_fabio_2026-10-31')
N_FEATURES = 8
DAY = 86400000


# ---------- model ----------
def fit_logit(X, y, lam=LAM, iters=50):
    n, d = X.shape
    A = np.column_stack([np.ones(n), X])
    pen = np.r_[0.0, np.ones(d)] * lam
    b = np.zeros(d + 1)
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-np.clip(A @ b, -30, 30)))
        w = np.maximum(p * (1 - p), 1e-6)
        g = A.T @ (y - p) - pen * b
        H = (A * w[:, None]).T @ A + np.diag(pen + 1e-9)
        step = np.linalg.solve(H, g)
        b += step
        if np.abs(step).max() < 1e-8:
            break
    return b


def folds_of(week, k=K_FOLDS):
    """[(test_mask, train_mask)]: k contiguous blocks of equal numbers of distinct weeks; training trades within 1 week of the block are purged."""
    uw = np.unique(week)
    out = []
    for blk in np.array_split(uw, k):
        lo, hi = blk.min(), blk.max()
        test = (week >= lo) & (week <= hi)
        out.append((test, (week < lo - 1) | (week > hi + 1)))
    return out


def oof_buckets(X, y, folds, lam=LAM):
    """(out-of-fold score, bucket 0/1/2). Amendment 3 (POST HOC): the tercile cut points of a test block come from the TRAINING fold's
    in-sample scores, never from the test block's own scores."""
    s = np.full(len(y), np.nan)
    bk = np.full(len(y), -1, int)
    for test, train in folds:
        mu, sd = X[train].mean(0), X[train].std(0)
        sd = np.where(sd > 0, sd, 1.0)
        b = fit_logit((X[train] - mu) / sd, y[train], lam)
        s[test] = b[0] + ((X[test] - mu) / sd) @ b[1:]
        c1, c2 = np.percentile(b[0] + ((X[train] - mu) / sd) @ b[1:], [100 / 3, 200 / 3])
        bk[test] = np.where(s[test] > c2, 2, np.where(s[test] > c1, 1, 0))
    return s, bk


def oof_scores(X, y, folds, lam=LAM):
    return oof_buckets(X, y, folds, lam)[0]


def week_kfold(week, k=K_FOLDS, seed=SEED):
    """Beside-only CV (amendment 4): weeks assigned at random to k groups; training trades within 1 week of any test week are purged."""
    uw = np.unique(week)
    grp = dict(zip(uw.tolist(), np.random.default_rng(seed).permutation(len(uw)) % k))
    g = np.array([grp[int(w)] for w in week])
    out = []
    for f in range(k):
        test = g == f
        tw = set(week[test].tolist())
        near = np.isin(week, [w + d for w in tw for d in (-1, 0, 1)])
        out.append((test, ~near))
    return out


def holm(ps):
    """Holm step-down adjusted p-values, same order as ps."""
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * ps[i]))
        adj[i] = run
    return adj.tolist()


def bh(ps):
    """Benjamini-Hochberg adjusted p-values (q-values), same order as ps."""
    m = len(ps)
    order = np.argsort(ps)[::-1]
    adj = np.empty(m)
    prev = 1.0
    for r, i in enumerate(order):
        prev = min(prev, ps[i] * m / (m - r))
        adj[i] = prev
    return adj.tolist()


def terciles(score):
    """0 bottom, 1 middle, 2 top third by score rank (stable)."""
    r = np.empty(len(score), int)
    r[np.argsort(score, kind='stable')] = np.arange(len(score))
    return np.minimum(r * 3 // len(score), 2)


# ---------- day-block bootstrap ----------
class DayBoot:
    def __init__(self, day):
        self.u, self.inv = np.unique(day, return_inverse=True)

    def sums(self, vals, mask):
        S = np.bincount(self.inv[mask], weights=vals[mask], minlength=len(self.u))
        C = np.bincount(self.inv[mask], minlength=len(self.u)).astype(float)
        return S, C

    def ci(self, vals, mask, q=(2.5, 97.5), B=B_BOOT, seed=SEED):
        S, C = self.sums(vals, mask)
        idx = np.random.default_rng(seed).integers(0, len(self.u), (B, len(self.u)))
        with np.errstate(invalid='ignore', divide='ignore'):
            m = S[idx].sum(1) / C[idx].sum(1)
        return [float(x) for x in np.nanpercentile(m, q)]

    def spread_ci(self, vals, top, bot, q=(2.5, 97.5), B=B_BOOT, seed=SEED):
        St, Ct = self.sums(vals, top)
        Sb, Cb = self.sums(vals, bot)
        idx = np.random.default_rng(seed).integers(0, len(self.u), (B, len(self.u)))
        with np.errstate(invalid='ignore', divide='ignore'):
            m = St[idx].sum(1) / Ct[idx].sum(1) - Sb[idx].sum(1) / Cb[idx].sum(1)
        return [float(x) for x in np.nanpercentile(m, q)]


def spread_of(net, tc):
    return float(net[tc == 2].mean() - net[tc == 0].mean())


def power(sd, n):
    return float(sd * np.sqrt(7.849 / n)) if n else float('nan')


def luck(sd, n, tries):
    return float(sd * np.sqrt(2 * np.log(tries)) / np.sqrt(n)) if n > 1 and tries > 1 else 0.0


# ---------- readings (descriptive table) ----------
def readings(raw, n):
    """{feature label: array of reading strings} over all filled trades; 'not available' where the feature is NaN."""
    def lab(x, rules, nan='not available'):
        out = np.full(len(x), nan, dtype=object)
        for cond, text in rules:
            out[np.where(np.isnan(x), False, cond(x))] = text
        return out
    rv = raw['relvol']
    lo, hi = np.nanpercentile(rv, [100 / 3, 200 / 3])
    return {
        'BBWP (1h)': lab(raw['bbwp'], [(lambda x: x <= 30, 'compression, 30 or below'), (lambda x: (x > 30) & (x < 85), 'normal, 30 to 85'), (lambda x: x >= 85, 'expansion, 85 or above')]),
        'D1 trend': lab(raw['d1'], [(lambda x: x > 0, 'up (close above 50-day average)'), (lambda x: x < 0, 'down (close below 50-day average)'), (lambda x: x == 0, 'flat')]),
        'Cowen band (daily close)': lab(raw['cowen'], [(lambda x: x > 0, 'above the band'), (lambda x: x == 0, 'inside the band'), (lambda x: x < 0, 'below the band')]),
        'Funding sign': lab(raw['fund'], [(lambda x: x > 0, 'positive'), (lambda x: x == 0, 'zero'), (lambda x: x < 0, 'negative')]),
        'Session (UTC)': lab(raw['hour'], [(lambda x: (x >= 21) | (x < 7), 'Asia, 21-07'), (lambda x: (x >= 7) & (x < 13), 'Europe, 07-13'), (lambda x: (x >= 13) & (x < 21), 'US, 13-21')]),
        'RSI 14 (1h)': lab(raw['rsi'], [(lambda x: x <= 40, 'low, 40 or below'), (lambda x: (x > 40) & (x < 60), 'middle, 40 to 60'), (lambda x: x >= 60, 'high, 60 or above')]),
        'WaveTrend (1h)': lab(raw['wt'], [(lambda x: x <= -1, 'oversold'), (lambda x: x == 0, 'middle'), (lambda x: x >= 1, 'overbought')]),
        'Relative volume (1h)': lab(rv, [(lambda x: x <= lo, 'low third'), (lambda x: (x > lo) & (x <= hi), 'middle third'), (lambda x: x > hi, 'high third')]),
    }


def table_rows(read, net):
    rows = []
    for feat, lab in read.items():
        for v in dict.fromkeys(lab.tolist()):
            m = lab == v
            rows.append([f'{feat}: {v}', str(int(m.sum())), f'{100 * float((net[m] > 0).mean()):.1f}', f'{float(net[m].mean()):+.3f}'])
    return rows


def splits(read, net, db, q):
    out = []
    for feat, lab in read.items():
        for v in dict.fromkeys(lab.tolist()):
            m = lab == v
            lo, hi = db.ci(net, m, q=q) if m.sum() >= 30 else (float('nan'), float('nan'))
            out.append({'feature': feat, 'reading': v, 'n': int(m.sum()), 'win_pct': 100 * float((net[m] > 0).mean()), 'mean': float(net[m].mean()),
                        'lo': lo, 'hi': hi, 'distinguishable_from_zero': bool(lo == lo and (lo > 0 or hi < 0))})
    return out


# ---------- one study ----------
def analyse(name, t, raw, placebo_n, log=print):
    net, side, tt = t['net'], t['side'], t['touch_t']
    day = tt // DAY
    week = (tt // DAY + 3) // 7
    Xall = F.model_matrix(raw, side)
    cc = np.isfinite(Xall).all(1)
    X, y, nt, wk, dy = Xall[cc], (net[cc] > 0).astype(float), net[cc], week[cc], day[cc]
    folds = folds_of(wk)
    sc, tc = oof_buckets(X, y, folds)
    assert np.isfinite(sc).all() and (tc >= 0).all()
    gr, fe = t['gross'][cc], t['fees'][cc]
    db = DayBoot(dy)
    top, mid, bot = tc == 2, tc == 1, tc == 0
    sd, n_top = float(nt.std(ddof=1)), int(top.sum())
    real = spread_of(nt, tc)
    rng = np.random.default_rng(SEED)
    pl = np.empty(placebo_n)
    for b in range(placebo_n):
        p = rng.permutation(len(nt))
        npm = nt[p]
        pl[b] = spread_of(npm, oof_buckets(X, (npm > 0).astype(float), folds)[1])
    p95 = float(np.percentile(pl, 95))
    top_lo, top_hi = db.ci(nt, top)
    sp_lo, sp_hi = db.spread_ci(nt, top, bot)
    top_lo975, top_hi975 = db.ci(nt, top, q=(1.25, 98.75))
    pos, neg = sc[y == 1], sc[y == 0]
    order = np.argsort(np.r_[pos, neg], kind='stable')
    ranks = np.empty(len(order))
    ranks[order] = np.arange(1, len(order) + 1)
    rank_auc = float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))
    passed = bool(top_lo > 0 and nt[top].mean() > 0 and real > p95)
    n_need = int(np.ceil(7.849 * (sd / 0.30) ** 2))            # amendment 8 (POST HOC): n per tercile to see a 0.30 R lift
    inconclusive = bool(top_lo <= 0 <= top_hi and n_top < n_need)
    word = 'PASSED' if passed else ('NOT ENOUGH DATA' if (n_top < MIN_TOP or inconclusive) else 'FAILED')
    sc2, tc2 = oof_buckets(X, y, week_kfold(wk))
    top2, bot2 = tc2 == 2, tc2 == 0
    t2_lo, t2_hi = db.ci(nt, top2)
    per = {}
    for lab, m in (('2022', dy < 19358), ('2023-01..2024-06', dy >= 19358)):          # 19358 = 2023-01-01
        tp, bt = top & m, bot & m
        per[lab] = {'n_top': int(tp.sum()), 'top_mean': float(nt[tp].mean()) if tp.any() else None, 'n_bottom': int(bt.sum()),
                    'bottom_mean': float(nt[bt].mean()) if bt.any() else None,
                    'spread': float(nt[tp].mean() - nt[bt].mean()) if tp.any() and bt.any() else None}
    sg = [v['top_mean'] for v in per.values()]
    sp = [v['spread'] for v in per.values()]
    read = readings(raw, len(net))
    allday = DayBoot(day)
    res = {'study': name, 'n_filled': int(len(net)), 'n_model': int(cc.sum()), 'n_dropped_incomplete': int((~cc).sum()), 'sd_all_filled': float(net.std(ddof=1)),
           'mean_all_filled': float(net.mean()), 'mean_model_sample': float(nt.mean()), 'win_pct_model_sample': 100 * float((nt > 0).mean()),
           'n_top': n_top, 'terciles': {k: {'n': int(m.sum()), 'mean': float(nt[m].mean()), 'win_pct': 100 * float((nt[m] > 0).mean()),
                                          'sd': float(nt[m].std(ddof=1))} for k, m in (('top', top), ('middle', mid), ('bottom', bot))},
           'top_ci95': [top_lo, top_hi], 'top_ci975': [top_lo975, top_hi975], 'spread': real, 'spread_ci95': [sp_lo, sp_hi],
           'placebo_n': placebo_n, 'placebo_p95': p95, 'placebo_mean': float(pl.mean()), 'placebo_p': float((1 + (pl >= real).sum()) / (1 + placebo_n)),
           'placebo_percentile_of_real': float(100 * (pl < real).mean()), 'oof_auc': rank_auc, 'power_delta_min_top': power(sd, n_top),
           'luck_best_of_16_top': luck(sd, n_top, 16), 'passed': passed, 'verdict': word,
           'random_third_mean': float(nt.mean()), 'table': table_rows(read, net), 'n_needed_for_0p30R_lift': n_need,
           'bucket_money': {k: {'n': int(m.sum()), 'gross': float(gr[m].mean()), 'fee': float(fe[m].mean()), 'net': float(nt[m].mean()),
                                'too_few': bool(m.sum() < 30)} for k, m in (('top', top), ('middle', mid), ('bottom', bot))},
           'week_kfold': {'top_mean': float(nt[top2].mean()), 'top_ci95': [t2_lo, t2_hi], 'bottom_mean': float(nt[bot2].mean()),
                          'spread': float(nt[top2].mean() - nt[bot2].mean()), 'n_top': int(top2.sum())},
           'periods': per, 'same_sign_top': bool(None not in sg and (sg[0] > 0) == (sg[1] > 0)),
           'same_sign_spread': bool(None not in sp and (sp[0] > 0) == (sp[1] > 0)),
           'splits': splits(read, net, allday, (0.3125, 99.6875))}
    log(f"{name}: n {len(net)} model {int(cc.sum())} top n {n_top} top {res['terciles']['top']['mean']:+.3f} [{top_lo:+.3f}, {top_hi:+.3f}] "
        f"bottom {res['terciles']['bottom']['mean']:+.3f} spread {real:+.3f} placebo p95 {p95:+.3f} p {res['placebo_p']:.3f} -> {word}")
    return res, {'cc': cc, 'tc': tc, 'sc': sc}


def verdict_line(r):
    t = r['terciles']['top']
    lo, hi = r['top_ci95']
    return (f"Best third by filter: {t['mean']:+.3f} R (range {lo:+.3f}..{hi:+.3f}) vs random third: {r['random_third_mean']:+.3f} R -> {r['verdict']}")


# ---------- export to the sim desk ----------
def export(name, study, q, r, trades, aux, results_dir):
    import charts as ch
    import desk
    res = study.run(q, progress=lambda *_: None)
    filled = np.flatnonzero(np.asarray(res['filled'], bool))
    tt = np.asarray(res['touch_t'])[filled]
    bucket = {}
    cc_idx = np.flatnonzero(aux['cc'])
    for j, i in enumerate(cc_idx):
        bucket[int(trades['touch_t'][i])] = int(aux['tc'][j])
    items = []
    for lab, want in (('Best third by filter', 2), ('Worst third by filter', 0)):
        m = np.zeros(len(res['net']), bool)
        for k, i in enumerate(filled):
            m[i] = bucket.get(int(tt[k])) == want
        sub = dict(res)
        sub['filled'] = m
        for it in ch.make(study, q, sub):
            it['note'] = f"{lab}: {it.get('note', '')}"
            items.append(it)
    ex = ch.export_example(items)
    ex['title'] = 'Example trades: 3 winners and 3 losers closest to typical, first in the best third by filter, then in the worst third'
    table = {'kind': 'table', 'title': f"{NAMES[name]}: what each layer reading did to its trades (all filled trades; each layer's rows add up to the filled-trade count)",
             'caption': 'win % = share of trades above 0 R after fees; average R after fees per trade; readings are the raw state at entry',
             'cols': ['Layer reading', 'trades', 'win %', 'average R after fees'], 'rows': r['table']}
    line = verdict_line(r)
    tone = {'PASSED': 'good', 'FAILED': 'bad'}.get(r['verdict'], 'warn')
    rid = f'desk-meta_label_{name}'
    title = {'tom_vp': 'Meta-label test, Tom VP daily value-area fade: can other layers\' state at entry pick the winners?',
             'fabio_c': 'Meta-label test, Fabio Model C price-only stand-in (ours): can other layers\' state at entry pick the winners?'}[name]
    doc = {'id': rid, 'kind': 'backtest', 'parity': None, 'family': 'Meta-label (layer filter)', 'title': title,
           'what': [{'name': 'Study', 'value_plain': f"{NAMES[name]}. {study.TITLE}: {study.label(q)}", 'label': 'OURS'},
                    {'name': 'Filter', 'value_plain': 'logistic score from 8 layer readings at entry (BBWP, D1 trend, Cowen band side, funding sign, session, RSI zone, WaveTrend zone, relative volume), '
                     'scored out of fold with week-purged blocked CV; thirds by score. Pre-registered in research/meta_label_tom_fabio_2026-10-31/PRE_REG.md', 'label': 'OURS'}],
           'how': 'Re-ran the study on development data, scored every trade out of fold, compared the best third by score with a random third; shuffled-label placebo and day-block bootstrap in REPORT.md.',
           'window': 'DEV only, 2022-04-01 to 2024-06-30 (VALIDATION and HOLDOUT never offered)',
           'verdict': {'label': r['verdict'], 'tone': tone}, 'why': [line],
           'kpis': [{'label': 'filled trades', 'value': str(r['n_filled'])}],
           'examples': [table, ex], 'source_files': ['MyTradingSys/research/meta_label_tom_fabio_2026-10-31/analyze.py'], 'commit': 'local desk run'}
    d = Path(results_dir)
    (d / f'{rid}.json').write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    cp = d / '_catalogue.json'
    cat = json.loads(cp.read_text(encoding='utf-8'))
    cat['rows'] = [x for x in cat['rows'] if x['id'] != rid]
    cat['rows'].append({'id': rid, 'family': doc['family'], 'title': title, 'kind': 'backtest', 'kind_source': 'result file', 'verdict': r['verdict'],
                        'source': f'MyTradingSys/research/sim_desk/results/{rid}.json', 'exported': True, 'result_id': rid, 'date': '2026-10-31',
                        'status': 'FAILED' if r['verdict'] == 'FAILED' else 'SEE_VERDICT',
                        'verdict_class': {'PASSED': 'passed', 'FAILED': 'failed'}.get(r['verdict'], 'unclear')})
    cat['rows'].sort(key=lambda x: (not x['exported'], x['family'].lower(), x['title'].lower()))
    cat['count'], cat['exported'] = len(cat['rows']), sum(1 for x in cat['rows'] if x['exported'])
    cp.write_text(json.dumps(cat, indent=0, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    return rid


def fill_check(study, q):
    """Amendment 1: features are stamped at the fill bar open. Replays every filled trade and compares the fill time with the desk's touch_t."""
    import _bars
    res = study.run(q, progress=lambda *_: None)
    a = _bars.load_1m()
    n = bad = later = 0
    for ref, f in zip(res['refs'], np.asarray(res['filled'], bool)):
        if not f:
            continue
        tr = _bars.replay(a, ref, q)
        n += 1
        if tr['entry'][0] != ref[1]:
            bad += 1
            later += tr['entry'][0] > ref[1]
    return {'filled_checked': n, 'fill_time_differs_from_touch_t': bad, 'fill_later_than_touch_t': int(later)}


NAMES = {'tom_vp': 'Tom VP daily value-area fade (prior_day FADE n6 shift WITH)', 'fabio_c': 'Fabio Model C price-only stand-in (ours)'}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--trades', default=str(TRADES))
    ap.add_argument('--placebo', type=int, default=300)
    ap.add_argument('--no-export', action='store_true')
    a = ap.parse_args(argv)
    import fabio_v3
    import tom_vp
    arr = tom_vp.load_1m_vol(lambda *_: None)
    ctx = F.build_context(arr, F.load_funding())
    out, aux_all, md = {}, {}, ['# Output of analyze.py (DEV only; amendments 1-8 of ROADMAP 2.1 applied POST HOC, after a first DEV read)\n']
    setups = (('tom_vp', tom_vp, {'symbol': 'BTCUSDT', 'anchor': 'prior_day', 'setup': 'FADE', 'accept_n': 6, 'shift': 'WITH', 'stop_atr': 1.0, 'target': 'POC'}),
              ('fabio_c', fabio_v3, {'model': 'C'}))
    for name, study, p in setups:
        z = np.load(Path(a.trades) / f'trades_{name}.npz', allow_pickle=True)
        t = {k: z[k] for k in z.files}
        raw = F.raw_features(ctx, t['touch_t'])
        r, aux = analyse(name, t, raw, a.placebo)
        r['fill_check'] = fill_check(study, study.normalize(p))
        out[name], aux_all[name] = r, (t, aux)
    ps = [out[n]['placebo_p'] for n, _, _ in setups]
    for (n, _, _), h, q in zip(setups, holm(ps), bh(ps)):
        out[n]['holm_p'], out[n]['bh_q'], out[n]['family_m'] = h, q, len(ps)
    for name, study, p in setups:
        r = out[name]
        md += [f"## {NAMES[name]}: {verdict_line(r)}\n", f"Holm-adjusted placebo p {r['holm_p']:.3f} (m = {r['family_m']}), BH q {r['bh_q']:.3f}\n",
               '| layer reading | trades | win % | average R after fees |', '|---|---|---|---|']
        md += ['| ' + ' | '.join(row) + ' |' for row in r['table']] + ['']
        if not a.no_export:
            export(name, study, study.normalize(p), r, aux_all[name][0], aux_all[name][1], HERE.parent / 'sim_desk' / 'results')
    (HERE / 'numbers.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8', newline='\n')
    (HERE / 'output.md').write_text('\n'.join(md) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
