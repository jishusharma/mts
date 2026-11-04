"""Wiring tests for study_long.py (wavetrend_c30 long-window pass, PRE_REG_LONG.md). Hand arithmetic, never read back from the study."""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("wt_c30_long", HERE / "study_long.py")
sl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sl)

DAY = 86400000


def test_proxy_bear_is_weekly_alone_and_needs_side_below():
    assert sl.proxy_regime("below", 35.0) == "bear"          # weekly <= 40, monthly never looked at
    assert sl.proxy_regime("below", 40.0) == "bear"          # boundary counts
    assert sl.proxy_regime("below", 40.1) == "other"
    assert sl.proxy_regime("above", 35.0) == "other"         # bear also needs close below SMA200 (as the strict arm)
    assert sl.proxy_regime(None, 35.0) is None and sl.proxy_regime("below", None) is None


def test_strict_gate_untouched_while_proxy_fires():
    from MyTradingSys.backtest import research_kit as rk
    assert rk.rsi_band(35.0, 55.0) == "mid"                  # strict needs weekly AND monthly <= 40: no bear
    assert rk.rsi_band(35.0, 38.0) == "bear"
    assert sl.proxy_regime("below", 35.0) == "bear"          # the proxy differs exactly there


def test_family_sizes_count_the_proxy_arm():
    assert sl.M_POOLED_LONG == 48 and sl.M_SESSION_LONG == 192     # (24 strict-trend cells + 24 proxy cells) and x4 sessions


def test_long_window_ends_at_dev_end_and_starts_2018():
    from MyTradingSys.backtest import splits
    lo, hi = sl.window_long("dev")
    assert hi == int(splits.DEV_END.timestamp() * 1000) == 1719792000000
    assert lo == 1522540800000                                # 2018-04-01 00:00 UTC
    assert sl.window_long("val") == (1719792000000, 1751328000000)


def test_segments_split_at_old_dev_start():
    assert sl.segment_of(1640995199999) == "fresh"            # 2021-12-31 23:59:59.999
    assert sl.segment_of(1640995200000) == "old"              # 2022-01-01 00:00


def test_loader_never_returns_bar_at_or_after_end():
    with tempfile.TemporaryDirectory() as d:
        k = Path(d) / "BTCUSDT" / "1h" / "klines"
        k.mkdir(parents=True)
        rows = [f"{t},1,2,0.5,1.5,10,{t + 3599999},1,1,1,1,0" for t in (1719784800000, 1719788400000, 1719792000000, 1719795600000)]
        (k / "BTCUSDT-1h-2024-06.csv").write_text("\n".join(rows) + "\n")
        bars = sl.spot_bars(d, "BTCUSDT", "1h", 1719792000000)
        assert [b["t"] for b in bars] == [1719784800000, 1719788400000]
