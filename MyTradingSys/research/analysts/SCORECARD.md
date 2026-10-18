# Imbalance & Price Action Analysts Multi-Provider Scorecard
**Date**: 2026-10-18  
**Status**: ACTIVE INGESTION & EVALUATION LEDGER  
**Methodology**: Binance BTCUSDT 1m klines, 0.05% fee per side (SOURCED: `MyTradingSys/backtest/layers/FORMULAS.md:s17`), stop checked first inside each bar (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:83-84`).

## 1. Summary Performance by Analyst

| Analyst | Platform | Imbalance Construct | Total Ingested | Evaluated | Win Rate | Net R Sum | Profit Factor | Status |
|---|---|---|---|---|---|---|---|---|

## 2. Statistical Power vs. Coin Flip (H0 = 50%, Claim = 67.1%)

Exact binomial test of true edge over random chance at alpha = 0.05 (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:38`):

| Scored Calls n | Power vs Coin Flip | Minimum Wins Needed to Reject H0 |
|---|---|---|
| 10 | 10.9% | 9 |
| 30 | 60.5% | 20 |
| 56 | 81.0% | 35 |
| 86 | 92.1% | 52 |

Threshold for 80% statistical power: **56 scored calls** (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:51`).

## 3. Active Call Ledger

| Call ID | Published (UTC) | Analyst | Direction | Entry | Stop | Target 1 | Risk | Status |
|---|---|---|---|---|---|---|---|---|

## 4. Execution & Audit Rules
- All signals require explicit Entry, Stop Loss, and at least one Target before scoring.
- Limit orders not reached within 24 hours are marked `NOT_FILLED` and discarded from win rate calculation.
- Positions still open after 7 days are closed at market.
- Taker fee of 0.05% applied to both entry and exit (total 0.10% round trip).
