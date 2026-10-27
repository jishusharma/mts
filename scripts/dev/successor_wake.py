"""successor_wake.py - the 4b2 one-time successor task (SCHEDULING_POLICY.md 4b2): a dead/ENDED Supervisor
boots its own successor so a rolling loop needs no operator click.

One ONE-TIME task `MTS-SuccWake-<login>` (fireAt, never cron / repeat): on fire it runs one headless
`claude -p` Supervisor session in the MTS checkout, logs to F:/MTS/succ_wake/<login>/out.log, and
self-unregisters in the same command line (that self-unregister IS the 4b2 "must be unregistered after
it fires" rule; the task's action registers nothing else - the booted session may register the next
link at its own ENDED). Pattern = nuc_wake.py minus the SSH gate; principal is the logged-in user
(Interactive, no password).

  python scripts/dev/successor_wake.py --login C                  # fireAt = now
  python scripts/dev/successor_wake.py --login C --at 2026-10-27T20:05Z  # fail closed: future only
  python scripts/dev/successor_wake.py --login C --dry            # print the PowerShell, run nothing

Budget-aware fireAt (operator d-47): supervisor.py handover computes it from the pacer's last plan
(slots >= 1 -> now, so the chain keeps draining the pacer's room; STOP -> the next reset that reopens
the binding constraint) and passes it here. The successor boots inside a window the pacer has room in,
so each reset opens and the station's loop keeps draining.
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MODEL = "claude-sonnet-5-5"          # cost rule (d-47 / SUPER_SESSION model rule)
SPOKEN_MODEL_FLAG = "--model"                # the 4b2 rule: the task prompt names the model
SPAWN_CEIL = 80                              # supervisor.SPAWN_CEIL: 5h % at which no worker starts


def task_name(login: str) -> str:
    return f"MTS-SuccWake-{(login or '').strip().upper()[:1]}"


def parse_utc(text: str) -> datetime:
    """'2026-10-27T20:05Z' (or a time with no zone) -> aware UTC datetime."""
    t = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def iso_utc(t: datetime) -> str:
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_prompt(login: str) -> str:
    """The handover successor line + the no-questions default (d-47: manual intervention stays possible)."""
    lg = (login or "").strip().upper()[:1]
    return (f"You are Supervisor. Login {lg}. Continue from MyTradingSys/system/handover/SUPERVISOR_{lg}.md. "
            f"Boot per CLAUDE.md (read STATUS.md, ANNOUNCEMENTS.md), take the next card, never ask the operator: "
            f"take the defaults and log DECISION (OURS) in the commit body.")


def successor_fireat(last_plan: dict, now: datetime) -> tuple[str, str]:
    """Pure: the successor fireAt from the pacer's last plan (d-47). `last_plan` is the `plan()` data dict
    (its `plan` key is the pace_plan output). slots >= 1 -> now (the pacer has room; chain keeps draining);
    STOP -> the next reset that reopens the binding constraint (5h block -> five_reset, weekly at cap ->
    week_reset). Returns (fireAt iso-utc, why)."""
    plan = (last_plan or {}).get("plan", {}) or {}
    mode = str(plan.get("mode", "?"))
    slots = int(plan.get("slots") or 0)
    if slots >= 1:
        return iso_utc(now), f"slots {slots} >= 1: the pacer has room, chain now"
    five_reset = str(plan.get("five_reset") or "").strip() + "Z" if str(plan.get("five_reset")) else iso_utc(now)
    week_reset = str(plan.get("week_reset") or "").strip() + "Z" if str(plan.get("week_reset")) else iso_utc(now)
    if mode == "STOP":
        if float(plan.get("five") or 0) >= SPAWN_CEIL:
            return five_reset, "STOP, 5h >= 80: wait for the 5h reset"
        return week_reset, "STOP, weekly at cap: wait for the weekly reset"
    return iso_utc(now), f"mode {mode}: default chain now"


def _psq(s: str) -> str:
    """PowerShell single-quoted literal of s (single quotes doubled; backslashes are literal, so Windows paths are safe)."""
    return "'" + s.replace("'", "''") + "'"


def _runner_ps(task: str, login: str, model: str, cwd: str) -> str:
    """The fired action: cd into the checkout, run one headless Supervisor session, then self-unregister (the 4b2 rule:
    the task must be gone after it fires). Written to F:/MTS/succ_wake/<login>/runner.ps1 and run with `powershell -File`,
    so there is no nested -Command quoting to break (same trick as scripts/sched/register_aibridge.ps1)."""
    d = f"F:/MTS/succ_wake/{(login or '').strip().upper()[:1]}"
    lines = [
        "$ErrorActionPreference = 'Continue'",
        f"$cid = {_psq(cwd)}",
        "$c = (Get-Command claude.exe).Source",
        f"Set-Location $cid",
        f"Get-Content -Raw {_psq(d + '/prompt.txt')} | & $c -p --model {model} --permission-mode bypassPermissions *>> {_psq(d + '/out.log')}",
        f"Unregister-ScheduledTask -TaskName {_psq(task)} -Confirm:$false",
        "Write-Output ('done ' + (Get-Date -Format o))",
    ]
    return "\n".join(lines) + "\n"


def build_ps(task: str, login: str, fire_at_iso: str, model: str, prompt: str, cwd: str) -> str:
    """The PowerShell that registers the one-time task. `Register-ScheduledTask -Force` keeps it idempotent.
    Trigger is `-Once -At <fireAt>`: one fireAt, no repeat interval, no cron. The fired action is
    conhost --headless -> `powershell -File runner.ps1` (which runs one `claude -p` session, then
    `Unregister-ScheduledTask` to self-delete). Logs land in F:/MTS/succ_wake/<login>/ so a human can
    verify without opening the app."""
    d = f"F:/MTS/succ_wake/{(login or '').strip().upper()[:1]}"
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"$task = {_psq(task)}",
        f"$dir = {_psq(d)}",
        "$conhost = Join-Path $env:SystemRoot 'System32\\conhost.exe'",
        "New-Item -ItemType Directory -Force $dir | Out-Null",
        "$p = @'",
        prompt.strip(),
        "'@",
        '[IO.File]::WriteAllText("$dir\\prompt.txt", $p)',
        "$runner = @'",
        _runner_ps(task, login, model, cwd).rstrip("\n"),
        "'@",
        '[IO.File]::WriteAllText("$dir\\runner.ps1", $runner)',
        "$runnerPath = $dir + '\\runner.ps1'",
        '$arg = "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File " + $runnerPath',
        "$act = New-ScheduledTaskAction -Execute $conhost -Argument $arg",
        # Parse the UTC iso directly: [DateTime] gives kind=Local and the -Once trigger fires at the right wall clock.
        # (.UtcDateTime.ToLocalTime() is wrong: it applies the tz offset twice, so the task would fire off by the zone offset.)
        f"$fireAt = [DateTime]::Parse({_psq(fire_at_iso)})",
        "$trg = New-ScheduledTaskTrigger -Once -At $fireAt",
        "$pr = New-ScheduledTaskPrincipal -LogonType Interactive -RunLevel Limited",
        "$set = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero)",
        "Register-ScheduledTask -TaskName $task -Action $act -Trigger $trg -Settings $set -Principal $pr -Force | Out-Null",
        f'Write-Output "registered $task fireAt {fire_at_iso}"',
    ]
    return "\n".join(lines) + "\n"


def register(login: str, fire_at_iso: str, model: str = DEFAULT_MODEL, prompt: str | None = None,
             cwd: str | None = None, dry: bool = False, now: datetime | None = None) -> int:
    """Register the one-time successor task (idempotent -Force). `dry` prints the PowerShell and runs nothing.
    `cwd` defaults to the running checkout; the task boots the successor there."""
    cwd = str(Path(cwd).resolve() if cwd else Path.cwd())
    prompt = (prompt if prompt is not None else default_prompt(login)).strip()
    task = task_name(login)
    ps = build_ps(task, login, fire_at_iso, model, prompt, cwd)
    if dry:
        print(ps)
        return 0
    if os.name != "nt":
        print(f"REFUSED: Windows only; would register {task} fireAt {fire_at_iso}", file=sys.stderr)
        return 2
    fd, tmp = tempfile.mkstemp(suffix=".ps1", prefix="mts_succ_wake_")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(ps)
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", tmp],
                           capture_output=True, text=True)
    finally:
        os.unlink(tmp)
    out = (r.stdout + r.stderr).strip()
    print(out or f"exit {r.returncode}")
    return r.returncode


def handover_line(task: str, fire_at_iso: str) -> str:
    """The one line the creating session records in its handover (the 4b2 rule: 'records the task id in its
    hand-over'). Idempotent via upsert_line."""
    return f"- Successor task: {task} fireAt {fire_at_iso} (SCHEDULING_POLICY 4b2, one-time, self-unregistering)"


def upsert_line(path: Path, line: str) -> None:
    """Replace any existing `Successor task:` line with `line` (a second run updates, never duplicates)."""
    path = Path(path)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    kept = [x for x in text.splitlines() if "Successor task:" not in x]
    kept.append(line)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(kept) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--login", required=True, choices=["A", "B", "C"])
    ap.add_argument("--dry", action="store_true", help="print the PowerShell, register nothing")
    ap.add_argument("--at", default="", help="future-only UTC fireAt (e.g. 2026-10-27T20:05Z); default = now")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--prompt-file", default="", help="override the successor boot prompt (UTF-8 text file)")
    ap.add_argument("--cwd", default="", help="the MTS checkout the successor boots in (default: this checkout)")
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    if a.at:
        at = parse_utc(a.at)
        if at <= now:
            print(f"REFUSED: --at {a.at} is not in the future (now {iso_utc(now)}); a one-time 4b2 task "
                  f"fires once, in the future", file=sys.stderr)
            return 2
        fire_iso = iso_utc(at)
    else:
        fire_iso = iso_utc(now)
    prompt = open(a.prompt_file, encoding="utf-8").read().strip() if a.prompt_file else None
    return register(a.login, fire_iso, model=a.model, prompt=prompt, cwd=a.cwd or None, dry=a.dry)


if __name__ == "__main__":
    sys.exit(main())
