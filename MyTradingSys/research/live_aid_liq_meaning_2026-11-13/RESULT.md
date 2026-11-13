# RESULT: after a 1m / 2m forced-selling or forced-buying burst, does price continue or turn? (2026-11-13)

Question (operator, Live Aid card "Forced selling and buying"): when forced selling or buying shows on the 1m or 2m window, is that enough for a move to change direction, or does it continue? How big is a signal?

## Verdict: NOT MEASURED. No usable liquidation history exists. No number is given.

## What was searched (all read, none usable)
| place | what is there | why it cannot answer |
|---|---|---|
| runtime_data/live_aid/xliq_events.jsonl (xliq_collector.py output) | file does not exist in this tree or the main checkout | collector has never stored history here |
| runtime_data/liq_events/*.jsonl, F:/MTS/liq_events (liq_mirror.py input) | do not exist | no recorder output |
| research/liquidation_layer_2026-10-28 | README + BANDS_LEDGER.csv of heatmap bands (modelled, not executed liquidations) | no executed events; its own test needs forward data, n >= 56 |
| research/liq_mirror_2026-11 + layer_lab/reports/2026-11-06_liq-mirror.md | code and spec tests only, no results | no data behind it |
| tools/live_aid/fixture_liq_cluster.json, fixture_bybit_flush_1030.json | 10-event and one-flush samples | far below any n |
| research/c26_roadmap_2026-11-01/phase1_liq_look.py | a modelled open-interest band proxy, not forced flow | different question |

## What is built so it runs the moment data exists
- `liq_meaning.py` (this folder): reads xliq_events.jsonl, sums venues per aligned 1m and 2m bin by side, drops same-side bursts within 15 min of a counted one, buckets by USD, fetches Binance spot 1m closes (public), and rewrites `tools/live_aid/liq_rates.js`. Below 24 h of history it writes rows [] with the reason. Logic was checked on a synthetic series only (not a result).
- Thresholds: bucket edges 250k / 1M / 5M USD (OURS), 15 min dedup (OURS), horizons 5 / 15 / 60 min (OURS), 24 h minimum span (OURS), n < 30 flagged as anecdote (OURS, matches the n >= 30 ask).
- Reading of "continued": longs forced out then price lower at the horizon; shorts forced out then higher. Reference price = close of the last minute inside the bin.

## What must be recorded (card live-aid-liq-history-log-1113)
Keep xliq_collector.py running with a 7-day prune removed or the file copied to a durable path (it prunes at 8 days). Each line {v, t, s, usd, px} is enough. Days needed: n >= 30 first-in-15-min bursts per window, side and bucket. Event rates are unknown until recording starts, so the day count cannot be stated yet. Expect the 5M+ bucket to be the bottleneck: at about one such burst per side per day it would take about 30 days; at one per week, about 30 weeks, and that bucket should then be merged with 1M-5M. Re-run `python MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py` after each week; the table prints with n beside every rate.

## How to read a 1m / 2m burst today (descriptive, no data behind it yet)
1. There is no measured count of past bursts that continued or reversed, so the card carries no hit rate.
2. A burst is a count of forced orders in one or two minutes, not a record of what price did next.
3. Heatmap bands (liquidation_layer README) are modelled estimates, not executed liquidations; do not mix them with burst counts.
4. Until n >= 30 per bucket, any "past X of Y continued" would be an anecdote.
5. liq_rates.js already holds the slot: when rows appear, LIQ_RATES.read(win, side, usd) returns the matching row.

## Limits
Spot closes stand in for perp price; venues are summed (Bybit, Binance, OKX); the 1m/2m bins are clock-aligned, so a burst split across a boundary is halved; no placebo (random-time baseline) is computed yet and should be added before any rate is called a signal.
