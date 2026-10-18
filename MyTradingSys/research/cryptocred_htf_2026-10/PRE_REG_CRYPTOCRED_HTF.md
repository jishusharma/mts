# Pre-registration: CryptoCred 4h/1d redesign (readiness checklist, PRE_REG_TEMPLATE.md)

Date: 2026-10-18. Card: `cryptocred-prereg-4h-1d`. Checklist: `research/tom_transfer_2026-10-11/BACKTEST_FAILURES_RESEARCH.md` section 6 (template: `backtest/PRE_REG_TEMPLATE.md`).
No P&L backtest run; no tuning; edits to live-path code out of scope.
Provenance rule: Every parameter / number is labelled SOURCED (quote + file:line) or OURS (engineering / design choice).
Numbers taken from `COUNT_POWER.md` (commit 380ae4e3eacc) are tagged UNCHECKED-BASE per card instructions.

## 0. Pre-build gate (items 0a-0f; decision q13, 2026-10-14: adopted, "be flexible")

- 0a Cost: Smallest stop or target this idea uses? On BTC fees stay under 0.25 R only with a stop of at least 0.40 % (taker legs) or 0.20 % (maker entry). The redesign replaces the unsourced 0.10 % stop (which produced fee share of R = 1.00 R = 100 % in `COUNT_POWER.md:15`) with an invalidation-based stop plus an OURS buffer in noise units (1.0x 14-period Wilder ATR from signal-bar structure, no forward bars). Under the primary ONE cost model (Deribit `fees.py:23`, taker 0.0005 per leg = 10 bps RT, maker 0.0), 4h median stop widths are: Setup 1 S/R flip = 1.461 % [OURS-UNREPRODUCED], cost_r (all_taker) = 0.068 R (fee share = 6.8 % of R < 0.25 R) [OURS-UNREPRODUCED], cost_r (maker_entry) = 0.034 R (fee share = 3.4 % of R) [OURS-UNREPRODUCED]; Setup 2 Fib pullback = 1.647 % [OURS-UNREPRODUCED], cost_r (all_taker) = 0.061 R (fee share = 6.1 % of R < 0.25 R) [OURS-UNREPRODUCED], cost_r (maker_entry) = 0.030 R [OURS-UNREPRODUCED]; Setup 3 Failed MSB reversal = 4.419 % [OURS-UNREPRODUCED], cost_r (all_taker) = 0.023 R (fee share = 2.3 % of R) [OURS-UNREPRODUCED]. Under the 14 bps RT sensitivity (0.0014, sourced in item 6 / gate 0b), 4h cost_r values are 0.096 R (setup 1), 0.085 R (setup 2), 0.032 R (setup 3) [OURS-UNREPRODUCED]. All stop widths exceed 0.40 % (taker) and 0.20 % (maker) by more than 3.6x to 11x [OURS, arithmetic: 1.461/0.40 and 4.419/0.40], and fee shares are strictly < 0.25 R. Gate 0a passes CONDITIONAL on the recompute (Provenance section): if the recomputed median stop width of 4h setup 1 or 2 is below 0.40 % or its all_taker cost_r is 0.25 R or more, gate 0a FAILS and the backtest card must not run.
- 0b Gross: Does a cheap fixed-horizon check on existing data show a raw move of at least 2x the round-trip cost? Yes. Round-trip fee on BTC is 10 bps (0.0010) [SOURCED fees.py:23] and the Binance sensitivity cost is 14 bps (0.0014) = 2 x (0.0005 fee + 0.0002 slippage) per round trip [SOURCED candle_patterns_2026-10-04/pilot/run_p1.py:27 and CANDLE_PATTERNS_RESEARCH_2026-10-04.md:19; components BINANCE_TAKER 0.0005 / BINANCE_MAKER 0.0002 at fees.py:27-28; the pure Binance taker fee RT is 10 bps]. 2x round-trip cost is 20 bps (0.0020) to 28 bps (0.0028). 4h BTC median true range is 1.278 % = 127.8 bps [OURS-UNREPRODUCED, DEV klines], and 1d median true range is 3.518 % = 351.8 bps [OURS-UNREPRODUCED, DEV klines]. Target moves at 1.5R to 2.0R span 2.19 % to 8.84 % [OURS-UNREPRODUCED], which are 15x to 44x round-trip fees [OURS, arithmetic: 2.19 %/0.14 % and 8.84 %/0.20 %]. Gate 0b passes CONDITIONAL on the recompute (Provenance section): if the recomputed 4h or 1d median true range is below 2x the round-trip cost (28 bps), gate 0b FAILS and the backtest card must not run.
- 0c Record: Does the source have dated calls or trades we can score on BTC data? No dated CryptoCred trade calls exist in repo data (0 dated calls in `extracts/processed/cryptocred/`, `HOME_FIT_AUDIT_CRYPTOCRED.md:19-21`, `COUNT_POWER.md:3`). Per gate 0c rule, with no dated record to score, the CryptoCred layer is classified strictly as a HYPOTHESIS, NEVER A CORE. Gate 0c is answered: layer is treated as hypothesis-only.
- 0d Data: Does BTC history hold every input the source reads? Yes. CryptoCred setups read OHLC price bars only to determine swing highs/lows, market structure breaks, and retests (`cc_setups.py:1-19`, `extract_BHwoN7VPrBE.md:12`, `HOME_FIT_AUDIT_CRYPTOCRED.md:33`). No aggressor volume, order book, or open interest is used. Binance BTCUSDT 1m klines across the DEV window (2022-01-01 to 2024-06-30, 1,313,280 bars, zero gaps [UNCHECKED-BASE COUNT_POWER.md:6]) provide complete OHLC inputs. The 30 monthly CSV files and their SHA-256 hashes are verified against `DATA_MANIFEST.csv`. Gate 0d passes.
- 0e Power: Trades in the dev window and the detectable edge; if larger than the claimed edge, write INCONCLUSIVE in advance or do not run (backtest/power_mde.py). Power computed via `power_mde.py` on DEV fills (2022-01-01 to 2024-06-30): 1d setups have fills N <= 31 (31, 30, 1) [UNCHECKED-BASE COUNT_POWER.md:21-23], all N < 100, and are declared INCONCLUSIVE IN ADVANCE (will not be run as a standalone edge test). 4h Setup 3 has N = 22 fills [UNCHECKED-BASE COUNT_POWER.md:20], N < 100, and is declared INCONCLUSIVE IN ADVANCE. 4h Setup 1 has N = 207 fills [UNCHECKED-BASE COUNT_POWER.md:18]: with redesign stop (1.0x ATR), cost_r = 0.068 R [OURS-UNREPRODUCED], breakeven p = 0.427 [OURS-UNREPRODUCED], MDE net R = 0.243 R [OURS-UNREPRODUCED], power at claimed +5 point edge (p=0.477) is 0.302 (30.2 %) [OURS-UNREPRODUCED], N for 80 % power = 783.3 trades [OURS-UNREPRODUCED]. 4h Setup 2 has N = 200 fills [UNCHECKED-BASE COUNT_POWER.md:19]: with redesign stop (1.0x ATR), cost_r = 0.061 R [OURS-UNREPRODUCED], breakeven p = 0.424 [OURS-UNREPRODUCED], MDE net R = 0.247 R [OURS-UNREPRODUCED], power at claimed +5 point edge (p=0.474) is 0.294 (29.4 %) [OURS-UNREPRODUCED], N for 80 % power = 782.8 trades [OURS-UNREPRODUCED]. Both 4h setups 1 and 2 are underpowered for a small 5-point win-rate edge (power ~30 % < 80 %), but powered to detect large effects (mean net R >= 0.243 R and >= 0.247 R). If observed mean net R is below MDE, the outcome is recorded as "underpowered / inconclusive", NEVER "no edge". Gate 0e passes CONDITIONAL on the recompute (Provenance section): N and power are re-counted with the new stop; if N for setup 1 or 2 falls below 100 the setup is INCONCLUSIVE IN ADVANCE.
- 0f Kill: Which result ends this source for good, and how many redesigns are allowed before it? The CryptoCred source is permanently KILLED (layer marked WONTFIX / DEAD, no further cards created or runs permitted) if: (1) On DEV: Neither 4h Setup 1 nor 4h Setup 2 achieves mean net R >= 0.0 R after fees across the pre-registered exit policies (fixed bracket, trailing swing low, FTA) on the primary 1.0x ATR stop; OR (2) On VALIDATION (single read): Combined mean net R <= 0.0 R after fees; OR (3) On sealed HOLDOUT: Combined mean net R <= 0.0 R after fees, OR the real strategy mean net R fails to exceed the 95th percentile of the matched random-entry null distribution. Exactly ONE (1) redesign attempt is permitted. This pre-registration constitutes that single redesign (4h HTF structure + invalidation stop with noise-unit buffer + trailing/FTA exits). If this redesign fails the backtest criteria, the redesign budget is exhausted (0 redesigns remaining) and the source is permanently closed. Gate 0f is strictly specified.

## 1. Source home: market, timeframe, session, holding period (with quote + file:line).

Answer: Home market is crypto (BTC/ETH perpetuals), so no market transfer is required [SOURCED HOME_FIT_AUDIT_CRYPTOCRED.md:12]. Timeframe is high timeframe structure on Daily (1d) and 4-hour (4h); entries and structure retests timed on 4h/1h. Structure breaks require a close on the same timeframe as the anchor [SOURCED extract_inqHN8q57X4.md:34, extract_BHwoN7VPrBE.md:106]. Continuous 24/7 market, so no session restrictions apply [SOURCED HOME_FIT_AUDIT_CRYPTOCRED.md:12]. Holding period is swing trading over days (typically 1 to 7 days for 4h structure, not intraday scalping) [SOURCED extract_XeQV2ECtZVQ.md:66, HOME_FIT_AUDIT_CRYPTOCRED.md:12]. Max holding period timeout cap is set to max_bars = 42 4h bars (7 days = 168 hours = 10,080 minutes) [OURS].
Evidence (file:line):
- `extract__ndAoizXy64.md:48` "I'll be trading high timeframe from the daily and weekly but a lot of my entries and management will be on the hourly timeframe"
- `extract_inqHN8q57X4.md:34` "if you've got a daily structure it's only broken if you get a daily candle close through it"
- `extract_BHwoN7VPrBE.md:106` "I want to see a daily close through that high or low to constitute a market structure break"
- `extract__ndAoizXy64.md:42` daily trades manage on daily + 4h/6h/12h
- `extract_XeQV2ECtZVQ.md:66` "soft stop... suitable for swing trades and less precise ideas"
- `HOME_FIT_AUDIT_CRYPTOCRED.md:12-14`

## 2. Ground truth: a ledger of the source's own trades read from frames (minute timestamps). The ledger is split into design and check sets.

Answer: NOT_IN_DATA. No dated CryptoCred trade ledger exists in repo data or public records (`HOME_FIT_AUDIT_CRYPTOCRED.md:18-21`). The five video extractions contain conceptual rules, diagrams, and retrospective examples, not timestamped trade execution logs with minute precision. Per Gate 0c, this missing input is recorded honestly; the layer remains an unverified hypothesis. Ground truth for detection logic is verified through deterministic hand-computed unit tests (Cases S1-S6 in `TEST_PLAN.md`).
Evidence (file:line):
- `HOME_FIT_AUDIT_CRYPTOCRED.md:18-22`
- `extracts/processed/cryptocred/` (5 files: `extract__ndAoizXy64.md`, `extract_BHwoN7VPrBE.md`, `extract_inqHN8q57X4.md`, `extract_XeQV2ECtZVQ.md`, `extract_Yp0k8HD5xro.md`)
- `MyTradingSys/backtest/layers/cryptocred/TEST_PLAN.md:1-30`

## 3. Recall (encoding fires on the check set) AND fire rate (not everywhere). Pass both before any P&L backtest.

Answer: Recall is NOT_IN_DATA due to lack of trade ledger (item 2). Fire rate on 4h DEV (30 months, 2022-01-01 to 2024-06-30, 5,472 bars):
- Setup 1 (S/R flip): 217 signals, 207 fills (6.90 fills/month, 1 fill every ~26.4 4h bars) [UNCHECKED-BASE COUNT_POWER.md:18].
- Setup 2 (Fib pullback): 200 signals, 200 fills (6.67 fills/month, 1 fill every ~27.4 4h bars) [UNCHECKED-BASE COUNT_POWER.md:19].
- Setup 3 (Failed MSB reversal): 22 signals, 22 fills (0.73 fills/month, 1 fill every ~248.7 4h bars) [UNCHECKED-BASE COUNT_POWER.md:20].
Total fills across setups 1 and 2 average ~13.5 fills/month on 4h, which satisfies the trader's requirement of selectivity ("most obvious or outstanding high or low", "smell test") without excessive sparsity. On 1d DEV (912 bars), fire rate is ~1.0 fill/month per setup (31 fills for setup 1, 30 for setup 2) [UNCHECKED-BASE COUNT_POWER.md:21-22], which is underpowered for standalone evaluation.
Evidence (file:line):
- `extract_BHwoN7VPrBE.md:12` swing "smell test" and selective high-conviction levels
- `COUNT_POWER.md:12-23`
- `HOME_FIT_AUDIT_CRYPTOCRED.md:25-28`

## 4. Data carries every proof input (aggressor side, real volume, OI, funding); missing inputs are NOT_IN_DATA, never 0 (B084/B136).

Answer: The three CryptoCred setups read only OHLC prices to compute fractal swings, MSB, and retests (`cc_setups.py:1-19`). No aggressor volume, order book depth, or open interest inputs are required by his core method.
Data verification for DEV window (2022-01-01 to 2024-06-30, 1,313,280 1m bars, zero gaps [UNCHECKED-BASE COUNT_POWER.md:6]):
30 monthly Binance BTCUSDT 1m kline files verified with exact SHA-256 checksums from `MyTradingSys/research/gross_effect_screen_2026-10-15/DATA_MANIFEST.csv`:
- `BTCUSDT-1m-2022-01.csv`: `4943153a1821c9b1004c619ef54837baefbf78a69f30c334051af05814b7ce39` [SOURCED DATA_MANIFEST.csv:2]
- `BTCUSDT-1m-2022-02.csv`: `b7fb123401c397e0fe80dba55db0532db3c95ac94a6c80189e0d06a08cbe8731` [SOURCED DATA_MANIFEST.csv:3]
- `BTCUSDT-1m-2022-03.csv`: `ac439203fa5953974ace41d4783e7e68c6fc8da12b6849b206d6ac202219def2` [SOURCED DATA_MANIFEST.csv:4]
- `BTCUSDT-1m-2022-04.csv`: `bd2aafb5a03111b4bd3d7a0180e1c1ab45490c3344326b62ce77110aa5f4efad` [SOURCED DATA_MANIFEST.csv:5]
- `BTCUSDT-1m-2022-05.csv`: `750b35643127b6d3001415f778ded10d28b9609a9a7e9470d5fab0432488ee9d` [SOURCED DATA_MANIFEST.csv:6]
- `BTCUSDT-1m-2022-06.csv`: `08e33417fc64107cafc9b930ca5e5daae49a5ce929b9ee1a6ccd0845ebf79aa3` [SOURCED DATA_MANIFEST.csv:7]
- `BTCUSDT-1m-2022-07.csv`: `b1d99b2d58514999fc59afb8b8842095057a9d59531be42640aa8f9fef12e1d4` [SOURCED DATA_MANIFEST.csv:8]
- `BTCUSDT-1m-2022-08.csv`: `be63b5c718611ebe90333c78cc35b5bf660fc9da8c2c50585513fee5640a7ee9` [SOURCED DATA_MANIFEST.csv:9]
- `BTCUSDT-1m-2022-09.csv`: `5d8adb1a9f3698c2da64b1f990d9a8dc98f2aa5ad5ced0c7e53c49237a1757a6` [SOURCED DATA_MANIFEST.csv:10]
- `BTCUSDT-1m-2022-10.csv`: `18bdebb2c3c2731b8ef9a45716fe3a6abd9ab6e212093e3b72662d5e58ce37c4` [SOURCED DATA_MANIFEST.csv:11]
- `BTCUSDT-1m-2022-11.csv`: `8763e1bc3d1a8e85c553249ec1f021e7e7c6a88dd44f6b0c491f7908f5093eec` [SOURCED DATA_MANIFEST.csv:12]
- `BTCUSDT-1m-2022-12.csv`: `bfc30590b4b4a235c1cd3ee4d8f5b5858992feac0086d0d2512c07c071a2618b` [SOURCED DATA_MANIFEST.csv:13]
- `BTCUSDT-1m-2023-01.csv`: `696430e1dc97a913e33cd47de5e775e43656cd366f36e364ad6aea60dd4851d3` [SOURCED DATA_MANIFEST.csv:14]
- `BTCUSDT-1m-2023-02.csv`: `fdedd0f51342917459a96c5d49582bff729346196a06e14d429f29f65d7894b9` [SOURCED DATA_MANIFEST.csv:15]
- `BTCUSDT-1m-2023-03.csv`: `278dd8fab5f7a5a80fd504c5b2e4c9b94f972106bc8cec1823f5578dce1f7386` [SOURCED DATA_MANIFEST.csv:16]
- `BTCUSDT-1m-2023-04.csv`: `95cc2eeff6b9f8ee4b355724ceb406b94250dcbe0a2d0dbc6de298657723672e` [SOURCED DATA_MANIFEST.csv:17]
- `BTCUSDT-1m-2023-05.csv`: `e4241efffd84d8dbcb8149fa453394ba14658be5700a9543a1b5031bcfc06357` [SOURCED DATA_MANIFEST.csv:18]
- `BTCUSDT-1m-2023-06.csv`: `5c40c5d56e27b113f2fafe7e29bdc17e6c7b2d68f8ab641bafade921ead48207` [SOURCED DATA_MANIFEST.csv:19]
- `BTCUSDT-1m-2023-07.csv`: `738805c6073f5ac74d0d713d5ca24b724afb7c0d83757c8f3a4dec4ebda621f7` [SOURCED DATA_MANIFEST.csv:20]
- `BTCUSDT-1m-2023-08.csv`: `e28570a7ef96012ba6983b2309241e356161d117b4590ea6e9ba93ecaf8171d8` [SOURCED DATA_MANIFEST.csv:21]
- `BTCUSDT-1m-2023-09.csv`: `c7145964a4124d8a96a99d8c97c9cc336d45bcf980f6de27db2a30b94a1393dd` [SOURCED DATA_MANIFEST.csv:22]
- `BTCUSDT-1m-2023-10.csv`: `8eb3bc9a557ab7daf9c75700209e50e2d8dc3e8e91d41ea0644f32ff3c967048` [SOURCED DATA_MANIFEST.csv:23]
- `BTCUSDT-1m-2023-11.csv`: `6823419707e45fd198edb266037f9d077cb7da9ee586480bea0be3f2149eaceb` [SOURCED DATA_MANIFEST.csv:24]
- `BTCUSDT-1m-2023-12.csv`: `8171a92a94ac6dd554eccdc20fc445bff8da97cad4ed77405987542374e16898` [SOURCED DATA_MANIFEST.csv:25]
- `BTCUSDT-1m-2024-01.csv`: `ab25f0fee86faa93df62f800adf92b742abdc60982e023159d0ca9faf3a4ba14` [SOURCED DATA_MANIFEST.csv:26]
- `BTCUSDT-1m-2024-02.csv`: `c5e5440d82285b059cf51e7271fa3e17596b7201b5b0185b0c3945b7242ad634` [SOURCED DATA_MANIFEST.csv:27]
- `BTCUSDT-1m-2024-03.csv`: `fb213d5bda7a27c50d63061d37d87bf1f9b16ebef083f465e3d3a97052854b7e` [SOURCED DATA_MANIFEST.csv:28]
- `BTCUSDT-1m-2024-04.csv`: `55ca319f8129a2da5aac7f3af0d9c9423116f19877b2278205e5fa2fe68b2103` [SOURCED DATA_MANIFEST.csv:29]
- `BTCUSDT-1m-2024-05.csv`: `9156e87e36d7c99c5e4fe5a74affe0f9a4bdbd64baeccc0e9d76f44b8dee7876` [SOURCED DATA_MANIFEST.csv:30]
- `BTCUSDT-1m-2024-06.csv`: `9dd0975779617caccc47784ec6c9e50d797c82fe4074478fc21944adad26c1dc` [SOURCED DATA_MANIFEST.csv:31]
Evidence (file:line):
- `MyTradingSys/research/gross_effect_screen_2026-10-15/DATA_MANIFEST.csv:1-31`
- `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:1-19`
- `HOME_FIT_AUDIT_CRYPTOCRED.md:32-35`

## 5. Profile/snapshot parity against the trader's own drawn levels or a raw-bar check (N3).

Answer: Video chart drawn levels are NOT_IN_DATA (video frames not transcribed to coordinate levels). Parity is established via raw-bar checks and deterministic test cases (Cases S1-S6 in `TEST_PLAN.md`) which check `find_swings` and `classify_msb` on hand-calculated synthetic bars. The swing detection algorithm (`cc_structure.py:15-35`) uses fractal swing highs/lows with strict inequality. Caveat from `COUNT_POWER.md:33`: synthetic gapless data rejects flat ties; live exchange klines have price micro-variations that form swings without divergence.
Evidence (file:line):
- `extract_BHwoN7VPrBE.md:12` "there's no single formula... recency... significance... smell test"
- `MyTradingSys/backtest/layers/cryptocred/TEST_PLAN.md:1-30`
- `COUNT_POWER.md:33`
- `HOME_FIT_AUDIT_CRYPTOCRED.md:38-42`

## 6. Cost per instrument; stop width in noise units; fee share of R < 0.25 R (VISION economics).

Answer: Cost model: ONE cost model chosen — Deribit BTC-PERPETUAL from `fees.py:22-29` (DERIBIT_TAKER = 0.0005, DERIBIT_MAKER = 0.0). Round-trip fee is 10 bps (0.0010) for all_taker and 5 bps (0.0005) for maker_entry [SOURCED fees.py:23-24]. (Binance 14 bps (0.0014) = 2 x (0.0005 fee + 0.0002 slippage) per round trip [SOURCED candle_patterns_2026-10-04/pilot/run_p1.py:27 and CANDLE_PATTERNS_RESEARCH_2026-10-04.md:19; components BINANCE_TAKER 0.0005 / BINANCE_MAKER 0.0002 at fees.py:27-28; the pure Binance taker fee RT is 10 bps] is reported alongside as a secondary sensitivity check only; it is not a second primary cost model).
Stop redesign: Replace the unsourced 0.10 % stop (which produced cost_r = 1.00 R in `COUNT_POWER.md:15`) with structural invalidation + an OURS buffer in noise units:
- Structural invalidation:
  * Setup 1 (S/R flip): Invalidation is the broken level being retested (`broken_level = entry_price`) [SOURCED extract_XeQV2ECtZVQ.md:33, cc_setups.py:62].
  * Setup 2 (Fib pullback): Invalidation is the far boundary of the Fibonacci zone (0.786 level) [SOURCED cc_setups.py:116,145].
  * Setup 3 (Failed MSB): Invalidation is the broken level that price failed to sustain [SOURCED cc_setups.py:213,236].
- Noise unit buffer: 14-period Wilder ATR computed on the signal bar (index `i`), without forward bars [OURS]. Median 4h TR fraction is 1.278 % (mean 1.626 %) [OURS-UNREPRODUCED, DEV klines].
- Recomputed stop width, cost R, and fee share on 4h DEV (primary buffer = 1.0x ATR [OURS]):
  * Setup 1 S/R flip: median stop width = 1.461 % [OURS-UNREPRODUCED], cost_r (all_taker) = 0.068 R (fee share = 6.8 % of R < 25 %) [OURS-UNREPRODUCED], cost_r (maker_entry) = 0.034 R (fee share = 3.4 % of R) [OURS-UNREPRODUCED].
  * Setup 2 Fib pullback: median stop width = 1.647 % [OURS-UNREPRODUCED], cost_r (all_taker) = 0.061 R (fee share = 6.1 % of R < 25 %) [OURS-UNREPRODUCED], cost_r (maker_entry) = 0.030 R (fee share = 3.0 % of R) [OURS-UNREPRODUCED].
  * Setup 3 Failed MSB: median stop width = 4.419 % [OURS-UNREPRODUCED], cost_r (all_taker) = 0.023 R (fee share = 2.3 % of R < 25 %) [OURS-UNREPRODUCED], cost_r (maker_entry) = 0.011 R (fee share = 1.1 % of R) [OURS-UNREPRODUCED].
- Sensitivity buffer grid in trial ledger [OURS]:
  * 0.5x ATR: Setup 1 med risk = 0.730 %, cost_r = 0.137 R (fee share 13.7 %); Setup 2 med risk = 0.892 %, cost_r = 0.112 R (fee share 11.2 %); Setup 3 med risk = 3.651 %, cost_r = 0.027 R. [OURS-UNREPRODUCED]
  * 1.5x ATR: Setup 1 med risk = 2.191 %, cost_r = 0.046 R (fee share 4.6 %); Setup 2 med risk = 2.380 %, cost_r = 0.042 R (fee share 4.2 %); Setup 3 med risk = 5.130 %, cost_r = 0.019 R. [OURS-UNREPRODUCED]
- 1d Timeframe (reference only, N < 100):
  * At 1.0x ATR: Setup 1 med risk = 3.703 %, cost_r = 0.027 R; Setup 2 med risk = 4.242 %, cost_r = 0.024 R; Setup 3 med risk = 21.242 %, cost_r = 0.005 R. [OURS-UNREPRODUCED]
All redesign variants satisfy `fee share of R < 0.25 R` and `stop width >= 0.40 %` (VISION economics).
Evidence (file:line):
- `extract_XeQV2ECtZVQ.md:33` "stop placement is inextricably linked with the trade idea itself your stop reflects your invalidation"
- `extract_XeQV2ECtZVQ.md:48` "strictness with stop usage and placement is inversely correlated with the size of the move"
- `extract_XeQV2ECtZVQ.md:78` "position size = (Portfolio x Risk%) / Distance to Invalidation"
- `MyTradingSys/backtest/fees.py:22-29`
- `HOME_FIT_AUDIT_CRYPTOCRED.md:46-48`
- `items/B143_cryptocred_stop_buffer_and_target_unsourced.md:12-20`

## 7. Fills: touch AND trade-through reported; the entry is on the passive side of price.

Answer: Setups 1 and 2: Resting limit order placed at the broken level / fib level at the close of the confirm bar (`placed_t`) [SOURCED cc_setups.py:79-84]. Fill condition: A subsequent 1m bar must trade through the level by at least 1 tick (0.1 USD) within the validity window (`find_limit_fill`, `run_cc_setups.py:105-120`) [SOURCED HOME_FIT_AUDIT_CRYPTOCRED.md:53-54]. Touch-fill count is reported side-by-side. The entry is on the passive side of price (maker entry on pullback). Setup 3 enters on market close of the failure-confirm bar (`run_cc_setups.py:17`, `cc_setups.py:211-212`).
Evidence (file:line):
- `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:105-120`
- `test_run_cc_setups.py:208`
- `HOME_FIT_AUDIT_CRYPTOCRED.md:52-55`

## 8. Exits match the trader's management, or the mismatch is stated (fixed bracket = a lower bound only).

Answer: Exit policies for the redesign are pre-registered across three models per CryptoCred's teaching:
1) Fixed Bracket Benchmark (Lower Bound): Fixed stop at invalidation + 1.0x ATR buffer; fixed target at 1.5R (setups 1-2) or 2.0R (setup 3) [OURS benchmark]. Mismatch is stated: fixed target is a conservative lower bound, not his full management [SOURCED HOME_FIT_AUDIT_CRYPTOCRED.md:58-61].
2) Trailing Exit (Trending Environment): Continually trailing the stop under swing lows (for longs) or above swing highs (for shorts) on 4h bars as new confirmed swing points form [SOURCED extract__ndAoizXy64.md:124-138].
3) First Trouble Area (FTA) Exit: Scaling out 50 % of the position at the first opposing swing level (FTA), moving the stop to the broken FTA structure (no automatic break-even on first reaction), and trailing the remainder under subsequent swing points [SOURCED extract_Yp0k8HD5xro.md:102,161-168; extract_XeQV2ECtZVQ.md:121-123].
Evidence (file:line):
- `extract__ndAoizXy64.md:124-138` "trailing stops under swing lows for trending; fixed at range boundaries/ATR for ranging"
- `extract_Yp0k8HD5xro.md:161-168` "swing trade graveyard - break-even on first reaction"
- `extract_BHwoN7VPrBE.md:82` "two reward for one risk instead of 1.5"
- `HOME_FIT_AUDIT_CRYPTOCRED.md:58-62`

## 9. Null like-for-like: same session window, same order type, same fill rules.

Answer: Random-entry null specification per `COUNT_POWER.md:35-42`:
1) For each real signal, draw a random entry timestamp uniformly across DEV 4h bars, preserving the long/short side ratio and validity windows without overlap.
2) Entry price set at the same limit offset in R from the bar close as the real signal, with identical limit-order validity window and trade-through fill rule on 1m bars.
3) Identical stop distance in % (median-matched risk: 1.461 % for setup 1, 1.647 % for setup 2) [OURS-UNREPRODUCED], identical target R, identical exit policies, identical timeout (max_bars = 42 4h bars), identical fees (Deribit all_taker and maker_entry).
4) 1,000 bootstrap resamples; fixed random seed = 42 [OURS].
5) Passing requirement: Real strategy mean net R must exceed the 95th percentile of the null distribution AND achieve two-sided 95 % CI lower bound > 0.
Evidence (file:line):
- `COUNT_POWER.md:35-42`
- `HOME_FIT_AUDIT_CRYPTOCRED.md:65-69`

## 10. Power: expected N per period computed before the run. If < 100, say "underpowered", never "no edge".

Answer: Expected N and power computed using `backtest/power_mde.py` on DEV (30 months, 2022-01-01 to 2024-06-30):
- 1d Timeframe: Fills are N = 31 (setup 1), N = 30 (setup 2), N = 1 (setup 3) [UNCHECKED-BASE COUNT_POWER.md:21-23]. All N < 100: Pre-registered as UNDERPOWERED / INCONCLUSIVE IN ADVANCE. No standalone 1d test will be run.
- 4h Setup 3: Fills N = 22 [UNCHECKED-BASE COUNT_POWER.md:20]. N < 100: Pre-registered as UNDERPOWERED / INCONCLUSIVE IN ADVANCE.
- 4h Setup 1 (S/R flip): Fills N = 207 [UNCHECKED-BASE COUNT_POWER.md:18]. N >= 100.
  With redesign 1.0x ATR stop: cost_r = 0.068 R [OURS-UNREPRODUCED], breakeven p = 0.427 [OURS-UNREPRODUCED].
  At claimed +5 point edge (p = 0.477): MDE net R = 0.243 R [OURS-UNREPRODUCED], power = 0.302 (30.2 %) [OURS-UNREPRODUCED], N for 80 % power = 783.3 trades [OURS-UNREPRODUCED].
- 4h Setup 2 (Fib pullback): Fills N = 200 [UNCHECKED-BASE COUNT_POWER.md:19]. N >= 100.
  With redesign 1.0x ATR stop: cost_r = 0.061 R [OURS-UNREPRODUCED], breakeven p = 0.424 [OURS-UNREPRODUCED].
  At claimed +5 point edge (p = 0.474): MDE net R = 0.247 R [OURS-UNREPRODUCED], power = 0.294 (29.4 %) [OURS-UNREPRODUCED], N for 80 % power = 782.8 trades [OURS-UNREPRODUCED].
Both 4h setups 1 and 2 are underpowered for detecting a modest 5-point win-rate edge (power ~30 % < 80 %), but powered for large effects (mean net R >= 0.243 R and >= 0.247 R). If observed mean net R is between 0 and MDE, the result is recorded as "underpowered / inconclusive", NEVER "no edge".
Evidence (file:line):
- `MyTradingSys/backtest/power_mde.py:19-52`
- `COUNT_POWER.md:12-23,27-34`
- `HOME_FIT_AUDIT_CRYPTOCRED.md:72-75`

## 11. Holdout: untouched by the ledger days and by every design look (N1); trial count includes extensions and recall iterations.

Answer: Data partitioning:
- DEV window: 2022-01-01 00:00 UTC to 2024-06-30 23:59 UTC (30 months, 1,313,280 1m bars, 5,472 4h bars) [OURS].
- VALIDATION window: 2024-07-01 00:00 UTC to 2025-06-30 23:59 UTC (12 months) [OURS] — to be read ONCE after DEV freeze.
- HOLDOUT window: 2025-07-01 00:00 UTC forward [OURS] — strictly SEALED. Untouched by any developer or runner.
Prior 1h trial history: 12 cells in stop sweep (`STOP_SOURCES.md:56-72`), 6 previous 1h reruns (`HOME_FIT_AUDIT_CRYPTOCRED.md:79-80`).
4h Redesign trial ledger (5 trials pre-registered before running):
- Trial 1 (Primary): 4h Setup 1 & Setup 2, Invalidation + 1.0x ATR stop, Deribit all_taker fees, Fixed 1.5R target.
- Trial 2: 4h Setup 1 & Setup 2, Invalidation + 1.0x ATR stop, Deribit all_taker fees, Trailing swing-low exit.
- Trial 3: 4h Setup 1 & Setup 2, Invalidation + 1.0x ATR stop, Deribit all_taker fees, First Trouble Area (FTA) 50/50 exit.
- Trial 4: Sensitivity arm: 0.5x ATR stop buffer, Fixed 1.5R target.
- Trial 5: Sensitivity arm: 1.5x ATR stop buffer, Fixed 1.5R target.
Total redesign trials = 5. Every trial is documented in advance.
Evidence (file:line):
- `HOME_FIT_AUDIT_CRYPTOCRED.md:78-82`
- `STOP_SOURCES.md:56-72`
- `MyTradingSys/research/gross_effect_screen_2026-10-15/DATA_MANIFEST.csv:1-31`

## 12. Stratified readout by regime and session (B154) next to the pooled number.

Answer: Stratified readout plan per B154 and CryptoCred teaching (`extract__ndAoizXy64.md:132-138`, `extract_BHwoN7VPrBE.md:82`):
1) Trend vs Range Regime:
   - Trend Bull: Price > 50-period SMA on 4h and 50 SMA sloping upward.
   - Trend Bear: Price < 50-period SMA on 4h and 50 SMA sloping downward.
   - Range / Consolidation: 4h ADX(14) < 20 or flat 50 SMA.
   - Sourced rationale: Trending environments favor continuation setups (Setup 1 S/R flip, Setup 2 Fib pullback) with trailing exits; ranging environments favor range-boundary targets and reversal setups (Setup 3 Failed MSB) [SOURCED extract__ndAoizXy64.md:138].
2) Volatility Regime:
   - High Volatility: 4h ATR(14) > 75th percentile of DEV window.
   - Normal Volatility: 25th to 75th percentile.
   - Low Volatility: < 25th percentile.
3) Session:
   - Although 24/7 continuous crypto trading applies, 8-hour UTC blocks (Asia 00:00-08:00 UTC, Europe 08:00-16:00 UTC, US 16:00-24:00 UTC) are reported alongside pooled figures as an execution sanity check.
Pooled and stratified results must be reported side by side in any future backtest report.
Evidence (file:line):
- `extract__ndAoizXy64.md:132-138`
- `extract_BHwoN7VPrBE.md:82`
- `items/INDEX.md:125` (B154 OPEN)
- `HOME_FIT_AUDIT_CRYPTOCRED.md:85-88`

## Provenance of the redesign numbers (Rule 11 fix, 2026-10-19)

- DECISION (OURS): the stop widths (1.461 %, 1.647 %, 4.419 %), the buffer grid, the 4h/1d true-range medians and the fire rates were produced by the prior session's DEV run of the committed `cc_htf_count.py` / `cc_setups.py` on the 30 klines files named in item 4; the script output was not committed and the Lenovo (no F: drive, no klines) cannot recompute it. They are therefore tagged OURS-UNREPRODUCED inline and in gates 0a/0b/0e (which pass only CONDITIONAL on the recompute): the backtest card MUST recompute them from the committed script before any P&L is read, publish the output file next to this document, and where a value differs the recomputed value governs and this file is amended before the run (changelog).
- cost_r = round-trip fee fraction / stop-width fraction (FORMULAS.md R definition; fee 0.0010 / 0.01461 = 0.068). The arithmetic and the power numbers below were recomputed independently on 2026-10-19 with `backtest/power_mde.py` (`power_mde(p, 1.5, cost_r, n)`, p = (1 + cost_r)/(1 + 1.5) + 0.05, n = 207 / 200): setup 1 power 0.3020, MDE 0.2432 R, N80 = 783.3; setup 2 power 0.2936, MDE 0.2473 R, N80 = 782.8. The 4h Binance-14 bp cost_r (0.096 / 0.085 / 0.032) was recomputed the same way.
- DECISION (OURS): the fill counts N = 207 / 200 / 22 come from COUNT_POWER.md, which used the old 0.10 % stop for its fills; the new stop can change which limit orders fill and how many trade. N is UNCHECKED-BASE and is re-counted by the backtest card with the new stop; power is re-run with that N; if N falls below 100 the setup is INCONCLUSIVE IN ADVANCE.
- DECISION (OURS): the item 3 "re-verified" wording was removed; nothing in this file claims a re-count of fills.

## Changelog

- 2026-10-18 fbc46cb8: file created (card cryptocred-prereg-4h-1d, prior session).
- 2026-10-19 Rule 11 review: BLOCK (Sonnet reviewer; defects: 14 bp mis-cited to fees.py:27-28; power figures "re-verified" without recipe; redesign numbers had no cited artifact; multipliers untagged; test too weak).
- 2026-10-19 fixes: 14 bp re-sourced to run_p1.py:27; power recipe and inputs added (recomputed with power_mde.py, values unchanged); redesign numbers tagged OURS-UNREPRODUCED with a mandatory recompute DECISION; multipliers tagged; stricter test (tags, redesign budget, verdict line).
- 2026-10-19 Rule 11 review 2: BLOCK (minor; defects: inline numbers tagged plain OURS and gates 0a/0b passed unconditionally; test partly vacuous).
- 2026-10-19 Rule 11 review: WAIVED. Review 2 BLOCK (minor) fixed; DECISION (OURS, coordinator 2026-10-19): ship without third review, defects were retag and test strength only.
