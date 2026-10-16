"""gate_select.py - which gate steps a ship must run (operator 2026-10-16: ship fast, the full suite runs behind in CI).

  select(files, steps) -> (mode, step numbers)
  explain(files, steps) -> (mode, step numbers, one-line reason: the first file/rule that forced full, or the ALWAYS steps of a smoke)
    files: paths changed vs origin/fast-track; steps: [(num, cmd_text)] of the plan (run_all_tests.build_plan).
    mode  none   nothing changed: no steps
          docs   only docs/data: the cheap doc invariants (DOC_STEPS), no gate slot needed
          smoke  code outside the live path: steps whose test file matches a changed file, the pytest shards whose tests mention
                 its module name, plus ALWAYS (wiring, task-card DoR, B150 discovery, CI deps lint); CI runs everything behind the push
          full   any live-path file, or ANY path no rule knows (fail closed): every step, the old --quick gate

Nothing here decides what is safe to deploy: CI on both OSes does, and auto_deploy only takes green/fast-track.
"""
import re
from functools import lru_cache
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[2]

DOC_SUFFIXES = (".md", ".txt")
# data/docs folders: json/csv/html in here is content, not code
DATA_DIRS = ("MyTradingSys/research/", "MyTradingSys/system/", "MyTradingSys/items/", "MyTradingSys/methodology/")
DATA_SUFFIXES = (".json", ".csv", ".html", ".jsonl")

# Live path (CLAUDE.md "Gates"): always the full quick gate.
FULL_RE = re.compile(
    r"^(MyTradingSys/execution/|MyTradingSys/runtime/|scripts/sched/|src/|pom\.xml$|\.github/|"
    r"scripts/dev/(sync|run_all_tests|gate_select|auto_deploy|live_mirror|cloud_setup)\.py$|"
    r"MyTradingSys/backtest/layers/[^/]+/[^/]*(live|writer)[^/]*\.py$)")
# Non-live code folders: smoke with name-matched steps + the pytest shards + extras
CODE_DIRS = ("scripts/dev/", "scripts/worker/", "MyTradingSys/tests/", "MyTradingSys/backtest/", "MyTradingSys/research/",
             "MyTradingSys/options/", "MyTradingSys/observation/")

ALWAYS = ("3w", "3x", "3tl", "3gd", "3dl")   # wiring, task-card DoR, test-file discovery (B150), CI deps lint: seconds, catch the usual merge-time breaks
DOC_STEPS = ("3tl", "3q", "3pc", "3c", "4d")   # task cards, INDEX/BUGS, prompt contract, guide sync, doc size/contract pytest
SHARD_PREFIX = "4"                    # every pytest shard is numbered 4, 4b, 4c ...


def _is_doc(f):
    if f.endswith(DOC_SUFFIXES):
        return True
    return f.endswith(DATA_SUFFIXES) and f.startswith(DATA_DIRS)


def _nums(steps):
    return [n for n, _ in steps]


def _name_matches(f, steps):
    """Steps whose command names this file or its test_<file>.py counterpart (by basename)."""
    base = PurePosixPath(f).name
    pair = {base, base[5:] if base.startswith("test_") else "test_" + base}
    return [n for n, cmd in steps if any(re.search(r"(^|[\s/\\(])" + re.escape(p) + r"(?![\w.])", cmd) for p in pair)]


@lru_cache(maxsize=None)
def _reference_re(stem):
    """A real reference to module `stem` in test source (2026-10-16: the bare word `dsa` pulled in 3 of 5 pytest shards through a variable
    name, a card id and a doc assertion on the text "dsa.py boot"): an import of it, the script run or opened (`.../<stem>.py`,
    `"<stem>.py"`, `python <stem>.py`), or a dotted string naming it (`patch("dsa.x")`, `import_module("scripts.dev.dsa")`).
    A comment, a longer name (`dsa_tools`, `test_dsa.py`), a directory or the filename inside a longer prose string is not."""
    s = re.escape(stem)
    return re.compile("|".join((
        rf"^[ \t]*import[ \t]+[^\n#;]*\b{s}\b",                                              # import s / import a, pkg.s as x
        rf"^[ \t]*from[ \t]+[\w.]*?\b{s}\b[\w.]*[ \t]+import\b",                             # from s import / from pkg.s import
        rf"^[ \t]*from[ \t]+[\w.]+[ \t]+import[ \t]+(?:\([^)]*|[^\n#;(]*)\b{s}\b",           # from pkg import s / import (a,\n s)
        rf"[/\\]{s}(?![\w/\\-])",                                                            # scripts/dev/s, ../s.py (a file, not a directory)
        rf"['\"]{s}\.py['\"]",                                                               # ROOT / "scripts" / "dev" / "s.py"
        rf"\bpython[\w.]*[ \t]+{s}\.py\b",                                                   # "python s.py boot"; "s.py boot" alone is prose
        rf"(?:import_module|__import__|spec_from_file_location|find_spec)\([ \t]*[rbf]?['\"](?:\w+\.)*{s}['\"]",
        rf"['\"](?:\w+\.)*{s}\.[A-Za-z_]\w*(?:\.\w+)*['\"]",                                 # "s.attr" for patch()/setattr()
    )), re.M)


def mentions(stem, cmd_text, root=REPO):
    """True when a test file named in cmd_text (or any test_*.py under a directory it names) really references the module `stem`
    (_reference_re), or is that file: the pytest shard that imports or runs the changed module. Unreadable = True (fail closed), and
    so is a module name no import can name (`__init__`, `conftest`: they act on every test beside them)."""
    if stem.startswith("__") or stem == "conftest":
        return True
    pat = _reference_re(stem)
    for tok in cmd_text.replace("\\", "/").split():
        p = Path(root) / tok
        if tok.endswith(".py") and p.is_file():
            files = [p]
        elif p.is_dir():
            files = list(p.rglob("test_*.py"))
        else:
            continue
        for f in files:
            if f.stem == stem:
                return True
            try:
                if pat.search(f.read_text(encoding="utf-8", errors="ignore")):
                    return True
            except OSError:
                return True
    return False


def explain(files, steps, mentioned=mentions):
    """select() plus WHY: (mode, step numbers, one-line reason). The reason names the first file and rule that forced `full`, or
    (smoke) the ALWAYS steps that ran plus the name-matched extras; select() returns the first two."""
    files = [f.replace("\\", "/") for f in files if f]
    all_nums = _nums(steps)
    if not files:
        return "none", [], "none: nothing changed vs origin/fast-track"
    code = [f for f in files if not _is_doc(f)]
    if not code:
        nums = [n for n in DOC_STEPS if n in all_nums]
        return "docs", nums, f"docs: {len(files)} doc/data file(s) only; doc invariants {','.join(nums)}"
    picked = {n for n in ALWAYS if n in all_nums}
    always = [n for n in all_nums if n in picked]
    if len(code) < len(files):                    # docs ride along: their invariants too
        picked |= {n for n in DOC_STEPS if n in all_nums}
    for f in code:
        if FULL_RE.match(f):
            return "full", list(all_nums), f"full: {f} is on the live path (FULL_RE)"
        if not f.endswith(".py") or not f.startswith(CODE_DIRS):
            return "full", list(all_nums), f"full: {f} matches no rule (fail closed: not a .py under a known code folder)"
        picked.update(_name_matches(f, steps))
        if f.startswith("MyTradingSys/backtest/layers/"):
            picked.add("5b")
        stem = PurePosixPath(f).stem
        picked.update(n for n, cmd in steps if n.startswith(SHARD_PREFIX) and n != "4d" and mentioned(stem, cmd))
        if f.startswith(("MyTradingSys/backtest/", "MyTradingSys/research/")) and "3xt" in all_nums:
            picked.add("3xt")
    nums = [n for n in all_nums if n in picked]
    extra = [n for n in nums if n not in always]
    return "smoke", nums, (f"smoke: {len(code)} code file(s) outside the live path; ALWAYS steps {','.join(always)} ran"
                           + (f"; plus {','.join(extra)} (name/test/shard match)" if extra else ""))


def select(files, steps, mentioned=mentions):
    mode, nums, _ = explain(files, steps, mentioned)
    return mode, nums
