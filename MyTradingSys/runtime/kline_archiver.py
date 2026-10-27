import sys
sys.dont_write_bytecode = True
import json, os, urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT  = Path(__file__).resolve().parents[2]
STORE = ROOT / "MyTradingSys" / "market_data" / "klines"
SYMBOL = "BTCUSDT"
INTERVALS = [("1h", 500), ("15m", 500), ("5m", 500)]

def fetch(interval, limit=100):
    url = (f"https://fapi.binance.com/fapi/v1/klines"
           f"?symbol={SYMBOL}&interval={interval}&limit={limit}")
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode())
def load(path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def merge(old, new, cap):
    by_time = {int(b["open_time"]): b for b in old}
    for k in new:
        by_time[int(k[0])] = {
            "open_time":  int(k[0]),
            "close_time": int(k[6]),
            "open":   float(k[1]),
            "high":   float(k[2]),
            "low":    float(k[3]),
            "close":  float(k[4]),
            "volume": float(k[5]),
        }
    bars = sorted(by_time.values(), key=lambda b: b["open_time"])
    if len(bars) > cap:
        bars = bars[-cap:]
    return bars
def main():
    STORE.mkdir(parents=True, exist_ok=True)
    report = []
    for interval, cap in INTERVALS:
        try:
            new = fetch(interval)
        except Exception as e:
            report.append(f"{interval}:ERR({e})")
            continue
        path = STORE / f"{SYMBOL}_{interval}.json"
        old = load(path)
        bars = merge(old, new, cap)
        tmp = path.with_suffix(".json.new")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(bars, f)
        os.replace(tmp, path)
        report.append(f"{interval}:{len(bars)}")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"{ts} klines {' '.join(report)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
