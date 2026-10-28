#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
T057 clutter-inventory module for MTS project.
This module performs read-only checks for repository clutter as defined in T057.
It never moves, renames, or deletes files. Its output feeds operator decisions.
"""

import os
import re
import sys
import datetime
from pathlib import Path

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parents[2]
OUT_PATH = REPO / "MyTradingSys" / "research" / "audits" / "T0_CHECKS.md"
DUMPS_WORKERS = REPO / "Dumps" / "workers"
DOC_SCAN_ROOTS = [REPO / "MyTradingSys" / "items", REPO / "MyTradingSys" / "research", REPO / "MyTradingSys" / "system"]
EXCLUDE_DIR_NAMES = {".git", "__pycache__", "Dumps", "backup_session"}
BIG_DIR_THRESHOLD_BYTES = 200 * 1024 * 1024
LEFTOVER_NAME_RE = re.compile(r"(rejected|qwen_raw|_raw)", re.IGNORECASE)
PRE_SUFFIX_RE = re.compile(r"\.pre_[A-Za-z0-9_]+(\.new)?$")

def find_stale_pre_backups() -> list:
    result = []
    for root, dirnames, filenames in os.walk(REPO):
        # Prune directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]
        for name in filenames:
            m = PRE_SUFFIX_RE.search(name)
            if m:
                stripped_name = name[:m.start()]
                full_path = Path(root) / name
                stripped_path = Path(root) / stripped_name
                if stripped_path.exists():
                    result.append(full_path.relative_to(REPO).as_posix())
    return sorted(result)

def find_leftover_names() -> list:
    if not DUMPS_WORKERS.exists():
        return []
    result = []
    # Walk DUMPS_WORKERS, but remove matching dirs from dirnames to avoid nested reporting
    for root, dirnames, filenames in os.walk(DUMPS_WORKERS):
        # Make a copy of dirnames to safely modify it
        dirs_to_check = list(dirnames)
        for name in dirs_to_check:
            if LEFTOVER_NAME_RE.search(name):
                full_path = Path(root) / name
                result.append(full_path.relative_to(REPO).as_posix())
                dirnames.remove(name)  # Remove from dirnames to prevent walking into it again
        for name in filenames:
            if LEFTOVER_NAME_RE.search(name):
                full_path = Path(root) / name
                result.append(full_path.relative_to(REPO).as_posix())
    return sorted(list(set(result)))

def find_big_dirs() -> list:
    result = []
    try:
        with os.scandir(REPO) as it:
            for entry in it:
                if entry.is_dir(follow_symlinks=False) and entry.name not in EXCLUDE_DIR_NAMES and not entry.name.startswith('.'):
                    total_size = 0
                    try:
                        for root, _, files in os.walk(entry.path):
                            # Prune directories
                            dirnames = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)) and d not in EXCLUDE_DIR_NAMES]
                            for name in files:
                                full_path = os.path.join(root, name)
                                try:
                                    total_size += os.path.getsize(full_path)
                                except OSError:
                                    continue
                    except OSError:
                        continue
                    if total_size > BIG_DIR_THRESHOLD_BYTES:
                        result.append((entry.name, total_size))
    except OSError:
        pass
    return sorted(result, key=lambda x: x[1], reverse=True)

def find_orphan_docs() -> list:
    # Collect all markdown candidates
    candidates = set()
    for root in DOC_SCAN_ROOTS:
        if root.exists():
            for md_file in root.rglob("*.md"):
                candidates.add(md_file.resolve())
    
    # Build haystack: (path, content) pairs of all .md and .py files
    haystack = []
    for root, dirnames, filenames in os.walk(REPO):
        # Prune directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]
        for name in filenames:
            p = Path(root) / name
            if p.suffix in (".md", ".py"):
                try:
                    content = p.read_text(encoding="utf-8", errors="ignore")
                    haystack.append((p, content))
                except OSError:
                    continue
    
    # Check each candidate for references
    result = []
    for candidate in candidates:
        needle = candidate.name
        referenced = False
        for path, text in haystack:
            if path.resolve() == candidate.resolve():
                continue  # Skip the candidate's own file
            if needle in text:
                referenced = True
                break
        if not referenced:
            result.append(candidate.relative_to(REPO).as_posix())
    return sorted(result)

def render_report(pre, leftover, big, orphan) -> str:
    timestamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
    report = f"# T0 clutter inventory (script-only checks, T057)\n"
    report += f"Generated: {timestamp}\n\n"

    report += "## Stale .pre_* backups (real file already exists)\n"
    if not pre:
        report += "(none found)\n\n"
    else:
        for path in pre:
            report += f"- {path}\n"
        report += "\n"

    report += "## Leftover rejected/raw directories or files\n"
    if not leftover:
        report += "(none found)\n\n"
    else:
        for path in leftover:
            report += f"- {path}\n"
        report += "\n"

    report += "## Directories over 200 MB\n"
    if not big:
        report += "(none found)\n\n"
    else:
        for name, size_bytes in big:
            report += f"- {name} ({size_bytes:,} bytes)\n"
        report += "\n"

    report += "## Markdown docs referenced nowhere else\n"
    if not orphan:
        report += "(none found)\n\n"
    else:
        for path in orphan:
            report += f"- {path}\n"
        report += "\n"

    report += "This report only lists candidates. Nothing is moved or deleted automatically -- an operator reviews this list before archiving anything (T057)."
    return report

def run_t0_checks() -> int:
    pre = find_stale_pre_backups()
    leftover = find_leftover_names()
    big = find_big_dirs()
    orphan = find_orphan_docs()

    report_text = render_report(pre, leftover, big, orphan)

    tmp = OUT_PATH.with_name("." + OUT_PATH.name + ".tmp")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(report_text)
    os.replace(tmp, OUT_PATH)

    print(f"WROTE {OUT_PATH}")
    print(f"stale_pre={len(pre)} leftover={len(leftover)} big_dirs={len(big)} orphan_docs={len(orphan)}")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(run_t0_checks())
