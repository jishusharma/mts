#!/usr/bin/env python
"""wt_maint.py - worktree maintenance, the same job on every device (JIS-NB, JIS-NUC, Lenovo laptop).

  python scripts/dev/wt_maint.py                 dry run (default): print what would happen, change nothing
  python scripts/dev/wt_maint.py --apply         do it
  python scripts/dev/wt_maint.py install [--at HH:MM]   register the daily headless scheduled task MTS-WorktreeMaint-<device>
  python scripts/dev/wt_maint.py status          device, task state, last run, last report
  python scripts/dev/wt_maint.py uninstall

One run: fetch origin/fast-track; retire finished worktrees (sync.py tidy's rules, with `--all`: hand-named trees too);
`git worktree prune`; delete local branches fully merged into origin/fast-track; write the trees that still hold work to
Dumps/worktree_report.txt (gitignored) and append one line to the SUPERVISOR_LOG.
Never touched: the primary tree, the tree we run in, the live tree (.mts_live), lane trees, Codex trees, any tree changed in the
last 30 minutes, any tree with uncommitted files or commits not on origin/fast-track. Never stash / reset / force-push. Idempotent.
Ignored data worth keeping (not regenerable, see sync.REGENERABLE) is moved to <primary>/Dumps/wt_rescue/<tree>/ before removal.
"""
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SUPERVISOR_LOG_REL = "MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_LOG.md"
RECENT_MIN = 30
IDLE_HOURS = sync.TIDY_IDLE_HOURS
PROTECT_BRANCHES = ("fast-track", "main", "master")
TASK_PREFIX = "MTS-WorktreeMaint"
# hostname (lower) -> canonical device name; the Lenovo laptop reports DESKTOP-F7IU69N (DEVICES.md s0)
KNOWN_DEVICES = {"jis-nb": "JIS-NB", "jis-nuc": "JIS-NUC", "desktop-f7iu69n": "Lenovo laptop"}


def device_name(hostname=None):
    """Canonical device name from the machine's hostname; an unknown host keeps its own (upper-cased) name."""
    h = (hostname or socket.gethostname()).strip()
    return KNOWN_DEVICES.get(h.lower(), h.upper() or "UNKNOWN")


def task_name(device=None):
    return f"{TASK_PREFIX}-{re.sub(r'[^A-Za-z0-9]+', '-', device or device_name()).strip('-')}"


def primary(repo):
    return Path(sync.worktrees(repo)[0][0])


def protected_reason(p, branch, primary_tree, here, now, mtime_of=None):
    """Why tree `p` must never be touched, or None. Independent of tidy's own rules: these are the hard filters."""
    p = Path(p).resolve()
    low = p.name.lower()
    if p == primary_tree.resolve():
        return "primary tree"
    if p == here:
        return "this tree"
    if (p / sync.LIVE_MARKER).exists():
        return "live tree"
    if p.name in sync.LANE_WORKTREES or low.startswith(("mts-relay", "mts-push", "mts-refiner", "mts-control-room")):
        return "lane tree"
    if "codex" in low or "codex" in branch.lower():
        return "codex tree"
    if "gemini" in low or "gemini" in branch.lower():
        return "gemini tree"   # the Antigravity project opens this folder; removing it breaks the project
    if "gpt" in low or "gpt" in branch.lower():
        return "gpt tree"      # GPT lab trees: same protection as codex trees
    if branch in PROTECT_BRANCHES or branch == "(detached)":
        return f"branch {branch}"
    idle = sync.idle_hours(p, branch, now) if mtime_of is None else mtime_of(p)
    if idle * 60 < RECENT_MIN:
        return f"changed {idle * 60:.0f} min ago"
    return None


def newest_file_mtime(p, limit=4000):
    """Newest mtime among tracked-or-not files of the tree that git reports as modified/untracked (cheap edit signal)."""
    best = 0.0
    rows = sync.git(p, "status", "--short", check=False).stdout.splitlines()
    for r in rows[:limit]:
        f = Path(p) / r[3:].strip('"').split(" -> ")[-1]
        try:
            best = max(best, f.stat().st_mtime)
        except OSError:
            pass
    return best


def classify(repo, now=None):
    """-> list of dicts {path, name, branch, action: 'remove'|'keep', why, data}. One per non-primary worktree."""
    now = time.time() if now is None else now
    prim, here = primary(repo), Path(repo).resolve()
    out = []
    for path, branch in sync.worktrees(repo):
        p = Path(path)
        row = dict(path=str(p), name=p.name, branch=branch, action="keep", why="", data=[])
        out.append(row)
        why = protected_reason(p, branch, prim, here, now)
        if why:
            row["why"] = why
            continue
        if not p.exists():
            row["why"] = "folder gone (git worktree prune)"
            continue
        status = [l for l in sync.git(p, "status", "--short", check=False).stdout.splitlines() if l]
        work = [l for l in status if not sync.is_noise(l)]
        if work:
            row["why"] = f"{len(work)} uncommitted file(s)"
            row["report"] = True
            continue
        if time.time() - newest_file_mtime(p) < RECENT_MIN * 60 and status:
            row["why"] = "files changed in the last 30 min"
            continue
        anc = sync.git(repo, "merge-base", "--is-ancestor", branch, f"origin/{sync.TRUNK}", check=False).returncode
        if anc > 1:
            row["why"] = f"HEAD names {branch}, not a branch"
            row["report"] = True
            continue
        if anc == 1:
            n = sync.git(p, "rev-list", "--count", f"origin/{sync.TRUNK}..HEAD", check=False).stdout.strip()
            row["why"] = f"{n} commit(s) not on origin/{sync.TRUNK}"
            row["report"] = True
            continue
        idle = sync.idle_hours(p, branch, now)
        if idle < IDLE_HOURS:
            row["why"] = f"active {idle:.1f} h ago (waits {IDLE_HOURS} h)"
            continue
        row["action"] = "remove"
        row["data"] = sync.ignored_data(p)
        row["noise"] = bool(status)
    return out


def merged_branches(repo, now=None):
    """Local branches fully merged into origin/fast-track that no worktree has checked out and that are not protected/new."""
    now = time.time() if now is None else now
    checked = {b for _, b in sync.worktrees(repo)}
    lanes = {b for p, b in sync.worktrees(repo) if Path(p).name in sync.LANE_WORKTREES}
    names = [l.strip().lstrip("*+ ").strip() for l in
             sync.git(repo, "branch", "--format=%(refname:short)", "--merged", f"origin/{sync.TRUNK}").stdout.splitlines()]
    common = Path(sync.git(repo, "rev-parse", "--git-common-dir").stdout.strip())
    if not common.is_absolute():
        common = Path(repo) / common
    out = []
    for b in names:
        if not b or b in checked or b in lanes or b in PROTECT_BRANCHES:
            continue
        stamp = sync.last_reflog_stamp(common / "logs" / "refs" / "heads" / b)
        if stamp is not None and now - stamp < RECENT_MIN * 60:
            continue
        out.append(b)
    return out


def rescue_data(repo, row):
    dest = primary(repo) / "Dumps" / "wt_rescue" / row["name"]
    for rel in row["data"]:
        src = Path(row["path"]) / rel.strip('"')
        tgt = dest / rel.strip('"').rstrip("/")
        tgt.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, tgt, dirs_exist_ok=True)
        elif src.exists():
            shutil.copy2(src, tgt)
    return dest


def remove_tree(repo, row):
    force = ["--force"] if row.get("noise") else []
    r = sync.git(repo, "worktree", "remove", *force, row["path"], check=False)
    if r.returncode != 0:
        row["action"], row["why"] = "keep", f"remove failed ({r.stderr.strip()[:80]})"
        return False
    sync.git(repo, "branch", "-d", row["branch"], check=False)   # -d, never -D: git refuses an unmerged branch
    return True


def run(repo=REPO, apply=False, now=None, log=print, host=None):
    """-> summary dict. Dry run unless apply."""
    repo = Path(repo)
    sync.git(repo, "fetch", "--quiet", "origin", sync.TRUNK, check=False)
    if apply:
        sync.repair_heads(repo)
    rows = classify(repo, now)
    removed, rescued = [], []
    for r in rows:
        if r["action"] != "remove":
            continue
        if apply:
            if r["data"]:
                rescued.append(str(rescue_data(repo, r)))
            if not remove_tree(repo, r):
                continue
        log(f"{'removed' if apply else 'would remove'}  {r['name']} [{r['branch']}]" + (f"  (data -> Dumps/wt_rescue)" if r["data"] else ""))
        removed.append(r["name"])
    if apply:
        sync.git(repo, "worktree", "prune", check=False)
    branches = merged_branches(repo, now)
    deleted = []
    for b in branches:
        if apply:
            if sync.git(repo, "branch", "-d", b, check=False).returncode != 0:
                continue
        deleted.append(b)
    log(f"{'deleted' if apply else 'would delete'} {len(deleted)} merged local branch(es)")
    held = [r for r in rows if r.get("report")]
    s = dict(device=device_name(host), apply=apply, removed=removed, branches=deleted, held=held,
             kept=sum(1 for r in rows if r["action"] == "keep"), rescued=rescued)
    write_report(repo, s)
    if apply:
        append_log(repo, s)
    log(f"{s['device']}: {'removed' if apply else 'would remove'} {len(removed)} tree(s), {'deleted' if apply else 'would delete'} "
        f"{len(deleted)} branch(es), kept {s['kept']}, {len(held)} hold unshipped work -> Dumps/worktree_report.txt")
    return s


def write_report(repo, s):
    f = primary(repo) / "Dumps" / "worktree_report.txt"
    f.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"worktree report {datetime.now(timezone.utc):%Y-%m-%d %H:%MZ} device={s['device']} mode={'apply' if s['apply'] else 'dry-run'}",
             f"trees holding work not on origin/{sync.TRUNK} (reported, never deleted): {len(s['held'])}"]
    lines += [f"  {r['name']} [{r['branch']}]: {r['why']}  {r['path']}" for r in s["held"]]
    f.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return f


def append_log(repo, s):
    f = primary(repo) / SUPERVISOR_LOG_REL
    if not f.parent.exists():
        return
    line = (f"- {datetime.now(timezone.utc):%Y-%m-%d %H:%MZ} | from: wt_maint.py ({s['device']}) | WORKTREE MAINT: removed {len(s['removed'])} tree(s), "
            f"deleted {len(s['branches'])} merged branch(es), {len(s['held'])} hold unshipped work (Dumps/worktree_report.txt)\n")
    with open(f, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(line)


# ---- scheduled task ---------------------------------------------------------------------------------------------------------

def ps(script):
    return subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True)


def install_script(repo, device, at="07:15"):
    """PowerShell that registers the task. conhost --headless shows no window (pythonw alone still flashes git children)."""
    py = sys.executable
    return (
        f"$ErrorActionPreference='Stop'; $conhost=Join-Path $env:SystemRoot 'System32\\conhost.exe'; "
        f"$a=New-ScheduledTaskAction -Execute $conhost -Argument '--headless \"{py}\" \"{repo}\\scripts\\dev\\wt_maint.py\" --apply' -WorkingDirectory '{repo}'; "
        f"$t=New-ScheduledTaskTrigger -Daily -At '{at}'; "
        f"$s=New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew "
        f"-ExecutionTimeLimit (New-TimeSpan -Hours 1); "
        f"Register-ScheduledTask -TaskName '{task_name(device)}' -Action $a -Trigger $t -Settings $s -Force | Out-Null; "
        f"Write-Output 'registered {task_name(device)}'")


def cmd_install(repo=REPO, at="07:15"):
    prim = primary(repo)   # the primary checkout: a worktree folder may be retired by this very job
    if (prim / "scripts" / "dev" / "wt_maint.py").exists():
        repo = prim
    else:
        print(f"WARNING: {prim} has no wt_maint.py yet; task points at {repo}. Pull the primary tree, then re-run `install`.")
    r = ps(install_script(repo, device_name(), at))
    print((r.stdout + r.stderr).strip())
    return r.returncode


def cmd_status(repo=REPO):
    d = device_name()
    print(f"device: {d} (hostname {socket.gethostname()})  task: {task_name(d)}")
    r = ps(f"$t=Get-ScheduledTask -TaskName '{task_name(d)}' -ErrorAction SilentlyContinue; if(-not $t){{'NOT INSTALLED'}}else{{"
           f"$i=Get-ScheduledTaskInfo -TaskName '{task_name(d)}'; 'state {{0}}, next {{1}}, last {{2}}, last result {{3}}' -f $t.State,$i.NextRunTime,$i.LastRunTime,$i.LastTaskResult; "
           f"($t.Actions | % {{ $_.Execute + ' ' + $_.Arguments }})}}")
    print((r.stdout + r.stderr).strip())
    rep = primary(repo) / "Dumps" / "worktree_report.txt"
    print("last report: " + (rep.read_text(encoding="utf-8").splitlines()[0] if rep.exists() else "none yet"))
    return 0 if "NOT INSTALLED" not in r.stdout else 1


def cmd_uninstall():
    r = ps(f"Unregister-ScheduledTask -TaskName '{task_name()}' -Confirm:$false -ErrorAction Stop; Write-Output 'unregistered {task_name()}'")
    print((r.stdout + r.stderr).strip())
    return r.returncode


def main(argv):
    if os.name != "nt" and argv and argv[0] in ("install", "status", "uninstall"):
        print("scheduled-task commands are Windows only")
        return 2
    if argv and argv[0] == "install":
        return cmd_install(at=argv[argv.index("--at") + 1] if "--at" in argv else "07:15")
    if argv and argv[0] == "status":
        return cmd_status()
    if argv and argv[0] == "uninstall":
        return cmd_uninstall()
    apply = "--apply" in argv and "--dry-run" not in argv
    try:
        run(REPO, apply=apply)
    except sync.SyncError as e:
        print(f"wt_maint: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
