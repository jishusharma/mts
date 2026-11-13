import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import routines_due as R
import supervisor as S

WED = datetime(2026, 11, 11, 13, 20, tzinfo=timezone.utc)      # Wednesday
SAT = datetime(2026, 11, 14, 13, 20, tzinfo=timezone.utc)


def ids(runs):
    return " | ".join(runs)


def test_daily_due_then_not_due_after_marker(tmp_path):
    runs, _ = R.lines(tmp_path, tmp_path, WED, table=[t for t in R.ROUTINES if t[0] == "tasks_stale"])
    assert len(runs) == 1 and "tasks.py stale" in runs[0] and "routine-done tasks_stale" in runs[0]
    R.write_marker(tmp_path, "tasks_stale", WED)
    assert R.lines(tmp_path, tmp_path, WED, table=[t for t in R.ROUTINES if t[0] == "tasks_stale"]) == ([], [])
    nxt = datetime(2026, 11, 12, 0, 5, tzinfo=timezone.utc)      # next UTC day: due again
    assert R.lines(tmp_path, tmp_path, nxt, table=[t for t in R.ROUTINES if t[0] == "tasks_stale"])[0]


def test_daily_routines_cover_hygiene_scenario_stale(tmp_path):
    runs, _ = R.lines(tmp_path, tmp_path, WED, table=[t for t in R.ROUTINES if t[0] in ("hygiene", "scenario_score", "tasks_stale")])
    t = ids(runs)
    assert "daily_hygiene.py" in t and "scenario_ledger.py score" in t and "tasks.py stale" in t


def test_learner_window_and_file(tmp_path):
    tbl = [t for t in R.ROUTINES if t[0] == "live_aid_learn"]
    assert R.lines(tmp_path, tmp_path, datetime(2026, 11, 11, 20, 59, tzinfo=timezone.utc), tbl) == ([], [])      # before 21:00Z
    late = datetime(2026, 11, 11, 21, 30, tzinfo=timezone.utc)
    runs, _ = R.lines(tmp_path, tmp_path, late, tbl)
    assert len(runs) == 1 and "--date 2026-11-11" in runs[0]
    d = tmp_path / "MyTradingSys" / "research" / "live_aid_learning"
    d.mkdir(parents=True)
    (d / "2026-11-11.md").write_text("x")
    assert R.lines(tmp_path, tmp_path, late, tbl) == ([], [])      # today's file exists


def test_us_prep_phase_windows_weekday_and_file(tmp_path):
    tbl = [t for t in R.ROUTINES if t[0] == "us_prep"]
    runs, _ = R.lines(tmp_path, tmp_path, WED, tbl)               # 13:20Z = P2 window
    assert len(runs) == 1 and "--phase P2" in runs[0]
    assert R.lines(tmp_path, tmp_path, SAT, tbl) == ([], [])      # weekend
    assert R.lines(tmp_path, tmp_path, datetime(2026, 11, 11, 11, 0, tzinfo=timezone.utc), tbl) == ([], [])   # between windows
    out = tmp_path / "MyTradingSys" / "runtime" / "us_prep"
    out.mkdir(parents=True)
    (out / "2026-11-11_P2.md").write_text("x")
    assert R.lines(tmp_path, tmp_path, WED, tbl) == ([], [])      # phase file exists


def test_due_check_error_fails_closed_to_note(tmp_path, monkeypatch):
    def boom(repo, home, now):
        raise OSError("disk gone")
    runs, notes = R.lines(tmp_path, tmp_path, WED, table=[("x", 99, "Haiku", boom)])
    assert runs == [] and len(notes) == 1 and "due-check failed" in notes[0] and "OSError" in notes[0]
    # real check against a path that is not a git repo: also no RUN, one NOTE
    runs, notes = R.lines(tmp_path / "nope", tmp_path, WED, table=[t for t in R.ROUTINES if t[0] == "main_refresh"])
    assert runs == [] and len(notes) == 1 and "main_refresh" in notes[0]


def test_main_refresh_note_only_when_behind(tmp_path, monkeypatch):
    tbl = [t for t in R.ROUTINES if t[0] == "main_refresh"]
    monkeypatch.setattr(R, "main_checkout", lambda repo: Path("C:/main"))
    monkeypatch.setattr(R, "_git", lambda repo, *a: "51")
    runs, notes = R.lines(tmp_path, tmp_path, WED, tbl)
    assert runs == [] and "51 commits behind" in notes[0]          # a NOTE, never a RUN (the script stashes in a shared tree)
    monkeypatch.setattr(R, "_git", lambda repo, *a: "50")
    assert R.lines(tmp_path, tmp_path, WED, tbl) == ([], [])


def test_shots_overdue_note_count(tmp_path, monkeypatch):
    import shot
    tbl = [t for t in R.ROUTINES if t[0] == "shots_overdue"]
    monkeypatch.setattr(shot, "store_dir", lambda: tmp_path)
    monkeypatch.setattr(shot, "load_events", lambda s: [])
    monkeypatch.setattr(shot, "status_line", lambda S_, *a: ("x", [1, 2, 3]))
    runs, notes = R.lines(tmp_path, tmp_path, WED, tbl)
    assert runs == [] and "3 screenshot(s) overdue" in notes[0]
    monkeypatch.setattr(shot, "status_line", lambda S_, *a: ("x", []))
    assert R.lines(tmp_path, tmp_path, WED, tbl) == ([], [])


def test_plan_lines_emit_routine_runs_for_owner_only():
    p = S.pace_plan(datetime(2026, 11, 11, 13, 0, tzinfo=timezone.utc), _rd(), 95)
    live = {"A": {"host": "JIS-NB", "mode": "NORMAL", "run": 0, "free": 3, "at": "x", "dsa": "up"}}
    ctx = {"ci": {"red": False}, "routine_runs": ["RUN python scripts/dev/tasks.py stale; x"], "routine_notes": ["NOTE routine y (row 9): 3"]}
    mine = S.plan_lines("A", "JIS-NB", p, live, ctx, gate_key=False)
    assert "RUN python scripts/dev/tasks.py stale; x" in mine and "NOTE routine y (row 9): 3" in mine
    live2 = {"A": dict(live["A"], host="JIS-NUC"), "B": dict(live["A"], host="JIS-NB")}
    other = S.plan_lines("B", "JIS-NB", p, live2, ctx, gate_key=False)
    assert "RUN python scripts/dev/tasks.py stale; x" not in other and "NOTE routine y (row 9): 3" in other


def _rd():
    import test_supervisor as T
    return T._rd(10, 20)
