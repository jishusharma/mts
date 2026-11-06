# PRE_REG: WT 30m lower-high divergence short (operator setup), frozen 2026-11-06 before any return was computed

Card `wt30-lower-high-divergence-short`. The design is SPEC.md Card 1 (`../SPEC.md`, commit bbaa2d3f1), copied by reference: event, his-context subset, 13 feature bins + 1 subset (m cells = 14), bin edges, fee-net 0.14 % RT (SOURCED), 24-bar exit, first-touch -1 %/+1 % secondary, same-window placebo. Parameters keep the SPEC labels (WT 10/21/4, +-53/+-60 and the 3-wave count SOURCED; every other number OURS).
Code `study.py` (WT from `backtest/layers/wavetrend/wavetrend.py` only; spot BTCUSDT 1m from F:/MTS/data/bigtrade/spot_raw, resampled to 30m and 4h; 2020-01..2021-12 bars are warm-up/context history only, no event scored there). Only event COUNTS were read before this freeze (`counts.csv`, `regime_mix_count.txt`).
Windows: SOURCED `backtest/splits.py`: DEV 2022-01-01..2024-06-30; the loader end is DEV_END, VALIDATION and HOLDOUT are never loaded by `--pass dev`.
Choices fixed here (OURS): the earlier cross is the most recent qualifying down-cross in the 48 h; "wt1 at least 10 higher" = wt1[earlier] - wt1[confirm] >= 10; drop size = min wt1 strictly between the crosses; top dot = down-cross with prior-bar wt1 >= 53, strictly before the confirming bar; 4h slope = wt1 of the last closed 4h bar minus wt1 three 4h bars earlier (as Card 2); first-touch checks bar highs/lows, stop first if both in one bar.

## Seen bars and confirming target
BTCUSDT 2020-01..2026-11 was already counted by the coordinator (disclosed in SPEC line 5). This setup on BTC VALIDATION and HOLDOUT bars is counted as READ, not a clean first look; no BTC VALIDATION read here is a confirmation.
Unseen confirming target (named before any run): the same frozen rule on ETHUSDT over VALIDATION 2024-07..2025-06 (never counted), only if ETH has full DEV coverage on disk, else NOT_IN_DATA; or a BTC forward window starting after the last bar the coordinator read. HOLDOUT is not loaded; the missing `holdout_reads.csv` row is added through `splits.read_holdout` before any such read.

## Power gate (`prereg_gate.py --m auto --new-cells 14`, run before any return)
DEV counts (`counts.csv`, event-days, BTC 30m): unconditional 183; his-context 146; largest marginal cell rsi_lower 118; smallest 31 (08-13 UTC).
```
python scripts/dev/prereg_gate.py --n 183 --sd 1.8 --cost 0.14 --m auto --new-cells 14
n 183 sd 1.8 m 234 z_holm 3.702 MDE 0.604 + cost 0.14 = 0.744 vs max plausible gross 0.3; n needed 2611
BLOCK: do not freeze (exit 1)   # n=118 also exit 1
```
sd 1.8 % = typical BTC 24-bar (12 h) return sd, OURS, not a study outcome; units % (no stop, as the c30 study). m = repo-wide DEV count 220 + 14 new cells.
Consequence: the card step says exit 1 = stop. No `--pass dev` is run; BLOCKED.md holds the numbers. Verdict: INCONCLUSIVE (underpowered), no PASS or FAIL claim.

## Context
Operator rule (Bible, verbatim in `system/layer_bible/wavetrend.md`): up-move to the red bands, WT fails to reach the centre, three waves above 0, dips below 0, rises again with higher price and lower WT = divergence short; the green line coming down confirms. Regimes: the setup is a counter-trend fade; where regimes differ is the point of the 4h slope and his-context cells (not run).
Regime mix: 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)  (DEV, research_kit.regime_tag, `regime_mix_count.txt`; no bear week in DEV, so bear-regime shorts are untestable here).
