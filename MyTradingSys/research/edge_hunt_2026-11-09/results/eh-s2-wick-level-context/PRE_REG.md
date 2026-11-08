# PRE_REG eh-s2-wick-level-context (trials T09 long, T10 short)

Written and committed BEFORE any return is computed. Card edge-hunt-plan-opus-1109, wave 2, worker model claude-sonnet-5-5.
Trials: **T09** (long, wick at an HTF support) and **T10** (the mirror, short at an HTF resistance). Both are confirmatory (Holm m = 15 over T01-T15). Everything else in this file marked "exploratory" cannot promote.

Hypothesis: the operator's "buy and sell into wicks with the whole context" (d-wicks-research-plan-first-1107; WICKS_NOTE s2/s6): a wick pays when it sweeps an HTF level on its first touch, on high sweep volume, with a fast reclaim and no falling knife, entered by a maker limit at the level, with the traders' payoff (target the next HTF level, break-even at +1R).

## Context
- Regime: none as a gate (the rule must fire in every regime; a gate would be a second trial). Report-only tag per trade and per DEV week: research_kit.regime_tag (daily close vs SMA200 side AND weekly/monthly RSI14 band; spot 1d history from 2017-08 is used for the RSI/SMA warm-up). RESULT carries the `Regime mix:` line and net R by regime (exploratory).
- Phase: first-touch wick sweep and reclaim (tf_break class W1 = wick sweep, research_kit.PHASE_OF_CLASS "range"), not a break-and-hold and not a free retest; the first touch of the level is the phase gate.
- Session: none as a gate (levels are daily/weekly/monthly); exploratory table by UTC 4h block (Asia 68 % in the 5-week census, n = 19).
- Entry: retest of the swept level: maker limit AT the level, placed at the reclaim close, live 4 bars, fills only if a later bar trades strictly through it (the research_kit.retest_entry idea with n = 4, strict fill).

## Data and splits
- BTCUSDT USD-M futures 15m klines and fundingRate from data.binance.vision, cached OUTSIDE the repo (F:/MTS/Dumps/backtest/eh_s2_wick). The monthly futures archive starts 2020-01 (the 2019-09..2019-12 monthly files 404; daily files exist only for 2019-12-31), so DEV effectively starts 2019-12-31 / 2020-01. Funding: the archive's rates where they exist, none before 2020-01.
- 1d, weekly (ISO, Monday 00:00 UTC) and monthly levels are built by resampling closed 15m bars in UTC. A level is usable only from the first bar after its period closed. A period counts only if its first bar is at the period start and (for days) it holds all 96 bars.
- DEV = data start .. 2024-06-30. VALIDATION = 2024-07-01 .. 2025-06-30, read ONCE and only per trial that passes the DEV screen. HOLDOUT (2025-07+) is never loaded. The loader refuses any bar at/after the split end and refuses the HOLDOUT split (tested). The brief's DEV start (data start) differs from splits.py DEV_START (2022-01-01); the brief wins (DECISION OURS, logged).
- Regime tag warm-up reads only spot 1d bars before 2024-07-01.

## Rules table (frozen)
| Item | T09 long (T10 = mirror at highs) | Label |
|---|---|---|
| HTF level | prior ISO-week low, prior calendar-month low, or an unbroken daily pivot low (5 days each side, confirmed only after the right side closes) | SOURCED in kind (Tom weekly/daily map, TOM-041; WICKS_NOTE s6 "daily/weekly low"); pivot 5 OURS |
| First touch | no 15m bar traded below the level since it formed | operator's "first try" (decision record); OURS |
| Sweep | 15m low < level and a close back above the level within 3 bars | wick_census V-sweep, OURS |
| Effort | the sweep bar's volume >= 3.0 x the median of the prior 96 bars (Friday case: 12x) | WICKS_NOTE s2 (fact); 3.0 OURS |
| Knife veto | fall >= 2 % from the highest high of the 12 bars before the sweep with the largest counter-move < 25 % of the fall -> no trade | d-wicks-research-plan-first-1107 defaults (OURS) |
| Entry | maker limit buy AT the level, placed at the reclaim close, live 4 bars; fills only if a later bar's low trades strictly below the level | Tom's limit order at the zone (TOM-005); fill rule and 4 bars OURS |
| Stop | the sweep extreme (lowest low of the sweep bars), no buffer | TOM-072 "below the last liquidity" |
| Target | the nearest HTF level above (prior-day high, prior-week high, unbroken daily pivot high) at least 2.5R away; if the nearest one is under 2.5R, skip (counted) | TOM-018 "next high-volume price" in kind; 2.5R OURS (POSTMORTEM s3 plan) |
| Management | stop to entry once price reaches +1R; time stop 96 bars | Fabio fast break-even SOURCED in kind (fZlNGWvd2Ko:43-61); 96 OURS |
| Fees | regime B (maker entry and target, taker stop/BE/timeout) | PLAN s5 |
| Exploratory | regime A version; by UTC 4h block; by level type; no-volume-gate version; fill rate; by regime tag | - |

## DECISION (OURS) fills for what the brief leaves open (chosen once, never tuned on the outcome)
1. "within 3 bars": the sweep bar s (first bar with low below the level) is bar 1; the reclaim is the first close above the level among bars s, s+1, s+2. The sweep bars are s..r (r = reclaim bar); the sweep extreme is the lowest low over s..r. The order is placed at the close of r.
2. First touch: every level whose price is above bar s's low is touched at s and then dead, whether or not it reclaimed. Levels have no expiry except week/month levels, which live only during the week/month after their period (the "prior" week/month); pivots live until touched.
3. Several levels touched at the same sweep bar: one trade, for the level reclaimed EARLIEST (the only choice that is causal at the order time), ties by priority month > week > pivot, then the higher level (T10: lower). Equal prices count once.
4. Pivot: strict (the pivot low is below the lows of the 5 days before and the 5 days after; a tie is no pivot). Confirmed at the start of day d+6.
5. Effort uses the volume of bar s (the first bar below the level) over the median volume of bars s-96..s-1. Fewer than 96 prior bars -> no event.
6. Knife (amended twice before any return was computed, each amendment its own commit): approach = bars s-12..s-1, H = their highest high (first one) at bar k, L = the lowest low over the bars AFTER k (k+1..s-1; no bar after k means no knife). fall = (H - L) / H; counter-move = the largest (high of a later bar - low of an earlier bar) over the bars after k, floor 0. Veto when fall >= 2 % and counter-move < 25 % of (H - L). The sweep bars are NOT part of the fall (measured to the sweep extreme, every wick deeper than 2 % would veto itself). Mirror for T10 with highs and lows swapped.
7. Target candidates are read at the reclaim close with state as of that close; "nearest above the entry" is literal (a candidate between entry and the current price counts). No candidate, or nearest < 2.5R: skipped and counted, no order. The target is a maker limit: it fills only when a bar's high trades strictly above it.
8. Fill price = the level even when the bar opens through it. On the fill bar only the stop is checked (low <= stop; stop wins the tie), never +1R or the target (the path inside the bar is unknown). After the fill: per bar the stop (or the entry price once at +1R) is checked first (stop wins ties), then the target, then the +1R trigger (high >= entry + 1R), which arms break-even from the NEXT bar.
9. Time stop: the close of bar fill+96, taker. A trade still open at the end of the loaded data is dropped and counted (unresolved).
10. One position or pending order at a time per side; an event arriving while busy is skipped and counted.
11. Costs: regime B = fees.FEES_DERIBIT (maker entry/target 0; stop, BE and timeout taker 0.0005) + 1 bp slippage on taker legs = 6 bps on those exits, 0 on target exits. Regime A (exploratory) = taker both legs 5 + 5 bps + 2 bps round-trip slippage = 12 bps on every exit. fee_r = cost bps / stop distance bps; funding by bt_data.funding_cost_pct (side +1 long pays a positive rate), entry = fill bar open, exit = exit bar close, divided by the stop distance as a fraction. net R = gross R - fee_r - funding R.
12. SE: clustered by UTC day of the fill (research_kit.cluster_mean_se). CI = mean +- 1.96 SE. MDE (80 % power) = 2.8 SE. Hit rate = share of trades with net R > 0.

## Trial ids and verdict rule
T09 and T10 separately. DEV screen: n >= 30 AND mean net R > 0 AND CI lower bound > 0. Only then one VALIDATION read per trial, one-sided p, Holm at m = 15. PASS = both; FAIL = DEV mean net R <= 0 with the CI upper bound below the MDE; INCONCLUSIVE otherwise. A PASS files a testnet-forward raw card; never a longer backtest.

## Kill and power note
Expected n is small (a first-touch HTF sweep with 3x volume and a 2.5R target 0 .. a few dozen a year). A count pass (orders, fills, funnel by year and side, regime mix, no returns) runs before DEV. If DEV n < 30 the verdict is INCONCLUSIVE (underpowered), not "no edge". No parameter is changed after the count pass.
