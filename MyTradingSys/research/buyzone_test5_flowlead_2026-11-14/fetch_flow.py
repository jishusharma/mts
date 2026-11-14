"""Fetch public Binance BTCUSDT aggTrades daily dumps (data.binance.vision, no key) and reduce each day to large-trade flow.
Cache dir: $MTS_FLOW_CACHE or C:/Users/e-ngineers/mts_cache/buyzone_test5 (outside the repo, never committed).
Usage: python fetch_flow.py [start YYYY-MM-DD] [end YYYY-MM-DD]   (days whose file is missing are recorded in gaps.json)
Large trade = one aggTrade row with price*qty >= cutoff (OURS). Aggressor buy = is_buyer_maker False.
"""
import io
import json
import os
import sys
import time
import urllib.request
import zipfile
from multiprocessing import Pool

import pandas as pd

CACHE = os.environ.get("MTS_FLOW_CACHE", "C:/Users/e-ngineers/mts_cache/buyzone_test5")
CUTS = (1_000_000.0, 5_000_000.0)
BASE = "https://data.binance.vision/data/"
KINDS = {"spot": "spot/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-%s.zip",
         "fut": "futures/um/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-%s.zip"}


def reduce_frame(df):
    """df columns: price, qty, maker (bool, True = buyer is maker = aggressive SELL). Returns the per-day flow dict."""
    notional = df["price"].to_numpy() * df["qty"].to_numpy()
    buy = ~df["maker"].to_numpy()
    out = {"n": int(len(df)), "total": float(notional.sum()), "buy_total": float(notional[buy].sum())}
    for cut in CUTS:
        m = notional >= cut
        k = str(int(cut // 1_000_000))
        out["buy" + k] = float(notional[m & buy].sum())
        out["sell" + k] = float(notional[m & ~buy].sum())
        out["n" + k] = int(m.sum())
    return out


def parse_zip(raw):
    z = zipfile.ZipFile(io.BytesIO(raw))
    with z.open(z.namelist()[0]) as f:
        df = pd.read_csv(f, header=None, usecols=[1, 2, 6], names=None, dtype=str)
    df.columns = ["price", "qty", "maker"]
    df = df[pd.to_numeric(df["price"], errors="coerce").notna()].copy()    # drops a header row if present
    df["price"] = df["price"].astype(float)
    df["qty"] = df["qty"].astype(float)
    df["maker"] = df["maker"].str.lower().eq("true")
    return reduce_frame(df)


def one(args):
    kind, day = args
    path = os.path.join(CACHE, kind, day + ".json")
    if os.path.exists(path):
        return kind, day, "have"
    url = BASE + KINDS[kind] % day
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(url, timeout=120).read()
            res = parse_zip(raw)
            json.dump(res, open(path, "w"))
            return kind, day, "ok"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return kind, day, "404"
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return kind, day, "fail"


def main():
    start = sys.argv[1] if len(sys.argv) > 1 else "2022-01-01"
    end = sys.argv[2] if len(sys.argv) > 2 else pd.Timestamp.utcnow().strftime("%Y-%m-%d")
    days = [d.strftime("%Y-%m-%d") for d in pd.date_range(start, end)]
    for k in KINDS:
        os.makedirs(os.path.join(CACHE, k), exist_ok=True)
    jobs = [(k, d) for d in days for k in KINDS]
    gaps = []
    with Pool(6) as p:
        for i, (k, d, st) in enumerate(p.imap_unordered(one, jobs, chunksize=2)):
            if st in ("404", "fail"):
                gaps.append([k, d, st])
            if i % 100 == 0:
                print(i, len(jobs), flush=True)
    json.dump(sorted(gaps), open(os.path.join(CACHE, "gaps.json"), "w"))
    print("gaps", len(gaps), sorted(gaps)[-6:])


if __name__ == "__main__":
    main()
