"""Fetch Bybit v5 linear 5m klines (public) for BTC/ETH/SOL, cache to runtime_data/edge-session-sweep-reclaim-1113/."""
import json, os, sys, time, urllib.request
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "runtime_data", "edge-session-sweep-reclaim-1113")
START = 1583020800000  # 2020-03-01Z
M5 = 300000

def fetch(sym):
    os.makedirs(OUT, exist_ok=True)
    fn = os.path.join(OUT, sym + "_5m.json")
    rows = {}
    end = int(time.time() * 1000)
    while end > START:
        url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={sym}&interval=5&limit=1000&end={end}"
        for k in range(8):
            try:
                d = json.load(urllib.request.urlopen(url, timeout=30)); d["result"]["list"]; break
            except Exception as e:
                time.sleep(3 + 3 * k)
        else:
            raise SystemExit("fetch failed " + sym)
        lst = d["result"]["list"]
        if not lst: break
        for r in lst:
            rows[int(r[0])] = [int(r[0])] + [float(x) for x in r[1:5]]
        end = min(int(r[0]) for r in lst) - 1
        time.sleep(0.05)
    out = [rows[k] for k in sorted(rows)]
    json.dump(out, open(fn, "w"))
    print(sym, len(out), out[0][0], out[-1][0], flush=True)

if __name__ == "__main__":
    for s in sys.argv[1:] or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        fetch(s)
