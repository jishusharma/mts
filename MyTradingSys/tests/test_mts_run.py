"""test_mts_run.py - scripts/dev/mts_run.py (RUN_MODEL.md phase 2). Expected values come from RUN_MODEL sections 2-4 and WORKERS.md rule 6,
not from the code. subprocess is mocked; no real claude is ever launched."""
import json
import subprocess
import sys

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import mts_run as m  # noqa: E402

UTC = timezone.utc


@pytest.fixture(autouse=True)
def _no_refresh(monkeypatch):
    monkeypatch.setenv("MTS_RUN_NO_REFRESH", "1")   # no test touches real git; the refresh tests clear it


def card(**kw):
    c = {"id": "x-1", "lane": "SONNET", "est_turns": 10, "weight": "ROUTINE", "approved_by": "", "title": "t"}
    c.update(kw)
    return c


def test_command_shape():
    cmd = m.build_command("BRIEF", "sonnet", 15, exe="claude")
    assert "--bare" not in cmd
    assert cmd[cmd.index("--tools") + 1] == "Bash,Read,Edit,Write,Grep,Glob"
    assert "--strict-mcp-config" in cmd
    assert cmd[cmd.index("--max-turns") + 1] == "15"
    assert cmd[cmd.index("--output-format") + 1] == "json"
    assert cmd[cmd.index("--permission-mode") + 1] == "auto"
    assert cmd[cmd.index("--permission-prompts") + 1] == "none"
    assert cmd[cmd.index("-p") + 1] == "BRIEF"


def test_max_turns_is_ceil_1_5x_default_30():
    assert m.max_turns(card(est_turns=7)) == 11
    assert m.max_turns(card(est_turns=10)) == 15
    assert m.max_turns(card(est_turns=None)) == 30


def test_model_rules():
    assert m.choose_model(card()) == "sonnet"
    assert m.choose_model(card(lane="HAIKU")) == "haiku"
    assert m.choose_model(card(lane="OPUS")) == "sonnet"
    assert m.choose_model(card(lane="OPUS", weight="CRUCIAL")) == "sonnet"
    assert m.choose_model(card(lane="OPUS", approved_by="op")) == "sonnet"
    assert m.choose_model(card(lane="OPUS", weight="CRUCIAL", approved_by="op")) == "opus"
    assert m.choose_model(card(lane="OPUS", weight="CRUCIAL", approved_by="op"), allow_opus=False) == "sonnet"
    assert m.choose_model(card(lane="SONNET", weight="CRUCIAL", approved_by="op")) == "sonnet"


def test_env_scrub():
    env = {"ANTHROPIC_API_KEY": "k", "ANTHROPIC_BASE_URL": "u", "CLAUDECODE": "1", "CLAUDE_CODE_X": "1",
           "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "2", "PATH": "p", "MTS_LOGIN": "A"}
    assert m.scrub_env(env) == {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "2", "PATH": "p", "MTS_LOGIN": "A"}


def test_parse_ok_and_error():
    ok = m.parse_result(json.dumps({"is_error": False, "num_turns": 6, "total_cost_usd": 0.094, "session_id": "s", "result": "done",
                                    "usage": {"input_tokens": 10, "cache_creation_input_tokens": 100,
                                              "cache_read_input_tokens": 1000, "output_tokens": 5}}))
    assert not ok["is_error"] and ok["turns"] == 6 and ok["cost"] == 0.094 and ok["cache_r"] == 1000 and ok["session_id"] == "s"
    assert m.parse_result(json.dumps({"is_error": False, "subtype": "error_max_turns", "num_turns": 15}))["is_error"]
    assert m.parse_result("not json")["is_error"]
    assert m.parse_result("")["is_error"]


def test_units_weights():
    assert m.units({"in": 100, "cache_w": 100, "cache_r": 100, "out": 10}) == 100 + 125 + 10 + 50


def test_ledger_roundtrip(tmp_path):
    p = tmp_path / "d" / "ledger.jsonl"
    m.append_ledger({"login": "A", "x": 1}, p)
    m.append_ledger({"login": "B", "x": 2}, p)
    assert [r["x"] for r in m.read_ledger(p)] == [1, 2]
    assert p.read_bytes().count(b"\n") == 2


def _pace(units_now, now):
    reset = now - timedelta(days=3.5)   # exactly half the week elapsed
    cal = {"A": {"used_pct": 10.0, "reset": reset.isoformat(), "at": (now - timedelta(days=1)).isoformat(), "units_at": 1000.0}}
    return cal, [{"login": "A", "ts": now.isoformat(), "in": units_now}]


def test_pace_boundaries():
    now = datetime(2026, 10, 22, 12, tzinfo=UTC)
    # 10% = 1000 units, so 1% = 100 units. Elapsed 50% = 5000 units; 90% = 9000 units.
    for u, want in ((1000, "run"), (5000, "run"), (5100, "slow"), (9000, "slow"), (9100, "stop")):
        cal, rows = _pace(u, now)
        assert m.pace("A", now, rows, cal)["decision"] == want, u
    cal, rows = _pace(0, now)
    assert abs(m.pace("A", now, rows, cal)["elapsed_pct"] - 50.0) < 0.01


def test_pace_uncalibrated_runs():
    now = datetime(2026, 10, 22, 12, tzinfo=UTC)
    r = m.pace("Z", now, [], {})
    assert r["decision"] == "run" and not r["calibrated"]


def test_calibrate_stores(tmp_path):
    now = datetime(2026, 10, 22, 12, tzinfo=UTC)
    led = tmp_path / "l.jsonl"
    m.append_ledger({"login": "A", "ts": now.isoformat(), "in": 700}, led)
    c = m.calibrate("A", 35, "2026-10-19T00:00:00+00:00", now, tmp_path / "c.json", led)
    assert c["used_pct"] == 35 and c["units_at"] == 700
    assert json.loads((tmp_path / "c.json").read_text())["A"]["used_pct"] == 35


def test_stop_detection(tmp_path):
    d = tmp_path / "MyTradingSys" / "system"
    d.mkdir(parents=True)
    (d / "ANNOUNCEMENTS.md").write_text("### A-20261018-1 INFO fine\n### A-20261022-2 STOP everything\n### A-20261022-3 HOLD x LIFTED\n",
                                        encoding="utf-8")
    assert m.active_stop(tmp_path) == {"A-20261022-2"}
    assert m.active_stop(tmp_path / "none") == set()


def _patch_run(monkeypatch, tmp_path, calls):
    monkeypatch.setattr(m, "pick_card", lambda cid=None, repo=None: card())
    monkeypatch.setattr(m, "sync", lambda *a, cwd=None: calls.append(a) or SimpleNamespace(returncode=0, stdout="", stderr=""))
    monkeypatch.setattr(m, "start_worktree", lambda slug: tmp_path)
    monkeypatch.setattr(m, "LEDGER", tmp_path / "led.jsonl")
    monkeypatch.setattr(m, "find_claude", lambda: "claude")


def test_once_failure_releases_claim(monkeypatch, tmp_path):
    calls, seen = [], {}
    _patch_run(monkeypatch, tmp_path, calls)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")

    def runner(cmd, **kw):
        seen.update(kw)
        return SimpleNamespace(returncode=1, stdout=json.dumps({"is_error": True, "num_turns": 3}), stderr="")
    st, row = m.run_once(login="A", runner=runner)
    assert st == "fail" and row["status"] == "FAILED" and row["card"] == "x-1"
    assert calls[0] == ("claim", "x-1") and ("release", "x-1") in calls
    assert "ANTHROPIC_API_KEY" not in seen["env"] and seen["cwd"] == str(tmp_path)
    assert m.read_ledger(tmp_path / "led.jsonl")[0]["login"] == "A"


def test_once_success_is_unverified_no_release(monkeypatch, tmp_path):
    calls = []
    _patch_run(monkeypatch, tmp_path, calls)
    out = json.dumps({"is_error": False, "num_turns": 4, "total_cost_usd": 0.1, "result": "shipped",
                      "usage": {"input_tokens": 1, "output_tokens": 2}})
    st, row = m.run_once(login="A", runner=lambda cmd, **kw: SimpleNamespace(returncode=0, stdout=out, stderr=""))
    assert st == "ok" and row["status"] == "UNVERIFIED" and row["turns"] == 4
    assert not any(c[0] == "release" for c in calls)


def test_once_timeout_is_failure(monkeypatch, tmp_path):
    _patch_run(monkeypatch, tmp_path, [])

    def runner(cmd, **kw):
        raise subprocess.TimeoutExpired(cmd, 1)
    st, row = m.run_once(login="A", runner=runner)
    assert st == "fail" and "timeout" in row["result"]


def test_loop_stops_on_hold_and_failures(monkeypatch):
    monkeypatch.setattr(m, "active_stop", lambda repo=None: {"A-1"})
    assert m.loop(1, "A") == "stopped"
    monkeypatch.setattr(m, "active_stop", lambda repo=None: set())
    monkeypatch.setattr(m, "pace", lambda login, **k: {"decision": "run"})
    n = []
    monkeypatch.setattr(m, "run_once", lambda **k: n.append(1) or ("fail", {}))
    assert m.loop(1, "A", sleep=lambda s: None) == "failures" and len(n) == 3


def test_loop_empty_queue_exits_when_hours_end(monkeypatch):
    monkeypatch.setattr(m, "active_stop", lambda repo=None: set())
    monkeypatch.setattr(m, "pace", lambda login, **k: {"decision": "run"})
    monkeypatch.setattr(m, "run_once", lambda **k: ("empty", None))
    t, sleeps = [0.0], []

    def sleep(s):
        sleeps.append(s)
        t[0] += s
    assert m.loop(0.5, "A", sleep=sleep, clock=lambda: t[0]) == "empty"
    assert sleeps and all(s == 600 for s in sleeps)


def test_run_once_refreshes_before_pick_and_survives_failure(monkeypatch, tmp_path, capsys):
    import sync as S
    monkeypatch.delenv("MTS_RUN_NO_REFRESH", raising=False)
    order = []
    monkeypatch.setattr(S, "merge_trunk", lambda repo: order.append("refresh") or 2)
    monkeypatch.setattr(m, "pick_card", lambda cid=None, repo=None: order.append("pick"))
    assert m.run_once(login="A")[0] == "empty" and order == ["refresh", "pick"]
    order.clear()

    def boom(repo):
        order.append("refresh")
        raise S.SyncError("fetch failed")
    monkeypatch.setattr(S, "merge_trunk", boom)
    assert m.run_once(login="A")[0] == "empty" and order == ["refresh", "pick"]   # failure: local cards still picked
    assert "refresh failed" in capsys.readouterr().out


def test_refresh_skipped_by_env(monkeypatch):
    import sync as S
    monkeypatch.setenv("MTS_RUN_NO_REFRESH", "1")
    monkeypatch.setattr(S, "merge_trunk", lambda repo: (_ for _ in ()).throw(AssertionError("must not refresh")))
    m.refresh_tree()


def test_loop_pace_stop(monkeypatch):
    monkeypatch.setattr(m, "active_stop", lambda repo=None: set())
    monkeypatch.setattr(m, "pace", lambda login, **k: {"decision": "stop"})
    assert m.loop(1, "A") == "pace-stop"


def test_summary():
    rows = [{"login": "A", "model": "sonnet", "turns": 3, "in": 10, "cost": 0.1, "status": "UNVERIFIED", "ts": "2026-10-22T00:00:00+00:00"},
            {"login": "A", "model": "sonnet", "turns": 2, "in": 5, "cost": 0.2, "status": "FAILED", "ts": "2026-10-22T00:00:00+00:00"}]
    s = m.summary(rows)[("A", "sonnet")]
    assert s["runs"] == 2 and s["fail"] == 1 and s["turns"] == 5 and s["units"] == 15
