"""Tests for run_dev.py: loader refuses a bar dated 2024-07-01; a one-day fixture net equals the hand value from fees.py."""
import csv
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))
import run_dev  # noqa: E402
from MyTradingSys.backtest import fees  # noqa: E402


def _write(tmp, name, rows):
    p = tmp / name
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["open_time", "open", "high", "low", "close", "volume"])
        w.writerows(rows)
    return p


def test_loader_raises_on_bar_dated_2024_07_01(monkeypatch):
    tmp_path = Path(tempfile.mkdtemp())
    _write(tmp_path, "BTCUSDT-1m-2024-06.csv", [[1719792000000, 1, 1, 1, 1, 1]])      # 2024-07-01 00:00Z inside a read file
    monkeypatch.setattr(run_dev, "DATA_GLOB", str(tmp_path / "BTCUSDT-1m-20??-??.csv"))
    with pytest.raises(ValueError):
        run_dev.load_dev()


def test_loader_never_opens_month_file_after_dev(monkeypatch):
    tmp_path = Path(tempfile.mkdtemp())
    _write(tmp_path, "BTCUSDT-1m-2024-07.csv", [[1719792000000, 1, 1, 1, 1, 1]])
    monkeypatch.setattr(run_dev, "DATA_GLOB", str(tmp_path / "BTCUSDT-1m-20??-??.csv"))
    assert run_dev.load_dev()[0] == []


def test_one_day_net_matches_hand_value():
    """Short at 100 (tranche 1 only, taker), target hit by a later bar: hand value from fees.py constants."""
    assert run_dev.TAKER == fees.BINANCE_TAKER and run_dev.MAKER == fees.BINANCE_MAKER
    day0, M = 86400000 * 10, 60000
    n = 24 * 60
    o = [100.0] * n; h = [100.0] * n; l = [100.0] * n; c = [100.0] * n
    t = [day0 + i * M for i in range(n)]
    ei = 8 * 60                                    # 08:00Z entry bar
    for i in range(ei + 2, ei + 5):
        l[i] = 89.0                                # target 95 (entry - 1.5*ATR with ATR=... set below) is traded through
    tp = run_dev.Tape.__new__(run_dev.Tape)
    tp.t, tp.o, tp.h, tp.l, tp.c = t, o, h, l, c
    tp.idx = {x: i for i, x in enumerate(t)}
    ep_atr = 10.0 / 1.5                            # entry - 1.5 ATR = 90; no S_dn level 1 ATR below (prior-day range absent -> fixture)
    pre = [95.0] * n                               # previous day for PDL: 95 is above entry - 1.0 ATR (93.3) -> not eligible
    tp.t = [x - 86400000 for x in t] + t
    tp.o = pre + o; tp.h = pre + h; tp.l = pre + l; tp.c = pre + c
    tp.idx = {x: i for i, x in enumerate(tp.t)}
    tp.swing = lambda *a, **k: None
    a, b = n, 2 * n
    ep = run_dev.trade(tp, day0, a, b, a + ei, ep_atr, 100.0, day0 + 13 * 3600000)
    e_px = 100.0 * (1 - 0.0002)                    # taker slippage 2 bps
    units = 0.25 / e_px
    hand = units * (e_px - 90.0) - fees.BINANCE_TAKER * 0.25 - fees.BINANCE_MAKER * units * 90.0
    assert ep["kind"] == "TARGET"
    assert ep["net"] == pytest.approx(hand, rel=1e-9)
