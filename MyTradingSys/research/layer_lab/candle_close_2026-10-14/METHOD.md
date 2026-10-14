# BTC candle-close study: frozen exploratory design

Written 2026-10-14 before this study reads price data. All numeric choices below are OURS, not a trader's rules. Scope authorised by the operator's 2026-10-14 request for end-to-end candle-closing research and LAB probabilities. No live layer is introduced.

## Method note
Test whether completed candle sequences at previously known levels improve conditional forward-direction probabilities over nearby-price controls, across timeframes and causally observable phases. Use development data only, report episode dependence, uncertainty and all variants; a later frozen validation and realistic execution study are required for an edge claim. Macro bottoms require a separate long-horizon study with independent cycles, not millions of minute bars treated as independent cycles.

## Data, freeze and primary endpoint
- Binance USDT-M BTCUSDT perpetual, monthly 1m public archive, January 2022 through June 2024 inclusive. Check exchange SHA256 files. No files dated July 2024 or later may be fetched or loaded. This preserves the older candle pilot's validation reservation, despite other MTS studies already having used parts of it.
- UTC epoch-aligned complete candles: 1, 2, 3, 5, 15, 30, 60 minutes. The 2m candle is constructed, not a native Binance interval. Reject duplicates, missing minutes, invalid OHLC and incomplete aggregation buckets. No forward filling.
- Levels: previous completed 4h, day and UTC Monday-start week high/low. Available only at that parent period's end. No developing highs/lows, retrospective pivots, profile or round-number arms in this pilot.
- Regime: last completed daily close relative to the close 30 days earlier: above +10% bull, below -10% bear, otherwise neutral. Separately, daily efficiency = absolute 30-day price change / sum of absolute daily changes; >=0.3 trending, otherwise ranging. Four-hour direction is the sign of the last complete 4h close-to-close return. These are causal proxies, not labels for a known cycle top/bottom. Require full 31-day warmup.
- Signal uses only closed bars. Reference entry is next minute open at signal candle end; outcome is open 60 minutes later. Gross signed return and positive-return probability are primary. Subtracting 14bp round trip is a COST SCREEN ONLY, excludes funding, spread variability and impact, and is not executable strategy P&L. Also screen at 20bp. No stops, limits, leverage or intrabar-order assumptions.
- Eligible decision: signal close within 0.25% of a level. Test both long and short orientations. Controls are all eligible closes with the same timeframe, level family, side, UTC date, six-hour UTC slot and daily regime; average their 60-minute outcomes. This controls location/time/context approximately, not a causal experiment. It does not prove the levels themselves beat random lines. Controls include signals, making the ablation conservative and dependent.
- First event per UTC date / level family / side / signature / timeframe only. Outcomes may overlap across families; do not treat pooled rows as independent trades. Retain high/low identity in event rows.

## Six signatures (mirror every inequality for shorts)
Let L be a support/resistance level known at the current bar open; C0 current close, C1/C2 previous closes, H0/L0 current high/low. All required previous bars must be contiguous.
1. rejection: C1>L, L0<L, C0>L (wick through then close back).
2. break: C1<=L and C0>L (one close through).
3. acceptance: C2<=L, C1>L, C0>L (two closes through).
4. reclaim: C2>L, C1<L, C0>L (one closed-bar failed break then recovery).
5. retest: C2>L, C1>L, L0<=L, C0>L (holds from the far side for two closes, then touches). This is a local retest proxy, not proof of an earlier break or Krown's full discretionary setup.
6. strong_break: break plus (C0-low)/(high-low)>=0.75 and abs(close-open)/(high-low)>=0.6; zero range never qualifies.

## Inference and decision
- 7 timeframes x 3 level families x 6 signatures = 126 pooled arms; high/low and long/short pooled only after orientation. Report side, month, daily phase, trend/range, 4h direction and UTC slot as descriptive subdivisions, never uncounted selection opportunities.
- 1,000 circular moving-block bootstrap draws of seven UTC calendar days, seed 20261014. Same sampled days for all arms. Resample event totals/counts, retaining zero-event days. Report pointwise 95% intervals for probability, probability lift and mean signed return. Probability lift compares each signal with its matched eligible-control mean. Serial dependence longer than seven days is a limitation.
- No automatic winner/promotion. A candidate needs >=100 events, >=30 event days, positive probability lift and positive 14bp-screened return. Report conservative Bonferroni two-sided normal-bootstrap intervals across all 126 arms as a screening aid; this is not a replacement for OOS or a calibrated trading probability. All subgroup looks count as exploration.
- Expected power before run: 912 calendar days, at most two side-events per day per arm; actual event count unknown. Under iid p=0.5, 100 events give about +/-9.8 percentage points at 95%; detecting 5pp vs a known 50% baseline at 80% power takes approximately 784 independent events. Matching, clustering and multiplicity require more. Do not infer no edge from an underpowered cell.
- Preserve prior 130 candle trials and eight levels-sizing arms in research lineage, without claiming this is the entire MTS search history. No validation selected from an already inspected window may be described as pristine OOS.

## Readiness template assessment (12 items)
1. Home: OURS BTC perpetual event study on the seven listed TFs, all UTC sessions, 60min horizon (this file).
2. Source trade ledger: NOT_IN_DATA; anonymous YouTube trader not identified. No faithful trader replication claim; mechanical OURS event definitions above are the study ground truth.
3. Recall/fire rate: synthetic pattern fixtures before real data; report event frequency. Trader recall remains NOT_IN_DATA and blocks trader-replication P&L.
4. Inputs: OHLC sufficient for this conditional-price question; OI, order book, liquidation and historical funding NOT_IN_DATA and not replaced with zero.
5. Parity: independent high/low check and timestamp availability tests; no profile approximation.
6. Economics: 14/20bp sensitivity only, not historical net P&L; actual venue fees/funding/fills required for later strategy study.
7. Fills: no passive orders; next-open reference-price event study. Touch/trade-through P&L is not applicable until an execution rule exists.
8. Exits: fixed 60min measurement horizon, not any trader's management, and not asserted to bound discretionary results.
9. Null: same location band/date/slot/side/regime/timeframe controls above; random-line level test remains a separate dependency.
10. Power: approximation above, achieved counts and independent days reported.
11. Holdout: forbidden. Existing candle validation July 2024 onward stays unread. Log all 126 arms and subgroup views.
12. Stratification: listed above; no bull/bear cell extrapolated to a cycle-low probability.

This authorises only an exploratory event study. It does NOT pass all gates for a source-faithful P&L backtest, OOS promotion or trading.
