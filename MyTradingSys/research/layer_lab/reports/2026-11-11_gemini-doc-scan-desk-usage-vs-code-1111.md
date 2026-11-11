COUNTS: MATCH=9 DIFF=1 NOT_IN_DATA=0

# Audit Report: `desk.py` Usage Block vs Implementation & Tests

- **Card**: `gemini-doc-scan-desk-usage-vs-code-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `scripts/dev/desk.py` (read)
  - `scripts/dev/test_desk.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-desk-usage-vs-code-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Scan

Evaluated 10 usage claims from the top docstring / usage block of `scripts/dev/desk.py` (lines 3-11) against the `argparse` definitions (lines 440-468), runtime command handlers (lines 469-506), helper functions, and test behaviors in `scripts/dev/test_desk.py`:
- `post "<title>" --need "<what>" --done-when "<observable>" [--target JIS-NB] [--no-ship]`
- `list [--all]`
- `take <id> [--no-ship]`
- `done <id> --result "<what happened>" [--failed] [--no-ship]`
- `wait <id> [--timeout 600]`
- `next [--host JIS-NUC]`
- `sweep [--json] [--as-of <iso utc>] [--no-fetch]`
- `assign [--no-ship]`

Audit outcome across 10 claims:
- **MATCH (9)**: Commands and flags accurately match their code definitions and execution logic across `post`, `list`, `take`, `done`, `wait`, `next`, `sweep`, and `assign`.
- **DIFF (1)**: `take <id>` usage line (`desk.py:6`) omits the `--no-ship` flag, but the parser (`desk.py:465-467`) attaches `--no-ship` to `take`, `desk.take` accepts `ship=True`, and `test_desk.py:44,46,66,87` explicitly passes and tests `ship=False`.
- **NOT_IN_DATA (0)**: None; all 8 commands and documented flags exist in the parser and codebase.

---

## 2. Clause Comparison Table

| # | Usage Block Claim | Code Implementation | Status | Audit Findings & Verification |
|---|---|---|---|---|
| 1 | `scripts/dev/desk.py:3-4`: `python scripts/dev/desk.py post "<title>" --need "<what, with exact paths/commands>" --done-when "<observable>" [--target JIS-NB] [--no-ship]` | `scripts/dev/desk.py:443-447,465-468,478-479`: `p = sub.add_parser("post"); p.add_argument("title"); p.add_argument("--need", required=True); p.add_argument("--done-when", required=True); p.add_argument("--target", default="JIS-NB"); p.add_argument("--no-ship", action="store_true")` | MATCH | SOURCED (`scripts/dev/desk.py:3-4,443-447,465-468,478-479`, `scripts/dev/test_desk.py:39`). Parser defines required positional `title`, required `--need`, required `--done-when`, optional `--target` defaulting to `JIS-NB`, and `--no-ship`. |
| 2 | `scripts/dev/desk.py:5`: `python scripts/dev/desk.py list [--all] # open tasks (default) or everything` | `scripts/dev/desk.py:456-457,484-487`: `p = sub.add_parser("list"); p.add_argument("--all", action="store_true")` and filters on `a.all or r["status"] in OPEN` | MATCH | SOURCED (`scripts/dev/desk.py:5,456-457,484-487`). Subcommand `list` registers boolean flag `--all`; without `--all`, only open tasks (`pending`, `taken`) are displayed. |
| 3 | `scripts/dev/desk.py:6`: `python scripts/dev/desk.py take <id> # desktop agent: claim a task (status taken)` | `scripts/dev/desk.py:448-450,465-468,480-481`: `p = sub.add_parser("take"); p.add_argument("id"); p.add_argument("--no-ship", action="store_true")` | DIFF | SOURCED (`scripts/dev/desk.py:6,448-450,465-468,480-481`, `scripts/dev/test_desk.py:44,46,66,87`). The usage block specifies `take <id>` without documenting `[--no-ship]`, whereas the parser explicitly includes `--no-ship` on `take` via line 466 (`"post", "take", "done", "assign"`), passes `not a.no_ship` to `take(repo, a.id, not a.no_ship)`, and `test_desk.py` repeatedly exercises `ship=False`. |
| 4 | `scripts/dev/desk.py:7`: `python scripts/dev/desk.py done <id> --result "<what happened>" [--failed] [--no-ship] # desktop agent: report` | `scripts/dev/desk.py:448-453,465-468,482-483`: `p = sub.add_parser("done"); p.add_argument("id"); p.add_argument("--result", required=True); p.add_argument("--failed", action="store_true"); p.add_argument("--no-ship", action="store_true")` | MATCH | SOURCED (`scripts/dev/desk.py:7,448-453,465-468,482-483`, `scripts/dev/test_desk.py:47,71`). Positional `id`, required option `--result`, store_true flag `--failed`, and `--no-ship` are implemented in parser and passed to `finish(repo, a.id, a.result, a.failed, not a.no_ship)`. |
| 5 | `scripts/dev/desk.py:8`: `python scripts/dev/desk.py wait <id> [--timeout 600] # poster: block until the task is done/failed on origin` | `scripts/dev/desk.py:448-455,502-504`: `p = sub.add_parser("wait"); p.add_argument("id"); p.add_argument("--timeout", type=int, default=600)` | MATCH | SOURCED (`scripts/dev/desk.py:8,448-455,502-504`, `scripts/dev/test_desk.py:41,49`). Positional `id` and optional `--timeout` (integer defaulting to 600) match code parser and dispatch to `wait(repo, a.id, a.timeout)`. |
| 6 | `scripts/dev/desk.py:9`: `python scripts/dev/desk.py next [--host JIS-NUC] # DSA: this host's first pending row (DSA-<host> or DSA); exit 1 = none` | `scripts/dev/desk.py:458-459,488-492`: `p = sub.add_parser("next"); p.add_argument("--host", default=None, help="host name (default: this machine)")` and returns `0 if r else 1` | MATCH | SOURCED (`scripts/dev/desk.py:9,172-185,458-459,488-492`, `scripts/dev/test_desk.py:107-121`). Parser defines `--host` (default None/this machine); logic queries `next_for(repo, a.host)` for `DSA-<host>` or `DSA` lanes, returning exit code 0 if found or 1 if none. |
| 7 | `scripts/dev/desk.py:10`: `python scripts/dev/desk.py sweep [--json] [--as-of <iso utc>] [--no-fetch]` | `scripts/dev/desk.py:461-464,493-497`: `p = sub.add_parser("sweep"); p.add_argument("--json", action="store_true"); p.add_argument("--as-of", default=None, help="ISO UTC time ages are measured at (default now)"); p.add_argument("--no-fetch", action="store_true")` | MATCH | SOURCED (`scripts/dev/desk.py:10,461-464,493-497`). All three flags (`--json`, `--as-of`, `--no-fetch`) are defined in argparse and handled in sweep execution. |
| 8 | `scripts/dev/desk.py:11`: `python scripts/dev/desk.py assign [--no-ship] # scheduled (daily_hygiene.py): post every ready DSA-lane card once` | `scripts/dev/desk.py:460,465-468,498-500`: `sub.add_parser("assign"); p.add_argument("--no-ship", action="store_true")` | MATCH | SOURCED (`scripts/dev/desk.py:11,187-212,460,465-468,498-500`, `scripts/dev/test_desk.py:122-139`). Subcommand `assign` takes optional `--no-ship` and posts rows for ready DSA-lane cards. |
| 9 | `scripts/dev/desk.py:19-21`: `Run from the live tree (.mts_live present), post/take/done never commit there: ... --no-ship is refused there` | `scripts/dev/desk.py:100-105`: `if not (Path(repo) / LIVE_MARKER).exists(): yield repo; return; if not ship: raise SystemExit(...)` | MATCH | SOURCED (`scripts/dev/desk.py:19-21,100-105`, `scripts/dev/test_desk.py:79-102`). Verified by `writable()` context manager and `test_live_tree_never_gets_a_commit` asserting `--no-ship` raises `SystemExit` in a live tree. |
| 10 | `scripts/dev/desk.py:17`: `A task the agent will not do is closed with done --failed --result "declined: <why>"; an Operator: line in the commit body surfaces it in sync.py news.` | `scripts/dev/desk.py:165-167`: `if failed: body += f"Operator: desk task {rid} not completed: {result}\n"` | MATCH | SOURCED (`scripts/dev/desk.py:17,165-167`, `scripts/dev/test_desk.py:69-75`). Verified in `finish()` implementation and `test_declined_task_raises_operator_line`, which checks commit body contains `Operator: desk task`. |
