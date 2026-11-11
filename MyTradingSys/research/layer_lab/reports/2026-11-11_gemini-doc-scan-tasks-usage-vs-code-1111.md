COUNTS: MATCH=9 DIFF=1 NOT_IN_DATA=0

# Audit Report: `tasks.py` Usage Block vs Implementation & Tests

- **Card**: `gemini-doc-scan-tasks-usage-vs-code-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `scripts/dev/tasks.py` (read)
  - `scripts/dev/test_tasks.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-tasks-usage-vs-code-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Scan

Evaluated 10 usage claims from the top docstring / usage block of `scripts/dev/tasks.py` (lines 3-14) against the `argparse` definitions (`scripts/dev/tasks.py:1752-1873`), command handlers, and test suites in `scripts/dev/test_tasks.py`:
1. `new "<title>" [--id B170] [--ref B170] [--lane SONNET] [--prio 3] [--from-inbox <fb id>] [--layer tom]`
2. `check [<id>]`
3. `lint`
4. `list [--state ready] [--lane SONNET] [--all]`
5. `status`
6. `tried <id> [--asks "<question>"]`
7. `next [--n 3] [--lane SONNET] [--all]`
8. `brief <id>`
9. `tag <id> [--refresh] [--add kind:ref --line "<one line>"]`
10. `twins` (named in card goal; verified against argparse & test_tasks.py) / `stale [--refresh]`

Audit outcome across 10 claims:
- **MATCH (9)**: Commands and documented arguments/options match their argparse configurations, runtime execution logic, and test cases across `new`, `check`, `lint`, `status`, `tried`, `next`, `brief`, `tag`, and `twins`.
- **DIFF (1)**: `list` usage line (`scripts/dev/tasks.py:6`) documents `list [--state ready] [--lane SONNET] [--all]`, but the parser (`scripts/dev/tasks.py:1802-1807`) also defines and supports `--prefix` (`ls.add_argument("--prefix", help=...)`), which is exercised in `scripts/dev/test_tasks.py:1517-1524` (`run_cli("list", "--prefix", "Q:")`) but omitted from the usage block.
- **NOT_IN_DATA (0)**: None; all 10 surveyed commands and flags exist in argparse and the codebase.

---

## 2. Clause Comparison Table

| # | Usage Block Claim | Code Implementation | Status | Audit Findings & Verification |
|---|---|---|---|---|
| 1 | `scripts/dev/tasks.py:3`: `python scripts/dev/tasks.py new "<title>" [--id B170] [--ref B170] [--lane SONNET] [--prio 3] [--from-inbox <fb id>] [--layer tom]` | `scripts/dev/tasks.py:1755-1766`: `n = sp.add_parser("new"); n.add_argument("title"); n.add_argument("--id"); n.add_argument("--ref", action="append"); n.add_argument("--lane", choices=LANES); n.add_argument("--prio", type=int, default=3, choices=range(1, 6)); n.add_argument("--from-inbox"); n.add_argument("--source", "--sources", action="append", dest="sources"); n.add_argument("--kind", choices=tuple(CODEX_KINDS)); n.add_argument("--layer", action="append"); n.add_argument("--crucial", action="store_true")` | MATCH | SOURCED (`scripts/dev/tasks.py:3,1755-1766`, `scripts/dev/test_tasks.py:208,434,1416`). Positional `title`, optional `--id`, `--ref` (append), `--lane`, `--prio` (default 3), `--from-inbox`, and `--layer` match parser definitions and CLI usage in tests. |
| 2 | `scripts/dev/tasks.py:4`: `python scripts/dev/tasks.py check [<id>] # Definition of Ready; promotes raw/refined -> ready when it passes (fail closed)` | `scripts/dev/tasks.py:805-851,1797-1800`: `c = sp.add_parser("check"); c.add_argument("id", nargs="?"); c.add_argument("--demote", action="store_true")` | MATCH | SOURCED (`scripts/dev/tasks.py:4,805-851,1797-1800`, `scripts/dev/test_tasks.py:807,1432`). Optional positional `id` (`nargs="?"`) parses single card or all cards; promotes cards when Definition of Ready checks succeed. |
| 3 | `scripts/dev/tasks.py:5`: `python scripts/dev/tasks.py lint # every card: a ready/active card that fails DoR is an error (exit 1)` | `scripts/dev/tasks.py:853-873,1801`: `sp.add_parser("lint").set_defaults(f=cmd_lint)` | MATCH | SOURCED (`scripts/dev/tasks.py:5,853-873,1801`, `scripts/dev/test_tasks.py:225,234,241,247,653`). Subcommand `lint` takes no additional arguments and exits with code 1 if any ready or active card fails DoR checks. |
| 4 | `scripts/dev/tasks.py:6`: `python scripts/dev/tasks.py list [--state ready] [--lane SONNET] [--all] # open cards only; --all adds done/dropped` | `scripts/dev/tasks.py:875-887,1802-1807`: `ls = sp.add_parser("list"); ls.add_argument("--state", choices=STATES); ls.add_argument("--lane", choices=LANES); ls.add_argument("--all", action="store_true"); ls.add_argument("--prefix", help=...)` | DIFF | SOURCED (`scripts/dev/tasks.py:6,875-887,1802-1807`, `scripts/dev/test_tasks.py:621,625,721,1510,1522`). While `--state`, `--lane`, and `--all` match exactly, the parser defines `--prefix` (`ls.add_argument("--prefix", help="only cards whose title starts with this (e.g. 'Q:' = open questions)")`), explicitly exercised in `scripts/dev/test_tasks.py:1522`, but omitted from the usage block. |
| 5 | `scripts/dev/tasks.py:7`: `python scripts/dev/tasks.py status # counts + the line the dispatcher reads: REFINE_NEEDED / REFINE_OK` | `scripts/dev/tasks.py:889-902,1808`: `sp.add_parser("status").set_defaults(f=cmd_status)` | MATCH | SOURCED (`scripts/dev/tasks.py:7,889-902,1808`). Subcommand `status` takes no positional or optional parameters, outputs counts and prints `REFINE_OK` or `REFINE_NEEDED`. |
| 6 | `scripts/dev/tasks.py:8`: `python scripts/dev/tasks.py tried <id> [--asks "<question>"] # refiner: a try that did not reach ready; --asks parks it for the operator` | `scripts/dev/tasks.py:1400-1431,1824-1827`: `tr = sp.add_parser("tried"); tr.add_argument("id"); tr.add_argument("--asks")` | MATCH | SOURCED (`scripts/dev/tasks.py:8,1400-1431,1824-1827`). Required positional `id` and optional `--asks` match parser definitions and `cmd_tried` handling. |
| 7 | `scripts/dev/tasks.py:9`: `python scripts/dev/tasks.py next [--n 3] [--lane SONNET] [--all] # the first ready cards no session holds, best first (--all: claimed too, marked)` | `scripts/dev/tasks.py:904-922,1809-1813`: `nx = sp.add_parser("next"); nx.add_argument("--n", type=int, default=3); nx.add_argument("--lane", choices=LANES); nx.add_argument("--all", action="store_true")` | MATCH | SOURCED (`scripts/dev/tasks.py:9,904-922,1809-1813`, `scripts/dev/test_tasks.py:526`). Flag `--n` (default 3), choices `--lane`, and boolean `--all` match parser definitions and dispatch logic. |
| 8 | `scripts/dev/tasks.py:10`: `python scripts/dev/tasks.py brief <id> # the <= 30 line session prompt for one card` | `scripts/dev/tasks.py:924-934,1814-1816`: `b = sp.add_parser("brief"); b.add_argument("id")` | MATCH | SOURCED (`scripts/dev/tasks.py:10,924-934,1814-1816`, `scripts/dev/test_tasks.py:1429`). Subcommand `brief` accepts required positional `id` and renders the prompt block under the line cap. |
| 9 | `scripts/dev/tasks.py:12`: `python scripts/dev/tasks.py tag <id> [--refresh] [--add kind:ref --line "<one line>"] # state tag + LATEST pointers (TASK_REFINEMENT.md)` | `scripts/dev/tasks.py:941-951,1851-1856`: `tg = sp.add_parser("tag"); tg.add_argument("id"); tg.add_argument("--refresh", action="store_true"); tg.add_argument("--add", help=...); tg.add_argument("--line", help=...)` | MATCH | SOURCED (`scripts/dev/tasks.py:12,941-951,1851-1856`, `scripts/dev/test_tasks.py:584,595,601,706,827`). Parser implements required positional `id`, boolean `--refresh`, string option `--add`, and string option `--line`. |
| 10 | `scripts/dev/tasks.py:1767`: `sp.add_parser("twins", help="likely duplicate open cards (close title or same rare files)").set_defaults(f=cmd_twins)` | `scripts/dev/tasks.py:689-694,1767`: `cmd_twins` calls `twin_pairs(load_all(REPO))` and prints pairs and total count | MATCH | SOURCED (`scripts/dev/tasks.py:689-694,1767`, `scripts/dev/test_tasks.py:1420-1421`). Subcommand `twins` takes no extra arguments, detects likely duplicate open cards based on title similarity and shared rare files, verified via `run_cli("twins")`. |
