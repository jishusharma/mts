"""Bybit v5 public linear 15m klines -> npz per coin (t_ms,o,h,l,c,v,turnover). Usage: python -I fetch_bybit.py <outdir>"""
import sys, json, time, urllib.request
import numpy as np
COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "LTCUSDT"]
HOST = "https://api.bybit.com/v5/market/kline"
def page(sym, end_ms):
    url = f"{HOST}?category=linear&symbol={sym}&interval=15&limit=1000&end={end_ms}"
    for k in range(5):
        try:
            d = json.loads(urllib.request.urlopen(url, timeout=30).read())
            if d["retCode"] == 0:
                return d["result"]["list"]
        except Exception:
            time.sleep(1 + k)
    return None
def main(out):
    now = int(time.time() * 1000)
    for sym in COINS:
        end, rows = now, []
        while True:
            r = page(sym, end)
            if r is None:
                print(sym, "ERR at", end, flush=True); break
            if not r:
                break
            rows += r
            oldest = int(r[-1][0])
            if len(r) < 1000:
                break
            end = oldest - 1
            time.sleep(0.12)
        A = np.array(rows, dtype=np.float64)[:, :7]
        A = A[np.argsort(A[:, 0])]
        _, idx = np.unique(A[:, 0], return_index=True); A = A[idx]
        np.savez_compressed(f"{out}/{sym}_15m.npz", a=A)
        print(sym, len(A), time.strftime("%Y-%m-%d", time.gmtime(A[0, 0] / 1000)), time.strftime("%Y-%m-%d %H:%M", time.gmtime(A[-1, 0] / 1000)), flush=True)
if __name__ == "__main__":
    main(sys.argv[1])
