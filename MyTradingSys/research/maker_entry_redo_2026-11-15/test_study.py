"""Wiring tests for maker_entry_redo_2026-11-15: through-by-one-tick fill (a touch is no fill), fill at the limit, no read before placement,
the 1m bracket walk (fill minute can stop out but not hit the target, stop first), shared-cost imports, the window and family size."""
import calendar
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("maker_redo_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)

T0 = calendar.timegm((2024, 3, 1, 0, 0, 0)) * 1000
MIN = 60000


def mk(rows, tick=0.5):
    """rows: (o, h, l, c) per minute from T0."""
    m = object.__new__(study.M1Data)
    m.t = np.array([T0 + i * MIN for i in range(len(rows))], dtype=np.int64)
    m.o, m.h, m.l, m.c = (np.array([r[k] for r in rows], dtype=float) for k in range(4))
    m.tick = tick
    return m


def test_long_touch_is_not_a_fill_one_tick_through_is():
    m = mk([(101, 102, 100.0, 101), (101, 102, 99.5, 101)])         # minute 0 touches 100.0 exactly; minute 1 trades 0.5 through
    assert study.limit_fill(m, T0, T0 + 2 * MIN, 100.0, 1) == 1


def test_short_symmetry():
    m = mk([(99, 100.0, 98, 99), (99, 100.5, 98, 99)])
    assert study.limit_fill(m, T0, T0 + 2 * MIN, 100.0, -1) == 1
    assert study.limit_fill(mk([(99, 100.0, 98, 99)]), T0, T0 + MIN, 100.0, -1) is None


def test_never_reads_before_placement_or_after_order_life():
    m = mk([(101, 102, 90, 101), (101, 102, 100.5, 101), (101, 102, 99.0, 101)])    # minute 0 trades through but is before placement
    assert study.limit_fill(m, T0 + MIN, T0 + 3 * MIN, 100.0, 1) == 2
    assert study.limit_fill(m, T0 + MIN, T0 + 2 * MIN, 100.0, 1) is None             # order cancelled before minute 2


def test_bracket_fill_minute_can_stop_out_but_not_hit_target():
    # long px 100 target 104, stop = 100 - 0.5*4 = 98. fill minute f=0 reaches both 98 and 104: stop wins
    m = mk([(100, 104.5, 97.5, 100), (100, 101, 99, 100)])
    g, kind = study.bracket_1m(m, 0, 100.0, 1, 104.0, 0.5, T0 + 2 * MIN, 100.0)
    assert kind == "stop" and abs(g - (-2.0)) < 1e-9
    # fill minute high reaches the target only: not counted (k > f), the next minute decides
    m = mk([(100, 104.5, 99, 100), (100, 101, 97, 100)])
    g, kind = study.bracket_1m(m, 0, 100.0, 1, 104.0, 0.5, T0 + 2 * MIN, 100.0)
    assert kind == "stop" and abs(g - (-2.0)) < 1e-9
    m = mk([(100, 104.5, 99, 100), (100, 105, 99, 100)])
    g, kind = study.bracket_1m(m, 0, 100.0, 1, 104.0, 0.5, T0 + 2 * MIN, 100.0)
    assert kind == "target" and abs(g - 4.0) < 1e-9


def test_bracket_gap_through_stop_fills_at_open_and_time_exit_uses_parent_close():
    m = mk([(100, 100.5, 99.5, 100), (97, 98, 96, 97)])
    g, kind = study.bracket_1m(m, 0, 100.0, 1, 104.0, 0.5, T0 + 2 * MIN, 100.0)
    assert kind == "stop" and abs(g - (97 - 100) / 100 * 100) < 1e-9
    g, kind = study.bracket_1m(mk([(100, 101, 99, 100)] * 3), 0, 100.0, 1, 104.0, 0.5, T0 + 3 * MIN, 101.0)
    assert kind == "time" and abs(g - 1.0) < 1e-9
    gs, ks = study.bracket_1m(mk([(100, 101, 99, 100)] * 3), 0, 100.0, -1, 96.0, 0.5, T0 + 3 * MIN, 101.0)
    assert ks == "time" and abs(gs - (-1.0)) < 1e-9
    assert study.bracket_1m(mk([(100, 101, 99, 100)]), 0, 100.0, 1, 99.0, 0.5, T0 + MIN, 100.0) is None   # target on the wrong side


def test_costs_are_the_shared_research_kit_values_and_family_and_window():
    assert study.TAKER_PCT is study.rk.TAKER_RT_PCT and study.MAKER_PCT is study.rk.MAKER_IN_RT_PCT
    assert study.MAKER_PCT < study.TAKER_PCT
    assert study.M_FAMILY == 21 and len(study.SYMS) == 10
    assert study.OOS_START == calendar.timegm((2024, 1, 1, 0, 0, 0)) * 1000 and study.OOS_END == calendar.timegm((2026, 11, 12, 0, 0, 0)) * 1000


def test_tick_and_tf_index():
    assert abs(study.infer_tick([100.0, 100.01, 100.03, 100.03]) - 0.01) < 1e-9
    bars = [{"t": T0 + i * 900000} for i in range(4)]
    assert study.tf_index(bars, 900000, T0 + 900000 + 5) == 1 and study.tf_index(bars, 900000, T0 + 4 * 900000) is None
    assert study.tf_index(bars, 900000, T0 - 1) is None


def test_cell_net_per_signal_counts_a_miss_as_zero():
    rows = [dict(arm="WT", t0=dict(gross=1.0, day=1, t=T0), m=dict(gross=1.0, day=1, t=T0, exit="time")),
            dict(arm="WT", t0=dict(gross=-1.0, day=2, t=T0), m=None)]
    c = study.cell(rows, dict(arm="WT", cell="x"))
    assert c["fill_rate"] == 0.5 and abs(c["m_net_per_signal"] - (1.0 - study.MAKER_PCT) / 2) < 1e-9
    assert abs(c["t_net_per_signal"] - ((1.0 - study.TAKER_PCT) + (-1.0 - study.TAKER_PCT)) / 2) < 1e-9
