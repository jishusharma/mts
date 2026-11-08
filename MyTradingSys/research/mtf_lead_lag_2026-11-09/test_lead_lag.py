"""mtf-timeframe-lead-lag-research: flip detection must be causal and the lead table must look back only."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("lead_lag", HERE / "lead_lag.py")
LL = importlib.util.module_from_spec(_s)
_s.loader.exec_module(LL)

STEP = 3_600_000


def bars_from(closes):
    return [{"t": i * STEP, "h": c + 1, "l": c - 1, "c": c} for i, c in enumerate(closes)]


def test_flip_detection_is_causal():
    # 20 flat-ish bars then a steady climb: RSI crosses 60 at some bar k; the flip is dated at bar k's CLOSE
    closes = [100 + (0.3 if i % 2 else -0.3) for i in range(20)] + [100 + 2 * j for j in range(1, 15)]
    flips = LL.rsi_flips(bars_from(closes), STEP)
    assert flips and flips[0][1] == "BULL"
    t_close = flips[0][0]
    k = t_close // STEP - 1                                       # index of the bar that closed the flip
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    r = rsi_core(closes, 14)
    assert r[k] >= 60 and r[k - 1] < 60                           # state changes on bar k itself, not earlier
    assert LL.rsi_flips(bars_from(closes[:k]), STEP) == [] or LL.rsi_flips(bars_from(closes[:k]), STEP)[-1][0] < t_close


def test_lead_table_only_looks_back():
    hi = [(100 * STEP, "BULL")]
    lo = [(90 * STEP, "BULL"), (101 * STEP, "BULL")]               # the later lower-TF flip must not count as a lead
    out = LL.lead_table(hi, lo, [x[0] for x in lo], 0, 10 ** 15)
    assert out["n"] == 1 and out["with_lead"] == 1.0 and out["median_h"] == 10.0


def test_state_at_uses_last_closed_flip():
    f = [(10, "BULL"), (20, "BEAR")]
    assert LL.state_at(f, 9) is None and LL.state_at(f, 10) == "BULL" and LL.state_at(f, 25) == "BEAR"
