"""Fetch Binance spot 5m klines from data.binance.vision bulk zips into the shared cache
F:\MTS\data_cache\binance\<SYMBOL>_5m.npz (cols: ts_ms,o,h,l,c,v). Reuses existing files. tmp then os.replace."""
import io, os, sys, zipfile, datetime as dt, urllib.request, time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
CACHE = r"F:\MTS\data_cache\binance"
COINS = ["BTC","ETH","BNB","XRP","ADA","DOGE","SOL","LTC","LINK","TRX","DOT","AVAX","ATOM","ETC","BCH","XLM","UNI","NEAR","FIL","EOS"]
BASE = "https://data.binance.vision/data/spot/%s/klines/%sUSDT/5m/%sUSDT-5m-%s.zip"

def get(u):
    for k in range(4):
        try:
            with urllib.request.urlopen(u, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(1+k)
        except Exception:
            time.sleep(1+k)
    return None

def parse(b):
    z = zipfile.ZipFile(io.BytesIO(b)); a = np.loadtxt(z.open(z.namelist()[0]), delimiter=",", usecols=(0,1,2,3,4,5))
    a = np.atleast_2d(a)
    if a.size and a[0,0] > 1e14: a[:,0] //= 1000
    return a

def one(args):
    kind, sym, tag = args
    b = get(BASE % (kind, sym, sym, tag))
    return parse(b) if b else None

def fetch(sym):
    path = os.path.join(CACHE, sym + "USDT_5m.npz")
    if os.path.exists(path): return sym, "cached"
    today = dt.date.today(); jobs = []
    y, m = 2019, 1
    while (y, m) < (today.year, today.month):
        jobs.append(("monthly", sym, "%d-%02d" % (y, m))); m += 1
        if m == 13: y, m = y+1, 1
    d = dt.date(today.year, today.month, 1)
    while d < today:
        jobs.append(("daily", sym, d.isoformat())); d += dt.timedelta(days=1)
    with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, jobs))
    parts = [r for r in res if r is not None and r.size]
    if not parts: return sym, "none"
    a = np.vstack(parts); a = a[np.argsort(a[:,0])]; _, i = np.unique(a[:,0], return_index=True); a = a[i]
    os.makedirs(CACHE, exist_ok=True); tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, a=a); os.replace(tmp, path)
    return sym, "%d rows %s" % (len(a), dt.datetime.utcfromtimestamp(a[0,0]/1000))

if __name__ == "__main__":
    for c in COINS: print(*fetch(c), flush=True)
