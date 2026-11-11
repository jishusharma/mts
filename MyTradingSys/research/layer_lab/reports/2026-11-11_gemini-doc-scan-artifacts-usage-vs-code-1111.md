COUNTS: MATCH=8 DIFF=2 NOT_IN_DATA=0

# Audit Report: `artifacts.py` Usage Text vs Argparse Definitions & Implementation

- **Card**: `gemini-doc-scan-artifacts-usage-vs-code-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `scripts/dev/artifacts.py` (read)
  - `scripts/dev/test_artifacts.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-artifacts-usage-vs-code-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Scan

Evaluated 10 usage claims from the top docstring / usage block of `scripts/dev/artifacts.py` (lines 3-12) against the `argparse` definitions (lines 484-491), runtime command handlers (lines 492-555), helper functions, and test behaviors in `scripts/dev/test_artifacts.py`:
1. `check`: `python scripts/dev/artifacts.py check` (line 3)
2. `list`: `python scripts/dev/artifacts.py list` (line 4)
3. `plan`: `python scripts/dev/artifacts.py plan --account jishu.sharma` (line 5)
4. `build`: `python scripts/dev/artifacts.py build` (line 6)
5. `stale`: `python scripts/dev/artifacts.py stale` (line 7)
6. `publish-record`: `python scripts/dev/artifacts.py publish-record --slug X [--date YYYY-MM-DD]` (line 8)
7. `stamp`: `python scripts/dev/artifacts.py stamp --file page.html` (line 9)
8. `republish`: `python scripts/dev/artifacts.py republish` (line 10)
9. `banner`: `python scripts/dev/artifacts.py banner --slug research_map [--file live.html]` (line 11)
10. `audit-links`: `python scripts/dev/artifacts.py audit-links` (line 12)

Audit outcome across 10 claims:
- **MATCH (8)**: Commands and flags accurately match their code definitions and execution logic across `check`, `list`, `plan`, `build`, `stale`, `publish-record`, `republish`, and `audit-links`.
- **DIFF (2)**:
  - `stamp` (`artifacts.py:9`): The usage block says `stamp --file page.html`, but `--file` in the parser is declared as an optional global flag (`artifacts.py:489`) without `required=True`. However, at runtime in `artifacts.py:504-506`, if `--file` is omitted or does not point to an existing file, the command fails with `SystemExit("artifacts: stamp needs --file <existing html>")`. Additionally, `stamp` accepts an unmentioned `--date` or other flags at parser level due to flat argparse architecture.
  - `banner` (`artifacts.py:11`): The usage block specifies `banner --slug research_map [--file live.html]`, but `--slug` in parser is optional (`artifacts.py:487`), and at runtime omitting `--slug` fails with `SystemExit: artifacts: no page None` (line 498). More importantly, the usage text says `--file` defaults to `live.html`, but line 489 & line 499 show that if `--file` is omitted, the code defaults to the page's repo html file (`REPO / pg["html"]`), not a fixed `live.html`.
- **NOT_IN_DATA (0)**: None; all 10 commands exist in `choices` of the positional argument `cmd` in `argparse` (`artifacts.py:485`). (Note: parser also defines an internal `stale-cache` command not listed in the 10 top usage lines).

---

## 2. Clause Comparison Table

| # | Usage Block Claim | Code Implementation | Status | Audit Findings & Verification |
|---|---|---|---|---|
| 1 | `scripts/dev/artifacts.py:3`: `python scripts/dev/artifacts.py check # registry is consistent with the repo (gate step)` | `scripts/dev/artifacts.py:485,546-548`: `ap.add_argument("cmd", choices=[..., "check", ...])` and `if a.cmd == "check": p = problems(reg); print(...); return 1 if p else 0` | MATCH | SOURCED (`scripts/dev/artifacts.py:3,485,546-548`, `scripts/dev/test_artifacts.py:17-19`). Evaluates `problems(reg)`. Returns 0 if no problems found, 1 if problems found. Directly matches gate step behavior. |
| 2 | `scripts/dev/artifacts.py:4`: `python scripts/dev/artifacts.py list # table: page, status, urls, last published` | `scripts/dev/artifacts.py:485,550`: `ap.add_argument("cmd", choices=[..., "list", ...])` and `if a.cmd == "list": cmd_list(reg)` | MATCH | SOURCED (`scripts/dev/artifacts.py:4,191-209,485,550`, `scripts/dev/test_artifacts.py:55-60`). Outputs table formatted with page slug, status, urls for accounts, and last published dates. |
| 3 | `scripts/dev/artifacts.py:5`: `python scripts/dev/artifacts.py plan --account jishu.sharma # what a session on that account must publish / pin / record` | `scripts/dev/artifacts.py:485-486,551-552`: `ap.add_argument("--account", default="jishu.sharma")` and `elif a.cmd == "plan": print("\n".join(plan(reg, a.account)))` | MATCH | SOURCED (`scripts/dev/artifacts.py:5,233-286,485-486,551-552`, `scripts/dev/test_artifacts.py:36-54`). Generates per-account plan lines (REPLACE, NO COPY, OPERATOR UNPIN+DELETE, etc.) for publishing and pinning. |
| 4 | `scripts/dev/artifacts.py:6`: `python scripts/dev/artifacts.py build # regenerate every page that has a generator in this repo` | `scripts/dev/artifacts.py:485,553-554`: `ap.add_argument("cmd", choices=[..., "build", ...])` and `else: cmd_build(reg)` | MATCH | SOURCED (`scripts/dev/artifacts.py:6,339-354,485,553-554`). Iterates through tracked generator pages in registry and invokes their generator script, placing output html in repo. |
| 5 | `scripts/dev/artifacts.py:7`: `python scripts/dev/artifacts.py stale # STALE <slug> <url> for each page whose repo build differs from what was last published` | `scripts/dev/artifacts.py:485,541-544`: `ap.add_argument("cmd", choices=[..., "stale", ...])` and `lines = stale_lines(reg); print("\n".join(lines) if lines else ...)` | MATCH | SOURCED (`scripts/dev/artifacts.py:7,321-325,485,541-544`, `scripts/dev/test_artifacts.py:315-328`). Formats lines as `STALE <slug> <url> (repo build differs from last publish)`. |
| 6 | `scripts/dev/artifacts.py:8`: `python scripts/dev/artifacts.py publish-record --slug X [--date YYYY-MM-DD] # after an Artifact publish: store published_sha + the publish date (default today)` | `scripts/dev/artifacts.py:485,487,490,536-540`: `ap.add_argument("--slug")`, `ap.add_argument("--date")`, `sha = publish_record(reg, a.slug, today=a.date)` | MATCH | SOURCED (`scripts/dev/artifacts.py:8,328-337,485,487,490,536-540`, `scripts/dev/test_artifacts.py:329-339`). Takes `--slug`, optional `--date` (defaults to today's date in ISO format), computes content_hash and stores in registry.json. |
| 7 | `scripts/dev/artifacts.py:9`: `python scripts/dev/artifacts.py stamp --file page.html # put "Updated <UTC>" first on a built page (build does it for generated pages)` | `scripts/dev/artifacts.py:485,489,503-509`: `ap.add_argument("--file")`, `f = Path(a.file or ""); if not f.is_file(): raise SystemExit(...)` | DIFF | SOURCED (`scripts/dev/artifacts.py:9,93-107,485,489,503-509`, `scripts/dev/test_artifacts.py:384-399`). Usage block lists `--file page.html` as if positional or required option without noting failure mode; parser defines `--file` as optional flag on top-level parser (`artifacts.py:489`), but runtime handler (`artifacts.py:504-506`) strictly enforces `if not f.is_file(): raise SystemExit("artifacts: stamp needs --file <existing html>")`. |
| 8 | `scripts/dev/artifacts.py:10`: `python scripts/dev/artifacts.py republish # REPUBLISH <slug> <html> <url> for each stale page (publisher login only; --all: any login)` | `scripts/dev/artifacts.py:485,488,528-535`: `ap.add_argument("--all", action="store_true")`, checks `is_publisher(reg, mts_signal.login())` unless `a.all`, calls `republish_lines(reg)` | MATCH | SOURCED (`scripts/dev/artifacts.py:10,366-372,485,488,528-535`, `scripts/dev/test_artifacts.py:423-432`). Emits `REPUBLISH <slug> <html> <url>` for stale pages; restricts to publisher logins unless `--all` is supplied. |
| 9 | `scripts/dev/artifacts.py:11`: `python scripts/dev/artifacts.py banner --slug research_map [--file live.html] # insert/refresh the "Part of MTS Home" line` | `scripts/dev/artifacts.py:485,487,489,495-502`: `f = Path(a.file or REPO / pg["html"])` and `ap.add_argument("--file", help="banner / stamp: html to update in place (default: the page's repo html)")` | DIFF | SOURCED (`scripts/dev/artifacts.py:11,58-84,485,487,489,495-502`, `scripts/dev/test_artifacts.py:98-115`). The usage synopsis shows `[--file live.html]` implying a specific default file name, but both the code (`Path(a.file or REPO / pg["html"])`, line 499) and argparse help (`line 489`) specify the default is the page's repo html (`REPO / pg["html"]`), not `live.html`. Additionally, `--slug` is required by runtime logic (`line 498`), but is registered as optional in argparse. |
| 10 | `scripts/dev/artifacts.py:12`: `python scripts/dev/artifacts.py audit-links # audit registry vs repo copy and verify relative links across pages` | `scripts/dev/artifacts.py:485,493-494`: `if a.cmd == "audit-links": return cmd_audit_links(reg)` | MATCH | SOURCED (`scripts/dev/artifacts.py:12,374-480,485,493-494`). Implements `cmd_audit_links`, parses html/markdown links across registered pages, and verifies link targets and repo vs registry freshness. |
