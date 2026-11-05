"""Tests for c31_multi_symbol_2026-11/study.py (synthetic data only; no market files read)."""
import datetime as dt
import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
_sp = importlib.util.spec_from_file_location("c31_multi_study", HERE / "study.py")
st = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(st)


def test_load_refuses_end_past_dev():
    with pytest.raises(ValueError):
        st.load([], end=dt.date(2024, 7, 2))


def test_load_stops_at_dev_end(tmp_path):
    f = tmp_path / "X-1m-2024-06.csv"
    t_in = int(dt.datetime(2024, 6, 30, 23, 59, tzinfo=dt.timezone.utc).timestamp() * 1000)
    t_out = int(dt.datetime(2024, 7, 1, 0, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)
    f.write_text("open_time,o,h,l,c\n%d,1,2,0.5,1.5\n%d,1,2,0.5,1.5\n" % (t_in, t_out))
    k = st.load([str(f)])
    assert len(k) == 1


def test_dev_files_skip_validation_months(tmp_path):
    for name in ("ETHUSDT-1m-2024-06.csv", "ETHUSDT-1m-2024-07.csv", "ETHUSDT-1m-2026-09-25.csv"):
        (tmp_path / name).write_text("")
    got = [Path(p).name for p in st.dev_files(str(tmp_path), "ETHUSDT")]
    assert got == ["ETHUSDT-1m-2024-06.csv"]


def test_sim_short_target_and_cost():
    # entry 100, stop 110 (10 % risk), target 90: target hit = +1 R gross, net = 1 - RT_DRAG / 0.10
    hit, gross, net = st.sim(100.0, 110.0, 90.0, [(0, 100, 101, 89, 95)])
    assert hit == "TGT" and gross == pytest.approx(1.0)
    assert net == pytest.approx(1.0 - st.RT_DRAG / 0.10)
    assert st.RT_DRAG == pytest.approx(2 * st.BINANCE_TAKER * 1.2)


def test_trades_only_downtrend_edge():
    # 60 falling days then a spike close above the upper band, then a drop: one trend-down edge short
    def day(i, o, h, l, c):
        return [i, o, h, l, c, [(i * 86400, o, h, l, c)]]
    B = [day(i, 400 - 4 * i, 401 - 4 * i, 399 - 4 * i, 400 - 4 * i) for i in range(60)]
    B.append(day(60, 170, 256, 169, 255))           # close above the upper band, still under SMA50
    for i in range(61, 90):
        B.append(day(i, 230, 240, 200, 205))
    xs = st.trades(B)
    # the edge looks back 3 candles, so days 61-63 may each fire (as in c31_halves.py); none before the spike
    assert 1 <= len(xs) <= 3 and xs[0][1] == "TGT" and xs[0][2] == pytest.approx((255 - 205) / (256 - 255) * 255 / 255, rel=0.1)
    first = dt.date(1970, 1, 1) + dt.timedelta(days=61)
    assert all(first <= x[0] <= first + dt.timedelta(days=2) for x in xs)
    up = [day(i, 100 + i, 101 + i, 99 + i, 100 + i) for i in range(90)]
    assert st.trades(up) == []                       # uptrend: never traded
