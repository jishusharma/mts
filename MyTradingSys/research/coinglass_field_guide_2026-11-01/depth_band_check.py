"""How much of the +/-1 % band does Binance USD-M depth limit=100 see, against limit=1000?

Mirrors MarketDataSnapshot.bidAskRatioFromDepth (USD within p >= px*0.99 / p <= px*1.01). Public endpoint, no keys.
Run on the feed host (fapi.binance.com timed out from JIS-NB on 2026-11-01). Prints JSON: deepest level as percent from
mid, USD and BTC inside the band, ratio and imbalance (bid - ask)/(bid + ask) for each limit. Compare the imbalance with the
CoinGlass heatmap page box "Imbalance +/-1 %" read at the same minute (FIELD_GUIDE.md section 5).
"""
import json
import sys
import time
import urllib.request

URL = "https://fapi.binance.com/fapi/v1/depth?symbol=%s&limit=%d"


def get(symbol, limit):
    with urllib.request.urlopen(URL % (symbol, limit), timeout=20) as r:
        return json.load(r)


def band(d, pct=0.01):
    """USD and base inside +/-pct of mid, the way the snapshot sums it, plus how far the deepest level reaches."""
    px = (float(d["bids"][0][0]) + float(d["asks"][0][0])) / 2
    b = a = bq = aq = 0.0
    for p, q in d["bids"]:
        if float(p) >= px * (1 - pct):
            b += float(p) * float(q)
            bq += float(q)
    for p, q in d["asks"]:
        if float(p) <= px * (1 + pct):
            a += float(p) * float(q)
            aq += float(q)
    return {"mid": px, "levels": len(d["bids"]),
            "deepest_bid_pct": 100 * (float(d["bids"][-1][0]) / px - 1),
            "deepest_ask_pct": 100 * (float(d["asks"][-1][0]) / px - 1),
            "bid_usd": round(b), "ask_usd": round(a), "bid_base": round(bq, 1), "ask_base": round(aq, 1),
            "ratio": (b / a) if a else None, "imbalance": ((b - a) / (b + a)) if (b + a) else None}


def main(argv):
    symbol = argv[1] if len(argv) > 1 else "BTCUSDT"
    out = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "symbol": symbol}
    for lim in (100, 1000):
        out[str(lim)] = band(get(symbol, lim))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
