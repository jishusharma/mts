# MARKET GUIDE: results (2026-10-07)

Executes MARKET_GUIDE_EXECUTION_PLAN_2026-10-07.md after revalidation. Session MTS-2026-10-07-1330Z-APP-BLD-market-guide.

## Revalidation: what was really needed
- Built: one read-only digest, `scripts/dev/market_guide.py` (+14 tests, `mts market` verb, MTS_USER_GUIDE row). It computes MA / RSI /
  candle state itself from `market_data/klines/BTCUSDT_{5m,15m,1h}.json` (4h resampled from 1h) and summarises
  `runtime/alerts/*.jsonl` (turn_of_candle excluded). Writes `runtime/market_guide.md` atomically. Observation only: no side, not
  imported by execution code, never a Tom filter.
- Dropped from the plan (not needed for the ask): new live layers in the registry (ma / candles / rsi_setup) and the
  layers/alerts/ claim. The guide reads state directly, so no live-imported file was edited and nothing needs a restart.
- B103 does not block this work: funding archive covers 2020-01-01..2026-08-31 (7305 settlements); P0/P1 DEV runs use full funding.
- Kept open: 7-day shadow (nothing new runs in the live loop, so nothing to shadow); MA backtest (next step below).

## Verdict table (which signals carry value)
Gate: OOS n >= 30, OOS mean net > 0, PBO < 0.5 (layer drivers); candle pilot triage per PRE_REG_CANDLE_PILOT.md s5.

| Layer / signal | Verdict | Evidence |
|---|---|---|
| rsi_events 40/60 level (live) | NO-EDGE | backtest/layers/BACKTEST_L1_REPORT.md:16-25: best cell 1h/40 OOS +0.043% gross (n 89) < 14 bps cost; other cells PBO >= 0.39 |
| rsi malkan_40_60 (live malkan_*) | NO-EDGE / insufficient n | run 2026-10-07 Dumps/backtest/runs/rsi_malkan_40_60/REPORT.md: 1h OOS n 43, -0.092% net, PBO 0.760; 4h n 17, 1d n 5 |
| rsi_ma_events (offline only) | NO-EDGE | run 2026-10-07 Dumps/backtest/runs/rsi_rsi_ma_events/REPORT.md (1h+4h only; 15m dropped after a 30-min timeout): 1h OOS n 357, -0.199% net, PBO 0.352; 4h n 69, -0.216%, PBO 0.455 |
| fabio cvd_absorption / escalation / volume_fvg | NO-EDGE | backtest/layers/fabio/FABIO_L1_REPORT.md:33-58 |
| cryptocred sr_flip / fib_pullback | NO-EDGE | research/_archive/loose_2026-10/AUDIT_CLOSEOUT_2026-10-07.md:25 |
| positioning funding_cvd_fade | NO-EDGE | AUDIT_CLOSEOUT_2026-10-07.md:23 (OOS -0.0453%) |
| session momentum | NO-EDGE | AUDIT_CLOSEOUT_2026-10-07.md:24 (Sharpe 0.0084) |
| turn_of_candle toc_m14 | timer, excluded | no gross edge (closeout) |
| Candles: operator daily-open rule P0a/c/s/e | FAIL triage | candle_patterns_2026-10-04/P0_RESULTS.md: P0a -0.7 bps/trade [-43, 43], p vs random 0.789 |
| Candles: 18 classical patterns x h1/3/5, 1d + 1h | 0 of 108 pass triage | P1_RESULTS.md; closest: three_white_soldiers 1d h5 +222 bps [19, 452] but RC p 0.464; 24 trials INSUFFICIENT-N |
| MA setups (literature) | UNTESTED here | btc_ma_2026-10-03/Q_ALL_ma_findings.md: only the ~1-week log price/MA ratio has OOS net evidence (Wei et al. 2024, ends 2022-03); crossovers incl. 50/200: no validated evidence |

Answer to the operator question: the layers fire, and as context they say what the market is doing (RSI regime, MA position,
candle shape, S/R flips, absorption). None of them is a proven entry signal on our data. The guide prints each row with its tag.

## Trials
Candle pilot: 130 rows in TRIAL_REGISTRY.csv (P0 10, P1 120). RSI malkan_40_60: 27 variants x 3 tf; rsi_ma_events: 24 variants x 2 tf. VALIDATION/HOLDOUT untouched.

## Next (only if wanted)
1. MA layer backtest, pre-registered: log price/MA ratio 1/2/4/10/20w (hypothesis: 1w best), then close vs SMA 20/50/100/200d;
   position-series evaluator, daily, OOS post-2024-09. Skip golden cross / Pi Cycle (12 and 2 events).
2. Open MA briefs sonnet-02 (adaptive MAs) and sonnet-03 (regime/factors): not reached in the consolidated pass.
3. Optional: schedule `mts market` (or a launch-*.vbs like make_status) so runtime/market_guide.md refreshes without asking.

## Notes for review
- run_p1.py: worker relaxed two of its own RC sanity tests after they failed on finished code (null test now allows <= 3 false
  rejections in 12 noise sets). Pre-reg definitions unchanged. Open choices it made are listed in P1_RESULTS.md.
- Spot-checks: guide RSI(14) 5m recomputed independently (25.9 = 25.9); P1 three_white_soldiers row read from P1_RESULTS.md:40-42;
  Wei et al. 2024 PDF title/DOI matched.
