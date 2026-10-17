import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ci_watch as W

NOW = datetime(2026, 10, 18, 0, 0, tzinfo=timezone.utc)


def run(sha, conclusion, at="2026-10-17T20:00:00Z"):
    return {"head_sha": sha * 8, "conclusion": conclusion, "created_at": at}


def test_two_failures_in_a_row_speak_and_name_the_last_green():
    runs = [run("a", None), run("b", "failure"), run("c", "cancelled"), run("d", "failure"), run("e", "success", "2026-10-17T20:19:00Z")]
    msg = W.message(runs, NOW)
    assert msg.startswith("CI RED: the newest 2 finished") and "bbbbbbbb" in msg and "3.7 h ago (eeeeeeee)" in msg


def test_flaky_pattern_that_fooled_the_green_ref_line_is_caught():
    # green ref keeps advancing between failures, so "oldest ungreen commit" looked fresh; the run conclusions do not
    runs = [run("a", "failure"), run("b", "failure"), run("c", "failure"), run("d", "success")]
    assert "newest 3 finished" in W.message(runs, NOW)


def test_single_failure_cancelled_and_green_stay_silent():
    assert W.message([run("a", "failure"), run("b", "success")], NOW) == ""
    assert W.message([run("a", "cancelled"), run("b", "cancelled"), run("c", "success")], NOW) == ""
    assert W.message([], NOW) == ""


def test_no_green_in_window_is_said():
    assert "no green run in the last 30" in W.message([run("a", "failure"), run("b", "failure")], NOW)


def test_hook_is_silent_when_offline(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("MTS_CI_WATCH_HOME", str(tmp_path))
    monkeypatch.setattr(W, "fetch", lambda: (_ for _ in ()).throw(OSError("offline")))
    assert W.hook() == 0 and capsys.readouterr().out == ""


def test_cache_avoids_a_second_call(monkeypatch, tmp_path):
    monkeypatch.setenv("MTS_CI_WATCH_HOME", str(tmp_path))
    calls = []
    monkeypatch.setattr(W, "fetch", lambda: calls.append(1) or [run("a", "failure")])
    W.current(); W.current()
    assert len(calls) == 1
    W.current(use_cache=False)
    assert len(calls) == 2
