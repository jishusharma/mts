"""Fetch Bybit v5 public linear klines (15m and daily) for 20 USDT perps into runtime_data/edge8-mined-rules-1114/ (git-ignored cache).
Usage: python fetch.py [15|D] [coins...]   (6 coins in parallel threads)"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "runtime_data", "edge8-mined-rules-1114"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX", "DOT", "TRX", "ATOM", "NEAR", "UNI", "ETC", "BCH", "FIL", "AAVE", "XLM"]
START_MS = 1577836800000  # 2020-01-01 UTC
BASE = "https://api.bybit.com/v5/market/"


def get(u):
    for k in range(10):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                d = json.load(r)
            if d.get("retCode") == 0 and "list" in d.get("result", {}):
                return d
            time.sleep(2 + 3 * k)
        except Exception:
            time.sleep(1 + k)
    raise RuntimeError(u)


def fetch(sym, iv):
    p = os.path.join(OUT, "%s_%s.json" % (sym, iv))
    if os.path.exists(p):
        return sym, iv, -1
    end = int(time.time() * 1000)
    rows = {}
    while end > START_MS:
        lst = get(BASE + "kline?category=linear&symbol=%sUSDT&interval=%s&limit=1000&end=%d" % (sym, iv, end))["result"]["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r[0])] = [int(r[0])] + [float(x) for x in r[1:6]]
        old = min(int(r[0]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.05)
    out = [rows[k] for k in sorted(rows) if k >= START_MS]
    json.dump(out, open(p, "w"))
    return sym, iv, len(out)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    iv = sys.argv[1] if len(sys.argv) > 1 else "15"
    coins = sys.argv[2:] or COINS
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(lambda c: fetch(c, iv), coins):
            print(*r, flush=True)
