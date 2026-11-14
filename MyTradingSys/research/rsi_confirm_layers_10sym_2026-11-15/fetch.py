"""Fetch the 10-symbol cache (Bybit v5 public linear 1h+1D klines, funding, 1h OI) into runtime_data/rsi-confirm-10sym-1115/ (ignored).
Reuses the 11-13 fetch code by path with only the coin list and cache dir replaced (no logic copied)."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("fetch_1113", os.path.join(HERE, "..", "rsi_confirm_layers_2026-11-13", "fetch.py"))
f = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(f)
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "rsi-confirm-10sym-1115"))
COINS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
f.OUT = OUT



def fetch_btc_context():
    """BTCUSDT spot 1d/1w/1M (regime context for research_kit.regime_tag), same source/code as the bb_range_retest_10sym fetch."""
    sp = importlib.util.spec_from_file_location("fetch_bb", os.path.join(HERE, "..", "bb_range_retest_10sym_2026-11-15", "fetch.py"))
    b = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(b)
    b.OUT = OUT
    for iv in ("1d", "1w", "1M"):
        print(b.fetch("BTC", iv, 0), flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for c in COINS:
        f.run(c)
    fetch_btc_context()
