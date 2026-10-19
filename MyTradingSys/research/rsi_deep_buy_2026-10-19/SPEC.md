# RSI DEEP-BUY study: buy the RSI extreme in every timeframe, exit on RSI levels or divergence (spec, 2026-10-19)

Status: EXPLORATORY SPEC, nothing here is a trading rule. Written by the Supervisor (login C, JIS-NB) from the operator's words; the build and runs go to other machines and models (section 7).
Public repo: no runtime/order/account data. Fee-net out-of-sample results decide, never doctrine (PROJECT_VISION).

## 0. Operator request (SOURCED, operator 2026-10-19, chat)
1. First find, per timeframe (1m, 2m, 3m, 5m and likewise higher), how low RSI goes in the past ("how negative it goes").
2. Blindly buy when RSI reaches those lows; sell when RSI hits 40 in each timeframe.
3. Iterate with variants from Malkan's 40/50/60 loop: stay in while RSI enters 40, takes support on its MA, crosses 50, takes support on 50, heads to 60; leave on divergence (test 1m, 2m, 3m ... which TF's divergence exit pays best).
4. No stop loss. Price can keep falling after RSI turns up from its lowest point; the position may be added to (double, triple) as price falls. Test these permutations.
5. Hit-and-trial research, channelled properly; run it on different models.
Not required to follow Malkan's rules (OPERATOR); his 40/50/60 loop is a source for variants. Malkan quotes live in `extracts/processed/malkan/` and `research/rsi_2a_2026-10-09/RSI_2A_SPEC.md` (T3: Indian equities D/W/M, not crypto, not intraday: a transfer assumption, say so).

## 1. What already exists (reuse, do not rebuild)
`MyTradingSys/backtest/layers/rsi/`: `rsi_core.py` (RSI14, MA), `rsi_events.py`, `rsi_reclaim.py` (40/60 reclaim, dwell/depth), `rsi_divergence.py`, `malkan_40_60.py`, `malkan_mtf.py`, `run_rsi_backtest.py`, `run_divergence_mtf.py`. Fees: `fees.py` (0.10% taker round trip). Prior results: RSI divergence on every TF = no edge net of fees (`research/rsi_divergence_mtf_2026-10-09/REPORT.md`, 1m-5m all negative, t below -18). Event tables with forward MFE/MAE in R: layer_lab `gptb-rsi-reclaim-event-table`, `gptb-malkan-rsi-event-table`, `gptb-forward-excursion-helper`. Tape: BTCUSDT 1m klines, `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv` (NB) and `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz` (lab). Code-only machines (Lenovo) have no data.
What is new here: (a) the per-TF depth map, (b) entry at the extreme with NO stop, (c) scale-in ladders, (d) exits by RSI level or by divergence on a chosen TF, (e) account-level risk metrics, because a no-stop strategy cannot be judged by win rate.

## 2. Phase 1: depth map (descriptive, no trades)
Per TF in {1m, 2m, 3m, 5m, 15m, 30m, 1h, 4h, 1d} (resample 1m, UTC, a bar needs all its minutes), RSI(14) on close (SOURCED Malkan RSI 14; OURS for the TFs).
- Find RSI local minima (OURS: a minimum is the lowest RSI within +-k bars, k in {3, 5, 10}; k is a trial). Per TF per year report the distribution of minimum values below 30: count, p5/p10/p25/median, plus bars spent below 30, below 20, below 10.
- Output: `depth_map.csv` + a table in `DEPTH_REPORT.md`. These quantiles define the entry levels L_tf (OURS, chosen on DEV only): L in {p25, p10, p5 of DEV minima} per TF.
- Trap to avoid: "buy when it hits the lowest" is look-ahead (the lowest is known only afterwards). Entry arms are therefore defined on information available at the time:
  - E1 TOUCH: first bar whose RSI closes at or below L_tf; fill at the NEXT bar's open.
  - E2 TURN: RSI has been at or below L_tf and then rises by d points from its running minimum (d in {1, 2, 3}; OURS); fill at the next bar's open. The true bottom is never used.
  - E3 ORACLE (diagnostic only, labelled so, never a candidate): enter at the confirmed pivot low to show the ceiling of the idea. Its numbers may not be quoted as a result.

## 3. Phase 2: exits and position handling
Entry sizes in units of u (OURS: u = 1 unit of quote notional, spot-style 1x, no leverage in the headline arm; a 3x perp arm is a sensitivity only).
Exit arms (applied per TF with the same TF's RSI unless stated):
- X1: RSI(TF) crosses up through 40 (the operator's rule).
- X2: RSI crosses 50. X3: RSI crosses 60.
- X4 (Malkan loop): hold while RSI keeps the loop (after crossing 40 it stays above its own 40 line on closes, or above its RSI MA); leave when the loop breaks, i.e. RSI closes back below 40 after having crossed 50 (OURS reading of the loop; quote it from the extract where possible, else tag OURS).
- X5: bearish divergence on divergence-TF D in {1m, 2m, 3m, 5m, 15m} (use `rsi_divergence.py`, Malkan min 3 bars, close-to-close) after the entry; D is a parameter, the entry TF is separate.
- X6: time stop N bars (control arm, OURS).
Scale-in ladders (no stop; every add is a new unit at the next open):
- S0: no adds. S1: add 1 unit each time price falls a further a% below the last fill (a in {0.5, 1, 2}% scaled by the TF's median bar range; OURS). S2: double each add (1, 2, 4). S3: add on each new RSI low below the previous trough (the "lower low" case). Max adds M in {2, 4, 6}; after M the position just waits (no stop) or hits the ruin test.
- Exit applies to the whole stack at its average cost; fees on every fill.

## 4. Metrics (a no-stop strategy is judged on the account, not the hit rate)
Per arm and TF: fee-net return per trade and per DAY (days, not events, are the unit: events cluster; overlapping stacks are one episode), Holm-adjusted across the grid, realised MDE vs the effect (repo convention). Plus: max capital deployed, max adverse excursion in % and in units of u, longest underwater stretch (days), share of episodes still open at data end (reported separately, never dropped, mark at last price), equity curve with unrealised PnL, max drawdown, worst-day loss. RUIN TEST: replay 2022-11 (FTX), 2020-03 style and the 2024-08-05 flush: capital needed to survive with M adds and no stop; a ladder that needs more than the stated bankroll is rejected whatever its mean return. Funding for the perp arm taken from real funding files (no zero-fill; missing = NOT_IN_DATA).
Verdict thresholds (OURS, frozen before any outcome): fee-net mean per day above 0 on DEV and VALIDATION, same sign in more than half the years, t >= 2 after Holm, ruin test passed, at least 100 independent days of episodes.

## 5. Splits, trials, honesty
BTCUSDT 1m 2022-01-01 .. data end. DEV = 2022-01-01 .. 2024-06-30 (matches the layer lab guard `dev_split_guard`), VALIDATION = 2024-07-01 .. 2025-06-30, HOLDOUT after, read ONCE. All depth levels, k, d, a, M chosen on DEV, checked once on VALIDATION. Every variant (TF x entry arm x exit arm x ladder x D) is a row in the trial ledger (`layer_lab/TRIALS.md`) BEFORE its outcome is read; expect a few thousand cells, so Holm/BH counts the full grid. PRE_REG.md is committed before any outcome file (git log is the proof). Parameter labels: SOURCED (operator words, Malkan quote + file:line) vs OURS (everything else). ETH/SOL optional replication only after BTC passes VALIDATION.

## 6. Cards (created with this spec; order)
1. `rsi-deep-depth-map` (SONNET, run on NB data): Phase 1 only, writes `depth_map.csv`, `DEPTH_REPORT.md`. Smallest, unblocks everything.
2. `rsi-deep-prereg` (SONNET): freeze the grid and verdict rules into `PRE_REG.md` from sections 2-5 and the depth map; trial rows written first.
3. `rsi-deep-engine` (CODEX lane build, GPT luna): `episode_sim.py` = entry arms, exit arms, ladders, account metrics, ruin test, with fail-first tests on synthetic series (planted: a falling series that never recovers must show open-episode loss, not a win; ladder average-cost arithmetic; no look-ahead via `lookahead_lint.py`).
4. `rsi-deep-run-dev` (DSA-NB run lane, DeepSeek, exact commands): run the full grid on DEV, produce `grid_dev.csv`; Claude spot-checks ONE number by hand.
5. `rsi-deep-crossvendor-review` (Gemini via `gemini_queue.py`): review spec and engine diff for look-ahead and ladder bookkeeping; producer is never the reviewer. Lab_Guy independent re-derivation of the top cell (C2, shared base result).
6. VALIDATION read once, then HOLDOUT once, only for cells that survive; report with the ruin test first.

## 7. Model split (cheapest first, different vendors on purpose)
Claude Sonnet: depth map, prereg, review of the engine diff. GPT (codex lab on the NUC, luna medium): engine build and tests. DeepSeek (DSA-NB, 1m data on NB): the grid runs. Gemini Flash: cross-vendor review of spec and engine. Same hypothesis, independent implementations of the exit logic by two vendors (GPT engine vs a Sonnet re-derivation of the top cell) is the check that the ladder arithmetic is right.
