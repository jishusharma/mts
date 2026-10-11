"""retention.py - one place that decides what MTS may discard. Dry run unless --apply.

Policy: MyTradingSys/system/RETENTION_POLICY.md. Every rule names a reason it is safe
(duplicate, regenerable, git has it, decommissioned lane, write-only log). Nothing that a
script, test or live process reads is a candidate. Run: python scripts/dev/retention.py [--apply]
"""
import filecmp
import gzip
import os
import shutil
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DAY = 86400
TAIL_LINES = 2000


def _age_days(path):
    return (time.time() - os.path.getmtime(path)) / DAY


def _size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(path) for f in fs)


def _files(root):
    """{relative path: size} for every file under root."""
    return {os.path.relpath(os.path.join(r, f), root): os.path.getsize(os.path.join(r, f))
            for r, _, fs in os.walk(root) for f in fs}


def _same_bytes(x, y):
    """Direct byte compare; filecmp caches by stat signature and goes stale on same-size rewrites in one mtime tick."""
    with open(x, 'rb') as fx, open(y, 'rb') as fy:
        return fx.read() == fy.read()


def dup_copy_is_subset(copy, original):
    """True only if every file in `copy` exists in `original` with the same size, except names in IGNORE_DIFF."""
    if not (os.path.isdir(copy) and os.path.isdir(original)):
        return False
    a, b = _files(copy), _files(original)
    # B152: sizes alone can hide a different file; require identical bytes too
    return all(k in b and (k in IGNORE_DIFF or (b[k] == v and _same_bytes(os.path.join(copy, k), os.path.join(original, k))))
               for k, v in a.items())


IGNORE_DIFF = {"SESSION_PASTE.txt"}  # regenerated on every session start; the live copy is newer


def old_children(parent, days):
    if not os.path.isdir(parent):
        return []
    return [os.path.join(parent, e) for e in os.listdir(parent)
            if _age_days(os.path.join(parent, e)) > days]


def plan(root=ROOT):
    """Returns [(kind, path, bytes, reason)]; kind is 'delete' or 'trim'."""
    out = []
    dup = os.path.join(root, "Dumps.pre_B138")
    if dup_copy_is_subset(dup, os.path.join(root, "Dumps")):
        out.append(("delete", dup, _size(dup), "strict subset of Dumps (B138 duplicate)"))
    for d in old_children(os.path.join(root, "backup_session"), 14):
        out.append(("delete", d, _size(d), "ignored pre-git session backup >14d; live files are tracked"))
    for d in old_children(os.path.join(root, "Dumps", "_archive"), 14):
        out.append(("delete", d, _size(d), "declutter archive >14d"))
    # B152: NUC-QUEUE/done is NOT a candidate: scripts/worker/audit_digest.py reads its task/verdict/reply files.
    # write-only / unread logs: keep the tail
    for rel in ("MyTradingSys/system/session_end_logs.md", "runtime_data/mts-watch.log",
                "runtime_data/supervisor_log.txt"):   # supervisor_log: head is gzipped beside it before the trim (B152)
        p = os.path.join(root, *rel.split("/"))
        if os.path.isfile(p) and os.path.getsize(p) > 200_000:
            out.append(("trim", p, os.path.getsize(p), f"log with no reader; keep last {TAIL_LINES} lines"))
    return out


def apply(items):
    for kind, path, _, _ in items:
        if kind == "delete":
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
        else:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            tail, head = lines[-TAIL_LINES:], lines[:-TAIL_LINES]
            if head:   # irreversible otherwise; the removed part stays as evidence (LOG_GAP_2026-10-02 cites old line numbers)
                stamp = time.strftime("%Y%m%d")
                with gzip.open(f"{path}.head_{stamp}.gz", "at", encoding="utf-8", newline=chr(10)) as z:
                    z.writelines(head)
            st = os.stat(path)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.writelines(tail)
            os.utime(path, (st.st_atime, st.st_mtime))   # testnet_canary reads the mtime as last activity (B152)


def main(argv):
    items = plan()
    total = 0
    groups = {}
    for kind, path, size, why in items:
        total += size
        key = (kind, os.path.dirname(os.path.relpath(path, ROOT)) or os.path.relpath(path, ROOT), why)
        g = groups.setdefault(key, [0, 0])
        g[0] += 1
        g[1] += size
    for (kind, where, why), (n, size) in groups.items():
        print(f"{kind:6} {size / 1e6:9.1f} MB {n:4d} item(s)  {where}  [{why}]")
    print(f"total {total / 1e6:.1f} MB in {len(items)} items")
    if "--apply" in argv:
        apply(items)
        print("applied")
    else:
        print("dry run; add --apply")


if __name__ == "__main__":
    main(sys.argv[1:])
