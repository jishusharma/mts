"""Manual helper for deploying the commit that UNTRACKS the live-host generated files (card move-live-host-generated-files-status-md).

Why: `git rm --cached` + commit deletes those files from the working tree of every tree that fast-forwards to it. In the live tree that
would delete runtime/oi_live/*.csv and research/htf_context/* (inputs the live runner and check_live_health READ), BUILD_REPORT.md,
AUDIT_DIGEST.md, T0_CHECKS.md. A modified (dirty) tracked file also makes `git merge --ff-only` refuse. So, in order:

  python scripts/dev/deploy_untrack_backup.py backup  <root>          copy the files to runtime_data/deploy_backup/<stamp>/untrack/ + MANIFEST.json (sha256)
  python scripts/dev/deploy_untrack_backup.py reset   <root> <stamp>  `git checkout --` the still-tracked, dirty ones (only after the backup verified)
  git -C <root> merge --ff-only <target>                              (the files disappear here: documented hazard)
  python scripts/dev/deploy_untrack_backup.py restore <root> <stamp>  put back every file the merge removed; sha256 against the manifest
  git -C <root> status --porcelain                                    must be empty (the files are ignored now)

Exit 0 = ok, 1 = a verification failed (the message says which file). STATUS.md is NOT in the groups: it stays tracked.
A file that exists again at restore time (a recorder re-created it) is never overwritten: it is reported as KEPT-NEWER with both shas and the exit code is 1 (merge it by hand from the backup).
The builder never runs this; the coordinator does, by hand (AutoDeploy is retired)."""
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Globs relative to the tree root; exactly the generated files the card untracks (oi_recorder.py / htf_context_live.py are code and stay).
GROUPS = (
    "MyTradingSys/research/audits/AUDIT_DIGEST.md",
    "MyTradingSys/research/audits/T0_CHECKS.md",
    "MyTradingSys/runtime/BUILD_REPORT.md",
    "MyTradingSys/runtime/oi_live/*.csv",
    "MyTradingSys/research/htf_context/*.jsonl",
    "MyTradingSys/research/htf_context/*_summary.json",
)
BACKUP_ROOT = "runtime_data/deploy_backup"
SUB = "untrack"
MANIFEST = "MANIFEST.json"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def collect(root):
    root = Path(root)
    found = set()
    for pattern in GROUPS:
        for p in root.glob(pattern):
            if p.is_file():
                found.add(p.relative_to(root).as_posix())
    return sorted(found)


def git(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def backup_dir(root, stamp):
    return Path(root) / BACKUP_ROOT / stamp / SUB


def backup(root, stamp=None):
    """Copy every generated file to the backup dir and verify each copy. Returns (stamp, manifest). Raises RuntimeError on a bad copy."""
    root = Path(root)
    stamp = stamp or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = backup_dir(root, stamp)
    if dest.exists():
        raise RuntimeError(f"{dest} already exists; refusing to overwrite a backup")
    dest.mkdir(parents=True)
    manifest = {}
    for rel in collect(root):
        src = root / rel
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        # a recorder may append during the copy: the copy is what gets restored, so the manifest records the copy's hash
        manifest[rel] = {"sha256": sha256(target), "size": target.stat().st_size}
    (dest / MANIFEST).write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return stamp, manifest


def load_manifest(root, stamp):
    p = backup_dir(root, stamp) / MANIFEST
    if not p.is_file():
        raise RuntimeError(f"no backup manifest at {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def verify_backup(root, stamp):
    """Every manifest entry has its file in the backup dir with the recorded sha. Returns a list of problems."""
    dest = backup_dir(root, stamp)
    bad = []
    for rel, meta in load_manifest(root, stamp).items():
        f = dest / rel
        if not f.is_file():
            bad.append(f"{rel}: missing from backup")
        elif sha256(f) != meta["sha256"]:
            bad.append(f"{rel}: backup sha differs from manifest")
    return bad


def refresh_entry(root, stamp, rel):
    """Re-copy one live file into the backup and update its manifest hash (narrows the backup-to-reset window to one file copy)."""
    root = Path(root)
    target = backup_dir(root, stamp) / rel
    live = (root / rel).read_bytes()
    if not live.startswith(target.read_bytes()):
        n = 1               # live is not the backup plus appended rows (rewritten, or reset once already): keep both, never replace a fuller backup
        while target.with_name(f"{target.name}.pre-reset-{n}").exists():
            n += 1
        shutil.copy2(root / rel, target.with_name(f"{target.name}.pre-reset-{n}"))
        return False
    shutil.copy2(root / rel, target)
    mp = backup_dir(root, stamp) / MANIFEST
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    manifest[rel] = {"sha256": sha256(target), "size": target.stat().st_size}
    mp.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def reset_dirty_tracked(root, stamp):
    """`git checkout --` the generated files that are still tracked and dirty, so the fast-forward can delete them cleanly.
    Refuses unless the backup verifies. Returns the reset paths."""
    problems = verify_backup(root, stamp)
    if problems:
        raise RuntimeError("backup does not verify, nothing reset: " + "; ".join(problems))
    reset = []
    for rel in collect(root):
        rc, out, _ = git(root, "ls-files", "--", rel)
        if rc != 0 or not out.strip():
            continue                                  # untracked or ignored: the merge does not touch it
        rc, out, _ = git(root, "status", "--porcelain", "--", rel)
        if out.strip():
            refresh_entry(root, stamp, rel)           # rows a recorder appended since `backup` go into the backup right before the checkout
            rc, _, err = git(root, "checkout", "--", rel)
            if rc != 0:
                raise RuntimeError(f"git checkout -- {rel} failed: {err.strip()}")
            reset.append(rel)
    return reset


def restore(root, stamp):
    """Put back every manifest file that is now missing, then verify. Returns (restored, kept_newer, problems)."""
    root = Path(root)
    dest = backup_dir(root, stamp)
    manifest = load_manifest(root, stamp)
    restored, kept, problems = [], [], []
    for rel, meta in sorted(manifest.items()):
        src, live = dest / rel, root / rel
        if not src.is_file() or sha256(src) != meta["sha256"]:
            problems.append(f"{rel}: backup copy missing or changed, cannot restore")
            continue
        if live.exists():
            now = sha256(live)
            if now != meta["sha256"]:
                kept.append(f"{rel}: KEPT-NEWER (live {now[:12]} vs backup {meta['sha256'][:12]})")
            continue
        live.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, live)
        if sha256(live) != meta["sha256"]:
            problems.append(f"{rel}: restored copy sha differs from backup")
        else:
            restored.append(rel)
    return restored, kept, problems


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) < 2 or a[0] not in ("backup", "reset", "restore") or (a[0] != "backup" and len(a) < 3):
        print(__doc__)
        return 1
    cmd, root = a[0], a[1]
    try:
        if cmd == "backup":
            stamp, manifest = backup(root)
            bad = verify_backup(root, stamp)
            print(f"backup {stamp}: {len(manifest)} file(s) under {BACKUP_ROOT}/{stamp}/{SUB}/")
            for p in bad:
                print("PROBLEM", p)
            return 1 if bad else 0
        if cmd == "reset":
            reset = reset_dirty_tracked(root, a[2])
            print(f"reset {len(reset)} dirty tracked file(s): {', '.join(reset) or '-'}")
            return 0
        restored, kept, problems = restore(root, a[2])
        print(f"restored {len(restored)} file(s): {', '.join(restored) or '-'}")
        for k in kept:
            print("PROBLEM", k, f"- the backup copy is {BACKUP_ROOT}/{a[2]}/{SUB}/<same path>; merge by hand, nothing was overwritten")
        for p in problems:
            print("PROBLEM", p)
        return 1 if (problems or kept) else 0
    except RuntimeError as e:
        print("PROBLEM", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
