"""Fetch public data for Test 4 into a host cache OUTSIDE the repo (never committed; repo is public).
Binance spot 1d klines (data-api.binance.vision) and Bybit linear funding history + 1d open interest (public, no key).
Cache: $BZ4_CACHE or C:/Users/e-ngineers/mts_cache/buyzone_test4. Files: <COIN>_spot.json, <COIN>_fund.json, <COIN>_oi.json."""
import json
import os
import time
import urllib.parse
import urllib.request

CACHE = os.environ.get("BZ4_CACHE", "C:/Users/e-ngineers/mts_cache/buyzone_test4")
UNIVERSE = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "LTC", "LINK", "TRX", "DOT", "AVAX", "ATOM",
            "ETC", "XLM", "BCH", "NEO", "UNI", "NEAR", "FIL", "ALGO", "VET"]
SPOT = "https://data-api.binance.vision/api/v3/klines"
BYBIT = "https://api.bybit.com/v5/market"


def get(url):
    for i in range(6):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(1 + i)
    raise RuntimeError(url)


def spot(coin):
    rows, start = [], 0
    while True:
        d = get("%s?symbol=%sUSDT&interval=1d&limit=1000&startTime=%d" % (SPOT, coin, start))
        if not d:
            break
        rows += [[int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in d]
        start = int(d[-1][0]) + 1
        if len(d) < 1000:
            break
    return rows


def funding(sym):
    out, end = [], int(time.time() * 1000)
    while True:
        d = get("%s/funding/history?category=linear&symbol=%s&limit=200&endTime=%d" % (BYBIT, sym, end))
        lst = d.get("result", {}).get("list", [])
        if not lst:
            break
        out += [[int(x["fundingRateTimestamp"]), float(x["fundingRate"])] for x in lst]
        nend = min(int(x["fundingRateTimestamp"]) for x in lst) - 1
        if nend >= end:
            break
        end = nend
        if len(lst) < 200:
            break
    return sorted(set(map(tuple, out)))


def oi(sym):
    out, cur = [], ""
    while True:
        u = "%s/open-interest?category=linear&symbol=%s&intervalTime=1d&limit=200" % (BYBIT, sym)
        if cur:
            u += "&cursor=" + urllib.parse.quote(cur, safe="")
        d = get(u)
        res = d.get("result", {})
        lst = res.get("list", [])
        out += [[int(x["timestamp"]), float(x["openInterest"])] for x in lst]
        cur = res.get("nextPageCursor", "")
        if not lst or not cur:
            break
    return sorted(set(map(tuple, out)))


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    for c in UNIVERSE:
        s = spot(c)
        json.dump(s, open("%s/%s_spot.json" % (CACHE, c), "w"))
        f = funding(c + "USDT")
        json.dump(f, open("%s/%s_fund.json" % (CACHE, c), "w"))
        o = oi(c + "USDT")
        json.dump(o, open("%s/%s_oi.json" % (CACHE, c), "w"))
        print(c, len(s), len(f), len(o), o[0][0] if o else None, f[0][0] if f else None, flush=True)
