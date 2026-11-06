"""MA state contract (ma_state.py). Expected numbers are hand-computed in the comments, never taken from the code."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ma_state as M  # noqa: E402


def kl(i, o, h, l, c):
    return [i * 60000, str(o), str(h), str(l), str(c), "1", i * 60000 + 59999, "0", 1, "0.5", "0", "0"]


def flat_then_jump(n_flat=299):
    """299 bars at close 100 (high 101, low 99, so TR = 2) then one forming bar o100 h111 l99 c110."""
    bars = [kl(i, 100, 101, 99, 100) for i in range(n_flat)]
    bars.append(kl(n_flat, 100, 111, 99, 110))
    return bars


def ramp(final):
    """closes 1..299 (h=c+1, l=c-1, TR = 2) then the forming bar `final` = (o,h,l,c)."""
    bars = [kl(i, c, c + 1, c - 1, c) for i, c in enumerate(range(1, 300))]
    bars.append(kl(299, *final))
    return bars


def test_sma_hand_computed_on_a_ramp():
    # closes 1..200: sma200 = 201/2 = 100.5; sma50 = mean(151..200) = 175.5; sma20 = mean(181..200) = 190.5
    c = [float(x) for x in range(1, 201)]
    assert M.sma_series(c, 200)[-1] == pytest.approx(100.5)
    assert M.sma_series(c, 50)[-1] == pytest.approx(175.5)
    assert M.sma_series(c, 20)[-1] == pytest.approx(190.5)
    assert M.sma_series(c, 200)[198] is None  # 199 closes: no average yet


def test_ema_alpha_and_seed():
    # [10,10,10,20], n=3: seed mean(10,10,10)=10 at index 2; alpha 2/4=0.5 -> 10 + 0.5*(20-10) = 15
    out = M.ema_series([10.0, 10.0, 10.0, 20.0], 3)
    assert out[:2] == [None, None] and out[2] == 10 and out[3] == pytest.approx(15)


def test_jump_row_all_numbers():
    r = M.ma_row("1h", flat_then_jump())
    a = r["avgs"]
    # 299 closes of 100 then 110. ema_N = 100 + 2/(N+1)*10: ema21 100.90909, ema55 100.35714, ema200 100.09950
    assert a["ema21"]["v"] == pytest.approx(100 + 20 / 22)
    assert a["ema55"]["v"] == pytest.approx(100 + 20 / 56)
    assert a["ema200"]["v"] == pytest.approx(100 + 20 / 201)
    # sma200 = (199*100+110)/200 = 100.05; sma50 = (49*100+110)/50 = 100.2; sma20 = (19*100+110)/20 = 100.5
    assert a["sma200"]["v"] == pytest.approx(100.05)
    assert a["sma50"]["v"] == pytest.approx(100.2)
    assert a["sma20"]["v"] == pytest.approx(100.5)
    # distPct to ema21 = 100*(110-100.90909)/100.90909 = 9.00901; ATR14 = 2 (14 closed bars of TR 2); distAtr = 9.09091/2 = 4.54545
    assert r["atr"] == pytest.approx(2.0)
    assert a["ema21"]["distPct"] == pytest.approx(9.00901, abs=1e-4)
    assert a["ema21"]["distAtr"] == pytest.approx(4.545455, abs=1e-5)
    # Mayer-style ratio price / sma200 = 110/100.05 = 1.099450
    assert a["sma200"]["ratio"] == pytest.approx(1.099450, abs=1e-6)
    assert all(a[k]["side"] == "above" for k in a)
    # ema21 moved 0.909 in 5 bars (< 0.5 ATR = 1): flat. First non-tie state is up with no earlier state: no cross yet
    assert a["ema21"]["slope"] == "flat"
    assert r["cross2155"] == {"state": "up", "barsSince": None}
    assert r["cross50200"] == {"state": "up", "barsSince": None}
    assert r["band"] == "above" and r["pullback"] is None  # ema55 slope flat: no trend, no pullback flag


def test_pullback_up_in_a_ramp_trend():
    # ramp: ema_N = close - (N-1)/2 exactly (seed mean of a ramp). Before the forming bar ema21 289, ema55 272.
    # forming close 285: ema21 = 289 + (2/22)*(285-289) = 288.63636; ema55 = 272 + (2/56)*13 = 272.46429
    r = M.ma_row("15m", ramp((299, 300, 283, 285)))
    assert r["avgs"]["ema21"]["v"] == pytest.approx(288.636364, abs=1e-5)
    assert r["avgs"]["ema55"]["v"] == pytest.approx(272.464286, abs=1e-5)
    assert r["avgs"]["ema55"]["slope"] == "up"  # 272.464 - 268 = 4.46 > 0.5 * ATR 2
    # low 283 <= 288.636 + 0.25*2 and close 285 >= ema55 272.46 -> pullback up
    assert r["pullback"] == "up"
    # sma200 = (sum 101..299 + 285)/200 = (39800 + 285)/200 = 200.425
    assert r["avgs"]["sma200"]["v"] == pytest.approx(200.425)


def test_no_pullback_when_the_low_stays_away_from_the_21():
    # forming o299 h301 l298 c300: ema21 = 289 + 11/11 = 290; low 298 > 290 + 0.5 -> no pullback
    assert M.ma_row("15m", ramp((299, 301, 298, 300)))["pullback"] is None


def test_no_pullback_when_close_is_through_the_55():
    # forming o299 h300 l250 c260: ema55 = 272 + (2/56)*(260-272) = 271.57 > close 260 -> broken through, no pullback
    assert M.ma_row("15m", ramp((299, 300, 250, 260)))["pullback"] is None


def test_pullback_down_is_the_mirror():
    # price' = 1000 - price: ema21 711.63636 hmm 1000-288.63636 = 711.36364, ema55 727.53571; forming h717 l700 c715
    bars = [kl(i, 1000 - c, 1000 - c + 1, 1000 - c - 1, 1000 - c) for i, c in enumerate(range(1, 300))]
    bars.append(kl(299, 701, 717, 700, 715))
    r = M.ma_row("15m", bars)
    assert r["avgs"]["ema21"]["v"] == pytest.approx(711.363636, abs=1e-5)
    assert r["pullback"] == "down"  # ema21 < ema55, ema55 slope down, high 717 >= 711.36 - 0.5, close 715 <= 727.5


def test_cross_state_hand_series():
    # fast 1,2,3,2,1 vs slow 2: down(i0), tie(i1, skipped), up(i2: change), tie(i3), down(i4: change) -> down, 0 bars since
    assert M.cross_state([1, 2, 3, 2, 1], [2] * 5) == {"state": "down", "barsSince": 0}
    # 1,3,3,3 vs 2: down at i0, up at i1 (change), n=4 -> barsSince = 4-1-1 = 2
    assert M.cross_state([1, 3, 3, 3], [2] * 4) == {"state": "up", "barsSince": 2}
    assert M.cross_state([None, 3, 3, 3], [None, 1, 1, 1]) == {"state": "up", "barsSince": None}
    assert M.cross_state([None, None], [None, None]) == {"state": None, "barsSince": None}


def test_fail_closed_short_history_and_bad_data():
    short = [kl(i, 100, 101, 99, 100) for i in range(60)]
    r = M.ma_row("1M", short)
    assert r["avgs"]["sma200"] is None and r["avgs"]["ema200"] is None
    assert r["avgs"]["ema55"] is not None and r["cross50200"] == {"state": None, "barsSince": None}
    assert M.atr14(short[:15]) is None and M.atr14(short[:16]) is not None
    assert M.ma_row("1d", short[:1]) is None
    bad = list(short)
    bad[10] = bad[10][:4] + ["x"] + bad[10][5:]
    assert M.ma_row("1d", bad) is None


def test_state_rows_follow_timeframe_order_and_missing_is_none():
    rows = M.ma_state({"1h": flat_then_jump()})
    assert [x["tf"] if x else None for x in rows] == [None, None, "1h", None, None, None, None]
    assert M.TFS == ["5m", "15m", "1h", "4h", "1d", "1w", "1M"]
