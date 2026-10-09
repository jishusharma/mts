#!/usr/bin/env python
"""auto_deploy.py - scheduled pull-and-deploy of green/fast-track into the LIVE tree, stopping on a red gate (Step 4, 2026-10-10).

Runs where the file `.mts_live` exists (JIS-NB). Anywhere else it reports NOT_LIVE and changes nothing. Recipe (MyTradingSys/system/DEPLOY_RUNBOOK.md):
  1. git fetch origin green/fast-track (the SHA CI gated on ubuntu AND windows); fetch failure = stop, nothing changed.
  2. same SHA = UP_TO_DATE. Not a fast-forward of HEAD = STOP_NOT_FF (never reset, rebase or force). A tracked file that other sessions
     edited and the deploy would change = STOP_DIRTY (never merge or stash over another session's edits).
  3. Gate the candidate in a throwaway detached worktree (run_all_tests.py --quick). Red = STOP_RED: the live tree is never touched, and the same
     SHA is not re-gated every cycle (the state file remembers it).
  4. Copy orderflow _state.json away (B152), `git merge --ff-only`, restore _state.json if the merge dropped it.
  5. Restart only the processes whose files changed (loop-supervisor revives them in about a minute). position_manager is never killed (it
     guards an open position; new managers pick the code up). Java (src/main/java, pom.xml) is reported in java_pending for a compile + JVM window.
Result of the last run: MyTradingSys/runtime/sched/auto_deploy_last.json (gitignored) and a line in auto_deploy.log beside it.
Usage: python scripts/dev/auto_deploy.py [--check]   (--check: decide and report, change nothing)
Exit 0 = deployed / up to date / not live; 1 = stopped (red gate, not ff, dirty, fetch failed): look at the json.
"""
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCHED = REPO / "MyTradingSys" / "runtime" / "sched"
STATE = SCHED / "auto_deploy_state.json"
LAST = SCHED / "auto_deploy_last.json"
LOG = SCHED / "auto_deploy.log"
BRANCH = "green/fast-track"
ORDERFLOW_STATE = "MyTradingSys/runtime/orderflow_live/_state.json"
JAVA_RE = re.compile(r"^(src/main/java/|src/test/java/|pom\.xml$)")
NEVER_KILL = ("position_manager",)
# (regex on a changed path, script name to restart). A process is listed once. position_manager is deliberately absent.
RESTART_MAP = [
    (re.compile(r"^MyTradingSys/execution/(auto_trader|auto_trader_config|executor|plan_compiler|mainnet_plan_check|risk_guard|journal|deribit_orders)\b"), "auto_trader.py"),
    (re.compile(r"^MyTradingSys/execution/(daily_loss_monitor|mainnet_pnl|kill_switch|deribit_orders)\b"), "daily_loss_monitor.py"),
    (re.compile(r"^MyTradingSys/backtest/layers/(alerts|rsi|fabio|session|positioning|cryptocred|turn_of_candle|tick|timeframe|consensus)/"), "live_runner_cli.py"),
    (re.compile(r"^MyTradingSys/backtest/(bt/|fees)"), "live_runner_cli.py"),
]


def decide(*, is_live, head, target, is_ff, changed, dirty, last_red_sha=None):
    """Pure decision -> dict(action, reason, restarts, java_pending).
    action: NOT_LIVE | UP_TO_DATE | STOP_NOT_FF | STOP_DIRTY | RED_KNOWN | DEPLOY (the gate still has to run)."""
    out = dict(action="", reason="", restarts=[], java_pending=[])
    if not is_live:
        out.update(action="NOT_LIVE", reason="no .mts_live marker here: not the live tree, nothing changed")
        return out
    if head == target:
        out.update(action="UP_TO_DATE", reason=f"HEAD already at {BRANCH} {target[:7]}")
        return out
    if not is_ff:
        out.update(action="STOP_NOT_FF", reason=f"HEAD {head[:7]} is not an ancestor of {BRANCH} {target[:7]}; never reset or rebase: a human decides")
        return out
    clash = sorted(set(changed) & set(dirty))
    if clash:
        out.update(action="STOP_DIRTY", reason="uncommitted edits by another session on files the deploy changes: " + ", ".join(clash[:8]))
        return out
    if last_red_sha == target:
        out.update(action="RED_KNOWN", reason=f"{target[:7]} already failed the gate here; waiting for a newer green SHA")
        return out
    restarts = []
    for path in changed:
        for rx, proc in RESTART_MAP:
            if rx.search(path) and proc not in restarts and not any(n in proc for n in NEVER_KILL):
                restarts.append(proc)
    out.update(action="DEPLOY", reason=f"{head[:7]} -> {target[:7]}, {len(changed)} file(s)", restarts=restarts,
               java_pending=[p for p in changed if JAVA_RE.search(p)])
    return out


def sh(argv, cwd=REPO, timeout=300):
    try:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timed out"
    except OSError as e:
        return 127, f"could not start: {e}"


def kill_process(script_name):
    """Stop the processes whose command line names `script_name` (Windows). -> how many were stopped."""
    ps = ("$n=0; Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match [regex]::Escape('" + script_name
          + "') -and $_.ProcessId -ne $PID } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; $n++ }; $n")
    rc, out = sh(["powershell", "-NoProfile", "-Command", ps], timeout=60)
    try:
        return int(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return 0


class Ops:
    """The side effects, injectable for tests."""

    def git(self, *a, timeout=300):
        return sh(["git", *a], timeout=timeout)

    def is_live(self):
        return (REPO / ".mts_live").exists()

    def gate(self, sha):
        wt = REPO.parent / "mts-deploy-gate"
        if wt.exists():
            self.git("worktree", "remove", "--force", str(wt))
            shutil.rmtree(wt, ignore_errors=True)
        rc, out = self.git("worktree", "add", "--detach", str(wt), sha)
        if rc != 0:
            return 125, "could not create gate worktree: " + out[-300:]
        try:
            return sh([sys.executable, "scripts/dev/run_all_tests.py", "--quick"], cwd=wt, timeout=1500)
        finally:
            self.git("worktree", "remove", "--force", str(wt))
            shutil.rmtree(wt, ignore_errors=True)

    def kill(self, script):
        return kill_process(script)

    def now(self):
        return datetime.now(timezone.utc)


def _load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write(path, text):
    SCHED.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8", newline="\n")


def _finish(res, save, state=None):
    if save:
        _write(LAST, json.dumps(res, indent=1) + "\n")
        with open(LOG, "a", encoding="utf-8", newline="\n") as f:
            f.write(f"{res['utc']} {res['action']} {res.get('target') or ''} {res['reason']}\n")
        if state is not None:
            _write(STATE, json.dumps(state, indent=1) + "\n")
    return res


def run(ops=None, check=False, state=None, save=True):
    ops = ops or Ops()
    state = _load_state() if state is None else state
    res = {"utc": ops.now().strftime("%Y-%m-%dT%H:%M:%SZ"), "check_only": check, "action": "", "reason": "", "target": None}
    if not ops.is_live():
        d = decide(is_live=False, head="", target="", is_ff=False, changed=[], dirty=[])
        res.update(action=d["action"], reason=d["reason"])
        return _finish(res, save)
    rc, out = ops.git("fetch", "origin", BRANCH)
    if rc != 0:
        res.update(action="STOP_FETCH", reason="git fetch failed: " + out.strip()[-200:])
        return _finish(res, save)
    target = ops.git("rev-parse", f"origin/{BRANCH}")[1].strip()
    head = ops.git("rev-parse", "HEAD")[1].strip()
    res["target"] = target
    is_ff = ops.git("merge-base", "--is-ancestor", head, target)[0] == 0
    changed = [p for p in ops.git("diff", "--name-only", head, target)[1].splitlines() if p.strip()] if is_ff else []
    dirty = [ln[3:].strip().strip('"') for ln in ops.git("status", "--porcelain", "--untracked-files=no")[1].splitlines() if ln[:2].strip()]
    d = decide(is_live=True, head=head, target=target, is_ff=is_ff, changed=changed, dirty=dirty,
               last_red_sha=state.get("last_red_sha"))
    res.update(action=d["action"], reason=d["reason"], restarts=d["restarts"], java_pending=d["java_pending"])
    if d["action"] != "DEPLOY":
        return _finish(res, save)
    if check:
        res["action"] = "WOULD_DEPLOY"
        return _finish(res, save)
    grc, gout = ops.gate(target)
    res["gate_tail"] = [ln for ln in gout.splitlines() if ln.strip()][-6:]
    if grc != 0:
        state["last_red_sha"] = target
        res.update(action="STOP_RED", reason=f"gate red on {target[:7]}; live tree untouched")
        return _finish(res, save, state)
    backup = None
    sp = REPO / ORDERFLOW_STATE
    if sp.exists():
        backup = REPO / "runtime_data" / "deploy_backup" / ops.now().strftime("%Y%m%dT%H%M%SZ")
        backup.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sp, backup / "_state.json")
    mrc, mout = ops.git("merge", "--ff-only", f"origin/{BRANCH}")
    if mrc != 0:
        res.update(action="STOP_MERGE", reason="ff-only merge refused: " + mout.strip()[-200:])
        return _finish(res, save, state)
    if backup and not sp.exists():
        sp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup / "_state.json", sp)
        res["state_json_restored"] = True
    res["restarted"] = {proc: ops.kill(proc) for proc in d["restarts"]}
    state["last_deployed_sha"] = target
    state.pop("last_red_sha", None)
    res.update(action="DEPLOYED", reason=d["reason"])
    return _finish(res, save, state)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    res = run(check="--check" in argv)
    print(json.dumps(res, indent=1))
    return 1 if res["action"].startswith("STOP") else 0


if __name__ == "__main__":
    sys.exit(main())
