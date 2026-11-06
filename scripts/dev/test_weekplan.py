"""Weekly plan per login (card weekly-plan-per-login-wired-into-supervi). Expected numbers are worked by hand.
Plan: login A, t0 2026-11-06T09:00Z, week 5%, cap 95, reset 2026-11-13T09:00Z. Last day starts 11-12T09:00Z, so 144 h to spread
90 pts = 0.625 pts/h = 15 pts/day = 3.125 pts per 5 h; the last 24 h go 95 -> 99 (traffic.LAST_DAY_CAP)."""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exhaust as E
import supervisor as S
import traffic as T

def U(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)

T0, RESET = U("2026-11-06T09:00Z"), U("2026-11-13T09:00Z")


def test_week_target_even_spread_then_last_day():
    f = lambda now, **k: T.week_target(T0, 5, 95, RESET, U(now), **k)
    assert f("2026-11-06T09:00Z") == 5
    assert abs(f("2026-11-09T09:00Z") - 50) < 1e-6        # 72 h * 0.625 = 45, +5
    assert abs(f("2026-11-12T09:00Z") - 95) < 1e-6
    assert abs(f("2026-11-12T21:00Z") - 97) < 1e-6        # 12 h of 24 from 95 to 99
    assert f("2026-11-13T10:00Z") == T.LAST_DAY_CAP


def test_weekplan_text_has_day_and_window_rows_and_no_account_data():
    txt = E.weekplan_text("A", 5, T0, RESET, 95, T0)
    assert "PARAMS login=A t0=2026-11-06T09:00Z w0=5 cap=95 reset=2026-11-13T09:00Z" in txt
    assert "| 2026-11-07T09:00Z | 20.0 |" in txt and "| 2026-11-09T09:00Z | 50.0 |" in txt   # 15 pts/day
    assert "| 2026-11-06T14:00Z | 8.1 |" in txt                                          # first 5 h window: +3.125
    assert "@" not in txt and "token" not in txt.lower()


def _rd(five, week, five_reset="2026-11-09T12:00Z", week_reset="2026-11-13T09:00Z"):
    return {"five": five, "week": week, "five_reset": five_reset, "week_reset": week_reset}


def _plan_file(tmp_path):
    (tmp_path / "MyTradingSys" / "system").mkdir(parents=True)
    (tmp_path / "MyTradingSys" / "system" / "WEEK_PLAN_A.md").write_text(E.weekplan_text("A", 5, T0, RESET, 95, T0), encoding="utf-8", newline="\n")


def test_week_pace_behind_adds_catchup_spawn(tmp_path):
    _plan_file(tmp_path)
    now = U("2026-11-09T09:00Z")                                   # target 50
    pl = S.pace_plan(now, _rd(10, 44), 95)
    L = S.week_pace_lines(tmp_path, "A", 44, "2026-11-13T09:00Z", now, pl)
    assert L[0] == "WEEK PACE login=A target=50% now=44% behind 6 pts"
    # 6 wk pts / k 0.12 = 50 pts of 5 h; room under the 80 ceiling = 70 -> 50 pts of 5 h -> 4 workers (>= 40)
    assert L[1].startswith("SPAWN CATCHUP") and "up to 4" in L[1]


def test_week_pace_small_gap_and_ahead_have_no_spawn(tmp_path):
    _plan_file(tmp_path)
    now = U("2026-11-09T09:00Z")
    pl = S.pace_plan(now, _rd(10, 47), 95)
    assert S.week_pace_lines(tmp_path, "A", 47, "2026-11-13T09:00Z", now, pl) == ["WEEK PACE login=A target=50% now=47% behind 3 pts"]
    assert S.week_pace_lines(tmp_path, "A", 55, "2026-11-13T09:00Z", now, pl) == ["WEEK PACE login=A target=50% now=55% ahead 5 pts"]


def test_week_pace_missing_or_stale_plan_says_so(tmp_path):
    now = U("2026-11-09T09:00Z")
    pl = S.pace_plan(now, _rd(10, 44), 95)
    L = S.week_pace_lines(tmp_path, "A", 44, "2026-11-13T09:00Z", now, pl)
    assert len(L) == 1 and L[0].startswith("WEEK PACE login=A NO PLAN") and "exhaust.py weekplan --login A" in L[0]
    _plan_file(tmp_path)
    L = S.week_pace_lines(tmp_path, "A", 44, "2026-11-20T09:00Z", now, pl)       # the reset moved: file is last week's
    assert "NO PLAN" in L[0]


def test_exhaust_window_caps_workers_by_projected_burn():
    """week 50, 5 h at 80%, both resets 2 h away: ceiling 95 -> 15 pts left; a worker burns 5 pts/h * 2 h = 10 pts -> 1 worker.
    Without the cap the room (15 pts) gives 2 slots."""
    now = U("2026-11-13T07:00Z")
    p = S.pace_plan(now, _rd(80, 50, five_reset="2026-11-13T09:00Z"), 99)
    assert p["ceil"] == 95 and p["slots"] == 1
    assert "exhaust cap" in p["why"]


def test_spawn_lines_order_commit_after_every_step():
    p = S.pace_plan(U("2026-11-09T09:00Z"), _rd(10, 20), 95)
    live = {"A": {"host": "JIS-NUC", "mode": "NORMAL", "run": 0, "free": 2, "at": "x", "dsa": "up"}}
    ctx = {"picks": [{"id": "s1", "role": "Builder", "worker": "session"}], "ci": {"red": False}}
    spawn = [l for l in S.plan_lines("A", "JIS-NUC", p, live, ctx, gate_key=False) if l.startswith("SPAWN")][0]
    assert "commit after every step" in spawn
    ctx = {"ci": {"red": True, "message": "x"}, "picks": []}
    red = [l for l in S.plan_lines("A", "JIS-NUC", p, live, ctx, gate_key=False) if l.startswith("SPAWN CI RED")]
    assert not red or "commit after every step" in red[0]


def test_plan_lines_print_week_pace_from_ctx():
    p = S.pace_plan(U("2026-11-09T09:00Z"), _rd(10, 20), 95)
    live = {"A": {"host": "JIS-NUC", "mode": "NORMAL", "run": 0, "free": 2, "at": "x", "dsa": "up"}}
    out = S.plan_lines("A", "JIS-NUC", p, live, {"ci": {"red": False}, "week_pace": ["WEEK PACE login=A target=50% now=44% behind 6 pts"]}, False)
    assert "WEEK PACE login=A target=50% now=44% behind 6 pts" in out
