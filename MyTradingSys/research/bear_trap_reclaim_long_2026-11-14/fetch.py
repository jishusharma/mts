"""Fetch Bybit v5 public linear USDT 1h klines and 1h open interest (no key) for the 20 coins fixed in PRE_REG.md.
Cache (git-ignored): runtime_data/edge9-bear-trap-1114/<COIN>_1h.json rows [open_ms,o,h,l,c,v]; <COIN>_oi.json rows [ts_ms, oi].
python fetch.py [--coins N]"""
import json, os, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge9-bear-trap-1114"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX",
         "DOT", "ATOM", "TRX", "BCH", "ETC", "UNI", "NEAR", "FIL", "XLM", "AAVE"]
START_MS = 1577836800000  # 2020-01-01


def get(u):
    for k in range(8):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                d = json.load(r)
            if d.get("retCode") == 0 and "list" in d.get("result", {}):
                return d
            time.sleep(2 + 3 * k)
        except Exception:
            time.sleep(1 + k)
    raise RuntimeError(u)


def fetch_k(sym):
    end, rows = int(time.time() * 1000), {}
    while end > START_MS:
        lst = get("https://api.bybit.com/v5/market/kline?category=linear&symbol=%sUSDT&interval=60&limit=1000&end=%d" % (sym, end))["result"]["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r[0])] = [int(r[0])] + [float(x) for x in r[1:6]]
        old = min(int(r[0]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.1)
    return [rows[k] for k in sorted(rows) if k >= START_MS]


def fetch_oi(sym):
    end, rows = int(time.time() * 1000), {}
    while end > START_MS:
        lst = get("https://api.bybit.com/v5/market/open-interest?category=linear&symbol=%sUSDT&intervalTime=1h&limit=200&endTime=%d" % (sym, end))["result"]["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r["timestamp"])] = float(r["openInterest"])
        old = min(int(r["timestamp"]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.1)
    return [[k, rows[k]] for k in sorted(rows)]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = int(sys.argv[sys.argv.index("--coins") + 1]) if "--coins" in sys.argv else len(COINS)
    for c in COINS[:n]:
        for name, fn in (("1h", fetch_k), ("oi", fetch_oi)):
            p = os.path.join(OUT, "%s_%s.json" % (c, name))
            if os.path.exists(p):
                continue
            rows = fn(c)
            json.dump(rows, open(p, "w"))
            print(c, name, len(rows), rows[0][0] if rows else None, flush=True)
