#!/usr/bin/env python
"""Wiring scan: which code files does the running system actually reach?

Builds a reference graph over tracked code files (python imports, `python -m` dotted paths, script file names in
launchers, java class names) and classifies every non-test code file:

  LIVE       reachable from a live launcher (runtime_data/*.vbs, scripts/core|live|sched|worker|operator, mts.ps1, CI)
  DEV-TOOL   reachable from scripts/dev (the gate and operator tools) but not from a live launcher
  TEST-ONLY  referenced by tests only: built and tested, never run by anything -> wire it or remove it
  ORPHAN     referenced by nothing at all

The scan reads code, not docs. Names are matched textually, so a launcher that builds a module name from
pieces will show its target as TEST-ONLY/ORPHAN; confirm those by hand before deleting anything.

Usage: python scripts/dev/wiring_scan.py [--check] [--json out.json] [--md out.md]

The gate runs --check: every TEST-ONLY/ORPHAN file must be declared in MyTradingSys/system/wiring_registry.json
(TOOL, REPRO, PARKED, WIRE) and every declaration must still be true. Work cannot go quietly unwired again.

scripts/dev files are all roots (the gate and operator tools), so a dead one-off script there never shows as unwired. --check
therefore also prints WARN NO-READER for a non-test scripts/dev file that no other non-test code file references, that no
entry doc (CLAUDE.md, MyTradingSys/system/*.md, MyTradingSys/runtime/*.md, SKILL.md, relay prompts,
artifacts/registry.json) names. Warn only (exit code unchanged): archive it (git mv to _archive/) or name its reader in a doc.
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CODE_EXT = {'.py', '.ps1', '.vbs', '.cmd', '.bat', '.java', '.yml', '.yaml'}
SKIP_DIRS = {'.git', 'target', '__pycache__', 'node_modules', '_archive', 'archive', 'raw_transcripts_canonical',
             'extracts', 'my_charts', '.pytest_cache'}
LIVE_ROOT_PREFIX = ('runtime_data/', 'scripts/core/', 'scripts/live/', 'scripts/sched/', 'scripts/worker/',
                    'scripts/operator/', 'scripts/monitor/', '.github/')
LIVE_ROOT_FILES = {'mts.ps1'}
TEST_RE = re.compile(r'(^|/)(test_[^/]*|[^/]*_test\.py|[^/]*Test\.java)$')
NUL = bytes([0])
BACKSLASH = chr(92)

REGISTRY_PATH = 'MyTradingSys/system/wiring_registry.json'
DISPOSITIONS = {
    'TOOL': 'run by hand on purpose (backtest driver, diagnostic, maintenance script)',
    'REPRO': 'reproduces a number recorded in a named note; kept so the note can be re-run',
    'PARKED': 'built for an item that is parked; wire it or archive it when the item resolves',
    'WIRE': 'built and tested but nothing runs it yet; ref names the item that finishes the job',
}
UNWIRED = ('TEST-ONLY', 'ORPHAN')
DEV_PREFIX = 'scripts/dev/'
INDEX_DOCS = {'MyTradingSys/system/03_FILE_INDEX.md', 'MyTradingSys/system/PROJECT_MAP.md',
              'MyTradingSys/system/LAYERS.md'}   # inventories name every file, so a mention there proves no one uses it
READER_JSON = {'MyTradingSys/system/artifacts/registry.json'}


def is_test(p):
    return bool(TEST_RE.search(p)) or '/tests/' in p or p.startswith('src/test/') or '/test/' in p


def _wanted(rel):
    parts = rel.split('/')
    if any(x in SKIP_DIRS for x in parts[:-1]):
        return False
    ext = os.path.splitext(rel)[1].lower()
    if ext not in CODE_EXT:
        return False
    if rel.startswith('runtime_data/') and ext not in ('.vbs', '.cmd', '.bat', '.ps1'):
        return False
    return True


def collect(root):
    """Tracked code files (git ls-files), so CI and a work tree agree; a plain walk when git is unavailable."""
    try:
        r = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, cwd=root, check=True)
        names = [n.decode('utf-8', 'replace') for n in r.stdout.split(NUL) if n]
        found = [n for n in names if _wanted(n) and os.path.exists(os.path.join(root, n))]
        if found:
            return found
    except (OSError, subprocess.CalledProcessError):
        pass
    out = []
    for d, dirs, files in os.walk(root):
        rel = os.path.relpath(d, root).replace(BACKSLASH, '/')
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            p = (rel + '/' + f) if rel != '.' else f
            if _wanted(p):
                out.append(p)
    return out


class ImportCache:
    """GATE_SPEED X4: the python imports of a file are a pure function of its text, so they are cached by content hash in the git common
    dir (shared by every worktree; 17 s of ast.parse, ast.walk and regex scans per run without it). A missing, unreadable or corrupt cache, or a root that is
    not a git repo (the tests' temp repos), means every file is parsed: the result never depends on the cache."""
    NAME = 'mts_wiring_facts_v2.json'
    CAP = 6000

    def __init__(self, root):
        self.path, self.rows, self.dirty = None, {}, False
        try:
            r = subprocess.run(['git', 'rev-parse', '--git-common-dir'], capture_output=True, text=True, cwd=root, timeout=20)
            if r.returncode == 0 and r.stdout.strip():
                common = r.stdout.strip()
                self.path = os.path.join(root, common) if not os.path.isabs(common) else common
                self.path = os.path.join(self.path, self.NAME)
                with open(self.path, encoding='utf-8') as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    self.rows = data
        except (OSError, ValueError, subprocess.SubprocessError):
            self.rows = {}
        self.used = set()

    def get(self, key):
        row = self.rows.get(key)
        if isinstance(row, dict) and all(k in row for k in ('imp', 'fr', 'mr')):
            self.used.add(key)
            return row
        return None

    def put(self, key, row):
        self.rows[key] = row
        self.used.add(key)
        self.dirty = True

    def save(self):
        if not self.path or not self.dirty:
            return
        try:
            rows = self.rows if len(self.rows) <= self.CAP else {k: self.rows[k] for k in self.used}
            tmp = f'{self.path}.{os.getpid()}.tmp'
            with open(tmp, 'w', encoding='utf-8', newline=chr(10)) as fh:
                json.dump(rows, fh)
            os.replace(tmp, self.path)
        except OSError:
            pass


FILE_REF = re.compile(r'[\w\-./\\]*?([\w\-]+\.(?:py|ps1|vbs|cmd|bat))')
MOD_REF = re.compile(r'\bMyTradingSys[.\\/][\w.\\/]+')


def file_facts(text, is_py, cache=None):
    """What one file says about others, a pure function of its text (so cacheable by content hash): 'imp' = [('I', dotted name) |
    ('F', module, level, [names])] of every import statement (nested ones too, ast.walk order), 'fr' = [[basename, path fragment]] of every
    script file name in it, 'mr' = [dotted MyTradingSys module names]. Only the resolution against the repo's files is left to build()."""
    import hashlib
    key = (hashlib.sha1(text.encode('utf-8', 'replace')).hexdigest() + ('p' if is_py else 'o')) if cache else None
    if cache:
        row = cache.get(key)
        if row is not None:
            return {'imp': [tuple(x) for x in row['imp']], 'fr': row['fr'], 'mr': row['mr']}
    imps = []
    if is_py:
        try:
            tree = ast.parse(text)
        except (SyntaxError, ValueError):
            tree = None
        for n in (ast.walk(tree) if tree else ()):
            if isinstance(n, ast.Import):
                imps.extend(('I', a.name) for a in n.names)
            elif isinstance(n, ast.ImportFrom):
                imps.append(('F', n.module or '', n.level or 0, [a.name for a in n.names]))
    fr = []
    for m in FILE_REF.finditer(text):
        item = [m.group(1), m.group(0).replace(BACKSLASH, '/').lstrip('./')]
        if item not in fr:
            fr.append(item)
    mr = []
    for m in MOD_REF.finditer(text):
        d = re.sub(r'[\\/]', '.', m.group(0)).rstrip('.')
        if d.endswith('.py'):
            d = d[:-3]
        if d not in mr:
            mr.append(d)
    if cache:
        cache.put(key, {'imp': [list(x) for x in imps], 'fr': fr, 'mr': mr})
    return {'imp': imps, 'fr': fr, 'mr': mr}


def build(root):
    code = collect(root)
    text = {}
    for p in code:
        try:
            with open(os.path.join(root, p), encoding='utf-8', errors='replace') as fh:
                text[p] = fh.read().replace(BACKSLASH + '.', '.')
        except OSError:
            text[p] = ''
    by_base = defaultdict(list)
    for p in code:
        by_base[os.path.basename(p)].append(p)
    dotted = {}
    for p in code:
        if p.endswith('.py'):
            d = p[:-3].replace('/', '.')
            dotted[d] = p
            if d.endswith('.__init__'):
                dotted[d[:-9]] = p
    java = {os.path.splitext(os.path.basename(p))[0]: p for p in code if p.endswith('.java')}
    edges = defaultdict(set)

    def add(a, b):
        if a != b:
            edges[a].add(b)

    suffixes = defaultdict(list)   # GATE_SPEED X4: dotted suffix -> files, so resolve() is a lookup, not a scan of every module per name
    for k, v in dotted.items():
        parts = k.split('.')
        for i in range(1, len(parts)):
            suffixes['.'.join(parts[i:])].append(v)
    memo = {}

    def resolve(name):
        if name in memo:
            return memo[name]
        parts, found = name.split('.'), None
        while parts:
            d = '.'.join(parts)
            if d in dotted:
                found = dotted[d]
                break
            c = suffixes.get(d, ())
            if len(c) == 1:
                found = c[0]
                break
            parts.pop()
        memo[name] = found
        return found

    cache = ImportCache(root)
    for p in code:
        t = text[p]
        facts = file_facts(t, p.endswith('.py'), cache)
        pkg = os.path.dirname(p).replace('/', '.')
        for imp in facts['imp']:
            if imp[0] == 'I':
                r = resolve(imp[1])
                if r:
                    add(p, r)
            else:
                _, module, level, names = imp
                base = module or ''
                if level:
                    up = pkg.split('.')
                    up = up[:len(up) - (level - 1)]
                    base = '.'.join(up + ([base] if base else []))
                r = resolve(base) if base else None
                if r:
                    add(p, r)
                for a in names:
                    r2 = resolve((base + '.' if base else '') + a)
                    if r2:
                        add(p, r2)
        for base, frag in facts['fr']:
            c = by_base.get(base, [])
            if len(c) == 1:
                add(p, c[0])
            elif len(c) > 1:
                for q in c:
                    if q.endswith(frag):
                        add(p, q)
        for d in facts['mr']:
            r = resolve(d)
            if r:
                add(p, r)
        if p.endswith('.java'):
            for cname, q in java.items():
                if q != p and re.search(r'\b' + re.escape(cname) + r'\b', t):
                    add(p, q)
        elif p.endswith(('.ps1', '.vbs', '.cmd', '.yml', '.yaml')) and 'datafeed.Main' in t:
            main_java = 'src/main/java/datafeed/Main.java'
            if main_java in text:
                add(p, main_java)
    cache.save()
    return code, edges


def reach(roots, edges, skip_tests):
    seen = set(roots)
    stack = list(roots)
    while stack:
        x = stack.pop()
        for y in edges.get(x, ()):
            if y in seen or (skip_tests and is_test(y)):
                continue
            seen.add(y)
            stack.append(y)
    return seen


def _is_reader_doc(rel):
    """An entry doc whose mention of a scripts/dev tool counts as a reader (not a dated note or a generated inventory)."""
    if rel in INDEX_DOCS:
        return False
    if rel in READER_JSON:
        return True
    if not rel.endswith('.md'):
        return False
    return (rel == 'CLAUDE.md' or rel.endswith('SKILL.md') or rel.startswith('scripts/sched/relay_prompts/')
            or (rel.startswith(('MyTradingSys/system/', 'MyTradingSys/runtime/')) and rel.count('/') == 2))


def reader_docs_text(root):
    try:
        r = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, cwd=root, check=True)
        names = [n.decode('utf-8', 'replace') for n in r.stdout.split(NUL) if n]
    except (OSError, subprocess.CalledProcessError):
        names = []
        for d, dirs, files in os.walk(root):
            rel = os.path.relpath(d, root).replace(BACKSLASH, '/')
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            names += [(rel + '/' + f) if rel != '.' else f for f in files]
    chunks = []
    for n in names:
        if _is_reader_doc(n):
            try:
                with open(os.path.join(root, n), encoding='utf-8', errors='replace') as fh:
                    chunks.append(fh.read())
            except OSError:
                pass
    return '\n'.join(chunks)


def dev_no_reader(root, code, edges):
    """Non-test scripts/dev files nobody reads: no other non-test code file references them and no entry doc names them.
    scripts/dev files are all roots, so classify() can never call them unwired."""
    referenced = set()
    for src, targets in edges.items():
        if not is_test(src):
            referenced.update(targets)
    docs = reader_docs_text(root)
    out = []
    for p in sorted(code):
        if not p.startswith(DEV_PREFIX) or is_test(p) or p in referenced:
            continue
        if re.search(r'(?<![\w\-])' + re.escape(os.path.basename(p)), docs):
            continue
        out.append(p)
    return out


def classify(root, built=None):
    code, edges = built or build(root)
    live_roots = [p for p in code if (p.startswith(LIVE_ROOT_PREFIX) or p in LIVE_ROOT_FILES) and not is_test(p)]
    dev_roots = [p for p in code if p.startswith('scripts/dev/') and not is_test(p)]
    test_roots = [p for p in code if is_test(p)]
    live = reach(live_roots, edges, True)
    dev = reach(dev_roots, edges, True)
    tested = reach(test_roots, edges, False)
    res = {}
    for p in code:
        if is_test(p):
            continue
        res[p] = 'LIVE' if p in live else 'DEV-TOOL' if p in dev else 'TEST-ONLY' if p in tested else 'ORPHAN'
    return res


def load_registry(root):
    try:
        with open(os.path.join(root, REGISTRY_PATH), encoding='utf-8') as fh:
            return json.load(fh).get('entries', {})
    except (OSError, ValueError):
        return {}


LAB_PREFIX = 'MyTradingSys/research/layer_lab/'
RESEARCH_PREFIX = 'MyTradingSys/research/'


def p_in_research(p):
    return p.startswith(RESEARCH_PREFIX)


def check(res, registry):
    """Errors for the gate. Every unwired file must be declared; a declaration must still be true."""
    errors = []
    # Study folders hold run-once repro scripts, not production code: declaring each one cost ~68 registry commits in 72 h
    # (2026-10-17 audit) and the shared JSON was a merge-conflict hot spot. They are listed by --check as NOTE, never FAIL.
    for p in sorted(k for k, v in res.items() if v in UNWIRED and k not in registry and not p_in_research(k)):
        errors.append('UNDECLARED %s: %s, referenced by %s. Wire it, archive it (git mv to MyTradingSys/archive/), '
                      'or add it to %s with a disposition and a reason.'
                      % (res[p], p, 'tests only' if res[p] == 'TEST-ONLY' else 'nothing', REGISTRY_PATH))
    for p, e in sorted(registry.items()):
        if p not in res:
            if not p_in_research(p):
                errors.append('STALE %s: file is gone or is not code; remove the entry.' % p)
            continue
        if res[p] not in UNWIRED:
            if p_in_research(p):
                continue  # a study script that later got run by something: harmless, not worth failing a ship
            if p.startswith(LAB_PREFIX):
                continue  # lab declares TOOL/REPRO, then lists the test in run_extra_tests (-> LIVE); not worth failing the lab ship
            errors.append('STALE %s: now %s (something runs it); remove the entry.' % (p, res[p]))
        if not isinstance(e, dict) or e.get('disp') not in DISPOSITIONS:
            errors.append('BAD %s: disp must be one of %s.' % (p, sorted(DISPOSITIONS)))
            continue
        if not str(e.get('why', '')).strip():
            errors.append('BAD %s: why is empty.' % p)
        if e['disp'] == 'WIRE' and not str(e.get('ref', '')).strip():
            errors.append('BAD %s: WIRE needs ref (the item that finishes the wiring).' % p)
    return errors


def last_commit(root, p):
    try:
        r = subprocess.run(['git', 'log', '-1', '--format=%ad', '--date=short', '--', p],
                           capture_output=True, text=True, cwd=root)
        return r.stdout.strip()
    except OSError:
        return ''


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json')
    ap.add_argument('--md')
    ap.add_argument('--check', action='store_true', help='exit 1 on undeclared unwired files or stale declarations')
    ap.add_argument('--root', default=ROOT)
    a = ap.parse_args(argv)
    built = build(a.root)
    res = classify(a.root, built)
    counts = defaultdict(int)
    for v in res.values():
        counts[v] += 1
    print(dict(counts))
    no_reader = dev_no_reader(a.root, built[0], built[1])
    if a.json:
        with open(a.json, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.md:
        reg = load_registry(a.root)
        lines = ['# WIRING SCAN', '', 'Generated by scripts/dev/wiring_scan.py. Counts: ' +
                 ', '.join('%s %d' % (k, counts[k]) for k in sorted(counts)), '']
        for cls in UNWIRED:
            lines += ['## ' + cls, '', '| file | declared | last commit |', '|---|---|---|']
            for p in sorted(k for k, v in res.items() if v == cls):
                lines.append('| %s | %s | %s |' % (p, reg.get(p, {}).get('disp', '-'), last_commit(a.root, p)))
            lines.append('')
        lines += ['## NO-READER (scripts/dev, warn only)', ''] + ['- ' + p for p in no_reader] + ['']
        with open(a.md, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('\n'.join(lines))
    if a.check:
        errors = check(res, load_registry(a.root))
        for e in errors:
            print('FAIL:', e)
        if no_reader:
            print('WARN NO-READER (%d scripts/dev files nobody reads; archive or document the reader): %s'
                  % (len(no_reader), ', '.join(os.path.basename(p) for p in no_reader)))
        print('wiring check:', 'FAIL' if errors else 'PASS')
        return 1 if errors else 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
