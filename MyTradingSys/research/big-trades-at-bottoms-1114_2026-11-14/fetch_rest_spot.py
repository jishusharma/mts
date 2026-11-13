"""Binance spot aggTrades via REST for days whose daily dump is not published yet (2026-11-13, 2026-11-14 partial).
Parallel over 30 s slices. Output same hourly format as fetch_hourly.py."""
import json, sys, time, urllib.request, datetime as dt
import numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
OUT = 'F:/MTS/data_cache/bigtrades/spot'
BASE = 'https://data-api.binance.vision/api/v3/aggTrades?symbol=BTCUSDT&limit=1000&'


def get(u):
    for a in range(8):
        try:
            return json.load(urllib.request.urlopen(u, timeout=30))
        except Exception as e:
            err = e; time.sleep(1 + a)
    raise err


def slice_trades(t0, t1):
    rows = []; r = get(BASE + f'startTime={t0}&endTime={t1 - 1}')
    while r:
        rows += [(x['T'], float(x['p']), float(x['q']), x['m']) for x in r]
        if len(r) < 1000: break
        nxt = r[-1]['a'] + 1
        r = get(BASE + f'fromId={nxt}')
        r = [x for x in r if x['T'] < t1]
        if not r: break
    return rows


def agg(rows):
    a = np.array([(t, p, q, m) for t, p, q, m in rows], dtype=float)
    hr = (a[:, 0] // 3600000).astype('int64'); price = a[:, 1]; qty = a[:, 2]; sell = a[:, 3] == 1
    usd = price * qty
    g = pd.DataFrame({'hr': hr, 'usd': usd, 'qty': qty, 'sell': sell}); r = []
    for col, thr, nm in (('usd', 0, 'all'), ('usd', 1e6, '1m'), ('usd', 5e6, '5m'), ('qty', 10, 'b10'), ('qty', 50, 'b50')):
        x = g[g[col] >= thr]
        p = x.pivot_table(index='hr', columns='sell', values='usd', aggfunc=['sum', 'count'], fill_value=0)
        p.columns = [f'{a_}_{"sell" if b else "buy"}_{nm}' for a_, b in p.columns]
        r.append(p)
    cols = [f'{a_}_{b}_{n}' for a_ in ('sum', 'count') for b in ('buy', 'sell') for n in ('all', '1m', '5m', 'b10', 'b50')]
    o = pd.concat(r, axis=1).reindex(columns=cols, fill_value=0.0).fillna(0.0)
    o.index = pd.to_datetime(o.index * 3600, unit='s'); o.index.name = 'hour_utc'
    return o


if __name__ == '__main__':
    day = sys.argv[1]; end_ms = int(sys.argv[2]) if len(sys.argv) > 2 else None
    d0 = int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    d1 = d0 + 86400000 if end_ms is None else end_ms
    sl = list(range(d0, d1, 30000))
    with ThreadPoolExecutor(10) as ex:
        res = list(ex.map(lambda s: slice_trades(s, min(s + 30000, d1)), sl))
    rows = [x for r in res for x in r]
    print(day, len(rows), 'trades', flush=True)
    o = agg(rows); o.to_csv(f'{OUT}/{day}.csv' if end_ms is None else f'{OUT}/{day}_partial.csv'); print(o.tail(2).T.head(3))
