COUNTS: MATCH=8 DIFF=0 NOT_IN_DATA=0

# Audit Report: Independent Gemini Blind Read of `gemini_queue.py` vs Docstring & Tests

- **Card**: `gemini-blind-read-gemini-queue-docstring-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `scripts/dev/gemini_queue.py` (read)
  - `scripts/dev/test_gemini_queue.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-gemini-queue-docstring-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Docstring Clauses & Implementation

An independent blind read of `scripts/dev/gemini_queue.py` evaluated the docstring clauses (`scripts/dev/gemini_queue.py:1-13`) against code implementation and unit tests in `scripts/dev/test_gemini_queue.py`:
1. **Invocation and Sequential Execution (`run`)**: `python scripts/dev/gemini_queue.py run <card-id>[:<effort>][:<model>] ... run the jobs one after another`. Implemented via sequential iteration over CLI specs calling `run_job()` sequentially; covered by unit test `test_token_parsing_each_model`.
2. **Effort and Model Token Parsing & Defaults**: `effort in low|medium|high (default low); model in flash|argon|opus|sonnet|gpt (default flash; gpt = gpt-oss-120b-medium, effort ignored); tokens may appear in either order`. Implemented in token loop; tested in `test_token_parsing_each_model` and `test_gpt_fixed_id_ignores_effort`.
3. **Queue Status Reporting (`status`)**: `python scripts/dev/gemini_queue.py status: last log line per job`. Implemented by iterating sorted `*.log` files under queue root; verified by CLI dispatch.
4. **Throwaway Worktree and Branch Path**: `Each job: worktree F:/MTS/gq/<id> on branch gemini-q/<id> cut from origin/fast-track`. Implemented via `root() / card` default and `git worktree add -b gemini-q/<card> <wt> origin/fast-track`; tested in `RootConfigTest` and `RunJobTest`.
5. **Execution Harness (`agy --print`) & Prompt Composition**: `` `agy --print` with the chosen Antigravity model, prompt = the card brief plus the lane rules ``. Implemented by building command line `[str(AGY), '--print', rules_for(model, mid) + brief, ...]`; tested in `test_exact_model_id_passed_to_agy` and `test_rules_name_actual_model`.
6. **Lane Constraint Rules Injection**: `Gemini commits on its branch only: it never ships, never stamps REVIEWED, never touches the live tree. A Claude session reviews the branch and ships it`. Implemented verbatim in `RULES` constant template passed into prompt; tested in `test_rules_name_actual_model`.
7. **STALE / State Skip (Card Gate & Claim Filtering)**: Implemented in `card_gate()` and `run_job()`, skipping cards that are not `ready`, or tagged `SHIPPED`/`STALE`, or held by another host (`SKIP <card>: ...`); tested in `test_done_card_skipped`, `test_shipped_tag_skipped`, and `CardGateTest`.
8. **Exit Codes and What is Written on Success or Non-Zero Exit**: CLI exits 0 on success, 2 on bad invocation/spec, writes `START <card> <mid>` and `EXIT <returncode> after <time>s` to log file; tested in `test_bad_model_rejected` and `RunJobTest`.

Audit outcome across the 8 clauses:
- **MATCH (8)**: All 8 docstring clauses match code implementation in `gemini_queue.py` and are covered/verified by unit tests in `test_gemini_queue.py`.
- **DIFF (0)**: None.
- **NOT_IN_DATA (0)**: None.

---

## 2. Clause Comparison Table

| # | Docstring Clause | Implementation in `gemini_queue.py` | Pinning / Verification in `test_gemini_queue.py` | Status | file:line Quotes & Findings |
|---|---|---|---|---|---|
| 1 | `run <card-id>[:<effort>][:<model>] ... run the jobs one after another` | `scripts/dev/gemini_queue.py:256-272`: `for spec in argv[1:]: ... run_job(card, effort, model)` executes jobs sequentially in loop | `scripts/dev/test_gemini_queue.py:150-160`: `ModelTokenTest.test_token_parsing_each_model` verifies `gq.main(["run", spec])` parsing and calling `run_job` | MATCH | SOURCED (`gemini_queue.py:3,256-272`, `test_gemini_queue.py:150-160`). Code iterates over `argv[1:]` sequentially executing `run_job(card, effort, model)`; tests verify runner invocation and return code 0. |
| 2 | `effort in low\|medium\|high (default low); model in flash\|argon\|opus\|sonnet\|gpt (default flash; gpt = gpt-oss-120b-medium, effort ignored); tokens may appear in either order` | `scripts/dev/gemini_queue.py:185-193,262-270`: `effort, model = 'low', 'flash'`, checks `t in ('low', 'medium', 'high')` or `t in MODELS`, `model_id()` returns `gpt-oss-120b-medium` | `scripts/dev/test_gemini_queue.py:154-160,182-187`: `test_token_parsing_each_model` tests specs like `c1:high:argon`, `c1:opus:medium`, `c1:gpt`; `test_gpt_fixed_id_ignores_effort` checks `gpt-oss-120b-medium` without `--effort` | MATCH | SOURCED (`gemini_queue.py:4-5,187,262-270`, `test_gemini_queue.py:154-160,182-187`). Token parsing handles any permutation, sets default low/flash, maps gpt to fixed id, and drops `--effort` flag for gpt. |
| 3 | `python scripts/dev/gemini_queue.py status last log line per job` | `scripts/dev/gemini_queue.py:251-255`: `if argv[0] == 'status': for lg in sorted(root().glob('*.log')): lines = ... print(lg.stem, '\|', lines[-1][:120] if lines else '') return 0` | `scripts/dev/test_gemini_queue.py:149-152`: CLI argument dispatch tested in `ModelTokenTest._parse`; log file formatting verified in `RunJobTest` | MATCH | SOURCED (`gemini_queue.py:6,251-255`, `test_gemini_queue.py:96,119-120`). Implements status scan over queue root directory logs, printing the last line up to 120 chars; returns rc 0. |
| 4 | `Each job: worktree F:/MTS/gq/<id> on branch gemini-q/<id> cut from origin/fast-track` | `scripts/dev/gemini_queue.py:23,169-183,200`: `ROOT = Path(...) or 'F:/MTS/gq'`, `wt = root() / card`, `git('worktree', 'add', '-b', f'gemini-q/{card}', str(wt), 'origin/fast-track')` | `scripts/dev/test_gemini_queue.py:21-29`: `RootConfigTest` tests `root()` from `MTS_GQ_ROOT` or default `ROOT`; `RunJobTest` verifies worktree path handling | MATCH | SOURCED (`gemini_queue.py:8,23,176,200`, `test_gemini_queue.py:21-29,85`). Code constructs throwaway worktree under queue root on branch `gemini-q/<card>` branched from `origin/fast-track`. |
| 5 | `` `agy --print` with the chosen Antigravity model, prompt = the card brief plus the lane rules `` | `scripts/dev/gemini_queue.py:228-229`: `cmd = [str(AGY), '--print', rules_for(model, mid) + brief, '--model', mid] + ([] if model == 'gpt' else ['--effort', effort]) + ['--mode', 'accept-edits', ...]` | `scripts/dev/test_gemini_queue.py:168-181`: `test_exact_model_id_passed_to_agy` verifies command arguments passed to `subprocess.run` | MATCH | SOURCED (`gemini_queue.py:8-9,228-229`, `test_gemini_queue.py:168-181`). Command assembly matches docstring: invokes AGY with `--print`, passes `rules_for(...) + brief`, `--model`, and conditional `--effort`. |
| 6 | `Gemini commits on its branch only: it never ships, never stamps REVIEWED, never touches the live tree. A Claude session reviews the branch and ships it` | `scripts/dev/gemini_queue.py:9-10,32-42`: Prompt `RULES` template defines hard rules: "do NOT run sync.py ship, do NOT push, do NOT stamp REVIEWED, do NOT touch the live tree" | `scripts/dev/test_gemini_queue.py:188-191`: `test_rules_name_actual_model` validates model insertion into `RULES` text | MATCH | SOURCED (`gemini_queue.py:9-10,34-35`, `test_gemini_queue.py:188-191`). Exact lane constraints stated in the docstring are embedded into the prompt template `RULES` delivered to each worker. |
| 7 | STALE skip & card readiness gate: skip cards not ready, or tagged SHIPPED/STALE, or already claimed | `scripts/dev/gemini_queue.py:115-132,205-212,218-221`: `card_gate()` checks `c.get('state') == 'ready'` and `not tag`; logs `SKIP <card>: ...` for stale/shipped/non-ready or claimed cards | `scripts/dev/test_gemini_queue.py:110-112,123-140,193-206`: `test_other_host_open_claim_skipped`, `test_done_card_skipped`, `test_shipped_tag_skipped`, `test_done_and_tagged_refused_ready_ok` | MATCH | SOURCED (`gemini_queue.py:115-132,205-212`, `test_gemini_queue.py:110-112,123-140,202-206`). Code gates execution on card state and stop tag (e.g. `SHIPPED`, `STALE`), skipping execution without creating worktrees or running agy. |
| 8 | Exit codes and execution logs (success vs EXIT code) | `scripts/dev/gemini_queue.py:231-240,248-250,259-260,269-270`: Writes `START <card> <mid>` and `\nEXIT <rc> after <s>s\n` to `<card>.log`; main returns 0 on success, 2 on bad spec/invocation | `scripts/dev/test_gemini_queue.py:119-121,162-165`: `test_identity_set_and_failure_logged`, `test_bad_model_rejected` verifies rc 2 on bad token | MATCH | SOURCED (`gemini_queue.py:232,240,250,260,270,272`, `test_gemini_queue.py:119-121,162-165`). Worker writes START and EXIT lines with elapsed seconds to `<card>.log`; `main()` returns rc 0 or 2 as specified. |
