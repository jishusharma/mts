"""Static look-ahead lint for research and backtest scripts.

  python scripts/dev/lookahead_lint.py                 table of every hit (file:line, pattern, FAIL/WARN, allowlisted?) + counts
  python scripts/dev/lookahead_lint.py --new           only hits that are not in the allowlist
  python scripts/dev/lookahead_lint.py --update-baseline   add every unlisted hit to the allowlist as "pre-existing, unreviewed"
  exit code 1 when a FAIL hit is not allowlisted (WARN hits never fail the run)

Scans MyTradingSys/research/**/*.py and MyTradingSys/backtest/**/*.py (AST based, no code is run). Patterns:

  rolling-center         FAIL  .rolling(..., center=True): every value sees half a window of the future
  shift-negative         FAIL  .shift(-k) / np.roll(x, -k) / diff(-k) / pct_change(-k), unless the statement assigns a name,
                               column or keyword like fwd / forward / outcome / ret(urn) / exit, or sits in a function so named
  fwd-index              FAIL  x[i+k] (k > 0 or a name), x[i+1:], x[:i+k] (k > 1) under the same exemption; x[:i+1] is not a hit
  pivot-right-neighbour  FAIL  one expression reads x[i-a] and x[i+b] of the same series: a pivot whose right neighbour can be the
                               decision bar (the setup_alpha_beta_2026-10-10 sweep study, line 177: i+1 of the last bar of the previous day)
  fullsample-quantile    WARN  quantile / percentile / qcut over a whole array or frame used for an arm or threshold. OURS-on-DEV
                               and acceptable only if the cut-offs are frozen before VALIDATION; rolling/expanding and sliced
                               windows are not hits
  pivot-function         WARN  scipy argrelextrema / find_peaks (symmetric window: valid only with a confirmation delay)
  parse-error            WARN  the file does not parse

A hit is allowlisted when scripts/dev/lookahead_allowlist.tsv has a row with the same file, pattern and normalized source line
(so a line moving does not break the match). Rows carry the reason; "pre-existing, unreviewed" is the baseline, and a human
review replaces it with the real reason. Rows that no longer match any hit are reported as stale.

Not scanned: research/pit_levels_2026-10-16 and research/context_null_2026-10-16 (other sessions own them; pit_levels holds
deliberately leaky builders as test fixtures).
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALLOWLIST = Path(__file__).resolve().parent / "lookahead_allowlist.tsv"
SCAN_ROOTS = ("MyTradingSys/research", "MyTradingSys/backtest")
EXCLUDE_DIRS = ("MyTradingSys/research/pit_levels_2026-10-16", "MyTradingSys/research/context_null_2026-10-16")
BASELINE_REASON = "pre-existing, unreviewed"

EXEMPT_TOKENS = {"fwd", "forward", "outcome", "outcomes", "ret", "rets", "return", "returns", "exit", "exits"}
QUANTILE_FUNCS = {"quantile", "nanquantile", "percentile", "nanpercentile", "qcut"}
WINDOW_METHODS = {"rolling", "expanding", "ewm"}
SEVERITY = {"rolling-center": "FAIL", "shift-negative": "FAIL", "fwd-index": "FAIL", "pivot-right-neighbour": "FAIL",
            "fullsample-quantile": "WARN", "pivot-function": "WARN", "parse-error": "WARN"}


class Hit:
    def __init__(self, file, line, pattern, text):
        self.file, self.line, self.pattern, self.text = file, line, pattern, text
        self.severity = SEVERITY[pattern]
        self.reason = None                      # set when allowlisted

    @property
    def key(self):
        return (self.file, self.pattern, self.text)

    @property
    def allowlisted(self):
        return self.reason is not None

    def as_dict(self):
        return {"file": self.file, "line": self.line, "pattern": self.pattern, "severity": self.severity,
                "allowlisted": self.allowlisted, "reason": self.reason, "text": self.text}


def norm(text):
    return " ".join(text.split())


def _tokens(name):
    return [t.lower() for t in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", name)]


def _exempt_name(name):
    return any(t in EXEMPT_TOKENS for t in _tokens(name))


def _names_in(expr):
    """Identifiers, attribute names and string keys appearing in an expression (for the name exemption)."""
    out = []
    for n in ast.walk(expr):
        if isinstance(n, ast.Name):
            out.append(n.id)
        elif isinstance(n, ast.Attribute):
            out.append(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return out


def _parents(tree):
    par = {}
    for node in ast.walk(tree):
        for ch in ast.iter_child_nodes(node):
            par[ch] = node
    return par


def _context_names(node, par):
    """Names that label what this node computes: assignment targets, keyword names, dict keys, enclosing function names."""
    names = []
    cur, prev = node, None
    stmt_done = False
    while cur is not None:
        if isinstance(cur, ast.keyword) and cur.arg:
            names.append(cur.arg)
        elif isinstance(cur, ast.Dict) and prev is not None:
            for k, v in zip(cur.keys, cur.values):
                if v is prev and k is not None:
                    names += _names_in(k)
        elif isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(cur.name)
        elif isinstance(cur, ast.stmt) and not stmt_done:
            stmt_done = True
            if isinstance(cur, ast.Assign):
                for t in cur.targets:
                    names += _names_in(t)
            elif isinstance(cur, (ast.AugAssign, ast.AnnAssign)):
                names += _names_in(cur.target)
        prev, cur = cur, par.get(cur)
    return names


def _context_exempt(node, par, extra=()):
    return any(_exempt_name(n) for n in list(_context_names(node, par)) + list(extra))


def _neg(expr):
    if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.USub):
        return True
    return isinstance(expr, ast.Constant) and isinstance(expr.value, (int, float)) and expr.value < 0


def _offset(expr):
    """(variable, effective offset) of an index expression like i, i+1, i-w, i+w+1; None when it has no index variable."""
    terms = []

    def flat(e, sign):
        if isinstance(e, ast.BinOp) and isinstance(e.op, (ast.Add, ast.Sub)):
            flat(e.left, sign)
            flat(e.right, sign if isinstance(e.op, ast.Add) else -sign)
        else:
            terms.append((e, sign))

    flat(expr, 1)
    var, k = None, 0
    for e, sign in terms:
        if isinstance(e, ast.Constant) and isinstance(e.value, int):
            k += sign * e.value
        elif isinstance(e, ast.Name):
            if var is None:
                var = e.id if sign > 0 else None
                if var is None:
                    return None
            else:
                k += 2 * sign                     # a second name (k, w, h) counts as a step of at least 2 in its direction
        else:
            return None
    return (var, k) if var else None


def _index_items(sub):
    """(kind, expr) for each index expression of a Subscript: kind 'idx', 'lo' or 'hi' (Slice bounds)."""
    sl = sub.slice
    parts = sl.elts if isinstance(sl, ast.Tuple) else [sl]
    out = []
    for p in parts:
        if isinstance(p, ast.Slice):
            if p.lower is not None:
                out.append(("lo", p.lower))
            if p.upper is not None:
                out.append(("hi", p.upper))
        else:
            out.append(("idx", p))
    return out


def _effective(kind, off):
    """Offset of the last/first bar actually touched: an exclusive upper bound i+1 reaches bar i only."""
    return off - 1 if kind == "hi" else off


def _scan_tree(tree, lines, rel):
    hits = []
    par = _parents(tree)

    def add(node, pattern):
        ln = getattr(node, "lineno", 1)
        hits.append(Hit(rel, ln, pattern, norm(lines[ln - 1]) if 0 < ln <= len(lines) else ""))

    pivot_nodes = set()
    # pivots: per expression root of each statement, one series read at an index left and right of the same variable
    for stmt in (n for n in ast.walk(tree) if isinstance(n, ast.stmt)):
        for root in (c for c in ast.iter_child_nodes(stmt) if isinstance(c, ast.expr)):
            seen = {}
            for sub in (n for n in ast.walk(root) if isinstance(n, ast.Subscript)):
                base = ast.dump(sub.value)
                for kind, e in _index_items(sub):
                    o = _offset(e)
                    if o is None:
                        continue
                    seen.setdefault((base, o[0]), []).append((_effective(kind, o[1]), sub))
            for items in seen.values():
                if any(k < 0 for k, _ in items):
                    for k, sub in items:
                        if k > 0 and sub not in pivot_nodes:
                            pivot_nodes.add(sub)
                            add(sub, "pivot-right-neighbour")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else None)
            if name == "rolling":
                for kw in node.keywords:
                    if kw.arg == "center" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        add(node, "rolling-center")
            if name in ("shift", "roll", "diff", "pct_change"):
                arg = None
                if name == "roll":
                    arg = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == "shift"), None)
                else:
                    arg = node.args[0] if node.args else next((k.value for k in node.keywords if k.arg == "periods"), None)
                if arg is not None and _neg(arg) and not _context_exempt(node, par):
                    add(node, "shift-negative")
            if name in QUANTILE_FUNCS:
                chain, windowed = fn.value if isinstance(fn, ast.Attribute) else None, False
                while isinstance(chain, (ast.Call, ast.Attribute)):
                    if isinstance(chain, ast.Call) and isinstance(chain.func, ast.Attribute) and chain.func.attr in WINDOW_METHODS:
                        windowed = True
                    chain = chain.func if isinstance(chain, ast.Call) else chain.value
                bounded = any(isinstance(s, ast.Subscript) and any(k == "hi" for k, _ in _index_items(s))
                              for a in list(node.args) + ([fn.value] if isinstance(fn, ast.Attribute) else [])
                              for s in ast.walk(a))
                if not windowed and not bounded:
                    add(node, "fullsample-quantile")
            if name in ("argrelextrema", "find_peaks", "find_peaks_cwt"):
                add(node, "pivot-function")
        elif isinstance(node, ast.Subscript) and node not in pivot_nodes:
            for kind, e in _index_items(node):
                o = _offset(e)
                if o is None or _effective(kind, o[1]) <= 0:
                    continue
                if _context_exempt(node, par, _names_in(node.value)):
                    continue
                add(node, "fwd-index")
                break
    return hits


def scan_source(text, rel):
    """Hits of one file's source text (allowlist not applied)."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError) as e:
        return [Hit(rel, getattr(e, "lineno", 1) or 1, "parse-error", norm(str(e))[:80])]
    hits = _scan_tree(tree, text.splitlines(), rel)
    seen, out = set(), []
    for h in sorted(hits, key=lambda h: (h.line, h.pattern)):
        if (h.line, h.pattern) not in seen:
            seen.add((h.line, h.pattern))
            out.append(h)
    return out


def iter_files(root=REPO):
    for sr in SCAN_ROOTS:
        base = root / sr
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.py")):
            rel = p.relative_to(root).as_posix()
            if any(rel.startswith(e + "/") for e in EXCLUDE_DIRS) or "__pycache__" in rel:
                continue
            yield p, rel


def scan_tree(root=REPO):
    hits = []
    for p, rel in iter_files(root):
        hits += scan_source(p.read_text(encoding="utf-8", errors="replace"), rel)
    return hits


def load_allowlist(path=ALLOWLIST):
    """{(file, pattern, text): reason}. Tab separated; lines starting with # are comments."""
    out = {}
    if not Path(path).exists():
        return out
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        parts = ln.split("\t")
        if len(parts) >= 4:
            out[(parts[0], parts[1], parts[2])] = parts[3]
    return out


def write_allowlist(entries, path=ALLOWLIST):
    head = ["# lookahead_lint allowlist: file<TAB>pattern<TAB>normalized source line<TAB>reason",
            "# Replace 'pre-existing, unreviewed' with the real reason once a hit is reviewed. Generated rows come from",
            "# `python scripts/dev/lookahead_lint.py --update-baseline`; a row matches by text, not by line number."]
    body = [f"{k[0]}\t{k[1]}\t{k[2]}\t{entries[k]}" for k in sorted(entries)]
    Path(path).write_text("\n".join(head + body) + "\n", encoding="utf-8", newline="\n")


def apply_allowlist(hits, allow):
    for h in hits:
        h.reason = allow.get(h.key)
    return hits


def summarize(hits, allow):
    """Counts from the parsed hit objects (never from printed output)."""
    keys = {h.key for h in hits}
    return {
        "hits": len(hits),
        "FAIL": sum(h.severity == "FAIL" for h in hits),
        "WARN": sum(h.severity == "WARN" for h in hits),
        "FAIL_allowlisted": sum(h.severity == "FAIL" and h.allowlisted for h in hits),
        "FAIL_new": sum(h.severity == "FAIL" and not h.allowlisted for h in hits),
        "WARN_allowlisted": sum(h.severity == "WARN" and h.allowlisted for h in hits),
        "WARN_new": sum(h.severity == "WARN" and not h.allowlisted for h in hits),
        "stale_allowlist_rows": sum(1 for k in allow if k not in keys),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--new", action="store_true", help="only hits not in the allowlist")
    ap.add_argument("--json", action="store_true", help="JSON rows instead of the table")
    ap.add_argument("--update-baseline", action="store_true", help="append unlisted hits to the allowlist as pre-existing, unreviewed")
    ap.add_argument("--allowlist", default=str(ALLOWLIST))
    args = ap.parse_args(argv)
    hits = scan_tree()
    allow = load_allowlist(args.allowlist)
    apply_allowlist(hits, allow)
    if args.update_baseline:
        for h in hits:
            allow.setdefault(h.key, BASELINE_REASON)
        write_allowlist(allow, args.allowlist)
        apply_allowlist(hits, allow)
    rows = [h for h in hits if not (args.new and h.allowlisted)]
    if args.json:
        print(json.dumps([h.as_dict() for h in rows], indent=1))
    else:
        for h in rows:
            print(f"{h.file}:{h.line}\t{h.pattern}\t{h.severity}\t{'allowlisted' if h.allowlisted else 'NEW'}\t{h.text[:100]}")
    s = summarize(hits, allow)
    print(f"lookahead_lint: {s['hits']} hits = {s['FAIL']} FAIL ({s['FAIL_allowlisted']} allowlisted, {s['FAIL_new']} new) + "
          f"{s['WARN']} WARN ({s['WARN_allowlisted']} allowlisted, {s['WARN_new']} new); {s['stale_allowlist_rows']} stale allowlist rows",
          file=sys.stderr if args.json else sys.stdout)
    return 1 if s["FAIL_new"] else 0


if __name__ == "__main__":
    sys.exit(main())
