# Trust re-check: gpt-formulas-rederive ? 2026-10-25

**BLOCKED ? cross-vendor reviewer requirement is unmet.** The independent arithmetic, source comparison, test run, and scratch mutation are complete. The result cannot receive VERIFIED-C2 because the producer and reviewer are both CODEX/GPT (OpenAI); the read-only task brief requires a different vendor (Gemini or Claude). The exact producer model is not recorded in the available provenance.

## Provenance and reviewer

- Producer: CODEX/GPT, established by the supplied read-only task pack, `trust-recheck-gpt-formulas-rederive.md:26`; the original result is titled GPT re-derivation (`FORMULAS_REDERIVE.md:1`). The producer's exact model ID is not recorded there.
- Reviewer: OpenAI Codex, GPT-6 family for this session. This is the same vendor as the producer, so it does not meet the brief's cross-vendor independence condition. A Gemini or Claude review is still required.
- No outcomes, holdout data, or market data were read or rerun.

## Independent values and comparison

Before opening code, I read only `FORMULAS.md` sections 13 and 17 and wrote the arithmetic to `MyTradingSys/research/layer_lab/trust_recheck_gpt_formulas_rederive_calc.py.txt`. The stdlib script produced `net_rr=1.857142857142857` and `s13_long_net=0.008400000000000`.

| Check | Independent value | Repo / recorded value | Result and evidence |
|---|---:|---:|---|
| S17 net R:R, entry/target/stop 100/104/98 | 1.857142857142857 | Repo `1.857142857142857`; prior table `1.85714` | **MATCH** ? `FORMULAS.md:403-405`; `mts_math.py:78-85`; `FORMULAS_REDERIVE.md:17`. |
| S13 long 100?101, records exactly as printed at t=8h and t=16h | 0.0084 | `net_return` raises `ValueError` because loaded funding begins at 8h while the hold begins at 0 | **MISMATCH (input-span guard)** ? arithmetic is `0.01 - 0.0010 - 0.0002 - (0.0001 + 0.0003) = 0.0084` (`FORMULAS.md:350-353`). The exact input is rejected by `trade_costs.py:24-29`; same mismatch is recorded at `FORMULAS_REDERIVE.md:13,24`. Adding a zero-rate t=0 record satisfies the guard and returns `0.0084`, matching arithmetic (`FORMULAS_REDERIVE.md:14`). |
| Test fixture coverage for S13 | n/a | Fixture includes a t=0 funding record | **MATCH** ? `test_trade_costs.py:5-7,40-47` tests the numeric result with a covered span; it does not test the exact two-record worked input. |

The section 13 mismatch is confirmed by calculation: the value itself is correct, but the exact worked input is outside the implementation's accepted coverage span. The zero-rate pad is outside `(t_in, t_out]`, so it does not change the funding sum.

## Tests and mutation

Unmodified command:

```text
python -m pytest MyTradingSys/tests/test_mts_math.py MyTradingSys/backtest/layers/positioning/test_trade_costs.py -q
93 passed, 1 warning in 0.22s
```

The warning was pytest cache creation (`WinError 183`); test execution passed.

Scratch-copy mutation: copied only the relevant runtime, fee, trade-cost, and test files to a temporary directory; changed the scratch `fees.py:23` constant from `DERIBIT_TAKER = 0.0005` to `0.0006`; then ran the same two test files with `-p no:cacheprovider`. Result: **exit 1; 3 failed, 90 passed**. The failures were `test_net_rr_fee_model_long`, `test_net_rr_fee_model_short_mirrors_long`, and `test_net_rr_tight_stop_costs_more_r` in `test_mts_math.py` (expected constants at lines 225-250). Thus the tests catch this fee-constant mutation. The workspace `fees.py` was not changed.

## Findings

| Severity | File:line | Finding | Evidence | Proposed disposition |
|---|---|---|---|---|
| MED | `FORMULAS.md:353`; `trade_costs.py:24-29` | Worked S13 funding records do not span the hold under B103's guard. | Exact input raises; zero-rate t=0 pad returns the independently computed 0.0084. | Keep as a documented spec/guard mismatch for the cross-vendor reviewer; no audited source edited. |
| HIGH | `trust-recheck-gpt-formulas-rederive.md:26` (read-only pack) | Same-vendor review cannot satisfy the stated trust check. | Producer is CODEX/GPT; this reviewer is OpenAI Codex/GPT-6. | Obtain Gemini or Claude re-derivation before proposing VERIFIED-C2. |

**Tag proposal: DISPUTED pending the required cross-vendor re-check.** This is not a positive trust receipt. No audited source files were edited. The requested `tasks.py done` step was withheld because the instructions explicitly say not to mark a blocked card done.
