"""Example of backtest/trade_sanity.py on a finished study (read-only; no number of RESULT.md or PRE_REG.md changes).

Re-prints the study's primary cell (d=1, h=60) from ledger.csv: arm T = rows with F == 1. Entry bar = signal bar + 1 + d
minutes, exit bar = entry + h minutes, both filled at the 1m bar open (screen.py compute_cells).
Usage: python log_sanity_example.py   (needs the DEV 1m klines under F:/MTS/data/tom_raw/klines)
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "backtest"))
import trade_sanity as T  # noqa: E402

KL = Path("F:/MTS/data/tom_raw/klines")
D, H = 1, 60


def main():
    rows = [r for r in csv.DictReader(open(HERE / "ledger.csv", encoding="utf-8")) if r["F"] == "1" and r["dropped"] == "0"]
    klines = T.load_klines(sorted(KL.glob("BTCUSDT-1m-202[2-4]-*.csv")))
    trades = []
    for r in rows:
        e = int(r["t_open_time"]) + (1 + D) * T.MS
        x = e + H * T.MS
        side = int(r["side"])
        pin = float(r["p_in_d%d" % D])
        g = float(r["G_d%d_h%d" % (D, H)])
        pout = pin * (1 + g / 100.0 / side)      # G = side * (pout / pin - 1) * 100
        trades.append(dict(side=side, entry_ms=e, exit_ms=x, entry_px=pin, exit_px=pout, ret=g))
    print("arm T rows (F==1, not dropped): %d" % len(trades))
    T.log_sanity(trades, klines, tol_pct=0.001)
    print()
    print("\n".join(T.year_side_lines(trades)))


if __name__ == "__main__":
    main()
