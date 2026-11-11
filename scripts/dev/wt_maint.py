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
A tree with uncommitted files whose branch is fully on origin/fast-track and that has been idle DIRTY_IDLE_HOURS is patch-saved
(Dumps/wt_rescue/<tree>/uncommitted.patch + untracked/) and then removed. `--no-log` skips the SUPERVISOR_LOG line (the guard uses it).
A clean tree with commits not on origin/fast-track, idle PARK_IDLE_HOURS, is PARKED: branch pushed to origin and kept locally, folder
removed (restore: git worktree add ../<name> <branch>). A "trunk copy" (HEAD unresolvable, index = one trunk commit: a hand-made tree
whose case-mismatched branch was deleted) counts as clean and on trunk; only its non-"A " rows are work.
Never touched: the primary tree, the tree we run in, the live tree (.mts_live), lane trees, Codex trees, any tree changed in the
last 30 minutes, any tree with unshipped commits AND uncommitted files, or with uncommitted files that are recent, conflicted or too big to save. Never stash / reset / force-push. Idempotent.
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
import hosts  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
from cicd_run import SUPERVISOR_LOG_REL  # noqa: E402  (one owner of the path)
RECENT_MIN = 30
GATEWAY_IDLE_HOURS = 12    # DECISION (OURS): a .gateway_owner tree is the gateway session's own only while it is in use; with the machine flag
                           # ~/.claude/mts_gateway_on every tree gets the marker (66 trees, ~4 GB, kept C: at 6 GB free 2026-10-28). Idle this long
                           # it is an ordinary finished tree: the clean / merged / no-unshipped-commits checks below still decide.
IDLE_HOURS = sync.TIDY_IDLE_HOURS
DIRTY_IDLE_HOURS = 24      # DECISION (OURS, operator 2026-10-26 "same mechanism on all devices, periodically"): a tree whose branch is fully on trunk
                           # but holds uncommitted files is patch-saved and removed only after this many idle hours; unshipped commits never
BIG_UNTRACKED_MB = 50      # an untracked file this large is not copied into the rescue: the tree stays
PARK_IDLE_HOURS = 72       # DECISION (OURS, operator 2026-11-01 "ship, clean work trees - every machine"): a clean tree whose commits are not
                           # on trunk and that nobody touched for this long is PARKED: its branch is pushed to origin and kept locally, only the
                           # folder goes (restore: git worktree add ../<name> <branch>). No commit is ever lost; 8 such trees held ~1.5 GB each.
TRUNK_TREE_DEPTH = 6000    # trunk commits whose tree hash identifies a "trunk copy" (a hand-made tree whose branch vanished, see classify)
# Ignored caches inside an ignored dir that rescue_data must not copy: rebuilt for free. sim_desk/cache/bars (~0.17 GB per tree,
# `desk.py --build`) filled Dumps/wt_rescue with 6.4 GB on JIS-NB by 2026-11-01; cache/results (TRIALS counting) is still rescued.
RESCUE_SKIP = ("MyTradingSys/research/sim_desk/cache/bars",
               "MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/.gapfreq_cache")
PROTECT_BRANCHES = ("fast-track", "main", "master")
TASK_PREFIX = "MTS-WorktreeMaint"
# hostname (lower) -> canonical device name; the Lenovo laptop reports DESKTOP-F7IU69N (DEVICES.md s0)
KNOWN_DEVICES = {"jis-desktop": "JIS-NB", "jis-nuc": "JIS-NUC", "jis-laptop": "Lenovo laptop"}   # keyed by hosts.key(): old and new names both land here; device names (task names) stay


def device_name(hostname=None):
    """Canonical device name from the machine's hostname; an unknown host keeps its own (upper-cased) name."""
    h = (hostname or socket.gethostname()).strip()
    return KNOWN_DEVICES.get(str(hosts.key(h)), h.upper() or "UNKNOWN")


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
    if (p / sync.GATEWAY_MARKER).exists():
        g_idle = sync.idle_hours(p, branch, now) if mtime_of is None else mtime_of(p)
        if g_idle < GATEWAY_IDLE_HOURS:
            return "gateway tree"   # GATEWAY_NUC.md rule 7, while in use
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


def dirty_removable(repo, p, branch, work, now, on_trunk=False):
    """True when a tree with uncommitted files may be patch-saved and removed: branch fully on origin/<trunk> (or `on_trunk`: a trunk
    copy, see classify), no merge conflict, tree and every dirty file idle DIRTY_IDLE_HOURS, no untracked file over BIG_UNTRACKED_MB."""
    if any(l[:2] in ("UU", "AA", "DD", "AU", "UA", "DU", "UD") for l in work):
        return False
    if not on_trunk and sync.git(repo, "merge-base", "--is-ancestor", branch, f"origin/{sync.TRUNK}", check=False).returncode != 0:
        return False
    if sync.idle_hours(p, branch, now) < DIRTY_IDLE_HOURS or now - newest_file_mtime(p) < DIRTY_IDLE_HOURS * 3600:
        return False
    for f in untracked_files(p):
        try:
            if (Path(p) / f).stat().st_size > BIG_UNTRACKED_MB * 1e6:
                return False
        except OSError:
            pass
    return True


def untracked_files(p):
    return [l for l in sync.git(p, "ls-files", "--others", "--exclude-standard", check=False).stdout.splitlines() if l]


def rescue_patch(repo, row):
    """Save what the tree holds uncommitted before it is removed: uncommitted.patch (tracked changes, binary-safe), the untracked
    files under their own paths, STATUS.txt. -> destination dir, or None when the patch could not be written (the tree stays)."""
    p = Path(row["path"])
    dest = primary(repo) / "Dumps" / "wt_rescue" / row["name"]
    try:
        dest.mkdir(parents=True, exist_ok=True)
        # a trunk copy has no HEAD: its index IS the trunk commit, so index-vs-worktree holds exactly the real edits
        diff = subprocess.run(["git", "-C", str(p), "--no-optional-locks", "diff", "--binary"] + ([] if row.get("copy") else ["HEAD"]),
                              capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if diff.returncode != 0:
            return None
        (dest / "uncommitted.patch").write_bytes(diff.stdout)
        head = f"{row['name']} [{row['branch']}] {datetime.now(timezone.utc):%Y-%m-%d %H:%MZ}"
        (dest / "STATUS.txt").write_text(head + chr(10) + sync.git(p, "status", "--short", check=False).stdout,
                                         encoding="utf-8", newline=chr(10))
        for f in untracked_files(p):
            src = p / f
            tgt = dest / "untracked" / f
            tgt.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, tgt, dirs_exist_ok=True)
            elif src.exists():
                shutil.copy2(src, tgt)
        return dest
    except OSError:
        return None


def trunk_trees(repo):
    """Tree hashes of the last TRUNK_TREE_DEPTH origin/<trunk> commits."""
    out = sync.git(repo, "log", f"origin/{sync.TRUNK}", f"-{TRUNK_TREE_DEPTH}", "--format=%T", check=False).stdout
    return set(out.split())


def is_trunk_copy(repo, p, trees):
    """True for a tree whose HEAD does not resolve while its index is exactly one trunk commit's tree: a hand-made
    `git worktree add -b jis-nb/x` whose ref landed under an existing JIS-NB/ dir (case-insensitive FS) and was later deleted as
    an unchecked-out merged branch. git then shows every file as staged-new ("A "), 7,000+ "uncommitted files" that are trunk
    content (5 trees, ~7 GB on JIS-NB, 2026-11-01). Only the rows that are not "A " can be real work."""
    if sync.git(p, "rev-parse", "-q", "--verify", "HEAD", check=False).returncode == 0:
        return False
    return sync.git(p, "write-tree", check=False).stdout.strip() in trees


def classify(repo, now=None):
    """-> list of dicts {path, name, branch, action: 'remove'|'park'|'keep', why, data}. One per non-primary worktree."""
    now = time.time() if now is None else now
    prim, here = primary(repo), Path(repo).resolve()
    trees = None
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
        copy = False
        if any(l.startswith("A") for l in status):     # "A " / "AM": staged-new rows, the trunk-copy signature (cheap pre-check)
            trees = trunk_trees(repo) if trees is None else trees
            copy = is_trunk_copy(repo, p, trees)
            if copy:
                row["copy"] = True
                status = [l for l in status if not l.startswith("A ")]
        work = [l for l in status if not sync.is_noise(l)]
        if work:
            row["why"] = f"{len(work)} uncommitted file(s)" + (" in a trunk copy (branch gone)" if copy else "")
            row["report"] = True
            if dirty_removable(repo, p, branch, work, now, on_trunk=copy):
                row["action"], row["save_patch"], row["report"] = "remove", True, False
                row["why"] = f"{len(work)} uncommitted file(s), branch on origin/{sync.TRUNK}, idle {DIRTY_IDLE_HOURS} h+: patch saved first"
                row["data"] = sync.ignored_data(p)
            continue
        if time.time() - newest_file_mtime(p) < RECENT_MIN * 60 and status:
            row["why"] = "files changed in the last 30 min"
            continue
        anc = 0 if copy else sync.git(repo, "merge-base", "--is-ancestor", branch, f"origin/{sync.TRUNK}", check=False).returncode
        if anc > 1:
            row["why"] = f"HEAD names {branch}, not a branch"
            row["report"] = True
            continue
        idle = sync.idle_hours(p, branch, now)
        if anc == 1:
            n = sync.git(p, "rev-list", "--count", f"origin/{sync.TRUNK}..HEAD", check=False).stdout.strip()
            row["why"] = f"{n} commit(s) not on origin/{sync.TRUNK}"
            row["report"] = True
            if idle >= PARK_IDLE_HOURS:
                row["action"], row["report"] = "park", False
                row["why"] = f"{n} commit(s) not on origin/{sync.TRUNK}, idle {PARK_IDLE_HOURS} h+: branch pushed to origin and kept, folder removed"
                row["data"] = sync.ignored_data(p)
                row["noise"] = bool(status)
            continue
        if idle < IDLE_HOURS:
            row["why"] = f"active {idle:.1f} h ago (waits {IDLE_HOURS} h)"
            continue
        row["action"] = "remove"
        row["data"] = sync.ignored_data(p)
        row["noise"] = bool(status) or copy      # git counts a trunk copy's staged files as dirt: --force removes them, nothing is lost
    return out


def merged_branches(repo, now=None):
    """Local branches fully merged into origin/fast-track that no worktree has checked out and that are not protected/new.
    Checked-out is compared ignoring case: a worktree HEAD naming `jis-nb/x` holds the ref file `JIS-NB/x` on Windows, and
    `git branch -d jis-nb/x` happily deleted it (the trunk copies above)."""
    now = time.time() if now is None else now
    checked = {b.lower() for _, b in sync.worktrees(repo)}
    lanes = {b.lower() for p, b in sync.worktrees(repo) if Path(p).name in sync.LANE_WORKTREES}
    names = [l.strip().lstrip("*+ ").strip() for l in
             sync.git(repo, "branch", "--format=%(refname:short)", "--merged", f"origin/{sync.TRUNK}").stdout.splitlines()]
    common = Path(sync.git(repo, "rev-parse", "--git-common-dir").stdout.strip())
    if not common.is_absolute():
        common = Path(repo) / common
    out = []
    for b in names:
        if not b or b.lower() in checked or b.lower() in lanes or b in PROTECT_BRANCHES:
            continue
        stamp = sync.last_reflog_stamp(common / "logs" / "refs" / "heads" / b)
        if stamp is not None and now - stamp < RECENT_MIN * 60:
            continue
        out.append(b)
    return out


def rescue_data(repo, row):
    dest = primary(repo) / "Dumps" / "wt_rescue" / row["name"]
    root = Path(row["path"])
    skip = {os.path.normcase(str(root / s)) for s in RESCUE_SKIP}

    def regenerable(d, names):
        return [n for n in names if os.path.normcase(os.path.join(d, n)) in skip]
    for rel in row["data"]:
        src = root / rel.strip('"')
        if os.path.normcase(str(src).rstrip("\\/")) in skip:
            continue
        tgt = dest / rel.strip('"').rstrip("/")
        tgt.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, tgt, dirs_exist_ok=True, ignore=regenerable)
        elif src.exists():
            shutil.copy2(src, tgt)
    return dest


def remove_tree(repo, row):
    force = ["--force"] if row.get("noise") or row.get("save_patch") else []
    r = sync.git(repo, "worktree", "remove", *force, row["path"], check=False)
    if r.returncode != 0:
        row["action"], row["why"] = "keep", f"remove failed ({r.stderr.strip()[:80]})"
        return False
    if row["action"] != "park":
        sync.git(repo, "branch", "-d", row["branch"], check=False)   # -d, never -D: git refuses an unmerged branch
    return True


def park_tree(repo, row):
    """Push the tree's branch to origin (same bytes `sync.py ship` would push), then remove the folder; the local branch stays.
    The push failing keeps the tree: a folder goes only once its commits exist in two places."""
    r = sync.git(repo, "push", "-q", "origin", f"{row['branch']}:{row['branch']}", check=False)
    if r.returncode != 0:
        row["action"], row["why"], row["report"] = "keep", f"park: push failed ({r.stderr.strip()[:80]})", True
        return False
    return remove_tree(repo, row)


def run(repo=REPO, apply=False, now=None, log=print, host=None, write_log=True):
    """-> summary dict. Dry run unless apply."""
    repo = Path(repo)
    sync.git(repo, "fetch", "--quiet", "origin", sync.TRUNK, check=False)
    if apply:
        sync.repair_heads(repo)
    rows = classify(repo, now)
    removed, rescued, parked = [], [], []
    for r in rows:
        if r["action"] == "park":
            if apply:
                if r["data"]:
                    rescued.append(str(rescue_data(repo, r)))
                if not park_tree(repo, r):
                    log(f"kept  {r['name']}: {r['why']}")
                    continue
            log(f"{'parked' if apply else 'would park'}  {r['name']} [{r['branch']}]: {r['why']}; restore: git worktree add ../{r['name']} {r['branch']}")
            parked.append(r["name"])
            continue
        if r["action"] != "remove":
            continue
        if apply:
            if r.get("save_patch"):
                saved = rescue_patch(repo, r)
                if saved is None:
                    log(f"kept  {r['name']}: could not save its uncommitted files")
                    continue
                rescued.append(str(saved))
            if r["data"]:
                rescued.append(str(rescue_data(repo, r)))
            if not remove_tree(repo, r):
                continue
        log(f"{'removed' if apply else 'would remove'}  {r['name']} [{r['branch']}]"
            + (f": uncommitted files saved to Dumps/wt_rescue/{r['name']}" if r.get("save_patch") else "")
            + (f"  (data -> Dumps/wt_rescue)" if r["data"] else ""))
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
    s = dict(device=device_name(host), apply=apply, removed=removed, branches=deleted, held=held, parked=parked,
             parked_rows=[r for r in rows if r["name"] in parked],
             kept=sum(1 for r in rows if r["action"] == "keep"), rescued=rescued)
    write_report(repo, s)
    if apply and write_log:
        append_log(repo, s)
    log(f"{s['device']}: {'removed' if apply else 'would remove'} {len(removed)} tree(s), {'parked' if apply else 'would park'} {len(parked)}, "
        f"{'deleted' if apply else 'would delete'} {len(deleted)} branch(es), kept {s['kept']}, {len(held)} hold unshipped work -> Dumps/worktree_report.txt")
    return s


def write_report(repo, s):
    f = primary(repo) / "Dumps" / "worktree_report.txt"
    f.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"worktree report {datetime.now(timezone.utc):%Y-%m-%d %H:%MZ} device={s['device']} mode={'apply' if s['apply'] else 'dry-run'}",
             f"trees holding work not on origin/{sync.TRUNK} (reported, never deleted): {len(s['held'])}"]
    lines += [f"  {r['name']} [{r['branch']}]: {r['why']}  {r['path']}" for r in s["held"]]
    if s.get("parked_rows"):
        lines.append(f"parked (folder removed, branch kept locally and on origin; restore: git worktree add ../<name> <branch>): {len(s['parked_rows'])}")
        lines += [f"  {r['name']} [{r['branch']}]: {r['why']}" for r in s["parked_rows"]]
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
    return subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


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
    repo = Path(argv[argv.index("--repo") + 1]) if "--repo" in argv else REPO   # another clone's trees, e.g. the Run-value checkout is not the one holding the worktrees
    try:
        run(repo, apply=apply, write_log="--no-log" not in argv)
    except sync.SyncError as e:
        print(f"wt_maint: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
