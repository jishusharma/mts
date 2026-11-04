"""Long-window wiring for rsi_divergence_mtf_gated (study_long.py): the P40 bear proxy ignores monthly RSI but nothing else,
the proxy reads only as-of data, the ungated control keeps regime-tagged events only, and the spot loader never returns a bar at/after end_ms."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("rsi_gated_study_long", HERE / "study_long.py")
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)
DAY = L.DAY


def _ctx(close_slope=-1.0, wk=30.0, mo=55.0, n=400, future=False):
    td = [(k + 1) * DAY for k in range(n)]
    cd = [1000.0 + close_slope * k for k in range(n)]          # falling: below SMA200 once 200 bars exist
    tw = [(7 * k + 7) * DAY for k in range(n // 7)]
    tm = [(30 * k + 30) * DAY for k in range(n // 30)]
    rw, rm = [wk] * len(tw), [mo] * len(tm)
    if future:
        tw += [(n + 7) * DAY]
        rw += [90.0]
    return (td, cd), (tw, rw), (tm, rm)


def test_proxy_bear_ignores_monthly_primary_does_not():
    t = 300 * DAY + 5
    ctx = _ctx(wk=30.0, mo=55.0)                                # weekly <=40, monthly 55: Malkan bear needs both
    assert L.make_regime_at(*ctx)(t) == "range"
    assert L.make_regime_at(*ctx, bear_proxy=True)(t) == "bear"


def test_proxy_needs_close_below_sma200_and_weekly_le_40():
    t = 300 * DAY + 5
    assert L.make_regime_at(*_ctx(close_slope=+1.0, wk=30.0), bear_proxy=True)(t) != "bear"   # above SMA200
    assert L.make_regime_at(*_ctx(wk=45.0), bear_proxy=True)(t) != "bear"                    # weekly 45 > 40


def test_proxy_leaves_bull_untouched():
    t = 300 * DAY + 5
    ctx = _ctx(close_slope=+1.0, wk=70.0, mo=70.0)
    assert L.make_regime_at(*ctx)(t) == "bull" == L.make_regime_at(*ctx, bear_proxy=True)(t)


def test_proxy_is_as_of_planted_future_week_changes_nothing():
    t = 300 * DAY + 5
    assert L.make_regime_at(*_ctx(future=True), bear_proxy=True)(t) == L.make_regime_at(*_ctx(), bear_proxy=True)(t) == "bear"


def test_all_control_drops_untagged_events():
    regs = {10: None, 11: "bull", 12: "range"}
    ev = [{"t_close": d * DAY + 1, "i": d, "close_b": 1.0} for d in regs]
    assert [e["i"] for e in L.gate_all_tagged(ev, lambda t: regs[int(t // DAY)], "bullish")] == [11, 12]


def test_spot_loader_never_returns_bar_at_or_after_end(tmp_path):
    d = tmp_path / "BTCUSDT" / "1d" / "klines"
    d.mkdir(parents=True)
    rows = ["%d,1,2,0.5,1.5,10,0,0,0,0,0,0" % (k * DAY) for k in range(10)]
    (d / "x.csv").write_text("\n".join(rows) + "\n")
    bars = L.load_spot("1d", 5 * DAY, root=str(tmp_path))
    assert bars and bars[-1]["t"] < 5 * DAY and len(bars) == 5
