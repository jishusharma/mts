# BIG-TRADE BACKTEST PLAN 2026-10-09

Session: MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt. Operator directive (chat, 2026-10-09): backtesting exists so the layers
FIRE on good, big trades and are PROFITABLE; parameters may be tuned toward that. It is no longer a pass/fail gate
for "does this rule have edge". Spawn cheap local workers; run a separate thread on chart/screenshot observations.

## 1. What the audits already say (do not redo)
| Finding | Source |
|---|---|
| Tom core: gross R <= 0, net R -2.91 (fee ~2.76 R/trade after stop floor removal); live rule 0 signals (was 17) | TOM_CORE_BT_RERUN_2026-10-06.md |
| T055 C1 funding_cvd_fade FAIL, C2 session_momentum FAIL (full funding) | T055_BT_RERUN_FULLFUNDING_2026-10-07.md |
| CryptoCred setups 1-3 FAIL once the limit-fill bias was fixed | CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md |
| Fabio v3 L3-FAIL; Fabio OF 0/64 variants net-positive OOS; fee drag 0.66 R at 0.05-0.2% stops | PRE_REG_FABIO_V3.md, FABIO_OF_REPORT.md |
| Live testnet ledger 2026-09-28..10-08: 333 closed; 262 turn_of_candle 1m (net -3.02 USD), 28 rsi 5m, 9 rsi 15m, 3 rsi 1h (+9.75, 2 hit target). ~97% exit by time_exit, almost none by target | auto_trades.jsonl (this session) |

Diagnosis: every test so far used fixed-horizon or tight-stop trades and asked "is there edge net of fees". None asked
"how many BIG moves did the layer see, how early, and what does a trade managed to ride them pay". Tight stops make
fee-per-R huge; live trades are scalps closed by timer. The missing backtests are below.

## 2. Backtests needed now (in order)
| # | Backtest | Question it answers | Wave |
|---|---|---|---|
| A | Big-move ground truth + layer CAPTURE matrix | Per layer x TF x side: of all big legs, how many had a same-side fire early enough to catch them (recall, lead)? Of all fires, how many were followed by a big leg (lift vs base rate)? | 1 |
| B | Fire history for every layer on current live params | Gives A its fire lists. B1 = kline-only layers, B2 = order-flow/Tom/funding layers | 1 (B1), 2 (B2) |
| C | Runner-management backtest | Same fires, exit policies: current time_exit vs bracket vs BE@+1R then trail vs hold-to-structure. Net of Deribit fees, limit-fill model | 2 |
| D | Walk-forward parameter tuning per layer | Pre-registered small grids; objective = net R expectancy and big-leg recall together; trial registry + PBO | 3 |
| E | Module gap list | Which layers/modules have never been backtested at all, with the data each needs | 1 (inventory, by supervisor) |
| F | Chart/screenshot observations | What the operator's charts show that the Java snapshots/data do not (thread runs in parallel, no dependency) | 1 |

## 3. Definitions (analysis settings, printed in every report; they are not trading parameters)
- ATR(14) on the layer's own TF (Wilder). R = 1 ATR of the TF at the fire bar close.
- Big leg (ground truth, hindsight by design): from a swing pivot to the opposite pivot. Pivot = bar whose extreme is not
  exceeded for N bars either side with the leg reversing at least r x ATR; report r in {1.5, 2.0} and a leg size threshold
  k in {3, 5, 8} x ATR. Output every leg with all (r, k) flags so thresholds are columns, not a choice.
  Also per-bar forward label: MFE_atr and MAE_before_MFE_atr over H bars, H in {24, 96} bars of the TF.
- A fire is CATCHABLE for a leg if side matches and fire time t satisfies leg_start <= t <= leg_start + 25% of leg duration
  (EARLY), 25-50% (MID), later (LATE, not counted as capture). Report all three buckets.
- Causality: a fire uses only bars closed at or before t. Entry is the next bar open (market) or a resting limit with a
  fill rule (no fill = no trade). Never fill at a level after the bar that proves it (CryptoCred lesson).
- Costs: MyTradingSys/backtest/layers/positioning/trade_costs.py (fee + slippage + funding). Deribit maker/taker per
  FORMULAS.md. Expected numbers in tests are hand-computed, never taken from the code under test.

- Stop model (F-BT-01): every fire carries stop_dist_atr and fee_R = round-trip fee / stop distance. Stops are structure level +/- k x ATR(TF);
  k is a tuned parameter, never zero. Any fire with stop distance under the round-trip fee is flagged `fee_dominated` and reported separately.

## 3b. Findings protocol (operator rule 2026-10-09: observe something wrong -> report -> audit -> fix)
Anything off or wrong that a worker sees (data gap, impossible number, doc contradicting disk, code disagreeing with its spec, a layer behaving
unlike its backtest) is appended to FINDINGS.md using its template BEFORE the worker moves on. Audit = an independent re-check by script or a
second read, plus a search for other instances. Fix = code or doc change with a test that fails on the old state; live-path files are staged as
`.new` and escalated. The worker's final reply lists its finding ids. Open findings: F-BT-01 (degenerate stops), F-BT-02 (turn_of_candle).

## 4. Splits and anti-overfit rules
- TRAIN 2022-01..2024-12, VALIDATE 2025-01..2025-06, HOLDOUT 2025-07..2026-09 (do not open until one frozen candidate per layer).
  SUPERSEDED 2026-10-17 (DECISION OURS): repo split applies, TRAIN to 2024-06-30, VALIDATE 2024-07-01..2025-06-30; see backtest/bigtrade/SPLIT_ALIGNMENT_2026-10-17.md.
- Every grid cell is a registered trial: append to research/fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv (existing format).
- A tuned value needs: IS and VALIDATE net expectancy > 0 with the same sign, PBO (CSCV, MyTradingSys/backtest/bt/bt_stats.py or
  ref_pbo.py) < 0.5, n >= 30 trades in each split, then one look at HOLDOUT. FAIL closes the candidate; no re-tuning on HOLDOUT.
- Provenance (CLAUDE.md): operator override 2026-10-09 allows tuning for this purpose. A tuned value is labelled
  `BT-TUNED <run_id> <split results>` and is NOT NO-SOURCE. It is never written into a live file by a worker.
  Where the trader's own words give a range, tune inside that range and cite it.

## 5. Files and schemas
- Code (new, not imported by live processes): MyTradingSys/backtest/bigtrade/ . Tests beside it, in run_all_tests.py list at promote time.
- Data (gitignored store): F:\MTS\data\bigtrade\ . Reports: MyTradingSys/research/bigtrade_2026-10-09/ .
- `legs_<TF>.csv`: leg_id, tf, side(long|short), t_start_ms, t_end_ms, p_start, p_end, size_atr, atr_at_start, dur_bars, flags_r1.5_k3 ... (one 0/1 column per r,k).
- `fires_<layer>.csv`: layer, key, tf, side, t_fire_ms (close of the bar that fired), price, params_id, params_json, code_commit.
- Layer keys follow the live names (layer:turn_of_candle:turn_of_candle:1m, layer:rsi:rsi_events:5m ...).
- Data on disk: 1m klines 2022-01..2025-08 (Dumps/backtest/raw_1m_2022/klines, monthly), 2025-09..2026-10 (Dumps/backtest/raw/klines),
  funding 2020-01.. (raw/fundingRate), OI metrics 2025-09.. (raw/metrics), aggTrades 2024-12.. (F:\MTS\data\orderflow_1m), Tom rows
  (F:\MTS\data\tom_bt_2026-10-07). Check coverage yourself before relying on a range and state it in the report.

## 6. Hard rules for every worker
Live tree runs the testnet system. Do not edit, move or restart anything under MyTradingSys/execution/ or
MyTradingSys/backtest/layers/alerts/, or any file auto_trader, position_manager, daily_loss_monitor, live_runner_cli import.
New files only, plus the TRIAL_REGISTRY append. No HALT files, no orders, no `.secrets/`, `.env`. Testnet only.
Write files with newline='\n'. Long patches go in a .py script. Do not commit; report paths. Never conclude from truncated output.

## 7. Module gap list (supervisor, from audits)
Backtested at all: Tom core (rows), T055 C1/C2/C3, CryptoCred 1-3, Fabio L1/OF/v3, RSI events (grid), session_momentum, turn_of_candle (alert-only).
Never backtested on history: turn_of_candle as the live 1m trader (262 live trades, no side edge study), malkan_40_60 / malkan_mtf,
tick extremes / OI extremes, rsi_events 1h/15m/5m on current live params for big-leg capture, any exit policy other than time_exit,
HTF context (R4), consensus writer. Tom's value-area/sweep concepts as a capture check (OPERATOR_ASKS 10-05 ask 1: stop-run then reversal).
