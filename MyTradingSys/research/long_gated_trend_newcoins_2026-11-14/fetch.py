"""Fetch public data into runtime_data/edge8-long-gated-trend-newcoins-1114/ (git-ignored cache).
New coins: Bybit v5 linear daily klines + funding history (symbol = COIN + USDT). BTC (gate): data-api.binance.vision spot daily klines (as the parent)."""
import json, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from universe import COINS
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge8-long-gated-trend-newcoins-1114"))
START = 1577836800000  # 2020-01-01
DAY = 86400000


def get(u):
    for k in range(6):
        try:
            with urllib.request.urlopen(u, timeout=30) as r: return json.load(r)
        except Exception:
            time.sleep(1 + k)
    return None


def btc():
    rows, st = [], START
    while True:
        d = get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1000&startTime=%d" % st)
        if not d: break
        rows += [[r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[7])] for r in d]
        if len(d) < 1000: break
        st = d[-1][0] + 1
    return rows


def bybit_klines(sym):
    rows, end = [], int(time.time() * 1000)
    while True:
        d = get("https://api.bybit.com/v5/market/kline?category=linear&symbol=%s&interval=D&limit=1000&start=%d&end=%d" % (sym, START, end))
        lst = (d or {}).get("result", {}).get("list", [])
        if not lst: break
        rows += [[int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[6])] for x in lst]
        nend = min(int(x[0]) for x in lst) - 1
        if len(lst) < 1000 or nend >= end: break
        end = nend
    return sorted({r[0]: r for r in rows}.values())


def bybit_funding(sym):
    end, rows = int(time.time() * 1000), []
    while True:
        d = get("https://api.bybit.com/v5/market/funding/history?category=linear&symbol=%s&limit=200&startTime=%d&endTime=%d" % (sym, START, end))
        lst = (d or {}).get("result", {}).get("list", [])
        if not lst: break
        rows += [[int(x["fundingRateTimestamp"]), float(x["fundingRate"])] for x in lst]
        nend = min(int(x["fundingRateTimestamp"]) for x in lst) - 1
        if nend >= end or len(lst) < 200: break
        end = nend
    return sorted({r[0]: r for r in rows}.values())


def one(c):
    sym = c + "USDT"
    k = bybit_klines(sym); f = bybit_funding(sym)
    json.dump(k, open(os.path.join(OUT, c + "_1d.json"), "w")); json.dump({"sym": sym, "rows": f}, open(os.path.join(OUT, c + "_fund.json"), "w"))
    return c, len(k), len(f)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    json.dump(btc(), open(os.path.join(OUT, "BTC_spot_1d.json"), "w"))
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(one, COINS): print(*r, flush=True)
