"""Reduce Binance USD-M BTCUSDT aggTrades (public data.binance.vision; zips kept on D:) to 1-minute bars with large-print fields.

Large print = one aggTrade row with notional (price x quantity) >= T USD, T in 250k / 500k / 1M / 5M (OURS, set by the operator's
order of 2026-11-13: ">= $1M and >= $5M"). Aggressor: is_buyer_maker == false -> BUY (taker bought), true -> SELL.
Output per month: <OUT>/bars1m/YYYY-MM.csv.gz (or YYYY-MM-DD for the current partial month): one row per UTC minute that had trades:
  t,o,h,l,c,vol,buy_vol,sell_vol,n, then per T: bu<T>,se<T> (USD sums), nb<T>,ns<T> (counts).
No raw trade rows are stored. Public market data only, no account.

Usage: python reduce_public.py [--months 2022-01:2026-10] [--days 2026-11-01:2026-11-13] [--procs 5]
"""
import argparse, hashlib, io, os, sys, time, urllib.request, zipfile
from concurrent.futures import ProcessPoolExecutor
from datetime import date, timedelta
import numpy as np, pandas as pd

ZDIR = "D:/MTS_data/binance_aggtrades/um/BTCUSDT"
ZDIR_D = "D:/MTS_data/binance_aggtrades/um_daily/BTCUSDT"
OUT = "F:/MTS/data_cache/large_trades/large-trade-evidence-1114/bars1m"
BASE = "https://data.binance.vision/data/futures/um"
THR = {"250k": 250_000.0, "500k": 500_000.0, "1M": 1_000_000.0, "5M": 5_000_000.0}


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    urllib.request.urlretrieve(url, tmp)
    h = hashlib.sha256()
    with open(tmp, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    want = urllib.request.urlopen(url + ".CHECKSUM").read().decode().split()[0]
    if h.hexdigest() != want:
        os.remove(tmp)
        raise RuntimeError("checksum mismatch " + url)
    os.replace(tmp, dest)


def reduce_zip(zpath):
    parts = []
    with zipfile.ZipFile(zpath) as z:
        name = z.namelist()[0]
        with z.open(name) as f:
            first = f.readline()
        hdr = 0 if first.startswith(b"agg_trade_id") else None
        with z.open(name) as f:
            rd = pd.read_csv(f, header=hdr, usecols=[1, 2, 5, 6], chunksize=3_000_000)
            for ch in rd:
                ch.columns = ["price", "qty", "time", "maker"]
                if ch["maker"].dtype == object:
                    ch["maker"] = ch["maker"].astype(str).str.lower().eq("true")
                ch["maker"] = ch["maker"].astype(bool)
                tm = ch["time"].to_numpy()
                assert tm.max() < 4e12, "timestamp not ms"
                m = tm // 60000 * 60000
                p = ch["price"].to_numpy(); q = ch["qty"].to_numpy(); buy = ~ch["maker"].to_numpy()
                nt = p * q
                d = {"t": m, "p": p, "q": q, "qb": q * buy, "qs": q * ~buy, "n": np.ones(len(p))}
                for k, T in THR.items():
                    big = nt >= T
                    d["bu" + k] = nt * (big & buy); d["se" + k] = nt * (big & ~buy)
                    d["nb" + k] = (big & buy).astype(float); d["ns" + k] = (big & ~buy).astype(float)
                df = pd.DataFrame(d)
                g = df.groupby("t", sort=True)
                agg = g.agg(**{"o": ("p", "first"), "h": ("p", "max"), "l": ("p", "min"), "c": ("p", "last"), "vol": ("q", "sum"),
                               "buy_vol": ("qb", "sum"), "sell_vol": ("qs", "sum"), "n": ("n", "sum"),
                               **{c: (c, "sum") for c in df.columns if c[:2] in ("bu", "se", "nb", "ns")}})
                parts.append(agg.reset_index())
    a = pd.concat(parts, ignore_index=True)
    g = a.groupby("t", sort=True)
    sums = [c for c in a.columns if c not in ("t", "o", "h", "l", "c")]
    res = g.agg(**{"o": ("o", "first"), "h": ("h", "max"), "l": ("l", "min"), "c": ("c", "last"), **{c: (c, "sum") for c in sums}}).reset_index()
    for c in res.columns:
        if c[:2] in ("nb", "ns") or c == "n":
            res[c] = res[c].astype("int64")
    return res


def job(arg):
    kind, key = arg
    t0 = time.time()
    if kind == "m":
        zp = f"{ZDIR}/BTCUSDT-aggTrades-{key}.zip"
        if not os.path.exists(zp):
            fetch(f"{BASE}/monthly/aggTrades/BTCUSDT/BTCUSDT-aggTrades-{key}.zip", zp)
    else:
        zp = f"{ZDIR_D}/BTCUSDT-aggTrades-{key}.zip"
        if not os.path.exists(zp):
            fetch(f"{BASE}/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-{key}.zip", zp)
    outp = f"{OUT}/{key}.csv.gz"
    if os.path.exists(outp):
        return key, "exists", 0, 0
    r = reduce_zip(zp)
    r.to_csv(outp + ".tmp", index=False, compression="gzip")
    os.replace(outp + ".tmp", outp)
    return key, "ok", len(r), round(time.time() - t0)


def month_range(a, b):
    y, m = map(int, a.split("-")); y2, m2 = map(int, b.split("-"))
    while (y, m) <= (y2, m2):
        yield f"{y:04d}-{m:02d}"
        m += 1
        if m == 13:
            y += 1; m = 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", default="2022-01:2026-10")
    ap.add_argument("--days", default="2026-11-01:2026-11-13")
    ap.add_argument("--procs", type=int, default=5)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    jobs = [("m", k) for k in month_range(*a.months.split(":"))]
    if a.days:
        d0, d1 = (date.fromisoformat(x) for x in a.days.split(":"))
        while d0 <= d1:
            jobs.append(("d", d0.isoformat())); d0 += timedelta(days=1)
    with ProcessPoolExecutor(a.procs) as ex:
        for r in ex.map(job, jobs):
            print(*r, flush=True)
