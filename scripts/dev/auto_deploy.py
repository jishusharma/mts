#!/usr/bin/env python
"""auto_deploy.py - scheduled pull-and-deploy of green/fast-track into the LIVE tree, stopping on a red gate (Step 4, 2026-10-10).

Runs where the file `.mts_live` exists (JIS-NB). Anywhere else it reports NOT_LIVE and changes nothing. Recipe (MyTradingSys/system/DEPLOY_RUNBOOK.md):
  1. git fetch origin green/fast-track (the SHA CI gated on ubuntu AND windows); fetch failure = stop, nothing changed.
  2. same SHA = UP_TO_DATE. Not a fast-forward of HEAD = STOP_NOT_FF (never reset, rebase or force). A tracked file that other sessions
     edited and the deploy would change = STOP_DIRTY (never merge or stash over another session's edits).
  3. Gate the candidate in a throwaway detached worktree (run_all_tests.py --quick, limit GATE_TIMEOUT_S = 2700 s, env MTS_DEPLOY_GATE_TIMEOUT). Red =
     STOP_RED: the live tree is never touched, and the same SHA is not re-gated every cycle (the state file remembers it). A timed-out gate keeps its
     partial output in gate_tail; every gated result records gate_secs.
     The gate holds one machine-wide gate slot (sync.gate_slot, GATE_SLOTS=2, shared with the ship gates; waits at most gate_timeout()). No slot in time =
     STOP_SLOT: nothing was tested so nothing is deployed, it is not red, the next tick retries the same SHA.
  3b. Dirty GENERATED files (GENERATED_RE) are backed up to runtime_data/deploy_backup/<stamp>/regenerated/ and restored by `git checkout -- <file>`.
  3c. Fast-track fallback (stale green) only while the newest COMPLETED CI run on fast-track is green; red = FALLBACK_REFUSED_CI_RED, unknown
     (gh missing / auth / parse error / no completed run) = FALLBACK_REFUSED_CI_UNKNOWN (fail closed): both stay on green/fast-track.
  3d. Untracked files in the live tree that the merge would create make `git merge --ff-only` refuse. Only machine-generated CI cards
     (UNTRACKED_CLEARABLE_RE: make_status.py filed MyTradingSys/system/tasks/ci-<sha>.json while CI was red, then a builder shipped the same card)
     whose content equals the incoming blob or has the generated card shape are backed up to runtime_data/deploy_backup/<stamp>/untracked/<path>
     and removed (result key untracked_cleared). Any other untracked clash = STOP_MERGE, nothing removed (fail closed).
  4. Copy orderflow _state.json away (B152), `git merge --ff-only`, restore _state.json if the merge dropped it. Live INPUTS among the
     regenerated files (LIVE_INPUT_RE: htf_context, oi_live) are put back from the backup after the merge (L6); STATUS.md etc. stay committed.
  5. Restart only the processes whose files changed (loop-supervisor revives them in about a minute). position_manager is never killed (it
     guards an open position; new managers pick the code up). Java (src/main/java, pom.xml) is reported in java_pending for a compile + JVM window.
Result of the last run: MyTradingSys/runtime/sched/auto_deploy_last.json (gitignored) and a line in auto_deploy.log beside it.
Usage: python scripts/dev/auto_deploy.py [--check]   (--check: decide and report, change nothing)
Exit 0 = deployed / up to date / not live; 1 = stopped (red gate, not ff, dirty, fetch failed): look at the json.
"""
import nowin  # B173: no console flash from git/python children under pythonw
nowin.install()
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync import GateSlotTimeout

REPO = Path(__file__).resolve().parents[2]
SCHED = REPO / "MyTradingSys" / "runtime" / "sched"
STATE = SCHED / "auto_deploy_state.json"
LAST = SCHED / "auto_deploy_last.json"
LOG = SCHED / "auto_deploy.log"
LOCK = SCHED / "auto_deploy.lock"   # run-lock: one deploy at a time (2026-10-11: manual start stacked on the 15-min run, two merges raced on .git/index.lock)
LOCK_STALE_S = 30 * 60
BRANCH = "green/fast-track"
FALLBACK_BRANCH = "fast-track"   # gated here by the same local gate when CI has not advanced green for GREEN_STALE_S
GREEN_STALE_S = 90 * 60
# The quick gate takes ~290 s on an idle host (DEPLOY_RUNBOOK Quick-gate speed). 2026-10-16 04:45Z it hit the old 1500 s while parallel sessions kept
# the 8 CPUs at 100% (STOP_RED, gate_tail ['timed out']). Env override: MTS_DEPLOY_GATE_TIMEOUT (seconds).
GATE_TIMEOUT_S = 2700
GATE_TIMEOUT_ENV = "MTS_DEPLOY_GATE_TIMEOUT"
ORDERFLOW_STATE = "MyTradingSys/runtime/orderflow_live/_state.json"
JAVA_RE = re.compile(r"^(src/main/java/|src/test/java/|pom\.xml$)")
NEVER_KILL = ("position_manager",)
# GENERATED files that scheduled jobs on the live host rewrite while they are tracked in git (each generator checked in the repo, 2026-10-15):
# STATUS.md make_status.py; AUDIT_DIGEST.md scripts/worker/audit_digest.py; T0_CHECKS.md scripts/worker/audit_t0_checks.py;
# runtime/BUILD_REPORT.md scripts/Build-Check.ps1; runtime/oi_live/*.csv oi_recorder.py; research/htf_context/* fabio/htf_context_live.py.
# Dirty + in the deploy diff = back up, `git checkout -- <file>`, merge. Anything else dirty stays STOP_DIRTY (fail closed).
GENERATED_RE = re.compile(
    r"^MyTradingSys/(research/STATUS\.md|research/audits/(AUDIT_DIGEST|T0_CHECKS)\.md|runtime/BUILD_REPORT\.md"
    r"|runtime/oi_live/[^/]+\.csv|research/htf_context/[^/]+\.(jsonl|json))$")
# Subset of GENERATED_RE that the live runner / health check READS: the checked-out committed copy would be a stale input, so the live-written
# copy is restored after the merge. STATUS.md, AUDIT_DIGEST, T0_CHECKS, BUILD_REPORT are outputs only and take the committed version.
LIVE_INPUT_RE = re.compile(r"^MyTradingSys/(runtime/oi_live/[^/]+\.csv|research/htf_context/[^/]+\.(jsonl|json))$")
# UNTRACKED files the incoming diff would create: only the machine-generated CI card may be cleared (2026-10-16: make_status.py on the live host
# filed ci-1bb1b39.json untracked, a builder shipped the same card, the gated merge stopped). Everything else untracked stays STOP_MERGE.
UNTRACKED_CLEARABLE_RE = re.compile(r"^MyTradingSys/system/tasks/ci-([0-9a-f]+)\.json$")
_BLOB_RE = re.compile(r"^[0-9a-f]{40,64}$", re.M)
# (regex on a changed path, script name to restart). A process is listed once. position_manager is deliberately absent.
# The alert runner is launched as `python -m MyTradingSys.backtest.layers.alerts.live_runner_cli` (loop-supervisor / mts.ps1): its command line has
# no ".py", so the old name "live_runner_cli.py" matched nothing and a deploy never restarted it (2026-10-16: W3 layers stayed unloaded for hours).
RUNNER_PROC = "layers.alerts.live_runner_cli"
RESTART_MAP = [
    (re.compile(r"^MyTradingSys/execution/(auto_trader|auto_trader_config|executor|plan_compiler|mainnet_plan_check|risk_guard|journal|deribit_orders)\b"), "auto_trader.py"),
    (re.compile(r"^MyTradingSys/execution/(daily_loss_monitor|mainnet_pnl|kill_switch|deribit_orders)\b"), "daily_loss_monitor.py"),
    # recorder: launched as `python -m MyTradingSys.backtest.layers.fabio.orderflow_live` (command line has no .py); loop-supervisor relaunches it.
    (re.compile(r"^MyTradingSys/backtest/layers/fabio/(orderflow_live|orderflow_bars)\.py$"), "orderflow_live"),
    (re.compile(r"^MyTradingSys/backtest/layers/(alerts|rsi|fabio|session|positioning|cryptocred|turn_of_candle|tick|timeframe|consensus)/"), RUNNER_PROC),
    (re.compile(r"^MyTradingSys/backtest/(bt/|fees)"), RUNNER_PROC),
]


def decide(*, is_live, head, target, is_ff, changed, dirty, last_red_sha=None, ws_only=()):
    """Pure decision -> dict(action, reason, restarts, java_pending).
    action: NOT_LIVE | UP_TO_DATE | STOP_NOT_FF | STOP_DIRTY | RED_KNOWN | DEPLOY (the gate still has to run)."""
    out = dict(action="", reason="", restarts=[], java_pending=[], regenerate=[])
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
    # ws_only: dirty files the caller verified differ from HEAD by trailing whitespace / EOL only (Q75): handled like generated files
    # (backed up, `git checkout -- <file>`). Anything the caller did not verify stays a clash (fail closed).
    regen = [p for p in clash if GENERATED_RE.match(p) or p in set(ws_only)]
    clash = [p for p in clash if p not in regen]
    if clash:
        out.update(action="STOP_DIRTY", reason="uncommitted edits by another session on files the deploy changes: " + ", ".join(clash[:8]))
        return out
    out["regenerate"] = regen
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


def gate_timeout():
    """Seconds the gate may run: MTS_DEPLOY_GATE_TIMEOUT (a positive finite number) or GATE_TIMEOUT_S."""
    try:
        v = float(os.environ.get(GATE_TIMEOUT_ENV, ""))
    except ValueError:
        return GATE_TIMEOUT_S
    if not (math.isfinite(v) and v > 0):
        return GATE_TIMEOUT_S
    return int(v) if v == int(v) else v


def _text(x):
    """subprocess hands back None, str or (after a timeout, even in text mode) bytes."""
    if x is None:
        return ""
    return x.decode("utf-8", "replace") if isinstance(x, bytes) else x


def kill_tree(proc):
    """Kill `proc` and every process it started (Q75: subprocess.run(timeout) kills only the direct child, so the gate's pytest/maven/java
    grandchildren kept the 8 CPUs busy and held the output pipe open). Windows: taskkill /T /F; elsewhere: the child's own process group."""
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True, timeout=30)
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        proc.kill()   # the direct child too, if taskkill / killpg did not get it
    except OSError:
        pass


def sh(argv, cwd=REPO, timeout=300):
    kw = {"start_new_session": True} if os.name != "nt" else {}
    try:
        proc = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kw)
    except OSError as e:
        return 127, f"could not start: {e}"
    try:
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, (out or "") + (err or "")
    except subprocess.TimeoutExpired as e:
        kill_tree(proc)
        # keep what the child printed before the kill: a timed-out gate's tail then shows the step it reached (2026-10-16 04:45Z: only 'timed out')
        partial = _text(e.stdout) + _text(e.stderr)
        try:
            out, err = proc.communicate(timeout=30)   # the tree is dead: the pipes close
            partial = (out or "") + (err or "") if (out or err) else partial
        except (subprocess.TimeoutExpired, OSError, ValueError):
            pass
        return 124, partial if partial.strip() else "timed out"


def kill_process(script_name):
    """Stop the processes whose command line names `script_name` (Windows). -> how many were stopped."""
    ps = ("$n=0; Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match [regex]::Escape('" + script_name
          + "') -and $_.ProcessId -ne $PID } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; $n++ }; $n")
    rc, out = sh(["powershell", "-NoProfile", "-Command", ps], timeout=60)
    try:
        return int(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return 0


def is_generated_ci_card(rel, text):
    """True when `text` has the shape ci_red_card.card_for writes for the card file `rel` (MyTradingSys/system/tasks/ci-<sha>.json): id and title
    name the file's sha, pinned, goal and sources in the generated wording. Shape only: a hand-written card or any other JSON is False."""
    m = UNTRACKED_CLEARABLE_RE.match(rel)
    if not m:
        return False
    sha = m.group(1)
    try:
        c = json.loads(text)
    except ValueError:
        return False
    if not isinstance(c, dict):
        return False
    src = c.get("sources")
    return (c.get("id") == f"ci-{sha}" and c.get("title") == f"fix CI {sha}: fast-track is red" and c.get("pinned") is True
            and str(c.get("goal", "")).startswith(f"CI on fast-track is red since commit {sha} (run ")
            and isinstance(src, list) and len(src) == 1 and re.fullmatch(r"CI run \d+", str(src[0])) is not None)


def _blob_id(out):
    ids = _BLOB_RE.findall(out or "")
    return ids[-1] if ids else ""


def plan_untracked(ops, target, changed):
    """Untracked files of the live tree that the incoming diff creates (the ff-only merge refuses to overwrite them). Read-only.
    -> (clear, blocking). clear: generated CI cards (UNTRACKED_CLEARABLE_RE) whose content equals the incoming blob or has the generated card
    shape: safe to back up and remove. blocking: every other clash, or `git ls-files` failing (fail closed)."""
    rc, out = ops.git("ls-files", "--others", "--exclude-standard")
    if rc != 0:
        return [], ["(git ls-files --others failed: " + out.strip()[-120:] + ")"]
    untracked = {ln.strip().strip('"') for ln in out.splitlines() if ln.strip()}
    clear, blocking = [], []
    for rel in sorted(set(changed) & untracked):
        if not UNTRACKED_CLEARABLE_RE.match(rel):
            blocking.append(rel)
            continue
        irc, iout = ops.git("rev-parse", f"{target}:{rel}")
        incoming = _blob_id(iout) if irc == 0 else ""
        same = bool(incoming) and incoming == _blob_id(ops.git("hash-object", "--", rel)[1])
        if not same:
            try:
                same = is_generated_ci_card(rel, (REPO / rel).read_text(encoding="utf-8"))
            except (OSError, ValueError):
                same = False
        (clear if same else blocking).append(rel)
    return clear, blocking


class Ops:
    """The side effects, injectable for tests."""

    def git(self, *a, timeout=300):
        return sh(["git", *a], timeout=timeout)

    def is_live(self):
        return (REPO / ".mts_live").exists()

    def whitespace_only(self, rel):
        """True only when git confirms `rel` differs from HEAD by trailing whitespace / EOL alone (exit 0 of --quiet). Any error = False."""
        return self.git("diff", "--ignore-space-at-eol", "--quiet", "HEAD", "--", rel)[0] == 0

    def gate(self, sha):
        """Run the quick gate on `sha` while holding one machine-wide gate slot (sync.gate_slot: the same slots the ship gates use, dead-PID
        slots reclaimed, released in the with-exit whatever raised). No slot within gate_timeout() raises sync.GateSlotTimeout: the caller
        must not deploy (fail closed)."""
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import sync
        with sync.gate_slot(REPO, timeout=gate_timeout()):
            return self._gate_in_worktree(sha)

    def _gate_in_worktree(self, sha):
        wt = REPO.parent / "mts-deploy-gate"
        if wt.exists():
            self.git("worktree", "remove", "--force", str(wt))
            shutil.rmtree(wt, ignore_errors=True)
        rc, out = self.git("worktree", "add", "--detach", str(wt), sha)
        if rc != 0:
            return 125, "could not create gate worktree: " + out[-300:]
        try:
            return sh([sys.executable, "scripts/dev/run_all_tests.py", "--quick"], cwd=wt, timeout=gate_timeout())
        finally:
            self.git("worktree", "remove", "--force", str(wt))
            shutil.rmtree(wt, ignore_errors=True)

    def clock(self):
        return time.monotonic()

    def kill(self, script):
        return kill_process(script)

    def ci_runs(self):
        """Newest-first CI runs on fast-track, or None when unknown (gh missing / error). Uses ci_red_card.fetch_runs."""
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import ci_red_card
        return ci_red_card.fetch_runs(REPO)

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


GATE_FAILED_CHARS = 4000


def failed_step_blocks(gout, limit=GATE_FAILED_CHARS):
    """The failing steps of a run_all_tests.py transcript: each 'Step N: FAIL' line with the 'Last output:' lines under it (the failed
    pytest test names, the assertion), up to the next step block. 2026-10-16: the record kept only the last 6 summary lines, so a red
    Step 4b could not be traced to a test afterwards. Capped at `limit` characters, the end kept; never raises (a parse slip must not stop
    the red-gate record)."""
    try:
        blocks, cur = [], None
        for ln in gout.splitlines():
            if re.match(r"Step \S+: FAIL\b", ln):   # not the summary's 'Step 4b: Pytest tests: FAIL'
                cur = [ln]
                blocks.append(cur)
            elif cur is not None and (ln.startswith("[Step ") or ln.startswith("=" * 10)):
                cur = None
            elif cur is not None and ln.strip():
                cur.append(ln)
        text = "\n".join("\n".join(b) for b in blocks)
        return text[-limit:]
    except Exception:   # noqa: BLE001
        return ""


def _finish(res, save, state=None):
    if save:
        _write(LAST, json.dumps(res, indent=1) + "\n")
        with open(LOG, "a", encoding="utf-8", newline="\n") as f:
            f.write(f"{res['utc']} {res['action']} {res.get('target') or ''} {res['reason']}\n")
        if state is not None:
            _write(STATE, json.dumps(state, indent=1) + "\n")
    return res


def ci_state(ops):
    """-> "GREEN" | "RED" | "UNKNOWN" for the newest COMPLETED CI run on fast-track. Any error or missing data is UNKNOWN (fail closed)."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import ci_red_card
        runs = ops.ci_runs()
        if not isinstance(runs, list):
            return "UNKNOWN"
        if ci_red_card.first_failing(runs) is not None:
            return "RED"
        done = [r for r in runs if r.get("status") == "completed" and r.get("conclusion") in ("success", "failure", "timed_out")]
        return "GREEN" if done and done[0]["conclusion"] == "success" else "UNKNOWN"
    except Exception:   # noqa: BLE001 - gh/parse trouble must never open the fallback
        return "UNKNOWN"


def pick_branch(ops, note=None):
    """green/fast-track normally. If CI has not advanced it for GREEN_STALE_S (burst of pushes, CI down) and fast-track is ahead of it,
    use fast-track ONLY while the newest completed CI run on fast-track is green (red -> FALLBACK_REFUSED_CI_RED, unknown ->
    FALLBACK_REFUSED_CI_UNKNOWN, both stay on green; recorded in note["fallback"]). The local gate in a throwaway worktree is the second check."""
    green = ops.git("rev-parse", f"origin/{BRANCH}")[1].strip()
    trunk = ops.git("rev-parse", f"origin/{FALLBACK_BRANCH}")[1].strip()
    if not green or not trunk or green == trunk:
        return BRANCH
    if ops.git("merge-base", "--is-ancestor", green, trunk)[0] != 0:
        return BRANCH
    try:
        age = ops.now().timestamp() - int(ops.git("log", "-1", "--format=%ct", f"origin/{BRANCH}")[1].strip())
    except ValueError:
        return BRANCH
    # The live tree can be AHEAD of green (an earlier fallback deploy of fast-track): green is then an ancestor of HEAD, never
    # fast-forwardable, and every later deploy stopped with STOP_NOT_FF until CI re-marked green (2026-10-16). Same CI check below.
    head = ops.git("rev-parse", "HEAD")[1].strip()
    live_ahead = bool(head) and ops.git("merge-base", "--is-ancestor", green, head)[0] == 0         and ops.git("merge-base", "--is-ancestor", head, trunk)[0] == 0
    if age <= GREEN_STALE_S and not live_ahead:
        return BRANCH
    st = ci_state(ops)
    if st != "GREEN":
        if note is not None:
            note["fallback"] = "FALLBACK_REFUSED_CI_RED" if st == "RED" else "FALLBACK_REFUSED_CI_UNKNOWN"
        return BRANCH
    return FALLBACK_BRANCH


def _clock(ops):
    """Monotonic seconds from the ops (a test injects its own); an ops without a clock uses time.monotonic."""
    return getattr(ops, "clock", time.monotonic)()


def run(ops=None, check=False, state=None, save=True):
    ops = ops or Ops()
    state = _load_state() if state is None else state
    res = {"utc": ops.now().strftime("%Y-%m-%dT%H:%M:%SZ"), "check_only": check, "action": "", "reason": "", "target": None}
    if not ops.is_live():
        d = decide(is_live=False, head="", target="", is_ff=False, changed=[], dirty=[])
        res.update(action=d["action"], reason=d["reason"])
        return _finish(res, save)
    rc, out = ops.git("fetch", "origin", BRANCH, FALLBACK_BRANCH)
    if rc != 0:
        res.update(action="STOP_FETCH", reason="git fetch failed: " + out.strip()[-200:])
        return _finish(res, save)
    note = {}
    branch = pick_branch(ops, note)
    res["branch"] = branch
    if note.get("fallback"):
        res["fallback"] = note["fallback"]
    target = ops.git("rev-parse", f"origin/{branch}")[1].strip()
    head = ops.git("rev-parse", "HEAD")[1].strip()
    res["target"] = target
    is_ff = ops.git("merge-base", "--is-ancestor", head, target)[0] == 0
    changed = [p for p in ops.git("diff", "--name-only", head, target)[1].splitlines() if p.strip()] if is_ff else []
    dirty = [ln[3:].strip().strip('"') for ln in ops.git("status", "--porcelain", "--untracked-files=no")[1].splitlines() if ln[:2].strip()]
    ws = []
    for rel in sorted(set(changed) & set(dirty)):   # Q75: an EOL / trailing-space-only edit is no other session's work
        try:
            if not GENERATED_RE.match(rel) and ops.whitespace_only(rel):
                ws.append(rel)
        except Exception:   # fail closed: unknown = still a clash
            pass
    d = decide(is_live=True, head=head, target=target, is_ff=is_ff, changed=changed, dirty=dirty,
               last_red_sha=state.get("last_red_sha"), ws_only=ws)
    res.update(action=d["action"], reason=d["reason"], restarts=d["restarts"], java_pending=d["java_pending"])
    if d["action"] != "DEPLOY":
        return _finish(res, save)
    uclear, ublock = plan_untracked(ops, target, changed)   # before the gate: a clash that cannot be cleared must not cost a gate run
    if ublock:
        res.update(action="STOP_MERGE", reason="untracked working tree files would be overwritten by merge: " + ", ".join(ublock[:8]))
        return _finish(res, save)
    if check:
        if uclear:
            res["untracked_would_clear"] = uclear
        res["action"] = "WOULD_DEPLOY"
        return _finish(res, save)
    t0 = _clock(ops)
    try:
        grc, gout = ops.gate(target)
    except GateSlotTimeout as e:   # no free gate slot: nothing was tested, so nothing is deployed; not red, so the same SHA is gated on the next tick
        res.update(action="STOP_SLOT", reason=f"{e}; nothing deployed, the next tick retries {target[:7]}", gate_secs=round(_clock(ops) - t0))
        return _finish(res, save)
    res["gate_secs"] = round(_clock(ops) - t0)   # every gated result carries it: a slow gate shows up before it times out
    res["gate_tail"] = [ln for ln in gout.splitlines() if ln.strip()][-6:]
    if grc != 0:
        res["gate_failed"] = failed_step_blocks(gout)
        state["last_red_sha"] = target
        why = f" (timed out after {gate_timeout():g}s)" if grc == 124 else ""
        res.update(action="STOP_RED", reason=f"gate red on {target[:7]}{why}; live tree untouched")
        return _finish(res, save, state)
    uclear, ublock = plan_untracked(ops, target, changed)   # the gate takes minutes: read the live tree again (a card may have been filed since)
    if ublock:
        res.update(action="STOP_MERGE", reason="untracked working tree files would be overwritten by merge: " + ", ".join(ublock[:8]))
        return _finish(res, save, state)
    backup = None
    sp = REPO / ORDERFLOW_STATE
    if sp.exists():
        backup = REPO / "runtime_data" / "deploy_backup" / ops.now().strftime("%Y%m%dT%H%M%SZ")
        backup.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sp, backup / "_state.json")
    has_state = backup is not None
    regen = d.get("regenerate") or []
    for rel in regen:   # generated file edited on the live host: keep a copy, restore only that file, then the merge can proceed
        src = REPO / rel
        if src.exists():
            if backup is None:
                backup = REPO / "runtime_data" / "deploy_backup" / ops.now().strftime("%Y%m%dT%H%M%SZ")
            dst = backup / "regenerated" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        crc, cout = ops.git("checkout", "--", rel)
        if crc != 0:
            res.update(action="STOP_MERGE", reason=f"could not restore generated file {rel}: " + cout.strip()[-200:])
            return _finish(res, save, state)
    if regen:
        res["regenerated"] = regen
    if ws:
        res["whitespace_only_reset"] = [p for p in ws if p in regen]
    for rel in uclear:   # generated CI card filed on the live host and also shipped to the trunk: keep a copy, remove only that file
        src = REPO / rel
        if backup is None:
            backup = REPO / "runtime_data" / "deploy_backup" / ops.now().strftime("%Y%m%dT%H%M%SZ")
        dst = backup / "untracked" / rel
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            src.unlink()
        except OSError as e:
            res.update(action="STOP_MERGE", reason=f"could not back up and clear untracked {rel}: {e}")
            return _finish(res, save, state)
        res.setdefault("untracked_cleared", []).append(rel)
    mrc, mout = ops.git("merge", "--ff-only", f"origin/{branch}")
    if mrc != 0:
        res.update(action="STOP_MERGE", reason="ff-only merge refused: " + mout.strip()[-200:])
        return _finish(res, save, state)
    if has_state and not sp.exists():
        sp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup / "_state.json", sp)
        res["state_json_restored"] = True
    for rel in regen:   # L6: live inputs (htf_context, oi_live) keep the live-written copy; the checkout above only let the merge pass
        if LIVE_INPUT_RE.match(rel):
            b = backup / "regenerated" / rel if backup is not None else None
            if b is not None and b.exists():
                (REPO / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(b, REPO / rel)
                res.setdefault("live_inputs_restored", []).append(rel)
    res["restarted"] = {proc: ops.kill(proc) for proc in d["restarts"]}
    state["last_deployed_sha"] = target
    state.pop("last_red_sha", None)
    res.update(action="DEPLOYED", reason=d["reason"])
    return _finish(res, save, state)


def _pid_alive(pid):
    if pid <= 0:
        return False
    if os.name == "nt":
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def acquire_lock(path=None, pid_alive=_pid_alive, now=time.time):
    """Atomic O_EXCL create. Returns (True, '') or (False, reason). A lock whose owner pid is dead, or older than LOCK_STALE_S, is taken over."""
    path = Path(path or LOCK)
    path.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        try:
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                pid, ts = (int(x) for x in path.read_text(encoding="utf-8").split()[:2])
            except (OSError, ValueError):
                pid, ts = 0, 0
            if pid_alive(pid) and now() - ts < LOCK_STALE_S:
                return False, f"another auto_deploy is running (pid {pid}, started {int(now() - ts)}s ago); exiting without touching git"
            try:
                path.unlink()
            except OSError:
                pass
            continue
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"{os.getpid()} {int(now())}\n")
        return True, ""
    return False, "could not take auto_deploy lock"


def release_lock(path=None):
    try:
        Path(path or LOCK).unlink()
    except OSError:
        pass


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    check = "--check" in argv
    if not check:
        ok, why = acquire_lock()
        if not ok:
            res = {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "check_only": False, "action": "SKIP_LOCKED", "reason": why, "target": None}
            print(json.dumps(res, indent=1))
            return 0   # not a failure: the running deploy owns the result files, so nothing is written here
    try:
        res = run(check=check)
    finally:
        if not check:
            release_lock()
    print(json.dumps(res, indent=1))
    return 1 if res["action"].startswith("STOP") else 0


if __name__ == "__main__":
    sys.exit(main())
