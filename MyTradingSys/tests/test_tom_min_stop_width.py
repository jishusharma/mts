"""Tests for Tom v2 minimum stop width gate (noise unit N5 and fee floor).
Sources:
- TOM_LAYER_V2_SPEC.md section 11.4 (SOURCED 0.88, his 20-point stop, k0zm5NYn0IQ:22-24)
- PROJECT_VISION.md:234 (SOURCED 0.25 R fee floor: "Stops are wide enough that fees cost under 0.25 R")
- FORMULAS.md section 12 (Wilder True Range as fraction of close)
"""
import sys
sys.dont_write_bytecode = True
import os
from array import array
from datetime import date, datetime, timezone
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "dev"))
import tom_noise_units as t
from MyTradingSys.backtest.fees import FEES_ALL_TAKER, FEES_DERIBIT
from MyTradingSys.backtest.tom_bt import Bars1m, run_variant


def _make_dummy_bars1m(t0, prices):
    """prices: list of (o, h, l, c) for contiguous 1m bars."""
    o, h, l, c, v, tbv = (array("d") for _ in range(6))
    for p in prices:
        o.append(p[0])
        h.append(p[1])
        l.append(p[2])
        c.append(p[3])
        v.append(10.0)
        tbv.append(5.0)
    return Bars1m(t0, o, h, l, c, v, tbv)


@pytest.mark.parametrize('kind', ['dict', 'iterable', 'bars1m'])
def test_n5_uses_only_five_minute_bars_closed_by_asof(kind):
    # Two synthetic buckets: first H=101,L=99,C=100; second H=150,L=50,C=100.
    # Before minute 10 only bucket 0 has closed, so no TR with a prior close.
    # At minute 10, TR_1=max(150-50,abs(150-100),abs(50-100))/100=1.
    t0 = 1704067200000  # 2024-01-01T00:00:00Z, DEV synthetic timestamps
    prices = [(100., 101., 99., 100.)] * 9 + [(100., 150., 50., 100.)]
    rows = {t0 + i*60000: p for i, p in enumerate(prices)}
    bars = rows if kind == 'dict' else list(rows.items()) if kind == 'iterable' else _make_dummy_bars1m(t0, prices)
    assert t.n5(bars, asof=t0 + 9*60000 + 30000) == 0.0
    assert t.n5(bars, asof=t0 + 10*60000) == 1.0


def test_n5_iterable_future_bars_cannot_change_past():
    t0 = 1704067200000
    prices = [(100., 101., 99., 100.)] * 9 + [(100., 150., 50., 100.)]
    rows = [(t0 + i*60000, p) for i, p in enumerate(prices)]
    future = [(t0 + i*60000, (100., 10000., 1., 100.)) for i in range(10,20)]
    assert t.n5(rows, asof=t0+10*60000) == 1.0
    assert t.n5(rows+future, asof=t0+10*60000) == 1.0


def test_n5_date_means_completed_utc_day_and_requires_timestamped_asof_input():
    t0 = 1704067200000
    rows = {t0+i*60000: (100., 101., 99., 100.) for i in range(10)}
    assert t.n5(rows, asof=date(2024,1,1)) == t.n5(rows, asof=datetime(2024,1,2,tzinfo=timezone.utc))
    late = {t0+(1430+i)*60000: (100.,101.,99.,100.) for i in range(9)}
    late[t0+1439*60000] = (100.,150.,50.,100.)
    assert t.n5(late, asof=date(2024,1,1)) == 1.0
    assert t.n5(late, asof=datetime(2024,1,2,tzinfo=timezone.utc)) == 1.0
    with pytest.raises(ValueError, match='timestamp'):
        t.n5([(101.,99.,100.)]*3, asof=t0)
    with pytest.raises(ValueError, match='timezone'):
        t.n5(rows, asof=datetime(2024,1,1,0,10))


def test_worked_example():
    # 1. Formula math: entry 100000, N5 0.14 pct
    # SOURCED 0.88: TOM_LAYER_V2_SPEC.md 11.4; SOURCED 0.25 R: PROJECT_VISION.md:234
    entry = 100000.0
    n5_pct = 0.0014  # 0.14 pct
    w_noise = 0.88 * n5_pct * entry
    assert round(w_noise, 2) == 123.20

    taker_fee_rt = FEES_ALL_TAKER["entry"] + FEES_ALL_TAKER["stop"]  # 0.0005 + 0.0005 = 0.0010 (10 bps)
    taker_w_fee = (taker_fee_rt / 0.25) * entry
    assert round(taker_w_fee, 2) == 400.00

    w_min = t.min_stop_width(entry, n5_pct, FEES_ALL_TAKER)
    assert round(w_min, 2) == 400.00

    # FEES_DERIBIT: maker in (0.0), taker stop (0.0005) -> round-turn 0.05 pct on loser
    deribit_fee_rt = FEES_DERIBIT["entry"] + FEES_DERIBIT["stop"]  # 0.0005 (5 bps)
    deribit_w_fee = (deribit_fee_rt / 0.25) * entry
    assert round(deribit_w_fee, 2) == 200.00
    w_min_deribit = t.min_stop_width(entry, n5_pct, FEES_DERIBIT)
    assert round(w_min_deribit, 2) == 200.00

    # 2. bars TR 2, 2, 2.5 give n5 0.190476 (true_ranges are fractions of close)
    # FORMULAS.md section 12 worked example: closes=[9.5, 10.5, 11.5, 10]
    bars_f12 = [(10, 9, 9.5), (11, 9, 10.5), (12, 10, 11.5), (11, 9, 10)]
    got_n5 = t.n5(bars_f12)
    assert round(got_n5, 6) == 0.190476

    # 3. Stop 100399 dropped (stop_below_min_width), 100400 kept at 0.25 R
    # Create synthetic bars for simulation
    t0 = 1000000000000  # ms
    # 200 minutes of bars around 100000
    dummy_prices = [(100000.0, 100050.0, 99950.0, 100000.0)] * 200
    b = _make_dummy_bars1m(t0, dummy_prices)

    # Signal 1: stop 100399 (width 399 < 400) -> dropped
    # Signal 2: stop 100400 (width 400 >= 400) -> kept
    sig_dropped = {
        "t": t0 / 1000.0,  # seconds
        "dir": "short",
        "ztype": "15m_swing",
        "zprice": entry,
        "stop": 100399.0,
        "target": 99000.0,
        "setup": "test",
        "zone": "z1",
    }
    sig_kept = {
        "t": (t0 + 60000) / 1000.0,
        "dir": "short",
        "ztype": "15m_swing",
        "zprice": entry,
        "stop": 100400.0,
        "target": 99000.0,
        "setup": "test",
        "zone": "z2",
    }

    n5_fn = lambda asof_ms: n5_pct

    # With min_width callable
    trades = run_variant([sig_dropped], b, fees=FEES_ALL_TAKER, one_at_a_time=False, min_width=n5_fn)
    assert len(trades) == 1
    assert trades[0]["filled"] is False
    assert trades[0]["reason"] == "stop_below_min_width"

    trades_kept = run_variant([sig_kept], b, fees=FEES_ALL_TAKER, one_at_a_time=False, min_width=n5_fn)
    assert len(trades_kept) == 1
    assert trades_kept[0]["reason"] != "stop_below_min_width"
    # Check that fee at 100400 is exactly 0.25 R:
    risk = abs(entry - 100400.0)
    fee_cost = taker_fee_rt * entry
    assert fee_cost / risk == 0.25

    # 4. min_width=None = old tom_bt run
    trades_default = run_variant([sig_dropped], b, fees=FEES_ALL_TAKER, one_at_a_time=False, min_width=None)
    assert len(trades_default) == 1
    assert trades_default[0]["reason"] != "stop_below_min_width"


def test_off_by_default_identity():
    """Default min_width=None produces exact bit-identical output to calling run_variant without min_width."""
    t0 = 1000000000000
    dummy_prices = [(100000.0, 100050.0, 99950.0, 100000.0)] * 200
    b = _make_dummy_bars1m(t0, dummy_prices)
    sigs = [
        {
            "t": t0 / 1000.0,
            "dir": "short",
            "ztype": "15m_swing",
            "zprice": 100000.0,
            "stop": 100100.0,
            "target": 99500.0,
            "setup": "s1",
            "zone": "z1",
        },
        {
            "t": (t0 + 120000) / 1000.0,
            "dir": "long",
            "ztype": "5m_swing",
            "zprice": 99900.0,
            "stop": 99800.0,
            "target": 100200.0,
            "setup": "s2",
            "zone": "z2",
        },
    ]
    out_implicit = run_variant(sigs, b)
    out_explicit_none = run_variant(sigs, b, min_width=None)
    assert out_implicit == out_explicit_none
