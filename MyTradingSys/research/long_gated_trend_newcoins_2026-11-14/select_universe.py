"""Select the 'next 60' coins: Bybit v5 linear USDT perps, status Trading, symbolType '' or 'innovation' (crypto only: no stock/ETF/commodity/forex),
not a stablecoin / tokenised commodity, base not in the parent's 60, ranked by CURRENT 24h turnover. Prints and writes universe.py. Public endpoints only."""
import json, re, urllib.request, os
from universe_parent import COINS as PARENT
HERE = os.path.dirname(os.path.abspath(__file__))
EXCL = {"USDC", "USDE", "FDUSD", "TUSD", "DAI", "USDD", "PYUSD", "XAUT", "PAXG", "USD1", "RLUSD", "USDG", "USDT0"}
def get(u): return json.load(urllib.request.urlopen(u, timeout=30))["result"]
def norm(b): return re.sub(r"^(1000000|100000|10000|1000)|1000$", "", b)
info, cur = [], ""
while True:
    d = get("https://api.bybit.com/v5/market/instruments-info?category=linear&limit=1000" + ("&cursor=" + cur if cur else ""))
    info += d["list"]; cur = d.get("nextPageCursor", "")
    if not cur: break
meta = {x["symbol"]: x for x in info}
tk = get("https://api.bybit.com/v5/market/tickers?category=linear")["list"]
rows = sorted(((float(t["turnover24h"]), t["symbol"]) for t in tk), reverse=True)
par = {norm(c) for c in PARENT}; out = []
for to, s in rows:
    m = meta.get(s)
    if not m or m["quoteCoin"] != "USDT" or m["status"] != "Trading" or m["contractType"] != "LinearPerpetual" or m["symbolType"] not in ("", "innovation"): continue
    if m["baseCoin"] in EXCL or norm(m["baseCoin"]) in par or "USD" in m["baseCoin"] and m["baseCoin"].startswith("USD"): continue
    out.append((s, m["baseCoin"], to, m["fullName"], m["launchTime"]))
    if len(out) == 60: break
for i, o in enumerate(out, 1): print(i, *o)
json.dump([{"symbol": o[0], "base": o[1], "turnover24h": o[2], "name": o[3], "launch_ms": int(o[4])} for o in out], open(os.path.join(HERE, "universe_snapshot.json"), "w"), indent=1)
