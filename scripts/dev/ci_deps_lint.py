#!/usr/bin/env python
"""ci_deps_lint.py - a test file the gate runs must not hard-depend on a package the CI job does not install.

Why (2026-10-16, three CI-red rounds in 3 h): research test files import pandas (directly or through a sibling module such as
`import common` -> `import pandas`), but ci.yml installed only "pytest numpy tzdata". The desktop gate has every package, so it never
caught it; the runners died at collection with "ModuleNotFoundError: No module named 'pandas'".

What it does: for every tracked test file (test_*.py / *_test.py, archives and B150 SKIP entries excluded; B150 guarantees the gate
runs each one) it walks the imports that EXECUTE at import time, in source order, and follows repo modules transitively:
  - resolved like Python would: sys.path inserts found in the files (Path(__file__).parents[N] / "a" / "b" is evaluated statically),
    the test file's own dir (script dir / pytest rootdir), its package base, the repo root, the importing file's dir; as a last resort
    a repo module name that exists exactly once in the repo;
  - package, name = third-party when it is not stdlib (sys.stdlib_module_names) and not a repo module;
  - NOT a hard dependency: imports inside functions, under `if TYPE_CHECKING:` or `if __name__ == "__main__":`; in a `try:` whose
    handler catches ImportError (also ModuleNotFoundError / Exception / bare except, without a bare re-raise; the guard covers what the
    imported repo module imports too); under an `if` that tests importlib.util.find_spec("pkg") or a flag assigned from it or from
    such a try; after a module-level `pytest.importorskip("pkg")` or after an availability `if` whose body skips/raises.
A package must be in the `pip install ...` text line of .github/workflows/ci.yml (CI has no PyYAML: parsed as text). A package pulled
in by a listed one counts (PROVIDES: pandas -> numpy, dateutil, pytz, six; pytest -> pluggy, iniconfig, packaging, pygments, py).

Entries are the test files (plus the conftest.py files above them); scripts a gate step runs directly (tasks.py, wiring_scan.py) are
reached only when a test imports them. Not covered (stay manual): importlib.import_module(name) with a non-literal name, imports done
by a function the module calls, pytest plugins named in ini files, a package that is installed but too old. Literal
import_module("x") / __import__("x") at module level count.

Usage: python scripts/dev/ci_deps_lint.py [-v] [--ci-yml FILE] [--root DIR]     exit 1 + one line per violation
       test file -> import chain -> package. Add the package to the ci.yml pip line AND scripts/dev/cloud_setup.py GATE_DEPS
       (test_cloud_setup keeps them equal), or guard the import (try/except ImportError, find_spec flag, pytest.importorskip).
"""
import ast
import gc
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CI_YML = ".github/workflows/ci.yml"

# pip distribution (lower case, '_' -> '-') -> import names it provides on the CI Python (3.12, ubuntu + windows), dependencies included
PROVIDES = {
    "pytest": ("pytest", "_pytest", "py", "pluggy", "iniconfig", "packaging", "pygments"),
    "numpy": ("numpy",),
    "pandas": ("pandas", "numpy", "dateutil", "pytz", "six", "tzdata"),
    "tzdata": ("tzdata",),
}
IMPORT_NAME = {"pyyaml": "yaml", "pillow": "PIL", "opencv-python": "cv2", "opencv-python-headless": "cv2", "scikit-learn": "sklearn",
               "python-dateutil": "dateutil", "beautifulsoup4": "bs4", "attrs": "attr"}
# removed from the stdlib in Python 3.13 (PEP 594) but still there on the CI Python 3.12; a newer desktop Python no longer lists them
LEGACY_STDLIB = frozenset("aifc audioop cgi cgitb chunk crypt imghdr mailcap msilib nis nntplib ossaudiodev pipes sndhdr spwd sunau "
                          "telnetlib uu xdrlib lib2to3 asyncore asynchat imp distutils smtpd".split())
ARCHIVE_PREFIXES = ("Dumps/", "_archive/")
PIP_RE = re.compile(r"\bpip[0-9.]*\s+install\b([^#&;|]*)")
SKIP_ARG_FLAGS = ("-r", "--requirement", "-c", "--constraint", "-e", "--editable", "-i", "--index-url", "--extra-index-url", "-f",
                  "--find-links", "-t", "--target")
IMPORT_ERRORS = ("ImportError", "ModuleNotFoundError", "Exception", "BaseException")
FUNC_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)


# ---------------------------------------------------------------------------------------------------------------- ci.yml

def norm_dist(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def ci_distributions(text):
    """Distribution names on every `pip install ...` line of the workflow text (versions, extras, options dropped), in order."""
    dists = []
    for line in text.splitlines():
        m = PIP_RE.search(line)
        if not m:
            continue
        toks = m.group(1).split()
        i = 0
        while i < len(toks):
            t = toks[i].strip("\"'")
            if t in SKIP_ARG_FLAGS:
                i += 2
                continue
            i += 1
            if not t or t.startswith("-") or t.startswith("$") or "/" in t or t.endswith((".txt", ".whl", ".gz")):
                continue
            n = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", t)
            if n:
                dists.append(norm_dist(n.group(0)))
    return dists


def ci_import_names(dists):
    """Top-level import names that exist on a CI runner after installing `dists`."""
    names = set()
    for d in dists:
        names.update(PROVIDES.get(d) or (IMPORT_NAME.get(d) or d.replace("-", "_"),))
    return names


# ---------------------------------------------------------------------------------------------------------------- repo index

class Repo:
    """The files a CI checkout would have: git's tracked + untracked-not-ignored files (a new file in this change counts), or a plain
    directory walk when root is not a git repo (the unit tests' tmp dirs). Parsed ASTs are cached."""

    def __init__(self, root, files=None):
        self.root = Path(root).resolve()
        self.files = sorted(set(files)) if files is not None else self._list()
        self.py = {f for f in self.files if f.endswith(".py")}
        self.dirs = {""}
        for f in self.files:
            parts = f.split("/")
            for i in range(1, len(parts)):
                self.dirs.add("/".join(parts[:i]))
        self.py_dirs = set()          # dirs with a python file somewhere below (namespace packages)
        for f in self.py:
            parts = f.split("/")
            for i in range(1, len(parts)):
                self.py_dirs.add("/".join(parts[:i]))
        self.by_top = {}
        for f in self.py:
            parts = f.split("/")
            if parts[-1] == "__init__.py":
                if len(parts) >= 2:
                    self.by_top.setdefault(parts[-2], set()).add("/".join(parts[:-2]))
            else:
                self.by_top.setdefault(parts[-1][:-3], set()).add("/".join(parts[:-1]))
        self._trees = {}
        self._infos = {}
        self._calls = {}

    def _list(self):
        try:
            r = subprocess.run(["git", "-C", str(self.root), "ls-files", "--cached", "--others", "--exclude-standard"],
                               capture_output=True, text=True, timeout=60)
            if r.returncode == 0 and r.stdout.strip():
                return [p for p in r.stdout.splitlines()
                        if p and not p.startswith(".claude/worktrees/") and (self.root / p).is_file()]   # other sessions' work trees are not this checkout
        except (OSError, subprocess.SubprocessError):
            pass
        out = []
        for dp, dn, fn in os.walk(self.root):
            dn[:] = [d for d in dn if not d.startswith(".") and d not in ("__pycache__", "node_modules")]
            out += [(Path(dp) / f).relative_to(self.root).as_posix() for f in fn]
        return out

    def tree(self, rel):
        if rel not in self._trees:
            try:
                self._trees[rel] = ast.parse((self.root / rel).read_text(encoding="utf-8", errors="replace"), filename=rel)
            except (SyntaxError, ValueError, OSError):
                self._trees[rel] = None
        return self._trees[rel]

    def info(self, rel):
        if rel not in self._infos:
            self._infos[rel] = FileInfo(self.tree(rel), self.root / rel)
        return self._infos[rel]

    def relevant_calls(self, stmt):
        """Calls inside one module-level statement that matter: importorskip("x"), sys.path.insert/append(..), import_module("x") /
        __import__("x"). Cached per statement (the same file is walked once per test file that reaches it)."""
        key = id(stmt)
        found = self._calls.get(key)
        if found is None:
            found = []
            for n in ast.walk(stmt):
                if not isinstance(n, ast.Call):
                    continue
                name = call_name(n)
                if name == "importorskip" and n.args and const_str(n.args[0]):
                    found.append(n)
                elif name in ("insert", "append") and n.args and isinstance(n.func, ast.Attribute) \
                        and isinstance(n.func.value, ast.Attribute) and n.func.value.attr == "path" \
                        and isinstance(n.func.value.value, ast.Name) and n.func.value.value.id == "sys":
                    found.append(n)
                elif name in ("import_module", "__import__") and n.args and const_str(n.args[0]):
                    found.append(n)
            self._calls[key] = found
        return found

    def is_file(self, rel):
        return rel in self.py

    def is_dir(self, rel):
        return rel in self.dirs


def join(a, b):
    return f"{a}/{b}" if a else b


def top_of(name):
    return str(name).split(".")[0]


def call_name(node):
    f = node.func
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""


def const_str(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def catches_import_error(try_node):
    """True when a handler of this try swallows ImportError (names, tuple, bare except) and does not just re-raise it."""
    for h in getattr(try_node, "handlers", []):
        t = h.type
        names = []
        if t is None:
            names = ["BaseException"]
        else:
            for e in (t.elts if isinstance(t, ast.Tuple) else [t]):
                names.append(e.attr if isinstance(e, ast.Attribute) else e.id if isinstance(e, ast.Name) else "")
        if any(n in IMPORT_ERRORS for n in names) and not any(isinstance(n, ast.Raise) and n.exc is None for n in ast.walk(h)):
            return True
    return False


def imported_tops(stmts):
    out = set()
    for s in stmts:
        for n in ast.walk(s):
            if isinstance(n, ast.Import):
                out.update(top_of(a.name) for a in n.names)
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                out.add(top_of(n.module))
    return out


def find_spec_tops(node):
    """Package names in find_spec("pkg") / find_loader("pkg") calls inside this expression."""
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and call_name(n) in ("find_spec", "find_loader") and n.args and const_str(n.args[0]):
            out.add(top_of(const_str(n.args[0])))
    return out


class FileInfo:
    """Module-level facts of one file: simple name = expression assignments (for static path evaluation) and availability flags
    (name -> packages), e.g. HAS_PIL = find_spec("PIL") is not None, or HAS_CV set in a try/except ImportError."""

    def __init__(self, tree, path):
        self.path = path
        self.env = {}
        self.flags = {}
        if tree is not None:
            self._scan(tree.body, False)

    def _scan(self, stmts, in_guard_try, pkgs=frozenset()):
        for s in stmts:
            if isinstance(s, (ast.Assign, ast.AnnAssign)):
                value = s.value
                targets = s.targets if isinstance(s, ast.Assign) else [s.target]
                names = [t.id for t in targets if isinstance(t, ast.Name)]
                for n in names:
                    if value is not None:
                        self.env[n] = value
                    found = find_spec_tops(value) if value is not None else set()
                    if found:
                        self.flags[n] = found
                    elif in_guard_try and pkgs:
                        self.flags[n] = set(pkgs)
            elif isinstance(s, (ast.Try, getattr(ast, "TryStar", ast.Try))):
                guard = catches_import_error(s)
                self._scan(s.body, guard, imported_tops(s.body) if guard else frozenset())
                for h in s.handlers:
                    self._scan(h.body, guard, imported_tops(s.body) if guard else frozenset())
                self._scan(s.orelse, False)
                self._scan(s.finalbody, False)
            elif isinstance(s, ast.If):
                self._scan(s.body, in_guard_try, pkgs)
                self._scan(s.orelse, in_guard_try, pkgs)
            elif isinstance(s, (ast.With, ast.For, ast.While)):
                self._scan(s.body, in_guard_try, pkgs)


# ---------------------------------------------------------------------------------------------------------------- static paths

def eval_path(node, info, root, depth=0):
    """The value of a path expression as a str (absolute, derived from __file__ / cwd), or None when it cannot be known statically."""
    if depth > 12 or node is None:
        return None

    def e(n):
        return eval_path(n, info, root, depth + 1)

    s = const_str(node)
    if s is not None:
        return s
    if isinstance(node, ast.Name):
        if node.id == "__file__":
            return str(info.path)
        return e(info.env.get(node.id))
    if isinstance(node, ast.Attribute) and node.attr == "parent":
        v = e(node.value)
        return os.path.dirname(os.path.normpath(v)) if v is not None else None
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and node.value.attr == "parents":
        idx = node.slice
        if isinstance(idx, ast.Constant) and isinstance(idx.value, int) and idx.value >= 0:
            v = e(node.value.value)
            if v is None:
                return None
            v = os.path.normpath(v)
            for _ in range(idx.value + 1):
                v = os.path.dirname(v)
            return v
        return None
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.Add)):
        a, b = e(node.left), e(node.right)
        if a is None or b is None:
            return None
        return os.path.join(a, b) if isinstance(node.op, ast.Div) else a + b
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            piece = const_str(v) if isinstance(v, ast.Constant) else e(v.value) if isinstance(v, ast.FormattedValue) else None
            if piece is None:
                return None
            parts.append(piece)
        return "".join(parts)
    if isinstance(node, ast.Call):
        name, f = call_name(node), node.func
        args = node.args
        if name in ("Path", "PurePath", "PosixPath", "WindowsPath") and args:
            vals = [e(a) for a in args]
            return None if any(v is None for v in vals) else os.path.join(*vals)
        if name in ("cwd", "getcwd") and not args:
            return str(root)
        if name in ("resolve", "absolute", "expanduser", "as_posix") and not args and isinstance(f, ast.Attribute):
            return e(f.value)
        if name in ("str", "fspath", "abspath", "realpath", "normpath", "expanduser") and len(args) == 1:
            return e(args[0])
        if name == "dirname" and len(args) == 1:
            v = e(args[0])
            return os.path.dirname(os.path.normpath(v)) if v is not None else None
        if name == "joinpath" and isinstance(f, ast.Attribute):
            vals = [e(f.value)] + [e(a) for a in args]
            return None if any(v is None for v in vals) else os.path.join(*vals)
        if name == "join" and isinstance(f, ast.Attribute) and (
                (isinstance(f.value, ast.Attribute) and f.value.attr == "path") or (isinstance(f.value, ast.Name) and f.value.id in ("path", "posixpath", "ntpath"))):
            vals = [e(a) for a in args]
            return None if not vals or any(v is None for v in vals) else os.path.join(*vals)
    return None


# ---------------------------------------------------------------------------------------------------------------- the walk

def label(rel):
    p = Path(rel)
    return f"{p.parent.name}/__init__.py" if p.name == "__init__.py" and p.parent.name else p.name


def is_main_guard(test):
    return (isinstance(test, ast.Compare) and isinstance(test.left, ast.Name) and test.left.id == "__name__"
            and any(const_str(c) == "__main__" for c in test.comparators))


def is_type_checking(test):
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")


def body_skips(stmts):
    """The block ends the import of the module (skip / exit / raise): what follows only runs when the check above passed."""
    for s in stmts:
        for n in ast.walk(s):
            if isinstance(n, ast.Raise):
                return True
            if isinstance(n, ast.Call) and call_name(n) in ("skip", "exit", "SkipTest", "skipTest", "_exit"):
                return True
    return False


class EntryWalk:
    """The import-time walk of ONE test file. State shared along the chain, as in a real import: sys.path inserts and importorskip."""

    def __init__(self, repo, allowed, entry):
        self.repo, self.allowed, self.entry = repo, allowed, entry
        self.inserted = []            # repo-relative dirs put on sys.path by executed code, newest first
        self.skipped = set()          # packages a module-level importorskip / skip-block has vouched for
        self.seen = set()
        self.violations = {}          # package -> chain (first one found)
        self.edges = []               # (chain, package) of third-party imports that were guarded (-v)
        entry_dir = str(Path(entry).parent.as_posix())
        entry_dir = "" if entry_dir == "." else entry_dir
        base = entry_dir
        while base and repo.is_file(join(base, "__init__.py")):
            base = str(Path(base).parent.as_posix())
            base = "" if base == "." else base
        self.base_dirs = [entry_dir, base, ""]

    # -- walk
    def run(self):
        d = Path(self.entry).parent.as_posix()
        dirs = []
        while True:
            dirs.append("" if d == "." else d)
            if d in (".", ""):
                break
            d = Path(d).parent.as_posix()
        for dd in reversed(dirs):   # pytest loads conftest.py from the root down before the test module
            c = join(dd, "conftest.py")
            if self.repo.is_file(c):
                self.follow(c, False, [])
        self.follow(self.entry, False, [])
        return self.violations

    def follow(self, rel, guarded, chain):
        key = (rel, guarded)
        if key in self.seen:
            return
        self.seen.add(key)
        tree = self.repo.tree(rel)
        if tree is None:
            return
        self.visit(tree.body, rel, guarded, chain + [rel])

    def visit(self, stmts, rel, guarded, chain):
        info = self.repo.info(rel)
        for s in stmts:
            if isinstance(s, ast.Import):
                for a in s.names:
                    self.do_import(a.name.split("."), [], 0, rel, guarded, chain)
            elif isinstance(s, ast.ImportFrom):
                self.do_import((s.module or "").split(".") if s.module else [], [a.name for a in s.names if a.name != "*"], s.level,
                               rel, guarded, chain)
            elif isinstance(s, (ast.Try, getattr(ast, "TryStar", ast.Try))):
                g = guarded or catches_import_error(s)
                self.visit(s.body, rel, g, chain)
                for h in s.handlers:
                    self.visit(h.body, rel, guarded, chain)
                self.visit(s.orelse, rel, g, chain)
                self.visit(s.finalbody, rel, guarded, chain)
            elif isinstance(s, ast.If):
                if is_type_checking(s.test):
                    self.visit(s.orelse, rel, guarded, chain)
                elif is_main_guard(s.test):
                    self.visit(s.orelse, rel, guarded, chain)
                else:
                    pkgs = set(find_spec_tops(s.test))
                    for n in ast.walk(s.test):
                        if isinstance(n, ast.Name) and n.id in info.flags:
                            pkgs |= info.flags[n.id]
                    g = guarded or bool(pkgs)
                    self.visit(s.body, rel, g, chain)
                    self.visit(s.orelse, rel, g, chain)
                    if pkgs and (body_skips(s.body) or body_skips(s.orelse)):
                        self.skipped |= pkgs
            elif isinstance(s, (ast.With, ast.AsyncWith, ast.For, ast.AsyncFor, ast.While)):
                self.visit(s.body, rel, guarded, chain)
                self.visit(getattr(s, "orelse", []), rel, guarded, chain)
            elif isinstance(s, ast.ClassDef):
                self.visit(s.body, rel, guarded, chain)
            elif isinstance(s, FUNC_DEFS):
                continue
            elif isinstance(s, getattr(ast, "Match", ())):
                for case in s.cases:
                    self.visit(case.body, rel, guarded, chain)
            else:
                self.calls(s, rel, guarded, chain)

    def calls(self, stmt, rel, guarded, chain):
        """Module-level expression statements: sys.path changes, importorskip, literal dynamic imports."""
        for n in self.repo.relevant_calls(stmt):
            name = call_name(n)
            if name == "importorskip":
                self.skipped.add(top_of(const_str(n.args[0])))
            elif name in ("insert", "append"):
                d = self.rel_dir(eval_path(n.args[-1], self.repo.info(rel), self.repo.root))
                if d is not None:
                    if name == "insert":
                        self.inserted.insert(0, d)
                    else:
                        self.inserted.append(d)
            else:
                self.do_import(const_str(n.args[0]).split("."), [], 0, rel, guarded, chain)

    def rel_dir(self, value):
        """Repo-relative dir for a statically known sys.path entry, or None (outside the repo / not a directory of it)."""
        if value is None:
            return None
        try:
            p = Path(os.path.normpath(value)).resolve().relative_to(self.repo.root).as_posix()
        except (ValueError, OSError):
            return None
        p = "" if p == "." else p
        return p if self.repo.is_dir(p) else None

    # -- resolution
    def exists_top(self, base, name):
        """`name` is importable from a sys.path entry `base`: a module file, a package, or a namespace dir holding python files."""
        d = join(base, name)
        return self.repo.is_file(d + ".py") or self.repo.is_file(join(d, "__init__.py")) or d in self.repo.py_dirs

    def resolve_in(self, base, parts):
        """Repo files an import of dotted `parts` executes with `base` on sys.path (package __init__s, then the module)."""
        out, cur = [], base
        for p in parts:
            d = join(cur, p)
            if self.repo.is_file(d + ".py"):
                out.append(d + ".py")
                break
            if not self.repo.is_dir(d):
                break
            init = join(d, "__init__.py")
            if self.repo.is_file(init):
                out.append(init)
            cur = d
        return out

    def locate(self, parts, rel):
        """Repo files the import executes; [] = a repo module we cannot place (ambiguous name); None = not a repo module."""
        if not parts or not parts[0]:
            return None
        here = str(Path(rel).parent.as_posix())
        for base in self.inserted + self.base_dirs + ["" if here == "." else here]:
            if self.exists_top(base, parts[0]):
                return self.resolve_in(base, parts)
        top = parts[0]
        if top in sys.stdlib_module_names or top in LEGACY_STDLIB:
            return None
        cands = self.repo.by_top.get(top)
        if cands and len(cands) == 1:
            return self.resolve_in(next(iter(cands)), parts)
        return [] if cands else None

    def do_import(self, parts, names, level, rel, guarded, chain):
        cur_dir = str(Path(rel).parent.as_posix())
        cur_dir = "" if cur_dir == "." else cur_dir
        if level:
            base = cur_dir
            for _ in range(level - 1):
                base = str(Path(base).parent.as_posix()) if base else ""
                base = "" if base == "." else base
            files = []
            if parts and parts[0]:
                files = self.resolve_in(base, parts) or []
            else:
                init = join(base, "__init__.py")
                files = [init] if self.repo.is_file(init) else []
            for f in files:
                self.follow(f, guarded, chain)
            for n in names:
                sub = self.resolve_in(base, (parts if parts and parts[0] else []) + [n]) or []
                for f in sub:
                    self.follow(f, guarded, chain)
            return
        if not parts or not parts[0]:
            return
        top = parts[0]
        files = self.locate(parts, rel)
        if files is None:
            if not (top in sys.stdlib_module_names or top in LEGACY_STDLIB):
                self.third_party(top, guarded, chain)
            return
        for f in files:
            self.follow(f, guarded, chain)
        for n in names:                      # `from pkg import submodule`
            more = self.locate(parts + [n], rel) or []
            for f in more:
                self.follow(f, guarded, chain)

    def third_party(self, top, guarded, chain):
        if guarded or top in self.skipped:
            self.edges.append((chain, top, "guarded"))
        elif top in self.allowed:
            self.edges.append((chain, top, "ci"))
        elif top not in self.violations:
            self.violations[top] = list(chain)


# ---------------------------------------------------------------------------------------------------------------- driver

def b150_skips(repo):
    """Keys of MyTradingSys/tests/test_gate_discovery_b150.py SKIP (test files deliberately outside the gate), read as a literal."""
    p = "MyTradingSys/tests/test_gate_discovery_b150.py"
    tree = repo.tree(p) if repo.is_file(p) else None
    for n in (tree.body if tree else []):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SKIP" for t in n.targets):
            try:
                return set(ast.literal_eval(n.value))
            except (ValueError, TypeError):
                return set()
    return set()


def test_files(repo):
    skip = b150_skips(repo)
    out = []
    for f in repo.files:
        name = f.rsplit("/", 1)[-1]
        if not (name.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py"))):
            continue
        if "archive" in f.lower() or f.startswith(ARCHIVE_PREFIXES) or f in skip:
            continue
        out.append(f)
    return sorted(out)


def lint(root, ci_text, files=None, entries=None, edges=None, repo=None):
    """[(entry file, chain of files, package)] for every hard third-party import CI cannot satisfy. Raises ValueError when ci_text has
    no pip install line (fail closed: the parse would be blind). `edges`, a list, receives (entry, chain, package, "ci"|"guarded") for
    every third-party import that is fine (-v shows them, so a pass is not a blind pass). `repo`: a prebuilt Repo (tests share one parse)."""
    dists = ci_distributions(ci_text)
    if not dists:
        raise ValueError("no `pip install <packages>` line found in the CI workflow text")
    allowed = ci_import_names(dists)
    gc_was_on = gc.isenabled()
    gc.disable()            # ~500 parsed ASTs: the cyclic collector otherwise costs a third of the run
    try:
        repo = repo or Repo(root, files)
        entries = list(entries) if entries is not None else test_files(repo)
        found = []
        for entry in entries:
            walk = EntryWalk(repo, allowed, entry)
            for pkg, chain in sorted(walk.run().items()):
                found.append((entry, chain, pkg))
            if edges is not None:
                edges.extend((entry, c, pkg, how) for c, pkg, how in walk.edges)
    finally:
        if gc_was_on:
            gc.enable()
    return found, dists, len(entries)


def format_violation(entry, chain, pkg):
    hops = [entry] + [label(c) for c in chain[1:]] if chain else [entry]
    return f"{' -> '.join(hops)} -> {pkg}"


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    root = REPO
    ci_path = None
    verbose = "-v" in args
    entries = None
    if "--root" in args:
        root = Path(args[args.index("--root") + 1])
    if "--ci-yml" in args:
        ci_path = Path(args[args.index("--ci-yml") + 1])
    if "--entries" in args:
        raw = args[args.index("--entries") + 1]
        entries = [e.strip() for e in raw.split(",") if e.strip()]
    ci_path = ci_path or (Path(root) / CI_YML)
    if not hasattr(sys, "stdlib_module_names"):
        print("ci_deps_lint: needs Python 3.10+ (sys.stdlib_module_names)")
        return 1
    try:
        text = ci_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"ci_deps_lint: cannot read {ci_path}: {e}")
        return 1
    edges = []
    try:
        found, dists, n = lint(root, text, entries=entries, edges=edges)
    except ValueError as e:
        print(f"ci_deps_lint: {e}")
        return 1
    for entry, chain, pkg in found:
        print(format_violation(entry, chain, pkg))
    if verbose:
        seen = {}
        for entry, chain, pkg, how in edges:
            seen.setdefault((pkg, how), []).append(format_violation(entry, chain, pkg))
        for (pkg, how), lines in sorted(seen.items()):
            print(f"  [{how}] {pkg}: {len(lines)} test file(s), e.g. {lines[0]}")
            if how == "guarded":
                for ln in lines[1:6]:
                    print(f"           {ln}")
    if found:
        print(f"ci_deps_lint: FAIL - {len(found)} hard import(s) of a package the CI pip line does not install ({' '.join(dists)}). "
              "Add it to the ci.yml pip line AND scripts/dev/cloud_setup.py GATE_DEPS, or guard the import "
              "(try/except ImportError, find_spec flag, pytest.importorskip).")
        return 1
    print(f"ci_deps_lint: OK - {n} test files, every hard third-party import is in the CI pip line ({' '.join(dists)}) or guarded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
