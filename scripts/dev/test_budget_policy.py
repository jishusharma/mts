"""One budget policy (SUPER_SESSION.md 'Budget policy'): supervisor.py pace_plan, traffic.py pacing_state and exhaust.py plan must agree.
Goal 1: weekly room unused at the reset is lost, so the last 24 h lift every cap to 99 and the last 2 h lift the 5 h stop to 95.
Goal 2: outside those windows the 5 h window stops at 80, so it is not run to 100 every time."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exhaust as E
import supervisor as S
import traffic as T

NOW = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
STOPS = ("STOP", "SUPERVISOR-ONLY")


def z(t):
    return t.strftime("%Y-%m-%dT%H:%MZ")


def views(five, week, h_to_reset, login="C", host="JIS-NB", running=0):
    """supervisor mode, traffic state, exhaust phase for one reading (5 h window resets in 3 h)."""
    wr = NOW + timedelta(hours=h_to_reset)
    rd = {"five": five, "week": week, "five_reset": z(NOW + timedelta(hours=3)), "week_reset": z(wr)}
    cap = S.weekly_cap(login, host, h_to_reset)
    pl = S.pace_plan(NOW, rd, cap, (), running)
    st, _ = T.pacing_state({"at": NOW, "week": week, "five_h": five, "reset": wr}, NOW)
    ex = E.plan(login, week, five, wr, {}, NOW)
    return pl, st, ex["phase"], cap


def test_fresh_window_early_week_spends():          # 5 h 7% / week 5%
    pl, st, _, _ = views(7, 5, 6 * 24)
    assert pl["mode"] in ("SPEND", "NORMAL") and pl["slots"] >= 1 and st != "THROTTLE"


def test_hot_window_holds_back():                   # 5 h 85% / week 40%: goal 2
    pl, st, ph, _ = views(85, 40, 4 * 24)
    assert pl["mode"] == "STOP" and pl["slots"] == 0 and st == "THROTTLE" and ph == "none"


def test_last_day_lifts_every_cap_even_on_the_desktop():      # goal 1: C on JIS-NB was capped 85 to the end
    assert S.weekly_cap("C", "JIS-NB", 20) == 99 and S.weekly_cap("B", "JIS-NB", 20) == 99
    assert S.weekly_cap("C", "JIS-NB", 30) == 85 and S.weekly_cap("B", "JIS-NB", 30) == 75
    pl, st, _, cap = views(10, 90, 20, "C", "JIS-NB")
    assert cap == 99 and pl["mode"] != "STOP" and st == "SPEND"


def test_last_day_pace_throttle_does_not_override_unused_room():  # week 94%, 20 h left: 5 pts left under 99
    pl, st, _, _ = views(10, 94, 20, "A", "DESKTOP-F7IU69N")
    assert st == "SPEND" and pl["mode"] != "STOP"


def test_login_at_its_cap_stops_everywhere():
    pl, st, _, _ = views(10, 99, 20)
    assert pl["mode"] == "STOP" and st == "THROTTLE"
    pl, st, _, _ = views(10, 85, 72, "C", "JIS-NB")           # at the desktop cap, 3 days left
    assert pl["mode"] == "STOP" and st == "THROTTLE"


def test_exhaust_window_lifts_the_five_hour_stop():          # 90 min to reset, 5 h 85%, week 92%
    pl, st, ph, _ = views(85, 92, 1.5)
    assert ph == "plan" and pl["mode"] != "STOP" and pl["slots"] >= 1 and st != "THROTTLE"
    assert E.plan("C", 92, 85, NOW + timedelta(hours=1.5), {}, NOW)["five_stop"] == 95
    assert E.plan("C", 92, 85, NOW + timedelta(hours=5), {}, NOW)["five_stop"] == 80
    pl, _, _, _ = views(96, 92, 1.5)
    assert pl["mode"] == "STOP"                                # never the full 100


def test_outside_exhaust_window_five_hour_stop_is_80():
    for h in (2.5, 30, 100):
        pl, st, ph, _ = views(82, 30, h)
        assert ph == "none" and pl["mode"] == "STOP" and st == "THROTTLE"


def test_constants_have_one_source():
    assert E.PLAN_MIN == T.EXHAUST_H * 60 and T.five_ceiling(2.0) == 95 and T.five_ceiling(2.01) == 80
    assert S.SPAWN_CEIL == T.SPAWN_CEIL == 80 and S.LAST_DAY_CAP == T.LAST_DAY_CAP == 99 and S.LAST_DAY_H == T.LAST_DAY_H == 24


def test_grid_the_three_views_never_contradict():
    for login, host in (("A", "DESKTOP-F7IU69N"), ("B", "JIS-NUC"), ("B", "JIS-NB"), ("C", "JIS-NB"), ("C", "JIS-NUC")):
        for h in (1, 1.9, 3, 12, 23, 25, 48, 100, 160):
            for five in (0, 7, 30, 59, 65, 75, 82, 90, 96):
                for week in (5, 40, 70, 80, 90, 94, 98, 99.5):
                    pl, st, ph, cap = views(five, week, h, login, host)
                    where = (login, host, h, five, week, pl["mode"], st, ph)
                    # traffic says a login can spend -> supervisor must not zero it out (else work is routed to a login that refuses it)
                    if st == "SPEND" and week < cap:
                        assert pl["mode"] not in STOPS or five >= T.five_ceiling(h) - 10, where
                    # supervisor spends -> traffic must not throttle it
                    if pl["mode"] == "SPEND":
                        assert st != "THROTTLE", where
                    # exhaust window with room: the supervisor may not idle on the 5 h stop below 95
                    if ph in ("plan", "exhaust") and week < 98 and five < 85:
                        assert pl["mode"] != "STOP", where


def test_heartbeat_window_covers_a_supervisors_real_cadence():   # A heartbeats every 60-90 min; 75 asked the operator for a second one
    assert S.HEARTBEAT_MIN >= 100 and S.live_supervisors.__defaults__[0] == S.HEARTBEAT_MIN


def test_plan_never_names_the_merged_pipeliner_role():       # merged into Lead 2026-10-25 (2c9bbaf9c)
    src = Path(S.__file__).read_text(encoding="utf-8")
    assert "SPAWN Pipeliner" not in src and "You are Pipeliner" not in src


def test_operator_day_caps_for_login_c_oct31_nov01():
    assert S.weekly_cap("C", "JIS-NB", 80, "2026-10-31") == 70
    assert S.weekly_cap("C", "JIS-NB", 80, "2026-11-01") == 80
    assert S.weekly_cap("C", "JIS-NB", 80, "2026-11-02") == 85 and S.weekly_cap("C", "JIS-NB", 80) == 85
    assert S.weekly_cap("B", "JIS-NB", 80, "2026-10-31") == 75
