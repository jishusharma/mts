"""Fetch futures funding / OI metrics and spot 1h taker klines from data.binance.vision (public market data).
Parsed per-coin npz go to F:/MTS/data_cache/<venue>/<slug>/ with .meta.json sidecars (key ts in ms). No raw zips kept."""
import datetime as dt, hashlib, io, json, sys, time, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np

SLUG = "nkp3-hilega-milega-phase-1114"
ROOT = Path(r"F:/MTS/data_cache")
BASE = "https://data.binance.vision/data/"
COINS = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "LTC", "LINK", "TRX", "DOT", "AVAX", "ATOM", "ETC", "BCH", "XLM", "UNI", "NEAR", "FIL", "EOS"]
END = dt.date(2026, 11, 13)


def get(path):
    for k in range(4):
        try:
            with urllib.request.urlopen(BASE + path, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except Exception:
            time.sleep(1 + k)
    return None


def head(path):
    try:
        req = urllib.request.Request(BASE + path, method="HEAD")
        with urllib.request.urlopen(req, timeout=20):
            return True
    except Exception:
        return False


def rows(zbytes):
    z = zipfile.ZipFile(io.BytesIO(zbytes))
    out = []
    for ln in z.read(z.namelist()[0]).decode().splitlines():
        p = ln.split(",")
        if not p or not p[0] or not (p[0][0].isdigit()):
            continue
        out.append(p)
    return out


def months(a, b):
    y, m = a
    while (y, m) <= b:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def save(venue, name, arr, src, key="ts"):
    d = ROOT / venue / SLUG
    d.mkdir(parents=True, exist_ok=True)
    f = d / name
    np.savez_compressed(f, a=arr)
    raw = f.read_bytes()
    meta = dict(source=src, fetch_utc=dt.datetime.now(dt.timezone.utc).isoformat(), rows=int(len(arr)),
                first_ts=int(arr[0, 0]) if len(arr) else None, last_ts=int(arr[-1, 0]) if len(arr) else None,
                sha256=hashlib.sha256(raw).hexdigest(), key=key, cols=None)
    (d / (name + ".meta.json")).write_text(json.dumps(meta))
    return meta


def spot(c):
    sym = c + "USDT"
    jobs = [f"spot/monthly/klines/{sym}/1h/{sym}-1h-{y}-{m:02d}.zip" for y, m in months((2019, 1), (2026, 10))]
    jobs += [f"spot/daily/klines/{sym}/1h/{sym}-1h-2026-11-{d:02d}.zip" for d in range(1, END.day + 1)]
    allr = []
    for j in jobs:
        z = get(j)
        if z is None:
            continue
        for p in rows(z):
            t = int(p[0])
            if t > 10**14:
                t //= 1000
            allr.append((t, float(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[5]), float(p[9])))
    a = np.array(sorted(set(allr)), dtype=float)
    return c, save("binance_spot", f"{sym}_1h_taker.npz", a, "data.binance.vision spot klines 1h; cols ts,o,h,l,c,vol,takerbuybase")


def funding(c):
    sym = c + "USDT"
    allr = []
    for y, m in months((2019, 9), (2026, 10)):
        z = get(f"futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{y}-{m:02d}.zip")
        if z is None:
            continue
        for p in rows(z):
            allr.append((int(p[0]), float(p[2])))
    a = np.array(sorted(set(allr)), dtype=float).reshape(-1, 2)
    return c, save("binance", f"{sym}_funding.npz", a, "data.binance.vision futures/um monthly fundingRate; cols ts,rate")


def oi_day(args):
    sym, d = args
    z = get(f"futures/um/daily/metrics/{sym}/{sym}-metrics-{d.isoformat()}.zip")
    out = []
    if z is None:
        return out
    for p in rows(z):
        ts = int(dt.datetime.strptime(p[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
        if ts % 3600000 == 0:
            out.append((ts, float(p[3])))
    return out


def oi(c):
    sym = c + "USDT"
    start = None
    for y, m in months((2019, 9), (2026, 10)):
        if head(f"futures/um/daily/metrics/{sym}/{sym}-metrics-{y}-{m:02d}-15.zip") or head(f"futures/um/daily/metrics/{sym}/{sym}-metrics-{y}-{m:02d}-28.zip"):
            start = dt.date(y, m, 1)
            break
    if start is None:
        return c, None
    days = [start + dt.timedelta(i) for i in range((END - start).days + 1)]
    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(oi_day, [(sym, d) for d in days]))
    allr = sorted(set(r for x in res for r in x))
    a = np.array(allr, dtype=float).reshape(-1, 2)
    return c, save("binance", f"{sym}_oi_1h.npz", a, "data.binance.vision futures/um daily metrics sum_open_interest_value hourly rows; cols ts,oi_usd")


if __name__ == "__main__":
    what = sys.argv[1]
    fn = dict(spot=spot, funding=funding, oi=oi)[what]
    par = 4 if what == "oi" else 10
    with ThreadPoolExecutor(par) as ex:
        for c, m in ex.map(fn, COINS):
            print(what, c, None if m is None else (m["rows"], dt.datetime.fromtimestamp(m["first_ts"] / 1000, dt.timezone.utc).date().isoformat()), flush=True)
