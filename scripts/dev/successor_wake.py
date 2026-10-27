#!/usr/bin/env python3
"""One-shot Windows Scheduled Task successor wake (4b2) — no human in the loop.

Implements MyTradingSys/research/lead/2026-10-27_successor-wake-design.md:
  - Registers a single-fire task `MTS-SuccWake-<login>` with one `FireAt` trigger.
  - No repetition / cron flags (`-Once`, self-unregisters after invocation).
  - Refuses past `--at` timestamps (fail closed, exit 2).
  - Computes budget-aware `fireAt` from `<loop_home>/<login>-last-plan.json` when `--at` is omitted:
      * If within 48h of weekly reset and >5% weekly pool remains -> `now + 1m` when 5h slots are available (`slots >= 1` and `mode != "STOP"`), or `five_reset` (or `now + 15m` fallback) when 5h budget is exhausted.
      * Else if `slots >= 1` and `mode != "STOP"` -> `now + 1m`.
      * Else -> `five_reset` (or `week_reset` if weekly pool exhausted, else `now + 15m`).
  - Records `- Successor task: MTS-SuccWake-<login> fireAt <iso> (4b2)` inside `## Open`
    of `MyTradingSys/system/handover/SUPERVISOR_<login>.md` idempotently.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
LOOP_HOME = Path(os.environ.get("MTS_LOOP_HOME") or (Path.home() / ".claude" / "mts-loop"))
DEFAULT_MODEL = "claude-sonnet-5-5"


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _parse_iso(ts: str) -> dt.datetime:
    d = dt.datetime.fromisoformat(ts.strip().replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def _iso_z(d: dt.datetime) -> str:
    return d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _prompt_stage_dir(login: str) -> Path:
    base = Path("F:/MTS/succ_wake") if Path("F:/").exists() else (Path(tempfile.gettempdir()) / "mts_succ_wake")
    return base / login.upper()


def default_prompt(login: str) -> str:
    L = login.upper()
    return (
        f"You are Supervisor {L}. Read MyTradingSys/system/handover/SUPERVISOR_{L}.md, "
        f"run `python scripts/dev/supervisor.py wake --lane {L.lower()}`, and continue the loop."
    )


def budget_fire_at(loop_home: Path | None, login: str, now: dt.datetime | None = None) -> dt.datetime:
    now = now or _utc_now()
    home = loop_home or LOOP_HOME
    plan_file = Path(home) / f"{login.upper()}-last-plan.json"
    immediate = now + dt.timedelta(minutes=1)
    if not plan_file.is_file():
        return immediate
    try:
        plan: dict[str, Any] = json.loads(plan_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return immediate

    slots = int(plan.get("slots", 1) or 0)
    mode = str(plan.get("mode") or "NORMAL").upper()
    five_raw = plan.get("five_reset")
    five_dt: dt.datetime | None = None
    if five_raw:
        try:
            cand_five = _parse_iso(str(five_raw))
            if cand_five > now:
                five_dt = cand_five
        except ValueError:
            pass

    # Check T-48h weekly reset window with >5% weekly left:
    # if 5h budget is exhausted (slots == 0 or mode == "STOP"), wait until five_reset if present so we don't wake into a 5h block;
    # otherwise wake immediately (now + 1m) to drain the weekly pool.
    wk_reset_raw = plan.get("week_reset")
    wk_pct = float(plan.get("week_pct", 0) or 0)
    wk_left = max(0.0, 100.0 - wk_pct)
    if wk_reset_raw:
        try:
            wk_dt = _parse_iso(str(wk_reset_raw))
            while wk_dt <= now:
                wk_dt += dt.timedelta(days=7)
            hours_to_wk = (wk_dt - now).total_seconds() / 3600.0
            if 0 < hours_to_wk <= 48.0 and wk_left > 5.0:
                if slots == 0 or mode == "STOP":
                    if five_dt is not None and five_dt < wk_dt:
                        return five_dt
                    return now + dt.timedelta(minutes=15)
                return immediate
        except ValueError:
            pass

    if slots >= 1 and mode != "STOP":
        return immediate

    if five_dt is not None:
        return five_dt
    if wk_reset_raw:
        try:
            cand = _parse_iso(str(wk_reset_raw))
            if cand > now:
                return cand
        except ValueError:
            pass
    return now + dt.timedelta(minutes=15)


def build_ps_script(
    *,
    login: str,
    fire_at: dt.datetime,
    cwd: Path,
    model: str = DEFAULT_MODEL,
    prompt_text: str | None = None,
    now: dt.datetime | None = None,
) -> str:
    now = now or _utc_now()
    if fire_at <= now:
        raise ValueError(f"--at timestamp {_iso_z(fire_at)} is in the past (now={_iso_z(now)})")
    L = login.upper()
    if L not in {"A", "B", "C"}:
        raise ValueError(f"--login must be A, B, or C (got {login!r})")
    import re
    if not re.fullmatch(r"[A-Za-z0-9._-]+", model):
        raise ValueError(f"--model contains invalid characters: {model!r}")

    task_name = f"MTS-SuccWake-{L}"
    stage_dir = _prompt_stage_dir(L)
    prompt_path = stage_dir / "prompt.txt"
    runner_path = stage_dir / "run_once.ps1"
    body = (prompt_text or default_prompt(L)).strip()
    fire_iso = _iso_z(fire_at)
    cwd_str = str(Path(cwd).resolve()).replace("'", "''")
    stage_str = str(stage_dir).replace("'", "''")
    prompt_str = str(prompt_path).replace("'", "''")
    runner_str = str(runner_path).replace("'", "''")
    escaped_body = body.replace("'", "''")

    return "\n".join(
        [
            "$ErrorActionPreference = 'Stop'",
            f"$stageDir = '{stage_str}'",
            "New-Item -ItemType Directory -Force -Path $stageDir | Out-Null",
            f"Set-Content -LiteralPath '{prompt_str}' -Value '{escaped_body}' -Encoding UTF8",
            "$runnerLines = @(",
            f"  'Set-Location -LiteralPath ''{cwd_str}'''",
            f"  'Unregister-ScheduledTask -TaskName \"{task_name}\" -Confirm:$false -ErrorAction SilentlyContinue'",
            f"  '$p = Get-Content -LiteralPath ''{prompt_str}'' -Raw -Encoding UTF8'",
            f"  'claude -p --model {model} $p'",
            ")",
            f"Set-Content -LiteralPath '{runner_str}' -Value ($runnerLines -join \"`r`n\") -Encoding UTF8",
            f"$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File \"{runner_str}\"' -WorkingDirectory '{cwd_str}'",
            f"$trigger = New-ScheduledTaskTrigger -Once -At ([datetime]::Parse('{fire_iso}').ToLocalTime())",
            "$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited",
            "$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries",
            f"Register-ScheduledTask -TaskName '{task_name}' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null",
        ]
    )


def record_handover_line(handover_path: Path, login: str, fire_at: dt.datetime) -> None:
    if not handover_path.is_file():
        return
    L = login.upper()
    prefix = f"- Successor task: MTS-SuccWake-{L}"
    entry = f"{prefix} fireAt {_iso_z(fire_at)} (4b2)"
    lines = handover_path.read_text(encoding="utf-8").splitlines()
    filtered = [ln for ln in lines if not ln.strip().startswith(prefix)]
    out: list[str] = []
    inserted = False
    for idx, ln in enumerate(filtered):
        out.append(ln)
        if ln.strip() == "## Open" and not inserted:
            out.append(entry)
            inserted = True
    if not inserted:
        out.append(entry)
    with handover_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out).rstrip() + "\n")


def _run_ps(script: str) -> tuple[int, str]:
    if os.environ.get("MTS_NO_SCHTASKS") == "1" or sys.platform != "win32":
        return 1, "skipped"
    try:
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except OSError as exc:
        return 1, str(exc)


def register_for_handover(
    repo: Path,
    login: str,
    handover_path: Path,
    *,
    home: Path | None = None,
    now: dt.datetime | None = None,
    fire_at: dt.datetime | None = None,
    model: str = DEFAULT_MODEL,
    dry: bool = False,
) -> dict[str, Any]:
    now = now or _utc_now()
    L = login.upper()
    if L not in {"A", "B", "C"}:
        return {"ok": False, "reason": f"unsupported login {login!r}"}
    target_at = fire_at or budget_fire_at(home, L, now=now)
    script = build_ps_script(login=L, fire_at=target_at, cwd=repo, model=model, now=now)
    if dry:
        return {"ok": True, "dry": True, "fire_at": _iso_z(target_at), "script": script}
    rc, out = _run_ps(script)
    if rc == 0:
        record_handover_line(handover_path, L, target_at)
    return {"ok": rc == 0, "rc": rc, "fire_at": _iso_z(target_at), "output": out.strip()}


def main(argv: list[str] | None = None, *, now: dt.datetime | None = None) -> int:
    ap = argparse.ArgumentParser(description="Register one-shot Windows Scheduled Task successor wake (4b2).")
    ap.add_argument("--login", required=True, help="Supervisor login lane (A, B, or C)")
    ap.add_argument("--at", default="", help="ISO UTC fire timestamp (must be in the future)")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="Claude model id for successor wake")
    ap.add_argument("--prompt-file", default="", help="Optional path to prompt file")
    ap.add_argument("--cwd", default=str(REPO), help="Working directory for the successor task")
    ap.add_argument("--dry", action="store_true", help="Print PowerShell registration script and exit without running")
    args = ap.parse_args(argv)

    now = now or _utc_now()
    L = args.login.strip().upper()
    cwd = Path(args.cwd).resolve()
    if not args.dry and not (cwd / "MyTradingSys").is_dir():
        print(f"ERROR: --cwd {cwd} is not an MTS checkout (missing MyTradingSys/)", file=sys.stderr)
        return 2

    try:
        fire_at = _parse_iso(args.at) if args.at else budget_fire_at(LOOP_HOME, L, now=now)
        prompt_text = Path(args.prompt_file).read_text(encoding="utf-8") if args.prompt_file else default_prompt(L)
        script = build_ps_script(login=L, fire_at=fire_at, cwd=cwd, model=args.model, prompt_text=prompt_text, now=now)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.dry:
        print(script)
        return 0

    rc, out = _run_ps(script)
    if rc != 0:
        print(f"ERROR: Register-ScheduledTask failed (rc={rc}): {out}", file=sys.stderr)
        return 1
    ho = cwd / "MyTradingSys" / "system" / "handover" / f"SUPERVISOR_{L}.md"
    record_handover_line(ho, L, fire_at)
    print(f"registered MTS-SuccWake-{L} fireAt {_iso_z(fire_at)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
