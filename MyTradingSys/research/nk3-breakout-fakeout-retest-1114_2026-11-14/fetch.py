"""Fetch Binance spot 15m klines (data-api.binance.vision) into shared cache F:/MTS/data_cache/binance_spot/<SYM>_15m.npz.
Reuses existing files. tmp then os.replace. Columns t(ms),o,h,l,c,v."""
import sys, os, json, time, urllib.request
import numpy as np
from concurrent.futures import ThreadPoolExecutor
CACHE = r"F:\MTS\data_cache\binance_spot"
START = 1546300800000  # 2019-01-01
STEP = 15 * 60 * 1000
COINS = "BTC ETH BNB XRP ADA SOL DOGE LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()

def get(sym, start):
    url = f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=15m&limit=1000&startTime={start}"
    for k in range(8):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=30).read())
        except Exception:
            time.sleep(1 + k)
    raise RuntimeError("fetch failed " + sym)

def run(coin, refresh=False):
    sym = coin + "USDT"
    path = os.path.join(CACHE, f"{sym}_15m.npz")
    if os.path.exists(path) and not refresh:
        return sym, "cached"
    rows, cur = [], START
    now = int(time.time() * 1000)
    while cur < now:
        lst = get(sym, cur)
        if not lst:
            if not rows:  # symbol not listed yet at START: jump a quarter
                cur += 90 * 86400000
                continue
            break
        rows += [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in lst]
        cur = lst[-1][0] + STEP
        if len(lst) < 1000:
            break
    a = np.array(rows, dtype=float)
    a = a[np.unique(a[:, 0], return_index=True)[1]]
    a = a[a[:, 0] + STEP <= now]  # closed bars only
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, t=a[:, 0].astype(np.int64), o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4], v=a[:, 5])
    os.replace(tmp, path)
    return sym, f"{len(a)} bars {time.strftime('%Y-%m-%d', time.gmtime(a[0,0]/1000))}..{time.strftime('%Y-%m-%d', time.gmtime(a[-1,0]/1000))}"

if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        for s, m in ex.map(run, COINS):
            print(s, m, flush=True)
