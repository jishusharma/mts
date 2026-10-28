"""successor_wake.py - register ONE one-time, self-unregistering task that boots the next Supervisor (SCHEDULING_POLICY.md 4b2).

Why: an ENDED supervisor has no live turn left; a signal reaches nothing. The only allowed boot is one fireAt task, and the
creating session must record its id in the hand-over. Design: MyTradingSys/research/lead/2026-10-27_successor-wake-design.md.
What: task MTS-SuccWake-<login> (Interactive principal, current user, no password), one trigger (-Once) or none (fire now),
action = conhost --headless -> run.ps1 -> `claude -p --model <m>` in the MTS checkout, then Unregister-ScheduledTask itself.
No cron, no repeat. Log: F:/MTS/succ_wake/<login>/out.log (override: env MTS_SUCC_WAKE_DIR).
fireAt is budget-aware (operator d-47): pacer slots >= 1 -> now; STOP band -> the next 5 h (or weekly, if the week is at cap) reset.
Usage: python scripts/dev/successor_wake.py --login C [--at 2026-10-27T20:05Z] [--model M] [--prompt-file F] [--cwd DIR] [--dry]
Tests use --dry / build_script only; nothing here touches HALT, secrets or orders.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

DEFAULT_MODEL = "claude-sonnet-5-5"     # cost rule: Sonnet
GRACE_MIN = 2                           # fire this long after a reset so the new window is open (OURS)
HANDOVER_REL = "MyTradingSys/system/handover/SUPERVISOR_{}.md"
MARK = "Successor task:"
BASE_DIR = "F:/MTS/succ_wake"

USAGE_REL = "USAGE"

PROMPT = ("You are Supervisor. Login {login}. Continue from MyTradingSys/system/handover/SUPERVISOR_{login}.md. "
          "Budget handoff: {usage_line} Never ask the operator; take the defaults and log them.")


def usage_dir(login: str, base: str | None = None) -> str:
    """The directory the usage file lives in: the task's prompt dir (base or MTS_SUCC_WAKE_DIR), so it sits next to out.log."""
    return f"{base or os.environ.get('MTS_SUCC_WAKE_DIR') or BASE_DIR}/{login}"


def usage_rel(login: str, base: str | None = None) -> str:
    """The usage file a register() writes: the pacer's last reading (five/week %, resets, mode, slots) plus the task it lives in,
    so a woken session on any Windows account can read its own budget without MCP get_usage (the gateway profile has none)."""
    return f"{usage_dir(login, base)}/{USAGE_REL}"


def wake_usage(login: str, plan: dict | None, fire_at: datetime, base: str | None = None) -> dict:
    """Pure: the usage-JSON written next to the task's prompt. Reads the pacer's last plan; a missing / unreadable plan is
    not an error, it is a note the woken session must re-read from get_usage. Returns the dict the JSON holds; the key
    `file` is the path a woken session reads it from (the task dir), so the prompt can name it without re-deriving base."""
    five = week = None
    five_reset = week_reset = None
    mode = "unknown"
    slots = 0
    if plan:
        try:
            five = float(plan.get("five"))
        except (TypeError, ValueError):
            five = None
        try:
            week = float(plan.get("week"))
        except (TypeError, ValueError):
            week = None
        five_reset = plan.get("five_reset")
        week_reset = plan.get("week_reset")
        mode = str(plan.get("mode"))
        try:
            slots = int(plan.get("slots"))
        except (TypeError, ValueError):
            slots = 0
    have_plan = bool(plan) and mode != "unknown"
    return {
        "file": usage_rel(login, base),
        "login": login,
        "at_fire": fire_at.isoformat(),
        "five_pct": five,
        "week_pct": week,
        "five_reset_utc": five_reset,
        "week_reset_utc": week_reset,
        "pacer_mode": mode,
        "slots": slots,
        "plan": plan or None,
        "note": "" if have_plan else "pacer plan missing or unreadable: re-read from get_usage before making budget decisions.",
    }


def usage_line(usage: dict) -> str:
    """The short handoff sentence PROMPT appends. A named file plus the one-line task that consumes the reading."""
    p = usage.get("file") or usage_rel(usage["login"])
    if usage.get("five_pct") is None or usage.get("pacer_mode") == "unknown":
        return f"usage file {p} (task MTS-SuccWake-{usage['login']}); pacer plan missing: re-read from get_usage before acting."
    return (f"usage file {p} (task MTS-SuccWake-{usage['login']}, pacer {usage['pacer_mode']} {usage['slots']} slot(s), "
            f"5h {usage['five_pct']}% week {usage['week_pct']}%): adopt it, then run `python scripts/dev/supervisor.py plan` "
            "with a fresh get_usage reading (on a gateway profile that has no get_usage, record by hand and say so).")


class WakeError(Exception):
    pass


def task_name(login: str) -> str:
    return f"MTS-SuccWake-{login}"


def _parse(s) -> datetime | None:
    try:
        d = datetime.fromisoformat(str(s).strip().replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def plan_fire_at(plan: dict | None, now: datetime) -> tuple[datetime, str]:
    """Pure: budget-aware fireAt from the pacer's last plan (supervisor.pace_plan). Returns (when, why).
    slots >= 1 -> now (incl. T-48h weekly drain window when 5h slots are open).
    slots < 1 (gate-blocked, ANY mode: STOP, SUPERVISOR-ONLY, CRUCIAL-ONLY) -> the weekly reset when the week is at cap,
    else the next 5 h reset (+GRACE). Waking now would hit the same gate and end with nothing re-registered.
    No plan / unreadable -> now (OURS: a missing reading must not stall the chain)."""
    if not plan:
        return now, "no pacer reading: now"
    try:
        slots = int(plan.get("slots", 1))
    except (TypeError, ValueError):
        slots = 1
    if slots >= 1:
        wk_raw = plan.get("week_reset")
        wk_dt = _parse(wk_raw)
        if wk_dt is not None:
            while wk_dt <= now:
                wk_dt += timedelta(days=7)
            if 0 < (wk_dt - now).total_seconds() / 3600.0 <= 48.0:
                try:
                    wk_used = float(plan.get("week", plan.get("week_pct", 0)) or 0)
                except (TypeError, ValueError):
                    wk_used = 0.0
                if 100.0 - wk_used > 5.0:
                    return now, f"T-48h weekly drain ({100.0 - wk_used:.0f}% left) slots {slots}: now"
        return now, f"pacer {plan.get('mode', '?')} slots {slots}: now"
    try:
        week_cap = float(plan.get("week", 0)) >= float(plan.get("cap", 101))
    except (TypeError, ValueError):
        week_cap = False
    key = "week_reset" if week_cap else "five_reset"
    r = _parse(plan.get(key))
    if r is None or r + timedelta(minutes=GRACE_MIN) <= now:
        return now, f"pacer {plan.get('mode', '?')} slots {slots} but {key} unreadable/past: now"
    return r + timedelta(minutes=GRACE_MIN), f"pacer {plan.get('mode', '?')} slots {slots}: next {key} {iso(r)}"


def check_checkout(cwd: Path) -> None:
    if not ((cwd / "MyTradingSys").is_dir() and (cwd / "scripts" / "dev" / "sync.py").is_file()):
        raise WakeError(f"{cwd} is not an MTS checkout (MyTradingSys/ or scripts/dev/sync.py missing)")


def build_script(login: str, model: str, prompt: str, cwd: Path, fire_at: datetime | None, base: str | None = None,
                 usage: dict | None = None) -> str:
    """The PowerShell that writes prompt.txt + USAGE + run.ps1 and registers the one-time task. fire_at None = start it now (no trigger).
    A future fire_at = one -Once trigger, never a repeat. The run script unregisters the task in a `finally`."""
    import json
    for v in (login, model, str(cwd)):
        if "'" in v or "\n" in v:
            raise WakeError("quote or newline in login/model/cwd")
    name = task_name(login)
    d = f"{base or os.environ.get('MTS_SUCC_WAKE_DIR') or BASE_DIR}/{login}"
    cwd_s = str(cwd).replace("\\", "/")
    usage_json = json.dumps(usage or {}, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    run = "\n".join([
        '$env:Path += ";C:/Users/E-ngineers/.local/bin"',
        f"Set-Location '{cwd_s}'",
        f"$env:MTS_SUCC_WAKE_TASK = '{name}'",
        "$c = (Get-Command claude.exe).Source",
        "try {",
        f"  Get-Content -Raw '{d}/prompt.txt' | & $c -p --model {model} --permission-mode bypassPermissions > '{d}/out.log' 2> '{d}/err.log'",
        "} finally {",
        f"  Unregister-ScheduledTask -TaskName '{name}' -Confirm:$false -ErrorAction SilentlyContinue",
        "}",
    ])
    L = [
        f"$d = '{d}'; New-Item -ItemType Directory -Force $d | Out-Null",
        "$p = @'", prompt, "'@",
        '[IO.File]::WriteAllText("$d/prompt.txt", $p)',
        "$u = @'", usage_json, "'@",
        f'[IO.File]::WriteAllText("$d/{USAGE_REL}", $u)',
        "$r = @'", run, "'@",
        '[IO.File]::WriteAllText("$d/run.ps1", $r)',
        '$a = New-ScheduledTaskAction -Execute "conhost.exe" -Argument "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File $d/run.ps1"',
        '$pr = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive',
    ]
    if fire_at is None:
        L.append(f'Register-ScheduledTask -TaskName "{name}" -Action $a -Principal $pr -Force | Out-Null')
        L.append(f'Start-ScheduledTask -TaskName "{name}"')
    else:
        L.append(f"$FireAt = [DateTimeOffset]::Parse('{iso(fire_at)}').LocalDateTime")
        L.append("$t = New-ScheduledTaskTrigger -Once -At $FireAt")
        L.append(f'Register-ScheduledTask -TaskName "{name}" -Action $a -Trigger $t -Principal $pr -Force | Out-Null')
    L.append('"registered"')
    return "\n".join(L) + "\n"


def record_handover(repo: Path, login: str, line: str) -> Path | None:
    """Put exactly one `Successor task:` line in the hand-over preamble (under the title; the form allows 2 lines there).
    A second call replaces it. Returns the path, or None when there is no hand-over file."""
    p = Path(repo) / HANDOVER_REL.format(login)
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    lines = [x for x in lines if not x.startswith(MARK)]
    lines.insert(1, line)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return p


def load_plan(login: str, home=None) -> dict | None:
    try:
        import json
        import supervisor
        return json.loads((supervisor.loop_home(home) / f"{login}-last-plan.json").read_text(encoding="utf-8")).get("plan")
    except Exception:
        return None


LIVE_STATES = ("Running", "Queued")     # a successor of this task is up or about to start (B10)
SELF_ENV = "MTS_SUCC_WAKE_TASK"         # run.ps1 sets it: the woken session is that task's own run


def task_state(name: str) -> str:
    """The scheduled task's State ('Running', 'Ready', 'Queued', ...), '' when it does not exist or cannot be read (OURS: the
    registration itself then fails or succeeds on its own; an unreadable state never blocks the chain)."""
    try:
        r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                            f"(Get-ScheduledTask -TaskName '{name}' -ErrorAction SilentlyContinue).State"],
                           capture_output=True, text=True, timeout=60)
        return r.stdout.strip()
    except Exception:
        return ""


def register(login: str, *, at: str | None = None, model: str = DEFAULT_MODEL, prompt_file: str | None = None,
             cwd: str | Path | None = None, dry: bool = False, now: datetime | None = None, plan: dict | None = None,
             home=None, base: str | None = None, runner=None, probe=None) -> dict:
    """Validate, choose fireAt, build the script, run it (unless dry), record the id line. Raises WakeError (fail closed).
    B10: refuses while MTS-SuccWake-<login> is Running or Queued (its successor is already up); -Force + Start would boot a second.
    `probe(name) -> state`; default: the real task state, or none when a stub runner is given (tests)."""
    now = now or datetime.now(timezone.utc)
    login = (login or "").strip().upper()[:1]
    if login not in ("A", "B", "C"):
        raise WakeError("login must be A, B or C")
    cwd = Path(cwd or REPO).resolve()
    check_checkout(cwd)
    if at:
        when = _parse(at)
        if when is None:
            raise WakeError(f"cannot read --at {at!r}")
        if when <= now:
            raise WakeError(f"--at {at} is in the past (now {iso(now)}): refused")
        why = "--at given"
    else:
        when, why = plan_fire_at(plan if plan is not None else load_plan(login, home), now)
    fire = iso(now) if when <= now + timedelta(minutes=1) else iso(when)
    usage = wake_usage(login, plan if plan is not None else load_plan(login, home), _parse(fire) or now, base)
    prompt = PROMPT.format(login=login, usage_line=usage_line(usage))
    if prompt_file:
        try:
            prompt = Path(prompt_file).read_text(encoding="utf-8").strip()
        except OSError as e:
            raise WakeError(f"cannot read --prompt-file: {e}")
        if not prompt or "'@" in prompt:
            raise WakeError("prompt file empty or contains a here-string terminator")
    immediate = when <= now + timedelta(minutes=1)
    script = build_script(login, model, prompt, cwd, None if immediate else when, base, usage=usage)
    line = f"{MARK} {task_name(login)} fireAt {fire} (4b2)"
    res = {"script": script, "line": line, "fire_at": fire, "why": why, "task": task_name(login), "ran": False, "handover": None, "usage": usage}
    if dry:
        return res
    if probe is None:
        probe = task_state if runner is None else (lambda name: "")
    state = probe(task_name(login))
    if state in LIVE_STATES and os.environ.get(SELF_ENV) != task_name(login):    # the task's own run may hand over
        raise WakeError(f"{task_name(login)} is already live ({state}): its successor is up; a second registration would start "
                        f"another Supervisor {login}. Refused")
    if runner is None:
        runner = _run_ps
    runner(script)
    res["ran"] = True
    res["handover"] = record_handover(cwd, login, line)
    return res


def _run_ps(script: str) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8-sig", newline="\n") as f:
        f.write(script)
        path = f.name
    try:
        r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", path],
                           capture_output=True, text=True)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    if r.returncode != 0:
        raise WakeError(f"registration failed (exit {r.returncode}): {(r.stdout + r.stderr).strip()[:300]}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--login", required=True, help="A|B|C: the supervisor login to wake")
    ap.add_argument("--at", help="UTC fireAt, e.g. 2026-10-27T20:05Z (future only); default: budget-aware from the pacer")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--prompt-file", help="override the successor prompt")
    ap.add_argument("--cwd", help="MTS checkout to run in (default: the checkout this script is in)")
    ap.add_argument("--dry", action="store_true", help="print the PowerShell, register nothing")
    a = ap.parse_args(argv)
    try:
        r = register(a.login, at=a.at, model=a.model, prompt_file=a.prompt_file, cwd=a.cwd, dry=a.dry)
    except WakeError as e:
        print(f"REFUSED: {e}")
        return 2
    if a.dry:
        print(r["script"])
    print(f"{r['line']} [{r['why']}]" + (" (dry: nothing registered)" if a.dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
