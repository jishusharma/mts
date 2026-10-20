"""gate_select.py - which gate steps a ship must run (operator 2026-10-16: ship fast, the full suite runs behind in CI).

  select(files, steps) -> (mode, step numbers)
  explain(files, steps) -> (mode, step numbers, one-line reason: the first file/rule that forced full, or the ALWAYS steps of a smoke)
    files: paths changed vs origin/fast-track; steps: [(num, cmd_text)] of the plan (run_all_tests.build_plan).
    mode  none   nothing changed: no steps
          docs   only docs/data: NO steps (D10 2026-10-20: CI gates behind the push); only a task card in the diff adds the card lint 3tl
          smoke  code outside the live path: steps whose test file matches a changed file, the pytest shards whose tests mention
                 its module name, plus ALWAYS (wiring, B150 discovery, CI deps lint) and 3tl when a card is in the diff; CI runs everything
                 behind the push
          full   any live-path file, or ANY path no rule knows (fail closed): every step, the old --quick gate

Nothing here decides what is safe to deploy: CI on both OSes does, and auto_deploy only takes green/fast-track.
"""
import re
from functools import lru_cache
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[2]

DOC_SUFFIXES = (".md", ".txt")
# data/docs folders: json/csv/html in here is content, not code (GATE_SPEED D5: .tsv .gz .err .log .png .svg .parquet .pdf .jpg too,
# 2026-10-18: a research .tsv / .json.gz / .err each forced a full gate)
DATA_DIRS = ("MyTradingSys/research/", "MyTradingSys/system/", "MyTradingSys/items/", "MyTradingSys/methodology/")
DATA_SUFFIXES = (".json", ".csv", ".html", ".jsonl", ".tsv", ".gz", ".err", ".log", ".png", ".svg", ".parquet", ".pdf", ".jpg")
# Config/data that is not code but that tests read (GATE_SPEED D5): smoke = ALWAYS + every step whose tests name the file.
# .claude/settings.json also gets its JSON parse step (3js). .gitattributes, .github/, mts.ps1, scripts/core|sched stay full.
CONFIG_FILES = (".gitignore", ".aiexclude", ".claude/settings.json")
DEV_DATA_SUFFIXES = (".tsv", ".json", ".csv", ".html")   # scripts/dev/<x>.tsv (lookahead allowlist), *.tpl.html: read by their tests
JSON_STEP = "3js"
WIRING_REGISTRY = "MyTradingSys/system/wiring_registry.json"

# Live path (CLAUDE.md "Gates"): always the full quick gate.
FULL_RE = re.compile(
    r"^(MyTradingSys/execution/|MyTradingSys/runtime/|scripts/sched/|src/|pom\.xml$|\.github/|"
    r"scripts/dev/(sync|run_all_tests|gate_select|run_extra_tests|auto_deploy|live_mirror|cloud_setup|wiring_scan|ci_watch|config_check|"
    r"ci_deps_lint|run_staged_tests|gate_impact)\.py$|scripts/dev/gate_quarantine\.tsv$|"
    r"MyTradingSys/backtest/layers/[^/]+/[^/]*(live|writer)[^/]*\.py$)")
# Non-live code folders: smoke with name-matched steps + the pytest shards + extras
CODE_DIRS = ("scripts/dev/", "scripts/worker/", "MyTradingSys/tests/", "MyTradingSys/backtest/", "MyTradingSys/research/",
             "MyTradingSys/options/", "MyTradingSys/observation/")

ALWAYS = ("3w", "3x", "3gd", "3dl")   # wiring, test-file discovery (B150), CI deps lint: seconds, catch the usual merge-time breaks
CARDS_DIR = "MyTradingSys/system/tasks/"
CARD_LINT = "3tl"   # task-card DoR lint (~2 min): only when a card is in the diff (D10 2026-10-20)
DOC_STEPS = ("3tl", "3q", "3pc", "3c", "4d")   # no longer selected by any mode (docs take no local step); kept for gate_impact/run_all_tests
SHARD_PREFIX = "4"                    # every pytest shard is numbered 4, 4b, 4c ...


def _is_doc(f):
    if f.endswith(".md"):
        return True
    if f.endswith(".txt"):
        return not FULL_RE.match(f)   # a .txt on the live path (resources, run lists) is read by live code: not a doc
    return f.endswith(DATA_SUFFIXES) and f.startswith(DATA_DIRS)


def has_card(files):
    return any(f.replace("\\", "/").startswith(CARDS_DIR) for f in files)


def docs_only(files):
    """True when every changed path is a doc/data file (the `docs` mode of explain): a ship of these takes no local gate."""
    return bool(files) and all(_is_doc(f.replace("\\", "/")) for f in files)


def _is_config(f):
    """GATE_SPEED D5: config/data files that are not code; smoke runs ALWAYS + the steps whose tests name them."""
    return f in CONFIG_FILES or (f.startswith("scripts/dev/") and f.count("/") == 2 and f.endswith(DEV_DATA_SUFFIXES))


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


def _cmd_files(cmd_text, root):
    """The test files a step command names: each .py file token, and every test_*.py under each directory token."""
    for tok in cmd_text.replace("\\", "/").split():
        p = Path(root) / tok
        if tok.endswith(".py") and p.is_file():
            yield p
        elif p.is_dir():
            yield from p.rglob("test_*.py")


@lru_cache(maxsize=4096)
def _text(path):
    """Source of one test file; None when unreadable (callers fail closed)."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def references(stem, path):
    """True when the test file at `path` is module `stem`'s test, or really references it (_reference_re). Unreadable = True."""
    if Path(path).stem == stem:
        return True
    t = _text(str(path))
    return True if t is None else bool(_reference_re(stem).search(t))


def names(basename, path):
    """True when the test file at `path` names the (non-.py) file `basename` anywhere in its text. Unreadable = True."""
    t = _text(str(path))
    return True if t is None else basename in t


def mentions(stem, cmd_text, root=REPO):
    """True when a test file named in cmd_text (or any test_*.py under a directory it names) really references the module `stem`
    (_reference_re), or is that file: the pytest shard that imports or runs the changed module. Unreadable = True (fail closed), and
    so is a module name no import can name (`__init__`, `conftest`: they act on every test beside them)."""
    if stem.startswith("__") or stem == "conftest":
        return True
    return any(references(stem, f) for f in _cmd_files(cmd_text, root))


def names_file(basename, cmd_text, root=REPO):
    """True when a test file named in cmd_text names the data/config file `basename` (GATE_SPEED D5: tests that read it)."""
    return any(names(basename, f) for f in _cmd_files(cmd_text, root))


SHARED_STEMS = ("__init__", "conftest")


def _shared_module(f):
    """A .py that acts on every test beside it or that sibling tests import by a name no regex can follow: __init__, conftest,
    common*, _private helpers. Its whole parent folder's tests run."""
    stem = PurePosixPath(f).stem
    return f.endswith(".py") and (stem in SHARED_STEMS or stem.startswith(("common", "_")))


def _study_folder(f):
    """MyTradingSys/research/<study>/ (layer_lab: research/layer_lab/<study>/) holding f, or None for a file directly in research/."""
    parts = f.split("/")
    if len(parts) >= 5 and parts[:3] == ["MyTradingSys", "research", "layer_lab"]:
        return "/".join(parts[:4]) + "/"
    if len(parts) >= 4 and parts[:2] == ["MyTradingSys", "research"] and parts[2] != "layer_lab":
        return "/".join(parts[:3]) + "/"
    return None


def extra_subset(files, tests, root=REPO):
    """GATE_SPEED D6: the step-3xt test files (`tests`, repo-relative) a change can reach. A file runs when: it changed; it sits in
    the study folder of a changed code/data file; its folder (or a parent) holds a changed shared module (_shared_module); it
    references a changed module (references) or names a changed non-.py file (names). A changed doc only reaches tests that name it.
    Returns the subset in `tests` order. Over-selection is the safe direction: same-named stems in other folders are run too."""
    files = [f.replace("\\", "/") for f in files if f]
    picked = set()
    for f in files:
        doc = f.endswith(DOC_SUFFIXES)
        base, stem = PurePosixPath(f).name, PurePosixPath(f).stem
        folder = None if doc else _study_folder(f)
        shared = PurePosixPath(f).parent.as_posix() + "/" if _shared_module(f) else None
        for t in tests:
            if t == f or PurePosixPath(t).name == "test_" + base or (folder and t.startswith(folder)) or (shared and t.startswith(shared)):
                picked.add(t)
            elif f.endswith(".py") and references(stem, Path(root) / t):
                picked.add(t)
            elif not f.endswith(".py") and names(base, Path(root) / t):
                picked.add(t)
    return [t for t in tests if t in picked]


LAYERS = "MyTradingSys/backtest/layers/"


def layer_subset(files, modules, root=REPO):
    """GATE_SPEED D6: the step-5b layer test modules (dotted names) a change can reach: every module of a changed layer folder
    (layers/<L>/), every module that references a changed module or names a changed non-.py file, and ALL modules when a changed file
    sits directly in layers/, is a shared module (_shared_module) of layers/, or is in a layer folder with no test module of its own."""
    files = [f.replace("\\", "/") for f in files if f and not f.endswith(DOC_SUFFIXES)]
    paths = {m: m.replace(".", "/") + ".py" for m in modules}
    picked = set()
    for f in files:
        base, stem = PurePosixPath(f).name, PurePosixPath(f).stem
        if f.startswith(LAYERS):
            rest = f[len(LAYERS):].split("/")
            folder = LAYERS + rest[0] + "/"
            if len(rest) == 1 or (_shared_module(f) and len(rest) == 2) or not any(p.startswith(folder) for p in paths.values()):
                return list(modules)
            picked.update(m for m, p in paths.items() if p.startswith(folder))
        for m, p in paths.items():
            if p == f or (f.endswith(".py") and references(stem, Path(root) / p)) or (not f.endswith(".py") and names(base, Path(root) / p)):
                picked.add(m)
    return [m for m in modules if m in picked]


def explain(files, steps, mentioned=mentions, named=names_file, step_files=None):
    """select() plus WHY: (mode, step numbers, one-line reason). The reason names the first file and rule that forced `full`, or
    (smoke) the ALWAYS steps that ran plus the name-matched extras; select() returns the first two.
    step_files (GATE_SPEED D6, from run_all_tests): {"3xt": [extra test paths], "5b": [layer module dotted names]}. Given, 3xt and 5b
    are picked when extra_subset / layer_subset reach a test (run_all_tests then runs only that subset); a docs ship whose study
    folder tests name a changed doc picks 3xt too. None = the old rules (3xt for backtest/research code, 5b for layer code)."""
    files = [f.replace("\\", "/") for f in files if f]
    all_nums = _nums(steps)
    if not files:
        return "none", [], "none: nothing changed vs origin/fast-track"
    code = [f for f in files if not _is_doc(f)]
    sf = step_files or {}
    subset_steps = set()
    if step_files is not None and code:
        if "3xt" in all_nums and extra_subset(files, sf.get("3xt", [])):
            subset_steps.add("3xt")
        if "5b" in all_nums and layer_subset(code, sf.get("5b", [])):
            subset_steps.add("5b")
    card = {CARD_LINT} & set(all_nums) if has_card(files) else set()
    if not code:
        nums = [n for n in all_nums if n in card]
        return "docs", nums, f"docs: {len(files)} doc/data file(s) only; " + (f"card lint {','.join(nums)} only" if nums else "no local step, CI gates behind the push")
    picked = {n for n in ALWAYS if n in all_nums} | subset_steps | card
    always = [n for n in all_nums if n in ALWAYS]
    for f in code:
        if FULL_RE.match(f):
            return "full", list(all_nums), f"full: {f} is on the live path (FULL_RE)"
        if _is_config(f):
            base = PurePosixPath(f).name
            picked.update(_name_matches(f, steps))
            picked.update(n for n, cmd in steps if named(base, cmd))
            if f == ".claude/settings.json" and JSON_STEP in all_nums:
                picked.add(JSON_STEP)
            continue
        if not f.endswith(".py") or not f.startswith(CODE_DIRS):
            return "full", list(all_nums), f"full: {f} matches no rule (fail closed: not a .py under a known code folder)"
        picked.update(_name_matches(f, steps))
        stem = PurePosixPath(f).stem
        picked.update(n for n, cmd in steps if n.startswith(SHARD_PREFIX) and n != "4d" and mentioned(stem, cmd))
        if step_files is None:
            if f.startswith("MyTradingSys/backtest/layers/"):
                picked.add("5b")
            if f.startswith(("MyTradingSys/backtest/", "MyTradingSys/research/")) and "3xt" in all_nums:
                picked.add("3xt")
    nums = [n for n in all_nums if n in picked]
    extra = [n for n in nums if n not in always]
    return "smoke", nums, (f"smoke: {len(code)} code file(s) outside the live path; ALWAYS steps {','.join(always)} ran"
                           + (f"; plus {','.join(extra)} (name/test/shard match)" if extra else ""))


def select(files, steps, mentioned=mentions):
    mode, nums, _ = explain(files, steps, mentioned)
    return mode, nums
