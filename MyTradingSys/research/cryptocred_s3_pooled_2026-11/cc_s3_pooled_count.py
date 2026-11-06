"""Count-only: pooled BTC+ETH DEV fills of CryptoCred 4h Setup 1 (sr_flip), ATR buffer k. No trade is simulated,
no exit or R is computed: only find_limit_fill (does the resting limit trade through the level) is called.
Card route-cryptocred-s3-power-unblock. DEV only: bars cut at 2024-07-01 and splits.assert_dev_only."""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE.parent / "cryptocred_s3_2026-11"))

import cc_s3_run as S  # noqa: E402
from MyTradingSys.backtest.layers.cryptocred import run_cc_setups as R  # noqa: E402

TICKS = {"BTCUSDT": 0.1, "ETHUSDT": 0.01}   # Binance tick sizes (SOURCED: exchange filters); BTC = repo TICK
DATASETS = {"BTCUSDT": "klines", "ETHUSDT": "klines_eth"}


def dev_bars(bars):
    out = [b for b in bars if S.DEV_START_MS <= b["t"] < S.DEV_END_MS]
    S.assert_bars_dev_only(out)
    return out


def count_fills(bars_1m, htf_4h, k, tick, setup="setup1_sr_flip"):
    """Signals and filled limits for one symbol on DEV bars. Refuses any bar at/after DEV_END."""
    S.assert_bars_dev_only(bars_1m)
    S.assert_bars_dev_only(htf_4h)
    sigs, skipped = S.build_signals(setup, htf_4h, k)
    times = [b["t"] for b in bars_1m]
    filled = sum(1 for s in sigs if R.find_limit_fill(s, bars_1m, S.TF_MS["4h"], times, tick) is not None)
    return {"signals": len(sigs), "skipped": skipped, "filled": filled}


def pooled(per_symbol):
    return sum(v["filled"] for v in per_symbol.values())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--k", type=float, default=1.0)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    from MyTradingSys.backtest.bt.bt_data import load_klines
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    reg = json.loads(R.REGISTRY_PATH.read_text(encoding="utf-8"))
    res = {}
    for sym, ds in DATASETS.items():
        bars = dev_bars(load_klines(Path(a.data_root), dataset=ds))
        res[sym] = count_fills(bars, resample(bars, "4h", reg), a.k, TICKS[sym])
        res[sym]["bars_1m"] = len(bars)
        print(sym, res[sym], file=sys.stderr)
    res["pooled_filled"] = pooled({s: res[s] for s in DATASETS})
    print(json.dumps(res))
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
