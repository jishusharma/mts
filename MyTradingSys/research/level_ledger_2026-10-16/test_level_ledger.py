"""Tests for level_ledger.py / java_zone_check.py (synthetic bars, no archive, no Java)."""
import numpy as np
import pytest

import level_ledger as LL
import java_zone_check as JZ

N = 1440


def _bp(l, h, v):
    return {"poc_price": float(np.nanmedian((l + h) / 2)), "vah": float(np.nanmax(h)) - 1, "val": float(np.nanmin(l)) + 1}


def _day(base=100.0):
    l = np.full(N, base)
    l[10] = base - 5
    h = l + 2
    h[20] = base + 9
    return l, h, np.ones(N)


def test_row_available_at_next_midnight_after_formed():
    l, h, v = _day()
    rows = LL.day_rows(3, LL.TS0 + 3 * LL.DAY_MS, l, h, v, _bp, "t")
    assert [r["origin"] for r in rows] == list(LL.ORIGINS)
    for r in rows:
        assert r["available_at"] == LL.TS0 + 4 * LL.DAY_MS
        assert r["formed_at"] < r["available_at"]
    assert rows[0]["price"] == 109.0 and rows[1]["price"] == 95.0


def test_later_day_bar_cannot_change_an_available_row():
    A = {k: np.full(2 * N, 100.0) for k in ("L", "H", "V")}
    A["V"][:] = 1.0
    A["H"] = A["L"] + 2
    before = LL.build(A, 2, _bp, "t")
    A["H"][N:][7] = 10_000.0          # planted: a day-1 high
    after = LL.build(A, 2, _bp, "t")
    day0 = [r for r in before if r["available_at"] == LL.TS0 + LL.DAY_MS]
    assert day0 == [r for r in after if r["available_at"] == LL.TS0 + LL.DAY_MS]
    assert LL.readable(after, LL.TS0 + LL.DAY_MS - 1) == []
    assert len(LL.readable(after, LL.TS0 + LL.DAY_MS)) == 5
    assert max(r["price"] for r in LL.readable(after, LL.TS0 + LL.DAY_MS)) < 1000


def test_day_with_many_missing_minutes_gives_no_level():
    l, h, v = _day()
    l[:LL.MAX_MISSING + 1] = np.nan
    assert LL.day_rows(0, LL.TS0, l, h, v, _bp, "t") == []


def test_java_bin_rule_and_tolerance():
    assert JZ.java_bin(0.0, 1000.0) == 5.0                  # 1000 / max(50, 200)
    assert JZ.java_bin(0.0, 100.0) == 2.0                   # floor of 50 bins
    jv = {"poc": 100.0, "vah": 130.0, "val": 80.0}
    py = {"poc_price": 108.0, "vah": 131.0, "val": 100.0}
    out = JZ.compare(jv, py, 0.0, 200.0)                    # tol = max(4, 10) = 10
    assert out["poc"][1] and out["vah"][1] and not out["val"][1]
