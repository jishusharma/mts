"""Tests for dev_ext.py: the DEV_EXT flag can never return VALIDATION/HOLDOUT rows (synthetic files, CI-safe)."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import context_asof as C  # noqa: E402
import dev_ext as X  # noqa: E402

MIN = 60_000
Y2020 = X.DEV_EXT_START_MS
Y2024_07 = C.DEV_END_MS


def _bars(ots):
    n = len(ots)
    return {"ot": np.array(ots, dtype=np.int64), "o": np.ones(n), "h": np.ones(n), "l": np.ones(n), "c": np.ones(n), "v": np.ones(n)}


def _ext_dir(tmp_path, planted_ms=()):
    k = tmp_path / "klines"
    k.mkdir()
    for ym in X.ext_months():
        rows = []
        if ym == "2020-01":
            rows += [Y2020 + i * MIN for i in range(10)]
        if ym == "2021-12":
            rows += [X.DEV_EXT_END_MS - 2 * MIN, X.DEV_EXT_END_MS - MIN] + list(planted_ms)
        lines = ["open_time,open,high,low,close,volume"] + [f"{t},1,2,0.5,1.5,1" for t in rows]
        (k / f"BTCUSDT-1m-{ym}.csv").write_text("\n".join(lines) + "\n", newline="\n")
    return tmp_path


def test_segment_boundaries_are_adjacent_and_below_validation():
    assert X.DEV_EXT_END_MS == C.DEV_START_MS
    assert X.DEV_EXT_START_MS < X.DEV_EXT_END_MS < C.DEV_END_MS


def test_planted_dev_validation_holdout_rows_in_ext_files_are_dropped(tmp_path):
    planted = [X.DEV_EXT_END_MS, Y2024_07, Y2024_07 + 400 * 86_400_000]
    m = X.load_ext_1m(_ext_dir(tmp_path, planted))
    assert int(m["ot"].max()) < X.DEV_EXT_END_MS
    assert not set(planted) & set(m["ot"])
    assert len(m) == 12


def test_flag_off_is_the_old_loader():
    base = _bars([C.DEV_START_MS])
    base["fund_t"], base["fund_r"] = np.array([C.DEV_START_MS]), np.array([1e-4])

    def boom():
        raise AssertionError("ext read with flag off")

    assert X.load_dev_bars(False, base_loader=lambda: base, ext_loader=boom) is base


def test_flag_on_prepends_ext_and_never_returns_validation(tmp_path):
    d = _ext_dir(tmp_path, [Y2024_07])
    base = _bars([C.DEV_START_MS, C.DEV_START_MS + C.MIN5])
    base["fund_t"], base["fund_r"] = np.array([C.DEV_START_MS]), np.array([1e-4])
    out = X.load_dev_bars(True, base_loader=lambda: base, ext_loader=lambda: X.load_ext_5m(d, use_cache=False),
                          ext_funding_loader=lambda: (np.array([Y2020, Y2024_07]), np.array([2e-4, 3e-4])))
    assert int(out["ot"].max()) < Y2024_07
    assert np.all(np.diff(out["ot"]) > 0)
    assert int(out["ot"][0]) == Y2020
    assert list(out["fund_t"]) == [Y2020, C.DEV_START_MS]


def test_validation_row_from_any_loader_is_refused_or_dropped():
    with pytest.raises(ValueError):
        X.load_dev_bars(False, base_loader=lambda: _bars([Y2024_07]))
    with pytest.raises(ValueError):
        X.load_dev_bars(True, base_loader=lambda: _bars([C.DEV_START_MS, Y2024_07]),
                        ext_loader=lambda: _bars([Y2020]), ext_funding_loader=lambda: (np.array([Y2020]), np.array([0.0])))
    out = X.load_dev_bars(True, base_loader=lambda: _bars([C.DEV_START_MS]),
                          ext_loader=lambda: _bars([Y2020, X.DEV_EXT_END_MS, Y2024_07]),
                          ext_funding_loader=lambda: (np.array([Y2020]), np.array([0.0])))
    assert list(out["ot"]) == [Y2020, C.DEV_START_MS]
