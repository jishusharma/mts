"""Fetch Bybit v5 public linear 1h + daily klines + funding for 20 coins into runtime_data/edge9-phase-matched-1114/ (git-ignored).
Reuses the fetch helpers of research/rsi_extreme_confirm_2026-11-13/fetch_bybit.py (same API, same format)."""
import importlib.util, json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SIB = os.path.join(HERE, "..", "rsi_extreme_confirm_2026-11-13", "fetch_bybit.py")
spec = importlib.util.spec_from_file_location("sibfetch", SIB); sf = importlib.util.module_from_spec(spec); spec.loader.exec_module(sf)
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge9-phase-matched-1114"))
COINS = ["BTC","ETH","SOL","XRP","DOGE","BNB","ADA","LINK","LTC","AVAX","DOT","TRX","BCH","ATOM","NEAR","UNI","APT","ARB","OP","SUI"]
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for c in COINS:
        for iv in ("60", "D"):
            p = os.path.join(OUT, "%s_%s.json" % (c, iv))
            if os.path.exists(p): continue
            rows = sf.fetch(c, iv); json.dump(rows, open(p, "w")); print(c, iv, len(rows), rows[0][0] if rows else None, flush=True)
        p = os.path.join(OUT, "%s_fund.json" % c)
        if not os.path.exists(p):
            f = sf.fetch_funding(c); json.dump(f, open(p, "w")); print(c, "funding", len(f), flush=True)
