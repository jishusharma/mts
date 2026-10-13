#!/usr/bin/env python3
"""
Generate MyTradingSys/research/STATUS.md
Gathers: git status, queue_tool status, in-flight .new files, recent reports, open findings.
"""
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re

def run_cmd(cmd, cwd=None):
    """Run shell command and return stdout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def get_git_branch():
    """Get current git branch."""
    return run_cmd("git branch --show-current")

def get_git_log():
    """Get last 10 commits."""
    return run_cmd("git log --oneline -10")

def get_queue_status():
    """Get queue_tool.py status output."""
    return run_cmd("python scripts/worker/queue_tool.py status")

def get_screenshot_status():
    """One line from the screenshot store plus any overdue shots; never fails the status build."""
    try:
        r = subprocess.run([sys.executable, "scripts/dev/shot.py", "status"], capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).strip() or "(no screenshot store on this machine)"
    except Exception as e:
        return f"(screenshot status unavailable: {e})"


def get_lab_status():
    """Codex layer lab in plain words (scripts/dev/codex_run.py status); never fails the status build."""
    try:
        r = subprocess.run([sys.executable, "scripts/dev/codex_run.py", "status"], capture_output=True, text=True, timeout=60)
        return (r.stdout or r.stderr).strip() or "(no lab status)"
    except Exception as e:
        return f"(lab status unavailable: {e})"


def get_hygiene_status(sched_dir=None):
    """Head of the scheduled daily hygiene report (scripts/dev/daily_hygiene.py); never fails the status build."""
    d = Path(sched_dir) if sched_dir else Path("MyTradingSys/runtime/sched")
    f = d / "hygiene_latest.md"
    try:
        lines = f.read_text(encoding="utf-8").splitlines()
    except OSError:
        return "(no hygiene run on this host yet: python scripts/dev/daily_hygiene.py, or register_cicd_tasks.ps1)"
    return chr(10).join(lines[:12])


def get_group_line():
    """Open / HIGH / closed registry rows per project group; never fails the status build."""
    try:
        r = subprocess.run([sys.executable, "scripts/dev/make_groups.py", "--line"], capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).strip() or "(no group line)"
    except Exception as e:
        return f"(group line unavailable: {e})"


def get_new_files():
    """Get .new files under MyTradingSys with age in hours."""
    now = datetime.now()
    new_files = []
    for root, dirs, files in os.walk("MyTradingSys"):
        for f in files:
            if f.endswith(".new"):
                fpath = os.path.join(root, f)
                mtime = os.path.getmtime(fpath)
                mtime_dt = datetime.fromtimestamp(mtime)
                age_hours = (now - mtime_dt).total_seconds() / 3600
                new_files.append((fpath, age_hours))

    new_files.sort(key=lambda x: x[0])
    return new_files

REPORT_TAGS = ("HANDOFF", "SESSION", "REPORT")


def git_commit_times(root, since_days=7, cwd=None):
    """{path: last commit datetime} for files under root committed in the last since_days (one git call)."""
    out = run_cmd(f'git log --since="{since_days} days ago" --name-only --format=@%ct -- "{root}"', cwd=cwd)
    times, ts = {}, None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("@") and line[1:].isdigit():
            ts = datetime.fromtimestamp(int(line[1:]))
        elif line and ts is not None:
            times.setdefault(line, ts)  # newest first, keep the first (latest) commit seen
    return times


def git_tracked(root, cwd=None):
    return set(run_cmd(f'git ls-files -- "{root}"', cwd=cwd).splitlines())


def get_recent_reports(root="MyTradingSys/research", days=7, cwd=None):
    """*HANDOFF*/*SESSION*/*REPORT*.md changed in the last `days` days.

    Tracked files are dated by their last commit, not mtime: a fresh clone or checkout stamps every file
    with the checkout time, which made every old handoff look new. Untracked files fall back to mtime.
    """
    base = Path(cwd) if cwd else Path(".")
    cutoff = datetime.now() - timedelta(days=days)
    committed = git_commit_times(root, days, cwd=cwd)
    tracked = git_tracked(root, cwd=cwd)
    reports = []
    for dirpath, dirs, files in os.walk(base / root):
        for f in files:
            if not (f.endswith(".md") and any(x in f for x in REPORT_TAGS)):
                continue
            full = Path(dirpath) / f
            rel = full.relative_to(base).as_posix()
            if rel in tracked:
                when = committed.get(rel)  # tracked but not committed in the window -> old
            else:
                when = datetime.fromtimestamp(os.path.getmtime(full))
            if when is None or when < cutoff:
                continue
            first_heading = ""
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        if line.startswith("#"):
                            first_heading = line.strip()
                            break
            except OSError:
                first_heading = "(read error)"
            reports.append((rel, when.strftime("%Y-%m-%d %H:%M"), first_heading))
    reports.sort(key=lambda x: x[1], reverse=True)
    return reports


# keep in step with the push paths filter in .github/workflows/ci.yml
CI_PATHS = ["src", "MyTradingSys/backtest", "MyTradingSys/execution", "MyTradingSys/runtime", "MyTradingSys/tests",
            "MyTradingSys/items", "scripts", ".github/workflows"]
CI_STALE_MIN = 60  # a CI run takes ~4 min; a commit still not green after this means CI is red or stuck


def get_ci_line(cwd=None, now=None):
    """Where origin/green/fast-track (last SHA CI passed on both OSes) sits vs origin/fast-track.

    Auto-deploy only deploys the green SHA, so an old ungreen commit means CI is red and nothing deploys."""
    green = run_cmd("git rev-parse --short origin/green/fast-track", cwd=cwd)
    if not re.fullmatch(r"[0-9a-f]{4,40}", green or ""):
        return "CI green: (no origin/green/fast-track ref here; git fetch origin green/fast-track)"
    when = run_cmd("git log -1 --format=%ci origin/green/fast-track", cwd=cwd)
    # --first-parent: trunk commits only; their committer time ~ when they landed (merged branches carry old times)
    pending = [int(t) for t in run_cmd("git log --first-parent --format=%ct origin/green/fast-track..origin/fast-track", cwd=cwd).split()
               if t.isdigit()]
    if not pending:
        return f"CI green: {green} ({when}) = origin/fast-track: OK"
    # ci.yml only runs on pushes touching CI_PATHS: a tip that differs from green only in docs never gets a run
    if not run_cmd("git diff --name-only origin/green/fast-track origin/fast-track -- " + " ".join(CI_PATHS), cwd=cwd):
        return f"CI green: {green} ({when}), {len(pending)} docs-only commit(s) ahead (no CI-gated path changed): OK"
    age_min = ((now or datetime.now()).timestamp() - min(pending)) / 60
    tag = (f"RED: oldest ungreen commit is {age_min / 60:.1f} h old - CI is failing, auto-deploy is idle; fix CI first"
           if age_min > CI_STALE_MIN else "CI running")
    return f"CI green: {green} ({when}), {len(pending)} commit(s) behind origin/fast-track: {tag}"


LESSONS = "MyTradingSys/system/LESSONS_LEARNED.md"
DIGEST = "MyTradingSys/system/LESSONS_DIGEST.md"


def get_lessons_line(cwd=None):
    """LESSONS_DIGEST.md (the boot read) records the LESSONS_LEARNED.md blob it was synced from; STALE when that moved."""
    base = Path(cwd) if cwd else Path(".")
    try:
        m = re.search(r"at blob: ([0-9a-f]{8})", (base / DIGEST).read_text(encoding="utf-8"))
    except OSError:
        return f"LESSONS: no {DIGEST}; read {LESSONS} in full"
    blob = run_cmd(f'git hash-object "{LESSONS}"', cwd=cwd)[:8]
    if not m or not re.fullmatch(r"[0-9a-f]{8}", blob):
        return "LESSONS: digest sync blob unreadable; read LESSONS_LEARNED.md entries newer than the digest"
    if m.group(1) == blob:
        return "LESSONS: digest in sync"
    return (f"LESSONS: digest STALE (synced {m.group(1)}, now {blob}): read the new LESSONS_LEARNED.md entries "
            "(git diff), add their rule lines to LESSONS_DIGEST.md, update the blob")


def get_open_findings():
    """Get open findings from OPEN_FINDINGS.md (status == OPEN)."""
    findings = []
    open_findings_path = "MyTradingSys/research/fast_track_2026-09-27/OPEN_FINDINGS.md"

    if os.path.exists(open_findings_path):
        try:
            with open(open_findings_path, 'r', encoding='utf-8', errors='ignore') as f:
                in_table = False
                for line in f:
                    # Skip header rows and markdown formatting
                    if line.startswith("|"):
                        if "ID" in line or "---" in line:
                            in_table = True
                            continue
                        if in_table and "OPEN" in line:
                            # Extract the finding ID and relevant info
                            parts = [p.strip() for p in line.split("|")]
                            if len(parts) >= 4 and parts[2] == "OPEN":
                                finding_id = parts[1]
                                fixed_in = parts[3]
                                note = parts[4] if len(parts) > 4 else ""
                                findings.append(f"- {finding_id}: {fixed_in} {note}")
        except:
            pass

    return findings

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../..")

    output = []
    output.append("# Development Status")
    output.append("")
    output.append("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    output.append("")

    # Git status
    output.append("## Git Status")
    branch = get_git_branch()
    output.append(f"**Branch:** {branch} (the host that generated this file; yours may differ)")
    output.append("")
    output.append(get_ci_line())
    output.append(get_lessons_line())
    output.append("")
    output.append("**Last 10 commits:**")
    output.append("```")
    output.append(get_git_log())
    output.append("```")
    output.append("")

    # Queue status
    output.append("## Queue Status")
    output.append("```")
    output.append(get_queue_status())
    output.append("```")
    output.append("")

    # In-flight .new files
    output.append("## In-Flight .new Files")
    new_files = get_new_files()
    if new_files:
        for fpath, age_hours in new_files:
            output.append(f"- {fpath} ({age_hours:.1f}h)")
    else:
        output.append("(none)")
    output.append("")

    # Recent reports
    output.append("## Recent Reports (last 7 days)")
    reports = get_recent_reports()
    if reports:
        for fpath, mtime, heading in reports:
            heading_str = heading if heading else "(no heading)"
            output.append(f"- {fpath} ({mtime}) {heading_str}")
    else:
        output.append("(none)")
    output.append("")

    # Screenshots: every image the operator showed a session, and how far each got (scripts/dev/shot.py)
    output.append("## Screenshots")
    output.append("```")
    output.append(get_screenshot_status())
    output.append("```")
    output.append("")

    # Codex layer lab: unattended runs on JIS-NUC; a line under NEEDS A LOOK is work for the next NUC session (LAYER_LAB.md)
    output.append("## Layer Lab (Codex)")
    output.append("```")
    output.append(get_lab_status())
    output.append("```")
    output.append("")

    # Scheduled daily hygiene (gate, where, declutter dry run): the report a session reads at boot
    output.append("## Daily Hygiene (scheduled)")
    output.append("```")
    output.append(get_hygiene_status())
    output.append("```")
    output.append("")

    # Project groups: where the open work sits (definitions: MyTradingSys/system/groups.json, map: PROJECT_MAP.md)
    output.append("## Project Groups")
    output.append("```")
    output.append(get_group_line())
    output.append("```")
    output.append("")

    # Open findings
    output.append("## Open Findings")
    findings = get_open_findings()
    if findings:
        for finding in findings:
            output.append(finding)
    else:
        output.append("(none)")
    output.append("")

    # Write output
    status_path = "MyTradingSys/research/STATUS.md"
    with open(status_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))

    # Print summary
    total_lines = len(output)
    print(f"Generated {status_path} ({total_lines} lines)")
    print("\nFirst 20 lines:")
    for i, line in enumerate(output[:20]):
        print(line)

if __name__ == "__main__":
    main()
