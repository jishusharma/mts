"""Fail-first: flush bar's OI change is I[j+1]/I[j]-1 (Bybit OI stamped at bar open). Synthetic 4-bar series."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oi_after_flush import flush_oi_change


def series():
    C = [100.0, 99.6, 99.6, 99.6]          # bar 1 drops price 0.4%
    O = [100.0, 100.0, 99.6, 99.6]
    I = [1000.0, 1000.0, 997.0, 997.0]     # I[2]/I[1]-1 = -0.3%; I[1]/I[0]-1 = 0
    return O, C, I


def test_new_pairing_uses_next_stamp():
    O, C, I = series()
    assert abs(flush_oi_change(O, C, I, 1) - (-0.003)) < 1e-12


def test_old_pairing_is_previous_bar():
    O, C, I = series()
    assert flush_oi_change(O, C, I, 1, "old") == 0.0
