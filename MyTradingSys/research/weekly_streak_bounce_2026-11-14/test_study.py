"""Run: python -m pytest test_study.py  (or python test_study.py). With STUDY_BUG=lookahead this must FAIL."""
import sys, pathlib
sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np
import study

MON = 4  # epoch day 0 is Thursday; day 4 is a Monday
def synth(red_weeks, nweeks=12):
    """Weekly pattern: red weeks fall 100->90 (open at Mon, close Sun); green rise. Daily bars flat inside a week."""
    rows, px = [], 100.0
    for w in range(nweeks):
        wo = px; wc = px * (0.9 if w in red_weeks else 1.1)
        for d in range(7):
            o = wo + (wc - wo) * d / 7; c = wo + (wc - wo) * (d + 1) / 7
            rows.append([(MON + 7 * w + d) * 86400000, o, max(o, c) * 1.01, min(o, c) * 0.99, c])
        px = wc
    return rows

def test_streak_event_and_e1_is_next_monday_open():
    c = study.Coin("S", synth({1, 2, 3, 4, 5}, 14))
    evs = study.events(c, "S5")
    assert len(evs) == 1 and evs[0]["w"] == 5          # fires when the 5th red week closes
    e, p, _ = study.entry(c, evs[0], "E1")
    assert e == 7 * 6                                   # Monday after week 5, never earlier
    assert abs(p - c.o[7 * 6]) < 1e-12
    assert p == c.wc[5] or abs(p - c.wc[5]) < 1.0      # open == prior close in this synthetic

def test_no_event_before_streak_complete():
    c = study.Coin("S", synth({1, 2, 3, 4}, 14))
    assert study.events(c, "S5") == []

def test_fixed_exit_uses_close_of_last_day_and_costs():
    c = study.Coin("S", synth({1, 2, 3, 4, 5}, 14))
    e = 7 * 6
    r, _ = study.exit_ret(c, e, c.o[e], "X1", 0, e)
    assert abs(r - (c.c[e + 6] / c.o[e] - 1 - 0.0012)) < 1e-12

def test_stop_hit_before_time_exit():
    rows = synth({1, 2, 3, 4, 5}, 14)
    c = study.Coin("S", rows)
    ev = study.events(c, "S5")[0]
    e = ev["d0"]
    res = study.exit_ret(c, e, c.o[e], "XS", ev["base_low"], e)
    assert res is not None and res[1] is not None

if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f(); print("ok", k)
