"""Fetch Binance spot 15m klines (data-api.binance.vision) into F:\MTS\data_cache\binance\<SYM>_15m.npz (reuse if present).
cols: open_time_ms,o,h,l,c,v. Run: python fetch_15m.py [SYM...]"""
import os, sys, json, time, urllib.request
import numpy as np
from concurrent.futures import ThreadPoolExecutor
CACHE = r"F:\MTS\data_cache\binance"
SYMS = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
START = 1546300800000  # 2019-01-01
END = int(time.time() * 1000) // 900000 * 900000
def get(url):
    for i in range(6):
        try:
            return json.load(urllib.request.urlopen(url, timeout=30))
        except Exception:
            time.sleep(1 + i)
    raise RuntimeError(url)
def fetch(sym):
    path = os.path.join(CACHE, sym + "USDT_15m.npz")
    if os.path.exists(path):
        return sym, "cached"
    rows, t = [], START
    while t < END:
        d = get("https://data-api.binance.vision/api/v3/klines?symbol=%sUSDT&interval=15m&limit=1000&startTime=%d" % (sym, t))
        if not d:
            if not rows:
                t += 90 * 86400000  # pre-listing gap
                continue
            break
        rows += [[int(r[0])] + [float(x) for x in r[1:6]] for r in d]
        t = int(d[-1][0]) + 900000
        if len(d) < 1000 and t >= END - 900000 * 2:
            break
    a = np.array(rows)
    if len(a) == 0:
        return sym, "empty"
    _, i = np.unique(a[:, 0], return_index=True)
    a = a[i]
    os.makedirs(CACHE, exist_ok=True)
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, a=a)
    os.replace(tmp, path)
    return sym, "%d rows %s" % (len(a), time.strftime("%Y-%m-%d", time.gmtime(a[0, 0] / 1000)))
if __name__ == "__main__":
    syms = sys.argv[1:] or SYMS
    with ThreadPoolExecutor(5) as ex:
        for r in ex.map(fetch, syms):
            print(*r, flush=True)
