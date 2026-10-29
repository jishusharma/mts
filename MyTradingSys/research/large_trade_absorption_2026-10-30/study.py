"""Operator shot d107df338858 (2026-10-30): CoinGlass Large Trades bubbles. Big green (buy) bubbles printed on red
5m bars after the 81,953 top and on the 80.5k breakdown; price kept falling. He asks MTS to read buying vs
absorption live. Fabio F-CVD4: "positive delta but negative closure. This is the textbook example for absorption."

Definitions fixed before the first run (all OURS; descriptive, no fees; DEV = 2024-12-02 .. 2025-12-31 only):
- Data: F:/MTS/data/orderflow_1m (Binance BTCUSDT perp aggTrades rolled to 1m): b99_buy_vol / b99_sell_vol = volume
  of prints at or above the trailing 99th-percentile trade size (the bubbles). Rolled to 5m bars.
- Large net = b99_buy - b99_sell in the bar. A bar is a LARGE-BUY bar when large net is in the top 2% of all 5m bars
  (threshold from DEV), LARGE-SELL in the bottom 2%.
- Result of the bar: green = close > open by >= 0.05%; red = close < open by >= 0.05%; else flat.
- Classes: buy-aggression = large-buy + green; buy-absorbed = large-buy + red (effort, no result);
  sell-aggression = large-sell + red; sell-absorbed = large-sell + green.
- Outcomes from the bar close: close 60 min and 4 h later up; first of +0.5% / -0.5% within 4 h. No overlap: skip 6 bars.
"""
import glob
import numpy as np, pandas as pd

fs = [f for f in sorted(glob.glob('F:/MTS/data/orderflow_1m/*.csv.gz')) if f.replace('\\', '/').split('/')[-1][:7] <= '2025-12']
d = pd.concat([pd.read_csv(f, usecols=['t', 'o', 'h', 'l', 'c', 'b99_buy_vol', 'b99_sell_vol', 'delta']) for f in fs], ignore_index=True)
d = d.drop_duplicates('t').sort_values('t')
d['g'] = d.t // 300000
b = d.groupby('g').agg(o=('o', 'first'), h=('h', 'max'), l=('l', 'min'), c=('c', 'last'), lb=('b99_buy_vol', 'sum'),
                       ls=('b99_sell_vol', 'sum'), dl=('delta', 'sum'), n=('c', 'size')).reset_index()
b = b[b.n == 5].reset_index(drop=True)
g = b.g.to_numpy(); o, h, l, c = (b[x].to_numpy(float) for x in 'ohlc')
net = (b.lb - b.ls).to_numpy(float)
hi, lo = np.quantile(net, 0.98), np.quantile(net, 0.02)
print(f'5m bars {len(b)}; large-net thresholds: buy >= {hi:.1f} BTC, sell <= {lo:.1f} BTC')
rows = []; i = 0; N = len(c)
while i < N - 49:
    if not (net[i] >= hi or net[i] <= lo) or g[i + 48] - g[i] != 48:
        i += 1; continue
    r = c[i] / o[i] - 1
    res = 'green' if r >= .0005 else 'red' if r <= -.0005 else 'flat'
    side = 'buy' if net[i] >= hi else 'sell'
    cls = {('buy', 'green'): 'buy-aggression', ('buy', 'red'): 'buy-absorbed', ('sell', 'red'): 'sell-aggression',
           ('sell', 'green'): 'sell-absorbed'}.get((side, res), f'{side}-flat')
    up, dn = c[i] * 1.005, c[i] * 0.995; first = 'none'
    for j in range(i + 1, i + 49):
        a, z = h[j] >= up, l[j] <= dn
        if a and z: first = 'both'; break
        if a: first = 'up'; break
        if z: first = 'down'; break
    rows.append(dict(cls=cls, up60=c[i + 12] > c[i], up240=c[i + 48] > c[i], first=first))
    i += 6
R = pd.DataFrame(rows)
t = R.groupby('cls').agg(n=('up60', 'size'), up60=('up60', 'mean'), up240=('up240', 'mean'),
                         up_first=('first', lambda s: (s == 'up').mean()), down_first=('first', lambda s: (s == 'down').mean()))
print(t.round(3).to_string())
