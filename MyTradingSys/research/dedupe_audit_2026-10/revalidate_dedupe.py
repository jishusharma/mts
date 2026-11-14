"""Reproduces every count in IMPLEMENTATION_PLAN_2026-11-14.md from the checked-out tree (read-only, no network).
Run from the repo root:  python MyTradingSys/research/dedupe_audit_2026-10/revalidate_dedupe.py [--json]
Each line is `KEY = value`; the plan quotes these keys."""
import ast, collections, hashlib, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
SYS = ROOT / "MyTradingSys" / "system"


def tracked():
    return subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines()


def card_counts():
    c = collections.Counter()
    for f in (SYS / "tasks").glob("*.json"):
        try:
            c[json.loads(f.read_text(encoding="utf-8")).get("state")] += 1
        except ValueError:
            c["unparsable"] += 1
    return c


def research_dup_py(files):
    """Byte-identical .py files under MyTradingSys/research/ with the same sha256 -> {hash: [paths]}."""
    h = collections.defaultdict(list)
    for f in files:
        if f.startswith("MyTradingSys/research/") and f.endswith(".py"):
            h[hashlib.sha256((ROOT / f).read_bytes()).hexdigest()].append(f)
    return {k[:16]: v for k, v in h.items() if len(v) > 1}


def shared_test_basenames(files):
    a = {Path(f).name for f in files if f.startswith("scripts/dev/test_") and f.endswith(".py")}
    b = {Path(f).name for f in files if f.startswith("MyTradingSys/tests/test_") and f.endswith(".py")}
    return sorted(a & b)


def ast_dups(files, prefix, names):
    """For each function name: groups of files whose def has an identical ast.dump body (docstring included, name included)."""
    out = {}
    for n in names:
        g = collections.defaultdict(list)
        for f in files:
            if not (f.startswith(prefix) and f.endswith(".py")):
                continue
            try:
                tree = ast.parse((ROOT / f).read_text(encoding="utf-8"))
            except (SyntaxError, ValueError, OSError):
                continue
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == n:
                    g[ast.dump(node)].append(f"{f}:{node.lineno}")
        out[n] = sorted((sorted(v) for v in g.values()), key=len, reverse=True)
    return out


def index_false_rows():
    """INDEX.md indicator rows marked PARTIAL/MISSING while <ROW_FILE>.md exists with all 8 template sections (rows 7-8 of the old plan, STOCH_RSI and
    TREND_LINES, are already DONE in INDEX.md, so they are not counted)."""
    rb = ROOT / "MyTradingSys" / "research" / "indicator_rulebooks"
    row_file = {"rsi": "RSI.md", "moving averages": "MOVING_AVERAGES.md", "cvd": "CVD.md", "funding": "FUNDING_LS.md",
                "hilega": "HILEGA_MILEGA.md", "stochastic rsi": "STOCH_RSI.md", "trend lines": "TREND_LINES.md"}
    out = []
    for ln in (rb / "INDEX.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in ln.split("|")]
        if len(cells) > 5 and cells[4] in ("PARTIAL", "MISSING"):
            for key, fn in row_file.items():
                f = rb / fn
                if cells[1].lower().startswith(key) and f.is_file() and len(set(re.findall(r"^## ([1-8])\.", f.read_text(encoding="utf-8"), re.M))) == 8:
                    out.append((cells[1], cells[4], fn))
    return out


def const_count(files, const):
    return sorted(f for f in files if f.startswith("scripts/dev/") and f.endswith(".py")
                  and re.search(rf"^{const}\s*=", (ROOT / f).read_text(encoding="utf-8"), re.M))


def main():
    files = tracked()
    cc = card_counts()
    closed = cc["done"] + cc["dropped"]
    dup = research_dup_py(files)
    red = sum(len(v) - 1 for v in dup.values())
    res = {
        "cards_total": sum(cc.values()), "cards_by_state": dict(cc), "cards_closed_done_plus_dropped": closed,
        "research_dup_groups": {k: v for k, v in dup.items()}, "research_dup_group_count": len(dup), "research_redundant_copies": red,
        "shared_test_basenames": shared_test_basenames(files),
        "ast_identical_dev": ast_dups(files, "scripts/dev/", ["utcnow", "iso_now", "_flags"]),
        "index_rows_false": index_false_rows(),
        "LIVE_MARKER_files": const_count(files, "LIVE_MARKER"),
        "pid_alive_defs": subprocess.run(["git", "-C", str(ROOT), "grep", "-n", "^def pid_alive", "--", "scripts/dev/*.py"], capture_output=True, text=True).stdout.splitlines(),
        "lookahead_allowlist_lines": len((ROOT / "scripts/dev/lookahead_allowlist.tsv").read_text(encoding="utf-8").splitlines()),
    }
    if "--json" in sys.argv:
        print(json.dumps(res, indent=1, default=str))
        return
    for k, v in res.items():
        if k == "ast_identical_dev":
            for n, groups in v.items():
                print(f"AST_{n} = " + " | ".join(f"{len(g)}x" for g in groups))
        elif isinstance(v, (list, dict)) and k not in ("cards_by_state",):
            print(f"{k} = {len(v)}  {v if len(str(v)) < 700 else ''}")
        else:
            print(f"{k} = {v}")


if __name__ == "__main__":
    main()
