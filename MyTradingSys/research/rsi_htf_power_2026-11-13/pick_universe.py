"""Selects Block 2 universe: top USDT spot pairs by 24h quote volume (data-api.binance.vision) with first daily kline before 2022-01-01,
excluding the parent's 20, stablecoins, wrapped/synthetic/tokenised-stock/fiat/gold tokens. Run once; result frozen in PRE_REG.md."""
import json, urllib.request
API = "https://data-api.binance.vision/api/v3/"
PARENT = set("BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM UNI TRX BCH ETC FIL XLM NEAR SAND".split())
EXCL = set("USDC USD1 RLUSD FDUSD TUSD USDP DAI BUSD USDE USDS PYUSD AEUR EUR GBP TRY BRL XAUT PAXG WBTC WBETH WBNB BETH STETH WEETH BFUSD RWUSD U UST USTC LUNC".split())
def get(p): return json.load(urllib.request.urlopen(API + p, timeout=30))
if __name__ == "__main__":
    ex = get("exchangeInfo?permissions=SPOT")
    base = {s["symbol"]: s["baseAsset"] for s in ex["symbols"] if s["status"] == "TRADING" and s["quoteAsset"] == "USDT"}
    rows = sorted(((float(x["quoteVolume"]), x["symbol"]) for x in get("ticker/24hr") if x["symbol"] in base), reverse=True)
    out = []
    for v, s in rows:
        b = base[s]
        if not s.isascii() or not s.isalnum():
            continue
        if b in PARENT or b in EXCL or b.endswith("B") and len(b) > 4 or b.endswith(("UP", "DOWN")):
            continue
        k = get("klines?symbol=%s&interval=1d&startTime=0&limit=1" % s)
        if not k or k[0][0] >= 1640995200000:
            continue
        out.append(b)
        if len(out) == 40: break
    print(" ".join(out))
