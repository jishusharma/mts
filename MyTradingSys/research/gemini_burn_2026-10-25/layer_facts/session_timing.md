# Layer Fact Sheet: session_timing

Facts compiled strictly from repository files per MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:27-34 item C and task lf-session_timing-gemini-facts.
No verdicts on keeping, dropping, demoting, or parking any layer. Every fact line cites `file:line` or `NOT_IN_DATA`.
Layers covered: `session_momentum`, `turn_of_candle`, `session_levels` (`MyTradingSys/system/LAYERS.md:148-165`; `MyTradingSys/system/layer_index.json:416-439`).

---

## 1. session_momentum

### ORIGIN (Quoted Source)
- **Academic Source**: "Shen, Urquhart, Wang, *Financial Review* 57(2), 319-344, 2022, DOI 10.1111/fire.12290 (T1): the first half-hour return predicts the last half-hour return (liquidity-provision mechanism). The T055b report words it as 'first-half-session return biases rest-of-session'; both entries are supported via `entry_min`." (`MyTradingSys/backtest/layers/FORMULAS.md:374-376`).
- **Screen Specification Quote**: "Candidate C2 of the T055 proven-setups screen: intraday momentum, first-half-hour predicts last-half-hour" (`MyTradingSys/research/fast_track_2026-09-27/T055b_PROVEN_SETUPS.md:30`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:137`).
- **Module Implementation Docstring**: "Shen, Urquhart, Wang (2022) 'Intraday momentum in cryptocurrency markets', Financial Review 57(2), 319-344. DOI: 10.1111/fire.12290. Core finding: first-half-hour return of a trading session positively predicts the last-half-hour return of the same session" (`MyTradingSys/backtest/layers/session/session_momentum.py:1-4`).
- **Counter-Evidence Finding in Repo**: "BTC_SESSION_EXTERNAL:88-90 reports reversal at hour scale (counter-evidence)" (`MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:142`).
- **Trader Association / Ledger**: NOT_IN_DATA ("no non-core layer has a sourced exit... no trader source" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:40-42`; layer originates from academic literature and internal screening; no external trader and no dated call list exists).

### PARAMETERS (SOURCED or OURS)
- **Market**: Binance USDT-M BTCUSDT perpetual (`SOURCED`, quote: "Binance USDT-M perp" in `MyTradingSys/backtest/layers/FORMULAS.md:345`).
- **Execution / Taker Fee**: 10 bps round trip (0.0010) (`SOURCED`, quote: "taker fee 10 bps round trip (0.0010)" in `MyTradingSys/backtest/layers/FORMULAS.md:345`).
- **Slippage**: 2 bps round trip (0.0002) (`OURS`, quote: "realistic slippage added as `slip_rt` (default 0.0002 = 2 bps RT; source: internal fee floor in T055b 'SCALPING FEE FLOOR', internal arithmetic)" in `MyTradingSys/backtest/layers/FORMULAS.md:345-347`).
- **First Window Length**: 30 minutes (`OURS` / `CONCEPT-ONLY`, quote: "T055b:30 'intraday momentum, first-half-hour predicts last-half-hour'... Paper is in VOLUME time... code uses clock minutes" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:137`; `MyTradingSys/backtest/layers/session/session_momentum.py:12,40`).
- **Entry Time**: 30 minutes after session start (`OURS` / `CONCEPT-ONLY`, quote: "T055b:30 predicts the LAST half-hour... Default enters for the rest of the day, not the last half-hour" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:138`; `MyTradingSys/backtest/layers/FORMULAS.md:381`; `MyTradingSys/backtest/layers/session/session_momentum.py:12,80`).
- **Session Start Anchor**: 00:00 UTC (initial fixed UTC, later DST-aware via day_gates) (`OURS` / `NO-SOURCE`, quote: "FORMULAS.md:382 'UNDEFINED in source'... Fixed UTC, no DST (B102)" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:139`; `MyTradingSys/backtest/layers/session/session_momentum.py:11,29`).
- **Session Length**: 24 h (UTC day) (`OURS` / `NO-SOURCE`, quote: "24/7 adaptation is ours" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:140`; `MyTradingSys/backtest/layers/session/session_momentum.py:5-6,23,29`).
- **Minimum First-Window Move (`min_abs`)**: 0.0 (`OURS` / `NO-SOURCE`, quote: "Inert at default" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:141`; `MyTradingSys/backtest/layers/session/session_momentum.py:12,71-74`).
- **Directional Side Rule**: sign of first-window return (continuation) (`SOURCED`, quote: "T055b:30 'first-half-hour predicts last-half-hour'" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:142`; `MyTradingSys/backtest/layers/session/session_momentum.py:71-74`).
- **Timeframe / Base Bar**: 5m in backtest run, 1m supported in code (`OURS`, quote: "bar_min: 5" in `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md:7`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:144`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **Initial T055-C2 Run (2026-09-29)** [SUPERSEDED: funding history was 2025-09 onward only; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md:14`; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:3`]:
   - **Path**: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md:1-40`
   - **Fee-Net**: Fee-net evaluated (fee 10 bps RT + slip 2 bps RT + partial funding; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md:5,14`).
   - **IS / OOS Partition**: Single 70/30 split; 498,240 1m bars (IS 348,768 / OOS 149,472); 16 variants (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md:5`).
   - **Sample Size (n)**: IS n = 1,211 events, gross mean +0.0441%, net mean -0.0759%, net Sharpe -0.0270 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md:11`); OOS n = 519 events, gross mean -0.1792%, net mean -0.2988%, net Sharpe -0.1371 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md:12`). Verdict: FAIL (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md:3,21-27`).
2. **Corrected T055-C2 Rerun with Full Funding (2026-10-07)** [MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:68-114]:
   - **Path**: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:68-114`
   - **Fee-Net**: Fee-net evaluated (fee 10 bps RT + slip 2 bps RT + full funding from 2020-01; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:74,83`).
   - **IS / OOS Partition**: Single 70/30 split; 490,656 5m bars clipped to funding coverage (IS 343,459 / OOS 147,197) (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:74`).
   - **Sample Size (n)**: IS n = 731 events, gross mean +0.2193%, net mean +0.0999%, net Sharpe 0.0356 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:80`); OOS n = 299 events, gross mean +0.1358%, net mean +0.0177%, net Sharpe 0.0084 (< 0.3 FAIL mark) (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:81,93`). Only 1 of 2 OOS years positive (2025 net +0.0636%, 2026 net -0.0332%; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:85,96`). Verdict: FAIL (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:72`).
3. **Exit Policies Backtest C on Bigtrade Kline Fires (2026-10-09)** [MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:123-128]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:123-128`
   - **Fee-Net**: Fee-net evaluated under 6 exit policies (assumed round-trip cost 12 bps; `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:123-128,144`).
   - **IS / OOS Partition**: TRAIN 2022-01..2025-06 / VALIDATE 2025-07..2026-08 (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:123-128`).
   - **Sample Size (n)**: TRAIN n = 1,095 fires, mean net -10.7 to -15.2 bps; VALIDATE n = 181 fires, mean net -6.2 to -12.3 bps; 0 of 6 exit policies positive (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:123-128`).
4. **Kline Fires Parity Replay FIRES-B1 (2026-10-09)** [MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:37,70]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:37,70`
   - **Fee-Net**: Parity verification (firing timing and direction, not fee-net P&L; `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:12,16`).
   - **Sample Size (n)**: 1,740 total fires (2022-2026); live-up parity n = 3 (100% agreement, classified UNTESTED n=3; `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:37,70`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Ruling B102**: "Offline session models anchor NY/London at fixed UTC minutes (no DST); wrong by 1 h on ~40% of days" (`MyTradingSys/research/BUGS.md:212`). Closed 2026-10-04 by replacing fixed-UTC anchors with `day_gates` DST rules (`MyTradingSys/research/BUGS.md:212`).
- **Clock-vs-Volume Time Mismatch**: Original academic finding was established in volume time, while repo implementation operates in clock minutes (`MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:137`).
- **Prediction Horizon Drift**: Source paper specifies first-half-hour return predicting last-half-hour return; default backtest configuration enters at minute 30 and holds for the rest of the 24h session (`MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:138`; `MyTradingSys/backtest/layers/FORMULAS.md:381`).

### CONFLUENCE
- **Intended Role**: Standalone candidate C2 in T055 screen; independent setup, never a filter on Tom core (`MyTradingSys/backtest/layers/FORMULAS.md:370,383`; `MyTradingSys/research/fast_track_2026-09-27/T055b_PROVEN_SETUPS.md:30`).
- **Integration Classification**: Classed as TRIGGER candidate (Lead draft, OURS) (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:33`; `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:31`).
- **Actual Live Confluence**: Zero real trades combined ("Nothing combines on a live trade. `promoted_setups.json` ships empty... So no confluence rule has ever decided a real trade" in `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

---

## 2. turn_of_candle

### ORIGIN (Quoted Source)
- **Primary Academic Source**: "Shanaev, Vasenin, Stepanov, *Heliyon*, PMC10015199 (T1): returns concentrate at the opening of 15-minute candles (minutes 0, 15, 30, 45 of the hour). The paper has no cost model" (`MyTradingSys/backtest/layers/FORMULAS.md:387-388`; `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:9-10`).
- **Secondary Preprint Source**: "Kim and Hansen, 'The Quarter-Hour Effect', arXiv 2607.09426 (tier T2 preprint): the order imbalance in the opening window predicts returns over **4 to 12 hours**, on six perps with trade-level data" (`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:11-12`; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:6`).
- **Screen Specification Quote**: "Candidate C3 of the T055 proven-setups screen (research/fast_track_2026-09-27/T055b_PROVEN_SETUPS.md:38,51,80): 'cheapest to test, klines only'" (`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:8`).
- **Trader Association / Ledger**: NOT_IN_DATA ("no non-core layer has a sourced exit" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:40`; layer originates from academic literature and internal screening; no external trader and no dated call list exists).

### PARAMETERS (SOURCED or OURS)
- **Market**: Binance USDT-M BTCUSDT perpetual (`SOURCED`, quote: "Binance USDT-M perp" in `MyTradingSys/backtest/layers/FORMULAS.md:345`).
- **Execution / Taker Fee**: 10 bps round trip (0.0010) (`SOURCED`, quote: "taker fee 10 bps round trip (0.0010)" in `MyTradingSys/backtest/layers/FORMULAS.md:345`).
- **Slippage**: 2 bps round trip (0.0002) (`OURS`, quote: "realistic slippage added as `slip_rt` (default 0.0002 = 2 bps RT; source: internal fee floor in T055b 'SCALPING FEE FLOOR', internal arithmetic)" in `MyTradingSys/backtest/layers/FORMULAS.md:345-347`).
- **Candle Length**: 15 minutes (`SOURCED`, quote: "T055b:51 'Turn-of-candle effect (returns concentrated at 15-min candle opens)'" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:152`; `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:3`).
- **Turn Minute**: minute 0 of the quarter (`SOURCED`, quote: "T055b:51 (same)" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:153`; `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:36`).
- **Lead Minutes**: 1 minute (enter at minute 14 close) or 2 minutes in C3 driver (`OURS` / `CONCEPT-ONLY`, quote: "lead 1 min (enter at minute 14 close)" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:154`; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:9`).
- **Directional Side (Backtest)**: long fixed (`OURS` / `NO-SOURCE`, quote: "FORMULAS.md:393 'direction of the effect is NOT stated'" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:155`; `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:59`).
- **Directional Side (Live Testnet)**: sign of the quarter's minute-0 taker imbalance (`OURS` / `NO-SOURCE`, quote: "operator 2026-09-30 data-collection ruling, live_layers.py:171-175... Trades on testnet as 'sampling'" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:156`; `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:22-25`).
- **Holding Horizon**: 2 bars in C3 default (2 minutes); ~1 minute live; 4h/8h/12h in Kim & Hansen imbalance study (`OURS`, quote: "2-bar hold" in `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:9`; `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:22`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **T055-C3 Part 1 Driver Default Backtest (2026-09-29)** [MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:8-10]:
   - **Path**: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:8-10`
   - **Fee-Net**: Fee-net evaluated (fee 10 bps RT + slip 2 bps RT + funding; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:9`).
   - **IS / OOS Partition**: 70/30 chronological split; 2,491,200 1m BTCUSDT bars (IS 1,743,840 / OOS 747,360) (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:9`).
   - **Sample Size (n)**: IS n = 116,255 events, net -0.1183%; OOS n = 49,823 events, gross -0.0000%, net -0.1201%, net Sharpe -1.49; 0 of 2 OOS years positive (2025 net -0.1198%, 2026 net -0.1203%) (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:9`). Verdict: NO EDGE (FAIL) (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:3,9`).
2. **T055-C3 Part 2 Order-Imbalance Backtest (2026-09-29)** [MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:11-24]:
   - **Path**: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:11-24`
   - **Fee-Net**: Fee-net evaluated (fee 10 bps RT + slip 2 bps RT + funding; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:12`).
   - **IS / OOS Partition**: 70/30 chronological split; 48 variants across window {1,5} x min |imb| {0,0.1} x dir {mom,contra} x horizon {1,2,5 bars, 4h, 8h, 12h} (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:12`).
   - **Sample Size (n)**: OOS n = 40,857 events across short horizons 1, 2, 5 bars (net -0.1179% to -0.1195%, net Sharpe -0.91 to -1.93); 4h OOS n = 3,113 (gross +0.0143%, net -0.1058%, net Sharpe -0.12); 8h OOS n = 1,556 (gross -0.0154%, net -0.1353%, net Sharpe -0.11); 12h OOS n = 1,029 (gross -0.0109%, net -0.1310%, net Sharpe -0.09) (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:14-23`). 0 of 2 years positive across all horizons (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:16-23`). Verdict: NO EDGE (FAIL) (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:3,23`).
3. **Exit Policies Backtest C on Bigtrade Kline Fires (2026-10-09)** [MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:123-128]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:129-134,144`
   - **Fee-Net**: Fee-net evaluated under 6 exit policies against 12 bps assumed cost (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:129-134,144`).
   - **IS / OOS Partition**: TRAIN 2022-01..2025-06 / VALIDATE 2025-07..2026-08 (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:129-134`).
   - **Sample Size (n)**: TRAIN n = 105,199 fires, mean net -11.1 to -11.9 bps; VALIDATE n = 17,376 fires, mean net -10.8 to -11.9 bps; gross edge is +0.1 to +0.9 bps ("the signal pays its fees and nothing else; managed exits do not change it") (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:129-134,144`).
4. **Kline Fires Parity Replay FIRES-B1 (2026-10-09)** [MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:37,70]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:31,64`
   - **Fee-Net**: Parity verification (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:12,16`).
   - **Sample Size (n)**: 167,130 total fires (2022-2026); timing parity 99.7% (383 of 384 slots), side parity 70.8% (112 side mismatches on perp replay, 0 on spot replay) (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:12,31,64`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Live Deployment of Killed Layer**: Deployed live 3.5 hours after backtest killed it, under an operator "sampling" ruling (`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:22-25`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:156`).
- **Live Testnet Log Dominance**: Accounted for 79% to 81% of all testnet trades (300 of 372 trades, net -3.69 USD, 100% time exits), crowding statistical logs while executing on separate dedicated subaccount `jishu_1` (`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:28,33-35`; `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:144`).
- **Data Gap for Replication**: Original preprint finding required trade-level aggTrades for 4-12h order imbalance; repo possessed only 1m kline column 9 taker-buy volume proxy (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:26`; `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:37`).

### CONFLUENCE
- **Intended Role**: Standalone candidate C3 in T055 screen; explicit rule: "Never a Tom filter (layer stays separate)" (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:31`).
- **Integration Classification**: Classed as TRIGGER candidate (Lead draft, OURS) (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:33`; `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:31`).
- **Actual Live Confluence**: Zero real trades combined (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

---

## 3. session_levels

### ORIGIN (Quoted Source)
- **Problem Statement / Origin**: Task T087: "Session-levels observation layer: MTS did not see today's failed first break of the prior-day high (1h close sweep, target session low / daily open / Asian low); add session-levels layer + pre-reg backtest" (`MyTradingSys/research/BUGS.md:183`).
- **Operator Question / Observation**: "The 1m-only data answers Jis's question as a base rate: after a failed first break of the prior-day high, price retakes the local (spike) high before the Asia low in 57-67% of events and reaches the Asia low first in 24% (EU low first in 20%); the rest do neither before 14:00 UTC" (`MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:40`).
- **EUR-Low / US-Sweep Question**: Operator ask (2026-10-14, screenshot `e2379c5fdf2e`): "a local low is set - then a retest - does not take it out so that longs build then on US session start - low broken! happens quite often! ... A valid back test must be established first" (`MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:3-6`).
- **Trader Association / Ledger**: NOT_IN_DATA (originates from operator observational prompts on 2026-10-09 and 2026-10-14; no external trader and no dated trader ledger exists; `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:3,43`; `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:8`).

### PARAMETERS (SOURCED or OURS)
- **Market**: Binance USDT-M perpetual BTCUSDT 1m (`OURS`, quote: "BTCUSDT 1m 2022-01-01 .. 2026-10-07" in `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:1`).
- **Costs / Taker Fee**: 0.05% per side = 0.10% round trip (2 x taker 0.05%) (`OURS`, quote: "Net = minus 2 x taker 0.05%" in `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:3`; "Taker fee 0.05% per side on every fill. Funding is not modelled" in `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:9`).
- **Slippage**: 0 bps in T087 and EUR-low US-sweep; 1 bp in levels sizing (`OURS`, quote: "no slippage" in `MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md:3`; "5bp fee + 1bp slippage" in `MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md:7`).
- **Fail Window**: Close back through prior-day high/low within 60 minutes (`OURS` / `NO-SOURCE`, quote: "close back through the level within 60 min... All clocks/thresholds NO-SOURCE" in `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:3,43`).
- **Invalidation / Stop Loss**: Spike extreme (`OURS`, quote: "stop = spike extreme" in `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:3`).
- **Profit Targets**: Asia session extreme or EU session extreme on opposite side (`OURS`, quote: "target = Asia or EU session extreme on the other side" in `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:3`).
- **Time Exit**: 14:00 UTC US-open placeholder (`OURS` / `NO-SOURCE`, quote: "time exit 14:00 UTC (US-open placeholder)" in `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:3,43`).
- **US Open Anchor (EUR-Low Study)**: 13:30 UTC under US DST, 14:30 UTC standard (`OURS`, quote: "A = US cash open (13:30Z under US DST, otherwise 14:30Z)" in `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:12`).
- **Retest Threshold (EUR-Low Study)**: Within 0.20% of 24h lowest low L, >= 2h after L was set, bounce >= 0.6% (`OURS`, quote: "within 0.20% of L, at least 2 h after L was set and after a bounce of at least 0.6%" in `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:14-15`).
- **Position Sizing Ladder**: Flat vs 1-1-2-3 ladder (adds at +0.4%, +0.8%, +1.2%, stop at +1.6%) (`OURS`, quote: "Fixed-fixed-double-triple (1-1-2-3 units)... Adds at +0.4%, +0.8% and +1.2%; one stop at +1.6%" in `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:40-41`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **T087 Failed First Break Base Rates Backtest (2026-10-09)** [MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:1-43]:
   - **Path**: `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:1-43`
   - **Fee-Net**: Fee-net evaluated (2 x 0.05% taker = 0.10% RT; `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:3`).
   - **IS / OOS Partition**: Full sample 2022-01-01 to 2026-10-07 (913 total days; high side 466, low side 447), broken down by year (2022-2026) (`MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:1,5,26-37`).
   - **Sample Size (n)**: Pooled Asia target both sides n = 911 (touch all), target 24%, stop 63%, neither 13%, net mean -0.036%, t -1.72, win 31% (`MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:15`); Asia target touch Asia both sides n = 646, net -0.035%, t -1.43 (`MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:9`). EU target both sides n = 269, net -0.049%, t -1.39 (`MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:24`). Verdict: no edge / insufficient n (`MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:7-24`).
2. **EUR-LOW-US-SWEEP Base Rates and Leveraged Short Backtest (2026-10-14)** [MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:1-68]:
   - **Path**: `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:1-68`
   - **Fee-Net**: Fee-net evaluated (0.05% taker per side; funding unmodeled; `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:9`).
   - **IS / OOS Partition**: DEV 2022-2024, VAL 2025, HOLDOUT 2026 (`MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:8`).
   - **Sample Size (n)**: Retested weekdays n = 99 (low breaks 56.6% / 57%), single-low weekdays n = 1,027 (low breaks 25.5% / 26%) (`MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:20-21`). Trading short on retested days: mean net -0.02% per trade, t -0.24, win 42% (DEV +0.10%, VAL -0.37%, HOLDOUT +0.01%) (`MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:37-38`). 1-1-2-3 ladder: mean net -0.02%, t -0.32 (`MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:40-42`). Verdict: EXPLORATORY NEGATIVE (short leg) (`MyTradingSys/system/layer_map.json:1016`).
3. **Levels + Staged Sizing Quick Diagnostic (2026-10-14)** [MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md:1-48]:
   - **Path**: `MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md:1-48`
   - **Fee-Net**: Fee-net evaluated (5 bp fee + 1 bp slippage each fill + 1 bp funding stress charge per 8h; `MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md:7`).
   - **IS / OOS Partition**: DEV exploratory probe, 120 UTC days (2024-12-02..2025-03-31) (`MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md:5`).
   - **Sample Size (n)**: 117 paired signal days (50 long, 67 short; 8 variants across 936 campaigns) (`MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md:5,9-18`). All 8 variants lost after costs (mean net R -0.195 to -0.216, net USD -$1,139.58 to -$1,264.14) (`MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md:9-18`). Verdict: EXPLORATORY NEGATIVE (`MyTradingSys/system/layer_map.json:1009`).
4. **EUR-LOW-US-SWEEP Follow-ups Pre-Registered Study (2026-10-18)** [MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md:1-34]:
   - **Path**: `MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md:1-34`
   - **Fee-Net**: Pre-registered fee-net design (taker 0.05%/side; `MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md:3`).
   - **IS / OOS Partition**: DEV only (bars before 2024-07-01; VAL and HOLDOUT sealed; `MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md:1,16-20`).
   - **Sample Size (n)**: Tradeable days: Arm A n = 133, Arm B n = 208, Arm C n = 100 (`MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md:9-11,16-20`). All three arms BLOCKED by statistical power gate (MDE + cost > 0.30 R plausible cap; required 834 to 3,723 days; `MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md:3,16-20,34`). Verdict: BLOCKED by power gate; legs stay open (`MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md:3,34`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Geometric Retake Artifact**: "The 'retake' share is geometric: the stop sits a few ticks above the entry, the targets are far below it. It is a base rate, not an edge" (`MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:41`).
- **Distance Confound in Level Breaks**: Retest does not cause the extra break rate; proximity to the low explains the effect (0.2-0.5% away breaks 74% on retested vs 79% on single) (`MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:22-29`).
- **Volatility vs Direction Confound**: US window breaks levels more often due to heightened volatility (US open 57% break vs 30-34% at 6h/12h placebo shifts), not directional bias (`MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:30-33`).
- **P&L Weighting Bug in First Ladder Script**: First script averaged P&L per filled unit, giving 7-unit losers identical weight as 1-unit winners (showing false +0.30%, t 3.4); fixed before write-up (`MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:43-44`).
- **Ruling B187**: PIT price-level study blocked by power gate on available DEV data (MDE + cost 0.411 R vs 0.30 R cap; 662 days available vs 2,427 needed) (`MyTradingSys/research/BUGS.md:283`).

### CONFLUENCE
- **Intended Role**: Session levels observation layer intended to feed level context / trigger setups (`MyTradingSys/research/BUGS.md:183`; `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:14`).
- **Integration Classification**: Classed as DEAD (provisional) in layer review (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:32`).
- **Actual Live Confluence**: Zero real trades combined ("Nothing combines on a live trade. `promoted_setups.json` ships empty... So no confluence rule has ever decided a real trade" in `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).
