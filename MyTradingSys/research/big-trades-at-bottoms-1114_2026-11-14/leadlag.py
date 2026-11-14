"""Descriptive check: does large-trade net flow lead or just follow price? (not a trading rule, no outcomes tuned)"""
import glob, numpy as np, pandas as pd
R = 'F:/MTS/data_cache/bigtrades'
d = np.load('F:/MTS/data_cache/binance_spot/BTCUSDT_15m.npz')
px = pd.DataFrame({'t': pd.to_datetime(d['t'], unit='ms'), 'c': d['c']}).set_index('t').c.resample('1h').last()
def load(v):
    return pd.concat([pd.read_csv(f, parse_dates=['hour_utc']) for f in sorted(glob.glob(f'{R}/{v}/*.csv'))]).drop_duplicates('hour_utc').set_index('hour_utc').sort_index()
bn = load('spot').add(load('fut'), fill_value=0)
LOWS = ['2022-06-18', '2022-11-21', '2024-08-05', '2025-04-07', '2026-02-06', '2026-07-01']
res = []
for thr in ('1m', 'b50'):
    net = (bn[f'sum_buy_{thr}'] - bn[f'sum_sell_{thr}']); tot = bn.sum_buy_all + bn.sum_sell_all
    full = pd.date_range(bn.index.min(), bn.index.max(), freq='h')
    f24 = (net.reindex(full).rolling(24, min_periods=24).sum() / tot.reindex(full).rolling(24, min_periods=24).sum() * 1e4)
    ret_past = np.log(px).diff(24).reindex(full)
    ret_next = (np.log(px).shift(-24) - np.log(px)).reindex(full)
    # non-overlapping 24h samples to avoid inflated n
    idx = [t for t in full if t.hour == 0]
    df = pd.DataFrame({'flow24': f24.reindex(idx), 'past': ret_past.reindex(idx), 'next': ret_next.reindex(idx)}).dropna()
    # exclude the per-event dependence by also reporting per event
    res.append((thr, len(df), df.flow24.corr(df.past), df.flow24.corr(df.next), df.flow24.rank().corr(df.past.rank()), df.flow24.rank().corr(df.next.rank())))
    # "capitulation" days: flow24 in bottom quintile of the sample -> next-24h return
    q = df.flow24.quantile(0.2); lo = df[df.flow24 <= q]
    print(thr, 'n days', len(df), 'bottom-quintile flow days', len(lo), 'mean next-24h ret %.2f%% vs all %.2f%%' % (lo.next.mean() * 100, df.next.mean() * 100), 'share up %.0f%% vs %.0f%%' % ((lo.next > 0).mean() * 100, (df.next > 0).mean() * 100))
print(pd.DataFrame(res, columns=['thr', 'n_days', 'corr(flow24, past24h ret)', 'corr(flow24, next24h ret)', 'spearman past', 'spearman next']).round(3).to_string(index=False))
