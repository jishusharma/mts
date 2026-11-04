#!/usr/bin/env python3
"""prereg_context_lint.py - every NEW pre-registration states its market context, every NEW result states its window's regime mix.

    python scripts/dev/prereg_context_lint.py [--root <repo>] [--allow <tsv>] [--write-allow]

Operator 2026-11-04 (d-context-retest-1104): 10 of 33 backtests tested a bare trigger in every regime, and only 4 of 33 reports say
what regime their window was (CONTEXT_FILTER_REVIEW_2026-11-04.md). This is a GATE (exit 1 on an offender), not a report:

* A `PRE_REG*.md` under MyTradingSys/research that is not in the allowlist (the studies frozen before this rule) must carry a
  `## Context` section with four lines `Regime:`, `Phase:`, `Session:`, `Entry:`; each line names the gate used, or says
  `none, because ...`. Writing "none" is allowed; forgetting to decide is not.
* A `RESULT*.md` or `DEV_CHECK*.md` in the same folder as such a PRE_REG must carry a `Regime mix:` line (bull / bear / range share of
  the window, or NOT_IN_DATA with the reason).

--write-allow rewrites the allowlist from the PRE_REG files present now (used once, 2026-11-04). The allowlist is scripts/dev/
prereg_context_lint_allow.tsv (one path per line). Stale rows (files gone) are reported, never fatal.
"""
import argparse
import re
import sys
from pathlib import Path

SCAN = "MyTradingSys/research"
DEFAULT_ALLOW = Path(__file__).resolve().parent / "prereg_context_lint_allow.tsv"
CONTEXT_HEAD = re.compile(r"^##+\s*Context\b", re.M | re.I)
LINES = ("Regime:", "Phase:", "Session:", "Entry:")
REGIME_MIX = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?Regime mix(?:\*\*)?\s*:", re.M | re.I)


def prereg_files(root):
    base = root / SCAN
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("PRE_REG*.md") if "_archive" not in p.relative_to(root).parts)


def context_missing(text):
    """Names of the context lines missing from the `## Context` section; all four when the section is absent."""
    m = CONTEXT_HEAD.search(text)
    if not m:
        return list(LINES)
    rest = text[m.end():]
    nxt = re.search(r"^##\s", rest, re.M)
    section = rest[: nxt.start()] if nxt else rest
    missing = []
    for key in LINES:
        if not re.search(r"^\s*(?:[-*]\s*)?(?:\*\*)?" + re.escape(key[:-1]) + r"(?:\*\*)?\s*:\s*\S", section, re.M | re.I):
            missing.append(key)
    return missing


def result_files(folder):
    return sorted(p for p in folder.glob("*.md") if p.name.startswith(("RESULT", "DEV_CHECK")))


def read_allow(path):
    try:
        return {ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip() and ln.strip() != "path"}
    except OSError:
        return set()


def lint(root, allow):
    """Return (offenders, stale): offenders = list of (rel path, problem); stale = allowlist rows with no file."""
    root = Path(root)
    files = prereg_files(root)
    rels = {p.relative_to(root).as_posix() for p in files}
    offenders = []
    for p in files:
        rel = p.relative_to(root).as_posix()
        if rel in allow:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        miss = context_missing(text)
        if miss:
            offenders.append((rel, "PRE_REG without a `## Context` line for: " + ", ".join(miss)))
        for r in result_files(p.parent):
            if not REGIME_MIX.search(r.read_text(encoding="utf-8", errors="replace")):
                offenders.append((r.relative_to(root).as_posix(), "result without a `Regime mix:` line"))
    stale = sorted(a for a in allow if a not in rels)
    return offenders, stale


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--allow", default=str(DEFAULT_ALLOW))
    ap.add_argument("--write-allow", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.root)
    if a.write_allow:
        rows = [p.relative_to(root).as_posix() for p in prereg_files(root)]
        Path(a.allow).write_text("path\n" + "\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        print(f"allowlist written: {len(rows)} PRE_REG files frozen before the context rule")
        return 0
    allow = read_allow(a.allow)
    offenders, stale = lint(root, allow)
    checked = len(prereg_files(root)) - len(allow & {p.relative_to(root).as_posix() for p in prereg_files(root)})
    print(f"prereg context lint: {checked} new PRE_REG checked, {len(offenders)} offender(s), {len(stale)} stale allow row(s)")
    for rel, why in offenders:
        print(f"  FAIL {rel}: {why}")
    for rel in stale:
        print(f"  STALE allow row (file gone): {rel}")
    if offenders:
        print("  fix: add `## Context` with Regime:/Phase:/Session:/Entry: lines to the PRE_REG (say `none, because ...` when a gate is "
              "deliberately absent) and a `Regime mix:` line to the result; see CONTEXT_FILTER_REVIEW_2026-11-04.md")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
