# B163 - 'Setup Alpha / Setup Beta' BTC perp handoff: implement and backtest as NO-SOURCE research

Status: OPEN. Severity: MED. Opened 2026-10-10.
Source: Control Room inbox, four items of kind requirement, full text verbatim in MyTradingSys/system/OPERATOR_INBOX.md:
711u1pgwu643b1yvewz9 (22:48Z), yj7c1p8t23rcl9ic0z6o (22:54Z), mk5rh9m8ic48g1glmgk0 (22:56Z), 5aepufr6439im1l1vumi (23:04Z), all 2026-10-09.

## Operator's words (verbatim excerpts)

> Long Entry: Daily Close > SMA(200) AND Daily Close > EMA(7) AND RSI(2) > ADX(2).

> **What Claude must implement / backtest**

> 3. Automatic detection of pre-marked levels + four-stage sweep logic.

## What it is

Two setups from a chatbot-written handoff (the pasted text ends with chatbot follow-up offers):
- Alpha: daily long-only/flat trend engine. Close > SMA200 plus a momentum filter (three variants across the four pastes:
  EMA7 + RSI(2) > ADX(2); EMA20/50 + ADX(14) > 20-25; Donchian 20/10 or Supertrend 10x3). Stop entry - 2x ATR(14); trail
  2x ATR behind highest close after +1 ATR.
- Beta: 15m/1h sweep of a pre-marked level (wick beyond, body back inside), CVD not confirming the new extreme, 5m market
  structure shift entry, stop 1-3 ticks past the wick, 1.5-3R target, 50% off at 1.5R, time stop 45-90 min, London/NY only,
  OI falling after the sweep.

## Provenance (CLAUDE.md hard rule)

No trader transcript behind any number; the performance claims (e.g. Donchian 48% CAGR, 55-68% win rate) are unverified
web summaries. So: research test only, labelled NO-SOURCE, never a live layer or a Tom filter. A trader source for any
part (e.g. Fabio's sweep/CVD rules, research/fast_track_2026-09-27/FABIO_RULEBOOK.md) would replace the matching number.

## What exists

- research/_archive/loose_2026-10/BTC_MA_SETUPS_RESEARCH_2026-10-03.md:64-75: 1d close x SMA200 gives 52 events 2020-01..2026-09 (18 OOS), below
  the 30-event gate, so Alpha needs a position-series test (daily returns while in), not an event test.
- research/btc_ma_2026-10-03/Q_ALL_ma_findings.md F1: crossover/momentum rules not robust out of sample after snooping control.
- research/_archive/loose_2026-10/T5_CVD_DEFINITION_2026-10-01.md (CVD definition), research/session_sweeps/ (session-open study).
- Kline taker-buy volume gives a per-bar CVD proxy; true multi-venue aggTrades are not on disk.

## Plan (waits on decision D22)

1. Alpha: long-flat position series on Binance BTCUSDT 1d 2018-2026, the three filter variants as written (no tuning),
   0.05% per side + funding; report CAGR, max DD, PF, time in market vs buy-and-hold, per regime year.
2. Beta: event study on 15m/1h with kline CVD proxy, previous-day high/low and equal highs/lows as pre-marked levels,
   rules exactly as pasted; report n, win rate, net R after fees.
3. Both go to DSA as desk tasks once D22 is answered.

## 2026-10-10 Control Room D22
Operator: "Run both as research tests" (note: "just for you - fresh eyes - see if there is something new in all this").
Applied: DSA desk tasks 20261009-231504 (Alpha) and 20261009-231505 (Beta), both labelled NO-SOURCE.
Fresh-eyes read: the one idea not already tested here is Beta's with/without-CVD comparison (does absorption add anything over a plain sweep reclaim); Alpha mostly repeats the 2026-10-03 MA research, so its likely value is drawdown cut, not return. Beta's task reports both rows.

## 2026-10-30 v2 re-run (card ask-p0-65-setup-alpha-beta-backtest)
v1 void: no DEV/VAL split, Beta n 708,240 was per bar, beta_sweep.py swing code read the next bar. v2 pre-registered (research/setup_alpha_beta_v2_2026-10/PRE_REG.md), run once, HOLDOUT sealed.
Result: Alpha FAIL (Sharpe and drawdown better than buy-and-hold in DEV, worse in VALIDATION; 4 and 11 entries). Beta S1 INCONCLUSIVE by the n floors (DEV n 50 mean -0.58 R, VAL n 23 mean -0.70 R fee-net), all 8 cells negative; kline-CVD absorption adds nothing over a plain sweep. See RESULT.md there.
