"""Top-up/fetch Bybit v5 public linear 1h+1D klines, funding history and 1h open interest for 20 coins into runtime_data/edge4-rsi-confirm-layers-1113/ (ignored cache)."""
import json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge4-rsi-confirm-layers-1113"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX",
         "DOT", "ATOM", "NEAR", "UNI", "TRX", "BCH", "ETC", "FIL", "APT", "ARB"]
START_MS = 1577836800000
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


def pages(url_fn, ts_key, cap):
    end = int(time.time() * 1000)
    rows = {}
    while end > START_MS:
        lst = get(url_fn(end))["result"]["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r[ts_key] if not isinstance(r, list) else r[0])] = r
        old = min(int(r[ts_key] if not isinstance(r, list) else r[0]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.1)
    return rows


def run(sym):
    for iv in ("60", "D"):
        p = os.path.join(OUT, "%s_%s.json" % (sym, iv))
        if os.path.exists(p):
            continue
        rows = pages(lambda e: BASE + "kline?category=linear&symbol=%sUSDT&interval=%s&limit=1000&end=%d" % (sym, iv, e), 0, 1000)
        json.dump([[k] + [float(x) for x in rows[k][1:6]] for k in sorted(rows) if k >= START_MS], open(p, "w"))
    p = os.path.join(OUT, "%s_fund.json" % sym)
    if not os.path.exists(p):
        rows = pages(lambda e: BASE + "funding/history?category=linear&symbol=%sUSDT&limit=200&endTime=%d" % (sym, e), "fundingRateTimestamp", 200)
        json.dump([[k, float(rows[k]["fundingRate"])] for k in sorted(rows) if k >= START_MS], open(p, "w"))
    p = os.path.join(OUT, "%s_oi.json" % sym)
    if not os.path.exists(p):
        rows = pages(lambda e: BASE + "open-interest?category=linear&symbol=%sUSDT&intervalTime=1h&limit=200&endTime=%d" % (sym, e), "timestamp", 200)
        json.dump([[k, float(rows[k]["openInterest"])] for k in sorted(rows)], open(p, "w"))
    print(sym, "ok", flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for c in COINS:
        run(c)
