"""Executing-session wrapper: build the DEV frames with the frozen `run_dev.py vec`, no edit to any frozen file.

Why a wrapper: `context_asof.load_funding` reads zipped monthly funding files from F:/MTS/data/candle_close_dev_2022_2024,
which does not exist on this machine (JIS-NB). The same Binance monthly fundingRate series (columns calc_time,
funding_interval_hours, last_funding_rate) sits as CSV in F:/MTS/Dumps/backtest/raw/fundingRate. DECISION (OURS): read that
CSV instead, same rows. Funding enters the frame only through `f7_funding`, which is NOT part of C (PRE_REG s.2), and the
trade funding in study.py reads the same CSV through `load_funding_csv`.

  python build_frames.py       -> CACHE/frame_long.pkl, frame_short.pkl (what `run_dev.py vec` writes)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import context_asof as C  # noqa: E402

FUND_CSV_DIR = Path("F:/MTS/Dumps/backtest/raw/fundingRate")


def load_funding_csv():
    """Same output as context_asof.load_funding (calc_time ms, last_funding_rate), bar/settlement time < 2024-07-01."""
    rows = []
    for ym in C._months():
        rows.append(pd.read_csv(FUND_CSV_DIR / f"BTCUSDT-fundingRate-{ym}.csv"))
    f = pd.concat(rows, ignore_index=True).sort_values("calc_time")
    f = f[f["calc_time"] < C.DEV_END_MS]
    return f["calc_time"].to_numpy(np.int64), f["last_funding_rate"].to_numpy(float)


def main():
    if not C.FUND_DIR.exists():
        C.load_funding = load_funding_csv
    import run_dev  # noqa: E402
    run_dev.main("vec")


if __name__ == "__main__":
    main()
