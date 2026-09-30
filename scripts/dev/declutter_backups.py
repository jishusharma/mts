"""Classify and (optionally) archive backup/staging clutter in the working tree.

T0 maintainer tool. Never deletes: superseded files are MOVED to
Dumps/_archive/<date>/<same relative path> with a CSV manifest (path, class, reason, sha256).
Only __pycache__ dirs are deleted (with --apply).

Classes:
  superseded  - content recoverable from git, or a rejected/raw worker output, or a
                staged .new identical to its live file, or backup older than the last
                commit of its base (with no pending .new)
  staged      - live in-flight .new work (left alone)
  unknown     - could not prove superseded (left alone, listed for the supervisor)

Usage: python scripts/dev/declutter_backups.py [--apply] [--date YYYY-MM-DD]
"""
import argparse, csv, datetime as dt, hashlib, os, re, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SKIP_DIRS = {'.git', 'node_modules', 'target', '.idea', 'Dumps', '.secrets', 'backup_session'}
BACKUP_RE = re.compile(r'^(?P<base>.+?)(?P<new>\.new)?\.(?P<kind>pre_[A-Za-z0-9_\-]+|rejected_[A-Za-z0-9_]*|new|qwen_raw|qwen\d+)$')
REJECT_DIRS = ('_nuc_rejected', 'qwen_raw_015_017')


def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True).stdout


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


_hist = {}


def history_blobs(rel):
    """Set of blob ids this path has had in any commit."""
    if rel not in _hist:
        blobs = set()
        for line in git('log', '--all', '--format=%H', '--', rel).split():
            b = git('rev-parse', f'{line}:{rel}').strip()
            if b and ' ' not in b:
                blobs.add(b)
        _hist[rel] = blobs
    return _hist[rel]


def last_commit_ts(rel):
    out = git('log', '-1', '--format=%ct', '--', rel).strip()
    return int(out) if out else None


def tracked(rel):
    return bool(git('ls-files', '--', rel).strip())


def classify(rel):
    ap = os.path.join(ROOT, rel)
    name = os.path.basename(rel)
    parts = rel.replace('\\', '/').split('/')
    if any(d in parts for d in REJECT_DIRS) or parts[0].startswith(''):
        return 'superseded', 'rejected/raw worker output or stray scratch dir'
    m = BACKUP_RE.match(name)
    if not m:
        return None, None
    base_rel = os.path.join(os.path.dirname(rel), m.group('base'))
    base_ap = os.path.join(ROOT, base_rel)
    kind = m.group('kind')
    if kind.startswith('rejected') or kind.startswith('qwen'):
        return 'superseded', f'rejected worker output ({kind})'
    if kind == 'new' and m.group('new'):
        return 'superseded', '.new.new double-suffix Qwen output (verifier BLOCKED pattern)'
    blob = git('hash-object', ap).strip()
    if tracked(base_rel.replace('\\', '/')) and blob in history_blobs(base_rel.replace('\\', '/')):
        return 'superseded', 'content exists in git history of base'
    if kind == 'new':
        if os.path.exists(base_ap) and sha256(base_ap) == sha256(ap):
            return 'superseded', '.new identical to live file (promoted)'
        return 'staged', 'in-flight .new'
    # kind == pre_*
    mt = os.path.getmtime(ap)
    if m.group('new'):  # X.new.pre_tag : backup of a staged .new
        if os.path.exists(base_ap + '.new') and os.path.getmtime(base_ap + '.new') >= mt:
            return 'superseded', 'older snapshot of a still-staged .new (current .new is newer)'
    ts = last_commit_ts(base_rel.replace('\\', '/'))
    if ts and ts >= mt and not os.path.exists(base_ap + '.new'):
        return 'superseded', 'base committed after backup was taken; no pending .new'
    return 'unknown', 'base not committed after backup / untracked base'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--date', default=dt.date.today().isoformat())
    ap.add_argument('--exclude', action='append', default=[],
                    help='path prefix to leave alone (repeatable), e.g. an area another session is staging in')
    a = ap.parse_args()
    excl = tuple(p.replace('\\', '/').rstrip('/') + '/' for p in a.exclude)
    arch = os.path.join(ROOT, 'Dumps', '_archive', a.date)
    rows, pyc = [], set()
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        if os.path.basename(d) == '__pycache__':
            if not (excl and os.path.relpath(d, ROOT).replace('\\', '/').startswith(excl)):
                pyc.add(d)
            dirs[:] = []
            continue
        for f in files:
            rel = os.path.normpath(os.path.relpath(os.path.join(d, f), ROOT))
            if excl and rel.replace('\\', '/').startswith(excl):
                continue
            cls, why = classify(rel)
            if cls:
                rows.append((rel, cls, why, sha256(os.path.join(ROOT, rel))))
    for cls in ('superseded', 'staged', 'unknown'):
        sel = [r for r in rows if r[1] == cls]
        print(f'== {cls}: {len(sel)}')
        if cls != 'superseded':
            for r in sel:
                print(f'   {r[0]}  [{r[2]}]')
    print(f'== __pycache__ dirs: {len(pyc)}')
    if not a.apply:
        return
    os.makedirs(arch, exist_ok=True)
    man = os.path.join(arch, 'MANIFEST.csv')
    new_file = not os.path.exists(man)
    with open(man, 'a', newline='\n', encoding='utf-8') as fh:
        w = csv.writer(fh, lineterminator='\n')
        if new_file:
            w.writerow(['path', 'class', 'reason', 'sha256'])
        for rel, cls, why, h in rows:
            if cls != 'superseded':
                continue
            dst = os.path.join(arch, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(os.path.join(ROOT, rel), dst)
            w.writerow([rel.replace('\\', '/'), cls, why, h])
    for d in pyc:
        shutil.rmtree(d, ignore_errors=True)
    # remove now-empty reject dirs
    for d, dirs, files in os.walk(ROOT, topdown=False):
        if any(x in d for x in REJECT_DIRS) or os.path.relpath(d, ROOT).startswith(''):
            try:
                os.rmdir(d)
            except OSError:
                pass
    print('manifest:', man)


if __name__ == '__main__':
    main()
