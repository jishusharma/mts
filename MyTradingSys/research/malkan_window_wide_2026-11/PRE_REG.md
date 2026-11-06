# PRE_REG: Malkan window bands with wide pivots (strength 3), 10 symbols, fee-net, DEV (frozen 2026-11-06, before any count or return)

Card `malkan-window-comparison-needs-a-wider-p`. Follows `malkan_window_dev_2026-11` (adjacent strength-1 pivots left the OURS bands with 4 events).
Default window 3-10 stays unchanged whatever this says. Code `wide.py`, tests `test_wide.py` (written first, failed before wide.py existed).

## Arms and parameters

| Parameter | Value | Label |
|---|---|---|
| Bands (bars between swings, both swings inclusive) | S3_10 / B11_12 / C13_18 / D19_50, unchanged | S3_10 SOURCED (Malkan), others OURS |
| Pivot strength | 3 bars each side, strict close extreme, known at b+3, event bar = b+3 (causal) | OURS |
| Divergence | regular, close to close, RSI 14, any RSI difference, consecutive same-kind swings | SOURCED rsi_divergence convention |
| Symbols | BTC ETH SOL BNB XRP DOGE ADA AVAX LINK LTC, 1m resampled to 1h and 4h (full UTC buckets) | OURS |
| No-signal symbol | fewer than 7200 1h bars in DEV: excluded and named in symbols.json | OURS (card) |
| Window | DEV 2022-01-01..2024-07-01 only; loader refuses an end past DEV and never opens a later month file | SOURCED splits.py |
| Entry / exit | close of the event bar; exit close 10 bars later | OURS, NO-SOURCE (carried) |
| Cost | 0.14 % round trip (`research_kit.TAKER_RT_PCT`; `fees.py` taker 2 x 0.05 % = 0.10 % is the fee part) | SOURCED |
| Stats | cluster = symbol x UTC day; CI mean +- 1.96 SE; Holm over 16 cells (4 bands x 2 TF x 2 sides) added to the repo-wide DEV m (verdicts.py) | SOURCED research_kit |
| Survivor | n >= 30, >= 20 clusters, net mean > 0, Holm p < 0.05 | OURS |

## Order and gate

1. `wide.py --pass count`: events and days per (TF, band), sides pooled; pooled unconditional 10-bar return sd per TF on all bars (measured, not a placeholder).
2. Power gate per (TF, band): MDE = (z_holm + 0.84) * sd / sqrt(days) from `scripts/dev/prereg_gate.py` (same function, m = repo-wide DEV count + 16), BLOCK when MDE + cost > 0.30 %.
3. `--pass dev` computes returns ONLY for (TF, band) that PASS. Bands that BLOCK get counts and the gate line, no return is read.

Verdict rule: BLOCKED when every band blocks; INCONCLUSIVE when some band is run but none survives with a blocked family remaining; PASS only with a survivor in a passing band; FAIL only when all bands pass the gate and no cell survives. Verdict word first in RESULT.md.

## Context
Regime: not a filter; window regime mix reported as context (research_kit.regime_tag, as the 11-06 DEV study).
Phase: none, left to a later re-run.
Session: none, left to a later re-run.
Entry: signal-bar close only; no retest entry (OURS).
