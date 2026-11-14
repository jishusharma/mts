"""Fetch daily spot klines (data-api.binance.vision, public) and Bybit v5 linear funding history (public) into runtime_data/edge7-daily-trend-follow-1113/ (ignored cache)."""
import json, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from universe import COINS
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge7-daily-trend-follow-1113"))
START = 1577836800000  # 2020-01-01
def get(u):
    for k in range(6):
        try:
            with urllib.request.urlopen(u, timeout=30) as r: return json.load(r)
        except Exception:
            time.sleep(1 + k)
    return None
def klines(c):
    rows, st = [], START
    while True:
        d = get("https://data-api.binance.vision/api/v3/klines?symbol=%sUSDT&interval=1d&limit=1000&startTime=%d" % (c, st))
        if not d: break
        rows += [[r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[7])] for r in d]
        if len(d) < 1000: break
        st = d[-1][0] + 1
    return rows
def funding(c):
    for sym in (c + "USDT", "1000" + c + "USDT", "10000" + c + "USDT"):
        end, rows = int(time.time() * 1000), []
        while True:
            d = get("https://api.bybit.com/v5/market/funding/history?category=linear&symbol=%s&limit=200&startTime=%d&endTime=%d" % (sym, START, end))
            lst = (d or {}).get("result", {}).get("list", []) if d else []
            if not lst: break
            rows += [[int(x["fundingRateTimestamp"]), float(x["fundingRate"])] for x in lst]
            nend = min(int(x["fundingRateTimestamp"]) for x in lst) - 1
            if nend >= end or len(lst) < 200: break
            end = nend
        if rows: return sym, sorted(rows)
    return None, []
def one(c):
    k = klines(c); sym, f = funding(c)
    json.dump(k, open(os.path.join(OUT, c + "_1d.json"), "w")); json.dump({"sym": sym, "rows": f}, open(os.path.join(OUT, c + "_fund.json"), "w"))
    return c, len(k), sym, len(f)
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(one, COINS): print(*r, flush=True)
