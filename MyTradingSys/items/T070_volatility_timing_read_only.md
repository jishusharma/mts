# T070 - P6: Volatility timing read-only analysis

Opened 2026-10-06 by MTS-2026-10-06-1254Z-APP-ANA-research-agenda. Status QUEUED. Source: research agenda follow-up.

## Scope

Read-only analysis: does next-session realized volatility prediction improve existing Tom/Fabio stops without changing rules?
- **Input:** Time of day + recent range/OI (orderflow_1m features)
- **Prediction:** Forecast realized volatility (realized range, Parkinson estimator)
- **Test:** Would volatility-scaled stop width/size lift net R on existing Tom and Fabio live entries? (no rule changes, no position changes, no new trades)
- **Analysis:** Compute scaled stops; overlay on live results to measure would-have-been P&L improvement

## Rationale

P1 (passive execution cost negligible) + P2/P4 partial results suggest edge depends on execution and timing, not signals. Volatility-aware stops may reduce whipsaw without changing setups.

## Constraints

READ-ONLY: No changes to live trading, execution, or position sizing. Analysis only.

## Pre-registration

Must pre-register:
- Volatility estimator formula (realized range, Parkinson, Garman-Klass, etc.)
- Time-of-day proxy features
- Stop-scaling function (how width scales with vol forecast)
- Backtest dates and symbols

## Deliverable

Output: MyTradingSys/research/P6_VOLATILITY_TIMING_YYYY-MM-DD.md
Metrics: existing net R vs would-have-been scaled-stop net R (both sides: improve/degrade/no change)
