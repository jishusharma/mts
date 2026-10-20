"""gate_impact.py - which tests a change can reach, for the 60-second ship gate (GATE_SPEED.md X1, X2, X5).

  reach(changed, root)        -> Reach: the test files an import-graph reaches from the changed files, whether live code imports them
  plan_budget(...)            -> (kept, deferred): fills a time budget, direct tests of the change are never deferred
  balance(files, est, k)      -> the files split into at most k chunks of about equal estimated seconds
  quarantine_rows / quarantine_problems / active_deselects: the flaky-test list scripts/dev/gate_quarantine.tsv

The graph is built fresh from `git ls-files` on every call (about 1 s for ~900 files): nothing is stored, so nothing can be stale or
corrupt across the many worktrees. Edges are real imports only (`import a.b`, `from a import b`, relative ones; a package is known by the
name of its folder). A test is reached when it is in the reverse import closure of the changed modules, or when it references a module of that
closure (an import, a path or script name, `python x.py`, a quoted dotted name such as "pkg.mod.fn", `-m pkg.mod`, import_module), or it names
a changed data file. String mentions are NOT followed transitively (tried first: one string mention in a hub script made every module reach 59
tests). What this cannot see, CI sees: a module another module runs as a subprocess, a file read at run time.
Callers fall back to the old whole-shard smoke gate on any exception here.
"""
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

LIVE_DIRS = ("MyTradingSys/execution/", "MyTradingSys/runtime/", "scripts/sched/", "src/")
SHARED = ("__init__", "conftest")      # act on every test beside them
DATA_SKIP = (".md", ".txt")            # docs are the doc steps' job (a ride-along doc must not seed every script that names it)
FAST_BUDGET_S = 8                      # OURS: selection budget in wall seconds; keep fast gate well under smoke gate
EFFECTIVE_WORKERS = 3                  # OURS: measured 2026-10-18 on 4 cores / 8 threads with other sessions running: 6 workers gave a 2-3x speedup, not 6x
QUARANTINE = "scripts/dev/gate_quarantine.tsv"
NO_QUARANTINE = ("MyTradingSys/execution/", "MyTradingSys/runtime/", "MyTradingSys/tests/")   # live-path tests are never deselected (MyTradingSys/tests/ holds the live-code tests: DECISION OURS, whole dir refused)
QUARANTINE_MAX_DAYS = 14   # OURS: a quarantine row may expire at most this many days from today, so a flaky test cannot be parked for good

_IMPORT_RE = re.compile(r"^[ \t]*(?:from[ \t]+([\w.]+)[ \t]+import[ \t]+(\([^)]*\)|[^\n#;]*)|import[ \t]+([^\n#;]+))", re.M)
_NAME_RE = re.compile(r"[A-Za-z_]\w*")
_AS_RE = re.compile(r"\bas\s+\w+")
_PATH_RE = re.compile(r"[/\\]([A-Za-z_]\w*)(?![\w/\\-])")                   # scripts/dev/x, ../x.py (a file, not a directory)
_QUOTED_RE = re.compile(r"""['"]([A-Za-z_]\w*)\.py['"]""")                  # ROOT / "scripts" / "dev" / "x.py"
_PYRUN_RE = re.compile(r"\bpython[\w.]*[ \t]+([A-Za-z_]\w*)\.py\b")          # "python x.py boot"
_DOTTED_RE = re.compile(r"""['"]([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)['"]""")   # "pkg.mod.fn" for patch() / import_module / setattr
_DASHM_RE = re.compile(r"""-m['",\s]+([A-Za-z_][\w.]*)""")                   # [sys.executable, "-m", "pkg.mod"]


def norm(f):
    return f.replace("\\", "/")


def stem_of(f):
    """The name other code imports a file by: its stem, or its folder's name for a package's __init__.py."""
    p = PurePosixPath(norm(f))
    return p.parent.name if p.stem == "__init__" and p.parent.name else p.stem


def is_test_file(f):
    name = PurePosixPath(norm(f)).name
    return name.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py"))


def imported_names(text):
    """Every name an import statement in `text` can mean: the dotted parts of the module and the imported names."""
    out = set()
    for m in _IMPORT_RE.finditer(text):
        if m.group(1):
            out.update(x for x in m.group(1).split(".") if x)
            out.update(_NAME_RE.findall(_AS_RE.sub("", m.group(2))))
        else:
            out.update(_NAME_RE.findall(_AS_RE.sub("", m.group(3))))
    return out


def ref_stems(text):
    """Imports plus every other way test or script text names a module (see the module doc); a superset of imported_names."""
    out = imported_names(text)
    for rx in (_PATH_RE, _QUOTED_RE, _PYRUN_RE):
        out.update(rx.findall(text))
    for m in _DOTTED_RE.finditer(text):
        out.update(m.group(1).split("."))
    for m in _DASHM_RE.finditer(text):
        out.update(m.group(1).split("."))
    return out


def tracked_py(root=REPO):
    r = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, text=True, errors="replace", timeout=60)
    if r.returncode != 0:
        raise RuntimeError("git ls-files failed: " + r.stderr.strip())
    return [f for f in r.stdout.split("\0") if f.endswith(".py") and (Path(root) / f).is_file()]


class Reach:
    """tests: repo-relative test files reached; direct: the subset that references a changed file itself (never deferred); closure: every
    .py in the reverse import closure; live_hit: closure files under LIVE_DIRS that are not themselves changed (live code imports the change)."""

    def __init__(self):
        self.tests, self.direct, self.closure, self.live_hit, self.stems = set(), set(), set(), [], set()


_REPO_CACHE = {}


def _repo_index(root):
    root_key = str(Path(root).resolve())
    cached = _REPO_CACHE.get(root_key)
    if cached is not None:
        return cached
    files = tracked_py(root)
    texts = {}
    for f in files:
        try:
            texts[f] = (Path(root) / f).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            texts[f] = ""
    by_stem = defaultdict(set)
    test_files = []
    test_refs = {}
    for f in files:
        t = texts[f]
        for n in imported_names(t):
            by_stem[n].add(f)
        if is_test_file(f):
            test_files.append(f)
            test_refs[f] = ref_stems(t)
    entry = (files, texts, by_stem, test_files, test_refs)
    _REPO_CACHE[root_key] = entry
    return entry


def reach(changed, root=REPO):
    changed = [norm(f) for f in changed if f]
    files, texts, by_stem, test_files, test_refs = _repo_index(root)
    seed_stems = {stem_of(f) for f in changed if f.endswith(".py")}
    seed_files = {f for f in changed if f.endswith(".py") and f in texts}
    for f in changed:
        if not f.endswith(".py") and not f.endswith(DATA_SKIP):
            base = PurePosixPath(f).name
            for g, t in texts.items():
                if base in t:
                    seed_files.add(g)
                    seed_stems.add(stem_of(g))
    stems, closure, todo = set(seed_stems), set(seed_files), list(seed_stems)
    while todo:
        for g in by_stem.get(todo.pop(), ()):
            closure.add(g)
            s = stem_of(g)
            if s not in stems:
                stems.add(s)
                todo.append(s)
    r = Reach()
    r.stems, r.closure = stems, closure
    r.live_hit = sorted(f for f in closure if f.startswith(LIVE_DIRS) and f not in changed)
    def folders(fs):
        return {PurePosixPath(f).parent.as_posix() + "/" for f in fs if PurePosixPath(f).stem in SHARED and PurePosixPath(f).parent.as_posix() != "."}

    shared_seed, shared_all = folders(seed_files), folders(closure)
    counterparts = {"test_" + s for s in seed_stems}
    for t in test_files:
        refs = test_refs[t]
        if t in seed_files or refs & seed_stems or PurePosixPath(t).stem in counterparts or any(t.startswith(s) for s in shared_seed):
            r.tests.add(t)
            r.direct.add(t)
        elif t in closure or refs & stems or any(t.startswith(s) for s in shared_all):
            r.tests.add(t)
    return r


def estimate(f, table, default=2):
    return table.get(PurePosixPath(norm(f)).name, default)


def plan_budget(direct, others, est, workers, base_s=0, budget=FAST_BUDGET_S):
    """(kept, deferred): every `direct` file is kept; `others` are added cheapest first while the estimated wall time stays inside `budget`
    (lower bound: total work / workers, and the largest single file). est: file -> seconds. base_s: seconds of work already planned."""
    kept = list(direct)
    total = base_s + sum(est(f) for f in kept)
    longest = max([est(f) for f in kept] or [0])
    deferred = []
    for f in sorted(others, key=lambda f: (est(f), f)):
        e = est(f)
        if max(longest, e, (total + e) / max(1, workers)) <= budget:
            kept.append(f)
            total += e
            longest = max(longest, e)
        else:
            deferred.append(f)
    return kept, deferred


def balance(files, est, k):
    """Split `files` into at most k non-empty chunks of about equal estimated seconds (longest first into the lightest chunk)."""
    bins = [[0, []] for _ in range(max(1, min(k, len(files))))] if files else []
    for f in sorted(files, key=lambda f: (-est(f), f)):
        b = min(bins, key=lambda b: b[0])
        b[0] += est(f)
        b[1].append(f)
    return [sorted(b[1]) for b in bins if b[1]]


def quarantine_rows(text):
    """[(test_id, owner, expires 'YYYY-MM-DD', reason)] from the tsv text: blank lines and # comments skipped, short rows padded with ''."""
    rows = []
    for line in (text or "").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            cells = [c.strip() for c in line.split("\t")]
            rows.append(tuple((cells + ["", "", "", ""])[:4]))
    return rows


def quarantine_problems(rows, today=None):
    """One message per row that is not a valid, unexpired entry (owner and a real date are required; expiry at most QUARANTINE_MAX_DAYS ahead; live-path ids are refused)."""
    today = today or date.today()
    out = []
    for tid, owner, exp, why in rows:
        try:
            d = date.fromisoformat(exp)
        except ValueError:
            out.append(f"{tid}: expiry '{exp}' is not YYYY-MM-DD")
            continue
        if not tid or not owner or not why:
            out.append(f"{tid or '?'}: test id, owner and reason are all required")
        if d < today:
            out.append(f"{tid}: quarantine expired {exp} (owner {owner}): fix the test or renew with a reason")
        if d > today + timedelta(days=QUARANTINE_MAX_DAYS):
            out.append(f"{tid}: quarantine expiry {exp} is more than {QUARANTINE_MAX_DAYS} days away (owner {owner}): use a shorter expiry and renew with a reason")
        if tid.startswith(NO_QUARANTINE):
            out.append(f"{tid}: live-path tests are never quarantined")
    return out


def active_deselects(rows, today=None):
    """pytest node ids to deselect: valid rows only (an expired or live-path row deselects nothing)."""
    today = today or date.today()
    bad = {r[0] for r in rows if quarantine_problems([r], today)}
    return [r[0] for r in rows if r[0] not in bad]


def trunk_quarantine(root=REPO, ref="origin/fast-track"):
    """The quarantine rows as committed on the trunk (a ship cannot quarantine its own failing test); [] when unreadable."""
    r = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{QUARANTINE}"], capture_output=True, text=True, errors="replace", timeout=30)
    return quarantine_rows(r.stdout) if r.returncode == 0 else []


def main(argv):
    if argv[:1] == ["--check-quarantine"]:
        path = REPO / QUARANTINE
        rows = quarantine_rows(path.read_text(encoding="utf-8")) if path.is_file() else []
        bad = quarantine_problems(rows)
        for b in bad:
            print("QUARANTINE FAIL: " + b)
        print(f"quarantine: {len(rows)} row(s), {len(bad)} problem(s)")
        return 1 if bad else 0
    if argv[:1] == ["reach"]:
        r = reach(argv[1:])
        print(f"closure {len(r.closure)} files, tests {len(r.tests)} ({len(r.direct)} direct), live_hit {r.live_hit}")
        for t in sorted(r.tests):
            print(("  * " if t in r.direct else "    ") + t)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
