"""Fetch PUBLIC Binance spot 1m klines WITH volume (data.binance.vision, no keys) for the NKN-03 universe.
Output: F:/MTS/data_cache/nkn_1114/nkn03-intraday-sequence/<COIN>USDT_1m.npz (keys t_ms,o,h,l,c,v) + .meta.json. Never writes into other cache folders.
The existing binance_1m cache has no volume column, which the session VWAP needs.
Spot klines switched to microsecond timestamps in 2025: values above 1e14 are divided by 1000."""
import io
import json
import hashlib
import sys
import zipfile
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(r"F:\MTS\data_cache\nkn_1114\nkn03-intraday-sequence")
COINS = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM".split()
BASE = "https://data.binance.vision/data/spot"
LAST_DAY = "2026-11-13"


def get(url):
    for _ in range(4):
        try:
            return urllib.request.urlopen(url, timeout=90).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except Exception:
            pass
    return None


def parse(b):
    z = zipfile.ZipFile(io.BytesIO(b))
    raw = z.open(z.namelist()[0]).read().decode()
    if raw[:1].isalpha():
        raw = raw.split("\n", 1)[1]
    df = pd.read_csv(io.StringIO(raw), header=None, usecols=[0, 1, 2, 3, 4, 5])
    a = df.to_numpy(dtype=np.float64)
    t = a[:, 0].copy()
    t[t > 1e14] = t[t > 1e14] // 1000
    a[:, 0] = t
    return a


def months():
    out = []
    for y in range(2019, 2027):
        for m in range(1, 13):
            if (y, m) <= (2026, 10):
                out.append(f"{y}-{m:02d}")
    return out


def fetch_month(job):
    sym, ym = job
    b = get(f"{BASE}/monthly/klines/{sym}/1m/{sym}-1m-{ym}.zip")
    if b is not None:
        return parse(b)
    return None


def fetch_day(job):
    sym, ds = job
    b = get(f"{BASE}/daily/klines/{sym}/1m/{sym}-1m-{ds}.zip")
    return parse(b) if b is not None else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    coins = sys.argv[1:] or COINS
    for c in coins:
        sym = c + "USDT"
        dst = OUT / f"{sym}_1m.npz"
        if dst.exists():
            print(sym, "exists, skip")
            continue
        with ThreadPoolExecutor(8) as ex:
            parts = list(ex.map(fetch_month, [(sym, ym) for ym in months()]))
            days = [f"2026-11-{d:02d}" for d in range(1, 14)]
            dparts = list(ex.map(fetch_day, [(sym, d) for d in days]))
        parts = [p for p in parts + dparts if p is not None]
        a = np.concatenate(parts)
        a = a[np.argsort(a[:, 0], kind="stable")]
        keep = np.r_[True, np.diff(a[:, 0]) > 0]
        a = a[keep]
        a = a[a[:, 0] < np.datetime64(LAST_DAY).astype("datetime64[ms]").astype(np.int64) + 86400000]
        np.savez(dst, t_ms=a[:, 0].astype(np.int64), o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4], v=a[:, 5])
        meta = dict(source=BASE + "/monthly|daily/klines/" + sym + "/1m", rows=int(len(a)), first_ts=int(a[0, 0]), last_ts=int(a[-1, 0]),
                    sha256=hashlib.sha256(a.tobytes()).hexdigest(), key="t_ms", note="spot 1m with volume; us timestamps normalised to ms")
        (OUT / f"{sym}_1m.npz.meta.json").write_text(json.dumps(meta))
        print(sym, len(a), pd.to_datetime(a[0, 0], unit="ms"), pd.to_datetime(a[-1, 0], unit="ms"), flush=True)


if __name__ == "__main__":
    main()
