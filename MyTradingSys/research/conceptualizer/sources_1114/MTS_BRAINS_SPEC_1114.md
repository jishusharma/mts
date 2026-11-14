# MTS BRAINS SPEC for NK re-tests (1114)

**Verdict line: re-test every NK rule inside 6 causal phases x 8 single-bucket context layers; pick at most 3 cells per rule on DEV (<=2023-12-31), freeze them in git, then run VAL (>=2024-01-01) once, fee-net.**
Why: NK1-NK6 and edge9 showed gross R about 0 and costs 0.2-0.3 R/trade; matched direction did not beat mismatched (edge9). The one coarse ADX/MA20 phase (OURS) is too blunt. This spec adds the cycle clock (BIBLE s1, s5) and the daily structure, then lets context buckets pick only the trades where gross R is large enough to pay 12 bp.
Label rule: S = SOURCED (file named), O = OURS. No parameter below is the trader's. Nothing here is a forecast; all labels use data through the prior UTC close only.

## 0. Rules for the whole study
- Spec + cell-selection code + tests committed BEFORE any VAL row is computed (fixes the "code first committed with result" flag). `cells_frozen.json` carries the commit hash; VAL is run once.
- DEV/VAL split by SIGNAL bar time (not entry bar). Phase and context for a signal at time t use only bars closed before t; phase at day d uses closes through d-1.
- Mandatory test: `PHASE_LAG=0` (same-day close used) must FAIL the look-ahead test, like edge9. Add one test per context layer with a future-bar poke.
- Report header must carry `Regime mix:` (days per phase, DEV and VAL, plus signals per phase) and `## Context`.

## 1. PHASES (one label per UTC day d, from BTC; every coin trades under the BTC market phase)
Daily features through close of d-1 (BTC spot daily, history from `btc_cycles_2026-11/btc_daily.csv` for 2011-17 then Binance spot; S: BIBLE s1 data note):
- c close; SMA20/50/200 simple, days; S50 = SMA50/SMA50[10 days ago]-1; R10 = c/c[-10]-1; RB30 = c/min(close, last 30d)-1
- ATH = running max close; DD = c/ATH-1 (S: cycle-conditioned PRE_REG uses drawdown from ATH)
- W200 = SMA of last 1400 daily closes (the 200-week SMA; S: BIBLE s5 MA clock; needs 1400 days so first label 2015-08 on blockchain.info history)
- RSI14d = Wilder RSI(14) on daily closes (S: FORMULAS.md s1)
- RNG40 = (max high - min low over 40d)/c; NEWLOW15 = a close below the lowest close of the prior 60 days printed in the last 15 days
- Cycle state M: BEAR if DD <= -20% AND c < SMA200 (S: cycle-conditioned-buy-odds PRE_REG, bear = drawdown<=-20% and below 200d SMA); BULL if c > W200 AND DD > -20%; else BASE. Halving age (S: BIBLE s1 dates, 2020-05-11, 2024-04-20) is REPORTED per phase but not used in labels (4 cycles cannot power it).
First-match order (a day takes the first label whose test is true):
| # | Label | Test (all at close d-1) | Phase-appropriate direction | Status |
|---|---|---|---|---|
| 1 | CAPITULATION | M != BULL AND R10 <= -20% AND RSI14d <= 30; label sticks 3 days | LONG only (reclaim/fade) | O |
| 2 | MARKDOWN | c < SMA50 AND S50 <= -1% AND (M == BEAR OR c < SMA200) | SHORT (rally rejection, breakdown) | O |
| 3 | RELIEF | M != BULL AND c > SMA20 AND RB30 >= +12% AND c <= 1.05*SMA200 | LONG (pullback in bounce) | O |
| 4 | ACCUM-RANGE | M != BULL AND RNG40 <= 30% AND abs(c/SMA50-1) <= 7% AND NOT NEWLOW15 | BOTH: long at range low, short at range high (rule's own geometry) | O |
| 5 | MARKUP | c > SMA50 AND S50 >= +1% AND (c > SMA200 OR M == BULL) | LONG (pullback, breakout-retest) | O |
| 6 | DISTRIBUTION | everything else (stalled highs, bull-state chop, lower highs under SMA50 not yet MARKDOWN) | SHORT (failed break, resistance rejection) | O |
- Fixed rule: any label with < 5% of DEV days is reported but cannot supply a kept cell (UNDERPOWERED, never "fail").
- Sanity check, list not tuned: BTC must read CAPITULATION on 2020-03-12..15 and 2022-06-13..18, MARKDOWN across 2022-01..10 and 2025-11..2026-02, MARKUP on 2020-11..2021-03 and 2023-10..2024-03. If a listed window is mostly other labels, record it; do NOT retune.
- Why only BTC: coins share the market phase (edge9 pooled 20 coins the same way); coin-level phase would multiply cells. A coin-own MARKDOWN overlay is a separate, later pre-reg.

## 2. CONTEXT LAYERS (8, each bucketed into 3 with constants fixed now; one layer per cell, no pairs)
| ID | Layer | Causal formula at signal time t (last CLOSED bar) | Buckets | Source |
|---|---|---|---|---|
| C1 | 4h RSI state | Wilder RSI14 on 4h closes | LOW <= 40 / MID / HIGH >= 60 | S: layers/rsi/malkan_40_60.py (40/60), FORMULAS s1 |
| C2 | 1D WaveTrend | LazyBear WT1: esa=EMA(hlc3,10), d=EMA(abs(hlc3-esa),10), ci=(hlc3-esa)/(0.015*d), wt1=EMA(ci,21); daily | OS <= -53 / MID / OB >= +53 | S: layers/wavetrend (LazyBear defaults; verify param file) |
| C3 | 4h Bollinger %B | (c-lower)/(upper-lower), SMA20, 2 population sd | LOW < 0.10 / MID / HIGH > 0.90 | S: Bollinger period; thresholds O |
| C4 | OI change 24h | OI_usd(t)/OI_usd(t-24h)-1 (futures metrics `sumOpenInterestValue`) | UNWIND <= -3% / FLAT / BUILD >= +3% | O thresholds; data S: data.binance.vision futures/um metrics |
| C5 | Funding | mean of last 3 settled 8h funding rates (futures/um fundingRate monthly) | NEG < 0 / NORMAL 0..0.03%/8h / HOT > 0.03%/8h (baseline 0.01% is Binance default, S) | O thresholds |
| C6 | Taker delta vs price | TD24 = sum(2*takerBuyBase - volume)/sum(volume) over last 24 1h bars (spot kline col 9); P24 = c/c[-24h]-1 | BULL-DIV: P24<0 & TD24>0 / AGREE / BEAR-DIV: P24>0 & TD24<0 | O; caution: PRICE-CVD-DIV 1m/5m was NEGATIVE (layer_map), this is 24h, so a fresh test |
| C7 | Volatility regime | RV7/RV60 = stdev of 1h log returns last 7d / last 60d | COMPRESS < 0.70 / NORMAL / EXPAND > 1.30 | O |
| C8 | Session | UTC hour of signal: ASIA 00-07, EU 07-13, US 13-21; 21-24 pooled with ASIA | 3 buckets | O (NK1/NK5 windows) |
- Data limit: Binance futures `metrics` (OI) and some funding history may start after 2020-09 and per coin at listing. WORKER must probe the first available date per symbol with a HEAD request and write it to the RESULT. C4/C5 cells use only DEV days from first availability; if that leaves < 150 signals for a rule, C4/C5 are marked NO-DATA for that rule, not dropped silently. C1-C3, C6-C8 need only klines (spot since 2017).
- Cells = 6 phases x 8 layers x 3 buckets = 144 per rule. Pre-registered as the full family for BH.

## 3. META-LABEL METHOD
Step A, per-phase table FIRST (before any context): for each NK rule and each of the 6 phases show n signals, n days, gross R, cost R (fee/stop distance), fee-net R at 12 bp, in BOTH directions; mark the phase-appropriate direction (table s1). Verdict question answered here: does the phase-appropriate direction beat the opposite direction, day-clustered diff + se (edge9 format)? If no for every rule, report that before Step B; still run Step B (it is cheap) but label it exploratory.
Step B, DEV selection (<=2023-12-31 only):
1. Signals per rule from the rule's frozen NK definition (no re-tuning; maker 6 bp is a second row only).
2. For each cell: require n >= 150 signals AND >= 40 distinct UTC days. Score = lower 90% bound of the day-clustered mean fee-net R at 12 bp (bootstrap by day, 2000 draws, seed fixed).
3. Keep the top 3 cells per rule by score and ONLY if score > 0 and the cell is in the phase-appropriate direction (or ACCUM). At most one kept cell per context layer. Zero kept cells is a valid result (report "no DEV cell", stop for that rule).
4. Write `cells_frozen.json` (rule, phase, layer, bucket, direction) and commit before VAL.
Step C, VAL (>=2024-01-01) once, kept cells only, untouched:
- Costs: 12 bp round trip primary (taker both legs on the real notional) + funding where perp; 6 bp row (maker entry, with fill model, no free fills); stop >= max(0.6*ATR14 of the signal timeframe, 0.5% of price); gap-through stops/targets fill at the worse of level and next open.
- Stats per cell: n, days, win%, gross R, cost R, mean net R, day-cluster 95% CI, ex-best-5 days net R, win rate vs break-even.
- Placebo: 1000 random entries from the same cell (same phase day, same context bucket, same direction, same exit rule, same stop rule) matched on hour-of-day; report real minus placebo and p. Remember random entries lose about -0.18 R after fees, so also require net R > 0, not only p small.
- BH at q = 0.10 over all kept cells across rules (family = number of kept cells). PASS requires: net R > 0 at 12 bp, day-cluster CI low > 0, ex-best-5 > 0, placebo p < 0.05, BH q < 0.10, and n VAL >= 150 (else UNDERPOWERED).
- Control rows: same cell with opposite direction, and the same context bucket in the other 5 phases (does the phase add anything beyond the context?). Add the unconditional rule row for reference.
- Report: how many DEV cells passed VAL (expected by chance with 144 cells and top 3 picked: nearly all fail; a pass rate near 0 means no edge, near the kept count means real). Also report DEV net vs VAL net per kept cell (shrinkage).
- Today block: label for each of the last 10 days from the same code plus BTC close, SMA50/200, W200 (use the closed day; cycle-conditioned note: 2026-11-13 is provisional).

## 4. DATA (shared cache F:\MTS\data_cache\)
- Raw downloads only under `F:\MTS\data_cache\<venue>\<slug>\` (venue: binance, binance_spot, bybit; slug = the worker's study slug). Never write into a sibling's folder or the venue root.
- Every file gets a sidecar `<file>.meta.json`: source URL, fetch UTC, row count, first/last ts, sha256, key name (`ts` in ms, always; convert `t`).
- Read-only shared inputs: `F:\MTS\data_cache\btc_cycle_features_1114.csv`, `...\coinmetrics`. The daily phase table is built ONCE by the first worker into `F:\MTS\data_cache\mts_brains\phase_daily.csv` (with the git hash of the builder); the other workers read it and run `verify_phase.py` (recompute 30 random days) rather than rebuild.
- Worktree rule: only code, specs, summary CSVs and RESULT.md; every file < 5 MB (`git ls-files -s` size check in the test); no raw klines in git.
- Fix the `data_cacheinance` path typo class: build paths with `Path(...)/venue/slug`, never string concatenation.

## 5. Parameter ledger (all O unless marked): 20%/30%/12%/7% phase thresholds, 5% day floor, bucket cutoffs of C3-C8, 3-day CAP stickiness, 150/40 cell minimums. Not tuned on DEV or VAL; changing any of them after the first DEV score needs a new dated pre-reg.
## 6. Known weaknesses stated up front
- BTC-only phase on 20 coins: cells are day-clustered, so effective n is days, not signals (hence the 40-day floor and cluster CI).
- Four cycles: CAPITULATION and ACCUM-RANGE are thin; cycle conclusions are about about 4 episodes (cycle-conditioned note), so a pass is "survives one VAL regime (2024-26: bull then bear)", not a cycle law.
- 144 cells x rules: forking paths bounded by DEV-only selection plus BH on the kept cells; do not add layers after seeing DEV.
