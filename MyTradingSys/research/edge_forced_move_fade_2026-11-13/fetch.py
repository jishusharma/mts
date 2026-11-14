"""Fetch Bybit v5 public 15m kline + 15min open-interest for 10 perps -> runtime_data/edge-forced-1113/<SYM>.json (funding reused from edge-oi-flush cache)."""
import json, sys, time, urllib.request, urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
COINS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runtime_data" / "edge-forced-1113"
OLD = Path("C:/Users/E-ngineers/IdeaProjects/mts-jis-nb-edge-oi-flush-1113/runtime_data/edge-oi-flush-1113")
BASE = "https://api.bybit.com/v5/market/"
def get(ep, **p):
    for k in range(12):
        try:
            r = json.load(urllib.request.urlopen(BASE + ep + "?" + urllib.parse.urlencode(p), timeout=30))
            if r.get("retCode") == 0: return r
            time.sleep(1 + k)
        except Exception: time.sleep(1 + k)
    raise RuntimeError(ep)
def oi(sym):
    rows, cur = [], ""
    while True:
        p = dict(category="linear", symbol=sym, intervalTime="15min", limit=200)
        if cur: p["cursor"] = cur
        r = get("open-interest", **p)["result"]
        rows += [(int(x["timestamp"]), float(x["openInterest"])) for x in r["list"]]
        cur = r.get("nextPageCursor", "")
        if not cur or not r["list"]: break
    return sorted(set(rows))
def kl(sym):
    rows, end = [], int(time.time() * 1000)
    while True:
        l = get("kline", category="linear", symbol=sym, interval="15", limit=1000, end=end)["result"]["list"]
        if not l: break
        rows += [tuple(float(v) for v in x[:6]) for x in l]   # t,o,h,l,c,volume
        end = int(l[-1][0]) - 1
        if len(l) < 1000: break
    return sorted(set(rows))
def one(c):
    s = c + "USDT"
    f = OUT / f"{s}.json"
    if f.exists(): return s, "cached"
    old = json.loads((OLD / f"{s}.json").read_text())
    d = dict(oi=oi(s), kl=kl(s), fund=old["fund"])
    f.write_text(json.dumps(d))
    return s, {k: (len(v), time.strftime("%Y-%m-%d", time.gmtime(v[0][0] / 1000))) for k, v in d.items()}
if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(5) as ex:
        for s, i in ex.map(one, COINS): print(s, i, flush=True)
