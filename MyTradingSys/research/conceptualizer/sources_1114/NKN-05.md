# NKN-05 context design (frozen before results)

Rule: weekly HM "red line down" = buy state (FzNDQm7wC_s 00:03:09, 00:03:12, a CLAIM) plus daily gate (Hyp B).
Nothing run, no outcome data read. Data/code paths verified (table below).
Changes versus the NK55 draft: Hyp B gate is AND (not OR); Hyp A is never tested pooled across phases; phase is the cell, not a filter row.

## Existence check (done 2026-11-14)
| Item | Status |
|---|---|
| Weekly bars, 20 spot coins | EXISTS only as 15m: `<local-path>` (2019-01 to 2026-11-13; AVAX/DOT/FIL/NEAR/SOL/UNI start 2020-08..10). Weekly = resample 15m, Monday 00:00 UTC to Sunday 23:59. `binance_spot_htf` has weekly for only 5 coins (BTC from 2017-08-14, Monday-anchored): use it ONLY to cross-check the resampler on BTC/ETH |
| Daily bars | resample the same 15m files (`binance_1d` holds only a BTC tail csv) |
| Fresh holdout | `binance_fresh/nk5_nyasia/*_5m.npz`: AAVE, ENJ, GRT, HBAR, MANA, SAND, THETA, XTZ are the 8 not in the 20 (date range NOT checked; worker prints it). HOLDOUT rows, run once |
| BTC phase label | EXISTS: `<local-path>` (date,label,cycle,...; 2010 to 2026-11-14; last rows provisional=True; 1400 early rows have empty label). Labels CAPITULATION, MARKDOWN, RELIEF, ACCUM-RANGE, MARKUP, DISTRIBUTION; cycle BEAR/BASE/BULL. Builder `research/btc_cycles_2026-11/cycles.py` (+ `test_spec_cycles.py`) |
| MTS_BRAINS_SPEC_1114.md | NOT FOUND in the worktree. Definitions below come from phase_daily.csv columns and cycles.py, not spec text |
| HM code | `research/nkp1-session-rules-phase-1114_2026-11-14/study.py::hm_state` (RSI9, EMA3 span, WMA21; buy = red < green). Reuse, add the "inside" test below |
| ATR | `study.py::atr_s` (Wilder). `backtest/layers/adx/adx.py` EXISTS but is NOT used (V2 decision) |
| Funding | `<local-path>` (ts,rate; 8h; from 2020-01-01), 23 coins; overlap with the 20 spot coins = 17 (no ALGO, FIL, NEAR) |
| OI | `<SYM>_oi_daily.csv` from 2020-09-02. DROPPED |
| Dropped as not computable or not existing | buy-zone-map levels (BTC-only, hand-drawn from today = look-ahead); 200-week SMA (too few weeks); 1D WaveTrend (duplicates HM); CBP lean (label only) |

## Phase tested
- Weekly decision. BTC phase label read at the week-open Monday row of phase_daily.csv. The worker must prove by a future-bar poke that the label at date d uses closes <= d-1 (if it uses d, shift one day). provisional=True rows never enter a result except forward.
- **PRIMARY cell PC:** label in {RELIEF, ACCUM-RANGE} AND cycle in {BEAR, BASE} (post-fall turn; OURS reading of NK's bear-to-bull framing).
- **Side:** long, weekly HM buy state; contrast = same coins in weekly HM sell state, same cell.
- **Controls (each alone, never pooled):** C1 buy in MARKUP; C2 buy in MARKDOWN; C3 buy in DISTRIBUTION; C4 sell state in PC; C5 matched random coin-weeks in PC (placebo, same week-of-year spread, 1000 draws); C6 neutral state in PC. Pooled all-weeks buy appears only as a labelled REFERENCE row (R0).
- CAPITULATION is not a cell (too thin per the 11-14 synthesis); its weeks stay in R0 only.

## Context conditions
1. HM state W (formula OURS; "red line down" SOURCED FzNDQm7wC_s 00:03:09 and 00:03:12): closed weekly bar, RSI9 (Wilder); green = EMA3 (span 3) of RSI9; red = WMA21 of RSI9. BUY = red < green AND red < RSI9. SELL = red > green AND red > RSI9. Else NEUTRAL (three states SOURCED B7iGQef_z6I 00:03:22; neutral is not short). "Inside" test fixed once: strict inequalities on both lines.
2. Weekly anchor UTC Monday 00:00 (OURS); state read on the closed Sunday bar; reference = next Monday open; forward windows 1, 2, 4 weeks (OURS; 4w is the only gating horizon).
3. Phase = PC, thresholds taken as-is from cycles.py (OURS, no re-tuning).
4. V1 BTC trend (rule SOURCED t1b_1h2QMXw 00:18:13 "trade with the index"; BTC proxy OURS): BTC weekly close > its weekly SMA20 (SMA not EMA: FzNDQm7wC_s 00:02:39). BTC itself exempt. Alts reported with and without.
5. V2 daily agreement (SOURCED fZvp72BBmRI 00:04:58 RSI(14) > 50; ysq6x0eCFvI 00:04:37 close above SMA20): last closed daily bar before entry, daily RSI14 > 50 AND close > SMA20. AND, because his entry gate is "HM must agree"; the draft OR is dropped.
6. Level split, weekly SMA50 (OURS; NK names no weekly level): L = SMA50 of weekly closes through week t, A = Wilder ATR14 of weekly bars. AT-ABOVE: |close-L| <= 1.0 A and close >= L; AT-BELOW: |close-L| <= 1.0 A and close < L; AWAY: otherwise. One value, no second band. Uses the no-first-touch-support idea (fZvp72BBmRI 00:18:39) as a split, not a veto.
7. Funding split (OURS, no NK source): trailing 3-day mean of 8h funding at the Sunday close; terciles computed on DEV only, frozen, applied to VAL. Descriptive only; 17 coins.
8. Dropped from the Context angle: overheat veto >86 (caption UNCONFIRMED), RSI30 recovery (different rule), 2-close persistence on HM (our invention; first-week-of-state events are reported as a descriptor instead), 1 ATR vs 20-week-low level.
9. HM formula is OURS, unverified against his chart (NK4/NK5 flag). Before any verdict: TradingView cross-check of 3 dated weekly BTC bars, table in RESULT. Until done the verdict label is UNVERIFIED-HM.

## Crypto translation
- Session open: week open Monday 00:00 UTC (OURS). Daily gate bars close 00:00 UTC. London/NY opens and expiry are dropped.
- Gap replacement: none; entry = next weekly open (continuous market). Event study needs no entries and is gross.
- Funding: descriptive crowding split (cond. 7), replaces expiry. OI DROPPED (from 2020-09 only, too few weeks inside PC; funding_cvd_fade already failed). Any funding separation is a new hypothesis for a separate registration, never an NK confirmation.
- BTC market filter: V1. Weak Nifty proxy (alts are BTC beta); BTC-own rows reported separately.
- Does NOT translate: "market does not go down" (index of 50 names vs one coin; ported as 4-week return and max-drawdown distribution only); weekly expiry; gap; options; ADX/WT layers.
- Headline metric is the excess over the unconditional forward return of the same cell weeks (crypto drifts), not the raw return.
- Cluster by calendar week and by BTC-phase spell; effective n is about 150-380 weeks, not coin-weeks. The draft's "adequate power" is withdrawn.

## Layer agreement
| Variant | Exact layer read | Code path |
|---|---|---|
| V0 rule alone | weekly HM state W inside the cell, nothing else | `study.py::hm_state` on weekly resample; phase from `phase_daily.csv` (cell, not a filter) |
| V1 | V0 AND BTC weekly close > weekly SMA20 | resampled BTC weekly; coin HM unchanged |
| V2 | V1 AND daily RSI14 > 50 AND daily close > SMA20 (Hyp B gate, AND) | `rsi` / `CX.rsi_wilder`, plain SMA on daily resample |
Report overlap (share of PC buy weeks kept by V1 and V2). The cycle layer is not a separate variant: it is already inside PC (the layers-angle V1 would contradict the cell). ADX/DI dropped: correlated with smoothed-RSI HM and adds a layer on about 4 cycles. Prior evidence (RSI-CONFIRM-LAYERS 0/56; matching direction did not beat mismatching) makes C4 the control for every variant.

## Level type
One primary level: weekly SMA50 (cond. 6); at-level = within 1.0 weekly ATR14; away = complement. Role: H-A2, buy-minus-sell gap larger AT-level than AWAY. If equal, the level adds nothing and NKN-05 reduces to the plain HM claim. Doubt: 1 ATR may cover 40-50% of weeks; not tuned.

## Timeframes
Native weekly (decision and forward windows) and native daily (V2 gate). 15m, 1h and 4h are NOT expressible: the claim is a weekly state; lower timeframes would be a different rule (NK4 already tested the intraday HM flip: FAIL). Fee-net rows (12 bp taker, 6 bp maker non-gating) only for the filtered-entry version: Monday open entry, 4-week hold, R = max(0.5%, 0.6 x weekly ATR14).

## Cells (weekly decisions; horizons 1/2/4w describe each cell, only 4w gates)
| ID | Phase cell | Variant | Level | Side/state | Role |
|---|---|---|---|---|---|
| P1 | PC | V0 | all | long, buy | PRIMARY |
| P2 | PC | V1 | all | long, buy | PRIMARY |
| P3 | PC | V2 | all | long, buy | PRIMARY |
| C1 | MARKUP | V0 | all | buy | CONTROL |
| C2 | MARKDOWN | V0 | all | buy | CONTROL |
| C3 | DISTRIBUTION | V0 | all | buy | CONTROL |
| C4 | PC | V0 | all | sell | CONTROL (contrast for P1-P3) |
| C5 | PC | placebo random weeks | all | long | CONTROL |
| C6 | PC | V0 | all | neutral | CONTROL |
| C7 | PC | V1 complement (BTC <= SMA20) | all | buy | CONTROL |
| R0 | all phases pooled | V0 | all | buy | REFERENCE (labelled) |
| L1-L3 | PC | V0 | AT-ABOVE / AT-BELOW / AWAY | buy | CONTROL (descriptive) |
| L4-L6 | PC | V0 | AT-ABOVE / AT-BELOW / AWAY | sell | CONTROL (descriptive) |
| F1-F3 | PC | V0 | all | buy, funding tercile low/mid/high | CONTROL (descriptive) |
| N1-N2 | PC | V0 and V2 | all | buy, fee-net filtered entry (Hyp B) | CONTROL (non-gating) |

Gates for P1-P3 on VAL (>= 2024-01-01): week-cluster bootstrap CI low > 0 on the 4w excess return (buy minus sell in PC); ex-best-5-weeks > 0; beats C5; same sign on DEV (<= 2023-12-31); Benjamini-Hochberg q <= 0.10 across P1-P3 only; HM TradingView check done. Fresh-holdout coins and post-2026-11-13 weeks run once, reported separately.

Count: 3 primary + 7 controls (C1-C7) + 1 reference + 6 level + 3 funding + 2 fee-net = 22.
**Total cells tried: 22**
**Primary cells: 3**

## Underpowered rule
A cell with n VAL < 100 coin-weeks is UNDERPOWERED, not FAIL. Additionally a primary cell with fewer than 20 distinct VAL calendar weeks cannot PASS (reported UNDERPOWERED-WEEKS). Print coin-weeks, distinct weeks and distinct BTC-phase spells beside every row; PC on VAL is expected to be thin.

## Open doubts
- MTS_BRAINS_SPEC_1114.md missing from the worktree; labels rely on phase_daily.csv, whose look-ahead behaviour is unproven (poke test) and whose last rows are provisional.
- Whether "red line" is WMA21 and whether "inside" means both lines; HM unverified against his chart.
- Whether NK meant the state to hold in all phases (then C1-C3 are the real test and PC is only our reading).
- One BTC label for all alts (alts lag or lead the cycle); weekly HM over 20 coins may reduce to BTC's own cycle.
- Universe is 20 spot coins (not 30) plus 8 fresh coins of unchecked history; survivorship bias (all coins listed now); stated rule: a coin enters from its 52nd week after listing.
- SMA50w 1 ATR band width; funding covers 17 of 20 coins; HM and SMA50 states are strongly autocorrelated.
- Prior is low: 0 of about 100 NK rows have passed.
