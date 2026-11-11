counts MATCH=7 DIFF=1 NOT_IN_DATA=0

# Blind Read Report: scripts/dev/prereg_context_lint.py against Docstring and Tests

Date: 2026-11-11
Auditor: Gemini (independent blind read)
Target: `scripts/dev/prereg_context_lint.py`
Scope: SOURCED from `scripts/dev/prereg_context_lint.py` and `scripts/dev/test_prereg_context_lint.py`.

## Clause Comparison Table

| Clause # | Docstring Claim (Quote & file:line) | Implementation / Test Verification (Quote & file:line) | Status | Notes |
|:---|:---|:---|:---|:---|
| 1 | "every NEW pre-registration states its market context, every NEW result states its window's regime mix." (`scripts/dev/prereg_context_lint.py:2`) | Checked via `lint()` looping over unallowed `prereg_files()` and child `result_files()`: `scripts/dev/prereg_context_lint.py:69-79`; tested in `scripts/dev/test_prereg_context_lint.py:21-49`. | MATCH | Both PRE_REG context and result regime mix are enforced for new (unallowed) files. |
| 2 | "This is a GATE (exit 1 on an offender), not a report" (`scripts/dev/prereg_context_lint.py:7`) | `if offenders: ... return 1` (`scripts/dev/prereg_context_lint.py:104-107`); `sys.exit(main())` (`scripts/dev/prereg_context_lint.py:112`); tested in `scripts/dev/test_prereg_context_lint.py:31` (`self.assertEqual(lint.main(...), 1)`). | MATCH | Returns exit code 1 when offenders list is non-empty; returns 0 on clean run. |
| 3 | "A `PRE_REG*.md` under MyTradingSys/research that is not in the allowlist (the studies frozen before this rule) must carry a `## Context` section" (`scripts/dev/prereg_context_lint.py:9-10`) | `SCAN = "MyTradingSys/research"` (`scripts/dev/prereg_context_lint.py:23`); `base.rglob("PRE_REG*.md")` with `_archive` excluded (`scripts/dev/prereg_context_lint.py:34`); `CONTEXT_HEAD = re.compile(r"^##+\s*Context\b", re.M | re.I)` (`scripts/dev/prereg_context_lint.py:25`); skipped if `rel in allow` (`scripts/dev/prereg_context_lint.py:71-72`). | MATCH | Implementation scans `MyTradingSys/research/**/PRE_REG*.md` (excluding `_archive`) and requires `## Context` header unless allowlisted. |
| 4 | "four lines `Regime:`, `Phase:`, `Session:`, `Entry:`; each line names the gate used, or says `none, because ...`." (`scripts/dev/prereg_context_lint.py:10-11`) | `LINES = ("Regime:", "Phase:", "Session:", "Entry:")` (`scripts/dev/prereg_context_lint.py:26`); regex checks `^\s*(?:[-*]\s*)?(?:\*\*)?<key>:\s*\S` (`scripts/dev/prereg_context_lint.py:47`); tested in `scripts/dev/test_prereg_context_lint.py:33-37`. | MATCH | Implementation requires all 4 lines to have non-whitespace content (`\S`), accepting values like `none, because ...`. |
| 5 | "Writing "none" is allowed; forgetting to decide is not." (`scripts/dev/prereg_context_lint.py:11`) | Empty value check `\s*:\s*\S` fails when key has no value (`scripts/dev/test_prereg_context_lint.py:37`); non-empty strings like `none, because daily` pass (`scripts/dev/test_prereg_context_lint.py:34-36`). | MATCH | Content following the colon is required; "none" is treated as valid non-empty content. |
| 6 | "A `RESULT*.md` or `DEV_CHECK*.md` in the same folder as such a PRE_REG must carry a `Regime mix:` line (bull / bear / range share of the window, or NOT_IN_DATA with the reason)." (`scripts/dev/prereg_context_lint.py:12-13`) | `result_files(folder)` glob: `p.name.startswith(("RESULT", "DEV_CHECK"))` (`scripts/dev/prereg_context_lint.py:53`); regex: `REGIME_MIX = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?Regime mix(?:\*\*)?\s*:", re.M | re.I)` (`scripts/dev/prereg_context_lint.py:27`); tested in `scripts/dev/test_prereg_context_lint.py:39-49`. | DIFF | Docstring claims the line must specify "bull / bear / range share of the window, or NOT_IN_DATA with the reason", but regex `REGIME_MIX` only checks for the presence of the `Regime mix:` label/header, not its contents or semantic breakdown. |
| 7 | "--write-allow rewrites the allowlist from the PRE_REG files present now (used once, 2026-11-04)." (`scripts/dev/prereg_context_lint.py:15`) | `if a.write_allow: rows = [p.relative_to(root).as_posix() for p in prereg_files(root)]` (`scripts/dev/prereg_context_lint.py:91-95`); tested in `scripts/dev/test_prereg_context_lint.py:57-58`. | MATCH | `--write-allow` writes the paths of current `prereg_files(root)` prefixed by `path\n` header to `a.allow` and exits with code 0. |
| 8 | "The allowlist is scripts/dev/prereg_context_lint_allow.tsv (one path per line). Stale rows (files gone) are reported, never fatal." (`scripts/dev/prereg_context_lint.py:15-16`) | `DEFAULT_ALLOW = Path(__file__).resolve().parent / "prereg_context_lint_allow.tsv"` (`scripts/dev/prereg_context_lint.py:24`); `stale = sorted(a for a in allow if a not in rels)` (`scripts/dev/prereg_context_lint.py:80`); stale lines printed as `STALE allow row (file gone):` (`scripts/dev/prereg_context_lint.py:103`); exit code remains 0 if no offenders (`scripts/dev/prereg_context_lint.py:107-108`); tested in `scripts/dev/test_prereg_context_lint.py:60-61`. | MATCH | Stale rows are detected and printed, but do not contribute to `offenders`, hence exit code is 0 (never fatal). |

## Summary of Findings

1. **Glob & Scan**:
   - Scans `root / "MyTradingSys/research"` for `PRE_REG*.md`, omitting any path containing `_archive` in relative parts (`scripts/dev/prereg_context_lint.py:23,34`).
   - Sibling result files matching prefix `RESULT` or `DEV_CHECK` ending in `.md` are scanned (`scripts/dev/prereg_context_lint.py:53`).
2. **Offenders**:
   - Any `PRE_REG*.md` not present in the allowlist missing `## Context` or missing any of the 4 required lines (`Regime:`, `Phase:`, `Session:`, `Entry:`) with non-empty values (`scripts/dev/prereg_context_lint.py:47-49,74-76`).
   - Any sibling `RESULT*.md` or `DEV_CHECK*.md` missing the line prefix `Regime mix:` (`scripts/dev/prereg_context_lint.py:27,77-79`).
3. **Allow TSV**:
   - TSV file default is `scripts/dev/prereg_context_lint_allow.tsv` (`scripts/dev/prereg_context_lint.py:24`).
   - One path per line (ignores empty lines and header line `"path"`) (`scripts/dev/prereg_context_lint.py:58`).
   - Stale rows are reported on stdout but do not trigger exit code 1 (`scripts/dev/prereg_context_lint.py:80,103,107-108`).
4. **Exit Codes**:
   - Exit code 1 if `offenders` is non-empty (`scripts/dev/prereg_context_lint.py:107`).
   - Exit code 0 if `offenders` is empty or when `--write-allow` completes (`scripts/dev/prereg_context_lint.py:95,108`).
