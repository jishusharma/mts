"""Fail-first tests for recount_o2.py (O2 independent recount of the E2 Krown S8 4h C0).

The key O2 check: recount_o2's sealed-cut guard refuses a bar at/after 2024-07-01 00:00Z, so a planted
sealed bar makes the recount refuse to compute (raises), exactly as counts_only.guard / e2_run.assert_no_sealed do.
The C0 reproduction test is gated on the kline cache being on this machine (public Binance 4h, fetched by O2).
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import recount_o2 as ro  # noqa: E402


def test_sealed_cut_guard_refuses_planted_bar():
    """A bar at the sealed cut 2024-07-01 00:00Z must be refused by the guard; the recount would not compute on it."""
    with pytest.raises(ValueError):
        ro.assert_no_sealed([(ro.CUT_MS, 1.0, 1.0, 1.0, 1.0)], 'planted')
    # one bar before the cut is fine
    ro.assert_no_sealed([(ro.CUT_MS - ro.H4, 1.0, 1.0, 1.0, 1.0)], 'ok')


def test_load_drops_sealed_bars_at_read(tmp_path, monkeypatch):
    """The loader itself drops any cached bar >= the cut (a bar in the last month file at exactly the cut is removed)."""
    # every month is NOT_IN_DATA except 2024-06, which carries two in-range bars and one at the cut
    for ym in ro.months(ro.WARMUP_FROM, '2024-05'):
        (tmp_path / f'BTCUSDT-4h-{ym}.missing').write_text('404\n')
    cut, h4 = ro.CUT_MS, ro.H4
    f = tmp_path / 'BTCUSDT-4h-2024-06.csv'
    f.write_text(f'{cut - 2*h4},1,2,0.5,1.5\n{cut - h4},1.5,2,1,1.8\n{cut},1.8,3,1,2\n', encoding='utf-8')
    monkeypatch.setattr(ro, 'DATA', tmp_path)
    rows = ro.load('BTCUSDT', log=lambda *_: None)
    assert len(rows) == 2 and max(r[0] for r in rows) < cut and all(len(r) == 5 for r in rows)


@pytest.mark.skipif(not (ro.DATA / 'BTCUSDT-4h-2020-01.csv').exists(), reason='cached 4h klines not on this machine')
def test_recount_reproduces_e2_c0_within_one_percent():
    """O2's own recount matches the E2 published C0 (RESULT.md) within 1 % on n, days, mean, SE, t, gross, 4x-fee."""
    c0, _ = ro.c0_block()
    for key, want in ro.PUBLISHED.items():
        got = c0[key]
        if want:
            assert abs(got - want) <= abs(want) * 0.01, f'{key}: recount {got} vs published {want}'
        else:
            assert got == want
