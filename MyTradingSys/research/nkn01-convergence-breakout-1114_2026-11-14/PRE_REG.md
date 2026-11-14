# PRE_REG nkn01-convergence-breakout-1114 (written and committed together with study.py and test_study.py, before any run on real data)

Operator order 2026-11-14 06:12Z: NK rules must not be tested blindly: context applied correctly, several angles (phases / context / crypto context / layers / levels). A mechanical all-bars test is not acceptable. Rule: NKN-01 convergence breakout long (video 5GZIshXnxW8), draft in `MyTradingSys/research/nk_stocktalk_1113/extract55/NK55_RULES_1114.md` Part 2. Design frozen in `nkn_design/NKN-01.md` (side-session notes local_62e478d7); copied below. No outcome data was read for this design.
Labels: SOURCED = NK video id + time. OURS = one fixed value, no grid, never NK's. NK never mentions WaveTrend, funding, ATR depth or weekly levels: those are OURS and come from the operator order, not from NK.
**Today's state: CBP lean is bearish and BTC cycle state is MARKDOWN, so the primary cell (RANGE coin phase x ACCUM-RANGE BTC cycle) is out of phase right now. No live or forward trading on this study.**

## Context
- Regime: BTC cycle label per date from `F:/MTS/data_cache/mts_brains/phase_daily.csv` (column `label`, built from closes through the previous day; the final provisional row is dropped), used as a label only. PRIMARY = ACCUM-RANGE. Reported per label and per split (DEV holds the 2022 bear, VAL is mostly bull-dip).
- Phase: coin-own phase per coin-day from data through the prior daily close, 3 states UP / DOWN / RANGE. UP = ADX14 >= 20 and DI+ > DI- and SMA20 slope (SMA20[j] / SMA20[j-5] - 1) > 0; DOWN = ADX14 >= 20 and DI- > DI+ and slope < 0; everything else RANGE. PRIMARY = RANGE. See "Phase definition" below.
- Session: none, because the rule is read on closed daily bars (4h control uses the 00/04/08/12/16/20 UTC grid); no session gate.
- Entry: next bar open after the SECOND consecutive close above the highest EMA of a tight EMA20/50/100/200 stack that formed after a fall, at-level (12-week low) in the primary cell; the 4h and limit-at-SMA20 rows are controls.

## Hypothesis
After a fall, price that closes twice above a tight stack of EMAs 20 to 200 on the same timeframe, near a prior-low level, with the coin in RANGE and BTC in ACCUM-RANGE, has positive fee-net expectancy. The level, the phase and the two layers (WaveTrend, funding) each have to add something. Pre-registered prediction for the level: at-level mean net R > away-from-level mean net R. If away is equal or better, the level adds nothing and the rule fails the level step.

## Phase tested
- PRIMARY: LONG only, DAILY timeframe, coin phase RANGE x BTC cycle ACCUM-RANGE, both read BEFORE the first close above the stack (see "Reading convention"). Why: a tight 20-to-200 stack forms after a base; NK says long only after a fall (5GZIshXnxW8 00:13:58) and a thin stack in sideways (00:06:03). The draft's "UP and RANGE" pooled two situations, so UP is a control (C4). The cycle label is BTC-only and is a label, never a coin's own trend.
- CONTROLS (each reported alone, never pooled into a primary cell, descriptive and cannot make anything PASS): see the cell table.
- Regime-mix block per split in RESULT: share of coin-days UP / DOWN / RANGE (from 2021-03-01), share of days per BTC cycle label, share of days BTC above its SMA200; flagged "mixed" if no single coin phase has over 50%.

### Phase definition (design item: thresholds "copied verbatim from the 11-14 studies")
No reusable coin-phase function exists in the 11-14 studies: nkp2 uses the BTC 6-phase label only, `combo-edge-miner` uses a BTC-structure UP/MIX/DOWN, and NK55's text gives "20-day MA slope with 5-day lag plus ADX14 >= 20 with DI direction, else RANGE" without numbers beyond ADX 20. The slope sign test and the lag of 5 days are therefore OURS and defined here once, before any run: slope = SMA20[j] / SMA20[j-5] - 1, threshold 0 (sign only); ADX14 and DI are Wilder (FORMULAS s30.1, sum-seeded; toy values are in the tests). ADX14 < 20 is RANGE as the design says; ADX >= 20 with DI and slope disagreeing is also RANGE ("else RANGE").

### Reading convention (stated before any run)
Signal bar s = the SECOND close above the stack max; f = s-1 = the FIRST close above. Coin phase and BTC cycle are read at the close before f's UTC day starts (daily bar of day(f)-1; for the cycle, the label of date day(f), which is built from closes through day(f)-1). Level L and ATR_D are read at the close before s's UTC day. WT is read at the last daily bar closed at or before the decision time (the close of s). Funding uses prints with timestamp <= the close of s.

## Context conditions (all from closed bars)
1. Stack: EMA20, EMA50, EMA100, EMA200 on the signal timeframe (EMA seeded with the first close; no signal in the first 211 bars). OURS (NK says 20 to 200, lengths between not stated).
2. Tight stack: (max EMA - min EMA) / close <= 3% on daily, <= 1.5% on 4h, at the trigger bar s. OURS. Idea SOURCED (5GZIshXnxW8 00:06:03 and 00:14:52).
3. Prior fall, shape: the close 10 bars before f is under the lowest EMA of the stack. OURS (10). Idea SOURCED (5GZIshXnxW8 00:13:58).
4. Prior fall, depth: (highest high of the 50 bars before f - F) >= 1.5 x ATR14[f-1], F = lowest low of the 10 bars before f. OURS (50, 1.5, ATR14 Wilder).
5. Trigger: second consecutive close above the highest EMA of the stack. Two-close idea SOURCED a8RP5ftOfGo 00:08:50 and IjU9PpqvrI8 00:14:58 (the 5GZIshXnxW8 spans 00:07:20 and 00:12:14 are UNQUOTED); the count of two for convergence is OURS-informed.
6. De-overlap: a new episode needs the first close above after a close back inside (built into f: close[f-1] <= stack max). n counts coin-episodes. Episodes of one coin whose trades overlap in time are all kept (OURS; the 72h cluster bootstrap handles the dependence).
7. Coin phase RANGE at the prior daily close (above). OURS.
8. BTC cycle ACCUM-RANGE at the prior close (MTS_BRAINS_SPEC thresholds, OURS).
9. Entry next bar open (OURS). Stop = under the lowest EMA of the stack at s (SOURCED), R = max(e - lowest EMA[s], 0.5% of e, 0.6 x ATR14[s]); stop price = e - R. Exit (blended): half at 2R (OURS), the rest trails under the lowest EMA (stop = max(initial, lowest EMA at the previous close), only after the half is booked), all out at the second consecutive close <= the highest EMA of the stack (SOURCED two-close). No time cap (NK has none); a position still open at the data end exits at the last close and is counted as censored. Fee 12 bp taker, 6 bp maker as a non-gating line.
10. Level condition (below).
11. Short mirror (C7 only): prices mirrored, stack above price, close under the lowest EMA twice, the 10-bar-before close above the stack, rise depth, level = highest high of 12 weeks, stop above the highest EMA.

Considered and moved out of the gate: BTC index filter (control C8; BTC itself is excluded from C8); HM gate and HM overheat > 86 (formula unverified, 86 unconfirmed: NOT RUN); "no entry at first-touch support" (no level definition: NOT RUN); sideways-run condition and BTC SMA200 slope leg (redundant with the cycle state: dropped).

## Crypto translation
Session open not used. Gap DROPPED, expiry DROPPED (no substitute invented). "Price fell first" kept (price structure only). Market filter: BTC cycle label as a label (primary) and BTC close > SMA20 and SMA50 as control C8, never as the coin's own phase. Funding: V2 only, mean of the last 3 settled 8h prints with timestamp <= the signal bar close; a crowding check, not an expiry analogue. Open interest: not used (daily only, from 2020-09, earlier studies found no OI-class separation). Does NOT translate: gap, expiry, weekly options, value area/POC on daily bars. Prices: Binance spot (longest history for all 20 coins); spot vs perp is an open doubt.

## Layer agreement (3 variants, each its own cell row)
- V0: rule alone with conditions 1-9 and the level condition. Reference row.
- V1: V0 + WaveTrend agreement. Daily WT1 at the last daily bar closed at or before the close of s: WT1 < +53 AND WT1 > WT2. Module `backtest/layers/wavetrend/wavetrend.py` `compute()` on the daily bars. The +53 constant is OB2 in that module's parameter block (SOURCED there: Crosses:9-12; verified 2026-11-14). WT1 > WT2 is OURS. WT is NaN in the first 200 bars (module warm-up): such signals fail V1. Counts of signals V1 removes are reported.
- V2: V1 + mean of the last 3 settled funding rates <= 0.03% per 8h (OURS; Binance baseline 0.01% is not the cutoff). Causal reader over `binance_futures/nkp1/<SYM>_funding.csv` (17 coins; ALGO, FIL, NEAR have no file: NO-DATA, removed from V2 only; counts shown). If V2 VAL n < 100: UNDERPOWERED, not loosened.
- Rejected: volatility compression, Bollinger width (restate the stack), 4h RSI >= 60, taker delta, session, OI, divergence, `ma_daily`, `funding_cvd_fade`, `oi_delta`.

## Level type
One primary level: L = lowest low of the 12 weekly bars fully closed before the signal bar s (weeks Monday 00:00 to Sunday 23:59 UTC, built from the closed daily bars of the same source; for 4h rows, weeks closed before the 4h bar's open). OURS (12). Not NK's: no NK quote ties this rule to prior-low support. At-level: |F - L| <= 1.0 x ATR_D (daily ATR14 Wilder at the prior daily close; OURS 1.0; a sweep below L of up to 1 ATR_D counts). Away-from-level = the complement (L or ATR_D unavailable: no label, in neither). Rejected levels: moving averages (circular with the trigger), pivots (NK2 failed), value area/POC, prior-day high/low, the BTC buy-zone map. No tuning of 12 or 1.0. Before any outcome is read, `study.py counts` prints counts and the at-level share per split (committed as counts.json).

## Timeframes
Daily: primary, the only gated rows. 4h: control C6 only (R floor 1.2% instead of 0.5%, OURS, a deviation from the common block because a 1.5% stack with a 0.5% floor leaves fee/R near 0.2 R). Phase, cycle and level for 4h are read from the daily bars at the prior daily close. **Design items not implemented (frozen design, stated before the run):** 15m and 1h rows (NK says same timeframe; a 1h/15m EMA200 stack is a different rule with no source; the task text asked for them "wherever the rule can be expressed", the frozen design says NOT run); native weekly and monthly rows (too few events on 20 coins from 2020-08). Data limit: daily EMA200 needs about 200 days, so first signals appear about 2021-03; effective DEV is about 2021-03 to 2023-12.

## Cells (13 tried, 3 primary)
Splits by SIGNAL bar open: DEV < 2024-01-01 UTC, VALIDATION >= 2024-01-01.
| ID | Coin phase | BTC cycle | Level | Variant | TF | Side | Width | Status |
|---|---|---|---|---|---|---|---|---|
| P1 | RANGE | ACCUM-RANGE | at | V0 | 1d | long | 3% | PRIMARY |
| P2 | RANGE | ACCUM-RANGE | at | V1 | 1d | long | 3% | PRIMARY |
| P3 | RANGE | ACCUM-RANGE | at | V2 | 1d | long | 3% | PRIMARY |
| C1 | RANGE | ACCUM-RANGE | away | V0 | 1d | long | 3% | CONTROL (level comparison) |
| C2 | RANGE | MARKUP | at | V0 | 1d | long | 3% | CONTROL (a pause, not a turn) |
| C3 | DOWN | MARKDOWN | at | V0 | 1d | long | 3% | CONTROL (falling knife) |
| C4 | UP | any (also shown by label) | at | V0 | 1d | long | 3% | CONTROL (continuation) |
| C5 | RANGE | CAPITULATION or RELIEF | at | V0 | 1d | long | 3% | CONTROL (episodes only) |
| C6 | RANGE | ACCUM-RANGE | at | V0 | 4h | long | 1.5% | CONTROL (timeframe) |
| C7 | DOWN | MARKDOWN | mirrored at | V0 | 1d | short | 3% | CONTROL (NK forbids shorts) |
| C8 | RANGE | ACCUM-RANGE and BTC close > SMA20 and SMA50 | at | V0 | 1d | long | 3% | CONTROL (NK index filter, BTC excluded) |
| C9 | RANGE | ACCUM-RANGE | at | V0, limit at SMA20 filled within 5 bars | 1d | long | 3% | CONTROL (entry variant) |
| C10 | RANGE | ACCUM-RANGE | at | V0 | 1d | long | 5% | CONTROL (power check, one pre-declared value) |
**Total cells tried: 13. Primary cells: 3.** The by-label breakdown of C4 is a descriptive split of one cell, not extra cells. Each row also gets a placebo and a 6 bp maker line (references, not cells).

## Universe
Fixed here: 20 Binance spot USDT coins, BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO (all have history on both sides of 2024-01-01). Gated. Fresh holdout (descriptive column, VAL period only, never pooled): AAVE ENJ GRT HBAR MANA SAND THETA XTZ from `binance_fresh/nk5_nyasia` (5m, resampled): 8 coins, not 10; the shortfall is reported, nothing was fetched. No data exists after 2026-11-13, so the "days since 2026-11-13" forward column is empty.

## Data and fee convention
Read-only `F:/MTS/data_cache`: `binance_spot/<SYM>USDT_15m.npz` (key t or ts, asserted exactly one; strictly increasing; step a multiple of 15 min). The raw files have known intraday exchange gaps (about 10 to 22 events per coin, up to 41 bars): counted and printed in the RESULT provenance block, not filled. Daily and 4h bars are bucketed from this ONE source per coin (UTC aligned); incomplete first/last buckets are dropped; the daily series is asserted contiguous; a 4h bucket with no base bar simply does not exist (EMA recursion continues across it). BTC cycle from `mts_brains/phase_daily.csv` (shared file written by sibling workers: path, row count, last date in RESULT). Nothing is written into the existing cache folders and nothing was fetched.
Fee: fee-net R = gross R - fee R, fee R = (bp/2e4) x (|e| + exit notional) / R_dist with exit notional = |x| for a single exit, 0.5|x1| + 0.5|x2| for the blended exit: the nkp2 convention (12 bp round trip taker = 6 bp of entry notional plus 6 bp of exit notional, charged on both legs). 6 bp maker row: same formula with 3 bp per leg, with the entry still filled as in the taker row (a sensitivity line, optimistic, not PASS-bearing). Fills: market entry at the next bar open; a gap through a stop or target fills at the bar open; stop first if stop and target are inside one bar; on a limit-fill bar the target is not allowed.

## Parameters (SOURCED / OURS)
| Parameter | Value | Label |
|---|---|---|
| Stack lengths | 20, 50, 100, 200 | OURS (range SOURCED 5GZIshXnxW8) |
| Stack width | 3% daily, 1.5% 4h, 5% (C10) | OURS (idea SOURCED 5GZIshXnxW8 00:06:03) |
| Fall shape / depth | 10 bars; 50 bars and 1.5 ATR14 | OURS (idea SOURCED 5GZIshXnxW8 00:13:58) |
| Trigger | two consecutive closes above stack max | two-close SOURCED a8RP5ftOfGo 00:08:50, IjU9PpqvrI8 00:14:58; count for convergence OURS-informed |
| Stop | under lowest EMA | SOURCED (5GZIshXnxW8) |
| R floors | 0.5% (daily), 1.2% (4h), 0.6 x ATR14 | OURS (common block) |
| Exit | half at 2R; trail under lowest EMA; two closes inside | 2R OURS; trail and two-close SOURCED (5GZIshXnxW8, two-close idea a8RP5ftOfGo) |
| Coin phase | ADX14 >= 20, DI direction, SMA20 slope sign with 5-day lag, else RANGE | OURS |
| BTC cycle | phase_daily.csv labels | OURS (MTS_BRAINS_SPEC) |
| Level | lowest low of 12 closed weeks; at-level = within 1.0 ATR_D | OURS |
| V1 | WT1 < 53 and WT1 > WT2 | 53 SOURCED in the WT module (Crosses:9-12); WT1 > WT2 OURS |
| V2 | mean of last 3 funding prints <= 0.0003 | OURS |
| C8 | BTC close > SMA20 and SMA50 | SOURCED 3KnEiKNh1pc 00:15:29, 4SPDtbJVDr4 00:06:54 (Nifty proxy) |
| C9 | limit at SMA20, 5 bars | place SOURCED, window OURS |
| Fees | 12 bp taker, 6 bp maker | OURS (common block) |

## Gates on VALIDATION primary cells (all needed for PASS)
Mean net R > 0 at 12 bp; trade-level bootstrap CI low > 0 (2000 draws, 95%); 72h cross-coin-cluster bootstrap CI low > 0 (clusters = signal date // 3 days, 5000 draws, the design's cluster) AND day-cluster CI low > 0 (the task text's cluster); ex-best-5 mean > 0; placebo beaten (p < 0.05 and real mean > placebo mean); Benjamini-Hochberg q <= 0.10 across the 3 primary cells (p = one-sided 72h-cluster bootstrap p for mean <= 0); n VAL >= 200 coin-episodes to PASS. n VAL < 100: UNDERPOWERED (not FAIL, not PASS). n 100 to 199: reported with CIs, cannot PASS (labelled UNDERPOWERED, n 100-199) unless a gate already fails (then FAIL). Overall verdict: PASS if any primary cell PASSES; UNDERPOWERED if all three are UNDERPOWERED; else FAIL. Controls are descriptive.
Placebo like-for-like: for each real VAL trade, random VAL signal bars in the SAME coin with the same coin phase, same BTC cycle set, same side, same timeframe, same at-level/away class, same variant flags (V1/V2/C8 where the cell has them), in the trigger state (two consecutive closes above the stack, any width, any fall), simulated with the same stop/exit/fee; matched count per coin, 1000 draws; coins with an empty pool are excluded from the comparison (coverage reported); p = (1 + #placebo >= real)/1001. "Beats placebo" is reported separately from "profitable".

## Kill rules
n VAL < 100 for a primary cell: UNDERPOWERED, no loosening, no parameter change. Fewer than 50 total P1 episodes (DEV + VAL): the rule is reported as not testable on this universe. No parameter or cell changes after seeing results; a BUG fix is committed separately and listed under Deviations in RESULT.

## Protocol and tests
Order: PRE_REG + study.py + test_study.py committed; `study.py counts` (counts only, no outcome) committed; `study.py run` once (it refuses uncommitted code); RESULT from the committed code. test_study.py (synthetic data, no cache): look-ahead truncation and poke tests (phase, cycle, level, WT, funding, c8 and split attributes unchanged when data after t is cut, on 4h and daily rows), exact prior-close phase read, fee on both legs hand numbers, gap-fill and stop-first cases, limit fill bar, trail, split by signal bar, control-phase trade never in a primary cell, hand-built signal and each blocking condition, weekly level, BH, placebo. The look-ahead tests must fail under `STUDY_BUG=1` (phase and cycle read at the same day).

## Weaknesses stated up front
Power: a 3% stack x RANGE x ACCUM-RANGE x at-level on 20 coins from 2021-03 may give under 100 VAL episodes; UNDERPOWERED is the likely daily verdict (expectation only, not evidence). 0 of 17 earlier phase-chosen cells and 0 of about 100 NK rows passed, gross R about zero. BTC-only cycle label may not describe a coin's own base. Coin phase thresholds are OURS. Spot vs perp prices. V2 is NO-DATA for ALGO, FIL, NEAR and the fresh coins. At-level with 1.0 ATR_D may be true for most signals on volatile alts (share reported as counts, not tuned). Four BTC cycles only: a VAL pass would mean surviving one regime, not a cycle law.
