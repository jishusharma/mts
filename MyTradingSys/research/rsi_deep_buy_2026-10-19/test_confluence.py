"""Tests for confluence.py (RSI deep-buy Step H). Synthetic data only; expected numbers are hand computed
(see comments; Bollinger from FORMULAS.md s22), never taken from the module."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import confluence as cf  # noqa: E402

MIN = 60_000
T0 = int(np.datetime64("2023-03-01T00:00", "ms").astype("int64"))


def _synthetic_1m(n=14 * 1440, seed=7, change_from=None):
    rng = np.random.default_rng(seed)
    close = 20000 * np.exp(np.cumsum(rng.normal(0, 0.0015, n)))
    open_ = np.r_[close[0], close[:-1]]
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.0004, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.0004, n)))
    vol = rng.uniform(50, 150, n)
    tbv = vol * rng.uniform(0.3, 0.7, n)
    t = T0 + np.arange(n) * MIN
    if change_from is not None:                       # plant a different future: bars opening at or after change_from
        m = t >= change_from
        k = int(m.sum())
        rng2 = np.random.default_rng(99)
        close2 = close[~m][-1] * np.exp(np.cumsum(rng2.normal(-0.004, 0.003, k)))
        open2 = np.r_[close[~m][-1], close2[:-1]]
        close[m], open_[m] = close2, open2
        high[m] = np.maximum(open2, close2) * 1.002
        low[m] = np.minimum(open2, close2) * 0.998
        vol[m] = 400.0
        tbv[m] = 50.0
    return {"open_time": t, "open": open_, "high": high, "low": low, "close": close, "volume": vol, "taker_buy_volume": tbv}


def _votes(d1, tfs):
    dayd = cf.ef.resample({k: d1[k] for k in ("open_time", "open", "high", "low", "close")}, 1440)
    dayl = (dayd["open_time"], dayd["high"], dayd["low"])
    return {tf: cf.tf_votes(d1, tf, dayl) for tf in tfs}


def test_higher_tf_vote_uses_last_completed_bar_only():
    d1 = _synthetic_1m()
    base_tf = 5
    tfv = _votes(d1, (5, 15, 60))
    bd = tfv[5][0]
    # event bar: signal close is NOT a multiple of 15 or 60 minutes, so the 15m and 1h bars are still forming
    i0 = next(i for i in range(2900, 3300) if ((bd["open_time"][i] + 5 * MIN) // MIN) % 15 not in (0,)
              and ((bd["open_time"][i] + 5 * MIN) // MIN) % 60 not in (0,))
    signal_close = int(bd["open_time"][i0] + 5 * MIN)
    ev = np.array([i0])
    same1, high1 = cf.event_votes(base_tf, ev, bd, tfv)
    d2 = _synthetic_1m(change_from=signal_close)      # planted change in the CURRENT higher-TF bars (after the signal close)
    assert (d2["open_time"] == d1["open_time"]).all() and not np.array_equal(d1["close"], d2["close"])
    tfv2 = _votes(d2, (5, 15, 60))
    same2, high2 = cf.event_votes(base_tf, ev, tfv2[5][0], tfv2)
    for k in high1:
        np.testing.assert_array_equal(high1[k], high2[k])
    for k in same1:
        np.testing.assert_array_equal(same1[k], same2[k])
    s1, s2 = cf.scheme_states(same1, high1), cf.scheme_states(same2, high2)
    for k in s1:
        assert s1[k].tolist() == s2[k].tolist()
    assert all(np.isfinite(v).all() for v in high1.values())


def test_completed_index_hand_example():
    # 5m signal bar opens 10:05 (closes 10:10); 15m bars open 09:45, 10:00, 10:15 -> the 10:00 bar is still forming, 09:45 completed
    hopen = np.array([9 * 60 + 45, 10 * 60, 10 * 60 + 15]) * MIN
    ix = cf.htf_completed_index(np.array([(10 * 60 + 5) * MIN]), 5 * MIN, hopen, 15 * MIN)
    assert ix.tolist() == [0]
    # signal bar opens 10:10, closes 10:15 -> the 10:00 bar completes exactly at the signal close: completed index 1
    ix = cf.htf_completed_index(np.array([(10 * 60 + 10) * MIN]), 5 * MIN, hopen, 15 * MIN)
    assert ix.tolist() == [1]


def test_layer_without_history_is_not_in_data_never_zero():
    assert cf.layer_status("wavetrend") == "NOT_IN_DATA"
    assert cf.layer_status("oscillator_agreement_count") == "NOT_IN_DATA"
    assert cf.layer_status("V_BB") == "voter"
    # a voter with no history yet (series shorter than its window) reports NaN, not 0
    v = cf.vote_bb(np.arange(10, dtype=float))
    assert np.isnan(v).all()
    assert np.isnan(cf.vote_rsi([np.nan, np.nan])).all()
    # a score with a non-reporting voter is NaN, never the sum of the others
    s = cf.score_votes([1, np.nan, -1])
    assert np.isnan(s)
    st = cf.scheme_states({k: np.array([0.0]) for k in cf.SAME_VOTERS},
                          {**{k: np.array([0.0]) for k in cf.HIGH_VOTERS}, "V_DIV": np.array([np.nan])})
    assert all(v.tolist() == [-1] for v in st.values())


def test_score_equals_hand_count_three_voters():
    # votes +1, +1, -1 -> (2 plus) - (1 minus) = 1
    assert cf.score_votes([1, 1, -1]) == 1.0
    assert cf.score_votes([-1, -1, 0]) == -2.0
    assert cf.score_votes([0, 0, 0]) == 0.0          # a real zero is a reading, distinct from NaN
    assert cf.bucket_same([-3, -1, 0, 1, 2, 4]).tolist() == [0, 0, 1, 2, 3, 3]
    assert cf.bucket_total([-5, -1, 0, 1, 2, 3, 12]).tolist() == [0, 0, 1, 2, 2, 3, 3]
    assert cf.bucket_sign([-2, 0, 3]).tolist() == [0, 1, 2]


def test_scheme_states_hand_example():
    same = {"V_BB": np.array([1.0]), "V_KUR": np.array([1.0]), "V_TAK": np.array([0.0]), "V_SWP": np.array([-1.0])}   # S = 1
    high = {"V_RSI": np.array([2.0]), "V_BB": np.array([0.0]), "V_KUR": np.array([1.0]), "V_TAK": np.array([-1.0]),
            "V_SWP": np.array([0.0]), "V_DIV": np.array([1.0])}                                                          # H = 3
    st = cf.scheme_states(same, high)
    assert st["C_same"].tolist() == [2]               # S = 1
    assert st["C_high"].tolist() == [3]               # H = 3
    assert st["C_all"].tolist() == [3]                # T = 4
    # V_RSI total = 2 -> state 2 ; V_BB total = 1 + 0 = 1 -> 2 ; V_SWP total = -1 + 0 = -1 -> 0
    assert st["ADD1_V_RSI"].tolist() == [2] and st["ADD1_V_SWP"].tolist() == [0]
    # drop V_RSI: T = 4 - 2 = 2 -> bucket 2 ; drop V_KUR (total 2): 2 -> 2 ; drop V_SWP (-1): 5 -> 3
    assert st["DROP1_V_RSI"].tolist() == [2] and st["DROP1_V_SWP"].tolist() == [3]


def test_bollinger_hand_example_formulas_s22():
    # FORMULAS s22 style, n=4, mult=1 (n=4 cannot breach 2 sd): last window [10,10,10,20] mean 12.5, population var
    # (3*2.5^2 + 7.5^2)/4 = 18.75, sd 4.330127 ; upper = 16.830127 < 20 -> -1 ; window [10,10,10,0]: mean 7.5, lower 3.169873 > 0 -> +1
    assert cf.vote_bb([10, 10, 10, 20], n=4, mult=1.0).tolist()[-1] == -1.0
    assert cf.vote_bb([10, 10, 10, 0], n=4, mult=1.0).tolist()[-1] == 1.0
    assert cf.vote_bb([10, 10, 10, 10], n=4, mult=1.0).tolist()[-1] == 0.0       # sd 0: on the band, neither side
    # first three entries lack history
    assert np.isnan(cf.vote_bb([10, 10, 10, 20], n=4, mult=1.0)[:3]).all()


def test_taker_vote_hand_example():
    # previous 4 shares .4 .6 .4 .6: mean .5, population sd .1 ; share .9 -> z = 4 -> +1 ; .5 -> 0 ; .1 -> -4 -> -1 ; flat history -> NA
    assert cf.vote_taker([.4, .6, .4, .6, .9], win=4)[-1] == 1.0
    assert cf.vote_taker([.4, .6, .4, .6, .5], win=4)[-1] == 0.0
    assert cf.vote_taker([.4, .6, .4, .6, .1], win=4)[-1] == -1.0
    assert np.isnan(cf.vote_taker([.5, .5, .5, .5, .9], win=4)[-1])


def test_sweep_vote_and_prior_day():
    day = 86_400_000
    d_open = np.array([0, day, 2 * day])
    pdl, pdh = cf.prior_day_levels(np.array([2 * day + 5 * MIN, 5 * MIN]), d_open, np.array([110., 120., 130.]), np.array([90., 95., 100.]))
    assert pdl[0] == 95.0 and pdh[0] == 120.0          # bar on day 2 sees day 1
    assert np.isnan(pdl[1]) and np.isnan(pdh[1])       # bar on day 0 has no prior day
    # low 94 < PDL 95 and close 96 > 95 -> +1 ; high 121 > 120, close 119 < 120 -> -1 ; inside -> 0 ; no prior -> NaN
    v = cf.vote_sweep([100, 121, 100, 100], [94, 100, 99, 94], [96, 119, 100, 96], [95, 95, 95, np.nan], [120, 120, 120, 120])
    assert v[:3].tolist() == [1.0, -1.0, 0.0] and np.isnan(v[3])


def _div_example(n=60):
    close = np.full(n, 60.0)
    rsi = np.full(n, 50.0)
    close[10], rsi[10] = 50.0, 20.0                    # first price low, RSI 20
    close[20], rsi[20] = 45.0, 30.0                    # lower price low, higher RSI low -> bullish divergence
    return close, rsi


def test_divergence_stamped_at_confirmation_and_window_20():
    close, rsi = _div_example()
    sig = cf.div_signals(close, rsi)
    assert np.flatnonzero(sig).tolist() == [23] and sig[23] == 1.0       # pivot 20 + 3 confirmation bars
    v = cf.vote_div(close, rsi)
    assert v[22] == 0.0 and v[23] == 1.0 and v[42] == 1.0 and v[43] == 0.0   # active for 20 bars: 23..42
    # planting a future change after the stamp bar leaves the vote at and before the stamp unchanged
    c2 = close.copy(); c2[24:] = 10.0
    v2 = cf.vote_div(c2, rsi)
    assert v2[:24].tolist() == v[:24].tolist()
    # bearish mirror: higher price high with lower RSI high
    c3, r3 = 100 - close, 100 - rsi
    assert cf.vote_div(c3, r3)[23] == -1.0


def test_load_klines_refuses_bars_at_cutoff(tmp_path):
    p = tmp_path / "BTCUSDT-1m-2024-07.csv"
    p.write_text("open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
                 "1719792000000,1,1,1,1,1,0,0,0,1,0,0\n")
    with pytest.raises(ValueError):
        cf.load_klines([p], cf.ef.CUTOFF_MS)
