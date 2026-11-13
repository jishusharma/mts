# PRE_REG: cross-sectional momentum / reversal, Bybit USDT perps, weekly (edge-xsec-momentum-1113)

Frozen before any strategy outcome is computed. Code: study.py (written after this file is committed); data: fetch_data.py.

## Hypothesis
Within a liquid crypto-perp universe, coins with higher trailing return keep outperforming over the next week (momentum), or
the trailing 1-week winners mean-revert (reversal). The net of taker fees and funding, market-neutral, is positive.
SOURCED: academic literature on crypto cross-sectional momentum / short-term reversal (generic, no single paper relied on). All parameters below are OURS.

## Data
Bybit v5 public: instruments-info, kline (interval D), funding/history. Candidate set = linear USDT perps with launchTime <= 2021-12-31
(history since 2021). Delisted perps are not served, so the candidate set carries survivorship (stated limitation; the per-date
universe below removes the look-ahead part of the bias only).

## Rule (every number OURS unless marked)
| Item | Value |
|---|---|
| Rebalance | every Monday 00:00 UTC; entry at that day's daily open, exit at next Monday's daily open |
| Universe at date t | candidates with >= 29 daily bars strictly before t, top 20 by mean daily turnover (USDT) over the 30 days before t; >= 10 members required else skip week; list recorded per week |
| Signals (known at t) | R7, R14, R28 = close[t-1d]/close[t-1d-k]-1 (k = 7, 14, 28 days) |
| Quintile size | q = floor(N/5) (4 for N=20) |
| Cell MOM-k (k=7,14,28) | long top q equal weight (sum +1), short bottom q equal weight (sum -1); market neutral |
| Cell REV-7 | long bottom q on R7, short top q on R7 |
| Cell LO-k (k=7,14,28) | long top q on Rk (sum +1) minus equal-weight universe (each 1/N): weights net w_top - 1/N; excess over universe |
| Cost | fees.BINANCE_TAKER (SOURCED in repo fees.py) x sum of absolute weight change per rebalance, weights drifted by the week's returns before trading, positions leaving the universe are closed; first week pays full entry |
| Funding | for each held symbol, sum of Bybit funding rates stamped in [t, t+7d); pnl = -w_i x sum(rate); missing history = 0 and counted |
| Gross return | sum w_i x (open[t+7d]/open[t] - 1) |
| Weekly net | gross - fees + funding |

Cells (7 in total): MOM-7, MOM-14, MOM-28, REV-7, LO-7, LO-14, LO-28.

## Splits
DEV 2020-01-01..2024-06-30 (reported, not used to tune; nothing is tuned) / VALIDATION 2024-07-01..2025-06-30 / RECENT 2025-07-01..now.
Weeks are assigned to a split by their Monday date.

## Metric and pass rule
Primary metric: mean weekly fee-and-funding-net return, per split, per cell. Pass (per cell) = VALIDATION net mean > 0 AND moving-block
bootstrap (blocks of 4 weeks, OURS; 10000 resamples, seed 1113) 95% CI lower bound > 0 AND n >= 30 weeks AND mean above the 95th
percentile of the placebo means AND BH-10% significant over the 7 cells (one-sided bootstrap p that mean <= 0, VALIDATION).
RECENT is reported separately with the same statistics and never used to select. Verdict PASS / FAIL / UNDERPOWERED (n < 30 or CI wider than 2x |mean|).
Placebo: each week assign the same number of long and short names at random from the universe (quintile size q), 200 draws, same fees and funding, same split; compared with cell means (long-only placebo is a random q-set minus the EW universe).

## Context
Regime: none as a gate, because the factor is market neutral by construction; the BTC weekly regime mix (up > +5%, down < -5%, else range, OURS) is reported per split.
Phase: none, because no cycle phase is claimed; a descriptive all-phase factor test.
Session: none, because weekly Monday 00:00 UTC rebalance, no intraday timing.
Entry: Monday 00:00 UTC daily open at market (taker), exit at the next Monday open.

Regime mix: filled below from BTCUSDT weekly returns (data only, no strategy outcome).
Regime mix: BTCUSDT Monday-to-Monday weeks (bull = up > 5%, bear = down > 5%, else range; shares in %, bull/bear/range):
DEV 222 weeks 27/18/55; VALIDATION 53 weeks 26/9/64; RECENT 70 weeks 11/17/71. BTC daily data starts 2020-03-25, so DEV effectively starts there; the tested universe starts later still (>= 10 members).
Read: VALIDATION is a bull-leaning, low-bear year (only 5 bear weeks); a momentum result there says little about bear weeks, so RECENT (most bear weeks) is the check.
