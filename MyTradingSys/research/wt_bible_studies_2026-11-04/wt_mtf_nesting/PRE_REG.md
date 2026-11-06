# PRE_REG: WT multi-timeframe cycle nesting (Card 2, frozen 2026-11-06 before any return was computed)

Card `wt-mtf-cycle-nesting`; design copied from `../SPEC.md` Card 2 (fixed in bbaa2d3f1 after Gemini FIX-FIRST). Code `study.py` (this folder). Only event COUNTS were read before this freeze (`counts.csv`, `regime_mix_count.txt`). `verdicts.py check` on the family words: no prior row.

## Parameters (every one labelled)
| Parameter | Value | Label |
|---|---|---|
| WaveTrend | 10/21/4, K 0.015, bands +-53/+-60, `layers/wavetrend/wavetrend.py` compute() (golden-tested), WARMUP 200 bars | SOURCED LazyBear (FORMULAS s20) |
| Valid dot | wt1/wt2 cross with PRIOR-bar wt1 beyond +-53 (bottom: up-cross, top: down-cross), closed bars | OURS (Bible) |
| Data | BTCUSDT Binance 1m resampled to 5m/15m/30m/4h; files from 2022-01-01 only, no PRE_DEV warm-up on disk | OURS |
| Dedup | after an event the same side on the same TF is skipped for 48 bars | OURS (SPEC) |
| 30m phase | last 30m valid dot (all dots, not deduped) closed at/before the entry bar close: bottom = UP, top = DOWN | OURS (Bible) |
| Age | hours since that dot / median 30m cycle length measured on DEV (cycle = valid bottom to last valid top before next bottom); bins 0-0.5, 0.5-1, >1 | OURS |
| 4h slope | sign(wt1 of last closed 4h bar - wt1 three 4h bars earlier); 0/NaN = gate unknown, dot not nested | OURS |
| Entry / exit | close of the dot bar; exit close 12 bars of the entry TF later; long on bottom, short on top | SOURCED SPEC (exit 12), OURS (entry at close) |
| Nested | bottom dot with phase UP and slope up, or top dot with phase DOWN and slope down; all other known-gate dots are REJECTED | OURS (SPEC) |
| Arms | nested; phase_only; slope_only; age bins (each on nested trades); baseline (all deduped dots) | SPEC |
| Cost | 0.14 % round trip, net = gross - 0.14 | SOURCED `wavetrend_c30_retest_2026-11-04/PRE_REG.md`, research_kit.TAKER_RT_PCT |
| Statistic | per arm and TF: mean net, 95 % day-block bootstrap CI (resample UTC days, B=4000, seed 20261106); difference of means arm vs complement (nested vs rejected = primary), same bootstrap over the union of days, two-sided bootstrap p | OURS (SPEC) |
| Holm | m = 232 from prereg_gate.py `--m auto --new-cells 12` (12 = 6 arms x 2 TF) | OURS |
| TFs | 5m and 15m | SOURCED SPEC |
| Windows | DEV 2022-01-01..2024-06-30 via splits.py; loader end = DEV_END; VALIDATION read at most once only if the DEV rule below passes; HOLDOUT never loaded | SOURCED backtest/splits.py |

## Power gate (prereg_gate.py, before any return; counts from `study.py --pass count`, BTCUSDT DEV)
Counts: 5m baseline 3468, known-gate 3340, nested 544 (370 days), rejected 2796 (868 days); 15m baseline 1128, known 1085, nested 173 (171 days), rejected 912 (695 days). Median 30m cycle 43.5 h (161 cycles).
Inputs: n = nested days, sd OURS 0.25 % (5m) / 0.45 % (15m) typical 12-bar sd (not an outcome), cost 0.14, max plausible gross 0.30.
```
5m : n 370 sd 0.25 m 232 z_holm 3.700 MDE 0.059 R + cost 0.14 = 0.199 vs max plausible gross 0.3; n needed 50   PASS: may freeze
15m: n 171 sd 0.45 m 232 z_holm 3.700 MDE 0.156 R + cost 0.14 = 0.296 vs max plausible gross 0.3; n needed 163  PASS: may freeze
```
(15m passes narrowly.) Exit code 0 on both.

## Verdict rule (OURS, frozen)
- A TF PASSES on DEV only if the primary difference (nested minus rejected) has Holm p < 0.05, bootstrap CI lower bound > 0, AND the nested net mean > 0 (a gate that only rejects losers is not an edge). DEV-pass alone is not PASS: VALIDATION (once, same code) must confirm sign and CI > 0 raw; this study run reads DEV only, so the ceiling is INCONCLUSIVE (DEV-pass, VALIDATION unread).
- FAIL: no TF has Holm p < 0.05 with diff > 0 and both TFs adequately powered (gate PASS above).
- INCONCLUSIVE otherwise. Phase_only / slope_only / age bins are descriptive controls. No result is a trading claim.

## Context
Regime: no regime gate; the operator's rule is to trade with the higher-timeframe cycle direction, and the window's regime is stated by the Regime mix line below (research_kit.regime_mix_line, step 3pc; half the weeks n/a because weekly/monthly RSI history before 2022-01 is not on disk, the strict Malkan band gives no bear weeks).
Phase: the gate under test: 30m cycle phase (last valid 30m dot: bottom = UP, top = DOWN), its age in median cycles, plus the 4h wt1 slope sign (OURS, Bible).
Session: none, because the primary read is nested vs rejected dots per TF and a session split would leave too few nested trades per cell.
Entry: the valid 5m or 15m dot bar close, exit 12 bars of the entry TF later; no retest entry (OURS, SPEC); the first ~33 days of 2022 have no 4h slope (warm-up) and those dots are excluded as unknown gate (5m 128, 15m 43).
Regime mix: 130 weeks: bull 16 (12%) | bear 0 (0%) | range 49 (38%) | n/a 65 (50%)
Session / phase: phase = 30m last-dot side, age in median cycles; the first ~33 days of 2022 have no 4h slope (warm-up) and are excluded as unknown gate (5m 128, 15m 43 dots).
