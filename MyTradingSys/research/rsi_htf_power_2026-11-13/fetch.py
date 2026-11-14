"""Fetch Binance SPOT klines (1h, 1d) from data-api.binance.vision (public market data) for both blocks into the ignored cache runtime_data/edge5-rsi-htf-power-1113/."""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge5-rsi-htf-power-1113"))
PARENT20 = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM UNI TRX BCH ETC FIL XLM NEAR SAND".split()
NEW40 = ("ZEC INJ AAVE FET QNT HBAR ICP DODO ONE DASH STX RAY AR CAKE DEXE SHIB JST CRV ZEN BAT GTC ALGO RUNE GRT VET CITY AVA LSK GALA PHA AXS CFX RSR IOTA SUPER CHZ CVX TWT PEOPLE HOT").split()
API = "https://data-api.binance.vision/api/v3/klines"


def get(u):
    for k in range(8):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(1 + 2 * k)
    raise RuntimeError(u)


def fetch(sym, iv):
    p = os.path.join(OUT, "%s_%s.json" % (sym, iv))
    if os.path.exists(p):
        return sym, iv, -1
    rows, start = [], 0
    while True:
        lst = get("%s?symbol=%sUSDT&interval=%s&startTime=%d&limit=1000" % (API, sym, iv, start))
        if not lst:
            break
        rows += [[int(r[0])] + [float(x) for x in r[1:6]] for r in lst]
        start = int(lst[-1][0]) + 1
        if len(lst) < 1000:
            break
    json.dump(rows, open(p, "w"))
    return sym, iv, len(rows)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    jobs = [(c, iv) for c in PARENT20 + NEW40 for iv in ("1d", "1h")]
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(lambda a: fetch(*a), jobs):
            print(*r, flush=True)
