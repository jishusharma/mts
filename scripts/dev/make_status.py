#!/usr/bin/env python3
"""
Generate MyTradingSys/research/STATUS.md (the boot read: keep it short, one home per fact).
Gathers: the CI green line, the layer x gate board, trunk tip, in-flight .new files, the 5 newest reports, screenshots, the layer lab, the
hygiene report when this host has one, project groups, open findings. Lists that other indexes already hold (queue
status of the retired NUC worker, 10 commits, delivered lab cards) are not repeated here.
"""
import nowin  # B190: scheduled run (hidden console) must not flash git windows
nowin.install()
import json
import subprocess
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
import re

TRUNK = "origin/fast-track"
TRUNK_COMMITS = 3
GATE_BOARD = "MyTradingSys/system/gate_board.json"
RESEARCH_PATHS = ("MyTradingSys/research/", "MyTradingSys/methodology/", "MyTradingSys/extracts/", "MyTradingSys/backtest/")
INFRA_CAP_PCT = 30
RECENT_REPORTS = 5
RECENT_REPORT_DAYS = 3


def run_cmd(cmd, cwd=None):
    """Run shell command and return stdout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def get_trunk_log(n=TRUNK_COMMITS, cwd=None):
    """(label, one-line log) of the last n commits on origin/fast-track; falls back to HEAD and says so when the ref is missing.
    Never this host's local HEAD when the trunk is known: that was 258 commits behind the tip in the committed copy."""
    if run_cmd(f"git rev-parse --verify --quiet {TRUNK}", cwd=cwd):
        return TRUNK, run_cmd(f"git log --oneline -{n} {TRUNK}", cwd=cwd)
    return "HEAD (no origin/fast-track ref on this host)", run_cmd(f"git log --oneline -{n}", cwd=cwd)


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
        r = subprocess.run([sys.executable, "scripts/dev/codex_run.py", "status", "--brief"], capture_output=True, text=True, timeout=60)
        return (r.stdout or r.stderr).strip() or "(no lab status)"
    except Exception as e:
        return f"(lab status unavailable: {e})"


def get_hygiene_status(sched_dir=None):
    """Head of the scheduled daily hygiene report (scripts/dev/daily_hygiene.py), or "" when this host has none.

    The report is gitignored and host-local, so a host without the scheduled task would print 'no hygiene run yet' forever:
    the section is left out instead (main() skips an empty result). Never fails the status build."""
    d = Path(sched_dir) if sched_dir else Path("MyTradingSys/runtime/sched")
    f = d / "hygiene_latest.md"
    try:
        lines = f.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    return chr(10).join(lines[:12])


def get_stale_pages():
    """(count, lines) for the published claude.ai pages whose repo build differs from the last publish (artifacts.py stale)."""
    try:
        import artifacts as af
        lines = af.stale_lines(af.load())
    except Exception as e:  # a broken generator must not stop STATUS.md
        return 0, [f"(stale check failed: {e})"]
    return len(lines), lines


def get_group_line():
    """Open / HIGH / closed registry rows per project group; never fails the status build."""
    try:
        r = subprocess.run([sys.executable, "scripts/dev/make_groups.py", "--line"], capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).strip() or "(no group line)"
    except Exception as e:
        return f"(group line unavailable: {e})"


def get_new_files(root="MyTradingSys", cwd=None, now=None):
    """(path, age in hours) of the .new files under root.

    A tracked .new file is aged by its last commit, an untracked one by mtime: a checkout stamps every tracked file with the
    checkout time, which showed two days-old staged files as 0.2 h old."""
    base = Path(cwd) if cwd else Path(".")
    now = now or datetime.now()
    tracked = set(run_cmd(f'git ls-files -- "{root}/*.new"', cwd=cwd).splitlines())   # git pathspec * crosses directories
    new_files = []
    for dirpath, dirs, files in os.walk(base / root):
        for f in files:
            if not f.endswith(".new"):
                continue
            full = Path(dirpath) / f
            rel = full.relative_to(base).as_posix()
            when = None
            if rel in tracked:
                ts = run_cmd(f'git log -1 --format=%ct -- "{rel}"', cwd=cwd)
                when = datetime.fromtimestamp(int(ts)) if ts.isdigit() else None
            if when is None:
                when = datetime.fromtimestamp(os.path.getmtime(full))
            new_files.append((rel, (now - when).total_seconds() / 3600))

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
    now_ts = (now or datetime.now()).timestamp()
    age_min = (now_ts - min(pending)) / 60
    tag = (f"RED: oldest ungreen commit is {age_min / 60:.1f} h old - CI is failing, auto-deploy is idle; fix CI first"
           if age_min > CI_STALE_MIN else "CI running")
    # both numbers: the first-parent count (landings, drives the age above) is far below the plain commit count when merges land
    total = run_cmd("git rev-list --count origin/green/fast-track..origin/fast-track", cwd=cwd)
    green_ts = run_cmd("git log -1 --format=%ct origin/green/fast-track", cwd=cwd)
    green_age = f", {(now_ts - int(green_ts)) / 3600:.1f} h old" if green_ts.isdigit() else ""
    return (f"CI green: {green} ({when}{green_age}), {len(pending)} trunk landing(s) / {total or '?'} commit(s) behind "
            f"origin/fast-track: {tag}")


LIVE_MARKER = ".mts_live"   # marker FILE at the root of the live tree (auto_deploy.Ops.is_live)


def is_live_tree(root="."):
    return (Path(root) / LIVE_MARKER).exists()


def get_ci_card_line(ci_line, root=".", env=None):
    """The "CI card: ..." status line, or None when there is nothing to say (CI not red, or MTS_NO_CI_CARD set).

    Red CI files ONE "fix CI <sha>" card (ci_red_card.py); a builder ships it with the next ship. The LIVE tree never files it: this script runs
    there on a schedule, the untracked card then clashed with the same card shipped to fast-track and stopped the deploy merge (2026-10-16)."""
    if "RED" not in ci_line or (os.environ if env is None else env).get("MTS_NO_CI_CARD"):
        return None
    if is_live_tree(root):
        return "CI card: not filed (live tree)"
    try:
        import ci_red_card
        return "CI card: " + "; ".join(ci_red_card.run(str(Path(root).resolve()), apply=True))
    except Exception as e:   # never block the status page
        return f"CI card: not filed ({type(e).__name__}); run scripts/dev/ci_red_card.py --apply"


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

def _git(args, cwd=None):
    """git stdout as text, "" on any error (list form: no shell quoting of paths)."""
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, cwd=cwd)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def get_commit_mix(ref, cwd=None, now=None, hours=24):
    """Non-merge commits on ref in the last `hours`: claim/release, research (touches RESEARCH_PATHS, STATUS.md aside) or
    other (infra, process, pings). Observer 2026-10-15: other was 40% over 3 days; the board flags it above INFRA_CAP_PCT."""
    since = (now or time.time()) - hours * 3600
    n = {"research": 0, "claim/release": 0, "other": 0}
    for block in _git(["log", ref, "--no-merges", "-n", "3000", "--format=@@%ct %s", "--name-only"], cwd).split("@@")[1:]:
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        ts, _, subj = lines[0].partition(" ")
        if not ts.isdigit() or int(ts) < since:
            continue
        if re.match(r"(claim|release) ", subj):
            n["claim/release"] += 1
        elif any(f.startswith(RESEARCH_PATHS) and not f.endswith("/STATUS.md") for f in lines[1:]):
            n["research"] += 1
        else:
            n["other"] += 1
    tot = sum(n.values())
    if not tot:
        return f"commits {hours}h: 0"
    pct = {k: round(100 * v / tot) for k, v in n.items()}
    flag = f"  OVER {INFRA_CAP_PCT}% CAP" if pct["other"] > INFRA_CAP_PCT else ""
    return f"commits {hours}h: {tot} = research {pct['research']}% | claim/release {pct['claim/release']}% | other {pct['other']}%{flag}"


def get_gate_board(cwd=None, now=None, board=GATE_BOARD):
    """Layer x gate board (LAYER_REBUILD_PLAN_2026-10-15 s5): per layer its gate, the hours since its proof file last changed on
    the trunk, the next gate; then the 24 h commit mix. No proof changed in 24 h = the next spawn targets a gate."""
    now = now or time.time()
    p = Path(cwd or ".") / board
    if not p.exists():
        return [f"(no {board})"]
    ref = TRUNK if _git(["rev-parse", "--verify", "--quiet", TRUNK], cwd) else "HEAD"
    out, ages = [], []
    for row in json.loads(p.read_text(encoding="utf-8")).get("layers", []):
        proof = row.get("proof", [])
        ts = [_git(["log", "-1", "--format=%ct", ref, "--", f], cwd) for f in proof]
        ts = [int(t) for t in ts if t.isdigit()]
        if ts:
            age = (now - max(ts)) / 3600
            ages.append(age)
            moved = f"proof changed {age:.0f}h ago"
        else:
            moved = "proof not on trunk"
        out.append(f"{row.get('layer', '?'):<7} {row.get('gate', '?'):<3} {moved} | next: {row.get('next', '?')} | "
                   f"proof: {', '.join(proof) or '(none)'}")
    if not ages or min(ages) > 24:
        out.append("NO GATE MOVED IN 24h: the next spawn targets a gate (LAYER_REBUILD_PLAN s5)")
    out.append(get_commit_mix(ref, cwd=cwd, now=now))
    return out


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../..")

    output = []
    output.append("# Development Status")
    output.append("")
    output.append("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    output.append("")

    # Git status: trunk, not this host's branch (the old Branch line named the generating host's checkout)
    output.append("## Git Status")
    ci_line = get_ci_line()
    output.append(ci_line)
    card_line = get_ci_card_line(ci_line)
    if card_line:
        output.append(card_line)
    output.append(get_lessons_line())
    n_stale, stale_lines = get_stale_pages()
    output.append(f"Pages stale: {n_stale}")
    output.extend(stale_lines)
    output.append("")

    # Gate board: which gate each layer is at and when its proof last moved (LAYER_REBUILD_PLAN_2026-10-15 s5; gate_board.json)
    output.append("## Gate Board")
    output.append("```")
    output.extend(get_gate_board())
    output.append("```")
    output.append("")
    label, log = get_trunk_log()
    output.append(f"**Last {TRUNK_COMMITS} commits on {label}:**")
    output.append("```")
    output.append(log)
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

    # Recent reports: the newest few, one line each (the full list is git log / LAYERS.md)
    output.append(f"## Recent Reports (newest {RECENT_REPORTS}, last {RECENT_REPORT_DAYS} days)")
    reports = get_recent_reports(days=RECENT_REPORT_DAYS)[:RECENT_REPORTS]
    if reports:
        for fpath, mtime, heading in reports:
            heading_str = heading if heading else "(no heading)"
            output.append(f"- {fpath} ({mtime}) {heading_str[:90]}")
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

    # Scheduled daily hygiene (gate, where, declutter dry run): the report a session reads at boot; no section on a host with no report
    hygiene = get_hygiene_status()
    if hygiene:
        output.append("## Daily Hygiene (scheduled)")
        output.append("```")
        output.append(hygiene)
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
