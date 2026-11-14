"""Download Binance spot 1m monthly kline archives (public data.binance.vision) -> npz per symbol (t_ms,o,h,l,c,v).
Same as the parent fetch_1m.py with more symbols and a thread pool. Usage: python -I fetch_1m.py <outdir>"""
import sys, io, zipfile, urllib.request, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import numpy as np
NEW = ["BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "LTCUSDT", "DOTUSDT", "TRXUSDT", "BCHUSDT"]
SEEN = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
START, END = (2020, 1), (2026, 10)
def months():
    y, m = START
    while (y, m) <= END:
        yield y, m
        m += 1
        if m == 13: y, m = y + 1, 1
def get(args):
    sym, y, m = args
    url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1m/{sym}-1m-{y}-{m:02d}.zip"
    for _ in range(3):
        try:
            raw = urllib.request.urlopen(url, timeout=90).read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404: return (y, m), None
        except Exception:
            pass
    else:
        return (y, m), "ERR"
    z = zipfile.ZipFile(io.BytesIO(raw))
    a = np.loadtxt(z.open(z.namelist()[0]), delimiter=",", usecols=(0, 1, 2, 3, 4, 5), dtype=np.float64).reshape(-1, 6)
    a[:, 0] = np.where(a[:, 0] > 1e14, a[:, 0] / 1000.0, a[:, 0])   # microsecond stamps from 2025
    return (y, m), a
def main(out):
    with ThreadPoolExecutor(8) as ex:
        for sym in SEEN + NEW:
            res = list(ex.map(get, [(sym, y, m) for y, m in months()]))
            missing = [f"{y}-{m:02d}" for (y, m), a in res if a is None]
            err = [f"{y}-{m:02d}" for (y, m), a in res if isinstance(a, str)]
            rows = [a for _, a in res if isinstance(a, np.ndarray) and a.size]
            if not rows:
                print(sym, "NO DATA", flush=True); continue
            A = np.concatenate(rows); A = A[np.argsort(A[:, 0])]
            _, idx = np.unique(A[:, 0], return_index=True); A = A[idx]
            np.savez_compressed(f"{out}/{sym}_1m.npz", a=A)
            print(sym, len(A), dt.datetime.utcfromtimestamp(A[0, 0] / 1000), dt.datetime.utcfromtimestamp(A[-1, 0] / 1000),
                  "missing", missing, "ERR", err, flush=True)
if __name__ == "__main__":
    main(sys.argv[1])
