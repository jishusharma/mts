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

## Evidence added 2026-10-09 (volume study, MTS-2026-10-09-APP-ANA-btc-volume)

Volume is a volatility feature, not a direction feature. DEV 2020-2024H1, MyTradingSys/research/volume_2026-10-09/V0_RESULTS.md: autocorrelation of ln volume 0.67 (lag 1); next-bar range as a multiple of normal after a time-adjusted relative volume (RVadj) of 2-3 is 1.40 (1d) / 1.25 (4h), after >= 3 is 1.22 / 1.34;
hour-of-day volume share runs 2.4% (03-05 UTC) to 5.5% (14 UTC); Saturday volume is 0.62x. RVadj = volume / median of the same 4h slot over the previous 20 days (definition: PRE_REG_VOLUME_2026-10-09.md section 3, code vfeat.rv_adj). Use these as candidate forecast features; pre-register the estimator as this item already requires.
