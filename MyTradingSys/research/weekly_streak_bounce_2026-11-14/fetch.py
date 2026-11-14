"""Fetch public daily candles. Usage: python fetch.py <outdir>. No keys."""
import sys, json, time, urllib.request, pathlib
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
def get(u):
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "research"}), timeout=30))
        except Exception as e:
            time.sleep(2)
    raise RuntimeError(u)
cg = get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=100&page=1&order=market_cap_desc")
skip = {"usdt","usdc","steth","wbtc","weth","wsteth","weeth","usds","dai","usde","busd","tusd","fdusd","wbeth","bsc-usd","usdt0","susde","cbbtc","usd1","bfusd","figr_heloc","syrupusdc","usdtb","pyusd","ethena-usde","jitosol","reth","solvbtc","paxg","xaut","leo","hype","wlfi"}
def kl(sym):
    rows, start = [], 1498867200000  # 2017-07-01
    while True:
        d = get(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}USDT&interval=1d&limit=1000&startTime={start}")
        if not d: break
        rows += d; start = d[-1][0] + 86400000
        if len(d) < 1000: break
    return [[r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4])] for r in rows]
chosen, meta = [], []
for c in cg:
    s = c["symbol"].upper()
    if c["symbol"] in skip or c["id"] in skip: continue
    try: rows = kl(s)
    except Exception: continue
    if not rows: continue
    first = rows[0][0]
    ok = first <= 1667260800000  # 2022-11-01
    meta.append((c["market_cap_rank"], s, time.strftime("%Y-%m-%d", time.gmtime(first/1000)), ok, len(rows)))
    if ok:
        (out / f"{s}.json").write_text(json.dumps(rows))
        chosen.append(s)
    core = [x for x in chosen if x not in ("BTC", "ETH")]
    if "BTC" in chosen and "ETH" in chosen and len(core) >= 20: break
json.dump(meta, open(out / "_meta.json", "w"))
print("chosen", chosen)
for m in meta: print(m)
# Coinbase BTC-USD from 2015
import datetime as dt
rows = []; t = dt.datetime(2015, 1, 1)
end = dt.datetime(2026, 11, 14)
while t < end:
    t2 = min(t + dt.timedelta(days=299), end)
    d = get(f"https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400&start={t.isoformat()}Z&end={t2.isoformat()}Z")
    rows += d; t = t2 + dt.timedelta(days=1); time.sleep(0.4)
rows = sorted({r[0]: r for r in rows}.values())
json.dump([[r[0]*1000, r[3], r[2], r[1], r[4]] for r in rows], open(out / "BTC_COINBASE.json", "w"))
print("coinbase", len(rows), rows[0][0], rows[-1][0])
