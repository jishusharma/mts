"""Fetch Bybit v5 public SPOT 1h klines for the 40 new coins (PRE_REG.md list) into runtime_data/edge5-rsi-4h-exits-newcoins-1113/ (ignored cache)."""
import json, os, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge5-rsi-4h-exits-newcoins-1113"))
COINS = ["GRAM", "INJ", "QNT", "IMX", "HBAR", "ICP", "APEX", "MANA", "XDC", "SHIB", "STX", "FLR", "CRV", "OP", "BAT", "APT", "GALA", "TWT", "LDO", "HNT",
         "ALGO", "BONK", "APE", "GRT", "ZEN", "RUNE", "GMX", "DYDX", "CAKE", "THETA", "SAND", "WAVES", "CHZ", "MINA", "MPLX", "ENS", "AR", "XTZ", "NEXO", "JASMY"]
START_MS = 1577836800000  # 2020-01-01 UTC
BASE = "https://api.bybit.com/v5/market/"


def get(u):
    for k in range(8):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                d = json.load(r)
            if d.get("retCode") == 0 and "list" in d.get("result", {}):
                return d
            time.sleep(2 + 3 * k)
        except Exception:
            time.sleep(1 + k)
    raise RuntimeError(u)


def fetch_klines(sym, iv, since):
    end = int(time.time() * 1000)
    rows = {}
    while end > since:
        lst = get(BASE + "kline?category=spot&symbol=%sUSDT&interval=%s&limit=1000&end=%d" % (sym, iv, end))["result"]["list"]
        if not lst:
            break
        for r in lst:
            rows[int(r[0])] = [int(r[0])] + [float(x) for x in r[1:6]]
        old = min(int(r[0]) for r in lst)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.1)
    return rows


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for c in COINS:
        rows = fetch_klines(c, "60", START_MS)
        rows = [rows[k] for k in sorted(rows) if k >= START_MS]
        json.dump(rows, open(os.path.join(OUT, c + "_60.json"), "w"))
        print(c, len(rows), flush=True)
