"""Download Binance spot 1m monthly kline archives (public data.binance.vision) -> npz per symbol (t_ms,o,h,l,c,v).
Usage: python -I fetch_1m.py <outdir>"""
import sys, io, zipfile, urllib.request, datetime as dt
import numpy as np
SYMS = {"BTCUSDT": (2020, 1), "ETHUSDT": (2020, 1), "SOLUSDT": (2020, 9)}
END = (2026, 10)
def months(s):
    y, m = s
    while (y, m) <= END:
        yield y, m
        m += 1
        if m == 13: y, m = y + 1, 1
def main(out):
    for sym, st in SYMS.items():
        rows = []; missing = []
        for y, m in months(st):
            url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1m/{sym}-1m-{y}-{m:02d}.zip"
            try:
                raw = urllib.request.urlopen(url, timeout=60).read()
            except Exception as e:
                missing.append(f"{y}-{m:02d}"); continue
            z = zipfile.ZipFile(io.BytesIO(raw))
            a = np.loadtxt(z.open(z.namelist()[0]), delimiter=",", usecols=(0, 1, 2, 3, 4, 5), dtype=np.float64)
            if a.size == 0: continue
            a = a.reshape(-1, 6)
            a[:, 0] = np.where(a[:, 0] > 1e14, a[:, 0] / 1000.0, a[:, 0])  # microsecond stamps from 2025
            rows.append(a)
        A = np.concatenate(rows); A = A[np.argsort(A[:, 0])]
        _, idx = np.unique(A[:, 0], return_index=True); A = A[idx]
        np.savez_compressed(f"{out}/{sym}_1m.npz", a=A)
        print(sym, len(A), dt.datetime.utcfromtimestamp(A[0, 0] / 1000), dt.datetime.utcfromtimestamp(A[-1, 0] / 1000), "missing", missing, flush=True)
if __name__ == "__main__":
    main(sys.argv[1])
