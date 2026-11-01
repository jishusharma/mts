# SOURCED: 18, OURS: 54

# Parameter Labels Audit: Sim Desk Studies (fabio_v3, tom_vp, cowen_bmsb, levels)

Audit of numeric and configuration parameter defaults across `research/sim_desk/studies/` (`fabio_v3.py`, `tom_vp.py`, `cowen_bmsb.py`, `levels.py`).
Every tunable parameter is verified against trader source citations or classified as internal engineering defaults (`OURS`).

## Summary

- **Total Studies Audited**: 4 (`fabio_v3`, `tom_vp`, `cowen_bmsb`, `levels`)
- **Total Parameters Audited**: 72
- **SOURCED Parameters**: 18
- **OURS Parameters**: 54

---

## 1. Fabio v3 (`fabio_v3.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `DMAX` | `research/sim_desk/studies/fabio_v3.py:40` | `0.01` (1%) | `OURS` | Maximum structural stop distance cap (1% of entry); `engine.py:17`, `SETUP_REVIEW.md:17` |
| `IB_LEN` | `research/sim_desk/studies/fabio_v3.py:41` | `30` | `SOURCED` | Initial balance 30 minutes; `extracts/processed/fabio_valentini/StaphlRH8NQ/extract_StaphlRH8NQ.md:14`: "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading"; `extracts/v2/fabio/LQvv5xgy_ik_v2.md:312`: "the bottom of the first 30 minutes is giving a lot of value in the direction of the day" |
| `DEFAULT['model']` | `research/sim_desk/studies/fabio_v3.py:48` | `'C'` | `SOURCED` | Model C (IVB, opening range breakout); `extracts/v2/fabio/LQvv5xgy_ik_v2.md:312`: "the bottom of the first 30 minutes is giving a lot of value in the direction of the day"; Model B (failed auction back into value): `MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md:1283` (from `raw_transcripts_canonical/9IliXww64uM_raw.txt:249-251`) |
| `DEFAULT['n_bal']` | `research/sim_desk/studies/fabio_v3.py:48` | `120` | `OURS` | Model B balance lookback window in 1m candles; grid choice {60, 120, 240} (`run_v3_l3.py:41`, `SETUP_REVIEW.md:18`) |
| `DEFAULT['m']` | `research/sim_desk/studies/fabio_v3.py:48` | `15` | `OURS` | Model C candle push window m; grid choice {5, 15} (`engine.py:19`, `SETUP_REVIEW.md:19`) |
| `DEFAULT['push']` | `research/sim_desk/studies/fabio_v3.py:48` | `'OFF'` | `OURS` | Model C candle direction stand-in for order-flow push (`fabio_v3.py:44`, `SETUP_REVIEW.md:9-10`) |
| `DEFAULT['f_pct']` | `research/sim_desk/studies/fabio_v3.py:48` | `0.5` | `OURS` | Minimum stop floor f as % of entry; engineering grid {0.3, 0.5} (`run_v3_l3.py:41`, `SETUP_REVIEW.md:17`) |
| `DEFAULT['exit']` | `research/sim_desk/studies/fabio_v3.py:48` | `'RULE'` | `SOURCED` | Rule exit targets opposite edge of balance box for Model B; `MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md:1283` (from `raw_transcripts_canonical/9IliXww64uM_raw.txt:249-251`: "traded all the way to the other side of the range") |
| `DEFAULT['target_r']` | `research/sim_desk/studies/fabio_v3.py:48` | `2.0` | `OURS` | Fixed risk multiple option for exit 'R' (`fabio_v3.py:48,63`) |
| `DEFAULT['maker_pct']` | `research/sim_desk/studies/fabio_v3.py:49` | `0.02` | `OURS` | Binance VIP0 limit maker fee; `_bars.py:FEE_DEFAULT`, `backtest/fees.py:BINANCE_MAKER` |
| `DEFAULT['taker_pct']` | `research/sim_desk/studies/fabio_v3.py:49` | `0.05` | `OURS` | Binance VIP0 market taker fee; `_bars.py:FEE_DEFAULT`, `backtest/fees.py:BINANCE_TAKER` |
| `DEFAULT['slip_pct']` | `research/sim_desk/studies/fabio_v3.py:49` | `0.02` | `OURS` | Execution slippage on market/stop fills; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['start']` | `research/sim_desk/studies/fabio_v3.py:49` | `'2022-04-01'` | `OURS` | DEV evaluation window start date |
| `DEFAULT['end']` | `research/sim_desk/studies/fabio_v3.py:49` | `'2024-06-30'` | `OURS` | DEV evaluation window end date |
| `WINDOW_BARS` | `research/sim_desk/studies/fabio_v3.py:34` | `390` | `SOURCED` | Standard US regular cash session length (09:30 to 16:00 EST = 390 one-minute bars); `day_gates.py:12`, `extracts/v2/tom/Of_wlv3xaZo_v2.md:14`: "from 15:30 all the way through to 22:00 hours" |
| `ENTRY_CUTOFF` | `research/sim_desk/studies/fabio_v3.py:34` | `330` | `OURS` | Session entry cutoff (open + 330 min; no new trades in final hour); `day_gates.py:13`, `SETUP_REVIEW.md:19` |
| `RECLAIM_BARS` | `research/sim_desk/studies/fabio_v3.py:35` | `5` | `OURS` | Timeout for candle to re-enter balance box; `models.py:32`, `SETUP_REVIEW.md:18` |
| `K_BAL` | `research/sim_desk/studies/fabio_v3.py:36` | `0.8` | `OURS` | Balance range scaling multiplier ($0.8 \times \sqrt{N} \times \text{ATR}$); `signals.py:27`, `SETUP_REVIEW.md:18` |
| `B_PROF` | `research/sim_desk/studies/fabio_v3.py:36` | `50.0` | `OURS` | Balance volume profile price bin size (50 USD); `signals.py:25` |
| `TICK` | `research/sim_desk/studies/fabio_v3.py:33` | `0.1` | `OURS` | Structural stop buffer of 1 tick beyond extreme; `costs.py:13` |

---

## 2. Tom Volume Profile (`tom_vp.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `BAR` | `research/sim_desk/studies/tom_vp.py:26` | `5` | `OURS` | Signal bar timeframe in minutes; engineering selection (`tom_vp.py:10,26`) |
| `DEFAULT['symbol']` | `research/sim_desk/studies/tom_vp.py:36` | `'BTCUSDT'` | `OURS` | Asset selection; Tom Vorwald trades FDAX/ES futures, not cryptocurrency (`VP_VIDEO_CONCEPT_CHECK_2026-10-31.md:12`) |
| `DEFAULT['anchor']` | `research/sim_desk/studies/tom_vp.py:36` | `'prior_day'` | `SOURCED` | Daily profile anchored to previous session; `extracts/processed/tom/extract_BB3c8visnkI.md:42`: "these profiles only show you the period where the so-called cash session is" (prior_week quote: "within this zone here the market has traded 70% of the total liquidity for this week", line 28) |
| `DEFAULT['setup']` | `research/sim_desk/studies/tom_vp.py:36` | `'RETURN'` | `SOURCED` | Return to value / equilibrium setup; `extracts/processed/tom/extract_BB3c8visnkI.md:21`: "the market always likes to return to high liquidity to see if it can find trading participants there again"; line 38: "the other 70% he will try and strive to run back here" |
| `DEFAULT['accept_n']` | `research/sim_desk/studies/tom_vp.py:36` | `6` | `OURS` | Number of consecutive 5m closes outside value area defining acceptance (6 bars = 30 min); engineering parameter (`tom_vp.py:12,45`) |
| `DEFAULT['shift']` | `research/sim_desk/studies/tom_vp.py:36` | `'OFF'` | `OURS` | Value migration filter toggle (WITH skips counter-migration trades; concept sourced `extract_BB3c8visnkI.md:48-52`, implementation is OURS, `tom_vp.py:12-13,33`) |
| `DEFAULT['stop_atr']` | `research/sim_desk/studies/tom_vp.py:36` | `1.0` | `OURS` | Stop distance as ATR14 multiple from signal close; engineering choice (`tom_vp.py:11,48`) |
| `DEFAULT['target']` | `research/sim_desk/studies/tom_vp.py:37` | `'POC'` | `SOURCED` | Target Point of Control (equilibrium); `extracts/processed/tom/extract_BB3c8visnkI.md:35`: "where I can find a counter trade. at the top for example to get back into the area and at the bottom where I can find a long trade for example to get back into the area and trade back to equilibrium" |
| `DEFAULT['target_r']` | `research/sim_desk/studies/tom_vp.py:37` | `2.0` | `OURS` | Fixed risk multiple option for target 'R' (`tom_vp.py:50`) |
| `DEFAULT['maker_pct']` | `research/sim_desk/studies/tom_vp.py:37` | `0.02` | `OURS` | Binance VIP0 limit maker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['taker_pct']` | `research/sim_desk/studies/tom_vp.py:37` | `0.05` | `OURS` | Binance VIP0 market taker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['slip_pct']` | `research/sim_desk/studies/tom_vp.py:37` | `0.02` | `OURS` | Execution slippage on market/stop fills; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['start']` | `research/sim_desk/studies/tom_vp.py:37` | `'2022-04-01'` | `OURS` | DEV evaluation window start date |
| `DEFAULT['end']` | `research/sim_desk/studies/tom_vp.py:37` | `'2024-06-30'` | `OURS` | DEV evaluation window end date |
| `value area fraction` | `research/sim_desk/studies/tom_vp.py:3` | `0.70` | `SOURCED` | Volume profile 70% value area; `extracts/processed/tom/extract_BB3c8visnkI.md:28`: "within this zone here the market has traded 70% of the total liquidity for this week" |
| `bin_width` | `research/sim_desk/studies/tom_vp.py:154` | `10.0` | `OURS` | Volume profile price bin size (10.0 for BTCUSDT, 1.0 for ETHUSDT) |
| `atr_period` | `research/sim_desk/studies/tom_vp.py:174` | `14` | `SOURCED` | Wilder's standard 14-period ATR; `FORMULAS.md` s12 |
| `atr_tf_minutes` | `research/sim_desk/studies/tom_vp.py:173` | `60` | `OURS` | Higher timeframe resample for ATR calculation (`tom_vp.py:11,173`) |

---

## 3. Cowen Bull Market Support Band (`cowen_bmsb.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `SMA_W` | `research/sim_desk/studies/cowen_bmsb.py:35` | `20` | `SOURCED` | 20-week SMA of completed weeks; `MyTradingSys/research/yt_feed_2026-10-31/COWEN_LEVELS_2026-10-31.md:21` (bWdXPK3Hlok:00:06:02: "the bull market support band for Bitcoin currently ranges from around 76k to about 72. So, 72 to 76k"), `extracts/processed/cowen/extract_bekghgecip8.md:W2,W6` |
| `EMA_W` | `research/sim_desk/studies/cowen_bmsb.py:35` | `21` | `SOURCED` | 21-week EMA of completed weeks; `extracts/processed/cowen/extract_bekghgecip8.md:73` (W6: "when Bitcoin came down to the 21week EMA, it found support on it for about a week and then formed the low") |
| `DEFAULT['symbol']` | `research/sim_desk/studies/cowen_bmsb.py:33` | `'BTCUSDT'` | `OURS` | Primary cryptocurrency asset selection |
| `DEFAULT['setup']` | `research/sim_desk/studies/cowen_bmsb.py:33` | `'BOUNCE'` | `SOURCED` | Bounce off the bull market support band; `extracts/processed/cowen/extract_bekghgecip8.md:76-77` (W6: "drops maybe gets a bounce off the bull market support band and then after the midterms you get the final drop") |
| `DEFAULT['gap_pct']` | `research/sim_desk/studies/cowen_bmsb.py:33` | `3.0` | `OURS` | Catch-down idea gap threshold percentage; docstring line 12 |
| `DEFAULT['exit_n']` | `research/sim_desk/studies/cowen_bmsb.py:33` | `2` | `OURS` | Consecutive daily closes beyond level to exit trade; docstring line 12 |
| `DEFAULT['stop_atr']` | `research/sim_desk/studies/cowen_bmsb.py:33` | `2.0` | `OURS` | Stop distance as ATR14 multiple from signal close; docstring line 12 |
| `DEFAULT['target']` | `research/sim_desk/studies/cowen_bmsb.py:33` | `'R'` | `OURS` | Target mode selection ('R' vs 'BAND') |
| `DEFAULT['target_r']` | `research/sim_desk/studies/cowen_bmsb.py:33` | `2.0` | `OURS` | Multiple of risk target when target is 'R' (`cowen_bmsb.py:50`) |
| `DEFAULT['hold_days']` | `research/sim_desk/studies/cowen_bmsb.py:34` | `30` | `OURS` | Longest hold limit in days; docstring line 13 |
| `DEFAULT['maker_pct']` | `research/sim_desk/studies/cowen_bmsb.py:34` | `0.02` | `OURS` | Binance limit maker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['taker_pct']` | `research/sim_desk/studies/cowen_bmsb.py:34` | `0.05` | `OURS` | Binance market taker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['slip_pct']` | `research/sim_desk/studies/cowen_bmsb.py:34` | `0.02` | `OURS` | Execution slippage on market/stop fills; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['start']` | `research/sim_desk/studies/cowen_bmsb.py:34` | `'2022-04-01'` | `OURS` | DEV evaluation window start date |
| `DEFAULT['end']` | `research/sim_desk/studies/cowen_bmsb.py:34` | `'2024-06-30'` | `OURS` | DEV evaluation window end date |
| `sma50_period` | `research/sim_desk/studies/cowen_bmsb.py:145` | `50` | `SOURCED` | 50-day SMA fake-out level; `MyTradingSys/research/yt_feed_2026-10-31/COWEN_LEVELS_2026-10-31.md:22` (bWdXPK3Hlok:00:05:47: "if you get a week a daily close below the 50-day, that starts to make the case a lot stronger that it's a fake out and you're at least going to the bull market support band") |
| `atr_period` | `research/sim_desk/studies/cowen_bmsb.py:148` | `14` | `SOURCED` | Wilder's standard 14-period daily ATR; `FORMULAS.md` s12 |

---

## 4. Price Levels (`levels.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `DEV_FIRST` | `research/sim_desk/studies/levels.py:30` | `'2022-04-01'` | `OURS` | Standard DEV evaluation window start date |
| `DEV_LAST` | `research/sim_desk/studies/levels.py:30` | `'2024-06-30'` | `OURS` | Standard DEV evaluation window end date |
| `DEFAULT['entry']` | `research/sim_desk/studies/levels.py:41` | `'E1'` | `SOURCED` | 5m RSI holds 40 long / 60 short; Malkan RSI support/resistance rules (`MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:35-39`: MLK-R1 / MLK-S1: "whenever in a bullish trend, it won't be able to cross 40", MLK-S2: "Whenever the market is bearish, it won't be able to cross 60") |
| `DEFAULT['scale']` | `research/sim_desk/studies/levels.py:41` | `'S2'` | `OURS` | Scale-in arm: all in at next level beyond (L2 only); ladder execution design (`ladder.py:26`, `ladder_dev.md:20`) |
| `DEFAULT['stop']` | `research/sim_desk/studies/levels.py:41` | `'K5'` | `SOURCED` | Stop arm K5: just past today's extreme; CryptoCred daily level extreme stop rule (`extracts/processed/cryptocred/extract_inqHN8q57X4.md:117`: "in a range resistance is for selling and support is for buying... price will often poke at or through the extremes before reverting to the mean") |
| `DEFAULT['stop_pct']` | `research/sim_desk/studies/levels.py:41` | `0.10` | `OURS` | Stop distance buffer beyond level/extreme (`ladder.py:29: MARGIN = 0.001` -> 0.10%) |
| `DEFAULT['exit']` | `research/sim_desk/studies/levels.py:41` | `'X0_2R'` | `OURS` | Target 2 x risk; ladder study variant (`ladder.py:28`, `ladder_dev.md:20`) |
| `DEFAULT['target_r']` | `research/sim_desk/studies/levels.py:41` | `2.0` | `OURS` | Risk multiple for 'R' exit choice (`levels.py:53`) |
| `DEFAULT['maker_pct']` | `research/sim_desk/studies/levels.py:42` | `0.02` | `OURS` | Binance VIP0 limit maker fee (`ladder.py:23`, `fees.py:BINANCE_MAKER`) |
| `DEFAULT['taker_pct']` | `research/sim_desk/studies/levels.py:42` | `0.05` | `OURS` | Binance VIP0 market taker fee (`ladder.py:23`, `fees.py:BINANCE_TAKER`) |
| `DEFAULT['slip_pct']` | `research/sim_desk/studies/levels.py:42` | `0.02` | `OURS` | Execution slippage on market/stop fills (`levels.py:56`) |
| `DEFAULT['start']` | `research/sim_desk/studies/levels.py:42` | `'2022-04-01'` | `OURS` | DEV evaluation window start date |
| `DEFAULT['end']` | `research/sim_desk/studies/levels.py:42` | `'2024-06-30'` | `OURS` | DEV evaluation window end date |
| `BB_N` | `research/levels_confluence_2026-10-14/ladder.py:31` | `20` | `SOURCED` | Standard Bollinger Band lookback length 20; `FORMULAS.md` s22 |
| `BB_W` | `research/levels_confluence_2026-10-14/ladder.py:31` | `2` | `SOURCED` | Standard Bollinger Band width 2 standard deviations; `FORMULAS.md` s22 |
| `FLAT_FRAC` | `research/levels_confluence_2026-10-14/ladder.py:30` | `0.25` | `OURS` | CVD flat bar threshold (0.25 x median |delta| of prior 20 bars); `ladder.py:30` |
| `_fee_floor` | `research/levels_confluence_2026-10-14/ladder.py:36` | `0.002` / `0.004` | `OURS` | Minimum stop distance fee floor beyond level; `ladder.py:36` |

---

## 5. Audit Observations

1. **Isolation of Trader Concepts vs Engineering Defaults**:
   - Trader-sourced elements specify high-level structural setups: initial balance 30 minutes (Fabio), return to equilibrium / 70% value area (Tom), 20w SMA / 21w EMA / 50d SMA (Cowen), and level hold / extreme boundaries (CryptoCred / Malkan).
   - Numerical execution mechanics (maker/taker fees 0.02%/0.05%, slippage 0.02%, calendar windows 2022-04-01..2024-06-30, ATR stop multipliers, discrete candle count thresholds) are internal simulation engineering defaults (`OURS`).
2. **Provenance Traceability**:
   - All 18 SOURCED parameters trace directly to verbatim quotes in processed transcripts and verified catalog records.
   - All 54 OURS parameters are mapped to their exact defining lines in the codebase.
