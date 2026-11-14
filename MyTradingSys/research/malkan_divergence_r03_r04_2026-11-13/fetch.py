"""Fetch/top-up Bybit v5 public linear 1h klines for 20 USDT perps into runtime_data/edge4-malkan-divergence-1113/ (ignored cache)."""
import json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge4-malkan-divergence-1113"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX", "DOT", "TRX", "ATOM", "NEAR", "UNI", "ETC", "BCH", "FIL", "AAVE", "XLM"]
START_MS = 1577836800000  # 2020-01-01 UTC
BASE = "https://api.bybit.com/v5/market/"


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


def fetch_klines(sym, iv, since):
    end = int(time.time() * 1000)
    rows = {}
    while end > since:
        lst = get(BASE + "kline?category=linear&symbol=%sUSDT&interval=%s&limit=1000&end=%d" % (sym, iv, end))["result"]["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r[0])] = [int(r[0])] + [float(x) for x in r[1:6]]
        old = min(int(r[0]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.1)
    return rows


def topup(sym, iv):
    p = os.path.join(OUT, "%s_%s.json" % (sym, iv))
    old = {r[0]: r for r in json.load(open(p))} if os.path.exists(p) else {}
    since = max(old) - 3 * 86400000 if old else START_MS
    old.update(fetch_klines(sym, iv, since))
    rows = [old[k] for k in sorted(old) if k >= START_MS]
    json.dump(rows, open(p, "w"))
    return len(rows)


def fetch_oi(sym):
    p = os.path.join(OUT, "%s_oi.json" % sym)
    if os.path.exists(p):
        return -1
    end = int(time.time() * 1000)
    rows = {}
    while end > START_MS:
        lst = get(BASE + "open-interest?category=linear&symbol=%sUSDT&intervalTime=1h&limit=200&endTime=%d" % (sym, end))["result"]["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r["timestamp"])] = float(r["openInterest"])
        old = min(int(r["timestamp"]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.12)
    json.dump([[k, rows[k]] for k in sorted(rows)], open(p, "w"))
    return len(rows)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "klines"
    for c in COINS:
        if mode == "klines":
            for iv in ("60",):
                print(c, iv, topup(c, iv), flush=True)
        else:
            print(c, "oi", fetch_oi(c), flush=True)
