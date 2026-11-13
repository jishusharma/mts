"""Fetch Bybit v5 public 1h kline, open-interest (1h), funding history for 10 perps to runtime_data/edge-oi-flush-1113/."""
import json, sys, time, urllib.request, urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
COINS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
OUT = Path(__file__).resolve().parents[3] / "runtime_data" / "edge-oi-flush-1113"
BASE = "https://api.bybit.com/v5/market/"

def get(ep, **p):
    for k in range(10):
        try:
            r = json.load(urllib.request.urlopen(BASE + ep + "?" + urllib.parse.urlencode(p), timeout=30))
            if r.get("retCode") == 0:
                return r
            time.sleep(2 + 2 * k)
        except Exception:
            time.sleep(1 + k)
    raise RuntimeError(ep)

def oi(sym):
    rows, cur = [], ""
    while True:
        p = dict(category="linear", symbol=sym, intervalTime="1h", limit=200)
        if cur: p["cursor"] = cur
        r = get("open-interest", **p)["result"]
        rows += [(int(x["timestamp"]), float(x["openInterest"])) for x in r["list"]]
        cur = r.get("nextPageCursor", "")
        if not cur or not r["list"]: break
    return sorted(set(rows))

def kl(sym):
    rows, end = [], int(time.time() * 1000)
    while True:
        l = get("kline", category="linear", symbol=sym, interval="60", limit=1000, end=end)["result"]["list"]
        if not l: break
        rows += [tuple(float(v) for v in x[:5]) for x in l]
        end = int(l[-1][0]) - 1
        if len(l) < 1000: break
    return sorted(set(rows))

def fund(sym):
    rows, end = [], int(time.time() * 1000)
    while True:
        l = get("funding/history", category="linear", symbol=sym, limit=200, endTime=end)["result"]["list"]
        if not l: break
        rows += [(int(x["fundingRateTimestamp"]), float(x["fundingRate"])) for x in l]
        end = int(l[-1]["fundingRateTimestamp"]) - 1
        if len(l) < 200: break
    return sorted(set(rows))

def one(c):
    s = c + "USDT"
    if (OUT / f"{s}.json").exists():
        d = json.loads((OUT / f"{s}.json").read_text()); return s, {k: (len(v), v[0][0]) for k, v in d.items()}
    d = dict(oi=oi(s), kl=kl(s), fund=fund(s))
    (OUT / f"{s}.json").write_text(json.dumps(d))
    return s, {k: (len(v), v[0][0]) for k, v in d.items()}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(3) as ex:
        for s, i in ex.map(one, COINS):
            print(s, {k: (n, time.strftime("%Y-%m-%d", time.gmtime(t / 1000))) for k, (n, t) in i.items()}, flush=True)
