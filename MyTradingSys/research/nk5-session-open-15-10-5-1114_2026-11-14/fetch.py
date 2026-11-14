r"""Fetch Binance spot 5m klines via data-api.binance.vision into F:\MTS\data_cache\binance\<SYM>_5m.npz (tmp then replace)."""
import os, sys, time, json, urllib.request, numpy as np
from concurrent.futures import ThreadPoolExecutor
CACHE = r"F:\MTS\data_cache\binance"
SYMS = ["BTC","ETH","BNB","XRP","ADA","DOGE","LTC","LINK","TRX","EOS","XLM","ETC","DASH","ZEC","BCH","ATOM","NEO","IOTA","VET","ONT"]
def get(sym, start, tf="5m"):
    url = f"https://data-api.binance.vision/api/v3/klines?symbol={sym}USDT&interval={tf}&startTime={start}&limit=1000"
    for a in range(6):
        try:
            with urllib.request.urlopen(url, timeout=20) as r: return json.loads(r.read())
        except Exception as e:
            time.sleep(1+a)
    raise RuntimeError("fail " + url)
def fetch(sym, tf="5m"):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{sym}USDT_{tf}.npz")
    if os.path.exists(path): return sym, "cached"
    t = int(time.mktime((2019,1,1,0,0,0,0,0,0)) - time.timezone) * 1000
    rows = []
    end = int(time.time()*1000)
    while t < end:
        k = get(sym, t, tf)
        if not k: 
            if rows: break
            t += 30*86400000; 
            if t > end: break
            continue
        rows += [(x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])) for x in k]
        t = k[-1][0] + 1
        if len(k) < 1000: break
    a = np.array(rows, dtype=np.float64)
    a = a[np.argsort(a[:,0])]; _, i = np.unique(a[:,0], return_index=True); a = a[i]
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, a=a)
    os.replace(tmp, path)
    return sym, len(a)
if __name__ == "__main__":
    syms = sys.argv[1:] or SYMS
    with ThreadPoolExecutor(14) as ex:
        for r in ex.map(fetch, syms): print(r, flush=True)
