# BTC WaveTrend behaviour atlas and confluence study: bounded spec (2026-10-17)

Operator direction (OPERATOR_DIRECTION.md): discover how BTC behaves by timeframe/regime in and around the bands before any strategy; confluence only where the data shows structure; plain/extreme crosses are CONTROLS. This spec fixes causal definitions. `wavetrend-prereg-counts` freezes <= 12 cells from a count-only pass; `wavetrend-dev-atlas` runs once. Parameters 10/21/4, hlc3, +/-53/60 are SOURCED (PARITY_CONTRACT s2); every other number here is OURS (incl. EMA(200) trend state, 200 random draws, <= 3 bins, <= 12 cells), chosen on DEV counts only.

## 1. Data and clocks
Binance BTCUSDT perpetual klines (research tape, free public data), TF in {5m, 15m, 1h, 4h, 1d} (T061 scope; prereg-counts drops any TF whose independent episodes cannot reach its MDE). DEV only (to 2024-06-30). Event time `t_ev` = close time of the signalling bar. Features use bars <= `t_ev`; HTF features use the last closed HTF bar. Outcomes use bars after `t_ev` only; first price = next bar open. Every DEV read is logged in `research/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv`. VALIDATION and HOLDOUT: zero reads in these cards.

## 2. Events (causal; one row = one independent episode, never one bar)
| id | Event | Definition at `t_ev` |
|---|---|---|
| A1 band arrival | first bar with wt1 >= L (or <= -L), L in {53, 60}, after >= R_out bars outside the zone (R_out OURS from counts) | the episode lasts until wt1 re-enters below L; later bars are not new events |
| A2 turn-in-zone | inside an open A1 episode, first bar where wt1 turns (wt1[t] < wt1[t-1] for the upper zone) | the episode maximum is NOT known yet: depth is an outcome |
| A3 zone cross | wt1/wt2 cross (contract convention) while wt1 at t-1 is beyond L | the plain LazyBear signal, a CONTROL |
| A4 re-entry | wt1 crosses back through L toward the centre | |
| B1 centre cross | wt1 changes sign | |
| B2 centre test | wt1 comes within +/-c of 0 and leaves on the side it came from (c OURS) | confirmed at the leaving bar |
| C1 divergence | confirmed price pivot (k right-hand bars, k OURS) with the WT pivot making a lower/higher extreme; regular first, hidden later | `t_ev` = confirmation bar (pivot + k), never the pivot bar |
| C2 structure | second WT peak in a band lower (upper zone) than the first, both confirmed pivots, gap <= G bars | `t_ev` = confirmation of the second pivot |

## 3. Context (features, bars <= `t_ev` only)
Regime: trailing realized-volatility tercile and trend state (close vs EMA(200) of the same TF, plus slope sign). HTF state: WT zone of the next-higher TF at its last closed bar. Participation: volume vs the TRAILING mean (bars <= `t_ev` only, e.g. last 20 days) of the same UTC time slot. Hour slot. Each variable cut into <= 3 bins; edges are set once on DEV counts and frozen in PRE_REG (a mild in-DEV selection, disclosed; the regime label of a bar itself uses trailing data only).

## 4. Outcomes (measured after `t_ev`, gross, implied direction, no fees yet)
For each horizon H in a small frozen set (OURS, starting set 4, 12, 48 bars; final set frozen in PRE_REG): signed return open(t+1) to close(t+H); MFE and MAE from bar highs/lows over t+1..t+H (bar extremes, so upper bounds; flagged); response time = bars until wt1 re-crosses wt2 or reaches 0 (censored at H); full excursion depth = max |wt1| over the episode (outcome only: how far it reaches, where it reverses); reversal hit = signed return > 0 at H, with Wilson CI. No stops or targets in this study.

## 5. Arms per cell (same eligible clock)
(1) WT event alone, (2) context alone (same bin, no WT event, matched on hour of day), (3) conjunction, (4) random clock (random bars matched on TF, hour of day and regime bin, 200 draws). Without arm 4 nothing is read. Report N, independent episodes (clustered by day), rate and mean with CI, MFE/MAE medians, response time, realised MDE; Holm across the frozen cells. The conjunction must beat its WT-alone arm, its context-alone arm and the random clock, else "no incremental information".

## 6. Bound
<= 12 frozen cells; each variant (L, TF, bin edge, k, c, G) is its own trial row in the ledger; verdicts.py aliases {WT, wave_trend, wavetrend, LazyBear, cipher}. Cells with episodes below the MDE are reported "underpowered", not tuned. Output is a behaviour table, not a verdict; any strategy needs its own PRE_REG, venue fees/funding, VALIDATION once, HOLDOUT sealed.

## 7. Kept separate (not in this study)
BTC-author stop/target variant (TrendCrypto2022: 3-bar-low stop, 1:1.5), causal divergence strategy, volume/VWMA family, Supertrend/MTF family.
