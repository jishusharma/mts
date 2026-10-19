import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import supervisor as S


NOW = datetime(2026, 10, 18, 21, 0, 0, tzinfo=timezone.utc)


def test_sha_on_trunk_and_green(monkeypatch, tmp_path):
    """sha not on trunk -> false; sha on trunk -> true."""
    def fake_is_ancestor(repo, sha, ref):
        if sha == "aaa11111":
            return ref == "origin/fast-track"
        if sha == "bbb22222":
            return True
        return False

    monkeypatch.setattr(S, "is_ancestor", fake_is_ancestor)
    res = S.read_shas(tmp_path, ["aaa11111", "bbb22222", "ccc33333"])
    assert res["aaa11111"] == {"on_trunk": True, "on_green": False}
    assert res["bbb22222"] == {"on_trunk": True, "on_green": True}
    assert res["ccc33333"] == {"on_trunk": False, "on_green": False}


def test_sha_check_git_error_fails_closed(monkeypatch, tmp_path):
    """Any git failure/exception during sha check fails closed (False or error field, never True)."""
    def raising_ancestor(repo, sha, ref):
        raise RuntimeError("git merge-base crashed")

    monkeypatch.setattr(S, "is_ancestor", raising_ancestor)
    res = S.read_shas(tmp_path, ["deadbeef"])
    assert "error" in res["deadbeef"]
    assert res["deadbeef"].get("on_trunk") is not True


def test_failing_subcommands_fail_closed_with_error_field(monkeypatch, tmp_path):
    """Failing sub-command sets that sub-field to {'error': ...}, never a success value."""
    monkeypatch.setattr(S, "fetch_origin", lambda repo: None)
    monkeypatch.setattr(S, "_dispatch_raw", lambda repo, as_of: (_ for _ in ()).throw(RuntimeError("dispatch boom")))
    monkeypatch.setattr(S, "_desk_raw", lambda repo, as_of: (_ for _ in ()).throw(RuntimeError("desk boom")))
    monkeypatch.setattr(S, "_ci_raw", lambda: (_ for _ in ()).throw(OSError("ci offline")))
    monkeypatch.setattr(S, "_gate_slots_raw", lambda repo: (_ for _ in ()).throw(OSError("git common dir missing")))
    monkeypatch.setattr(S, "_lanes_raw", lambda repo: (_ for _ in ()).throw(ValueError("bad card json")))
    monkeypatch.setattr(S, "_budget_raw", lambda as_of, home=None: (_ for _ in ()).throw(OSError("disk error")))

    out = S.tick(repo=tmp_path, shas=[], no_fetch=True, as_of=NOW)
    for key in ("dispatch", "desk", "ci", "gate_slots", "lanes", "budget"):
        assert isinstance(out[key], dict) and "error" in out[key], f"{key} did not fail closed: {out[key]}"


def test_fetch_failure_recorded_fail_closed(monkeypatch, tmp_path):
    """If git fetch fails when not --no-fetch, fetch error is recorded without crashing tick."""
    def bad_fetch(repo):
        raise RuntimeError("fetch failed")

    monkeypatch.setattr(S, "fetch_origin", bad_fetch)
    out = S.tick(repo=tmp_path, shas=[], no_fetch=False, as_of=NOW, home=tmp_path)
    assert "error" in out.get("fetch", {})


def test_ci_red_and_green(monkeypatch):
    """CI red -> ci.red is True; CI green -> ci.red is False."""
    import ci_watch
    red_runs = [
        {"head_sha": "11111111deadbeef", "conclusion": "failure", "created_at": "2026-10-18T20:30:00Z"},
        {"head_sha": "22222222deadbeef", "conclusion": "failure", "created_at": "2026-10-18T20:00:00Z"},
        {"head_sha": "33333333deadbeef", "conclusion": "success", "created_at": "2026-10-18T19:00:00Z"},
    ]
    monkeypatch.setattr(ci_watch, "current", lambda use_cache=True: red_runs)
    ci_res = S.read_ci(now=NOW)
    assert ci_res["red"] is True
    assert ci_res["streak"] == 2
    assert "CI RED" in ci_res["message"]

    green_runs = [
        {"head_sha": "44444444deadbeef", "conclusion": "success", "created_at": "2026-10-18T20:45:00Z"},
        {"head_sha": "11111111deadbeef", "conclusion": "failure", "created_at": "2026-10-18T20:30:00Z"},
    ]
    monkeypatch.setattr(ci_watch, "current", lambda use_cache=True: green_runs)
    ci_ok = S.read_ci(now=NOW)
    assert ci_ok["red"] is False
    assert ci_ok["streak"] == 0


def test_gate_slots_busy_count(monkeypatch, tmp_path):
    """gate_slots counts alive PIDs in <git-common-dir>/gate-slots/slot-* and ignores dead PIDs."""
    slots_dir = tmp_path / "gate-slots"
    slots_dir.mkdir(parents=True)
    (slots_dir / "slot-0").write_text("1001", encoding="utf-8")
    (slots_dir / "slot-1").write_text("1002", encoding="utf-8")

    monkeypatch.setattr(S, "gate_slots_dir", lambda repo: slots_dir)
    monkeypatch.setattr(S, "pid_alive", lambda pid: pid == 1001)

    gs = S.read_gate_slots(tmp_path)
    assert gs["busy"] == 1
    assert gs["total"] == 2
    assert 1001 in gs["pids"]
    assert 1002 not in gs["pids"]


def test_lanes_ready_depth_and_dispatch_top_8(monkeypatch, tmp_path):
    """dispatch returns top 8 ready cards; lanes counts ready cards for CODEX, SONNET, GEMINI."""
    fake_cards = [{"id": f"c{i}", "rank": i, "lane": "SONNET"} for i in range(1, 12)]
    monkeypatch.setattr(
        S,
        "_dispatch_raw",
        lambda repo, as_of: {"as_of": "2026-10-18T21:00:00Z", "dispatch": fake_cards, "excluded": [{"id": "x1", "reason_code": "claimed"}]},
    )
    disp = S.read_dispatch(tmp_path, as_of=NOW)
    assert len(disp["top"]) == 8
    assert [c["id"] for c in disp["top"]] == [f"c{i}" for i in range(1, 9)]
    assert disp["total_ready"] == 11

    ready_by_lane = {
        "CODEX": [{"id": "cx1"}, {"id": "cx2"}, {"id": "cx3"}],
        "SONNET": [{"id": "sn1"}, {"id": "sn2"}],
        "HAIKU": [{"id": "hk1"}],
        "GEMINI": [{"id": "gm1"}],
    }
    monkeypatch.setattr(S, "_ready_for_lane", lambda repo, lane: ready_by_lane.get(lane, []))
    lanes = S.read_lanes(tmp_path)
    assert lanes["CODEX"] == 3
    assert lanes["SONNET"] == 2
    assert lanes["GEMINI"] == 1
    assert lanes["codex"] == 3
    assert lanes["sonnet"] == 2
    assert lanes["gemini"] == 1


def test_budget_age_and_missing(tmp_path):
    """~/.claude/mts-budget.json age in seconds/hours and state, or {'error': 'missing'} when absent."""
    missing = S.read_budget(as_of=NOW, home=tmp_path)
    assert missing == {"error": "missing"}

    budget_file = tmp_path / "mts-budget.json"
    budget_file.write_text(
        json.dumps({
            "utc": "2026-10-18T19:30:00Z",
            "weekly_all_pct": 30.0,
            "weekly_resets_at": "2026-10-20T00:00:00Z",
            "five_hour_pct": 15.0,
        }),
        encoding="utf-8",
    )
    b = S.read_budget(as_of=NOW, home=tmp_path)
    assert "error" not in b
    assert b["age_s"] == 5400
    assert b["age_h"] == 1.5
    assert b["state"] in ("SPEND", "NORMAL", "THROTTLE")
    assert b["five_hour_pct"] == 15.0
    assert b["weekly_all_pct"] == 30.0


def test_wait_sha_already_on_trunk_at_baseline_does_not_exit_until_new_sha_lands(tmp_path):
    """sha already on trunk at baseline start -> does NOT exit immediately; new sha lands (false -> true) -> exits 0 with one-line reason."""
    polls = [
        # baseline: sha1 already on trunk, sha2 not on trunk
        {"shas": {"sha1": True, "sha2": False}, "ci_red": False, "busy_slots": 0},
        # poll 1: still same (sha1 True, sha2 False) -> must NOT exit
        {"shas": {"sha1": True, "sha2": False}, "ci_red": False, "busy_slots": 0},
        # poll 2: sha2 lands (False -> True) -> exits 0
        {"shas": {"sha1": True, "sha2": True}, "ci_red": False, "busy_slots": 0},
    ]
    idx = [0]
    sleeps = []

    def fake_probe(repo, shas):
        cur = polls[min(idx[0], len(polls) - 1)]
        idx[0] += 1
        return cur

    rc, reason = S.wait_for_transition(
        repo=tmp_path,
        shas=["sha1", "sha2"],
        timeout=3000,
        interval=300,
        probe=fake_probe,
        fetcher=lambda repo: None,
        sleeper=lambda s: sleeps.append(s),
    )
    assert rc == 0
    assert "sha2" in reason
    assert "\n" not in reason.strip()
    assert len(sleeps) == 2


def test_wait_ci_flips_false_to_true_and_true_to_false(tmp_path):
    """CI flips (false -> true or true -> false) -> exits 0 with one-line reason; already red at start does not exit until flip."""
    def run_seq(seq):
        it = iter(seq)
        return S.wait_for_transition(
            repo=tmp_path,
            shas=[],
            timeout=900,
            interval=300,
            probe=lambda repo, shas: next(it),
            fetcher=lambda repo: None,
            sleeper=lambda s: None,
        )

    rc_red, msg_red = run_seq([
        {"shas": {}, "ci_red": False, "busy_slots": 0},
        {"shas": {}, "ci_red": True, "busy_slots": 0},
    ])
    assert rc_red == 0 and "ci" in msg_red.lower()

    # Already red at baseline -> poll 1 still red (no exit) -> poll 2 green (exits 0)
    rc_green, msg_green = run_seq([
        {"shas": {}, "ci_red": True, "busy_slots": 0},
        {"shas": {}, "ci_red": True, "busy_slots": 0},
        {"shas": {}, "ci_red": False, "busy_slots": 0},
    ])
    assert rc_green == 0 and "ci" in msg_green.lower()


def test_wait_busy_slot_frees_transition(tmp_path):
    """busy slot frees (busy -> free transition) -> exits 0; already free at baseline does not exit."""
    seq = iter([
        {"shas": {}, "ci_red": False, "busy_slots": 2},
        {"shas": {}, "ci_red": False, "busy_slots": 2},
        {"shas": {}, "ci_red": False, "busy_slots": 1},
    ])
    rc, reason = S.wait_for_transition(
        repo=tmp_path,
        shas=[],
        timeout=900,
        interval=300,
        probe=lambda repo, shas: next(seq),
        fetcher=lambda repo: None,
        sleeper=lambda s: None,
    )
    assert rc == 0
    assert "slot" in reason.lower()


def test_wait_timeout_exits_3(tmp_path):
    """timeout reached with no transition -> exits 3."""
    steady = {"shas": {"sha1": True, "sha2": False}, "ci_red": False, "busy_slots": 0}
    sleeps = []
    rc, reason = S.wait_for_transition(
        repo=tmp_path,
        shas=["sha1", "sha2"],
        timeout=600,
        interval=300,
        probe=lambda repo, shas: steady,
        fetcher=lambda repo: None,
        sleeper=lambda s: sleeps.append(s),
    )
    assert rc == 3
    assert "timeout" in reason.lower()
    assert sum(sleeps) >= 600


def _fake_cards(n=12):
    return [{"id": f"card-{i:02d}", "title": "t", "lane": "SONNET", "state": "ready", "prio": 3, "created": f"2026-10-1{i % 9}"}
            for i in range(n)]


def test_dispatch_shards_cards_across_logins(monkeypatch):
    """Three supervisors get disjoint own-shard heads; one supervisor alone is unsharded (same order as before)."""
    import tasks
    monkeypatch.setattr(tasks, "exclusion", lambda *a, **k: None)
    cards = _fake_cards()
    args = (cards, {}, [], {}, {}, NOW, "JIS-NB")
    owned = {}
    for lg in "ABC":
        snap = tasks.dispatch(*args, login=lg, logins=["A", "B", "C"])
        own = [r["id"] for r in snap["dispatch"] if r["own"]]
        assert [r["id"] for r in snap["dispatch"][:len(own)]] == own      # own shard ranked first
        owned[lg] = set(own)
    assert owned["A"] | owned["B"] | owned["C"] == {c["id"] for c in cards}
    assert not (owned["A"] & owned["B"]) and not (owned["B"] & owned["C"]) and not (owned["A"] & owned["C"])
    assert all(owned[lg] for lg in "ABC")
    solo = tasks.dispatch(*args, login="A", logins=["A"])
    assert "own" not in solo["dispatch"][0]
    assert [r["id"] for r in solo["dispatch"]] == [r["id"] for r in tasks.dispatch(*args)["dispatch"]]


def test_tick_reports_peers_and_unknown_login(monkeypatch, tmp_path):
    """tick names the active logins from BUDGET lines and says plainly when MTS_LOGIN is not set."""
    import traffic
    monkeypatch.delenv("MTS_LOGIN", raising=False)
    out = S.tick(repo=tmp_path, no_fetch=True, as_of=NOW, home=tmp_path)
    assert out["login"] is None and "MTS_LOGIN" in out["peers"]["error"]
    fresh = {"state": "NORMAL", "five_h": 10, "week": 30, "reset": "2026-10-22T19:59Z", "at": "2026-10-18T20:00Z"}
    old = dict(fresh, at="2026-10-17T01:00Z")
    monkeypatch.setattr(traffic, "budget_view", lambda do_fetch=True, now=None, hours=48: (
        {"logins": {"A": fresh, "C": old}, "overall": "NORMAL", "why": ""}, []))
    p = S.read_peers("B", NOW, do_fetch=False)
    assert p["active"] == ["A", "B"] and p["missing"] == ["B"] and p["logins"]["C"]["age_h"] > 6
