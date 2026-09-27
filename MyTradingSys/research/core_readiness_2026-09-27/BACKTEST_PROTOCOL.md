# BACKTEST PROTOCOL v1 — MTS (T051 L2-L4)
Opus 5.5, 2026-09-27. Status: PROPOSED (operator ratifies; then it is frozen like compiled_engine rules).
Extends SESSION_3_HANDOFF.md §4 (pipeline + gates P1/P2). Grounded in the standard literature
(Bailey, Borwein, López de Prado & Zhu 2014 "Probability of Backtest Overfitting"; Bailey & López de Prado
2014 "Deflated Sharpe Ratio"; López de Prado 2018 purging/embargo) and practitioner crypto-perp practice
(fees, funding, mark-price triggers, intrabar ambiguity). Where MTS differs from the textbook case it says so.

## 0. What MTS is testing (why the textbook needs adapting)
MTS is an event strategy: few, discrete signals (SETUP_FORMING ~23 in 2 weeks after D1/D4), each a trade with
a stop and targets. It is not a daily-return portfolio. So:
- the unit of evidence is the TRADE (R-multiple), not the daily return;
- sample size is the binding constraint — every claim carries a CI and a minimum-N rule;
- CPCV/PBO applies to variant SELECTION (thresholds, filters), not to the rule set itself.

## 1. Rule freeze and trial registry (the #1 professional control)
1. Before any run: rules, parameters and the exact code commit are frozen in `bt_runs/<run_id>/FROZEN.md`
   (git hash of verdict.py / SetupCandidatesBuilder / bt/*.py, D-rulings in force, CC-candidates on/off).
2. EVERY variant ever run is appended to `bt_runs/TRIAL_REGISTRY.csv` (run_id, date, variant, n_trades,
   mean_R, sharpe_per_trade). Nothing is deleted. N_trials for the Deflated Sharpe = row count of this file
   for the hypothesis family. A result reported without its trial count is invalid.
3. A change after seeing holdout results = new hypothesis, new registry family, holdout is spent.

## 2. Data split
- Development window: 2025-09-01 .. 2026-06-25 (~10 months). Walk-forward inside it (§5).
- HOLDOUT: 2026-06-26 .. 2026-09-26 (last 3 months). Untouched until the rules freeze; run ONCE.
- Parity window 2026-09-13 .. 26 is used only for gates P1/P2 (regeneration fidelity), never for performance.
- Regime tags on every trade (computed without look-ahead from prior 30d): trend-up / trend-down / range,
  realised-vol tercile. Results must be reported per regime; an edge that exists in one regime only is
  reported as such, not averaged away.

## 3. No look-ahead (checked, not assumed)
- Signal at candle close t; entry evaluated from the first bar with open_time > t (bt_engine enforces).
- L1 file-source adapter reads raw CSVs strictly <= t (design review: L1_ADAPTER_REVIEW.md).
- Funding: the rate is known only at its settlement; OI metrics (5m) usable only after their create_time.
- Mechanical test: run the pipeline with the future 24h of raw data deleted for 20 random signal times;
  verdicts must be byte-identical (look-ahead canary). Required before any L2 result is trusted.

## 4. Execution realism (Deribit BTC-PERPETUAL)
- Fees: taker on entry market/stop/timeout, maker on resting targets and ladder rungs. Use the CURRENT
  Deribit fee schedule (look up and record it in FROZEN.md; do not trust memory). Report gross AND net.
- Slippage: stop fills at trigger or bar open if gapped (worse). Add a fixed extra slippage stress of
  0 / 2 / 5 bps on market fills; the edge must survive 5 bps.
- Stops trigger on MARK (markPriceKlines); fills priced off trade bars. Report the Binance-vs-Deribit basis on
  the overlap (Deribit chart data) — if |basis| p95 > 10 bps, re-price fills with Deribit data.
- Intrabar ambiguity: default stop-first (conservative). Always also report target-first; the gap between the
  two is the "resolution risk". If it flips the sign of the edge, the result is INCONCLUSIVE at 1m and needs
  aggTrades resolution for the ambiguous bars only.
- Funding: Deribit perp funding accrues continuously; the Binance 8h rate is a PROXY. Report funding as its own
  line; stress with 2x funding.
- Ladders: rung fills when low<=rung (long), at the open if gapped; queue position ignored (optimistic) ->
  stress: a rung only counts as filled if price trades THROUGH it by 1 tick.
- Capacity: size is small vs BTC-perp depth; no market-impact model needed at testnet/mainnet test sizes. State it.

## 5. Validation design
- Walk-forward: rolling 3-month train / 1-month test inside the dev window, stepped monthly. For MTS the
  "train" step fits only the free parameters (proof threshold, distance caps if unfrozen, CC-candidate
  params); Tom rules are not fitted. Concatenate the OOS months -> the walk-forward equity curve.
- Purging/embargo: a trade whose holding period overlaps a train/test boundary is dropped from the side it
  leaks into; embargo = max_bars of the engine (default 1440 = 1 day).
- Variant selection (e.g. CC-1..CC-5 on/off, thresholds): build the T x N matrix of per-period returns for all
  variants and compute PBO via CSCV (S=16). PBO > 0.2 => the selection is not trusted.
- Deflated Sharpe (per-trade Sharpe, non-annualised) with N = registry trials, var_sr = variance of variant
  Sharpes: accept only DSR >= 0.95.
- Baselines every run: (a) random-entry null — same zones, same stop/target geometry, entry time shuffled
  within the same day, 1000 permutations -> empirical p-value of mean R; (b) "always WAIT" = 0;
  (c) Tom core without the layer under test (ablation). A layer is added only if it beats (c) out of sample.

## 6. Minimum evidence before a rule/layer enters the live engine
- >= 100 OOS trades for the layer (walk-forward + holdout combined) — below that, report as "insufficient N".
- Mean net R > 0 with bootstrap 95% CI lower bound > 0; win-rate Wilson CI reported.
- DSR >= 0.95, PBO <= 0.2 (if a variant was selected), random-entry p < 0.05.
- Survives: stop-first ambiguity, 5 bps slippage, 2x funding, through-the-rung ladder fills.
- Holdout result has the same sign and its CI overlaps the walk-forward CI.
- Parity gates P1 (Tom core 1-8 exact) and P2 (book proxy) passed for the data used.
Anything short of this = "not proven", and the engine keeps the rule OFF (fail-closed, same spirit as B071).

## 7. Report format (one per run, bt_runs/<run_id>/REPORT.md)
Frozen hash, trial count, data window, N trades (per regime), gross/net mean R with bootstrap CI, win rate with
Wilson CI, max drawdown in R, longest losing streak, exit-reason mix, ambiguity gap, funding share,
DSR, PBO (if applicable), random-entry p, ablation delta, holdout (only once).

## 8. Who builds what
- NUC builder (qwen3-coder): bt_data, bt_engine, bt_ladder, bt_stats (+ unit tests) — tasks 011-014.
- Sonnet: L1 file-source adapter per L1_ADAPTER_REVIEW.md, wiring L2 (verdict replay) -> L3/L4, registry, reports.
- Opus: reviews FROZEN.md before the holdout run and the first full REPORT.md.
