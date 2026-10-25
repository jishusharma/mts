"""Preship: the checks the ship gate fails on most, run while the work is written instead of at `sync.py ship` (operator 2026-10-22).

Operator 2026-10-22: "make sure that sessions, they know beforehand where the ship can actually fail ... whatever checks they must
do, it should also be hooked." RULES is built from the red CI runs and gate-fix commits of 2026-10-19..22 (each rule names them).
Every rule runs the gate's OWN check (never a copy), so it cannot drift from the gate.

  hook-edit    PostToolUse (Write|Edit|MultiEdit): the first time a session touches a file a rule covers, say what the ship will
               check and the fix; a fast rule (< 1 s) is also run on the spot and its failure shown. Never blocks.
  hook-commit  PreToolUse (Bash): on `git commit`, run every rule the staged files (plus tracked edits with -a) reach; any failure
               denies the commit with the fix. The same failure set is denied once per session, then allowed (a trunk that is
               already red must not trap a session; the ship gate still stops it). A doc size cap is denied every time: only
               this commit's own file can break it, and `sync.py ship` checks it again on a docs-only ship (docs_ship_failures).
  check [files...]   run the rules by hand (default: files changed against origin/fast-track plus the working tree); exit 1 on failure.
Env: MTS_PRESHIP=off disables both hooks. Never raises in hook mode.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import nowin  # noqa: E402
    nowin.install()
except Exception:
    pass

PY = sys.executable
COLLECTED = ("MyTradingSys/tests/", "MyTradingSys/backtest/", "MyTradingSys/options/tests/")   # test_gate_discovery_b150.py
COMMIT = re.compile(r"(^|[;&|(]\s*|\s)git(\s+-C\s+(\"[^\"]+\"|'[^']+'|\S+))?\s+commit(?![-\w])")


def _docs(p):
    return p in ("CLAUDE.md", "AGENTS.md") or (p.startswith("MyTradingSys/system/") and p.endswith((".md", ".txt"))) \
        or p.startswith("MyTradingSys/tests/docs/")


def _roles(p):
    return p.startswith("MyTradingSys/system/roles/") or p in ("MyTradingSys/system/ROLES.md", "MyTradingSys/system/START_HERE.txt")


def _new_test(p):
    return Path(p).name.startswith("test_") and p.endswith(".py") and not p.startswith(COLLECTED) and "archive" not in p.lower()


def _lookahead(p):
    return p.endswith(".py") and p.startswith("MyTradingSys/") and not p.startswith("MyTradingSys/tests/") \
        and not Path(p).name.startswith("test_")


def _own_test(p, root):
    """scripts/dev/x.py -> scripts/dev/test_x.py when it exists; a scripts/dev test file -> itself."""
    if not (p.startswith("scripts/dev/") and p.endswith(".py")):
        return None
    name = Path(p).name
    t = p if name.startswith("test_") else "scripts/dev/test_" + name
    return t if (Path(root) / t).exists() else None


CAP_TEST = "MyTradingSys/tests/docs/test_integrity.py"
# name, covers(path), commands(root, paths), fast, fix, seen in (evidence)
CAP_RULE = ("doc size cap", _docs, lambda r, ps: [[PY, "-m", "pytest", "-q", CAP_TEST, "-k", "size_cap"]], True,
            "move detail out of the file into a MyTradingSys/system/ doc (B18: not one-line word trims); caps: SIZE_CAPS in " + CAP_TEST,
            "2175ef80: a docs-only ship (no local gate) pushed CLAUDE.md 100 B over its cap, trunk red; CI 39650507034/39638135365")
ALWAYS_DENY = {CAP_RULE[0], "look-ahead lint"}   # lint: --new only fails on a hit nobody reviewed, so a red trunk never traps a session (62a05b2eb)
RULES = [
    CAP_RULE,
    ("doc caps and contracts", _docs, lambda r, ps: [[PY, "-m", "pytest", "-q", "-x", "MyTradingSys/tests/docs", "-k", "not size_cap"]], False,
     "trim under the cap in MyTradingSys/tests/docs/test_integrity.py SIZE_CAPS; never quote the CLAUDE.md cap number elsewhere; "
     "session logs keep the last five entries; no git command words in hand-overs/runbooks",
     "CI 39650507034/39638135365/39600601462 CLAUDE.md 7241 B over its cap; 39663504601 cap number quoted; cd611cc4, 19b4ae1d"),
    ("hook rows", lambda p: p == ".claude/settings.json",
     lambda r, ps: [[PY, "-m", "pytest", "-q", "MyTradingSys/tests/docs/test_debugging_spine.py"]], False,
     "every hook script needs a row in MyTradingSys/system/DEBUGGING.md section 2",
     "prereq_guard.py 2026-10-22 (this rule's own origin)"),
    ("role files", _roles, lambda r, ps: [[PY, "scripts/dev/role_loader.py", "check"], [PY, "scripts/dev/role_loader.py", "lint"],
                                          [PY, "-m", "pytest", "-q", "MyTradingSys/tests/test_role_budget.py"]], True,
     "after ANY role-file edit run `python scripts/dev/role_loader.py retoken <file>`; keep `Read first:` in the first 8 lines; "
     "fit the byte budget in MyTradingSys/tests/test_role_budget.py BUDGET; no rule that contradicts ROLES.md",
     "CI 39531253508 builder.md 1514 > 1500; 39546187460 no Read first; 39547550824/39548363830 contradiction + stale token"),
    ("task cards", lambda p: re.match(r"^MyTradingSys/system/tasks/[^/]+\.json$", p) is not None,
     lambda r, ps: [[PY, "-m", "pytest", "-q", "scripts/dev/test_tasks.py", "-k", "RepoDataTest"]], True,
     "a ready/active card meets the Definition of Ready (`python scripts/dev/tasks.py lint` names the field); "
     "a sized SONNET/HAIKU/OPUS card carries worker and est_turns",
     "CI 39952758592/39957175338/39958377375 dsa-audit-04..10 tests empty, krown-data-cme-btc-volume no worker fields"),
    ("bug group map", lambda p: p in ("MyTradingSys/research/BUGS.md", "MyTradingSys/system/groups.json"),
     lambda r, ps: [[PY, "scripts/dev/test_make_groups.py"]], True,
     "give the new BUGS.md row a group: `python scripts/dev/make_groups.py --check` names it; add it in MyTradingSys/system/groups.json",
     "CI 39930461927/39932950182 B199 UNGROUPED"),
    ("test file not in the gate", _new_test,
     lambda r, ps: [[PY, "-m", "pytest", "-q", "MyTradingSys/tests/test_gate_discovery_b150.py"]], True,
     "add the path to scripts/dev/extra_tests.tsv (or a run_all_tests.py step)",
     "d62e5415, 5cfec9c1, fc41f20e, test_prereq_guard.py 2026-10-22"),
    ("look-ahead lint", _lookahead, lambda r, ps: [[PY, "scripts/dev/lookahead_lint.py", "--new"]], False,
     "fix the hit, or after review add a row to scripts/dev/lookahead_allowlist.tsv",
     "CI 39493633599; 19b4ae1d, ecbc995c, 5a43f4e6, bca2e763"),
    ("own unit tests", lambda p: p.startswith("scripts/dev/") and p.endswith(".py"),
     lambda r, ps: [[PY, "-m", "pytest", "-q", "-x", t] for t in sorted({_own_test(p, r) for p in ps} - {None})], False,
     "fix the code or the test before committing", "outcome_labeler 5d812463/c791836a"),
]


def rules_for(paths):
    return [(rule, [p for p in paths if rule[1](p)]) for rule in RULES if any(rule[1](p) for p in paths)]


def run_rule(rule, paths, root, timeout=120):
    """-> list of failure texts (empty = pass). The doc checks see only `paths`, as in the ship gate (MTS_GATE_CHANGED_FILES)."""
    fails = []
    env = dict(os.environ, MTS_GATE_CHANGED_FILES=chr(10).join(paths))
    for cmd in rule[2](root, paths):
        try:
            r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace", env=env)
        except subprocess.TimeoutExpired:
            fails.append(f"{' '.join(cmd[1:])}: timed out after {timeout} s")
            continue
        if r.returncode != 0:
            lines = (r.stdout + r.stderr).splitlines()
            out = [x for x in lines if re.search(r"FAIL|Error|assert|STALE|missing|over|>", x)] or lines
            fails.append(f"{' '.join(c for c in cmd[1:] if c not in ('-m', '-q', '-x'))}: " + " | ".join(x.strip()[:220] for x in out[-3:]))
    return fails


def cap_failures(root, paths):
    """The doc size cap for `paths` (under 1 s); sync.py runs it on a docs-only ship, which has no other local gate."""
    ps = [p for p in paths if CAP_RULE[1](p)]
    if not ps or not (Path(root) / CAP_TEST).exists():
        return []
    return run_rule(CAP_RULE, ps, root)


# A docs/data-only ship has no local gate; these rules guard doc/data files and take seconds, so it runs them (7 of the 9 red
# fast-track runs of 2026-10-23 came from such ships: role files, task cards, BUGS.md rows; CI found them minutes later).
DOCS_SHIP_RULES = ("doc size cap", "role files", "task cards", "bug group map")


def docs_ship_failures(root, paths):
    """-> [(rule, failure texts)] of the DOCS_SHIP_RULES the paths reach; sync.py runs it on a docs-only ship.
    A rule whose checker script is not in `root` is not run (a repo without it: test_sync's scratch repos), as cap_failures did."""
    out = []
    for rule, ps in rules_for(paths):
        scripts = [a for cmd in rule[2](root, ps) for a in cmd[1:] if a.endswith(".py")]
        if rule[0] in DOCS_SHIP_RULES and all((Path(root) / s).exists() for s in scripts):
            fails = run_rule(rule, ps, root)
            if fails:
                out.append((rule, fails))
    return out


def report(results):
    return "; ".join(f"[{rule[0]}] {' / '.join(f)} -> FIX: {rule[4]}" for rule, f in results)


def toplevel(cwd):
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def git_lines(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return [x for x in r.stdout.splitlines() if x.strip()] if r.returncode == 0 else []


def state_file(name):
    return Path(os.environ.get("MTS_STOP_GUARD_HOME") or Path.home() / ".claude") / name


def remember(name, session_id, key):
    """True when (session, key) was already recorded in state file `name`; records it otherwise (last 50 sessions)."""
    if not session_id:
        return False
    f = state_file(name)
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    seen = d.get(session_id, [])
    if key in seen:
        return True
    d[session_id] = (seen + [key])[-40:]
    d = dict(list(d.items())[-50:])
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(d), encoding="utf-8", newline=chr(10))
    except OSError:
        pass
    return False


def hook_edit(data):
    tool_input = data.get("tool_input") or {}
    fp = tool_input.get("file_path") or tool_input.get("notebook_path")
    root = toplevel(Path(fp).parent if fp else data.get("cwd") or os.getcwd()) if fp else None
    if not root:
        return ""
    try:
        rel = Path(fp).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return ""
    notes = []
    for rule, ps in rules_for([rel]):
        if not rule[2](root, ps):
            continue
        fails = run_rule(rule, ps, root, timeout=20) if rule[3] else []
        if fails:
            notes.append(f"PRESHIP [{rule[0]}] now failing: {' / '.join(fails)} -> FIX: {rule[4]}")
        elif not remember("mts-preship-seen.json", data.get("session_id"), rule[0]):
            notes.append(f"PRESHIP [{rule[0]}] the ship gate checks this file; it failed here before ({rule[5]}). FIX if red: {rule[4]}. "
                         f"`python scripts/dev/preship.py check` runs it now; `git commit` runs it for you.")
    if not notes:
        return ""
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": chr(10).join(notes)}})


def hook_commit(data):
    cmd = str((data.get("tool_input") or {}).get("command") or "")
    m = COMMIT.search(cmd)
    if not m:
        return ""
    cwd = data.get("cwd") or os.getcwd()
    if m.group(3):
        cwd = str(Path(cwd) / m.group(3).strip("\"'"))
    root = toplevel(cwd)
    if not root:
        return ""
    paths = git_lines(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR")
    tail = cmd[m.end():].split("&&")[0]
    if re.search(r"(\s-[a-zA-Z]*a[a-zA-Z]*\b|\s--all\b)", tail):
        paths += git_lines(root, "diff", "--name-only", "--diff-filter=ACMR")
    paths = sorted(set(paths))
    results = [(rule, f) for rule, ps in rules_for(paths) for f in [run_rule(rule, ps, root)] if f]
    if not results:
        return ""
    text = report(results)
    key = hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
    if remember("mts-preship-denied.json", data.get("session_id"), key) and not any(r[0] in ALWAYS_DENY for r, _ in results):
        return ""
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                              "permissionDecisionReason": "PRESHIP: this commit would fail the ship gate. " + text
                                              + " (Fix and commit again; the same failure is not blocked twice, except a doc size cap.)"}})


def hook(mode, stdin_text):
    try:
        if os.environ.get("MTS_PRESHIP", "").lower() == "off":
            return ""
        data = json.loads(stdin_text or "{}")
        return hook_edit(data) if mode == "hook-edit" else hook_commit(data)
    except Exception:
        return ""


def main(argv):
    if argv[:1] in (["hook-edit"], ["hook-commit"]):
        out = hook(argv[0], sys.stdin.read())
        if out:
            print(out)
        return 0
    if argv[:1] == ["check"]:
        root = toplevel(os.getcwd()) or os.getcwd()
        paths = argv[1:] or sorted(set(git_lines(root, "diff", "--name-only", "--diff-filter=ACMR", "origin/fast-track")))
        bad = 0
        for rule, ps in rules_for(paths):
            fails = run_rule(rule, ps, root)
            print(("FAIL " if fails else "ok   ") + rule[0] + (f": {' / '.join(fails)} -> FIX: {rule[4]}" if fails else ""))
            bad += bool(fails)
        if not paths:
            print("no changed files")
        return 1 if bad else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
