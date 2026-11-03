import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prob_table_run as pt


def test_future_bar_does_not_change_prior_state():
    bars = pt.synthetic_bars([10, 11, 10, 12, 11, 13] * 4)
    before = pt.states(bars)
    changed = bars.copy()
    changed.loc[changed.index[-1] + pt.pd.Timedelta(hours=1)] = [999, 1000, 998, 999]
    after = pt.states(changed)
    assert before.iloc[:-1].equals(after.loc[before.index[:-1]])


def test_hand_logloss_for_two_cells():
    # EXPECT: y=[up, down], p_up=[.75, .75] -> (-ln(.75)-ln(.25))/2.
    got = pt.mean_logloss([1, 0], [0.75, 0.75])
    assert math.isclose(got, -0.5 * (math.log(.75) + math.log(.25)))


def test_shrinkage_uses_regime_parent_below_30():
    # EXPECT: 29-cell observation uses parent p_up=.6; 30-cell uses its own .2.
    cell, parent = {"n": 29, "p_up": .2}, {"n": 100, "p_up": .6}
    assert pt.shrunk_probability(cell, parent) == .6
    assert pt.shrunk_probability({"n": 30, "p_up": .2}, parent) == .2


def test_loader_refuses_any_window_after_frozen_cutoff():
    try:
        pt.load_minutes(Path("missing-data-is-not-read"), "2024-01-01", "2024-07-02")
    except ValueError as exc:
        assert "exceeds frozen cutoff" in str(exc)
    else:
        raise AssertionError("post-cutoff data window must be refused")


def test_month_files_outside_half_open_window_are_never_opened(monkeypatch):
    with tempfile.TemporaryDirectory(prefix="cutoff-fixture-", dir=Path(__file__).parent) as temp:
        folder = Path(temp)
        june = folder / "BTCUSDT-1m-2024-06.csv"
        july = folder / "BTCUSDT-1m-2024-07.csv"
        december = folder / "BTCUSDT-1m-2021-12.csv"
        january = folder / "BTCUSDT-1m-2022-01.csv"
        june.write_text("1719791940000,1,1,1,1,1,1719791999999,1,1,1,1,0\n", encoding="utf-8")
        july.write_text("SENTINEL: MUST NOT BE OPENED\n", encoding="utf-8")
        december.write_text("1640995140000,1,1,1,1,1,1640995199999,1,1,1,1,0\n", encoding="utf-8")
        january.write_text("SENTINEL: MUST NOT BE OPENED\n", encoding="utf-8")
        original_read_csv = pt.pd.read_csv

        def guarded_read_csv(path, *args, **kwargs):
            if Path(path).name in {july.name, january.name}:
                raise AssertionError(f"excluded monthly file was opened: {path}")
            return original_read_csv(path, *args, **kwargs)

        monkeypatch.setattr(pt.pd, "read_csv", guarded_read_csv)
        june_rows = pt.load_minutes(folder, "2024-06-30", "2024-07-01")
        december_rows = pt.load_minutes(folder, "2021-12-31", "2022-01-01")
        assert len(june_rows) == len(december_rows) == 1


def test_aggregate_refuses_incomplete_candle():
    idx = pt.pd.date_range("2024-01-01", periods=59, freq="min", tz="UTC")
    bars = pt.pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}, index=idx)
    try:
        pt.aggregate(bars, 1)
    except ValueError as exc:
        assert "incomplete 1h candle" in str(exc)
    else:
        raise AssertionError("incomplete candles must not be scored")


def test_aggregate_refuses_missing_source_minute():
    idx = pt.pd.date_range("2024-01-01", periods=60, freq="min", tz="UTC").delete(17)
    bars = pt.pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}, index=idx)
    try:
        pt.aggregate(bars, 1)
    except ValueError as exc:
        assert "missing source minute" in str(exc)
    else:
        raise AssertionError("missing source minutes must not be bridged")
