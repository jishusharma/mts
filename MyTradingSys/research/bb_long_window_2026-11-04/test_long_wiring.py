"""Wiring tests for bb_long_window_2026-11-04/study_long.py: the P40 bear gate is separate from the primary gate and as-of, 'all' keeps tagged events
only, the pooled Holm family is m = 30, the ungated control and P40 trades use the same fills, and nothing at/after the window end is loaded."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("bb_long_study", HERE / "study_long.py")
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)
DAY = L.DAY


def _ctx(close_slope=-1.0, wk=30.0, mo=55.0, n=400, future=False):
    td = [(k + 1) * DAY for k in range(n)]
    cd = [1000.0 + close_slope * k for k in range(n)]
    tw = [(7 * k + 7) * DAY for k in range(n // 7)]
    tm = [(30 * k + 30) * DAY for k in range(n // 30)]
    rw, rm = [wk] * len(tw), [mo] * len(tm)
    if future:
        tw += [(n + 7) * DAY]
        rw += [90.0]
    return (td, cd), (tw, rw), (tm, rm)


def _regs(**kw):
    ctx = _ctx(**kw)
    return L.RSI.make_regime_at(*ctx), L.RSI.make_regime_at(*ctx, bear_proxy=True)


def test_p40_gate_fires_where_primary_is_range():
    t = 300 * DAY + 5
    rp, rx = _regs(wk=30.0, mo=55.0)                            # weekly <= 40, monthly 55: Malkan needs both
    assert L.gate_pass("range", rp, rx, t) and not L.gate_pass("bear", rp, rx, t)
    assert L.gate_pass(L.ARM_P40, rp, rx, t)


def test_p40_gate_is_as_of_planted_future_week_changes_nothing():
    t = 300 * DAY + 5
    a, b = _regs(future=True), _regs()
    assert L.gate_pass(L.ARM_P40, *a, t) == L.gate_pass(L.ARM_P40, *b, t) is True


def test_all_gate_drops_untagged_events():
    rp, rx = _regs()
    assert not L.gate_pass("all", rp, rx, 10 * DAY + 5)          # no SMA200 yet -> untagged -> out of every row, ungated included
    assert L.gate_pass("all", rp, rx, 300 * DAY + 5)


def test_pooled_family_is_30_and_holm_uses_it():
    assert (L.FAM_A, L.FAM_B, L.FAMILY_PRIMARY, L.FAMILY_M) == (6, 9, 15, 30)
    row = {"study": "A_r2r", "tf": "15m", "session": "asia", "side": "both", "n": 100, "days": 90, "gate": "range", "width": "any",
           "p": 0.01, "net": 0.1, "vs_ungated_t": 3.0}
    L.holm_family([row])
    assert abs(row["holm_p"] - 0.30) < 1e-9 and row["survivor"] is False      # 0.01 * 30, not 0.01 * 1


def test_survivor_needs_gate_effect_t():
    row = {"study": "B_retest", "tf": "15m", "session": "ny", "side": "both", "n": 100, "days": 90, "gate": L.ARM_P40, "tag": "tagged",
           "p": 1e-9, "net": 0.2, "vs_ungated_t": 1.0}
    L.holm_family([row])
    assert row["survivor"] is False
    row["vs_ungated_t"] = 2.5
    L.holm_family([row])
    assert row["survivor"] is True


def test_spot_loader_never_returns_bar_at_or_after_end(tmp_path):
    d = tmp_path / "BTCUSDT" / "15m" / "klines"
    d.mkdir(parents=True)
    rows = ["%d,1,2,0.5,1.5,10,0,0,0,0,0,0" % (k * 900000) for k in range(20)]
    (d / "x.csv").write_text("\n".join(rows) + "\n")
    bars = L.RSI.load_spot("15m", 10 * 900000, root=str(tmp_path))
    assert bars and bars[-1]["t"] < 10 * 900000 and len(bars) == 10


def test_window_is_long_dev_and_val_is_original_validation():
    lo, hi = L.window("dev")
    assert lo == L.A.ms(L.RSI.pd.Timestamp("2017-08-01")) and hi == L.A.ms(L.splits.DEV_END)
    assert L.window("val") == (L.A.ms(L.splits.VALIDATION_START), L.A.ms(L.splits.VALIDATION_END))
