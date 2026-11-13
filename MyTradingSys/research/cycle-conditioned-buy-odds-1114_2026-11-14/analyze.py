import numpy as np, pandas as pd, json, os
rng = np.random.default_rng(7)
R = '../btc_cycles_2026-11/btc_daily.csv'
d = pd.read_csv(R, parse_dates=['date']).set_index('date')[['high', 'low', 'close']]
t = pd.read_csv('F:/MTS/data_cache/binance_1d/BTCUSDT_1d_tail.csv', parse_dates=['date']).set_index('date')
d = pd.concat([d[d.index < t.index[0]], t]).astype(float)
idx = pd.date_range(d.index[0], d.index[-1])
assert len(idx) == len(d), (len(idx), len(d))
mv = pd.read_csv('F:/MTS/data_cache/coinmetrics/btc_mvrv.csv', parse_dates=['date']).set_index('date')['mvrv']
d['mvrv'] = mv.reindex(d.index)
NOW = d.index[-1]  # provisional intraday
H = [30, 90, 180]
c, h, l = d.close, d.high, d.low
F = pd.DataFrame(index=d.index)
halv = pd.to_datetime(['2012-11-28', '2016-07-09', '2020-05-11', '2024-04-20'])
F['d_halv'] = [(x - halv[halv <= x][-1]).days if (halv <= x).any() else np.nan for x in d.index]
ath = h.cummax()
F['dd'] = c / ath - 1
athdate = pd.Series(np.where(h >= ath, d.index, pd.NaT), index=d.index)
athdate = pd.to_datetime(athdate).ffill()
F['d_ath'] = (pd.Series(d.index, index=d.index) - athdate).dt.days.values
F['d200w'] = c / c.rolling(1400).mean() - 1
F['d50w'] = c / c.rolling(350).mean() - 1
F['sma200d'] = c.rolling(200).mean()
w = d.resample('W-SUN').agg({'high': 'max', 'low': 'min', 'close': 'last'})


def rsi(x, n=14):
    dl = x.diff(); up = dl.clip(lower=0); dn = -dl.clip(upper=0)
    a = up.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    b = dn.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    return 100 - 100 / (1 + a / b)


def wt(hh, ll, cc, n1=10, n2=21):
    ap = (hh + ll + cc) / 3
    esa = ap.ewm(span=n1, adjust=False).mean()
    dd = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    ci = (ap - esa) / (0.015 * dd)
    return ci.ewm(span=n2, adjust=False).mean()


w['rsi'] = rsi(w.close); w['wt'] = wt(w.high, w.low, w.close)
w['red'] = (w.close < w.close.shift(1)).astype(int)
st = []; s = 0
for r in w.red:
    s = s + 1 if r else 0
    st.append(s)
w['streak'] = st
# w index label = Sunday week end; the last row may be incomplete (its label is in the future)
lastsun = pd.Series([x - pd.Timedelta(days=(x.weekday() + 1) % 7) for x in d.index], index=d.index)
# for non-Sunday x, lastsun = previous Sunday (completed week). For Sunday x, it is x itself (completed).
lw = w.reindex(lastsun.values); lw.index = d.index
F['rsiw'] = lw.rsi; F['wtw'] = lw.wt
isun = pd.Series(d.index.weekday == 6, index=d.index)
runred = (c < lw.close)
F['streak'] = np.where(isun, lw.streak, np.where(runred, np.where(lw.red == 1, lw.streak + 1, 1), 0))
F['mvrv'] = d.mvrv
F['phase'] = np.where(F.dd > -0.2, 'bull', np.where(c < F.sma200d, 'bear', 'base'))
for k in H:
    F[f'r{k}'] = c.shift(-k) / c - 1
    mn = l[::-1].rolling(k, min_periods=k).min()[::-1].shift(-1)
    F[f'm{k}'] = mn / c - 1
core = ['d_halv', 'd_ath', 'dd', 'streak', 'd200w', 'd50w', 'rsiw', 'wtw']
logc = ['d_halv', 'd_ath']


def X(cols):
    Z = F[cols].copy()
    for q_ in logc:
        if q_ in Z: Z[q_] = np.log1p(Z[q_])
    return Z


elig = F.dropna(subset=core + ['r90', 'm90']).index
print('first feature day', F.dropna(subset=core).index[0], 'eligible', len(elig), elig[0], elig[-1])


def greedy(dist, dates, k=15, ex=30):
    o = np.argsort(dist); ch = []
    for i in o:
        if np.isnan(dist[i]): continue
        if all(abs((dates[i] - dates[j]).days) > ex for j in ch): ch.append(i)
        if len(ch) == k: break
    return ch


def analogs(cols, q, pool_idx, k=15):
    Z = X(cols); P = Z.loc[pool_idx]; mu, sd = P.mean(), P.std()
    zq = ((Z.loc[q] - mu) / sd).values; zp = ((P - mu) / sd).values
    dist = np.sqrt(((zp - zq) ** 2).sum(1))
    ch = greedy(dist, pool_idx, k)
    return pool_idx[ch], dist[ch]


def episodes(ix, ex=30):
    ch = []
    for x in ix:
        if all(abs((x - y).days) > ex for y in ch): ch.append(x)
    return len(ch)


def stats(S, label, h=90):
    r = S[f'r{h}'].dropna(); m = S[f'm{h}'].dropna()
    return dict(set=label, n=len(r), med_r=r.median(), mean_r=r.mean(), pos=(r > 0).mean(),
                med_mae=m.median(), p10_mae=m.quantile(.1), mae20=(m < -.2).mean())


def boot(v, f=np.median, B=10000):
    v = np.asarray(v); b = [f(rng.choice(v, len(v))) for _ in range(B)]
    return tuple(np.round(np.percentile(b, [2.5, 97.5]), 4))


q = NOW; q2 = pd.Timestamp('2026-11-12')
pd.set_option('display.width', 250)
print('TODAY features'); print(F.loc[[q2, q], core + ['mvrv', 'phase']].T)
ALL = F.loc[elig]
out = {}; res = []
for name, cols in [('primary', core), ('V2_mvrv', core + ['mvrv']), ('V3_dd_d200_rsi', ['dd', 'd200w', 'rsiw'])]:
    pool = F.dropna(subset=cols + ['r90', 'm90']).index
    for qq in (q, q2):
        a, dist = analogs(cols, qq, pool)
        A = F.loc[a]
        out[(name, str(qq.date()))] = (a, dist)
        s = stats(A, name + '@' + str(qq.date()))
        s['ci_med_r'] = boot(A.r90); s['ci_med_mae'] = boot(A.m90)
        s['pct_rank_r'] = (ALL.r90 < s['med_r']).mean() * 100
        s['pct_rank_mae'] = (ALL.m90 < s['med_mae']).mean() * 100
        pl_r = []; pl_m = []
        for _ in range(1000 if name == 'primary' else 300):
            o = rng.permutation(len(pool)); ch = []
            for i in o:
                if all(abs((pool[i] - pool[j]).days) > 30 for j in ch): ch.append(i)
                if len(ch) == 15: break
            S = F.loc[pool[ch]]; pl_r.append(S.r90.median()); pl_m.append(S.m90.median())
        s['p_r_ge'] = (np.array(pl_r) >= s['med_r']).mean()
        s['p_mae_ge'] = (np.array(pl_m) >= s['med_mae']).mean()
        s['phase_mix'] = A.phase.value_counts().to_dict()
        s['dates'] = [str(x.date()) for x in sorted(a)]
        res.append(s)
allst = stats(ALL, 'ALL eligible'); allst['phase_mix'] = ALL.phase.value_counts().to_dict()
print(allst)
for s in res: print(json.dumps(s, default=str))
a, dist = out[('primary', str(q.date()))]
det = F.loc[a, ['dd', 'd_ath', 'd200w', 'rsiw', 'wtw', 'streak', 'phase', 'r30', 'r90', 'r180', 'm90']].copy(); det['dist'] = dist
print(det.sort_index().round(3).to_string())
pool = F.dropna(subset=['r90', 'm90', 'dd', 'd200w', 'd_ath'])
bins = {'B1 d200w<=+10%': pool.d200w <= .10, 'B2 d_ath 350-450': pool.d_ath.between(350, 450),
        'B3a dd -35..-20': pool.dd.between(-.35, -.2), 'B3b dd -50..-40': pool.dd.between(-.5, -.4)}
bins['B12 B1&B2'] = bins['B1 d200w<=+10%'] & bins['B2 d_ath 350-450']
bins['B1b B1&dd<=-40'] = bins['B1 d200w<=+10%'] & (pool.dd <= -.4)
rows = []
for nm, mk in [('ALL', pd.Series(True, index=pool.index))] + list(bins.items()):
    for phs in ['all', 'bull', 'base', 'bear']:
        S = pool[mk & ((pool.phase == phs) if phs != 'all' else True)]
        if len(S) == 0: continue
        r = stats(S, nm + '|' + phs); r['episodes'] = episodes(S.index)
        for hh in (30, 180): r[f'med_r{hh}'] = S[f'r{hh}'].median()
        rows.append(r)
B = pd.DataFrame(rows); print(B.round(3).to_string()); B.to_csv('bins.csv', index=False)
print('today', F.loc[q, ['dd', 'd_ath', 'd200w']].to_dict())
# walk-forward validation
val = F.loc['2024-01-01':].dropna(subset=core + ['r90']).index
pred = []
full = F.dropna(subset=core + ['r90', 'm90']).index
for t_ in val:
    pl = full[full <= t_ - pd.Timedelta(days=90)]
    a, _ = analogs(core, t_, pl); pred.append((t_, F.loc[a].r90.median(), F.loc[a].m90.median()))
P = pd.DataFrame(pred, columns=['t', 'pr', 'pm']).set_index('t')
P['r90'] = F.loc[P.index, 'r90']; P['m90'] = F.loc[P.index, 'm90']
lo, hi = P.pr.quantile([1 / 3, 2 / 3])
top = P[P.pr >= hi]; bot = P[P.pr <= lo]


def bb(P, B=2000):
    n = len(P); nb = int(np.ceil(n / 90)); r_ = []
    for _ in range(B):
        st_ = rng.integers(0, n - 90, nb); ix = np.concatenate([np.arange(s_, s_ + 90) for s_ in st_])[:n]; S = P.iloc[ix]
        r_.append(S[S.pr >= hi].r90.mean() - S[S.pr <= lo].r90.mean())
    return np.nanpercentile(r_, [2.5, 97.5])


print('VAL n', len(P), 'top r90', top.r90.mean(), 'bot', bot.r90.mean(), 'diff', top.r90.mean() - bot.r90.mean(),
      'CI', bb(P), 'corr', P.pr.corr(P.r90), 'top mae', top.m90.mean(), 'bot mae', bot.m90.mean(), 'all', P.r90.mean())
tp = F.loc[out[('primary', str(q.date()))][0]].r90.median()
print('today pred', tp, 'pct of val preds', (P.pr < tp).mean())
F.to_csv('F:/MTS/data_cache/btc_cycle_features_1114.csv')
