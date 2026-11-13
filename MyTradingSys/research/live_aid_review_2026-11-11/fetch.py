"""Public Binance spot klines (same source the Live Aid page reads) for the replay. Output is untracked (data/)."""
import json, pathlib, sys, time, urllib.request
BASE = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT"
OUT = pathlib.Path(__file__).parent / "data"; OUT.mkdir(exist_ok=True)
def get(tf, start, end):
    rows, t = [], start
    while t < end:
        u = f"{BASE}&interval={tf}&startTime={t}&endTime={end}&limit=1000"
        r = json.loads(urllib.request.urlopen(u, timeout=30).read())
        if not r: break
        rows += r; t = r[-1][0] + 1
        if len(r) < 1000: break
        time.sleep(0.2)
    return rows
now = int(sys.argv[1]) if len(sys.argv) > 1 else 1794343860000   # default frozen 2026-11-10 20:51Z (reproduces RESULT.md); pass epoch ms to extend
D = 86400000
for tf, days in [("1m", 32), ("3m", 32), ("5m", 33), ("15m", 36), ("30m", 40), ("1h", 45), ("2h", 60), ("4h", 90), ("1d", 40)]:
    rows = get(tf, now - days * D, now)
    (OUT / f"{tf}.json").write_text(json.dumps(rows))
    print(tf, len(rows), rows[0][0], rows[-1][0])
