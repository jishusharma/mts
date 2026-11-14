"""Fetch Binance spot klines (public bulk data, data.binance.vision) into the OWN cache folder
F:\MTS\data_cache\binance\nk-sourced-hm-supertrap-1114\<SYM>USDT_5m.npz (a: ts_ms,o,h,l,c,v) and BTCUSDT_1d.npz (from 2017-08).
Modest load: 4 threads. tmp then os.replace; reuses existing files."""
import io, os, sys, time, zipfile, datetime as dt, urllib.request, urllib.error
import numpy as np
from concurrent.futures import ThreadPoolExecutor

CACHE = r"F:\MTS\data_cache\binance\nk-sourced-hm-supertrap-1114"
COINS = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "LTC", "LINK", "TRX", "DOT", "AVAX", "ATOM", "ETC", "BCH", "XLM", "UNI", "NEAR", "FIL", "EOS"]
BASE = "https://data.binance.vision/data/spot/%s/klines/%sUSDT/%s/%sUSDT-%s-%s.zip"


def get(u):
    for k in range(4):
        try:
            with urllib.request.urlopen(u, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1 + k)
        except Exception:
            time.sleep(1 + k)
    return None


def parse(b):
    z = zipfile.ZipFile(io.BytesIO(b))
    a = np.atleast_2d(np.loadtxt(z.open(z.namelist()[0]), delimiter=",", usecols=(0, 1, 2, 3, 4, 5)))
    if a.size and a[0, 0] > 1e14:
        a[:, 0] //= 1000
    return a


def one(args):
    kind, sym, itv, tag = args
    b = get(BASE % (kind, sym, itv, sym, itv, tag))
    return parse(b) if b else None


def fetch(sym, itv, y0, m0):
    path = os.path.join(CACHE, "%sUSDT_%s.npz" % (sym, itv))
    if os.path.exists(path):
        return sym, itv, "cached"
    today = dt.date.today()
    jobs = []
    y, m = y0, m0
    while (y, m) < (today.year, today.month):
        jobs.append(("monthly", sym, itv, "%d-%02d" % (y, m)))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    d = dt.date(today.year, today.month, 1)
    while d < today:
        jobs.append(("daily", sym, itv, d.isoformat()))
        d += dt.timedelta(days=1)
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one, jobs))
    parts = [r for r in res if r is not None and r.size]
    if not parts:
        return sym, itv, "none"
    a = np.vstack(parts)
    a = a[np.argsort(a[:, 0])]
    _, i = np.unique(a[:, 0], return_index=True)
    a = a[i]
    os.makedirs(CACHE, exist_ok=True)
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, a=a)
    os.replace(tmp, path)
    return sym, itv, "%d rows %s .. %s" % (len(a), dt.datetime.utcfromtimestamp(a[0, 0] / 1000), dt.datetime.utcfromtimestamp(a[-1, 0] / 1000))


if __name__ == "__main__":
    print(*fetch("BTC", "1d", 2017, 8), flush=True)
    for c in COINS:
        print(*fetch(c, "5m", 2019, 1), flush=True)
