"""Hand-built bars; python -m pytest test_study.py. Red on a look-ahead entry (entry_offset = 0)."""
import datetime as dt
import os
import sys
from datetime import date

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study as S  # noqa: E402

D = date(2025, 3, 5)  # Wednesday


def bars():
    t0 = S.open_ms(D)
    t = t0 + np.arange(-5, 70) * S.MIN
    o = np.full(len(t), 100.0)
    c = np.full(len(t), 100.0)
    i = 5
    c[i + 2] = 101.0                         # first 3 minutes up 1 %
    o[i + 3] = 101.0                         # entry bar open
    c[i + 29], c[i + 59] = 102.01, 99.99     # exits
    return t.astype(np.int64), o, c


def test_entry_is_bar4_open_and_returns():
    t, o, c = bars()
    ev, sk = S.events_for(t, o, c, [D])
    assert sk == 0 and len(ev) == 1
    e = ev[0]
    assert abs(e["m3"] - 0.01) < 1e-12
    assert abs(e["r27"] - (102.01 / 101.0 - 1)) < 1e-12 and abs(e["r57"] - (99.99 / 101.0 - 1)) < 1e-12


def test_lookahead_entry_would_change_result():
    t, o, c = bars()
    bad, _ = S.events_for(t, o, c, [D], entry_offset=0)
    good, _ = S.events_for(t, o, c, [D])
    assert abs(bad[0]["r27"] - good[0]["r27"]) > 0.005


def test_net_cost_and_side():
    assert abs(S.net_bp(1, 0.0100) - (100 - S.COST_BP)) < 1e-9
    assert abs(S.net_bp(-1, 0.0100) - (-100 - S.COST_BP)) < 1e-9
    assert abs(S.COST_BP - 14.0) < 1e-9


def test_gap_skips_event():
    t, o, c = bars()
    keep = np.ones(len(t), bool)
    keep[20] = False
    ev, sk = S.events_for(t[keep], o[keep], c[keep], [D])
    assert ev == [] and sk == 1


def test_dst_open_hour():
    assert S.open_ms(date(2025, 1, 15)) == int(dt.datetime(2025, 1, 15, 14, 30, tzinfo=dt.timezone.utc).timestamp() * 1000)
    assert S.open_ms(date(2025, 7, 15)) == int(dt.datetime(2025, 7, 15, 13, 30, tzinfo=dt.timezone.utc).timestamp() * 1000)
