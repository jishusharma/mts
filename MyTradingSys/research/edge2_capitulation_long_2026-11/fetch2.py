"""Fetch Bybit v5 public 1h linear klines + funding for the 20 NEW coins; cache under runtime_data/edge2-capitulation-long-1113/ (ignored)."""
import json, os, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "runtime_data", "edge2-capitulation-long-1113")
CANDIDATES = "DOT UNI ATOM NEAR FIL TRX ETC BCH AAVE XLM ICP APT ARB OP INJ SAND MANA AXS ALGO GRT EOS THETA".split()
START_MS = 1577836800000
MIN_BARS = 2 * 365 * 24


def get(url):
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "mts-research"}), timeout=30) as r:
                d = json.load(r)
            if d.get("retCode") == 0:
                return d["result"]["list"]
        except Exception:
            pass
        time.sleep(1 + k)
    return None


def klines(sym):
    rows, end = {}, int(time.time() * 1000)
    while end > START_MS:
        lst = get("https://api.bybit.com/v5/market/kline?category=linear&symbol=%sUSDT&interval=60&limit=1000&end=%d" % (sym, end))
        if not lst:
            break
        for r in lst:
            rows[int(r[0])] = [int(r[0])] + [float(x) for x in r[1:6]]
        old = min(int(r[0]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.05)
    return [rows[k] for k in sorted(rows) if k >= START_MS]


def funding(sym):
    rows, end = {}, int(time.time() * 1000)
    while end > START_MS:
        lst = get("https://api.bybit.com/v5/market/funding/history?category=linear&symbol=%sUSDT&limit=200&endTime=%d" % (sym, end))
        if not lst:
            break
        for r in lst:
            rows[int(r["fundingRateTimestamp"])] = float(r["fundingRate"])
        old = min(int(r["fundingRateTimestamp"]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.05)
    return [[k, rows[k]] for k in sorted(rows) if k >= START_MS]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    good = []
    for c in CANDIDATES:
        if len(good) == 20:
            break
        p, p2 = os.path.join(OUT, c + "_1h.json"), os.path.join(OUT, c + "_fund.json")
        if not os.path.exists(p):
            k = klines(c)
            if len(k) < MIN_BARS:
                print(c, "SKIP bars", len(k), flush=True)
                continue
            json.dump(k, open(p, "w"))
        if not os.path.exists(p2):
            json.dump(funding(c), open(p2, "w"))
        k = json.load(open(p))
        print(c, len(k), time.strftime("%Y-%m-%d", time.gmtime(k[0][0] / 1000)), len(json.load(open(p2))), flush=True)
        good.append(c)
    json.dump(good, open(os.path.join(OUT, "coins.json"), "w"))
    print("NEW20", " ".join(good))
