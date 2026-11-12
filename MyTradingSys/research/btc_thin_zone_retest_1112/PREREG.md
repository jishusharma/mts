# PREREG: BTC thin-zone pass-through (T1) and accepted-breakdown retest (T2), card btc-thin-zone-and-breakdown-retest-prereg-1112, written 2026-11-12 before any result

Operator decisions that bind (2026-11-12): BTC is read on its own terms; only the order-flow IDEA is taken from Tom's videos; index-futures session clocks are not carried (BTC's own UTC day and rolling windows, labelled OURS); analyst statements are context, never signals.
Sources of the two ideas: research/orderflow_extracts_1112/extract_BB3c8visnkI.md (idea 3, thin zone) and extract_e83njGZFrPw.md (idea 1, accepted breakdown retest). Both extracts say every number is OURS (the video gives none), so every parameter below is OURS; the IDEA is SOURCED.
Nothing below was run. No trade was simulated, no return computed, no VALIDATION / GAP / RESERVE / HOLDOUT file opened. Parameters are fixed: one set per idea, no sweep, no change after the result. Labels: SOURCED (file or quote) or OURS.

## Context
Regime: none as a gate, because each idea is a path rule (move through thin volume; retest of a broken range) meant for any regime; RESULT reports `Regime mix:` and long/short rows (regime label SOURCED from btc_orderflow_map_1112/CLOCKS.md: trailing 90 daily-close return > +20 % bull, < -20 % bear, else range).
Phase: none as a gate (cycle phase not read, not tuned on).
Session: none as a gate, because index-futures session clocks are not carried to BTC; UTC hour only enters the placebo matching (OURS).
Entry: T1 next 1m open after the 5m trigger bar closes; T2 next 1m open after the 1h retest bar closes; taker fee both sides.
Regime mix (DEV window, SOURCED btc_orderflow_map_1112/CLOCKS.md): bull 35%, bear 16%, range 42%, n/a 7% of 851 DEV days.

## Not repeated
| Earlier work | Why this differs |
|---|---|
| extract_BB3c8visnkI idea 3: grep of research finds low-volume-node text only in design maps | no trial exists |
| extract_e83njGZFrPw idea 1: T04 sweep-reclaim, R25 fractal fades, btc_of_level_auction_1112 B1 | those fade or absorb at a level; T2 trades the RETEST after an ACCEPTED break |
| value_area_acceptance_2026-11-05, census ACCEPTED | descriptive, no fee-net frozen test, no profile thin zones |
verdicts.py check "thin zone low volume node pass through breakdown retest": no prior row matches (need 6 of 9 words). Not a twin of forced-selloff-long-pooled-10-coins-1111 (different rule, one coin).

## Data and splits
BTCUSDT 1m klines, Binance perp, F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv (DATA_MAP.md; bars counted, not files). Profile warm-up reads 2022-01 only. Files after 2024-05 are never opened.
| Split | Window (UTC) | Use |
|---|---|---|
| warm-up | 2022-01-01 .. 2022-01-31 | trailing windows only; no trades |
| DEV | 2022-02-01 .. 2024-05-31 | the only split read |
| DEV half A / half B | 2022-02-01 .. 2023-03-31 / 2023-04-01 .. 2024-05-31 | 14 months each (OURS), for the "both halves positive" bar |
| VALIDATION and later | 2024-07-01 .. | untouched; opened only by a later card for a PASS |
A trade whose entry or whose exit window contains a missing 1m bar is dropped (counted in RESULT).

## T1 thin-zone pass-through (5m, long and short)
Profile (OURS): for UTC day D, the 1m bars of days D-7 .. D-1 (7 full UTC days; refreshed at 00:00Z, so point-in-time). Each 1m bar's volume goes to the bucket of its typical price (high+low+close)/3. Buckets are a fixed log grid of 0.05 % width: bucket k = floor(ln(price) / ln(1.0005)), edges 1.0005^k and 1.0005^(k+1). POC = bucket with the most volume. A bucket is THIN if its volume < 25 % of the POC volume (empty = thin) and THICK-NODE if its volume >= 75 % of the POC volume. Idea source: "when price enters a node with volume under 25 % of the POC bucket, trade in the entry direction, target the next bucket above 75 % of the POC" (extract idea 3, numbers OURS).
Trigger: UTC-aligned 5m bar closes in bucket k that is THIN while the previous 5m close was in a bucket that is not THIN. Direction = sign(k - previous bucket): up = long, down = short.
Entry: next 1m open after the trigger bar. Target: long = lower edge of the nearest bucket j > k that is THICK-NODE, searched up to k+100 (5 %); short = upper edge of the nearest THICK-NODE bucket j < k, searched down to k-100. No node found = trigger dropped. Stop (one bucket back, OURS): long = lower edge of bucket k-1; short = upper edge of bucket k+1. If the entry open is not strictly between stop and target, drop. Time exit: close of the 120th 1m bar from entry (24 5m bars).
One position at a time: a trigger while a T1 trade is open is skipped.

## T2 accepted-breakdown retest (1h, long and short)
Short (long is the mirror: high for low, above for below, spike close above the range high, stop below, target the highest high):
1. Range = the 24 UTC-aligned 1h bars before the event bar; width = (range high - range low) / range low must be < 2.5 %.
2. Event bar: 1h close < range low, and its volume >= 2 x the median volume of those 24 bars.
3. Acceptance: the next two 1h closes are also < range low.
4. Retest (OURS reading of "a 1h high touches the range low from below within 24 bars"): from the bar after the 2nd acceptance bar, within the next 24 1h bars, the first bar with high >= range low. If that bar closes below the range low: trigger. If it closes at or above the range low, the setup is cancelled (reclaimed). No touch in 24 bars = no trade.
Entry: next 1m open after the trigger bar's hour closes. Stop = 0.2 % above the highest 1h high from the event bar through the trigger bar (long: 0.2 % below the lowest low). Target = lowest 1h low over the same bars (long: highest high). If the entry open is not strictly between target and stop, drop. Time exit: close of the 2880th 1m bar from entry (48 1h bars).
One position at a time: a trigger while a T2 trade is open is skipped.

## Fills, fee, outcome (both ideas)
Walk the 1m bars from the entry bar. Per bar, stop is tested before target (conservative, OURS). Long: if open <= stop, exit at the open; else if low <= stop, exit at stop; else if high >= target, exit at target. Short mirrored. Gap through a target fills at the target (not better, OURS). Gross bp = side x (exit / entry - 1) x 10,000; net = gross - 10 bp (SOURCED brief: fee 10 bp round trip). No sizing, no leverage; one unit per trade.

## Placebo (direction-matched)
Per idea: 1,000 draws (seed 1112). Each draw gives every real trade a random entry: a random DEV bar of the same bar size (5m or 1h) with the same UTC hour as the real trade, long or short as the real trade (so the long/short count matches), carrying the real trade's own stop %, target % (against the placebo entry open) and time exit. The placebo trade mean net per draw is collected; report its mean and 1st / 99th percentile. Placebo trades may overlap (OURS). A real mean inside the band is "not separable from random timing with the same geometry".

## Statistics reported per idea
n; win rate (net > 0); mean and median net bp; t = mean / (sd / sqrt(n)); max drawdown (peak-to-trough of cumulative net bp in entry order, labelled bp); mean and n by DEV half; per-year rows and long vs short rows (trade_sanity.year_side_lines); the last 5 trades checked against the 1m candles (trade_sanity.log_sanity, run before any metric); placebo row; regime mix of entries; dropped counts by reason.

## Pass bar (fixed now)
| Verdict | Rule (per idea, both sides pooled) |
|---|---|
| PASS | n >= 30 AND fee-net mean > 0 AND t >= 2 AND mean net > 0 in both DEV halves |
| INCONCLUSIVE | n < 30 (n too small; no mark) |
| FAIL | anything else; positive gross with negative net is written "gross only" |
A PASS is a DEV result only: not an edge claim; it earns one VALIDATION read by a later card. The placebo is reported beside the verdict; the verdict text states whether the real mean is outside the placebo 1-99 % band.

## Trial count
The family already holds about 100 counted studies (edge_views_2026-11-11/TESTED_MAP.md: 100; plus the order-flow map and level-auction cells since). This card adds 2 marked cells (T1, T2; long/short rows are descriptive, not extra marks), so the ledger is about 102 tries. At about 102 tries a t >= 2 bar lets luck through about once in twenty per cell, which is why PASS only opens one VALIDATION read and never an edge claim.

## Checkers
prereg_context_lint.py on this file (output in the commit message); verdicts.py check: no prior row; row appended after RESULT.
