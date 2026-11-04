# GPT independent re-derivation: WaveTrend C30 retest (2026-11-04)

Verdict: **BLOCKED** ? both registered runner inputs are absent, so the requested code-level audit of lookahead, retest-window behavior, and fee math cannot be completed.

## What was checked

- Expected inputs: `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/run_retest.py` and `run_long_window.py`; both `Get-Content` lookups returned ?Cannot find path?.
- Directory inventory: `Get-ChildItem MyTradingSys/research/wavetrend_c30_retest_2026-11-04 -Force` showed `study.py`, `study_long.py`, tests, result files and CSVs, but neither registered runner. A recursive search of `MyTradingSys/research` for either runner filename returned no paths.
- Reviewed the available `BLOCKED.md`, `BLOCKED_LONG.md`, `RESULT.md`, and `RESULT_LONG.md` as contextual artifacts only. Their described study design does not establish what the absent runner code actually executes. No market data was read or run.

## Findings

| Severity | File:line | Claim | Evidence / disposition | Proposed fix |
|---|---|---|---|---|
| HIGH | `run_retest.py` (missing) | Dot trigger and retest bar entry use closed bars without future leakage | NOT_IN_DATA: file absent; directory inventory has no such file | Restore the exact runner version named by the registry, then trace signal timestamps, retest search bounds, and fill timestamp. |
| HIGH | `run_long_window.py` (missing) | Long-window trigger, RSI confluence, and HTF regime gates use closed bars only | NOT_IN_DATA: file absent; directory inventory has no such file | Restore the registered file and independently verify each timeframe?s completed-bar alignment and shift/index operations. |
| HIGH | Both missing runners | Retest window and fee math are correct | NOT_IN_DATA: neither implementation can be inspected; result prose is not implementation evidence | Restore source; compare entry/exit prices, fee application per side, and exact eligible retest bars against the preregistration. |
| LOW | `RESULT.md`, `RESULT_LONG.md` (read) | Study reports describe underpowered/inconclusive results and do not claim a confirmatory pass | MATCH: report text says INCONCLUSIVE and cites blocked power gates; this is only a report-text check, not validation of the missing runners. | None for this narrow claim. |

## Limitations and close

No PASS or FAIL on implementation behavior is supportable. The available `study.py` and `study_long.py` are differently named artifacts; treating them as the registered runner versions without provenance would not independently audit the specified files. Restore the two registered scripts to the lab work tree and rerun this audit. Card left not done because the required audit inputs are missing.
