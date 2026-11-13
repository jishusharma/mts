"""Fail-first tests for fetch_klines.py: aligned 8h/12h resampling from 4h bars, and gap/duplicate detection."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_klines as fk  # noqa: E402

H = 3600000
D0 = 1577836800000  # 2020-01-01 00:00 UTC


def bars(start, n, step=4 * H):
    return [[start + i * step, 100.0 + i, 110.0 + i, 90.0 + i, 101.0 + i, 1.0] for i in range(n)]


def test_resample_8h_12h_boundaries_utc():
    b4 = bars(D0, 12)  # 2 days of 4h bars from 00:00 UTC
    r8 = fk.resample(b4, 8)
    assert [r[0] for r in r8] == [D0 + i * 8 * H for i in range(6)]
    first = r8[0]
    assert first[1] == b4[0][1] and first[4] == b4[1][4]
    assert first[2] == max(b4[0][2], b4[1][2]) and first[3] == min(b4[0][3], b4[1][3])
    assert first[5] == 2.0
    # starting off-boundary (04:00) drops the unaligned lone half
    r8b = fk.resample(bars(D0 + 4 * H, 5), 8)
    assert [r[0] for r in r8b] == [D0 + 8 * H, D0 + 16 * H]
    r12 = fk.resample(b4, 12)
    assert [r[0] for r in r12] == [D0 + i * 12 * H for i in range(4)]
    assert r12[0][4] == b4[2][4] and r12[0][5] == 3.0
    # an incomplete bucket (missing middle bar) is dropped
    assert fk.resample(b4[:1] + b4[2:], 8)[0][0] != D0


def test_no_gap_or_duplicate_bars():
    ok = bars(D0, 10)
    assert fk.check_continuity(ok, 4 * H) == {"gaps": 0, "dups": 0}
    assert fk.check_continuity(ok[:4] + ok[5:], 4 * H)["gaps"] == 1
    assert fk.check_continuity(ok[:4] + [ok[3]] + ok[4:], 4 * H)["dups"] == 1
