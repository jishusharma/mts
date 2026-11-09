"""Spec test: three hand-computed trades (fees.py Deribit: taker 0.0005, maker 0). Run: python <this file>."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from MyTradingSys.backtest.layers.fabio import rescore as R  # noqa: E402


def close(a, b):
    return abs(a - b) < 1e-9


def test_long_target_market_entry():
    # entry 100000, stop 99000 (risk 1000), target 102000 -> gross +2R; fee = 0.0005 * 100000 / 1000 = 0.05R (entry only, target maker)
    g, f, n = R.net_r(+1, 100000.0, 99000.0, 102000.0, "taker", "maker")
    assert close(g, 2.0) and close(f, 0.05) and close(n, 1.95)


def test_short_stop_both_taker():
    # short entry 50000, stop 50500 (risk 500), stopped at 50500 -> gross -1R; fee = 2 * 0.0005 * 50000 / 500 = 0.10R
    g, f, n = R.net_r(-1, 50000.0, 50500.0, 50500.0, "taker", "taker")
    assert close(g, -1.0) and close(f, 0.10) and close(n, -1.10)


def test_long_limit_entry_maker_zero_fee_target():
    # limit entry 80000 (maker 0), stop 79200 (risk 800), target 81600 maker -> +2R, fee 0 -> net +2R
    g, f, n = R.net_r(+1, 80000.0, 79200.0, 81600.0, "maker", R.exit_kind_for("target"))
    assert close(g, 2.0) and f == 0.0 and close(n, 2.0)
    assert R.exit_kind_for("stop") == "taker"


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v()
    print("ok")
