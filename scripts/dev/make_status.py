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

def get_recent_reports():
    """Get recent *HANDOFF*.md, *SESSION*.md, *REPORT*.md files (last 7 days)."""
    cutoff = datetime.now() - timedelta(days=7)
    reports = []

    for root, dirs, files in os.walk("MyTradingSys/research"):
        for f in files:
            if any(x in f for x in ["HANDOFF", "SESSION", "REPORT"]) and f.endswith(".md"):
                fpath = os.path.join(root, f)
                mtime = os.path.getmtime(fpath)
                mtime_dt = datetime.fromtimestamp(mtime)

                if mtime_dt >= cutoff:
                    # Get first heading
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                            first_heading = ""
                            for line in fh:
                                if line.startswith("#"):
                                    first_heading = line.strip()
                                    break
                    except:
                        first_heading = "(read error)"

                    reports.append((fpath, mtime_dt.strftime("%Y-%m-%d %H:%M"), first_heading))

    reports.sort(key=lambda x: x[1], reverse=True)
    return reports

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
    output.append(f"**Branch:** {branch}")
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
