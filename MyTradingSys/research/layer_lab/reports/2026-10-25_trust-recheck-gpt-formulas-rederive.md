# Trust re-check: gpt-formulas-rederive (2026-10-25)

**Verdict: BLOCKED - independent vendor requirement is unmet.** The available reviewer in this session is Codex / GPT, the same vendor family as the producer. The task requires a different reviewer vendor (Gemini or Claude), so these local findings cannot support a VERIFIED-C2 tag. No holdout or outcome data was read or rerun; no audited source file was edited.

## Identity and independent calculations

Producer: CODEX / GPT, identified in the read-only task pack and registry context. Reviewer: Codex / GPT (this session); same vendor, therefore not an eligible independent reviewer. No Gemini or Claude reviewer/model is available in this session.

Before comparing to implementation, I derived these values directly from FORMULAS.md sections 13 and 17 using exact rational arithmetic in a short Python stdlib calculation:

| Example | Independent derivation | Repo/table comparison | Status |
|---|---:|---|---|
| S17 net R:R, entry 100 / target 104 / stop 98 | cost = 2 * 0.0005 * 100 = 0.1; (4 - 0.1) / (2 + 0.1) = 13/7 = 1.857142857... | Section 17 and `calculate_net_rr` default agree; prior table row is 1.85714. [FORMULAS.md:400-404](../backtest/layers/FORMULAS.md); [mts_math.py:78-85](../../runtime/mts_math.py); [fees.py:23](../../backtest/fees.py); [FORMULAS_REDERIVE.md:17](../gpt-formulas-rederive/FORMULAS_REDERIVE.md) | MATCH |
| S13 long 100 to 101, t_in=0, t_out=16h, funding at 8h=0.0001 and 16h=0.0003 | 0.01 - 0.0010 - 0.0002 - (0.0001+0.0003) = 0.0084 | Formula and table arithmetic agree, but repo call rejects the exact example: first funding time is 8h, so `t_in < funding[0][0]` triggers B103. A zero-rate record at t=0 satisfies the span guard and yields 0.0084 without changing the open-closed interval sum. [FORMULAS.md:343-353](../backtest/layers/FORMULAS.md); [trade_costs.py:20-29](../../backtest/layers/positioning/trade_costs.py); [FORMULAS_REDERIVE.md:13-14](../gpt-formulas-rederive/FORMULAS_REDERIVE.md) | MISMATCH (example input vs guard; calculated, not a vote) |

This confirms the existing S13 mismatch. It is an input coverage contradiction between the worked example and the fail-closed span guard, not an arithmetic disagreement. The zero-rate padding control reproduces the expected formula result.

## Tests and fee mutation

The requested real-tree command passed: `python -m pytest MyTradingSys/tests/test_mts_math.py MyTradingSys/backtest/layers/positioning/test_trade_costs.py -q` -> **93 passed**. Pytest emitted a cache-path warning only.

The math tests pin the default fee indirectly through the S17 long and short expected results and the tight-stop case (`test_mts_math.py:227-250`). The positioning cost tests exercise their own Binance-style `fee_rt` default/arguments and do not import `DERIBIT_TAKER` (`test_trade_costs.py:41-55`), so they are not a direct guard on that constant.

For the fail-first probe, I copied the relevant `MyTradingSys/tests`, `runtime`, and `backtest` trees under a temporary directory inside the lab research tree, changed only the scratch `DERIBIT_TAKER` from 0.0005 to 0.0006, then ran the same two test modules. Result: **3 failed, 90 passed**; failures were `test_net_rr_fee_model_long`, `test_net_rr_fee_model_short_mirrors_long`, and `test_net_rr_tight_stop_costs_more_r`. The scratch tree was removed in the same script; the real fee file remained 0.0005.

## Tag decision

**Tag proposal: no VERIFIED-C2; BLOCKED pending a different-vendor reviewer.** The calculations and mutation probe support the stated MATCH/MISMATCH findings, but the required cross-vendor review cannot be claimed from this Codex/GPT session. Accordingly, this card is not marked done.
