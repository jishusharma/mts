import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
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


def test_wait_wakes_when_a_ship_that_started_during_the_watch_frees_its_gate(tmp_path):
    """Soak 2026-10-22: a worker ships after the watcher started (gates 0 -> 1 -> 0) and is then gone; its worker slot stood empty
    until the 50 min timeout because only a drop below the baseline counted. A drop below the peak seen since the start wakes."""
    seq = iter([{"shas": {}, "ci_red": False, "busy_slots": b} for b in (0, 0, 1, 1, 0)])
    sleeps = []
    rc, reason = S.wait_for_transition(repo=tmp_path, shas=[], timeout=3000, interval=300, probe=lambda repo, shas: next(seq),
                                       fetcher=lambda repo: None, sleeper=lambda s: sleeps.append(s))
    assert rc == 0 and "slot freed (1 -> 0" in reason and len(sleeps) == 4
    steady = iter([{"shas": {}, "ci_red": False, "busy_slots": b} for b in (1, 2, 2, 2)])     # rising alone never wakes
    assert S.wait_for_transition(repo=tmp_path, shas=[], timeout=900, interval=300, probe=lambda repo, shas: next(steady),
                                 fetcher=lambda repo: None, sleeper=lambda s: None)[0] == 3
    late = iter([{"shas": {}, "ci_red": False, "busy_slots": b} for b in (None, 1, 1, 0)])    # gates unreadable at the start
    assert S.wait_for_transition(repo=tmp_path, shas=[], timeout=3000, interval=300, probe=lambda repo, shas: next(late),
                                 fetcher=lambda repo: None, sleeper=lambda s: None)[0] == 0


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
    hb = "BUDGET login=A 5h=10% week=30% reset=2026-10-22T19:59Z sup=JIS-NUC mode=NORMAL run=1 free=2 end=23:00Z"
    sigs = [(datetime(2026, 10, 18, 20, 40, tzinfo=timezone.utc), "jis-nuc/sharma", "note", hb),
            (datetime(2026, 10, 18, 20, 50, tzinfo=timezone.utc), "jis-nb/awgp", "note", "BUDGET login=C 5h=1% week=2%")]
    monkeypatch.setattr(traffic, "read_signals", lambda since, until, d=None: ([x for x in sigs if since <= x[0] <= until], None))
    p = S.read_peers("B", NOW, do_fetch=False)
    # A runs a supervisor with free slots (heartbeat); C only sent a BUDGET line (no supervisor): C is not in the shard
    assert p["active"] == ["A", "B"] and p["missing"] == [] and p["logins"]["C"]["age_h"] > 6
    assert p["live"]["A"]["host"] == "JIS-NUC" and "C" not in p["live"]


# ---------- five-hour loop (SUPER_LOOP.md): expected numbers computed by hand from the rules in the docstrings ----------
T0 = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)


def _rd(five, week, five_reset="2026-10-19T14:00Z", week_reset="2026-10-23T16:00Z", at=None):
    d = {"five": five, "week": week, "five_reset": five_reset, "week_reset": week_reset}
    if at:
        d["at"] = at
    return d


def test_pace_over_weekly_cap_is_stop():
    """B/C on JIS-NB stop at 75% of the week (rule 12): 88% used -> no room, no Claude worker."""
    assert S.weekly_cap("C", "JIS-NB") == 75 and S.weekly_cap("C", "JIS-NUC") == 95 and S.weekly_cap("A", "JIS-NB") == 95
    p = S.pace_plan(T0, _rd(7, 88, week_reset="2026-10-20T20:00Z"), 75)
    assert p["mode"] == "STOP" and p["slots"] == 0 and p["new"] == 0 and p["room"] == 0


def test_last_day_before_the_weekly_reset_spends_the_last_points_slowly():
    """Operator 2026-10-22: A at 97% with 15 h to its reset. Cap 95 -> STOP (points lost); last-day cap 99 over 3 windows ->
    2/3 wk pt here / 0.12 = 5.6 pts of 5 h -> 1 Claude worker, NORMAL. NB B/C keep their 75."""
    assert S.weekly_cap("A", "DESKTOP-F7IU69N", 15) == 99 and S.weekly_cap("A", "DESKTOP-F7IU69N", 30) == 95
    assert S.weekly_cap("A", "DESKTOP-F7IU69N") == 95 and S.weekly_cap("C", "JIS-NB", 15) == 75
    assert S.pace_plan(T0, _rd(2, 97, week_reset="2026-10-20T03:00Z"), 95)["mode"] == "STOP"
    p = S.pace_plan(T0, _rd(2, 97, week_reset="2026-10-20T03:00Z"), S.weekly_cap("A", "DESKTOP-F7IU69N", 15))
    assert p["room"] == 5.6 and p["slots"] == 1 and p["mode"] == "NORMAL"


def test_pace_spreads_weekly_room_over_windows_left():
    """week 20%, cap 95, reset 100 h away -> 20 windows; share 75/20 = 3.75 wk pts; k 0.12 -> 31.25 pts of 5 h; 5 h at 10% -> SPEND, 3 slots."""
    p = S.pace_plan(T0, _rd(10, 20, week_reset="2026-10-23T16:00Z"), 95)
    assert p["room"] == 31.2 and p["target"] == 41 and p["slots"] == 3 and p["mode"] == "SPEND" and not p["k_measured"]


def test_fresh_supervisor_starts_light_one_new_worker_per_wake():
    """Operator 2026-10-22: a bare start line opens with minimum workers and grows. 4 slots, 0 running -> start 1; 3 running -> 1."""
    p = S.pace_plan(T0, _rd(20, 50, week_reset="2026-10-19T15:00Z"), 95)
    assert p["slots"] == 4 and p["new"] == 1
    assert S.pace_plan(T0, _rd(20, 50, week_reset="2026-10-19T15:00Z"), 95, running=3)["new"] == 1


def test_pace_spends_everything_before_weekly_reset_but_not_past_80():
    """weekly reset in 3 h -> one window: share 45 wk pts / 0.12 = 375, capped at 80 - 20 = 60 -> 4 slots, target 80."""
    p = S.pace_plan(T0, _rd(20, 50, week_reset="2026-10-19T15:00Z"), 95)
    assert p["room"] == 60 and p["target"] == 80 and p["slots"] == 4


def test_pace_burn_projection_shrinks_workers():
    """First reading of this window 1 h ago at 10%, now 40%: burn 30/h, 2 h left -> projects 100% > target 80: 3 running -> at most 2, start 0."""
    first = _rd(10, 50, week_reset="2026-10-19T15:00Z", at="2026-10-19T11:00:00Z")
    p = S.pace_plan(T0, _rd(40, 50, week_reset="2026-10-19T15:00Z"), 95, hist=[first], running=3)
    assert p["burn"] == 30 and p["projected"] == 100 and p["slots"] == 2 and p["new"] == 0


def test_pace_window_bands_and_reset_window():
    assert S.pace_plan(T0, _rd(65, 10), 95)["mode"] == "CRUCIAL-ONLY"
    assert S.pace_plan(T0, _rd(72, 10), 95)["slots"] == 0
    fresh = S.pace_plan(T0, _rd(90, 10, five_reset="2026-10-19T11:00Z"), 95)   # window already reset: counts as 0%
    assert fresh["five"] == 0 and fresh["mode"] != "STOP"


def test_estimate_k_from_one_window():
    """5 h 10 -> 20 while week 50 -> 51: k = 1/10. Readings from another window are not paired."""
    h = [_rd(10, 50), _rd(20, 51), _rd(5, 52, five_reset="2026-10-19T19:00Z")]
    assert S.estimate_k(h) == 0.1
    assert S.estimate_k(h[:1]) is None


def test_heartbeat_is_a_budget_line_and_marks_live_supervisors():
    import traffic
    import mts_signal
    p = S.pace_plan(T0, _rd(10, 20), 95, running=1)
    t = S.heartbeat_text("B", "JIS-NB", p, dsa="up")
    assert len(t) < 200 and mts_signal.clean(t) == t
    m = traffic.BUDGET_RE.search(t)
    assert m and m.group(1) == "B" and m.group(2) == "10" and m.group(3) == "20" and m.group(4) == "2026-10-23T16:00Z"
    sigs = [(T0 - timedelta(minutes=10), "jis-nb/awgp", "note", t),
            (T0 - timedelta(minutes=200), "jis-nuc/sharma", "note", t.replace("login=B", "login=A")),   # too old
            (T0 - timedelta(minutes=5), "x/y", "note", "BUDGET login=C 5h=1% week=1%")]                # no sup=: not a supervisor
    live = S.live_supervisors(sigs, T0)
    assert list(live) == ["B"] and live["B"]["host"] == "JIS-NB" and live["B"]["free"] == p["new"] and live["B"]["dsa"] == "up"


def test_every_supervisor_sees_every_machines_gates():
    """Heartbeat carries gates=busy/total; plan prints one GATES line over all live machines (operator 2026-10-23)."""
    import mts_signal
    p = S.pace_plan(T0, _rd(10, 20), 95, running=2)
    t = S.heartbeat_text("A", "DESKTOP-F7IU69N", p, dsa="up", free=0, gates={"busy": 2, "total": 2, "free": 0, "pids": [1, 2]})
    assert len(t) < 200 and mts_signal.clean(t) == t and " gates=2/2 " in t
    old = S.heartbeat_text("C", "JIS-NB", p)                                   # a peer not yet on this code: no gates=
    live = S.live_supervisors([(T0 - timedelta(minutes=5), "x/y", "note", t), (T0 - timedelta(minutes=5), "x/y", "note", old)], T0)
    assert live["A"]["gates"] == (2, 2) and live["C"]["gates"] is None
    live["B"] = {"host": "JIS-NUC", "mode": "NORMAL", "run": 0, "free": 2, "at": "x", "dsa": None, "gates": (0, 2)}
    out = "\n".join(S.plan_lines("A", "DESKTOP-F7IU69N", p, live, {"ci": {"red": False}}, gate_key=False))
    assert "GATES DESKTOP-F7IU69N 2/2 busy; JIS-NB ?; JIS-NUC 0/2 busy; free 2 of 4 known" in out
    assert "PEER B on JIS-NUC" in out and "gates=0/2" in out and "free gates on JIS-NUC" in out
    assert "free gates on" not in "\n".join(S.plan_lines("B", "JIS-NUC", p, live, {"ci": {"red": False}}, gate_key=False))


def test_lane_owner_is_deterministic():
    live = {"C": {"host": "JIS-NUC"}, "A": {"host": "JIS-NB"}, "B": {"host": "JIS-NUC"}}
    assert S.lane_owner(live, "JIS-NUC") == "B"
    assert S.lane_owner(live) == "A" and S.lane_owner(live, "DESKTOP-F7IU69N") == "A"
    assert S.lane_owner({}) is None


def test_pick_cards_respects_host_lanes():
    rows = [{"id": "c1", "lane": "CODEX"}, {"id": "n1", "lane": "JIS-NB"}, {"id": "l1", "lane": "SONNET", "role": "Lab_Guy"},
            {"id": "s1", "lane": "SONNET", "weight": "ROUTINE"}, {"id": "s2", "lane": "HAIKU", "weight": "CRUCIAL"}, {"id": "d1", "lane": "DSA-NB"}]
    ids = lambda h, n=9, c=False: [r["id"] for r in S.pick_cards(rows, h, n, c)]
    assert ids("DESKTOP-F7IU69N") == ["s1", "s2"]
    assert ids("JIS-NB") == ["n1", "s1", "s2"]
    assert ids("JIS-NUC") == ["l1", "s1", "s2"]
    assert ids("JIS-NUC", 1) == ["l1"] and ids("JIS-NB", 9, True) == ["s2"]


def test_pick_cards_jis_nb_lane_follows_the_live_host_file(monkeypatch, tmp_path):
    """After the cutover (live_host.txt = laptop) the JIS-NB lane runs on the laptop, not on JIS-NB; missing file = JIS-NB."""
    rows = [{"id": "n1", "lane": "JIS-NB"}, {"id": "s1", "lane": "SONNET"}]
    f = tmp_path / "live_host.txt"
    monkeypatch.setattr(S, "LIVE_HOST_FILE", f)
    ids = lambda h: [r["id"] for r in S.pick_cards(rows, h, 9)]
    assert S.live_host() == "JIS-NB" and ids("JIS-NB") == ["n1", "s1"]
    f.write_text("desktop-f7iu69n", encoding="utf-8")
    assert S.live_host() == "DESKTOP-F7IU69N"
    assert ids("DESKTOP-F7IU69N") == ["n1", "s1"] and ids("JIS-NB") == ["s1"] and ids("JIS-NUC") == ["s1"]


def test_dsa_target_down_after_24h():
    rows = [{"status": "pending", "target": "DSA-NB", "posted": "2026-10-16T12:00:00Z"},
            {"status": "pending", "target": "DSA-NUC", "posted": "2026-10-19T10:00:00Z"},
            {"status": "done", "target": "DSA", "posted": "2026-10-01T00:00:00Z"}, {"status": "pending", "target": "JIS-NB", "posted": "x"}]
    d = S.dsa_targets_state(rows, T0)
    assert d == {"DSA-NB": {"pending": 1, "oldest_h": 72.0, "down": True}, "DSA-NUC": {"pending": 1, "oldest_h": 2.0, "down": False}}


def test_plan_lines_only_the_owner_runs_shared_lanes():
    p = S.pace_plan(T0, _rd(10, 20), 95)
    live = {"A": {"host": "JIS-NUC", "mode": "NORMAL", "run": 1, "free": 2, "at": "x", "dsa": "up"},
            "B": {"host": "JIS-NB", "mode": "NORMAL", "run": 0, "free": 3, "at": "x", "dsa": "down"}}
    ctx = {"codex_ready": 9, "dsa_unposted": 2, "picks": [{"id": "s1", "role": "Builder", "worker": "session"}], "ci": {"red": False},
           "dsa": {"DSA-NB": {"pending": 3, "oldest_h": 30, "down": True}}}
    a = "\n".join(S.plan_lines("A", "JIS-NUC", p, live, ctx, gate_key=False))
    b = "\n".join(S.plan_lines("B", "JIS-NB", p, live, ctx, gate_key=True))
    assert "RUN python scripts/dev/codex_run.py tick" in a and "codex_run" not in b       # NUC supervisor owns the GPT lab
    assert "desk.py assign" in a and "desk.py assign" not in b                          # lowest live login owns DSA posting
    assert "SPAWN 1: s1" in a and "PEER B on JIS-NB" in a and "AIBridge agent down on JIS-NB" in a
    assert "OPERATOR DeepSeek DSA-NB" in b and "nuc_wake" not in b                      # NUC has a supervisor: no headless wake
    red = "\n".join(S.plan_lines("A", "JIS-NUC", p, live, dict(ctx, ci={"red": True, "message": "2 failed"}), gate_key=False))
    assert "SPAWN 1: s1" not in red and "CI RED" in red


def test_plan_lines_run_session_planner_when_raw_cards_are_old():
    p = S.pace_plan(T0, _rd(10, 20), 95)
    live = {"A": {"host": "JIS-NUC", "mode": "NORMAL", "run": 0, "free": 3, "at": "x", "dsa": "up"}}
    ctx = {"ci": {"red": False}, "picks": [], "refine_raw": 4}
    on = "\n".join(S.plan_lines("A", "JIS-NUC", p, live, ctx, gate_key=False))
    off = "\n".join(S.plan_lines("A", "JIS-NUC", p, live, dict(ctx, refine_raw=0), gate_key=False))
    assert "RUN Session_Planner (Agent, sonnet): refine 4 raw cards" in on and "RUN Session_Planner" not in off


def test_plan_lines_ssh_gate_and_nuc_wake_only_when_allowed():
    p = S.pace_plan(T0, _rd(10, 20), 95)
    live = {"B": {"host": "JIS-NB", "mode": "NORMAL", "run": 0, "free": 3, "at": "x", "dsa": None}}
    ctx = {"codex_ready": 3, "spare": "card-x", "ci": {}, "picks": []}
    no = "\n".join(S.plan_lines("B", "JIS-NB", p, live, dict(ctx, nuc_ok=False), gate_key=True))
    yes = "\n".join(S.plan_lines("B", "JIS-NB", p, live, dict(ctx, nuc_ok=True), gate_key=True))
    assert "ssh -i ~/.ssh/nuc_gate" in no and "nuc_wake" not in no and "nuc_wake.py --card card-x" in yes
    nokey = "\n".join(S.plan_lines("B", "JIS-NB", p, live, dict(ctx, nuc_ok=True), gate_key=False))
    assert "ssh" not in nokey and "lab idle" in nokey and "PEER none live" in nokey


def test_nuc_budget_ok_fails_closed():
    inv = {"machines": {"JIS-NUC": {"logins": ["A", "C"]}}}
    fresh = lambda st: {"state": st, "at": "2026-10-19T11:30Z"}
    assert S.nuc_budget_ok("B", "NORMAL", T0, view={"logins": {"A": fresh("NORMAL"), "C": fresh("SPEND")}}, inv=inv)
    assert not S.nuc_budget_ok("B", "NORMAL", T0, view={"logins": {"A": fresh("NORMAL")}}, inv=inv)           # C unknown
    assert not S.nuc_budget_ok("B", "NORMAL", T0, view={"logins": {"A": fresh("NORMAL"), "C": fresh("THROTTLE")}}, inv=inv)
    assert not S.nuc_budget_ok("C", "STOP", T0, view={"logins": {"A": fresh("NORMAL"), "C": fresh("NORMAL")}}, inv=inv)
    assert not S.nuc_budget_ok("B", "NORMAL", T0, view=None, inv={"machines": {}})                            # error -> no


def test_handover_round_trip(tmp_path, monkeypatch):
    """handover writes the per-login file from the last plan; the next plan's ctx shows its Next line."""
    import sync
    monkeypatch.setattr(sync, "read_claims", lambda repo, ref: [("card-a", {"host": "JIS-NB"}), ("card-b", {"host": "JIS-NUC"})])
    home = tmp_path / "home"
    (home).mkdir()
    (home / "C-last-plan.json").write_text(json.dumps({"plan": S.pace_plan(T0, _rd(10, 20), 95), "live": {"A": {"host": "JIS-NUC"}},
                                                        "picks": ["s1"]}), encoding="utf-8")
    p = S.handover(tmp_path, "c", note="ship s1 then take s2", host="JIS-NB", home=home, now=T0)
    t = p.read_text(encoding="utf-8")
    assert p.name == "SUPERVISOR_C.md" and "- Next: ship s1 then take s2" in t and "card-a" in t and "card-b" not in t
    assert "A@JIS-NUC" in t and "You are Supervisor. Login C." in t and "\r" not in t


# ---------- review fixes (Sonnet + Haiku review 2026-10-19) ----------
def test_ended_heartbeat_removes_supervisor_and_free_override():
    p = S.pace_plan(T0, _rd(10, 20), 95)
    t = S.heartbeat_text("A", "JIS-NUC", p, free=1)
    assert " free=1 " in t and S.heartbeat_text("A", "JIS-NUC", p, free=0, mode="ENDED").count("mode=ENDED") == 1
    sigs = [(T0 - timedelta(minutes=20), "n/a", "note", t), (T0 - timedelta(minutes=5), "n/a", "note", S.heartbeat_text("A", "JIS-NUC", p, free=0, mode="ENDED"))]
    assert S.live_supervisors(sigs, T0) == {} and list(S.live_supervisors(sigs[:1], T0)) == ["A"]


def test_estimate_k_tolerates_reset_jitter():
    h = [_rd(10, 50, week_reset="2026-10-23T16:00:00.100Z"), _rd(20, 51, week_reset="2026-10-23T16:00:00.900Z")]
    assert S.estimate_k(h) == 0.1


def test_plan_lines_stop_and_unknown_peers_start_nothing_shared():
    stop = S.pace_plan(T0, _rd(85, 20), 95)
    live = {"A": {"host": "JIS-NUC", "mode": "STOP", "run": 0, "free": 0, "at": "x", "dsa": None}}
    ctx = {"pipeliner_free": True, "desk_pending": 5, "gemini_ready": 2, "codex_ready": 3, "ci": {}, "picks": []}
    a = "\n".join(S.plan_lines("A", "JIS-NUC", stop, live, ctx, gate_key=False))
    assert "Pipeliner" not in a and "Lab_Guy" not in a and "RUN python scripts/dev/codex_run.py tick" in a   # model-free lane still runs
    ok = S.pace_plan(T0, _rd(10, 20), 95)
    u = "\n".join(S.plan_lines("A", "JIS-NUC", ok, live, dict(ctx, peers_unknown=True, dsa_unposted=2), gate_key=False))
    assert "PEERS UNKNOWN" in u and "RUN python scripts/dev/codex_run" not in u and "desk.py assign" not in u and "PEER none" not in u


def test_cli_rejects_bad_percent(capsys):
    assert S.main(["plan", "--login", "C", "--five", "700", "--five-reset", "2026-10-19T14:00Z", "--week", "8",
                   "--week-reset", "2026-10-20T20:00Z", "--no-send", "--no-fetch"]) == 2


# ---------- d-six-slots-poll (operator 2026-10-23: "go with A + C") ----------
def _wait_with_plan(tmp_path, last, probe_state, timeout=900):
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    last = {"at": S._now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"), **last}
    (home / "B-last-plan.json").write_text(json.dumps(last), encoding="utf-8")
    sleeps = []
    rc, reason = S.wait_for_transition(repo=tmp_path, shas=[], timeout=timeout, interval=300, probe=lambda repo, shas: probe_state,
                                       fetcher=lambda repo: None, sleeper=sleeps.append, login="B", home=home)
    return rc, reason, sleeps


def test_wait_wakes_on_a_free_slot_with_ready_cards_not_after_50_min(tmp_path):
    """Option A: the plan started 1 of 4 (RAMP) and 6 more cards fit; CI green, 1 of 2 gates busy -> wake at the first poll (5 min)."""
    last = {"plan": {"mode": "NORMAL", "running": 0}, "spare": 3, "ready_more": 6, "stuck": 0}
    green = {"shas": {}, "ci_red": False, "busy_slots": 1, "total_slots": 2}
    rc, reason, sleeps = _wait_with_plan(tmp_path, last, green, timeout=3000)
    assert rc == 0 and reason.startswith("ACTIONABLE 3 worker slot(s) free, 6 more card(s) ready") and sleeps == [300]


def test_wait_actionable_fails_closed_and_stops_after_plans_that_spawn_nothing(tmp_path):
    last = {"plan": {"mode": "NORMAL", "running": 0}, "spare": 3, "ready_more": 6, "stuck": 0}
    green = {"shas": {}, "ci_red": False, "busy_slots": 1, "total_slots": 2}
    for bad_last, state in [(last, dict(green, ci_red=None)),                 # CI unknown
                            (last, dict(green, ci_red=True)),                 # CI red: the CI flip wakes it, not this
                            (last, dict(green, busy_slots=2)),                # every gate here busy
                            (last, dict(green, busy_slots=None)),             # gates unreadable
                            (dict(last, stuck=S.STUCK_MAX), green),           # two plans in a row spawned nothing
                            (dict(last, ready_more=0), green),                # no more cards
                            (dict(last, plan={"mode": "CRUCIAL-ONLY"}), green),
                            (dict(last, at="2026-10-18T01:00:00Z"), green),   # an old run's plan
                            (dict(last, at=None), green),                     # undated
                            (dict(last, spare=0), green)]:                    # slots full
        rc, _r, _s = _wait_with_plan(tmp_path, bad_last, state, timeout=600)
        assert rc == 3, (bad_last, state)
    rc, _r = S.wait_for_transition(repo=tmp_path, shas=[], timeout=600, interval=300, probe=lambda r, s: green,
                                   fetcher=lambda r: None, sleeper=lambda s: None)
    assert rc == 3          # no --login: the old watcher, transitions only


def test_ramp_stays_one_per_plan_the_actionable_wake_does_the_speed_up():
    """Review 2026-10-23: 'no gate busy' is true whenever no worker is mid-ship, so it was no sign of an idle machine; the start-light
    rule (q-light-supervisor-start) stays: one new worker per plan, and the ACTIONABLE wake makes the next plan come 5 min later."""
    rd = _rd(20, 50, week_reset="2026-10-19T15:00Z")
    assert S.pace_plan(T0, rd, 95)["new"] == 1 and S.pace_plan(T0, rd, 95, running=1)["new"] == 1
    import inspect
    assert "gates_idle" not in inspect.signature(S.pace_plan).parameters


def test_idle_machine_with_ready_cards_and_budget_gets_one_operator_line():
    """Option C: A live on DESKTOP; JIS-NB silent with B fresh NORMAL and SONNET cards -> start-a-Supervisor line; JIS-NUC's other
    login C is THROTTLE and A is busy -> no line for it. Only the shared-lane owner prints it."""
    inv = {"machines": {"DESKTOP-F7IU69N": {"logins": ["A", "B", "C"]}, "JIS-NB": {"logins": ["B", "C"]}, "JIS-NUC": {"logins": ["A", "C"]}}}
    fresh = lambda st, week=40: {"state": st, "at": "2026-10-19T11:30Z", "week": week}
    view = {"logins": {"A": fresh("THROTTLE"), "B": fresh("NORMAL"), "C": fresh("THROTTLE")}}
    live = {"A": {"host": "DESKTOP-F7IU69N", "mode": "NORMAL", "run": 1, "free": 0, "at": "x", "dsa": None}}
    rows = [{"id": f"c{i}", "lane": "SONNET"} for i in range(3)]
    idle = S.idle_hosts(live, rows, T0, view=view, inv=inv)
    assert idle == [("JIS-NB", ["B"], 3)]
    assert S.idle_hosts(live, [], T0, view=view, inv=inv) == []                                  # no cards: no line
    assert S.idle_hosts(live, rows, T0, view={"logins": {"B": {"state": "NORMAL", "at": "2026-10-18T01:00Z"}}}, inv=inv) == []   # stale
    p = S.pace_plan(T0, _rd(10, 20), 95)
    ctx = {"ci": {}, "picks": [], "idle_hosts": idle}
    a = "\n".join(S.plan_lines("A", "DESKTOP-F7IU69N", p, live, ctx, gate_key=False))
    assert "OPERATOR start a Supervisor on JIS-NB" in a and "`You are Supervisor. Login B.`" in a
    assert "supervisor.py wait --timeout 50m --login A" in a
    two = dict(live, B={"host": "JIS-NUC", "mode": "NORMAL", "run": 0, "free": 0, "at": "x", "dsa": None})
    assert "OPERATOR start" not in "\n".join(S.plan_lines("B", "JIS-NUC", p, two, ctx, gate_key=False))   # A owns it


def test_idle_machine_needs_room_under_that_machines_weekly_cap_and_a_known_state():
    """B at 80% of the week is NORMAL by pace but JIS-NB stops B/C at 75% (rule 12): no line there; DESKTOP (cap 95) still gets B.
    An unknown state ('UNKNOWN') or a reading from the future is not budget."""
    inv = {"machines": {"JIS-NB": {"logins": ["B", "C"]}, "DESKTOP-F7IU69N": {"logins": ["B"]}}}
    rows = [{"id": "c1", "lane": "SONNET"}]
    b80 = {"logins": {"B": {"state": "NORMAL", "at": "2026-10-19T11:30Z", "week": 80}}}
    assert S.idle_hosts({}, rows, T0, view=b80, inv=inv) == [("DESKTOP-F7IU69N", ["B"], 1)]
    for r in ({"state": "UNKNOWN", "at": "2026-10-19T11:30Z", "week": 10}, {"state": "NORMAL", "at": "2026-10-19T13:30Z", "week": 10},
              {"state": "NORMAL", "at": "2026-10-19T11:30Z", "week": "n/a"}):
        assert S.idle_hosts({}, rows, T0, view={"logins": {"B": r}}, inv=inv) == [], r
    assert S.idle_hosts({}, rows, T0, view={"logins": {}}, inv={"machines": None}) == []        # broken inventory: no line


def test_idle_line_is_said_once_per_machine_per_2h(tmp_path):
    rows = [("JIS-NB", ["B"], 3), ("JIS-NUC", ["C"], 1)]
    assert S._idle_nag_due(rows, T0, tmp_path) == rows
    (tmp_path / "idle_JIS-NB.last").write_text("2026-10-19T11:00:00Z", encoding="utf-8")     # 1 h ago
    assert S._idle_nag_due(rows, T0, tmp_path) == rows[1:]
    assert S._idle_nag_due(rows, T0 + timedelta(hours=1), tmp_path) == rows                     # 2 h later: due again


def test_one_login_is_never_offered_for_two_idle_machines():
    """Real signals 2026-10-22: B live on JIS-NUC; A (97%, last day: cap 99) and C free. DESKTOP gets A, JIS-NB gets C; with only C
    free, C goes to the first machine and the second gets no line."""
    inv = {"machines": {"DESKTOP-F7IU69N": {"logins": ["A", "B", "C"]}, "JIS-NB": {"logins": ["B", "C"]}, "JIS-NUC": {"logins": ["A", "C"]}}}
    rd = lambda st, week: {"state": st, "at": "2026-10-19T11:30Z", "week": week, "reset": "2026-10-20T03:00Z"}   # 15 h to reset
    view = {"logins": {"A": rd("NORMAL", 97), "B": rd("THROTTLE", 73), "C": rd("SPEND", 12)}}
    live = {"B": {"host": "JIS-NUC"}}
    rows = [{"id": "c1", "lane": "SONNET"}]
    assert S.idle_hosts(live, rows, T0, view=view, inv=inv) == [("DESKTOP-F7IU69N", ["A", "C"], 1), ("JIS-NB", ["C"], 1)]
    only_c = {"logins": {"A": rd("THROTTLE", 97), "B": rd("THROTTLE", 73), "C": rd("SPEND", 12)}}
    assert S.idle_hosts(live, rows, T0, view=only_c, inv=inv) == [("DESKTOP-F7IU69N", ["C"], 1)]
    far = {"logins": {"A": dict(rd("NORMAL", 97), reset="2026-10-23T03:00Z")}}                                  # 87 h: cap 95
    assert S.idle_hosts(live, rows, T0, view=far, inv=inv) == []


def _stub_plan_reads(monkeypatch, ci_red=False, picks=5):
    import traffic
    monkeypatch.setattr(S, "read_gate_slots", lambda repo: {"busy": 0, "total": 2})
    monkeypatch.setattr(S, "fetch_origin", lambda repo: None)
    monkeypatch.setattr(S, "read_ci", lambda **k: {"red": ci_red, "message": "x"})
    monkeypatch.setattr(S, "_git_show", lambda repo, rel: None)
    monkeypatch.setattr(S, "_dispatch_raw", lambda *a, **k: {"dispatch": [{"id": f"c{i}", "lane": "SONNET"} for i in range(picks)]})
    monkeypatch.setattr(S, "nuc_budget_ok", lambda *a, **k: False)
    monkeypatch.setattr(traffic, "read_signals", lambda a, b: ([], None))
    import mts_signal
    monkeypatch.setattr(mts_signal, "send", lambda *a, **k: True)


def _plan_run(tmp_path, running, minutes, send=True):
    """A real (send=True) plan also writes mts-budget.json under MTS_RELAY_HOME: kept inside tmp_path."""
    from unittest import mock
    rd = _rd(10, 20, five_reset="2026-10-19T15:00Z", week_reset="2026-10-23T16:00Z")
    with mock.patch.dict(os.environ, {"MTS_RELAY_HOME": str(tmp_path / "relay")}):
        return S.plan(tmp_path, "C", rd, running=running, send=send, no_fetch=True, host="JIS-NB", home=tmp_path,
                      now=T0 + timedelta(minutes=minutes))


def test_plan_counts_a_wake_that_started_none_of_its_new_workers_as_stuck(tmp_path, monkeypatch):
    """plan() end to end with the reads stubbed: the plan said start 1, running did not grow -> stuck 1, then 2; running grows -> 0.
    A plan older than PLAN_MAX_MIN is another run's: stuck starts over."""
    _stub_plan_reads(monkeypatch)
    monkeypatch.setattr(S, "idle_hosts", lambda *a, **k: [])
    d = _plan_run(tmp_path, 0, 0)[1]
    assert d["plan"]["new"] == 1 and d["free"] == 1 and d["spare"] == 2 and d["ready_more"] == 4 and d["stuck"] == 0
    assert _plan_run(tmp_path, 0, 6)[1]["stuck"] == 1 and _plan_run(tmp_path, 0, 12)[1]["stuck"] == 2
    assert _plan_run(tmp_path, 1, 18)[1]["stuck"] == 0
    _plan_run(tmp_path, 1, 24)
    assert _plan_run(tmp_path, 1, 24 + S.PLAN_MAX_MIN + 1)[1]["stuck"] == 0                            # old plan: fresh count


def test_ci_red_or_no_cards_never_counts_as_stuck(tmp_path, monkeypatch):
    """Review 2026-10-23: two red-CI plans must not switch the ACTIONABLE wake off for the green that follows (free was 0: nothing
    was asked); same for plans with no card to start."""
    _stub_plan_reads(monkeypatch, ci_red=True)
    monkeypatch.setattr(S, "idle_hosts", lambda *a, **k: [])
    for m in (0, 6, 12):
        d = _plan_run(tmp_path, 0, m)[1]
        assert d["free"] == 0 and d["stuck"] == 0
    _stub_plan_reads(monkeypatch, picks=0)
    for m in (18, 24, 30):
        assert _plan_run(tmp_path, 0, m)[1]["stuck"] == 0


def test_a_damaged_last_plan_never_breaks_the_next_plan(tmp_path, monkeypatch):
    _stub_plan_reads(monkeypatch)
    monkeypatch.setattr(S, "idle_hosts", lambda *a, **k: [])
    (tmp_path / "C-last-plan.json").write_text(json.dumps({"at": "2026-10-19T11:58:00Z", "free": "x", "plan": "NORMAL"}), encoding="utf-8")
    assert _plan_run(tmp_path, 0, 0)[1]["stuck"] == 0


def test_idle_line_reaches_plan_output_and_its_stamp_only_on_a_real_plan(tmp_path, monkeypatch):
    """C wired end to end: plan() prints the OPERATOR line; a --no-send dry run leaves no stamp, a real plan stamps the machine and
    the next plan within IDLE_NAG_H stays quiet."""
    import mts_signal
    _stub_plan_reads(monkeypatch)
    monkeypatch.setattr(S, "idle_hosts", lambda *a, **k: [("DESKTOP-F7IU69N", ["A"], 4)])
    monkeypatch.setattr(mts_signal, "send", lambda *a, **k: True)
    monkeypatch.setenv("MTS_RELAY_HOME", str(tmp_path / "relay"))
    line = "OPERATOR start a Supervisor on DESKTOP-F7IU69N"
    assert any(x.startswith(line) for x in _plan_run(tmp_path, 0, 0, send=False)[0]) and not (tmp_path / "idle_DESKTOP-F7IU69N.last").exists()
    assert any(x.startswith(line) for x in _plan_run(tmp_path, 0, 6, send=True)[0])
    assert (tmp_path / "idle_DESKTOP-F7IU69N.last").exists()
    assert not any(x.startswith(line) for x in _plan_run(tmp_path, 0, 12, send=True)[0])


def test_one_actionable_wake_per_plan(tmp_path):
    """Review 2026-10-23: a watcher restarted without a new plan (compaction, a slip) must not wake again on the same plan every 5 min."""
    last = {"plan": {"mode": "NORMAL", "running": 0}, "spare": 3, "ready_more": 6, "stuck": 0}
    green = {"shas": {}, "ci_red": False, "busy_slots": 0, "total_slots": 2}
    (tmp_path / "home").mkdir()
    at = S._now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
    (tmp_path / "home" / "B-last-plan.json").write_text(json.dumps(dict(last, at=at)), encoding="utf-8")
    run = lambda: S.wait_for_transition(repo=tmp_path, shas=[], timeout=900, interval=300, probe=lambda r, s: green,
                                        fetcher=lambda r: None, sleeper=lambda s: None, login="B", home=tmp_path / "home")[0]
    assert run() == 0 and run() == 3                # second watcher on the same plan: no wake
    (tmp_path / "home" / "B-last-plan.json").write_text(json.dumps(dict(last, at=(S._now_utc() - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))), encoding="utf-8")
    assert run() == 0                               # a new plan: wakes again


def test_unknown_weekly_percent_is_no_budget():
    inv = {"machines": {"DESKTOP-F7IU69N": {"logins": ["B"]}}}
    view = {"logins": {"B": {"state": "SPEND", "at": "2026-10-19T11:30Z", "week": None}}}
    assert S.idle_hosts({}, [{"id": "c1", "lane": "SONNET"}], T0, view=view, inv=inv) == []


def test_a_damaged_plan_file_never_wakes_and_never_kills_the_watcher(tmp_path):
    green = {"shas": {}, "ci_red": False, "busy_slots": 0, "total_slots": 2}
    for bad in ({"spare": "x", "ready_more": 2, "plan": {"mode": "NORMAL"}}, {"spare": 2, "ready_more": 2, "plan": "NORMAL"},
                {"spare": 2, "ready_more": 2, "plan": {"mode": "NORMAL"}, "stuck": [1]}):
        rc, _r, _s = _wait_with_plan(tmp_path, bad, green, timeout=600)
        assert rc == 3, bad
    (tmp_path / "home" / "B-last-plan.json").write_text("{not json", encoding="utf-8")
    rc, _r = S.wait_for_transition(repo=tmp_path, shas=[], timeout=600, interval=300, probe=lambda r, s: green,
                                   fetcher=lambda r: None, sleeper=lambda s: None, login="B", home=tmp_path / "home")
    assert rc == 3


def test_a_dry_run_plan_never_replaces_the_real_plan(tmp_path, monkeypatch):
    """Review round 2: `plan --no-send --running 0` after a real plan with running 2 must not reset the wake guard or bump stuck."""
    _stub_plan_reads(monkeypatch)
    monkeypatch.setattr(S, "idle_hosts", lambda *a, **k: [])
    monkeypatch.setenv("MTS_RELAY_HOME", str(tmp_path / "relay"))
    real = _plan_run(tmp_path, 2, 0)[1]
    _plan_run(tmp_path, 0, 3, send=False)
    assert json.loads((tmp_path / "C-last-plan.json").read_text(encoding="utf-8"))["at"] == real["at"]
    assert (tmp_path / "C-dryrun-plan.json").exists()


def test_garbled_marker_files_never_kill_the_watcher_or_the_plan(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    (home / "B-woke.txt").write_bytes(b"\xff\xfe\x00bad")
    (home / "idle_JIS-NB.last").write_bytes(b"\xff\xfe")
    assert S._woke_on("B", home) == ""
    assert S._idle_nag_due([("JIS-NB", ["B"], 1)], T0, home) == [("JIS-NB", ["B"], 1)]
