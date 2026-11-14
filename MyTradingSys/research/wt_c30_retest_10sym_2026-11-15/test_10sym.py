"""Wiring tests for wt_c30_retest_10sym_2026-11-15: window constants, ten symbols, the 30m/1h resampler (aligned, complete buckets only, OHLC right),
the OOS window filter on dot closes, and the pooled-cell day cluster across symbols."""
import calendar
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("wt10_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)

M15 = 900000


def _ms(y, m, d):
    return calendar.timegm((y, m, d, 0, 0, 0)) * 1000


def test_constants_are_the_stated_dates_ten_symbols_and_family_24():
    assert study.OOS_START == _ms(2024, 1, 1) and study.SPLIT_MS == _ms(2025, 7, 1) and study.OOS_END == _ms(2026, 11, 15)
    assert len(study.SYMS) == 10 and len(set(study.SYMS)) == 10 and study.M_FAMILY == 24
    assert study.base.COST == study.rk.TAKER_RT_PCT          # shared cost model, not redefined


def _flat(t0, n, start_px=100.0):
    return [{"t": t0 + i * M15, "o": start_px + i, "h": start_px + i + 2, "l": start_px + i - 1, "c": start_px + i + 0.5} for i in range(n)]


def test_resample_1h_aligned_ohlc():
    t0 = _ms(2024, 3, 1)                       # hour aligned
    out = study.resample_from_15m(_flat(t0, 8), "1h")
    assert len(out) == 2 and out[0]["t"] == t0 and out[1]["t"] == t0 + 3600000
    assert out[0]["o"] == 100.0 and out[0]["c"] == 103.5 and out[0]["h"] == 105.0 and out[0]["l"] == 99.0


def test_resample_drops_partial_and_gapped_buckets():
    t0 = _ms(2024, 3, 1)
    bars = _flat(t0, 8)
    del bars[5]                                # second hour has a hole: dropped, never filled
    out = study.resample_from_15m(bars, "1h")
    assert [b["t"] for b in out] == [t0]
    assert len(study.resample_from_15m(_flat(t0 + M15, 7), "1h")) == 1     # misaligned start: leading partial hour dropped
    assert len(study.resample_from_15m(_flat(t0, 8), "30m")) == 4


def test_cell_trades_filters_dot_close_to_oos_and_pools_symbols_on_one_day_cluster():
    t0 = _ms(2024, 3, 1)
    bars = [{"t": t0 + i * 3600000, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0 + i} for i in range(60)]

    def ev(i, t_close):
        return {"i": i, "side": 1, "t_close": t_close, "ctx": {"side": "above", "regime": "range"}}
    inside = ev(10, t0 + 11 * 3600000)
    before = ev(11, study.OOS_START - 1)
    after = ev(12, study.OOS_END)
    per = {s: {"1h": {"bars": bars, "ev": {("buy", "rsi"): [inside, before, after]}, "tags": None}} for s in ("BTC", "ETH")}
    trs, nsig, _ = study.cell_trades(per, "1h", "buy", "rsi", "with", "signal", ["BTC", "ETH"])
    assert nsig == 2 and len(trs) == 2                  # only the in-window dot, once per symbol
    assert {x["sym"] for x in trs} == {"BTC", "ETH"} and len({x["day"] for x in trs}) == 1
    assert abs(trs[0]["gross"] - (bars[22]["c"] - bars[10]["c"]) / bars[10]["c"] * 100.0) < 1e-9     # 12 bars after the entry close
    trs2, _, _ = study.cell_trades(per, "1h", "buy", "rsi", "against", "signal", ["BTC"])
    assert trs2 == []                                    # gate "against" excludes an above-SMA buy
