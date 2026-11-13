"""Fetch Bybit v5 public linear USDT klines (no key): 4h (240), 12h (720) and daily (D) for 20 perps, 2020-01-01 on.
8h bars are built from 4h in run_1113.py (Bybit has no 8h). Cache (git-ignored): runtime_data/edge4-rsi-4h-le12-1113/<COIN>_<iv>.json
rows [open_ms, o, h, l, c, v] ascending.   python fetch_klines.py
"""
import json
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge4-rsi-4h-le12-1113"))
# 20 liquid USDT perps; list fixed in PRE_REG.md before any outcome (OURS): the 10 of the sibling RSI studies plus 10 older large caps.
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX",
         "DOT", "ATOM", "TRX", "BCH", "ETC", "UNI", "NEAR", "FIL", "XLM", "AAVE"]
START_MS = 1577836800000  # 2020-01-01 UTC
IVS = ("240", "720", "D")


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


def resample(rows, hours):
    """Aligned 8h/12h bars (UTC bucket start) from 4h rows [t,o,h,l,c,v]; a bucket missing any 4h bar is dropped."""
    step, span = 4 * 3600000, hours * 3600000
    by = {int(r[0]): r for r in rows}
    out = []
    for t0 in sorted(k for k in by if k % span == 0):
        parts = [by.get(t0 + i * step) for i in range(hours // 4)]
        if all(parts):
            out.append([t0, parts[0][1], max(p[2] for p in parts), min(p[3] for p in parts), parts[-1][4], sum(p[5] for p in parts)])
    return out


def check_continuity(rows, step_ms):
    """Count missing steps (gaps) and repeated open times (dups) in rows sorted by open time."""
    gaps = dups = 0
    for a, b in zip(rows, rows[1:]):
        d = int(b[0]) - int(a[0])
        if d == 0:
            dups += 1
        elif d > step_ms:
            gaps += 1
    return {"gaps": gaps, "dups": dups}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for c in COINS:
        for iv in IVS:
            p = os.path.join(OUT, "%s_%s.json" % (c, iv))
            if os.path.exists(p):
                continue
            rows = fetch(c, iv)
            json.dump(rows, open(p, "w"))
            print(c, iv, len(rows), rows[0][0] if rows else None, flush=True)
