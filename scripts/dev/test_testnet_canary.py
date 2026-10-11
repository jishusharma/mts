"""Tests for scripts/dev/testnet_canary.py. Expected outcomes come from the canary rules, not from the script.

Set CANARY_PATH to test a staged copy (e.g. testnet_canary.py.new); default is testnet_canary.py beside this file.
"""
import builtins
import importlib.machinery
import importlib.util
import json
import os
import pathlib
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = pathlib.Path(os.environ.get("CANARY_PATH", HERE / "testnet_canary.py"))


def load():
    loader = importlib.machinery.SourceFileLoader("testnet_canary_under_test", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


canary = load()  # fails (collection error) when the script does not exist

NOW = "2026-10-02T12:00:00Z"
NOW_EPOCH = 1790942400.0  # 2026-10-02T12:00:00Z
ROLE_CMDS = {
    "auto_trader": "python MyTradingSys/execution/auto_trader.py",
    "position_manager": "python MyTradingSys/execution/position_manager.py",
    "daily_loss_monitor": "python MyTradingSys/execution/daily_loss_monitor.py",
    "live_runner_cli": "python MyTradingSys/backtest/live_runner_cli.py",
    "loop-supervisor": "powershell -File runtime_data/loop-supervisor.ps1",
    "start-trading-day": "powershell -File scripts/start-trading-day.ps1",
    "java": "java -jar MyTradingSys/feed.jar",
}


def sh(repo, *a, env=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"] + list(a),
                          capture_output=True, text=True, env=e, check=True)


def touch(path, text="x", age_s=60):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    t = NOW_EPOCH - age_s
    os.utime(path, (t, t))


def make_repo(tmp_path, loop_age_min=1):
    repo = tmp_path / "repo"
    repo.mkdir()
    sh(repo, "init", "-q")
    touch(repo / "README.md", "r")
    sh(repo, "add", "-A")
    sh(repo, "commit", "-q", "-m", "init", env={"GIT_COMMITTER_DATE": "2026-10-01T00:00:00Z",
                                                "GIT_AUTHOR_DATE": "2026-10-01T00:00:00Z"})
    rd = repo / "runtime_data"
    ts = (canary.parse_iso(NOW) - canary.timedelta(minutes=loop_age_min)).strftime("%Y-%m-%dT%H:%M:%S.0000000Z")
    touch(rd / "loop_state.json", json.dumps({"ts_utc": ts}))
    touch(rd / "supervisor_log.txt")
    touch(rd / "apparatus_log.txt")
    touch(rd / "alert_counter.txt", "82\n")
    ex = repo / "MyTradingSys" / "execution"
    touch(ex / "auto_trader_state.json", json.dumps({"tom_last_alert_no": 81}))
    touch(ex / "auto_trades.jsonl", json.dumps({"ts": "2026-10-02T11:00:00Z", "event": "x"}) + "\n")
    touch(repo / "MyTradingSys" / "runtime" / "alerts" / "1m.jsonl")
    return repo


def procs(tmp_path, drop=(), start="2026-10-02T00:00:00Z"):
    ms = int(canary.parse_iso(start).timestamp() * 1000)
    rows = [{"ProcessId": 100 + i, "CreationDate": "/Date(%d)/" % ms,
             "CommandLine": cmd} for i, (role, cmd) in enumerate(ROLE_CMDS.items()) if role not in drop]
    rows.append({"ProcessId": 1, "CreationDate": None, "CommandLine": None})
    p = tmp_path / "procs.json"
    p.write_text(json.dumps(rows), encoding="utf-8")
    return p


def run(capsys, repo, tmp_path, *extra, proc=None):
    argv = ["--repo", str(repo), "--now", NOW, "--out-dir", str(tmp_path / "out")]
    argv += ["--proc-json", str(proc)] if proc else []
    code = canary.main(argv + list(extra))
    return code, capsys.readouterr().out


def test_all_fresh_all_roles_green(tmp_path, capsys):
    repo = make_repo(tmp_path)
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert out.splitlines()[0].startswith("CANARY GREEN 2026-10-02T12:00:00Z"), out
    assert code == 0
    md = (tmp_path / "out" / "CANARY_2026-10-02.md").read_text(encoding="utf-8")
    assert "## 2026-10-02T12:00:00Z GREEN" in md and "| check | status | detail |" in md


def test_loop_state_6_min_old_is_red(tmp_path, capsys):
    repo = make_repo(tmp_path, loop_age_min=6)
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 2 and out.startswith("CANARY RED")
    assert "loop_state" in out


def test_loop_state_4_min_old_is_ok(tmp_path, capsys):
    repo = make_repo(tmp_path, loop_age_min=4)
    code, _ = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 0


def test_log_stale_11_min_is_red(tmp_path, capsys):
    repo = make_repo(tmp_path)
    t = NOW_EPOCH - 11 * 60
    os.utime(repo / "runtime_data" / "apparatus_log.txt", (t, t))
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 2 and "apparatus_log" in out


def test_alert_gap_12_is_red(tmp_path, capsys):
    repo = make_repo(tmp_path)
    (repo / "runtime_data" / "alert_counter.txt").write_text("82\n")
    (repo / "MyTradingSys/execution/auto_trader_state.json").write_text(json.dumps({"tom_last_alert_no": 70}))
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 2
    assert "12 Tom alerts not seen by auto_trader" in out


def test_alert_gap_2_is_ok(tmp_path, capsys):
    repo = make_repo(tmp_path)
    (repo / "MyTradingSys/execution/auto_trader_state.json").write_text(json.dumps({"tom_last_alert_no": 80}))
    code, _ = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 0


def test_alert_counter_missing_is_warn(tmp_path, capsys):
    repo = make_repo(tmp_path)
    (repo / "runtime_data" / "alert_counter.txt").unlink()
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 1 and out.startswith("CANARY WARN")


def test_process_query_failure_is_red(tmp_path, capsys, monkeypatch):
    repo = make_repo(tmp_path)

    def boom():
        raise OSError("powershell unavailable")
    monkeypatch.setattr(canary, "query_processes", boom)
    code, out = run(capsys, repo, tmp_path)
    assert code == 2 and "process query failed" in out


def test_unparseable_proc_json_is_red(tmp_path, capsys):
    repo = make_repo(tmp_path)
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    code, out = run(capsys, repo, tmp_path, proc=bad)
    assert code == 2 and "process query failed" in out


def test_auto_trader_missing_is_red(tmp_path, capsys):
    repo = make_repo(tmp_path)
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path, drop=("auto_trader",)))
    assert code == 2 and "auto_trader" in out


def test_position_manager_missing_never_red(tmp_path, capsys):
    repo = make_repo(tmp_path)
    code, _ = run(capsys, repo, tmp_path, proc=procs(tmp_path, drop=("position_manager",)))
    assert code in (0, 1)


def test_no_proc_skips(tmp_path, capsys):
    repo = make_repo(tmp_path)
    code, out = run(capsys, repo, tmp_path, "--no-proc")
    assert code == 0 and out.startswith("CANARY GREEN")
    assert "SKIPPED" in (tmp_path / "out" / "CANARY_2026-10-02.md").read_text(encoding="utf-8")


def test_halt_present_warn_and_never_opened(tmp_path, capsys, monkeypatch):
    repo = make_repo(tmp_path)
    halt = repo / "MyTradingSys" / "execution" / "HALT"
    halt.write_bytes(b"\xff\xfe\x00garbage")
    real_open = builtins.open
    real_read_text = pathlib.Path.read_text
    real_read_bytes = pathlib.Path.read_bytes
    real_popen = pathlib.Path.open

    def guard(p):
        if pathlib.Path(str(p)).name in ("HALT", "HALT_DAILY_LOSS", "AUTO_PAUSE"):
            raise AssertionError("brake file opened: %s" % p)

    monkeypatch.setattr(builtins, "open", lambda f, *a, **k: (guard(f), real_open(f, *a, **k))[1])
    monkeypatch.setattr(pathlib.Path, "read_text", lambda self, *a, **k: (guard(self), real_read_text(self, *a, **k))[1])
    monkeypatch.setattr(pathlib.Path, "read_bytes", lambda self, *a, **k: (guard(self), real_read_bytes(self))[1])
    monkeypatch.setattr(pathlib.Path, "open", lambda self, *a, **k: (guard(self), real_popen(self, *a, **k))[1])
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 1 and out.startswith("CANARY WARN") and "HALT" in out


def test_state_not_written_without_flag(tmp_path, capsys):
    repo = make_repo(tmp_path)
    run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert not (repo / "runtime_data" / "canary_state.json").exists()


def test_state_written_with_flag(tmp_path, capsys):
    repo = make_repo(tmp_path)
    run(capsys, repo, tmp_path, "--write-state", proc=procs(tmp_path))
    head = sh(repo, "rev-parse", "HEAD").stdout.strip()
    st = json.loads((repo / "runtime_data" / "canary_state.json").read_text())
    assert st == {"last_commit": head}


def commit_live(repo, rel, date):
    touch(repo / rel, "# change")
    sh(repo, "add", rel)
    sh(repo, "commit", "-q", "-m", "live path change", env={"GIT_COMMITTER_DATE": date, "GIT_AUTHOR_DATE": date})


def test_live_commit_newer_than_process_start_restart_needed(tmp_path, capsys):
    repo = make_repo(tmp_path)
    commit_live(repo, "MyTradingSys/execution/auto_trader.py", "2026-10-02T06:00:00Z")
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path, start="2026-10-02T00:00:00Z"))
    assert code == 1
    assert "RESTART NEEDED (supervisor only): auto_trader" in out


def test_live_commit_older_than_process_start_no_restart(tmp_path, capsys):
    repo = make_repo(tmp_path)
    commit_live(repo, "MyTradingSys/execution/auto_trader.py", "2026-10-02T06:00:00Z")
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path, start="2026-10-02T08:00:00Z"))
    assert code == 0 and "RESTART NEEDED" not in out


def test_alerts_layer_commit_flags_restart(tmp_path, capsys):
    repo = make_repo(tmp_path)
    commit_live(repo, "MyTradingSys/backtest/layers/alerts/foo.py", "2026-10-02T06:00:00Z")
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 1 and "RESTART NEEDED (supervisor only)" in out


def test_non_live_commit_does_not_flag(tmp_path, capsys):
    repo = make_repo(tmp_path)
    commit_live(repo, "docs/notes.md", "2026-10-02T06:00:00Z")
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 0


def test_no_ids_or_secrets_in_output(tmp_path, capsys):
    repo = make_repo(tmp_path)
    touch(repo / "MyTradingSys" / "execution" / "auto_trades.jsonl",
          json.dumps({"ts": "2026-10-02T11:00:00Z", "plan_id": "L-mkt-0929-2215", "api_key": "abcdEFGH12345678xyz"}) + "\n")
    _, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    md = (tmp_path / "out" / "CANARY_2026-10-02.md").read_text(encoding="utf-8")
    for s in ("L-mkt-0929-2215", "abcdEFGH12345678xyz"):
        assert s not in out and s not in md


# --- module-form launches (mts.ps1:246 starts the trader as `python -m MyTradingSys.execution.auto_trader`)
MODULE_FORM = {
    "auto_trader": r'"C:\Python\python.exe" -m MyTradingSys.execution.auto_trader',
    "daily_loss_monitor": "python -m MyTradingSys.execution.daily_loss_monitor",
}


def procs_with(tmp_path, replace=None, extra=()):
    rows = json.loads(procs(tmp_path).read_text(encoding="utf-8"))
    ms = rows[0]["CreationDate"]
    for r in rows:
        for role, cmd in (replace or {}).items():
            if r["CommandLine"] == ROLE_CMDS[role]:
                r["CommandLine"] = cmd
    rows += [{"ProcessId": 900 + i, "CreationDate": ms, "CommandLine": c} for i, c in enumerate(extra)]
    p = tmp_path / "procs2.json"
    p.write_text(json.dumps(rows), encoding="utf-8")
    return p


def test_module_form_launch_counts_as_running(tmp_path, capsys):
    repo = make_repo(tmp_path)
    code, out = run(capsys, repo, tmp_path, proc=procs_with(tmp_path, replace=MODULE_FORM))
    assert out.splitlines()[0].startswith("CANARY GREEN"), out
    assert "proc:auto_trader | OK | 1 running" in (tmp_path / "out" / "CANARY_2026-10-02.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("decoy", [
    r"cmd /c type MyTradingSys\execution\auto_trader_state.json",
    "powershell Get-Content MyTradingSys/execution/auto_trader.log -Tail 5",
    "python scripts/dev/make_auto_trader_report.py",
    "pwsh -Command $Host.UI.RawUI.WindowTitle = 'MTS auto-trader'",
])
def test_non_launch_command_lines_are_not_the_trader(tmp_path, capsys, decoy):
    repo = make_repo(tmp_path)
    rows = json.loads(procs(tmp_path, drop=("auto_trader",)).read_text(encoding="utf-8"))
    rows.append({"ProcessId": 950, "CreationDate": rows[0]["CreationDate"], "CommandLine": decoy})
    p = tmp_path / "procs3.json"
    p.write_text(json.dumps(rows), encoding="utf-8")
    code, out = run(capsys, repo, tmp_path, proc=p)
    assert code == 2
    assert "proc:auto_trader | RED | not running" in (tmp_path / "out" / "CANARY_2026-10-02.md").read_text(encoding="utf-8")


# --- B124: every open plan (trade_attempt entered, no later trade_closed) needs execution/journal/<plan_id>.jsonl
def trades_log(repo, rows):
    touch(repo / "MyTradingSys" / "execution" / "auto_trades.jsonl",
          "".join(json.dumps(r) + "\n" for r in rows))


def attempt(pid, **kw):
    return dict({"ts": "2026-10-02T11:00:00Z", "event": "trade_attempt", "outcome": "entered", "plan_id": pid}, **kw)


def closed(pid):
    return {"ts": "2026-10-02T11:30:00Z", "event": "trade_closed", "plan_id": pid}


def journal_row(out):
    md = [x for x in out.splitlines() if x.startswith("CANARY")]
    return md[0]


def journal_md(tmp_path):
    md = (tmp_path / "out" / "CANARY_2026-10-02.md").read_text(encoding="utf-8")
    rows = [x for x in md.splitlines() if x.startswith("| journal ")]
    assert rows, md
    return rows[-1]


def test_journal_missing_for_open_plan_is_red(tmp_path, capsys):
    repo = make_repo(tmp_path)
    trades_log(repo, [attempt("L-mkt-1009-2100")])
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 2 and out.startswith("CANARY RED"), out
    assert "| RED | 1 of 1 open plans have no journal file" in journal_md(tmp_path)


def test_journal_present_is_ok(tmp_path, capsys):
    repo = make_repo(tmp_path)
    trades_log(repo, [attempt("L-mkt-1009-2100")])
    touch(repo / "MyTradingSys" / "execution" / "journal" / "L-mkt-1009-2100.jsonl", "{}\n")
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 0, out
    assert "| OK | 1 open, all journaled" in journal_md(tmp_path)


def test_closed_plan_without_journal_is_ok(tmp_path, capsys):
    repo = make_repo(tmp_path)
    trades_log(repo, [attempt("L-mkt-1009-2100"), closed("L-mkt-1009-2100")])
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 0, out
    assert "| OK | 0 open, all journaled" in journal_md(tmp_path)


def test_no_open_plans_ok(tmp_path, capsys):
    repo = make_repo(tmp_path)
    code, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert code == 0, out
    assert "| OK | 0 open, all journaled" in journal_md(tmp_path)


def test_trades_log_missing_is_warn(tmp_path, capsys):
    repo = make_repo(tmp_path)
    (repo / "MyTradingSys" / "execution" / "auto_trades.jsonl").unlink()
    _, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    assert "| WARN |" in journal_md(tmp_path)


def test_journal_output_has_no_plan_id(tmp_path, capsys):
    repo = make_repo(tmp_path)
    trades_log(repo, [attempt("L-mkt-1009-2100"), attempt("S-mkt-1009-1901")])
    touch(repo / "MyTradingSys" / "execution" / "journal" / "S-mkt-1009-1901.jsonl", "{}\n")
    _, out = run(capsys, repo, tmp_path, proc=procs(tmp_path))
    md = (tmp_path / "out" / "CANARY_2026-10-02.md").read_text(encoding="utf-8")
    assert "1 of 2 open plans have no journal file" in md
    for s in ("L-mkt-1009-2100", "S-mkt-1009-1901"):
        assert s not in out and s not in md
