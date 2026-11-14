"""Fetch Bybit v5 public linear 1h+1D klines and 1h open interest for the 40 new coins into runtime_data/edge5-rsi-oi-unwind-newcoins-1113/ (ignored cache)."""
import json, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge5-rsi-oi-unwind-newcoins-1113"))
COINS = ("ZEC AKE HYPE BARD 1000PEPE ENA INIT SUI ARIA AAVE JCT WLD XMR INJ PUMPFUN XLM ONDO SOPH TAO TRUMP ZRO H FARTCOIN BMT TIA "
         "USELESS HBAR PIEVERSE ICP QNT AERO STRK VVV OP KGEN WLFI XPL JUP Q ERA").split()
START_MS = 1577836800000
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


def pages(url_fn, ts_key):
    end = int(time.time() * 1000)
    rows = {}
    while end > START_MS:
        lst = get(url_fn(end))["result"]["list"]
        if not lst:
            break
        ks = [int(r[ts_key] if not isinstance(r, dict) else r[ts_key]) for r in lst]
        for k, r in zip(ks, lst):
            rows[k] = r
        old = min(ks)
        if old >= end:
            break
        end = old - 1
        time.sleep(0.05)
    return rows


def run(sym):
    for iv in ("60", "D"):
        p = os.path.join(OUT, "%s_%s.json" % (sym, iv))
        if not os.path.exists(p):
            rows = pages(lambda e: BASE + "kline?category=linear&symbol=%sUSDT&interval=%s&limit=1000&end=%d" % (sym, iv, e), 0)
            json.dump([[k] + [float(x) for x in rows[k][1:6]] for k in sorted(rows) if k >= START_MS], open(p, "w"))
    p = os.path.join(OUT, "%s_oi.json" % sym)
    if not os.path.exists(p):
        rows = pages(lambda e: BASE + "open-interest?category=linear&symbol=%sUSDT&intervalTime=1h&limit=200&endTime=%d" % (sym, e), "timestamp")
        json.dump([[k, float(rows[k]["openInterest"])] for k in sorted(rows)], open(p, "w"))
    print(sym, "ok", flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(run, COINS))
