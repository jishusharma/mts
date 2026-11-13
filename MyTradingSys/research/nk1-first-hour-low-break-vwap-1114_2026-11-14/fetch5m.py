"""Fetch Binance spot 5m klines (data-api.binance.vision) into the shared cache F:\MTS\data_cache\binance\<SYM>_5m.npz.
cols: t_ms,o,h,l,c,v. Resumes from existing file. tmp then os.replace."""
import json, os, sys, time, urllib.request
import numpy as np
from concurrent.futures import ThreadPoolExecutor
CACHE = os.environ.get("MTS_DATA_CACHE", r"F:\MTS\data_cache") + os.sep + "binance"
SYMS = "BTC ETH BNB XRP ADA LTC TRX LINK XLM DOGE ETC BCH SOL DOT AVAX ATOM UNI VET NEO ZEC".split()
START = 1546300800000  # 2019-01-01
STEP = 300000
def get(url):
    for i in range(6):
        try:
            return json.load(urllib.request.urlopen(url, timeout=30))
        except Exception:
            time.sleep(1 + i)
    raise RuntimeError(url)
def fetch(sym):
    path = os.path.join(CACHE, sym + "USDT_5m.npz")
    old = None
    start = START
    if os.path.exists(path):
        old = np.load(path)["a"]
        start = int(old[-1, 0]) + STEP
    rows = []
    while True:
        d = get("https://data-api.binance.vision/api/v3/klines?symbol=%sUSDT&interval=5m&limit=1000&startTime=%d" % (sym, start))
        if not d:
            if not rows and old is None and start < 1700000000000:  # listing later than start: jump a month
                start += 30 * 86400000
                if start > time.time() * 1000: break
                continue
            break
        rows += [[int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in d]
        start = int(d[-1][0]) + STEP
        if len(d) < 1000 or start > time.time() * 1000: break
    if old is not None and rows: a = np.vstack([old, np.array(rows)])
    elif old is not None: a = old
    else: a = np.array(rows)
    if len(a):
        a = a[np.argsort(a[:, 0])]
        tmp = path + ".tmp.npz"
        np.savez(tmp, a=a)
        os.replace(tmp, path)
    return sym, len(a)
if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    syms = sys.argv[1:] or SYMS
    with ThreadPoolExecutor(8) as ex:
        for s, n in ex.map(fetch, syms): print(s, n, flush=True)
