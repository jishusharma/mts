FINDINGS: 0 | GAPS_IN_TESTS: 2 | CASES_VERIFIED: 6

# Gemini Blind Read: `scripts/dev/api_agent.py` (max_tokens retry change)

- **Card**: `gemini-blind-read-of-scripts-dev-api-age`
- **Date**: 2026-11-10 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, blind read worker, JIS-NUC)
- **Target File**: `scripts/dev/api_agent.py` [SOURCED: `scripts/dev/api_agent.py:1-219`]
- **Reference Commit**: `53953633c085` (shipped via `api-agent-max-tokens-and-resume-1108`, merge `478efba5109d`) [SOURCED: commit `53953633c085`]
- **Test File**: `scripts/dev/test_api_agent_models.py` [SOURCED: `scripts/dev/test_api_agent_models.py:1-103`]
- **Scope**:
  - In: Blind read of `api_agent.py` main loop cold; analyze `max_tokens` stop handling (termination, turn counter, dropped reply, cut-off tool calls, single vs double cost counting); compare against the 4 `MaxTokens` unit tests in `test_api_agent_models.py`; identify defects or verify behavior.
  - Out: No code edits to `api_agent.py` or tests; no live job launches; no secret/key operations.

---

## 1. Questions Analyzed & Verdicts

### Q1: Does the retry loop terminate?
- **Verdict**: YES, strictly terminates [OURS].
- **Analysis**:
  - At line 180 of [api_agent.py](file:///F:/MTS/gq/gemini-blind-read-of-scripts-dev-api-age/scripts/dev/api_agent.py#L180-L188):
    ```python
    if resp.get("stop_reason") == "max_tokens" and max_tokens < MAX_TOKENS_CEILING:
        ...
        max_tokens = min(max_tokens * 2, MAX_TOKENS_CEILING)
        retries_used += 1
        turns -= 1
        continue
    ```
  - When starting at default `max_tokens = 32000` [SOURCED: `scripts/dev/api_agent.py:33,144`], `MAX_TOKENS_CEILING = 64000` [SOURCED: `scripts/dev/api_agent.py:34`].
  - On the first `max_tokens` stop: `32000 < 64000` is `True`. `max_tokens` becomes `min(32000 * 2, 64000) = 64000`. The loop calls `continue`.
  - On the second `max_tokens` stop on the retried turn: `max_tokens = 64000 < 64000` is `False`.
  - Execution falls through to line 189: the truncated assistant response is logged (`type: assistant`), appended to messages, and checked at lines 198-201:
    ```python
    if not tool_uses or resp.get("stop_reason") not in ("tool_use",):
        if resp.get("stop_reason") == "max_tokens":
            subtype = "error_max_tokens"
        break
    ```
  - Since `resp.get("stop_reason") == "max_tokens" != "tool_use"`, the loop immediately breaks with `subtype = "error_max_tokens"`.
  - If a user passes `--max-tokens 64000` (or higher) via CLI, `max_tokens < MAX_TOKENS_CEILING` is immediately `False`; 0 retries occur and it terminates on the first stop.
  - If a user passes `--max-tokens 16000`, it doubles to 32000, then to 64000 (at most `ceil(log2(64000 / initial))` retries), strictly finite.
  - In addition, both global `turns >= a.max_turns` (checked every turn) and `cost >= a.max_usd` (accumulated every call including retries) guarantee termination.

### Q2: Is the turn counter right?
- **Verdict**: YES, correctly maintained [OURS].
- **Analysis**:
  - Before the API call, `turns` represents the completed turns.
  - Line 178 increments `turns += 1` [SOURCED: `scripts/dev/api_agent.py:178`].
  - When a `max_tokens` stop triggers a retry, line 187 executes `turns -= 1` [SOURCED: `scripts/dev/api_agent.py:187`].
  - Thus, the dropped attempt does not consume a turn budget count.
  - When the retried call runs, line 178 increments `turns += 1` again, so the logical turn number remains unchanged.
  - The retry event is recorded separately in the log at line 182 (`"type": "retry", "turn": turns`) and in the final summary record as `max_tokens_retries: retries_used` [SOURCED: `scripts/dev/api_agent.py:209`].
  - The final `num_turns` counts only realized agent turns (including the final failed turn if the retry at the ceiling fails), matching the convention of `api_agent.py`.

### Q3: Is a cut-off tool call ever sent back to the model?
- **Verdict**: NO, never sent [OURS].
- **Analysis**:
  - Case A (Retry triggered, `max_tokens < MAX_TOKENS_CEILING`):
    - At line 180-188, when `stop_reason == "max_tokens"`, `continue` is invoked.
    - Lines 193-207 (which append `resp.get("content")` to `messages`, execute tools, and append `tool_result` to `messages`) are completely bypassed.
    - The truncated response is discarded; the messages history is unchanged from before the attempt. No tool execution or tool result is generated.
  - Case B (Retry exhausted at ceiling `max_tokens == MAX_TOKENS_CEILING`):
    - The branch at line 180 is skipped.
    - At line 198: `if not tool_uses or resp.get("stop_reason") not in ("tool_use",):`
    - Because `resp.get("stop_reason") == "max_tokens" != "tool_use"`, the condition evaluates to `True`.
    - Line 201 executes `break`.
    - Lines 202-207 (which loop over `tool_uses`, run tools, and append tool results to `messages`) are never reached.
    - Thus, no partial or cut-off tool call is ever executed or returned to the model as a `tool_result`.

### Q4: Is cost counted once?
- **Verdict**: YES, each API call's cost is accumulated exactly once into the running total [OURS].
- **Analysis**:
  - At line 179: `cost += usd(a.model, resp.get("usage", {}))` [SOURCED: `scripts/dev/api_agent.py:179`].
  - Every HTTP response returned from `call_api` incurs token usage billed by the API provider.
  - Even though the content of a dropped truncated reply is discarded, its input and output tokens were processed and billed.
  - Line 179 executes before the `if resp.get("stop_reason") == "max_tokens"` branch at line 180.
  - The cost of the dropped attempt is added once into `cost`.
  - The retried call subsequently adds its own token usage once into `cost`.
  - There is no double-counting of any single call, and no dropped call is omitted from total billing.

---

## 2. Cases Where a `max_tokens` Stop is Retried, Dropped, or Ended

| Case # | Scenario / Condition | Action Taken | Turn Counter (`turns`) | Cost Accounting | Final `subtype` | Code Reference |
|---:|---|---|---|---|---|---|
| 1 | `stop_reason == "max_tokens"` and `max_tokens < 64000` (e.g. 1st stop at default 32000) | **Retried & Dropped**: Reply dropped; logged as `type: retry`; `max_tokens` doubled (capped at 64000); turn retried immediately. | Decremented by 1 (`turns -= 1`), so turn index stays constant for the retry. | Usage of dropped call added to `cost`; retried call adds its own usage. | Continues loop (pending retry outcome) | `scripts/dev/api_agent.py:180-188` |
| 2 | `stop_reason == "max_tokens"` and `max_tokens >= 64000` (retry exhausted at ceiling) | **Ended as Error**: Truncated content logged as `type: assistant`; no tools executed; loop breaks immediately. | Kept as turn count (`turns` not decremented). | Usage of final attempt added to `cost`. | `error_max_tokens` (exit code 1) | `scripts/dev/api_agent.py:189,198-201,215` |
| 3 | Initial `--max-tokens 64000` specified on CLI and hits `max_tokens` stop | **Ended as Error**: Condition `max_tokens < 64000` is `False` on first encounter; 0 retries attempted; breaks immediately. | Kept as turn count (`turns = 1`). | Usage of call added to `cost`. | `error_max_tokens` (exit code 1) | `scripts/dev/api_agent.py:180,198-201` |
| 4 | First call truncated at 32000, retry succeeds with `stop_reason == "end_turn"` | **Recovered**: First attempt dropped; second attempt accepted; normal completion. | `turns = 1`, `retries_used = 1`. | Both calls billed into `cost`. | `success` (exit code 0) | `scripts/dev/api_agent.py:180-188,189-215` |
| 5 | First call truncated at 32000, retry succeeds with `stop_reason == "tool_use"` | **Recovered into Tool Use**: First attempt dropped; second attempt's tools run and results sent back to model. | Normal tool turn completion. | Both calls billed into `cost`. | Proceeds to next turn | `scripts/dev/api_agent.py:180-188,198,202-207` |
| 6 | Retried call exceeds `cost >= a.max_usd` | **Ended as Budget Exceeded**: Evaluated at loop head before next turn. | Reflects turns attempted. | Accurately reflects cumulative usage. | `error_max_budget_usd` (exit code 1) | `scripts/dev/api_agent.py:165-167` |

---

## 3. Comparison with the Four `MaxTokens` Tests

The four test cases in `MaxTokens` class of `scripts/dev/test_api_agent_models.py` [SOURCED: `scripts/dev/test_api_agent_models.py:37-101`] were inspected:

1. `test_default_token_cap_per_model`:
   - Checks that `default_max_tokens(m) >= 16000` for all known models and `>= 32000` for `claude-sonnet-5-5`.
   - Checks fallback for unknown model name.
2. `test_launch_passes_max_tokens_through_in_dry_run`:
   - Checks `api_job.py` CLI passthrough and formatting in dry-run output.
3. `test_retry_on_max_tokens_stop`:
   - Simulates 1st call `stop_reason: "max_tokens"` and 2nd call `stop_reason: "end_turn"`.
   - Verifies `rc == 0`, `len(bodies) == 2`, `bodies[1] > bodies[0]`, `subtype == "success"`, and `max_tokens_retries == 1`.
4. `test_max_tokens_at_the_ceiling_still_ends_as_error_max_tokens`:
   - Simulates repeated calls returning `stop_reason: "max_tokens"`.
   - Verifies `rc == 1`, `len(calls) <= 3`.

### Identified Gaps in Current Test Suite [OURS]
1. **Tool Use on Retry Not Tested**:
   - `test_retry_on_max_tokens_stop` tests a retry that completes immediately with text (`end_turn`).
   - It does not test the case where the retried response contains a valid `tool_use` block, to verify end-to-end that tools execute normally after a retry and messages history contains no orphaned blocks.
2. **Cost Accumulation Across Retry Not Explicitly Asserted**:
   - Neither test asserts that `recs[-1]["total_cost_usd"]` equals the sum of `usd(call_1)` + `usd(call_2)`.
   - (While verified by inspection in the code, having an explicit test assertion would prevent regression).

---

## 4. Summary & Verification

- `FINDINGS: 0` defects found in `scripts/dev/api_agent.py` logic.
- `GAPS_IN_TESTS: 2` gaps identified in test suite coverage.
- `CASES_VERIFIED: 6` operational flow cases verified.
- Unit tests pass cleanly: `python -m unittest scripts/dev/test_api_agent_models.py` (8/8 tests OK).
- Output file is the test; no edits were made to repo source files.
