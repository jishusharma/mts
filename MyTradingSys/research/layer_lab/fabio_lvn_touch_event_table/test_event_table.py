import importlib.util
from pathlib import Path

MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("fabio_lvn_touch_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)

H1 = 3_600_000
T0 = 1646092800000  # 2022-03-01T00:00Z
P = 20              # filler bars before the leg (ATR14 history)
# leg bars (zero range, so each volume lands in one 1.0-wide bin of the 100..120 range):
LEG = [(100, 5), (102, 10), (103, 30), (104, 20), (105, 40), (106, 30), (120, 5)]
# hand value: bins 0..19 of width 1; POC bin 5 (105); value area bins 3..6; lowest bin 4 -> [104,105] -> mid 104.5
HAND_LEVEL = 104.5
A_I, B_I, CONF = P, P + 6, P + 8


def _bar(i, o, h, l, c, v=1.0):
    return {"t": T0 + i * H1, "o": o, "h": h, "l": l, "c": c, "v": v}


def _bars(touch_at, n=P + 80, leg_vol=True):
    bars = [_bar(i, 110.0, 111.0, 109.0, 110.0) for i in range(n)]
    for j, (p, v) in enumerate(LEG):
        idx = A_I + j
        bars[idx] = _bar(idx, p, p, p, p, v if leg_vol else 0.0)
    early = B_I + 1
    bars[early] = _bar(early, 105.0, 106.0, 104.0, 105.0)  # touches the level BEFORE confirmed_i
    if touch_at is not None:
        bars[touch_at] = _bar(touch_at, 108.0, 108.5, 104.5, 108.0)  # low == level: touch
    return bars


def _leg(a=A_I, b=B_I, conf=CONF):
    return {"a_i": a, "b_i": b, "a_price": 0.0, "b_price": 0.0, "confirmed_i": conf}


def _run(bars, legs):
    event_table.swing_legs = lambda *a, **k: legs
    return event_table.build_event_table(bars)


def _atr(bars, last):
    trs = []
    for j in range(last - 13, last + 1):
        h, l, pc = bars[j]["h"], bars[j]["l"], bars[j - 1]["c"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(trs) / 14


def test_first_touch_bar_gives_single_row_with_hand_level_and_next_open_entry():
    k = CONF + 12
    bars = _bars(k)
    ent, hi_i, lo_i = k + 1, k + 3, k + 5
    bars[ent]["o"] = 107.0
    bars[hi_i]["h"], bars[lo_i]["l"] = 112.0, 105.0   # a later touch must not add a row
    rows = _run(bars, [_leg()])
    assert len(rows) == 1
    row = rows[0]
    assert row["level"] == HAND_LEVEL
    assert row["touch_t"] == bars[k]["t"]
    assert row["t"] == bars[ent]["t"]
    assert row["entry"] == 107.0
    assert row["status"] == "OK"


def test_excursions_long_and_short_hand_values():
    k = CONF + 12
    bars = _bars(k)
    ent, hi_i, lo_i, past = k + 1, k + 3, k + 5, k + 25
    bars[ent]["o"] = 107.0
    bars[hi_i]["h"] = 112.0      # +5 from entry
    bars[lo_i]["l"] = 105.0      # -2 from entry
    # the entry bar is inside the window; nothing beyond 24 bars counts
    bars[past]["h"], bars[past]["l"] = 999.0, 1.0
    r = _atr(bars, k)
    row = _run(bars, [_leg()])[0]
    assert row["r"] == r
    assert row["long_mfe_R"] == 5.0 / r
    assert row["long_mae_R"] == 2.0 / r
    assert row["short_mfe_R"] == 2.0 / r
    assert row["short_mae_R"] == 5.0 / r
    assert row["bars_forward"] == 24


def test_touch_before_confirmed_i_is_ignored():
    # bar B_I+1 touches the level but precedes confirmed_i; with no later touch there is no row
    assert _run(_bars(None), [_leg()]) == []


def test_touch_after_newer_confirmed_leg_gives_none():
    bars = _bars(CONF + 15)
    newer = _leg(a=B_I + 1, b=B_I + 7, conf=CONF + 5)
    rows = _run(bars, [_leg(), newer])
    assert [r for r in rows if r["leg_a_i"] == A_I] == []


def test_touch_beyond_48_bars_gives_none():
    assert _run(_bars(CONF + 49), [_leg()]) == []
    assert len(_run(_bars(CONF + 48), [_leg()])) == 1


def test_empty_profile_is_not_in_data():
    rows = _run(_bars(CONF + 12, leg_vol=False), [_leg()])
    assert len(rows) == 1
    assert rows[0]["status"] == "NOT_IN_DATA"
    assert rows[0]["level"] == "" and rows[0]["long_mfe_R"] == ""


def test_too_little_forward_data_is_not_in_data():
    k = CONF + 12
    rows = _run(_bars(k, n=k + 10), [_leg()])
    assert rows[0]["status"] == "NOT_IN_DATA" and rows[0]["long_mae_R"] == ""


def test_bars_outside_dev_are_dropped_before_building():
    start = 1719792000000  # 2024-07-01T00:00Z
    bars = _bars(CONF + 12)
    for i, b in enumerate(bars):
        b["t"] = start + i * H1
    assert _run(bars, [_leg()]) == []


def test_real_swing_detection_runs_end_to_end():
    import importlib
    spec = importlib.util.spec_from_file_location("fresh_lvn", MODULE)
    fresh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fresh)
    prices = [100, 101, 103, 106, 104, 101, 99, 102, 105, 107, 104, 100, 98, 101, 104, 108, 105, 102, 100, 103] * 4
    bars = [_bar(i, p, p + 1, p - 1, p, 10.0 + i % 7) for i, p in enumerate(prices)]
    assert isinstance(fresh.build_event_table(bars), list)
