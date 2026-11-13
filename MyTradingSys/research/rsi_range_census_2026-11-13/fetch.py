"""Fetch Bybit linear 5m klines (public) to runtime_data/rsi_range_census_1113/<SYM>_5m.csv, paged backwards."""
import sys, time, json, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runtime_data" / "rsi_range_census_1113"
OUT.mkdir(parents=True, exist_ok=True)
STEP = 5 * 60 * 1000

def get(sym, end_ms):
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={sym}&interval=5&limit=1000&end={end_ms}"
    for k in range(6):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=30).read())["result"]["list"]
        except Exception:
            time.sleep(1 + k)
    raise RuntimeError("fetch failed")

def run(sym):
    rows = {}
    end = int(time.time() * 1000)
    while True:
        lst = get(sym, end)
        if not lst:
            break
        for r in lst:
            rows[int(r[0])] = r[1:6]
        oldest = int(lst[-1][0])
        if oldest >= end:
            break
        end = oldest - 1
        if len(lst) < 1000:
            break
        time.sleep(0.05)
    with open(OUT / f"{sym}_5m.csv", "w") as f:
        f.write("t,o,h,l,c,v\n")
        for t in sorted(rows):
            f.write(f"{t},{','.join(rows[t])}\n")
    print(sym, len(rows), min(rows), max(rows), flush=True)

if __name__ == "__main__":
    for s in sys.argv[1:]:
        run(s)
