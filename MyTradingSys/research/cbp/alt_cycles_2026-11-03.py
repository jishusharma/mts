"""Past-cycle behaviour of majors: drawdown at each cycle low, gain from that low to the next peak, time to peak. CoinGecko days=max daily."""
import json, time, urllib.request, datetime as dt
IDS = {s: s for s in 'BTC ETH XRP ADA LINK HBAR DOT SOL AVAX UNI AAVE NEAR LTC XLM DOGE FIL ATOM VET'.split()}
WIN = [('2018-19 bear', '2018-01-01', '2019-02-28', '2021-12-31'), ('2022 bear', '2021-11-01', '2022-12-31', '2025-01-31'), ('2025-26 bear', '2025-01-01', '2026-07-31', '2026-11-03')]
def get(cid):
    out = []; st = 1483228800000
    while True:
        u = 'https://data-api.binance.vision/api/v3/klines?symbol=%sUSDT&interval=1d&limit=1000&startTime=%d' % (cid, st)
        try: rows = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30))
        except Exception as e: print('err', cid, e); return None
        if not rows: break
        out += [[r[0], float(r[4])] for r in rows]
        if len(rows) < 1000: break
        st = rows[-1][0] + 86400000
    return {'prices': out} if out else None
def d(ts): return dt.datetime.fromtimestamp(ts / 1000, dt.timezone.utc).date()
out = {}
for s, cid in IDS.items():
    j = get(cid)
    if not j: print('FAIL', s); continue
    px = [(d(t), p) for t, p in j['prices']]
    out[s] = {}
    for name, a, b, c in WIN:
        a, b, c = map(dt.date.fromisoformat, (a, b, c))
        pre = [p for t, p in px if t < b and t >= a - dt.timedelta(days=365)]
        bear = [(t, p) for t, p in px if a <= t <= b]
        if not bear or not pre: continue
        hi = max(pre); lo_t, lo = min(bear, key=lambda x: x[1])
        after = [(t, p) for t, p in px if lo_t < t <= c]
        if not after: continue
        pk_t, pk = max(after, key=lambda x: x[1])
        out[s][name] = (round(lo / hi - 1, 3), round(pk / lo - 1, 2), (pk_t - lo_t).days, str(lo_t))
    time.sleep(1)
json.dump(out, open('alt_cycles.json', 'w'), indent=0)
for name, *_ in WIN:
    print('\n' + name + ': drawdown at low (vs prior-year high) | gain low->next peak | days to peak | low date')
    for s in IDS:
        r = out.get(s, {}).get(name)
        if r: print('%-5s %6.0f%%  %+8.0f%%  %5dd  %s' % (s, r[0] * 100, r[1] * 100, r[2], r[3]))
