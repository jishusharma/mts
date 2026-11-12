"""Cycle MA clock contract (cycle_ma_clock.py). Expected numbers are hand-computed in comments, never taken from the code."""
import datetime as dt
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cycle_ma_clock as C  # noqa: E402


def make_daily_rows(start_date, n_days, price_fn):
    """Build (date, low, close) rows for n_days consecutive calendar days."""
    rows = []
    for i in range(n_days):
        d = start_date + dt.timedelta(days=i)
        low, close = price_fn(i, d)
        rows.append((d, float(low), float(close)))
    return rows


def test_mean_last_formulas_md_s3():
    # FORMULAS.md s3 worked example: length=3, [50, 55, 45] -> 50.0
    assert C.mean_last([50.0, 55.0, 45.0], 3) == pytest.approx(50.0)
    # Tail window only: last 2 of [10, 20, 30, 40] -> (30 + 40) / 2 = 35.0
    assert C.mean_last([10.0, 20.0, 30.0, 40.0], 2) == pytest.approx(35.0)
    # Insufficient history -> None
    assert C.mean_last([10.0, 20.0], 3) is None
    assert C.mean_last([], 1) is None


def test_clocks_fail_closed_when_history_short():
    # 199 daily bars: < 200 days, < 200 weeks, < 20 months -> all three SMAs None
    start = dt.date(2020, 1, 6)  # Monday
    rows = make_daily_rows(start, 199, lambda i, _: (100.0, 100.0 + i))
    s200, w200, m20, last = C.clocks(rows, rows[-1][0])
    assert s200 is None
    assert w200 is None
    assert m20 is None
    assert last == (dt.date(2020, 7, 22), 100.0, 298.0)

    # Exactly 200 daily bars with closes 1..200: mean = (1 + 200) / 2 = 100.5
    rows_200 = make_daily_rows(start, 200, lambda i, _: (90.0, float(i + 1)))
    s200, w200, m20, last = C.clocks(rows_200, rows_200[-1][0])
    assert s200 == pytest.approx(100.5)
    assert w200 is None
    assert m20 is None
    assert last == (dt.date(2020, 7, 23), 90.0, 200.0)


def test_clocks_respects_asof_no_lookahead():
    # 210 days with closes 1..210; asof = day 200 (index 199, close 200)
    # Days 201..210 have huge closes (99999) and must be excluded.
    start = dt.date(2020, 1, 6)
    rows = make_daily_rows(
        start,
        210,
        lambda i, _: (float(i + 1), float(i + 1) if i < 200 else 99999.0),
    )
    asof = start + dt.timedelta(days=199)
    s200, _, _, last = C.clocks(rows, asof)
    # Mean of 1..200 = 100.5
    assert s200 == pytest.approx(100.5)
    assert last == (asof, 200.0, 200.0)


def test_clocks_weekly_mon_sun_and_partial_asof_week():
    # 200 full weeks (1400 days) starting Monday 2018-01-01, plus 3 days (Mon, Tue, Wed) of week 201.
    # For each full week k in 0..199: Mon..Sat close = 10.0, Sun close = 100.0 + k.
    # For week 200 (the 201st week): Mon close = 500.0, Tue close = 600.0, Wed close = 700.0.
    start = dt.date(2018, 1, 1)  # Monday
    n_days = 200 * 7 + 3
    rows = []
    for i in range(n_days):
        d = start + dt.timedelta(days=i)
        wk_idx = i // 7
        dow = d.weekday()  # Mon=0 .. Sun=6
        if wk_idx < 200:
            c = (100.0 + wk_idx) if dow == 6 else 10.0
        else:
            c = 500.0 + 100.0 * dow  # Mon=500, Tue=600, Wed=700
        rows.append((d, c - 1.0, c))

    # As of Tuesday of week 201 (wk_idx = 200, dow = 1):
    # Weeks included: wk_idx 1..199 (199 weeks, closes 101..299) + wk_idx 200 (partial week, close 600).
    # Sum(101..299) = 199 * (101 + 299) / 2 = 199 * 200 = 39800.
    # + 600 = 40400 -> 200-week SMA = 40400 / 200 = 202.0.
    tue = start + dt.timedelta(days=200 * 7 + 1)
    _, w200_tue, _, last_tue = C.clocks(rows, tue)
    assert w200_tue == pytest.approx(202.0)
    assert last_tue == (tue, 599.0, 600.0)

    # As of Wednesday of week 201: partial week close becomes 700 -> (39800 + 700) / 200 = 202.5.
    wed = start + dt.timedelta(days=200 * 7 + 2)
    _, w200_wed, _, last_wed = C.clocks(rows, wed)
    assert w200_wed == pytest.approx(202.5)
    assert last_wed == (wed, 699.0, 700.0)


def test_clocks_weekly_handles_missing_sunday():
    # If a week is missing Saturday/Sunday, the last available day in that Mon-Sun week is its close.
    start = dt.date(2018, 1, 1)  # Monday
    rows = []
    for wk_idx in range(200):
        mon = start + dt.timedelta(days=wk_idx * 7)
        if wk_idx == 199:
            # Only Monday and Friday exist in week 199; Friday close = 300.0
            rows.append((mon, 1.0, 50.0))
            rows.append((mon + dt.timedelta(days=4), 1.0, 300.0))
        else:
            # Monday..Sunday, Sunday close = 100.0
            for dow in range(7):
                rows.append((mon + dt.timedelta(days=dow), 1.0, 100.0 if dow == 6 else 10.0))

    # 199 weeks at 100.0 + 1 week at 300.0 -> (19900 + 300) / 200 = 101.0
    _, w200, _, _ = C.clocks(rows, rows[-1][0])
    assert w200 == pytest.approx(101.0)


def test_clocks_monthly_calendar_and_partial_asof_month():
    # 20 calendar months: 2023-01 .. 2024-08.
    # Month m_idx in 0..18: day 1 close = 1.0, day 15 close = 100.0 + m_idx (last day in data for that month).
    # Month 19 (2024-08): day 1 close = 50.0, day 10 close = 200.0.
    rows = []
    for m_idx in range(19):
        year = 2023 + (m_idx // 12)
        month = (m_idx % 12) + 1
        rows.append((dt.date(year, month, 1), 1.0, 1.0))
        rows.append((dt.date(year, month, 15), 1.0, 100.0 + m_idx))

    # 19 months only -> m20 is None
    _, _, m20_19, _ = C.clocks(rows, dt.date(2024, 7, 31))
    assert m20_19 is None

    # Add 20th month (2024-08) with two days
    rows.append((dt.date(2024, 8, 1), 40.0, 50.0))
    rows.append((dt.date(2024, 8, 10), 190.0, 200.0))

    # As of 2024-08-10: months 0..18 closes = 100..118 (sum = 19 * 109 = 2071), month 19 = 200.
    # Total = 2271 -> m20 = 2271 / 20 = 113.55.
    _, _, m20_20, last = C.clocks(rows, dt.date(2024, 8, 10))
    assert m20_20 == pytest.approx(113.55)
    assert last == (dt.date(2024, 8, 10), 190.0, 200.0)


def test_load_parses_csv_columns(tmp_path, monkeypatch):
    csv_file = tmp_path / "btc_daily.csv"
    csv_file.write_text(
        "date,open,high,low,close,volume\n"
        "2024-01-01,42000,43000,41500.5,42500.25,100\n"
        "2024-01-02,42500,44000,42000,43500,200\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(C, "CSV", csv_file)
    rows = C.load()
    assert rows == [
        (dt.date(2024, 1, 1), 41500.5, 42500.25),
        (dt.date(2024, 1, 2), 42000.0, 43500.0),
    ]


def test_main_table_formatting_and_na(monkeypatch, capsys):
    # Synthetic series covering all BOTTOMS dates up to 2026-07-05, with < 200 days around 2015-01-15
    # so 2015 prints n/a for SMAs and percentages, while later dates have valid 200d SMA.
    start = dt.date(2015, 1, 1)
    # Generate key dates needed by BOTTOMS: 2015-01-15, 2018-12-15, 2022-11-21, 2026-07-01, plus 200 days before 2018-12-15
    rows = [(start, 150.0, 160.0), (dt.date(2015, 1, 15), 170.0, 172.0)]
    for i in range(250):
        d = dt.date(2018, 4, 15) + dt.timedelta(days=i)
        rows.append((d, 3000.0, 6000.0))
    rows.append((dt.date(2022, 11, 21), 15000.0, 16000.0))
    rows.append((dt.date(2026, 7, 1), 58000.0, 60000.0))
    rows.append((dt.date(2026, 11, 6), 75000.0, 76000.0))

    monkeypatch.setattr(C, "load", lambda: rows)
    C.main()
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 7  # header + separator + 4 bottoms + now
    assert lines[0].startswith("| Moment | Date | Low / close | 200-day SMA |")
    # 2015 row has n/a for all SMAs and percentages
    assert lines[2] == "| 2015 | 2015-01-15 | 170 / 172 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |"
    # now row ends on 2026-11-06
    assert lines[6].startswith("| now | 2026-11-06 | 75,000 / 76,000 |")
