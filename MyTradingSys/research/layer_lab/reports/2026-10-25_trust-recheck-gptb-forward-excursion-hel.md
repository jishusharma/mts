# Trust re-check: gptb-forward-excursion-helper

**Verdict: BLOCKED - independent check calculations match, but this run cannot satisfy the required different-vendor reviewer condition.** No VERIFIED-C2 proposal is made; the result tag remains unverified pending a non-OpenAI reviewer.

## Reviewer and producer

- Producer: CODEX / GPT, identified in the read-only card pack; archived producer card `MyTradingSys/system/tasks/archive/gptb-forward-excursion-helper.json` records model `gpt-6-luna`.
- Reviewer: OpenAI, GPT-6 (current Codex session; exact serving model variant is not exposed to this session).
- Vendor separation: **NOT MET**. This reviewer is from the same vendor as the producer, so these checks cannot authorize VERIFIED-C2 under the card requirement. The earlier report `MyTradingSys/research/layer_lab/reports/2026-10-23_trust-recheck-gptb-forward-excursion-hel.md` was absent on disk when checked.

## Checks

Read `forward_excursion/REPORT.md`, the archived producer report dated 2026-10-16, the producer task JSON, `event_table.py`, and `test_event_table.py`. No market data, outcome, or holdout data was read or rerun.

Independent short-script cases used entry close 100, R=2 and one subsequent bar. Calculations and function output:

| Case | Hand calculation | Function output | Result / source |
|---|---|---|---|
| Long target touched first: high 103, low 99 | MFE=(103-100)/2=1.5R; MAE=(100-99)/2=0.5R; target first | `mfe_r=1.5, mae_r=0.5, first_hit=target_1R, truncated=False` | MATCH; `event_table.py:30-44` |
| Short stop touched first: high 103, low 99 | MFE=(100-99)/2=0.5R; MAE=(103-100)/2=1.5R; stop first | `mfe_r=0.5, mae_r=1.5, first_hit=stop_1R, truncated=False` | MATCH; `event_table.py:30-44` |
| Long bar touches both: high 103, low 97 | MFE=1.5R; MAE=1.5R; stop has priority | `mfe_r=1.5, mae_r=1.5, first_hit=stop_1R, truncated=False` | MATCH; `event_table.py:38-44` |

The authored long/short fixtures have higher later highs/lower lows and their expected 2.0R MFE / 0.5R MAE are consistent with the implementation (`test_event_table.py:22-30`; source calculation `event_table.py:30-37`).

## Test and mutation evidence

- Real suite: `python -m pytest MyTradingSys/research/layer_lab/forward_excursion/test_event_table.py -q -p no:cacheprovider` -> **5 passed**.
- Test adequacy: the same-bar test asserts the exact required `stop_1R` output (`test_event_table.py:32-35`), so it detects reversal of the both-touch priority.
- Scratch mutation: swapped the two first-hit branches in temporary copies under the report directory; ran pytest with `--rootdir` set to that scratch directory. **Mutation killed**: `1 failed, 4 passed`; `test_same_bar_touching_both_levels_counts_stop_first` failed because mutant returned `target_1R`. Scratch directory was automatically removed.
- An initial scratch run under the Windows temp directory failed during pytest collection due to permission-denied traversal, before exercising tests. The workspace-rooted run above is the conclusive mutation result.

## Tag proposal

**BLOCKED; no VERIFIED-C2 proposal.** The calculations and mutation evidence match, but reviewer-vendor separation is a required condition and is unmet in this OpenAI/Codex session. Have a Claude- or Gemini-vendor reviewer re-derive before recording VERIFIED-C2. No mismatch found in the three checked cases.

Follow-up cards created: none.
