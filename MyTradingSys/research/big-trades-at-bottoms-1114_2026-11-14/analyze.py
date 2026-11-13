import glob, os, datetime as dt, numpy as np, pandas as pd
R = 'F:/MTS/data_cache/bigtrades'

def _md(self, index=True):
    df = self.reset_index() if index else self
    h = [str(c) for c in df.columns]
    lines = ['| ' + ' | '.join(h) + ' |', '|' + '|'.join(['---'] * len(h)) + '|']
    for _, r in df.iterrows():
        lines.append('| ' + ' | '.join(str(v) for v in r.values) + ' |')
    return chr(10).join(lines)
pd.DataFrame.to_markdown = _md
LOWS = ['2022-06-18', '2022-11-21', '2024-08-05', '2025-04-07', '2026-02-06', '2026-07-01']
d = np.load('F:/MTS/data_cache/binance_spot/BTCUSDT_15m.npz')
px = pd.DataFrame({'t': pd.to_datetime(d['t'], unit='ms'), 'l': d['l'], 'h': d['h'], 'c': d['c']}).set_index('t')
daily = px.c.resample('1D').last(); dhigh = px.h.resample('1D').max()
sma200 = daily.rolling(200).mean(); ath = dhigh.cummax()


def load(v):
    fs = sorted(glob.glob(f'{R}/{v}/*.csv'))
    x = pd.concat([pd.read_csv(f, parse_dates=['hour_utc']) for f in fs]).drop_duplicates('hour_utc').set_index('hour_utc').sort_index()
    return x


V = {v: load(v) for v in ('spot', 'fut', 'bybit')}
V['bn'] = V['spot'].add(V['fut'], fill_value=0)
prem = pd.read_csv(f'{R}/premium_1h.csv', parse_dates=['hour_utc']).set_index('hour_utc')


def feat(x, thr):
    b = x[f'sum_buy_{thr}']; s = x[f'sum_sell_{thr}']; tot = x['sum_buy_all'] + x['sum_sell_all']
    return pd.DataFrame({'buy': b, 'sell': s, 'net': b - s, 'tot': tot, 'nb': x[f'count_buy_{thr}'], 'ns': x[f'count_sell_{thr}']})


ev = []
out = []


def P(s=''):
    out.append(s)


P('## Events (low hour = lowest 15m low within the day -1/+2 days, from cached Binance spot)')
rows = []
for ds in LOWS:
    day = pd.Timestamp(ds)
    seg = px.loc[day - pd.Timedelta(days=1):day + pd.Timedelta(days=2)]
    lt = seg.l.idxmin().floor('h'); lp = seg.l.min()
    i = daily.index.get_loc(day)
    dd = lp / ath.iloc[i] - 1; rel = daily.iloc[i] / sma200.iloc[i] - 1
    h7 = dhigh.iloc[i - 49:i].max()
    ph = 'post-peak bear' if dd < -0.35 else 'bull / correction'
    rows.append(dict(low_utc=str(lt), low=lp, dd_from_ATH=f'{dd:.0%}', close_vs_200dSMA=f'{rel:+.0%}', drop_from_7w_high=f'{lp / h7 - 1:.0%}', phase_known_at_time=ph))
    ev.append((ds, lt))
P(pd.DataFrame(rows).to_markdown(index=False))
blocks = [('-96..-48h', -96, -48), ('-48..-24h', -48, -24), ('-24..0h', -24, 0), ('0..+24h', 0, 24), ('+24..+48h', 24, 48), ('+48..+96h', 48, 96)]


def blocktab(vn, thr, metric):
    res = {}
    x = feat(V[vn], thr)
    for ds, lt in ev:
        r = []
        for nm, a, b in blocks:
            w = x.loc[lt + pd.Timedelta(hours=a):lt + pd.Timedelta(hours=b) - pd.Timedelta(hours=1)]
            lg = w.buy.sum() + w.sell.sum()
            if metric == 'net_pct':
                r.append(w.net.sum() / w.tot.sum() * 1e4 if w.tot.sum() else np.nan)
            else:
                r.append(w.buy.sum() / lg * 100 if lg else np.nan)
        res[ds] = r
    return pd.DataFrame(res, index=[b[0] for b in blocks]).T


for vn, vl in (('bn', 'Binance spot + USDM futures'), ('bybit', 'Bybit USDT perp (individual fills, fewer big prints)')):
    for thr, tl in (('1m', '>= $1M'), ('5m', '>= $5M'), ('b50', '>= 50 BTC')):
        for metric, ml, fmt in (('net_pct', 'net large buying (buy minus sell) in bp of ALL volume in block', '{:+.1f}'), ('buyshare', 'buy share of large-trade volume, %', '{:.1f}')):
            if vn == 'bybit' and thr != '1m':
                continue
            t = blocktab(vn, thr, metric)
            P(); P(f'### {vl}, trades {tl}: {ml}'); P(t.map(lambda v: fmt.format(v)).to_markdown())
P(); P('### Binance spot+futures: count of >= $5M prints (buy/sell) per block')
x = feat(V['bn'], '5m'); rr = {}
for ds, lt in ev:
    rr[ds] = []
    for nm, a, b in blocks:
        w = x.loc[lt + pd.Timedelta(hours=a):lt + pd.Timedelta(hours=b) - pd.Timedelta(hours=1)]
        rr[ds].append(f'{int(w.nb.sum())}/{int(w.ns.sum())}')
P(pd.DataFrame(rr, index=[b[0] for b in blocks]).T.to_markdown())
P(); P('### Coinbase BTC-USD minus Binance BTCUSDT hourly close, bp, mean per block (includes USDT basis)')
rr = {}
for ds, lt in ev:
    rr[ds] = [prem.prem_bp.loc[lt + pd.Timedelta(hours=a):lt + pd.Timedelta(hours=b) - pd.Timedelta(hours=1)].mean() for _, a, b in blocks]
pt = pd.DataFrame(rr, index=[b[0] for b in blocks]).T
P(pt.map(lambda v: f'{v:+.1f}').to_markdown())
now_end = V['bn'].index.max() + pd.Timedelta(hours=1)
P(); P(f'## Today vs history (data through {now_end} UTC)')


def roll(vn, thr, H):
    x = feat(V[vn], thr)
    full = pd.date_range(x.index.min(), x.index.max(), freq='h')
    x = x.reindex(full)
    r = x.rolling(H, min_periods=H).sum()
    return pd.DataFrame({'net_bp': r.net / r.tot * 1e4, 'buyshare': r.buy / (r.buy + r.sell) * 100, 'lgshare': (r.buy + r.sell) / r.tot * 100})


today_rows = []
cut = pd.Timestamp('2026-10-24')
for thr in ('1m', '5m', 'b50'):
    for H in (24, 72):
        m = roll('bn', thr, H).dropna()
        hist = m[m.index < cut]; cur = m.iloc[-1]
        a = pd.DataFrame([m.loc[lt] for ds, lt in ev if lt in m.index])
        today_rows.append(dict(thr=thr, H=f'{H}h', net_bp_now=round(cur.net_bp, 1), pct_hist=round((hist.net_bp < cur.net_bp).mean() * 100), lows_below_now=f'{(a.net_bp < cur.net_bp).sum()}/{len(a)}',
                               buyshare_now=round(cur.buyshare, 1), bs_pct=round((hist.buyshare < cur.buyshare).mean() * 100), lgshare_now=round(cur.lgshare, 1), lg_pct=round((hist.lgshare < cur.lgshare).mean() * 100), lows_median_net=round(a.net_bp.median(), 1)))
P(pd.DataFrame(today_rows).to_markdown(index=False))
pm = prem.prem_bp; r24 = pm.rolling(24).mean(); cur = r24.iloc[-1]; hist = r24[r24.index < cut].dropna()
anch = [r24.loc[lt] for ds, lt in ev]
P(); P(f'Premium (24h mean) now {cur:+.1f} bp; percentile vs history windows {(hist < cur).mean() * 100:.0f}; at the 6 lows: ' + ', '.join(f'{v:+.1f}' for v in anch))
P(); P('### Last 3 weeks by UTC day (Binance spot+fut)')
rows = []
x1 = feat(V['bn'], '1m'); x5 = feat(V['bn'], '5m'); xb = feat(V['bn'], 'b50')
for day in pd.date_range('2026-10-24', '2026-11-12'):
    s = slice(day, day + pd.Timedelta(hours=23))
    w = x1.loc[s]; w5 = x5.loc[s]; wb = xb.loc[s]
    rows.append(dict(day=day.date(), close=round(daily.loc[day]), net1m_bp=round(w.net.sum() / w.tot.sum() * 1e4, 1), buyshare1m=round(w.buy.sum() / (w.buy.sum() + w.sell.sum()) * 100, 1), n5m_buy_sell=f'{int(w5.nb.sum())}/{int(w5.ns.sum())}', net50btc_bp=round(wb.net.sum() / wb.tot.sum() * 1e4, 1), prem_bp=round(prem.prem_bp.loc[s].mean(), 1)))
P(pd.DataFrame(rows).to_markdown(index=False))
open('analysis_out.md', 'w').write('\n'.join(out))
print('\n'.join(out))
