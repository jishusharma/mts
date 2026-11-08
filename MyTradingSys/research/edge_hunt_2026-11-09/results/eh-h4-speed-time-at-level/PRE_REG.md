# PRE_REG: eh-h4-speed-time-at-level (trial T05)

Card: edge-hunt-plan-opus-1109 (wave 1). Brief: workers/eh-h4-speed-time-at-level.txt. Frozen before any return is computed.
Trial: T05 only (TRIALS.md). Exploratory 2x2 is labelled exploratory and cannot promote.

## Hypothesis
WICKS_NOTE s5: "Fast in + no time at the level + reclaim = wick; fast in + time at the level + no reclaim = acceptance."
T05: a fade of a prior-day high/low touch in the cell "fast in (top tercile of 12-bar speed on DEV) AND reclaim within 3 bars AND at most 2 bars spent within 0.2 % of the level (counted only up to the reclaim bar)" has mean net R > 0 (stop at the extreme, 2R, 96 bars), both sides pooled.

## Rules table (frozen)
| Item | Rule | Label |
|---|---|---|
| Data | BTCUSDT USD-M 15m klines and fundingRate, data.binance.vision via fetch_binance_archive.py, cached at F:/MTS/Dumps/backtest/eh-h4-speed-time-at-level | public archive |
| Data start | 2020-01-01. The archive returned 404 for BTCUSDT 15m klines 2019-09-08..2019-12-31 (monthly and daily, checked 2026-11-09), so the effective start is 2020-01-01. The brief's "data start" for DEV is read as this | OURS (archive fact) |
| Split | DEV = 2020-01-01 .. 2024-06-30 23:59. VALIDATION = 2024-07-01 .. 2025-06-30, read once, only if DEV screens in. HOLDOUT = 2025-07-01 on, never loaded. The loader raises on any bar at or after 2025-07-01 and on any DEV read past 2024-06-30 | brief s-splits; repo splits.py uses DEV_START 2022-01-01, not used here (the brief fixes the data start) |
| Bars | 15m bars must be contiguous (t-13..t all 900 s apart); otherwise the event is skipped and counted | OURS |
| Prior-day levels | PDH / PDL = max high / min low of the previous closed UTC day (96 bars required). Used only for touch days after that day closes | OURS |
| Touch | one per UTC day: the first 15m bar of the day whose high > PDH or low < PDL. Requires close[t-12] strictly inside (PDL, PDH); if it fails, the day has no touch (counted). A bar beyond both levels is skipped (counted) | Brief: first bar, "close 12 bars earlier inside" (the 12-bar lookback is the brief's; index t-12 chosen, OURS) |
| Side | high touch (above PDH) = fade short; low touch (below PDL) = fade long | OURS |
| Speed-in | abs(close[t-1] - close[t-13]) / close[t-13] / 12 x 100, % per bar | WICKS_NOTE s5 formula (OURS) |
| Fast | speed-in >= the DEV 66.67th percentile (top tercile) of speed over ALL DEV touches (before the reclaim filter, numpy linear) | OURS. Cut-off computed on DEV touches in the count stage, written below before any return |
| Reclaim | first bar r in {t, t+1, t+2, t+3} with PDL < close[r] < PDH (k=0 allowed: the touch bar itself closes back inside) | OURS |
| Time-at-level (trade) | count of bars j in t..r with abs(close[j] - level) / level <= 0.002. Bars after r are never read | WICKS_NOTE s5 (0.2 %, OURS value) |
| Time-at-level (descriptive 2x2) | the same count over t..t+7. This uses bars after the entry; it is descriptive only | OURS |
| T05 cell | fast AND reclaim AND time-at-level(trade) <= 2 | brief |
| Entry | close[r], taker | brief |
| Stop | extreme beyond the level over t..r (max high for short, min low for long). Stop wins a same-bar tie | brief (structural, no buffer) |
| Target | 2R, R = |entry - stop| | brief |
| Time stop | close of bar r+96 (taker). Bars r+1..r+96 are scanned for stop/target | brief |
| Fees | regime A: taker 0.0005 per side on both legs (fees.py DERIBIT_TAKER, sourced) = 10 bps RT, plus 2 bps RT slippage (brief; the FORMULAS s13 file is not in this worktree) = 12 bps RT | SOURCED fees.py; slippage value from brief (OURS in amount) |
| fee_r | 0.0012 / (R / entry) | arithmetic |
| Funding | sum of fundingRate records with calc_time in (entry_ts, exit_ts]; cost for long = +rate, for short = -rate (longs pay positive funding). funding_cost_R = cost fraction / (R / entry) | standard convention, OURS (FORMULAS s13 not found) |
| Net R | gross R - fee_r - funding_cost_R. Gross: +2 target, -1 stop, time-stop (signed close minus entry) / R | arithmetic |
| Censoring | a trade whose window reaches the split end without resolving is dropped and counted (no partial fill) | OURS |
| Stats | per-trade net R; SE clustered by UTC day of the touch; DEV screen n >= 30 AND mean > 0 AND CI95 lower > 0. MDE80 = 2.80 x SE | repo practice, OURS |
| VALIDATION | one-sided p (normal, clustered SE) for mean > 0; PASS needs p <= 0.05 / 15 (conservative first Holm step at m = 15) and mean > 0 | Holm m = 15 from TRIALS.md; the step is OURS |
| Verdict | PASS = DEV screen and VALIDATION Holm pass; FAIL = DEV mean <= 0 and CI upper < MDE80; else INCONCLUSIVE | OURS, PLAN s5 |
| Exploratory 2x2 | touches with a reclaim within 3 bars, fast / slow x time(t..t+7) <= 2 / > 2. Reversal = target before stop (same entry and stop as the trade). Continuation = price reaches stop + 1R (beyond the stop, away from the level) before the target | OURS; cannot promote |

## Context
- Regime: research_kit.regime_tag (daily SMA200 side and weekly/monthly RSI band), reported as the weekly mix line. Not a gate for T05.
- Phase: none for T05 (the brief tests the fade in all phases; the regime mix is reported).
- Session: none, because the rule is daily-level and the brief sets no session gate.
- Entry: reclaim close, first bar in t..t+3 with the close back strictly inside the level.

Regime mix: see RESULT.md.

## Fast cut-off (filled in the count stage, before any return)
Status: PENDING (filled below by the count stage; no return has been computed when this line is written).
