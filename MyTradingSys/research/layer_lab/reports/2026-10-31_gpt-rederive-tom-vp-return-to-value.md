# BLOCKED - independent VP return recount

## Verdict

BLOCKED. I could not complete an independent recount from the permitted BTCUSDT 1-minute DEV archives, so none of the headline values can be classified SAME or DIFFERENT.

## What was checked

- Read the preregistration: `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/PRE_REG.md:12-22` (event, outcome, placebo and statistics); DEV window at `PRE_REG.md:42`.
- Read `MyTradingSys/backtest/layers/FORMULAS.md:422` (profile), `FORMULAS.md:482` (placebo), and `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/RESULT.md:15-16,53-55`.
- Confirmed monthly BTCUSDT 1m zips for 2022-01 through 2024-06 are present under `F:/MTS/data/candle_close_dev_2022_2024/`. No post-2024-06 bars were used.
- The preregistration names `Dumps/backtest/raw_1m_2022/klines` (`PRE_REG.md:34`), which the run instructions disallow as a DEV source. I attempted to recount directly from the supplied monthly archives. The independent aggregation script did not complete within the execution window; the initial version repeatedly scanned every minute for each 5-minute slot and was stopped for excessive runtime. The optimized rerun could not be launched because its PowerShell command quoting failed. No values from the study implementation were used to fill this gap.

## Headline comparison

| RESULT.md headline | Independent value | Status | Evidence |
|---|---:|---|---|
| Part A real return share 57.2% | NOT COMPUTED | BLOCKED | `RESULT.md:15`; definitions `PRE_REG.md:12-16`; aggregation attempt failed as described above |
| Part A placebo return share 46.8% | NOT COMPUTED | BLOCKED | `RESULT.md:16`; placebo rule `FORMULAS.md:482` and `PRE_REG.md:17` |
| Part B N=3 share 51.2% | NOT COMPUTED | BLOCKED | `RESULT.md:53`; acceptance/outcome rule `PRE_REG.md:18` |
| Part B N=6 share 47.8% | NOT COMPUTED | BLOCKED | `RESULT.md:54`; acceptance/outcome rule `PRE_REG.md:18` |
| Part B N=12 share 45.5% | NOT COMPUTED | BLOCKED | `RESULT.md:55`; acceptance/outcome rule `PRE_REG.md:18` |

## Finding

The permitted DEV inputs are present, but this run did not produce a trustworthy independent recount. The task remains open; no completion command was run.
