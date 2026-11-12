"""Spec tests for btc_cycles_2026-11/cycles.py.

All expected values are independently derived by hand from the BTC cycle definitions
(FORMULAS.md section 25, RULE.md, cycles.md, and Bitcoin protocol consensus block heights).
"""
import csv
import datetime as dt
from pathlib import Path
import pytest

HERE = Path(__file__).resolve().parent
import cycles as C


# ---------------------------------------------------------------------------
# 1. Constants & Protocol Consensus
# ---------------------------------------------------------------------------

def test_halving_constants_match_consensus():
    """Bitcoin protocol halving block heights (210k, 420k, 630k, 840k).

    FORMULAS.md section 25: 2012-11-28, 2016-07-09, 2020-05-11, 2024-04-20 00:09 UTC.
    """
    assert C.HALVINGS == [
        dt.date(2012, 11, 28),
        dt.date(2016, 7, 9),
        dt.date(2020, 5, 11),
        dt.date(2024, 4, 20),
    ]
    assert C.BINANCE_START == dt.date(2017, 8, 17)
    # Next halving estimate at block 1,050,000 (~10 min/block): 2028-04-15
    assert C.NEXT_HALVING_EST == dt.date(2028, 4, 15)


def test_timestamp_converter_d():
    """Converts UTC epoch timestamps in seconds to dt.date."""
    # Epoch origin 1970-01-01 00:00:00 UTC
    assert C.d(0) == dt.date(1970, 1, 1)
    # Halving 4 block 840,000 instant: 2024-04-20 00:09:00 UTC = 1713571740
    assert C.d(1713571740) == dt.date(2024, 4, 20)


# ---------------------------------------------------------------------------
# 2. Extrema Locator (extreme)
# ---------------------------------------------------------------------------

def test_extreme_max_and_min():
    """extreme() selects max high or min low within inclusive date bounds [lo, hi]."""
    sample = {
        dt.date(2020, 1, 1): (100.0, 90.0, 95.0),
        dt.date(2020, 1, 2): (120.0, 85.0, 110.0),  # highest high
        dt.date(2020, 1, 3): (115.0, 70.0, 80.0),   # lowest low
        dt.date(2020, 1, 4): (150.0, 50.0, 100.0),  # outside query window
    }
    # Within 2020-01-01 .. 2020-01-03:
    p = C.extreme(sample, dt.date(2020, 1, 1), dt.date(2020, 1, 3), "max")
    assert p == (dt.date(2020, 1, 2), (120.0, 85.0, 110.0))

    b = C.extreme(sample, dt.date(2020, 1, 1), dt.date(2020, 1, 3), "min")
    assert b == (dt.date(2020, 1, 3), (115.0, 70.0, 80.0))

    # Boundary inclusive: single day query
    b_single = C.extreme(sample, dt.date(2020, 1, 2), dt.date(2020, 1, 2), "max")
    assert b_single == (dt.date(2020, 1, 2), (120.0, 85.0, 110.0))


# ---------------------------------------------------------------------------
# 3. Hand-built Synthetic Series (30 bars with known cycle peaks and bottoms)
# ---------------------------------------------------------------------------

def make_hand_built_30_bar_series():
    """Hand-built 30-bar dataset spanning 2011 to 2026.

    Each cycle contains unambiguous peaks and bottoms, plus surrounding baseline bars.
    """
    rows = {
        # Cycle 0 (pre-halving bubble 2011):
        dt.date(2011, 1, 10): (15.0, 10.0, 12.0),
        dt.date(2011, 6, 1): (40.0, 30.0, 35.0),    # C0 peak: high 40.0
        dt.date(2011, 8, 1): (25.0, 20.0, 22.0),
        dt.date(2011, 11, 1): (10.0, 2.0, 5.0),     # C0 bottom: low 2.0
        dt.date(2012, 1, 15): (8.0, 4.0, 6.0),
        dt.date(2012, 6, 1): (12.0, 5.0, 10.0),

        # Cycle 1 (Halving 2012-11-28):
        dt.date(2012, 11, 28): (15.0, 12.0, 13.0),  # halving 1 day
        dt.date(2013, 3, 1): (50.0, 40.0, 45.0),
        dt.date(2013, 11, 28): (1000.0, 850.0, 950.0),  # C1 peak: high 1000.0 (365 d from halving)
        dt.date(2014, 4, 1): (600.0, 500.0, 550.0),
        dt.date(2014, 11, 28): (300.0, 200.0, 220.0),  # C1 bottom: low 200.0 (365 d from peak)
        dt.date(2015, 6, 1): (280.0, 220.0, 250.0),

        # Cycle 2 (Halving 2016-07-09):
        dt.date(2016, 7, 9): (660.0, 640.0, 650.0),    # halving 2 day
        dt.date(2017, 1, 1): (1000.0, 900.0, 950.0),
        dt.date(2017, 12, 1): (20000.0, 18000.0, 19000.0),  # C2 peak: high 20000.0 (510 d from halving)
        dt.date(2018, 5, 1): (10000.0, 8000.0, 9000.0),
        dt.date(2018, 12, 1): (4000.0, 3000.0, 3500.0),      # C2 bottom: low 3000.0 (365 d from peak)
        dt.date(2019, 6, 1): (9000.0, 7000.0, 8000.0),

        # Cycle 3 (Halving 2020-05-11):
        dt.date(2020, 5, 11): (9000.0, 8500.0, 8800.0),  # halving 3 day
        dt.date(2021, 1, 1): (30000.0, 28000.0, 29000.0),
        dt.date(2021, 11, 10): (60000.0, 55000.0, 58000.0),  # C3 peak: high 60000.0 (548 d from halving)
        dt.date(2022, 5, 1): (40000.0, 35000.0, 38000.0),
        dt.date(2022, 11, 20): (20000.0, 15000.0, 16000.0),  # C3 bottom: low 15000.0 (375 d from peak)
        dt.date(2023, 6, 1): (30000.0, 25000.0, 28000.0),

        # Cycle 4 (Halving 2024-04-20):
        dt.date(2024, 4, 20): (65000.0, 63000.0, 64000.0),  # halving 4 day
        dt.date(2025, 1, 1): (95000.0, 90000.0, 92000.0),
        dt.date(2025, 10, 6): (120000.0, 110000.0, 115000.0),  # C4 peak: high 120000.0 (534 d from halving)
        dt.date(2026, 2, 1): (90000.0, 80000.0, 85000.0),
        dt.date(2026, 7, 1): (65000.0, 50000.0, 55000.0),   # C4 bottom: low 50000.0 (268 d from peak)
        dt.date(2026, 11, 1): (75000.0, 72000.0, 74000.0),  # today bar
    }
    assert len(rows) == 30
    return dict(sorted(rows.items()))


def test_build_on_hand_built_series():
    """Verify all fields across cycles 0..4 against exact hand-worked numbers."""
    rows = make_hand_built_30_bar_series()
    out, today = C.build(rows)

    assert today == dt.date(2026, 11, 1)
    assert len(out) == 5

    # ------------------ Cycle 0 ------------------
    c0 = out[0]
    assert c0["cycle"] == 0
    assert c0["halving"] == ""
    assert c0["peak_date"] == dt.date(2011, 6, 1)
    assert c0["peak"] == 40.0
    assert c0["bottom_date"] == dt.date(2011, 11, 1)
    assert c0["bottom"] == 2.0
    assert c0["halving_to_peak_d"] == ""
    assert c0["peak_to_bottom_d"] == (dt.date(2011, 11, 1) - dt.date(2011, 6, 1)).days  # 153 d
    assert c0["peak_to_bottom_d"] == 153
    # Drawdown: (2.0 / 40.0 - 1) * 100 = -95.0%
    assert c0["drawdown_pct"] == -95.0
    assert c0["prev_bottom_to_peak_d"] == ""
    assert c0["prev_bottom_to_peak_x"] == ""
    assert c0["bottom_to_bottom_d"] == ""
    assert c0["bottom_is_final"] is True
    # bottom to next halving (Cycle 1 halving: 2012-11-28)
    assert c0["bottom_to_next_halving_d"] == (dt.date(2012, 11, 28) - dt.date(2011, 11, 1)).days  # 393 d
    assert c0["bottom_to_next_halving_d"] == 393

    # ------------------ Cycle 1 ------------------
    c1 = out[1]
    assert c1["cycle"] == 1
    assert c1["halving"] == dt.date(2012, 11, 28)
    assert c1["peak_date"] == dt.date(2013, 11, 28)
    assert c1["peak"] == 1000.0
    assert c1["bottom_date"] == dt.date(2014, 11, 28)
    assert c1["bottom"] == 200.0
    assert c1["halving_to_peak_d"] == (dt.date(2013, 11, 28) - dt.date(2012, 11, 28)).days  # 365 d
    assert c1["peak_to_bottom_d"] == (dt.date(2014, 11, 28) - dt.date(2013, 11, 28)).days  # 365 d
    # Drawdown: (200.0 / 1000.0 - 1) * 100 = -80.0%
    assert c1["drawdown_pct"] == -80.0
    assert c1["prev_bottom_to_peak_d"] == (dt.date(2013, 11, 28) - dt.date(2011, 11, 1)).days  # 758 d
    assert c1["prev_bottom_to_peak_d"] == 758
    assert c1["prev_bottom_to_peak_x"] == round(1000.0 / 2.0, 1)  # 500.0x
    assert c1["prev_bottom_to_peak_x"] == 500.0
    assert c1["bottom_to_bottom_d"] == (dt.date(2014, 11, 28) - dt.date(2011, 11, 1)).days  # 1123 d
    assert c1["bottom_to_bottom_d"] == 1123
    assert c1["bottom_is_final"] is True
    assert c1["bottom_to_next_halving_d"] == (dt.date(2016, 7, 9) - dt.date(2014, 11, 28)).days  # 589 d
    assert c1["bottom_to_next_halving_d"] == 589

    # ------------------ Cycle 2 ------------------
    c2 = out[2]
    assert c2["cycle"] == 2
    assert c2["halving"] == dt.date(2016, 7, 9)
    assert c2["peak_date"] == dt.date(2017, 12, 1)
    assert c2["peak"] == 20000.0
    assert c2["bottom_date"] == dt.date(2018, 12, 1)
    assert c2["bottom"] == 3000.0
    assert c2["halving_to_peak_d"] == (dt.date(2017, 12, 1) - dt.date(2016, 7, 9)).days  # 510 d
    assert c2["peak_to_bottom_d"] == 365
    # Drawdown: (3000.0 / 20000.0 - 1) * 100 = -85.0%
    assert c2["drawdown_pct"] == -85.0
    assert c2["prev_bottom_to_peak_d"] == (dt.date(2017, 12, 1) - dt.date(2014, 11, 28)).days  # 1099 d
    assert c2["prev_bottom_to_peak_x"] == round(20000.0 / 200.0, 1)  # 100.0x
    assert c2["bottom_to_bottom_d"] == (dt.date(2018, 12, 1) - dt.date(2014, 11, 28)).days  # 1464 d
    assert c2["bottom_is_final"] is True
    assert c2["bottom_to_next_halving_d"] == (dt.date(2020, 5, 11) - dt.date(2018, 12, 1)).days  # 527 d
    assert c2["bottom_to_next_halving_d"] == 527

    # ------------------ Cycle 3 ------------------
    c3 = out[3]
    assert c3["cycle"] == 3
    assert c3["halving"] == dt.date(2020, 5, 11)
    assert c3["peak_date"] == dt.date(2021, 11, 10)
    assert c3["peak"] == 60000.0
    assert c3["bottom_date"] == dt.date(2022, 11, 20)
    assert c3["bottom"] == 15000.0
    assert c3["halving_to_peak_d"] == (dt.date(2021, 11, 10) - dt.date(2020, 5, 11)).days  # 548 d
    assert c3["peak_to_bottom_d"] == (dt.date(2022, 11, 20) - dt.date(2021, 11, 10)).days  # 375 d
    # Drawdown: (15000.0 / 60000.0 - 1) * 100 = -75.0%
    assert c3["drawdown_pct"] == -75.0
    assert c3["prev_bottom_to_peak_d"] == (dt.date(2021, 11, 10) - dt.date(2018, 12, 1)).days  # 1075 d
    assert c3["prev_bottom_to_peak_x"] == round(60000.0 / 3000.0, 1)  # 20.0x
    assert c3["bottom_to_bottom_d"] == (dt.date(2022, 11, 20) - dt.date(2018, 12, 1)).days  # 1450 d
    assert c3["bottom_is_final"] is True
    assert c3["bottom_to_next_halving_d"] == (dt.date(2024, 4, 20) - dt.date(2022, 11, 20)).days  # 517 d
    assert c3["bottom_to_next_halving_d"] == 517

    # ------------------ Cycle 4 ------------------
    c4 = out[4]
    assert c4["cycle"] == 4
    assert c4["halving"] == dt.date(2024, 4, 20)
    assert c4["peak_date"] == dt.date(2025, 10, 6)
    assert c4["peak"] == 120000.0
    assert c4["bottom_date"] == dt.date(2026, 7, 1)
    assert c4["bottom"] == 50000.0
    assert c4["halving_to_peak_d"] == (dt.date(2025, 10, 6) - dt.date(2024, 4, 20)).days  # 534 d
    assert c4["peak_to_bottom_d"] == (dt.date(2026, 7, 1) - dt.date(2025, 10, 6)).days  # 268 d
    # Drawdown: (50000.0 / 120000.0 - 1) * 100 = -58.333... -> -58.3%
    assert c4["drawdown_pct"] == -58.3
    assert c4["prev_bottom_to_peak_d"] == (dt.date(2025, 10, 6) - dt.date(2022, 11, 20)).days  # 1051 d
    assert c4["prev_bottom_to_peak_x"] == round(120000.0 / 15000.0, 1)  # 8.0x
    assert c4["bottom_to_bottom_d"] == (dt.date(2026, 7, 1) - dt.date(2022, 11, 20)).days  # 1319 d
    # 2026-07-01 < 2026-11-01 - 60 days (2026-09-02) -> bottom_is_final is True
    assert c4["bottom_is_final"] is True
    # Next halving estimate: 2028-04-15
    assert c4["bottom_to_next_halving_d"] == (dt.date(2028, 4, 15) - dt.date(2026, 7, 1)).days  # 654 d
    assert c4["bottom_to_next_halving_d"] == 654


# ---------------------------------------------------------------------------
# 4. Edge Cases: bottom_is_final 60-day rule
# ---------------------------------------------------------------------------

def test_bottom_is_final_boundary_rule():
    """c['bottom_is_final'] = c['bottom_date'] < today - dt.timedelta(days=60)."""
    rows = make_hand_built_30_bar_series()
    # Add a newer, lower bottom within 60 days of today (e.g., 2026-10-15 when today is 2026-11-01: 17 days ago)
    rows[dt.date(2026, 10, 15)] = (45000.0, 30000.0, 35000.0)
    out, today = C.build(rows)
    c4 = out[4]
    assert c4["bottom_date"] == dt.date(2026, 10, 15)
    assert c4["bottom"] == 30000.0
    # 2026-10-15 is NOT < 2026-11-01 - 60 days (2026-09-02)
    assert c4["bottom_is_final"] is False


# ---------------------------------------------------------------------------
# 5. Golden Historical Dataset Regression (btc_daily.csv)
# ---------------------------------------------------------------------------

def test_real_historical_dataset_against_golden_cycles():
    """Verifies that cycles.py reproduces all verified numbers from cycles.csv / cycles.md.

    Source: btc_daily.csv (5925 daily rows).
    """
    btc_daily = HERE / "btc_daily.csv"
    if not btc_daily.exists():
        pytest.skip("btc_daily.csv not present in test directory")

    rows = {}
    with open(btc_daily, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            y, m, day = (int(x) for x in r["date"].split("-"))
            rows[dt.date(y, m, day)] = (float(r["high"]), float(r["low"]), float(r["close"]))

    out, today = C.build(rows)
    assert today == dt.date(2026, 11, 6)
    assert len(out) == 5

    # Match exact golden numbers from cycles.csv:
    # Cycle 0
    assert out[0]["peak_date"] == dt.date(2011, 6, 11) and out[0]["peak"] == 33.8
    assert out[0]["bottom_date"] == dt.date(2011, 11, 22) and out[0]["bottom"] == 2.3
    assert out[0]["peak_to_bottom_d"] == 164 and out[0]["drawdown_pct"] == -93.2

    # Cycle 1
    assert out[1]["peak_date"] == dt.date(2013, 12, 5) and out[1]["peak"] == 1136.9
    assert out[1]["bottom_date"] == dt.date(2015, 1, 15) and out[1]["bottom"] == 172.0
    assert out[1]["halving_to_peak_d"] == 372 and out[1]["peak_to_bottom_d"] == 406
    assert out[1]["drawdown_pct"] == -84.9
    assert out[1]["prev_bottom_to_peak_d"] == 744 and out[1]["prev_bottom_to_peak_x"] == 494.3

    # Cycle 2
    assert out[2]["peak_date"] == dt.date(2017, 12, 17) and out[2]["peak"] == 19798.68
    assert out[2]["bottom_date"] == dt.date(2018, 12, 15) and out[2]["bottom"] == 3156.26
    assert out[2]["halving_to_peak_d"] == 526 and out[2]["peak_to_bottom_d"] == 363
    assert out[2]["drawdown_pct"] == -84.1
    assert out[2]["prev_bottom_to_peak_d"] == 1067 and out[2]["prev_bottom_to_peak_x"] == 115.1

    # Cycle 3
    assert out[3]["peak_date"] == dt.date(2021, 11, 10) and out[3]["peak"] == 69000.0
    assert out[3]["bottom_date"] == dt.date(2022, 11, 21) and out[3]["bottom"] == 15476.0
    assert out[3]["halving_to_peak_d"] == 548 and out[3]["peak_to_bottom_d"] == 376
    assert out[3]["drawdown_pct"] == -77.6
    assert out[3]["prev_bottom_to_peak_d"] == 1061 and out[3]["prev_bottom_to_peak_x"] == 21.9

    # Cycle 4
    assert out[4]["peak_date"] == dt.date(2025, 10, 6) and out[4]["peak"] == 126199.63
    assert out[4]["bottom_date"] == dt.date(2026, 7, 1) and out[4]["bottom"] == 57800.19
    assert out[4]["halving_to_peak_d"] == 534 and out[4]["peak_to_bottom_d"] == 268
    assert out[4]["drawdown_pct"] == -54.2
    assert out[4]["prev_bottom_to_peak_d"] == 1050 and out[4]["prev_bottom_to_peak_x"] == 8.2
    assert out[4]["bottom_to_next_halving_d"] == 654


# ---------------------------------------------------------------------------
# 6. File Writer Test (write)
# ---------------------------------------------------------------------------

def test_write_creates_expected_artifacts(tmp_path, monkeypatch):
    """write() creates btc_daily.csv, cycles.csv, and cycles.md with matching schemas."""
    monkeypatch.setattr(C, "HERE", tmp_path)
    rows = make_hand_built_30_bar_series()
    out, today = C.build(rows)
    C.write(out, rows, today)

    assert (tmp_path / "btc_daily.csv").exists()
    assert (tmp_path / "cycles.csv").exists()
    assert (tmp_path / "cycles.md").exists()

    with open(tmp_path / "cycles.csv", newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 5
        assert reader[0]["cycle"] == "0"
        assert reader[4]["cycle"] == "4"

    md_content = (tmp_path / "cycles.md").read_text(encoding="utf-8")
    assert "# BTC cycles" in md_content
    assert "## Cycle 4 now" in md_content
