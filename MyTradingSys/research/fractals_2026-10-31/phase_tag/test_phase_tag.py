"""Fail-first tests for phase_tag.py and harness.py (card btc-phase-context-layer-1031).

The expected values below come from reference_calc() (plain-python loops, no pandas,
no import of phase_tag) and from the arithmetic noted per case. They are never taken from phase_tag.py.
"""
import datetime as dt
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402
import phase_tag  # noqa: E402

START = dt.date(2023, 1, 2)  # a Monday


def synth(n=900):
    """close = 100+i for i<450, then falls 1 per day. Dates from 2023-01-02."""
    close = [100.0 + i if i < 450 else 549.0 - (i - 449) for i in range(n)]
    dates = [START + dt.timedelta(days=i) for i in range(n)]
    return pd.DataFrame({"date": pd.to_datetime(dates), "close": close})


def _d(x):
    return x.date() if hasattr(x, "date") else x


def reference_calc(dates, close, i):
    """Independent tag for row i, using only bars 0..i-1 (plain python, no pandas)."""
    s = i - 1
    d = _d(dates[s])
    out = {}
    hal = [dt.date(2012, 11, 28), dt.date(2016, 7, 9), dt.date(2020, 5, 11), dt.date(2024, 4, 20)]
    last = max(h for h in hal if h <= d)
    out["days_since_halving"] = (d - last).days
    out["dd_ath"] = close[s] / max(close[: s + 1]) - 1.0
    out["sma200"] = sum(close[s - 199: s + 1]) / 200 if s >= 199 else None
    out["sma400"] = sum(close[s - 399: s + 1]) / 400 if s >= 399 else None
    # completed weeks: Sunday bars whose Monday (6 bars earlier) is also in the data
    wk = []
    for j in range(s + 1):
        if _d(dates[j]).isoweekday() == 7 and j >= 6:
            wk.append(close[j])
    out["sma10w"] = sum(wk[-10:]) / 10 if len(wk) >= 10 else None
    out["sma20w"] = sum(wk[-20:]) / 20 if len(wk) >= 20 else None
    ema = None
    if len(wk) >= 21:
        ema = sum(wk[:21]) / 21
        for w in wk[21:]:
            ema = ema + (2 / 22) * (w - ema)
    out["ema21w"] = ema
    out["close"] = close[s]
    return out


# ---------- shift test (look-ahead) ----------

def test_shift_tag_at_t_ignores_bar_t_and_later():
    df = synth()
    base = phase_tag.compute_tags(df)
    rng = np.random.default_rng(1)
    for t in (50, 300, 520, 899):
        d2 = df.copy()
        d2.loc[t:, "close"] = d2.loc[t:, "close"] * rng.uniform(0.2, 5.0, size=len(d2) - t)
        alt = phase_tag.compute_tags(d2)
        pd.testing.assert_frame_equal(base.iloc[: t + 1].reset_index(drop=True), alt.iloc[: t + 1].reset_index(drop=True))


def test_shift_test_has_teeth_unshifted_version_fails():
    """The leaky version (features at close of bar t, no shift) must FAIL the same property."""
    df = synth()
    t = 300
    d2 = df.copy()
    d2.loc[t:, "close"] = d2.loc[t:, "close"] * 3.0
    a = phase_tag.features_at_close(df).iloc[t]
    b = phase_tag.features_at_close(d2).iloc[t]
    assert not a.equals(b), "unshifted features must change when bar t changes"


def test_first_row_has_no_tag():
    tags = phase_tag.compute_tags(synth())
    assert pd.isna(tags["dd_ath"].iloc[0]) and pd.isna(tags["days_since_halving"].iloc[0])


# ---------- 5 hand-computed dates ----------
# Row index i -> tag uses bars <= i-1.  Date of row i = 2023-01-02 + i days.
# Case 1 i=250: s=249 close 349, running max 349 -> dd 0. SMA200 = 100 + mean(50..249) = 249.5 -> above.
#   weeks: Sunday bars 6,13,..,244 (k=0..34), W_k = 106+7k. SMA10 = 106+7*mean(25..34) = 312.5 -> above;
#   SMA10 one week earlier 305.5 -> rising. SMA20 = 106+7*mean(15..34) = 277.5; close 349 is above SMA20 and
#   above the EMA21 -> band side above. Halving: date(s)=2023-09-08 vs 2020-05-11 -> 1095 + 120 = 1215 days.
# Case 2 i=475: date(s=474)=2024-04-20 -> first day of the epoch: 0 days. (i=474: date(s)=2024-04-19 -> 1439 days)
# Case 3 i=520: s=519 close 549-70=479, max 549 -> dd = 479/549-1 = -0.127505; days = 45.
# Case 4 i=899: s=898 close 100, dd = 100/549-1; SMA200 = mean c[699..898] = (299+100)/2 = 199.5 -> below.
# Case 5 i=700: s=699 close 299; SMA400 = mean c[300..699]: ramp c300..c449 = 400..549 (150 terms, avg 474.5 = 71175),
#   fall c450..c699 = 548..299 (250 terms, avg 423.5 = 105875); total 177050/400 = 442.625 -> close 299 below.
HAND = {
    250: dict(days=1215, dd=0.0, s200="above", w10="above_up", cowen="above"),
    474: dict(days=1439),
    475: dict(days=0),
    520: dict(days=45, dd=479 / 549 - 1.0),
    700: dict(s400="below", sma400=442.625),
    899: dict(dd=100 / 549 - 1.0, s200="below"),
}


def test_five_hand_dates_against_arithmetic():
    df = synth()
    tags = phase_tag.compute_tags(df)
    for i, exp in HAND.items():
        row = tags.iloc[i]
        if "days" in exp:
            assert row["days_since_halving"] == exp["days"], i
        if "dd" in exp:
            assert row["dd_ath"] == pytest.approx(exp["dd"], abs=1e-9), i
        if "s200" in exp:
            assert row["sma200_side"] == exp["s200"], i
        if "s400" in exp:
            assert row["sma400_side"] == exp["s400"], i
        if "sma400" in exp:
            assert row["sma400"] == pytest.approx(exp["sma400"], abs=1e-9), i
        if "w10" in exp:
            assert row["wsma10_phase"] == exp["w10"], i
        if "cowen" in exp:
            assert row["cowen_side"] == exp["cowen"], i
    assert tags["sma200"].iloc[250] == pytest.approx(249.5)
    assert tags["sma10w"].iloc[250] == pytest.approx(312.5)
    assert tags["sma20w"].iloc[250] == pytest.approx(277.5)
    assert tags["ema21w"].iloc[250] == pytest.approx(274.0)  # seed SMA(W0..W20)=176=W20-70 is the ramp steady state: EMA = W - (1-a)/a*7 = W - 70, W34=344
    assert pd.isna(tags["sma400"].iloc[250]) and pd.isna(tags["sma400_side"].iloc[250])


def test_all_rows_match_independent_reference():
    df = synth()
    tags = phase_tag.compute_tags(df)
    close = list(df["close"])
    dates = list(df["date"])
    for i in range(1, len(df), 7):
        ref = reference_calc(dates, close, i)
        row = tags.iloc[i]
        assert row["days_since_halving"] == ref["days_since_halving"]
        assert row["dd_ath"] == pytest.approx(ref["dd_ath"], abs=1e-12)
        for k in ("sma200", "sma400", "sma20w", "ema21w", "sma10w"):
            if ref[k] is None:
                assert pd.isna(row[k]), (i, k)
            else:
                assert row[k] == pytest.approx(ref[k], rel=1e-9), (i, k)
        if ref["sma200"] is not None:
            assert row["sma200_side"] == ("above" if ref["close"] > ref["sma200"] else "below")
        if ref["ema21w"] is not None:
            hi, lo = max(ref["sma20w"], ref["ema21w"]), min(ref["sma20w"], ref["ema21w"])
            want = "above" if ref["close"] > hi else ("below" if ref["close"] < lo else "inside")
            assert row["cowen_side"] == want, i


def test_partial_first_week_excluded():
    """Data starting on a Thursday: the first (partial) week must not count as a completed week."""
    df = synth(300).iloc[3:].reset_index(drop=True)
    assert df["date"].iloc[0].isoweekday() == 4
    tags = phase_tag.compute_tags(df)
    ref = reference_calc(list(df["date"]), list(df["close"]), 200)
    assert tags["sma10w"].iloc[200] == pytest.approx(ref["sma10w"], rel=1e-9)


def test_gap_in_dates_rejected():
    df = synth(100).drop(index=50).reset_index(drop=True)
    with pytest.raises(ValueError):
        phase_tag.compute_tags(df)


def test_halving_constants():
    assert phase_tag.HALVINGS_UTC[-1] == dt.datetime(2024, 4, 20, 0, 9)
    assert [h.date() for h in phase_tag.HALVINGS_UTC] == [
        dt.date(2012, 11, 28), dt.date(2016, 7, 9), dt.date(2020, 5, 11), dt.date(2024, 4, 20)]


@pytest.mark.skipif(not os.path.exists("F:/MTS/data/krown_daily/BTCUSDT_1d.csv"), reason="data file not on this machine")
def test_real_data_peak_day_534():
    d = pd.read_csv("F:/MTS/data/krown_daily/BTCUSDT_1d.csv")
    df = pd.DataFrame({"date": pd.to_datetime(d["open_time_ms"], unit="ms").dt.normalize(), "close": d["close"]})
    tags = phase_tag.compute_tags(df)
    row = tags[tags["date"] == "2025-10-07"].iloc[0]  # uses the 10-06 close = the peak close 124658.54
    assert row["days_since_halving"] == 534
    assert row["dd_ath"] == pytest.approx(0.0, abs=1e-12)


# ---------- harness ----------

def test_power_n_formula():
    # n = ((1.959964 + 0.841621) * sd / effect)^2 ; sd=1.0, effect=0.10 -> 784.9 -> 785
    assert harness.power_n(sd=1.0, effect=0.10) == 785
    # sd=2.5: (2.801585*25)^2 = 4905.4 -> 4906
    assert harness.power_n(sd=2.5, effect=0.10) == 4906


def test_inject_and_remove_roundtrip():
    rng = np.random.default_rng(3)
    out = rng.normal(0, 1, 4000)
    labels = np.repeat(np.arange(4), 1000)
    inj, mask = harness.inject_edge(out, labels, cell=2, delta=0.3, frac=0.2, rng=np.random.default_rng(4))
    assert mask.sum() == 200 and set(labels[mask]) == {2}
    assert np.allclose((inj - out)[mask], 0.3) and np.allclose((inj - out)[~mask], 0.0)
    assert np.allclose(harness.remove_edge(inj, mask, 0.3), out)


def _make(rng, n_cell, n_cells=4, sd=1.0):
    n = n_cell * n_cells
    labels = harness.block_labels(n, n_cells, mean_block=60, rng=rng)
    return rng.normal(0.0, sd, n), labels


def test_planted_edge_detected_at_stated_n_and_only_there():
    sd, delta, frac, k = 1.0, 0.3, 0.2, 4
    n_cell = harness.power_n(sd=sd, effect=delta * frac, n_cells=k)
    hits = other = 0
    reps = 150
    for r in range(reps):
        rng = np.random.default_rng(1000 + r)
        out, labels = _make(rng, n_cell, k, sd)
        inj, _ = harness.inject_edge(out, labels, cell=1, delta=delta, frac=frac, rng=rng)
        res = harness.shift_null_test(inj, labels, n_shifts=400, rng=rng)
        hits += 1 in res["flagged"]
        other += len([c for c in res["flagged"] if c != 1])
    assert 0.72 <= hits / reps <= 1.0, hits / reps
    assert other / reps <= 0.10, other / reps


def test_planted_edge_missed_at_a_fifth_of_the_n():
    sd, delta, frac, k = 1.0, 0.3, 0.2, 4
    n_cell = harness.power_n(sd=sd, effect=delta * frac, n_cells=k) // 5
    hits = 0
    for r in range(100):
        rng = np.random.default_rng(5000 + r)
        out, labels = _make(rng, n_cell, k, sd)
        inj, _ = harness.inject_edge(out, labels, cell=1, delta=delta, frac=frac, rng=rng)
        hits += 1 in harness.shift_null_test(inj, labels, n_shifts=300, rng=rng)["flagged"]
    assert hits / 100 < 0.35


def test_no_injection_stays_null():
    sd, k = 1.0, 4
    n_cell = harness.power_n(sd=sd, effect=0.06, n_cells=k)
    fp = 0
    reps = 80
    for r in range(reps):
        rng = np.random.default_rng(9000 + r)
        out, labels = _make(rng, n_cell, k, sd)
        fp += bool(harness.shift_null_test(out, labels, n_shifts=400, rng=rng)["flagged"])
    assert fp / reps <= 0.12, fp / reps


def test_default_is_1000_shifts():
    import inspect
    assert inspect.signature(harness.shift_null_test).parameters["n_shifts"].default == 1000
