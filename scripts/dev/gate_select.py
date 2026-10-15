"""gate_select.py - which gate steps a ship must run (operator 2026-10-16: ship fast, the full suite runs behind in CI).

  select(files, steps) -> (mode, step numbers)
    files: paths changed vs origin/fast-track; steps: [(num, cmd_text)] of the plan (run_all_tests.build_plan).
    mode  none   nothing changed: no steps
          docs   only docs/data: the cheap doc invariants (DOC_STEPS), no gate slot needed
          smoke  code outside the live path: steps whose test file matches a changed file, the shards of the tests that import
                 it, plus ALWAYS (wiring, task-card DoR); CI runs everything behind the push
          full   any live-path file, or ANY path no rule knows (fail closed): every step, the old --quick gate

Nothing here decides what is safe to deploy: CI on both OSes does, and auto_deploy only takes green/fast-track.
"""
import re
from pathlib import PurePosixPath

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

ALWAYS = ("3w", "3x", "3tl")          # wiring + task-card Definition of Ready: seconds, catch the usual merge-time breaks
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
    return [n for n, cmd in steps if any(re.search(r"(^|[\s/\\])" + re.escape(p) + r"(\s|$)", cmd) for p in pair)]


def select(files, steps):
    files = [f.replace("\\", "/") for f in files if f]
    all_nums = _nums(steps)
    if not files:
        return "none", []
    code = [f for f in files if not _is_doc(f)]
    if not code:
        return "docs", [n for n in DOC_STEPS if n in all_nums]
    picked = {n for n in ALWAYS if n in all_nums}
    if len(code) < len(files):                    # docs ride along: their invariants too
        picked |= {n for n in DOC_STEPS if n in all_nums}
    for f in code:
        if FULL_RE.match(f) or not f.endswith(".py") or not f.startswith(CODE_DIRS):
            return "full", list(all_nums)          # live path, or a path no rule knows: fail closed
        picked.update(_name_matches(f, steps))
        if f.startswith("MyTradingSys/backtest/layers/"):
            picked.add("5b")
        if f.startswith(("MyTradingSys/backtest/", "MyTradingSys/research/", "MyTradingSys/tests/", "scripts/dev/")):
            picked.update(n for n in all_nums if n.startswith(SHARD_PREFIX) and n != "4d" or n == "3xt")
    return "smoke", [n for n in all_nums if n in picked]
