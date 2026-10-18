# PRE-REGISTRATION: funding carry basis (frozen before any outcome)

Thread task 2026-10-18 (funding-carry-with-real-spot-basis-margi).
Question: In `published_strats_2026-10-13/supp_carry.txt`, funding-only carry yielded net annualized returns of 15.4% (DEV), 12.1% (VAL), and 6.2% (HOLD) with Sharpe ratios 10.70 to 18.65. That model assumed return = funding rate only, ignoring spot-vs-perp basis price risk, 4-leg execution fees, and margin/borrow constraints. Does real spot-vs-perp basis mark-to-market PnL, 4 legs x 0.10% fees, and margin/borrow leave a viable carry return, or is the edge nil?

This is a one-run study: the design, definitions, data sources, formulas, and gates are frozen below before any backtest is run. Not changed after the first outcome.

## 1. Data and Windows
- Symbol: BTCUSDT.
- Spot data: Binance official archive spot 1h and 1d klines (`data.binance.vision/data/spot/monthly/klines/BTCUSDT/`).
- Perp data: Binance official archive USD-M perp 1h klines (`data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1h/`) and 8h funding rates (`fundingRate/`).
- Stored under: `MTS_DUMPS` (`C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\Dumps\backtest`).
- Windows (SOURCED: `run_pub.py:24`):
  - DEV: 2021-01-01 00:00:00 UTC to 2023-07-01 00:00:00 UTC (911 daily bars).
  - VAL: 2023-07-01 00:00:00 UTC to 2024-07-01 00:00:00 UTC (366 daily bars).
  - HOLD: 2024-07-01 00:00:00 UTC to 2025-07-01 00:00:00 UTC (365 daily bars).
  - Sealed holdout from 2025-07-01 UTC onward is strictly NOT read (SOURCED: `run_pub.py:17,438`).
  - Reports will evaluate DEV, VAL, and HOLD side by side (`DEV+VALIDATION+HOLDOUT`).

## 2. Portfolio and Execution Model
All parameters labelled SOURCED or OURS. No parameter is tuned.
- Long 1 unit spot BTC, short 1 unit perp BTC (delta-neutral notional).
- Daily mark-to-market PnL (OURS):
  - Spot price change return: $(S_t - S_{t-1}) / S_{t-1}$
  - Perp price change return: $(P_t - P_{t-1}) / P_{t-1}$
  - Net price change return: $\Delta S_t / S_{t-1} - \Delta P_t / P_{t-1}$
  - Funding received: $+F_t$, where $F_t$ is the sum of settled funding rates in day $t$.
  - Daily gross return: $(\Delta S_t / S_{t-1} - \Delta P_t / P_{t-1}) + F_t$.
- Transaction costs (SOURCED: `run_pub.py:15,404`):
  - Fee: 0.10% per side per leg (cost 0.10 %).
  - Entry: buy spot + sell perp = 2 legs x 0.10% = 0.20%.
  - Exit: sell spot + buy perp = 2 legs x 0.10% = 0.20%.
  - Full round trip = 4 legs x 0.10% = 0.40%.
  - `CARRY_always` (no-exit always-on case): enters once at inception (2 legs = 0.20%), holds continuously, 0 exit fee.
  - `CARRY_switch` (switched on trailing 3-day funding sum > 0, SOURCED: `run_pub.py:334-338`): pays 2 legs (0.20%) on entry and 2 legs (0.20%) on exit.
- Borrow & Margin models (OURS):
  - Arm 1 (Primary): Unlevered cash-and-carry (1x leverage), borrow rate = 0.0% (spot BTC posted as portfolio collateral or 100% unlevered capital base).
  - Arm 2: Switched carry, unlevered (1x leverage), borrow rate = 0.0%.
  - Arm 3 (Sensitivity): 3x margin carry (3:1 leverage, equity = 1/3 notional), returns scaled 3x, with liquidation check against 1h bar lows (assets / borrowed debt <= 1.10 maintenance threshold on spot margin, or perp spikes > 32.8% intraday).

## 3. Metrics and Baseline Comparison
- Metrics:
  - Net annualized return (`ann` %, simple daily return x 365 x 100).
  - Annualized Sharpe ratio (`sharpe`, daily mean / daily std x sqrt(365)).
  - Maximum drawdown (`mdd` %, peak-to-trough on cumulative equity curve).
  - Worst 30-day rolling return (`worst_30d` %, 30-day cumulative rolling window).
- Baseline comparison (SOURCED: `published_strats_2026-10-13/supp_carry.txt:1-3`):
  - DEV: net_ann = 15.4%, sharpe = 10.70, mdd = -0.4%
  - VAL: net_ann = 12.1%, sharpe = 18.65, mdd = -0.0%
  - HOLD: net_ann = 6.2%, sharpe = 18.40, mdd = -0.1%
- Haircut sensitivity table:
  - Fee sweep: 0.00%, 0.02%, 0.05%, 0.10%, 0.15%, 0.20% per side.
  - Basis adverse move tolerance: what cumulative basis drag reduces net return to zero.

## 4. Verdict Arms and Stopping Rule
Primary arms registered for evaluation:

| arm | description |
|---|---|
| CARRY_always_unlevered | Always-on carry, 1x unlevered, spot-perp basis MTM + funding + 2 legs entry fee |
| CARRY_switch_unlevered | Switched carry on trailing 3d funding > 0, 1x unlevered, 4 legs fees per trade |
| CARRY_always_margin3x | Always-on carry, 3x margin, liquidation check at 1h lows |

FAIL means stop: cash-and-carry basis trading on BTC perp is nil or unviable if DEV net annual return is <= 0.0% or worst 30-day drawdown exceeds 15% unlevered.
