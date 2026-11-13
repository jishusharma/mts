"""Fetch Binance spot 15m klines (monthly zips from data.binance.vision + API tail) into F:\MTS\data_cache\binance_spot."""
import os, io, sys, zipfile, time, json, urllib.request
import numpy as np
from concurrent.futures import ThreadPoolExecutor
SYMS = "BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK DOT AVAX ATOM ETC XLM BCH UNI NEAR FIL ALGO".split()
OUT = r"F:\MTS\data_cache\binance_spot"
def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(1+i)
        except Exception: time.sleep(1+i)
    return None
def month_rows(sym, y, m):
    b = get(f"https://data.binance.vision/data/spot/monthly/klines/{sym}/15m/{sym}-15m-{y}-{m:02d}.zip")
    if b is None: return None
    z = zipfile.ZipFile(io.BytesIO(b)); rows = []
    for ln in z.read(z.namelist()[0]).decode().splitlines():
        p = ln.split(",")
        t = int(p[0]); t = t//1000 if t > 10**14 else t
        rows.append((t, float(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[5])))
    return rows
def do(base):
    sym = base + "USDT"; path = f"{OUT}\{sym}_15m.npz"
    if os.path.exists(path): return base, "cached"
    now = time.gmtime(); rows = []
    for y in range(2019, now.tm_year + 1):
        for m in range(1, 13):
            if (y, m) >= (now.tm_year, now.tm_mon): break
            r = month_rows(sym, y, m)
            if r: rows += r
    last = rows[-1][0] + 900000 if rows else int(time.mktime((now.tm_year, now.tm_mon, 1, 0, 0, 0, 0, 0, 0)) * 1000)
    while True:
        b = get(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=15m&limit=1000&startTime={last}")
        if not b: break
        k = json.loads(b)
        if not k: break
        rows += [(x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])) for x in k]
        last = k[-1][0] + 900000
        if len(k) < 1000: break
    if not rows: return base, "none"
    a = np.array(rows, dtype=np.float64); a = a[np.argsort(a[:, 0])]
    _, ix = np.unique(a[:, 0], return_index=True); a = a[ix]
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, ts=a[:, 0].astype(np.int64), o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4], v=a[:, 5])
    os.replace(tmp, path)
    return base, f"{len(a)} bars {time.strftime('%Y-%m-%d', time.gmtime(a[0,0]/1000))}..{time.strftime('%Y-%m-%d %H:%M', time.gmtime(a[-1,0]/1000))}"
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(do, SYMS): print(*r, flush=True)
