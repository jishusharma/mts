# Model bake-off: qwen3-coder:30b vs gpt-oss:20b (NUC), 2026-09-29

Same spec, same Sonnet-written test file. gpt-oss specs are copies with `MODEL: gpt-oss:20b`, OUTPUT_TOKENS x2, output suffixed `_gptoss.py.new`.
Tests run raw (Qwen/gpt-oss output unmodified) in a temp dir; review notes are about code quality beyond the tests.

| Task | Model | Wall-clock | Tests (raw) | Notes |
|---|---|---|---|---|
| 126 journal-env | qwen3-coder:30b | 340.2 s | 10/10 | Deleted an existing docstring paragraph instead of adding one sentence (restored by hand). Otherwise correct. |
| 128 mainnet-plan-check | qwen3-coder:30b | 210.9 s | 10/10 | Correct; module docstring missing (added by hand). |
| 129 mainnet-pnl | qwen3-coder:30b | 348.1 s | 15/15 | Correct; module docstring placed after the imports (so not a real docstring), moved by hand. |
| 140 journal-env (spec 126 copy) | gpt-oss:20b | pending | pending | task 140 packed 2026-09-29, waiting in NUC queue behind audits |
| 141 mainnet-plan-check (spec 128 copy) | gpt-oss:20b | pending | pending | packed, waiting |
| 142 mainnet-pnl (spec 129 copy) | gpt-oss:20b | pending | pending | packed, waiting |

To fill the pending rows: `python scripts/worker/queue_tool.py verify 140 141 142`, then run each `*_gptoss.py.new.new` (module renamed) against
`MyTradingSys/execution/test_{journal_env,mainnet_plan_check,mainnet_pnl}.py` (already promoted; use a temp dir copy, do not overwrite).
Wall-clock comes from the verify SUMMARY line ("... s on JIS-NUC").

## Result 2026-09-29 07:45Z (supervisor)
- 140 gpt-oss:20b: 1632 s, done_reason=length, eval 7000 tokens, EMPTY response (all reasoning) -> FAIL. Qwen 126: 340 s, 10/10.
- 142 withdrawn to held/; 141 left to finish (already running). Verdict: gpt-oss:20b is not used for code specs; qwen3-coder:30b stays sole code worker.

## qwen3.6:35b, THINK false (2026-09-29 ~09:30Z)
| task | wall s | eval tok | result |
|---|---|---|---|
| 150 journal env | 167 | 119 | FAIL: empty FILE block |
| 151 plan check | 128 | 125 | FAIL: empty FILE block |
| 152 mainnet pnl | 145 | 104 | FAIL: empty FILE block |
Retry 153 = 151 with THINK true, OUTPUT_TOKENS 12000 (pending).
| 153 plan check, THINK true | 959 | 8015 | PASS 10/10 (Qwen3-coder: 211 s, 10/10) |

**Verdict (supervisor):** qwen3-coder:30b stays primary (4.5x faster, same pass rate). qwen3.6:35b is kept on F: as the RETRY model: when a Qwen reply fails its tests twice, repack once with MODEL: qwen3.6:35b, THINK: true, OUTPUT_TOKENS >= 12000 before handing to Sonnet. Never use qwen3.6 with THINK false (empty files).
