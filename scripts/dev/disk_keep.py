r"""disk_keep.py - keep every drive of this host above its floor (operator 2026-11-14: "make sure F does not get into the same issues like C").

Plan: MyTradingSys/system/disk_plan.json (per host: drives + floor GB, overflow folders, protected paths). A host with no KNOWN row prints
`DISK UNKNOWN` and the command that fills it in. Commands:
  status            DISK line per drive (free GB vs floor), DISK ACT line when a floor is breached
  facts             this host's drives as JSON (paste into disk_plan.json as the row; what a broadcast --cmd runs)
  speed [DRIVE]     one write+read timing of the overflow drive (MB/s); cold data goes there whatever the answer, hot data never
  move [--apply] [--hours N] [--max N]   coldest idle study trees (and cold cache files) to the overflow drive:
                    copy -> verify file count + bytes -> git worktree repair -> remove source. Dry-run by default.
Never moved: the primary checkout, .mts_live, lane trees, gateway trees, a tree with a live process naming it, a dirty tree, a tree
with an open claim, anything under a `protect` path (CBP store). A source is removed only after its copy verified. Stdlib only.
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hosts  # noqa: E402

PLAN_FILE = HERE.parents[1] / "MyTradingSys" / "system" / "disk_plan.json"
GB = 1024 ** 3


def load_plan(path=None):
    try:
        return json.loads(Path(path or PLAN_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"hosts": {}}


def host_row(plan, host=None):
    host = hosts.canonical(host or hosts.this_host())
    return host, (plan.get("hosts") or {}).get(host)


def free_gb(drive):
    try:
        return shutil.disk_usage(drive).free / GB
    except OSError:
        return None


def status_lines(plan=None, host=None):
    """DISK lines for this host. Never raises."""
    plan = plan if plan is not None else load_plan()
    host, row = host_row(plan, host)
    if not row or row.get("status") != "KNOWN":
        cmd = (row or {}).get("fact_cmd") or "python scripts/dev/disk_keep.py facts"
        return [f"DISK UNKNOWN host={host}: no data plan yet; run `{cmd}` here and paste its JSON as the row in MyTradingSys/system/disk_plan.json"]
    out = []
    for d, v in (row.get("drives") or {}).items():
        floor, free = float(v.get("floor_gb", 0)), free_gb(d)
        if free is None:
            out.append(f"DISK {d} host={host} not present")
        elif floor and free < floor:
            ov = (row.get("overflow") or {}).get("wt") or "overflow"
            out.append(f"DISK {d} host={host} free {free:.1f} GB < floor {floor:g} GB LOW")
            out.append(f"DISK ACT {d}: run `python scripts/dev/disk_keep.py move --apply` (cold trees/data to {ov}); "
                       f"if it frees too little, ship and `sync.py tidy --apply` the unshipped study trees")
        else:
            out.append(f"DISK {d} host={host} free {free:.1f} GB" + (f" >= floor {floor:g} GB ok" if floor else " (overflow, no floor)"))
    return out


def facts(host=None):
    out = {"host": hosts.canonical(host or hosts.this_host()), "status": "KNOWN", "drives": {}}
    for letter in "CDEFGHIJ":
        d = letter + ":\\"
        try:
            u = shutil.disk_usage(d)
        except OSError:
            continue
        out["drives"][d] = {"floor_gb": 20 if letter in "CF" else 0, "total_gb": round(u.total / GB), "free_gb": round(u.free / GB, 1),
                            "holds": "FILL IN"}
    out["overflow"] = {"wt": "FILL IN", "data": "FILL IN"}
    return out


def speed(drive, mb=64):
    """(write MB/s, read MB/s) of one `mb` MB file on drive; the file is removed. Read may come from the page cache: an upper bound."""
    d = Path(drive) / "MTS" / "_speedtest"
    d.mkdir(parents=True, exist_ok=True)
    f = d / "s.bin"
    blob = os.urandom(1024 * 1024)
    try:
        t = time.time()
        with open(f, "wb") as h:
            for _ in range(mb):
                h.write(blob)
            h.flush()
            os.fsync(h.fileno())
        w = mb / max(time.time() - t, 1e-6)
        t = time.time()
        with open(f, "rb") as h:
            while h.read(1024 * 1024):
                pass
        return w, mb / max(time.time() - t, 1e-6)
    finally:
        try:
            f.unlink()
            d.rmdir()
        except OSError:
            pass


def tree_size(p):
    n = b = 0
    for root, _, files in os.walk(p):
        for f in files:
            try:
                b += os.lstat(os.path.join(root, f)).st_size
                n += 1
            except OSError:
                pass
    return n, b


def live_process_naming(path, snapshot=None):
    """True when any process command line names `path` (either slash, any case). An unreadable snapshot counts as busy."""
    try:
        if snapshot is None:
            import host_health as hh
            snapshot = hh.snapshot()
    except Exception:    # noqa: BLE001
        return True
    needle = os.path.normcase(str(path)).replace("/", "\\")
    return any(needle in os.path.normcase(r.get("cmd", "")).replace("/", "\\") for r in snapshot if r.get("pid") != os.getpid())


def open_claim_slugs(repo):
    """Slugs of open claims; fails closed ([""] = every tree counts as claimed) when the list cannot be read."""
    import sync
    try:
        return [c for c, _ in sync.open_claims(repo, fetch=False)]
    except Exception:    # noqa: BLE001
        return [""]


def claimed(p, branch, slugs):
    names = {branch.rsplit("/", 1)[-1].lower(), Path(p).name.lower()}
    return any(c == "" or any(n == c or n.endswith("-" + c) or (len(c) >= 8 and (n.startswith(c) or c.startswith(n))) for n in names)
               for c in slugs)


def cold_trees(row, hours, repo, now=None, snapshot=None, claims=None):
    """([(path, branch, idle_h)] movable, coldest first; [(path, why)] kept)."""
    import sync
    now = time.time() if now is None else now
    rows = sync.worktrees(repo)
    prim = Path(rows[0][0]).resolve()
    protect = [os.path.normcase(str(Path(x))) for x in row.get("protect", [])]
    ov = os.path.normcase(str((row.get("overflow") or {}).get("wt") or "\x00"))
    ok, keep = [], []
    slugs = open_claim_slugs(repo) if claims is None else claims
    for path, branch in rows[1:]:
        p = Path(path).resolve()
        n = os.path.normcase(str(p))
        if p == prim or not p.exists() or n.startswith(ov):
            continue
        why = None
        if (p / sync.GATEWAY_MARKER).exists():
            why = "gateway-marked (GATEWAY_NUC.md rule 7; `sync.py release` its task to free it)"
        elif (p / sync.LIVE_MARKER).exists() or p.name in sync.LANE_WORKTREES or sync.is_app_tree(p):
            why = "lane/live tree"
        elif any(n.startswith(x) for x in protect):
            why = "protected path"
        elif branch == "(detached)":
            why = "detached"
        elif any(l for l in sync.git(p, "status", "--short", check=False).stdout.splitlines() if l and not sync.tidy_noise(l)):
            why = "uncommitted files"
        elif claimed(p, branch, slugs):
            why = "open claim"
        elif live_process_naming(p, snapshot):
            why = "live process names it"
        else:
            idle = sync.idle_hours(p, branch, now)
            if idle >= hours:
                ok.append((str(p), branch, idle))
                continue
            why = f"active {idle:.1f} h ago"
        keep.append((str(p), why))
    ok.sort(key=lambda r: -r[2])
    return ok, keep


def move_tree(repo, src, dest_root):
    """copy -> verify count+bytes -> git worktree repair -> check git sees it -> remove source. (ok, message); source kept on any failure."""
    import sync
    src, dest_root = Path(src), Path(dest_root)
    dest = dest_root / src.name
    if dest.exists():
        return False, f"{dest} already exists"
    dest_root.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(src, dest, symlinks=True)
    except (OSError, shutil.Error) as e:
        shutil.rmtree(dest, ignore_errors=True)
        return False, f"copy failed ({str(e)[:80]}); source kept"
    if tree_size(src) != tree_size(dest):
        shutil.rmtree(dest, ignore_errors=True)
        return False, "verify failed (file count/bytes differ); source kept"
    r = sync.git(repo, "worktree", "repair", str(dest), check=False)
    seen = {os.path.normcase(str(Path(p).resolve())) for p, _ in sync.worktrees(repo)}
    if os.path.normcase(str(dest.resolve())) not in seen:
        shutil.rmtree(dest, ignore_errors=True)
        sync.git(repo, "worktree", "repair", str(src), check=False)
        return False, f"git worktree repair did not register the copy ({r.stderr.strip()[:60]}); source kept"
    try:
        shutil.rmtree(src)
    except OSError as e:
        return True, f"moved to {dest}; source folder not fully removed ({str(e)[:60]}), retry later"
    sync.git(repo, "worktree", "prune", check=False)
    return True, f"moved to {dest}"


def cold_cache_files(row, now=None):
    import data_cache
    hrs = float((row.get("cold_after_hours") or {}).get("data", 168))
    now = time.time() if now is None else now
    out = []
    for f in data_cache.cache_dir().rglob("*"):
        try:
            if f.is_file() and not f.name.endswith(".tmp") and (now - f.stat().st_mtime) / 3600 >= hrs:
                out.append(f)
        except OSError:
            pass
    return out


def move_cache(row, files, apply):
    """Copy cold cache files to the overflow data folder, remove the source once the size matches. data_cache.cached() reads them from
    the cold folder (cold_dir), so a moved file is still a hit."""
    import data_cache
    base, dest_root, n = data_cache.cache_dir(), Path((row.get("overflow") or {}).get("data") or ""), 0
    for f in files:
        tgt = dest_root / f.relative_to(base)
        if not apply:
            n += 1
            continue
        try:
            tgt.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, tgt)
            if tgt.stat().st_size == f.stat().st_size:
                f.unlink()
                n += 1
        except OSError:
            pass
    return n


def main(argv):
    cmd = argv[0] if argv else "status"
    plan = load_plan()
    if cmd == "status":
        print("\n".join(status_lines(plan)))
        return 0
    if cmd == "facts":
        print(json.dumps(facts(), indent=1))
        return 0
    host, row = host_row(plan)
    if cmd == "speed":
        d = argv[1] if len(argv) > 1 else (Path((row or {}).get("overflow", {}).get("wt") or "D:\\").anchor or "D:\\")
        w, r = speed(d)
        print(f"SPEED {d} write {w:.0f} MB/s read {r:.0f} MB/s ({'fast disk' if w > 150 else 'slow disk: cold data only'})")
        return 0
    if cmd == "move":
        if not row or row.get("status") != "KNOWN" or not (row.get("overflow") or {}).get("wt"):
            print("move: no KNOWN data plan with an overflow folder for this host (disk_plan.json)")
            return 1
        apply = "--apply" in argv
        hours = float(argv[argv.index("--hours") + 1]) if "--hours" in argv else float((row.get("cold_after_hours") or {}).get("wt", 24))
        cap = int(argv[argv.index("--max") + 1]) if "--max" in argv else 5
        ov = Path(row["overflow"]["wt"])
        if not Path(ov.anchor).exists():
            print(f"move: overflow drive {ov.anchor} not present")
            return 1
        import sync
        repo = Path(sync.worktrees(HERE.parents[1])[0][0])
        ok, keep = cold_trees(row, hours, repo)
        for p, why in keep:
            print(f"  keep   {Path(p).name}: {why}")
        done = 0
        for p, branch, idle in ok[:cap]:
            if not apply:
                print(f"  would move {Path(p).name} [{branch}] idle {idle:.0f} h -> {ov}")
                continue
            good, msg = move_tree(repo, p, ov)
            print(f"  {'moved' if good else 'FAILED'} {Path(p).name}: {msg}")
            done += good
        files = cold_cache_files(row)
        if files:
            print(f"  {'moved' if apply else 'would move'} {move_cache(row, files, apply)} cold cache file(s) to {row['overflow'].get('data')}")
        print(f"move: {'moved' if apply else 'would move'} {done if apply else min(len(ok), cap)} tree(s), {len(keep)} kept"
              + ("" if apply else "; --apply moves"))
        print("\n".join(status_lines(plan)))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
