"""Fetch Bybit v5 public linear 1h and daily klines to runtime_data/edge-rsi-extreme-confirm-1113/ (ignored cache)."""
import json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge-rsi-extreme-confirm-1113"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX"]
START_MS = 1577836800000  # 2020-01-01 UTC
IV_MS = {"60": 3600000, "D": 86400000}


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


def fetch(sym, iv):
    end = int(time.time() * 1000)
    rows = {}
    while end > START_MS:
        d = get("https://api.bybit.com/v5/market/kline?category=linear&symbol=%sUSDT&interval=%s&limit=1000&end=%d" % (sym, iv, end))
        lst = d["result"]["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r[0])] = [int(r[0])] + [float(x) for x in r[1:6]]
        old = min(int(r[0]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.12)
    return [rows[k] for k in sorted(rows) if k >= START_MS]


def fetch_funding(sym):
    end = int(time.time() * 1000)
    rows = {}
    while end > START_MS:
        d = get("https://api.bybit.com/v5/market/funding/history?category=linear&symbol=%sUSDT&limit=200&endTime=%d" % (sym, end))
        lst = d["result"]["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r["fundingRateTimestamp"])] = float(r["fundingRate"])
        old = min(int(r["fundingRateTimestamp"]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.12)
    return [[k, rows[k]] for k in sorted(rows) if k >= START_MS]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for c in COINS:
        for iv in ("60", "D"):
            p = os.path.join(OUT, "%s_%s.json" % (c, iv))
            if os.path.exists(p):
                continue
            rows = fetch(c, iv)
            json.dump(rows, open(p, "w"))
            print(c, iv, len(rows), rows[0][0] if rows else None, flush=True)
        p = os.path.join(OUT, "%s_fund.json" % c)
        if not os.path.exists(p):
            f = fetch_funding(c)
            json.dump(f, open(p, "w"))
            print(c, "funding", len(f), flush=True)
