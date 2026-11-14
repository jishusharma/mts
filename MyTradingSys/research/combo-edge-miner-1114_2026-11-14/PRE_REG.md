# PRE_REG: combinatorial edge miner (combo-edge-miner-1114), written and committed WITH the code before any combo outcome is computed

Order 2026-11-13 ~21:20Z: "Spawn agents that can think! Think of finding permutations and combinations that works!" Today's single-rule studies (about 20, edge4..edge9, nk1..nk6) all failed fee-net: gross R about 0, fees 0.1-0.8 R per trade from tight stops. This study changes the mechanism in three ways: (1) stops are 2-15% so fees are 0.01-0.06 R, (2) exits are a 3R target, an ATR trail and a ride-until-structure-break instead of fixed short holds, (3) every combination of 26 causal layers is tried across 6 phases, with the number of tries counted and deflated. Labels: SOURCED = a named layer, formula in FORMULAS.md or a thinker note; OURS = our fixed choice. Every threshold below is OURS unless marked SOURCED. Nothing is tuned after DEV starts.

## Data (public data.binance.vision only, no keys, no orders)
- Universe, 20 USDT coins: BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK DOT AVAX ATOM ETC XLM BCH UNI VET ZEC NEO. Chosen as "BTC, ETH + 18 liquid" among coins that have BOTH spot taker data and Binance futures funding + daily open interest in the cache (nkp1); NEAR, FIL, ALGO were dropped for that reason. Fixed list, not point-in-time by volume: survivorship is a stated limit (delisted coins are absent).
- Spot klines 4h and 1d with taker-buy base volume (col 9), 2017-08 onward, to the last bar CLOSED by 2026-11-13 20:00Z. Trades are simulated on SPOT prices as the perp proxy; funding from the perp is charged on top. Futures funding (8h prints) and daily open interest (last 5m row of each UTC day, base units) copied from the nkp1 cache. Cache: `F:\MTS\data_cache\binance\combo-edge-miner-1114\` (fetch.py). Nothing above 5 MB in the git tree. 1h is not used (no idea needs it).
- Entries are allowed from 2020-01-01 and only after the coin's first funding print (earlier bars feed indicator warm-up only). OI starts 2020-09, so OI features are False before then (never 0).
- DEV = entry day <= 2023-12-31. VAL = entry day >= 2024-01-01. VAL is not looked at until the top 10 are frozen (see Selection). A DEV trade may exit after 2023-12-31 (at most 60 days of 2024 prices enter a late-December DEV trade); stated, not removed.
- Peeks before this file was written (descriptive, no combo run): all-days LONG entries on BTC, ETH, ADA, DEV, daily bars, 12 bp: mean net R +0.31 (3R target), +0.59 (ATR trail), +0.76 (ride) with stop about 16% of price. That is the drift of a 2020-21 bull market; it is the beta every long cell is up against, and the reason the VAL gate includes a same-phase random-entry placebo.

## Phase label (6 labels, causal)
Day D reads only closes of days <= D-1 (the label from the close of day d is keyed to day d+1). Structure from BTC daily close vs its SMA200d and the 20-day slope of that SMA: UP = close > SMA200 and slope > 0; DOWN = close < SMA200 and slope < 0; MIX = everything else (SMA200 above and falling, or below and rising). Cycle clock (FORMULAS 25, halvings 2016-07-09, 2020-05-11, 2024-04-20): EARLY = fewer than 540 days since the last halving, LATE = 540 or more. Labels: UP_E, UP_L, MIX_E, MIX_L, DOWN_E, DOWN_L. One BTC-based label for every coin and every bar of that day (market phase). The label is assigned to the ENTRY bar's day. `Regime mix:` is reported as bull = UP, range = MIX, bear = DOWN, per window.

## Feature bank (26 booleans, every window in DAYS converted to bars: nb = 6 for 4h, 1 for 1d; all computed from bars <= signal bar)
ATR14 = plain SMA of true range on the tf bars (FORMULAS 12). RSI14 = Wilder (FORMULAS 1). ADX/DI 14 = FORMULAS 30. BB(20,2) population sd (FORMULAS 22). Directional features have a long reading L and a short reading S; neutral features are one reading for both.

| # | Feature | Type | Long reading | Short reading |
|---|---|---|---|---|
| 1 | BRK20 | dir | close > prior 20d high | close < prior 20d low |
| 2 | BRK5 | dir | close > prior 5d high | close < prior 5d low |
| 3 | RSI_X | dir | RSI14 <= 30 | RSI14 >= 70 |
| 4 | RSI_MOM | dir | RSI14 >= 60 | RSI14 <= 40 |
| 5 | BB_EXT | dir | close < lower band | close > upper band |
| 6 | SWEEP | dir | low < prior 10d low and close > that low | high > prior 10d high and close < that high |
| 7 | ADX_DI | dir | ADX >= 20 and DI+ > DI- | ADX >= 20 and DI- > DI+ |
| 8 | TREND_MA | dir | close > SMA50d and SMA50d above its value 10d ago | mirror |
| 9 | ABOVE_200 | dir | close > SMA200d (coin's own) | close < SMA200d |
| 10 | FLUSH_EXT | dir | close is the lowest close of 10d | highest close of 10d |
| 11 | BIGBAR | dir | range >= 2 x previous ATR14, close in bottom 25% of the bar | top 25% |
| 12 | NB_ABS | dir | spot de-biased net taker ratio over 3 bars >= +0.08 | <= -0.08 |
| 13 | NB_PER | dir | same ratio over 10 days >= +0.03 | <= -0.03 |
| 14 | BB_SQZ | neutral | BB width within the lowest 25% of the prior 365d | |
| 15 | VOLX | neutral | volume >= 2 x median volume of the prior 30d | |
| 16 | DD_DEEP | neutral | close <= 0.60 x highest close of 365d (daily grid) | |
| 17 | NEAR_200W | neutral | BTC close <= 1.10 x its 200-week SMA (cycle file d200w, lagged 1 day) | |
| 18 | OI_FLUSH | neutral | daily OI change over 2d <= -5% | |
| 19 | OI_BUILD | neutral | daily OI change over 3d >= +5% | |
| 20 | OI_HI | neutral | OI >= 0.95 x max OI of 60d | |
| 21-24 | PUOU / PUOD / PDOU / PDOD | neutral | price move over 3d in daily-ATR units (up >= +1, down <= -1) x OI move over 3d (up >= +3%, down <= -3%): up-up, up-down (rally on falling OI), down-up (drop on rising OI = trapped longs), down-down (flush) | |
| 25 | FUND_LO | neutral | 3-day mean funding at or below its 10th percentile of the prior 90 days | |
| 26 | FUND_HI | neutral | at or above the 90th percentile | |

Spot taker de-bias: nt = (2 tbv - v)/v; bias = mean(nt over the prior 30d); de-biased delta = (2 tbv - v) - bias x v; ratio = sum(de-biased delta)/sum(v) over the window. Thresholds 0.08 and 0.03 are the thinker notes' NB(t,3) >= 0.25 and NB10 >= 1.0 rescaled to a ratio of window volume (OURS). Daily-grid flow features (18-26 except NEAR_200W's source) use day-D OI / funding / close; a 4h bar on day D reads the PREVIOUS completed day, a 1d bar reads its own day (its close is the bar close). NEAR_200W reads the row one day earlier on both. Missing OI / funding / history makes a feature False.

## Combinations searched (exhaustive, no sampling)
Every 2-way (325) and 3-way (2,600) AND of the 26 features = 2,925 combos; x direction (long, short) x 6 phase labels (the trade's entry day) x 3 exits x 2 timeframes (4h, 1d) = **210,600 cells enumerated**; a combo may include one directional and one neutral features in any mix. The signal fires on the ONSET bar (combo true now, false on the previous bar of that coin); no overlapping trades per coin (next signal only at or after the exit bar). A cell enters the ranking only with n >= 100 non-overlapping DEV trades (n counted after the overlap rule). Named thinker combos add 14 combos x 3 exits x 2 timeframes = 84 trials (below). **Total trials = 210,684**, counted whether or not they pass the n floor; BH uses m = 210,684.

## Trade management (frozen)
Entry at the next bar's open. Stop distance S = max(2.5 x ATR14, 2.0% of entry) from entry (>= 0.6 x ATR and >= 0.5%, the thinker floor; fee share at 12 bp is 0.012-0.06 R). Exits: **T3R** stop S, target +3R, time exit at the close of day 30; **TRAIL** stop S, after +1R the stop follows the highest (lowest, for shorts) close minus (plus) 3 x ATR14, time exit day 60; **RIDE** stop S, exit at the next open after a close beyond the opposite prior-10-day extreme ("opposite structural signal"), time exit day 60. Stops fill at the worse of stop and open; same-bar stop and target = stop; targets fill at the target. A trade not resolved by the last closed bar is dropped (the last 30-60 days are not scored). Net R = (gross return - cost - side x funding paid) / (S / entry), FORMULAS 13: cost 12 bp = 2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 (from `MyTradingSys/backtest/fees.py`; 6 bp = half of it, informational maker-like case); funding = actual 8h prints between entry and exit, longs pay positive, shorts receive.

## Selection on DEV (no VAL look)
For every qualifying cell: mean net R at 12 bp, day-cluster robust standard error (clusters = entry UTC day pooled over coins, CR1 correction), one-sided normal p, 95% CI. Deflation: (a) Benjamini-Hochberg over m = 210,684 (cells below n = 100 count as untested but stay in m); (b) max-of-N placebo: 40 rounds in which every qualifying cell is replaced by the same number of RANDOM same-phase same-exit DEV entries and the maximum day-cluster t over all cells is recorded; a cell's deflated p = share of rounds whose max t is at least its t. Ranking for the top 10: day-cluster CI LOWER bound of mean net R at 12 bp; at most one cell per (timeframe, direction, feature set). The top 10 is frozen from DEV and written to results before VAL is evaluated by the same script run. A cell that survives neither BH nor the max-of-N placebo is still confirmed on VAL (the order says keep the top 10) but the RESULT shows its DEV deflation columns.

## Confirmation on VAL (top 10, untouched)
Same rule, same exit, same phase, entries >= 2024-01-01, 12 bp and 6 bp. **PASS needs ALL**: n >= 30 (else UNDERPOWERED); mean net R > 0 at 12 bp; day-cluster bootstrap 95% CI lower bound > 0 (2,000 resamples of entry days); mean net R > 0 after removing the 5 best UTC days; beats same-phase random entries (1,000 draws of the same n from all VAL eligible entries in that phase, same exit; p < 0.05); BH q < 0.05 over the 10 one-sided bootstrap p-values. The 6 bp row is informational unless 12 bp passes. VAL contains one regime sequence (2024-26 bull then the 2026 bear), so a pass is a testnet-forward candidate, never an "edge".

## Named thinker combos (a): pre-registered, not selected
14 bank-feature versions of the thinker ideas (the ideas' multi-step arm/trigger logic is approximated by same-bar AND of bank features; this is a mechanical analog, stated in RESULT): T1 flush-reset long (OI_FLUSH, NB_ABS, SWEEP; non-bear phases), T2 trapped-longs short (PDOU, OI_HI, FUND_HI; DOWN), T2b the same plus NB_PER short, T3 trapped-shorts squeeze long (FUND_LO, NB_ABS, BRK5; non-bear), T4 squeeze-exhaustion short (PUOD, ABOVE_200, BIGBAR; DOWN), T5 spot-led ignition long (NB_PER, BRK20, NEAR_200W; non-bear), T7 bear rip-sell short (BB_EXT, ADX_DI, ABOVE_200; DOWN), T8 broken-low continuation short (BRK20, ADX_DI, FUND_HI; DOWN), T9 200w failed breakdown long (NEAR_200W, SWEEP, RSI_X; MIX and DOWN), T10 washout band-reclaim trend long (TREND_MA, RSI_MOM, ADX_DI; UP_E, UP_L, MIX_E), T11 sweep-reclaim discount long (SWEEP, DD_DEEP; all phases) and T11b with OI_FLUSH, T12 flag long (BB_SQZ, ADX_DI, BRK5; UP) and short (DOWN). Non-bear = UP_E, UP_L, MIX_E, MIX_L; DOWN = DOWN_E, DOWN_L. Each x 3 exits x 2 timeframes, evaluated on DEV and VAL with the same VAL gates (BH over the named family). T6 cohort divergence is NOT_IN_DATA (top-trader position ratio not in the cache). Not tested: any thinker feature that needs data outside the bank (cost-basis VWAP of OI additions, weekly Cowen band, monthly low) beyond the analogs above.

## Tests (test_miner.py)
Worked examples from FORMULAS.md (ATR s12, RSI s1, ADX s30.2, net R s13), simulator hand cases (stop, gap, target, time, ride, trail), greedy overlap, day-cluster SE, BH, a planted-edge world (the miner finds it, the null world does not), and a causality test: features and phase labels at bars before a cut must not change when later data is removed (4h and 1d, three cuts). `test_bug_flag_is_detected` runs the causality test with STUDY_BUG=1 (same-day phase label and same-day daily flow = look-ahead) in a subprocess and requires it to FAIL.

## Context (d-context-retest-1104; prereg_context_lint)
Regime: BTC structure UP / MIX / DOWN (close vs SMA200d and its 20-day slope), reported as bull / range / bear mix for DEV and VAL.
Phase: BTC cycle clock (halving, early under 540 days / late) x structure = 6 labels; every cell is conditioned on exactly one label, entry day label from prior closes only.
Session: none, because the timeframe is 4h and 1d with holds of days to weeks; intraday session timing is not the mechanism.
Entry: next bar open after the onset bar (taker, 12 bp round trip with funding charged), stop at 2.5 ATR or 2%, three exits.

## Power and limits (stated in advance)
About 4 DEV years (2020-2023) and 20 coins: cross-coin entries on one day are correlated, so the day-cluster CI is the minimum honest unit and independent episodes are far fewer than trades. Edge claims need an episode count the data cannot give for rare phase cells (DOWN_E is a short window), so small cells are UNDERPOWERED, never "no edge". Spot price stands in for the perp. Survivorship (fixed list). The ranking maximises over 210,600 cells; the deflation columns are the defence and the VAL confirmation is the test.
