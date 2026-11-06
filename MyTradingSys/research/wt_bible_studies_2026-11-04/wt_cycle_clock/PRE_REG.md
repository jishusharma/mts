# PRE_REG: WT cycle clock (Card 3, descriptive, count-only; design copied unchanged from ../SPEC.md Card 3)

Card `wt-cycle-clock`. Order disclosure: the first `study.py` run happened before this file was committed (single run, design taken verbatim from SPEC.md, nothing tuned; there is no hypothesis to tune toward). No fees, no edge claim, no PASS/FAIL.

## Parameters (every one labelled)
| Parameter | Value | Label |
|---|---|---|
| WaveTrend | 10/21/4, bands +-53/+-60, `layers/wavetrend/wavetrend.py` only, WARMUP 200 | SOURCED LazyBear (FORMULAS s20) |
| Valid dot | cross with prior-bar wt1 beyond +-53, closed bars; ALL valid dots used, no 48-bar dedup (descriptive clock) | OURS (Bible) |
| TFs | 5m, 15m, 30m, 1h, 4h, BTCUSDT, Binance 1m resampled | SOURCED SPEC |
| Cycle | valid bottom up-cross to the last valid top before the next bottom; length = hours between them | OURS (Bible rule, SPEC) |
| Median cycle | per TF, DEV; age unit = hours since last valid dot / that median | OURS |
| Age bins | 0-0.25, 0.25-0.5, ... 1.25-1.5, >1.5 median cycles | SOURCED SPEC |
| State and target | every closed bar: last valid dot type + age bin; time (hours) to the next opposite-type valid dot and close-to-close raw % move to it (signed as price change, not direction-adjusted); median, p25, p75, n_bars, n_episodes (distinct last dots; bars of one episode are autocorrelated, so n_episodes is the honest n) | OURS |
| Censoring | bars with no later opposite dot inside DEV are dropped (counted in meta.json) | OURS |
| Cycles per week | cycles / weeks from first non-NaN WT bar to the last DEV bar | OURS |
| Windows | DEV 2022-01-01..2024-06-30 (splits.py) only; PRE_DEV is not on disk so not used; VALIDATION/HOLDOUT never loaded | SOURCED backtest/splits.py |
| Cost | none | no returns are claimed |

**Seen bars (SPEC line 5, repeated):** the coordinator's scratch cycle-frequency counts (Card 3 candidate numbers) were taken on BTCUSDT 2020-01..2026-11 bars, which include VALIDATION and sealed HOLDOUT. This study counts DEV only; the candidates are checked, not copied, and any later VALIDATION read of cycle frequency is NOT a clean first look.

## Power gate
`prereg_gate.py --n 126 --sd 1.0 --cost 0 --m auto --new-cells 0` printed `MDE 0.403 R vs max plausible 0.3; n needed 228: BLOCK`. The gate tests an edge claim against Holm family size; this card tests no hypothesis (no Holm, no p-values, no fees), so the BLOCK does not apply to a count table and is recorded here instead of a BLOCKED.md. Consequence: no sentence of the result may read as an edge; 4h episodes are very few (see n_episodes) and are flagged.

## Context
Operator's rule: trade with the cycle direction; the clock says where in the cycle we are. Regime: research_kit.regime_mix_line over DEV weeks (half n/a: weekly/monthly RSI history before 2022-01 not on disk). Phase = last valid dot type; age in median cycles of the same TF.
Regime mix: 130 weeks: bull 16 (12%) | bear 0 (0%) | range 49 (38%) | n/a 65 (50%)
