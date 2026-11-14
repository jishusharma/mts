"""Fetch Bybit v5 public linear USDT 5m klines + 1h open interest (no key), 2021-01-01 on, 20 perps, threaded by coin.
Cache (git-ignored): runtime_data/edge9-winrate-1114/<COIN>_5m.json rows [open_ms,o,h,l,c,v]; <COIN>_oi1h.json rows [ts_ms, oi].
python fetch_klines.py [ncoins]"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge9-winrate-1114"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX",
         "DOT", "ATOM", "TRX", "BCH", "ETC", "UNI", "NEAR", "FIL", "XLM", "AAVE"]
START_MS = 1609459200000  # 2021-01-01


def get(u):
    for k in range(8):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                d = json.load(r)
            if d.get("retCode") == 0 and "list" in d.get("result", {}):
                return d["result"]
            time.sleep(1 + 2 * k)
        except Exception:
            time.sleep(1 + k)
    raise RuntimeError(u)


def fetch_k(sym):
    end, rows = int(time.time() * 1000), {}
    while end > START_MS:
        lst = get("https://api.bybit.com/v5/market/kline?category=linear&symbol=%sUSDT&interval=5&limit=1000&end=%d" % (sym, end))["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r[0])] = [int(r[0])] + [float(x) for x in r[1:6]]
        old = min(int(r[0]) for r in lst)
        if old >= end:
            break
        end = old - 1
    return [rows[k] for k in sorted(rows) if k >= START_MS]


def fetch_oi(sym):
    end, rows = int(time.time() * 1000), {}
    while end > START_MS:
        res = get("https://api.bybit.com/v5/market/open-interest?category=linear&symbol=%sUSDT&intervalTime=1h&limit=200&endTime=%d" % (sym, end))
        lst = res["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r["timestamp"])] = float(r["openInterest"])
        old = min(int(r["timestamp"]) for r in lst)
        if old >= end:
            break
        end = old - 1
    return [[k, rows[k]] for k in sorted(rows)]


def one(sym):
    p = os.path.join(OUT, sym + "_5m.json")
    if not os.path.exists(p):
        json.dump(fetch_k(sym), open(p, "w"))
    p = os.path.join(OUT, sym + "_oi1h.json")
    if not os.path.exists(p):
        json.dump(fetch_oi(sym), open(p, "w"))
    print("done", sym, flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else len(COINS)
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(one, COINS[:n]))
