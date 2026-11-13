"""Spot-only (Binance) comparison including the 2026-11-13 drop day (REST data; futures/Bybit dumps for that day are not published yet)."""
import glob, numpy as np, pandas as pd
R = 'F:/MTS/data_cache/bigtrades'
d = np.load('F:/MTS/data_cache/binance_spot/BTCUSDT_15m.npz')
px = pd.DataFrame({'t': pd.to_datetime(d['t'], unit='ms'), 'l': d['l'], 'c': d['c']}).set_index('t')
sp = pd.concat([pd.read_csv(f, parse_dates=['hour_utc']) for f in sorted(glob.glob(f'{R}/spot/*.csv'))]).drop_duplicates('hour_utc').set_index('hour_utc').sort_index()
prem = pd.read_csv(f'{R}/premium_1h.csv', parse_dates=['hour_utc']).set_index('hour_utc')
LOWS = ['2022-06-18', '2022-11-21', '2024-08-05', '2025-04-07', '2026-02-06', '2026-07-01']
lows = []
for ds in LOWS:
    day = pd.Timestamp(ds); seg = px.loc[day - pd.Timedelta(days=1):day + pd.Timedelta(days=2)]
    lows.append(seg.l.idxmin().floor('h'))
last = px.loc['2026-11-13']; lt_now = last.l.idxmin()
print('2026-11-13 low', last.l.min(), 'at', lt_now, 'last bar', px.index[-1], 'close', px.c.iloc[-1])
end = sp.index.max()
print('spot data ends hour', end)
rows = []
cut = pd.Timestamp('2026-10-24')
full = pd.date_range(sp.index.min(), end, freq='h')
for thr in ('1m', 'b10', 'b50'):
    b = sp[f'sum_buy_{thr}'].reindex(full); s = sp[f'sum_sell_{thr}'].reindex(full); tot = (sp.sum_buy_all + sp.sum_sell_all).reindex(full)
    for H in (24, 72):
        rb = b.rolling(H, min_periods=H).sum(); rs = s.rolling(H, min_periods=H).sum(); rt = tot.rolling(H, min_periods=H).sum()
        net = ((rb - rs) / rt * 1e4); share = rb / (rb + rs) * 100; lg = (rb + rs) / rt * 100
        hist = net[net.index < cut].dropna(); a = net.reindex([l for l in lows]).dropna()
        cur = net.iloc[-1]
        # also window ending at the 2026-11-13 low hour
        at_low = net.get(lt_now.floor('h'), np.nan)
        rows.append(dict(thr=thr, H=f'{H}h', net_bp_end=round(cur, 1), net_bp_at_nov13_low=round(at_low, 1), pct_vs_hist=round((hist < cur).mean() * 100), lows_below_now=f'{(a < cur).sum()}/{len(a)}',
                         lows_median=round(a.median(), 1), buyshare_end=round(share.iloc[-1], 1), buyshare_pct=round((share[share.index < cut].dropna() < share.iloc[-1]).mean() * 100), lgshare_end=round(lg.iloc[-1], 2), lg_pct=round((lg[lg.index < cut].dropna() < lg.iloc[-1]).mean() * 100)))
print(pd.DataFrame(rows).to_string(index=False))
# the 6 lows, spot only, same metrics at the low hour (24h ending at low and 24h after)
print('\nSpot-only at each low: 24h ending at low | 24h after low (net bp of all spot volume; buy share %), thr b50')
for l in lows:
    def m(a, bnd):
        w = sp.loc[a:bnd]; bb = w.sum_buy_b50.sum(); ss = w.sum_sell_b50.sum(); t = w.sum_buy_all.sum() + w.sum_sell_all.sum()
        return (bb - ss) / t * 1e4, bb / (bb + ss) * 100
    p = m(l - pd.Timedelta(hours=23), l); n = m(l + pd.Timedelta(hours=1), l + pd.Timedelta(hours=24))
    print(l, 'before %+.0f bp / %.0f%%' % p, '| after %+.0f bp / %.0f%%' % n)
w = sp.loc[lt_now.floor('h') - pd.Timedelta(hours=23):lt_now.floor('h')]; bb = w.sum_buy_b50.sum(); ss = w.sum_sell_b50.sum(); t = w.sum_buy_all.sum() + w.sum_sell_all.sum()
print('2026-11-13 low hour', lt_now, 'before %+.0f bp / %.0f%%' % ((bb - ss) / t * 1e4, bb / (bb + ss) * 100))
y = sp.loc['2026-11-13']; print('11-13 UTC day so far: b50 buy/sell $M', y.sum_buy_b50.sum() / 1e6, y.sum_sell_b50.sum() / 1e6, ' 1m buy/sell', y.sum_buy_1m.sum() / 1e6, y.sum_sell_1m.sum() / 1e6, 'counts b50', y.count_buy_b50.sum(), y.count_sell_b50.sum(), 'total', (y.sum_buy_all.sum() + y.sum_sell_all.sum()) / 1e6)
print('hourly 11-13 b50 net $M, price', )
y2 = sp.loc['2026-11-12 12:00':'2026-11-13 21:00']; print(((y2.sum_buy_b50 - y2.sum_sell_b50) / 1e6).round(1).to_string())
print(prem.prem_bp.loc['2026-11-13'].describe().round(1).to_string())
print('premium hourly last 6', prem.prem_bp.iloc[-6:].round(1).tolist())

print('\n--- spot all-trade taker imbalance (buy-sell)/total, bp, 24h ending at hour ---')
b = sp.sum_buy_all.reindex(full); s = sp.sum_sell_all.reindex(full)
imb24 = ((b - s).rolling(24, min_periods=24).sum() / (b + s).rolling(24, min_periods=24).sum() * 1e4)
imb72 = ((b - s).rolling(72, min_periods=72).sum() / (b + s).rolling(72, min_periods=72).sum() * 1e4)
vol24 = (b + s).rolling(24, min_periods=24).sum() / 1e6
hist = imb24[imb24.index < cut].dropna()
print('lows imb24:', [round(imb24.get(l, np.nan), 1) for l in lows], 'vol24 $M:', [round(vol24.get(l, np.nan)) for l in lows])
print('now imb24 %.1f (pct vs hist %.0f), at Nov13 low hour %.1f; imb72 now %.1f; vol24 now %.0f $M, pct %.0f' % (imb24.iloc[-1], (hist < imb24.iloc[-1]).mean() * 100, imb24.get(lt_now.floor('h')), imb72.iloc[-1], vol24.iloc[-1], (vol24[vol24.index < cut].dropna() < vol24.iloc[-1]).mean() * 100))
print('lows premium at low hour:', [round(prem.prem_bp.get(l, np.nan), 1) for l in lows], 'prem at 11-13 low hour', round(prem.prem_bp.get(lt_now.floor('h')), 1))
# share of volume in >=$1M prints, per venue per event window (all days)
for v in ('spot', 'fut', 'bybit'):
    x = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f'{R}/{v}/*.csv'))])
    t = x.sum_buy_all.sum() + x.sum_sell_all.sum()
    print(v, 'share of volume in >=$1M prints %.2f%%, >=$5M %.2f%%, >=50BTC %.2f%%' % (((x.sum_buy_1m.sum() + x.sum_sell_1m.sum()) / t * 100), ((x.sum_buy_5m.sum() + x.sum_sell_5m.sum()) / t * 100), ((x.sum_buy_b50.sum() + x.sum_sell_b50.sum()) / t * 100)))
