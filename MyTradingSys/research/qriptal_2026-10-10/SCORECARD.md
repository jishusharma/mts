# Qriptal scorecard (card qriptal-score-binance, B162 step 1)

Result: **scored n = 0.** No call is both ELIGIBLE and inside the DEV window, so there is no win rate and no net R to put against his 67.1% / 3.99% / 0.63%. Power at n = 0 is zero. Of 70 candidate statements, 2 are ELIGIBLE and both sit in the holdout window, which the card does not allow reading.

## Count per split (the data rule)

Card: dev data only, scope-out holdout reads. BACKTEST_PROTOCOL section 2: DEV 2025-09-01..2026-06-25, HOLDOUT 2026-06-26..2026-09-26. A call is DEV only if its call time + 8 days (24 h fill window + 7 days open, RULES.md) ends by 2026-06-26T00:00Z (DECISION OURS, so no scored candle can be a holdout candle). The earliest Qriptal statement in the staged transcripts is dated {cn['earliest_call'][:10]}.

| Split | Ledger rows | ELIGIBLE | Scored |
|---|---|---|---|
| DEV | 11 | 0 | 0 |
| HOLDOUT | 59 | 2 | 0 |
| Total | 70 | 2 | 0 |

ELIGIBLE rows left unscored because they fall in the holdout window (not read):

| call_id | published (UTC) | direction | entry | stop | targets |
|---|---|---|---|---|---|
| QRP-ZPFK3ZsLwoo-05 | 2026-09-21T07:11:25Z | short | 79,500 (loss of the level) | 82,800 (his hard invalidation of the whole idea) | 73,000; 72,000 |
| QRP-ZPFK3ZsLwoo-06 | 2026-09-21T07:11:25Z | short | 82,200 (sweep of 82.2, not of 82.8) | 82,800 (his hard invalidation) | 73,000; 72,000 |

These 2 rows come from 1 video(s); variants of one plan are one observation, not several. The staged extract's own outcome check (stopped out about 14 h after the stream) is not reused: it reads holdout candles.

## Score against his claim

| | His claim (qriptal.com, 86 setups) | Scored here (DEV, 0.05% per side) |
|---|---|---|
| Setups / calls | 86 (49 W / 13 BE / 24 L) | n = 0 |
| Win rate | 67.1% (= 49 / (49 + 24), BE left out; with BE counted 57.0%) | n/a (wins / (wins + losses)) |
| Average winner | 3.99% | n/a |
| Average loser | 0.63% | n/a |
| Net R per call | about +3.3R before fees if 1R = his average loser (expectancy 2.10% per setup, BE as 0) | n/a (second column: n/a) |

His percentages are as he posts them; whether they are price moves or account percent is not stated. Fees at 0.05% per side are 0.10% a round trip, about 0.16R if 1R is his 0.63% average loser.

## Power

Test: exact binomial, H0 true win rate = 67.1% (his claim), H1 = 50%, one-sided alpha 0.05. With n = 0 the power is 0%, because no sample means no evidence either way.

| Scored calls n | Reject his claim if wins are | Power vs a coin flip |
|---|---|---|
| 0 | cannot reject | 0.0% |
| 2 | cannot reject | 0.0% |
| 3 | 0 or fewer | 12.5% |
| 10 | 3 or fewer | 17.2% |
| 30 | 15 or fewer | 57.2% |
| 49 | 26 or fewer | 71.6% |
| 56 | 31 or fewer | 82.5% |
| 86 | 49 or fewer | 92.0% |

First n with 80% power: **56** scored calls. To separate his claimed rate from a still-profitable 57% (his own tally with BE counted) takes 146 calls. Holdout rows that are variants of one plan count once, so scoring them would give n = 1 and power 0%.

## Method (frozen before any score; every number OURS, none from a trader quote)

- Prices only from the ledger's ELIGIBLE rows: entry, stop and at least one target spoken with a number. A stop that was never priced is not invented; the 7 PLAN rows with an entry and a target but no stop stay unscored (NO-SOURCE, card scope-out).
- Call time = YouTube publish time (CALL_LEDGER.csv `published_utc`). The first candle used is the first one that opens at or after it.
- Entry fills at the posted price in the first 1m candle whose range contains it, within 24 h; else NOT_FILLED (counted, not scored). In the fill candle only the stop is checked (the order of entry and target inside one candle is unknown).
- Stop and target inside the same 1m candle = stop. Trade still open 7 days after the fill = closed at the close of the last candle before day 7. A series that ends before the trade resolves is NO_DATA (not scored).
- Primary column exits everything at T1; second column exits everything at the last target. Fee 0.05% of price per side: net = side x (exit - entry) - 0.0005 x (entry + exit); R = net / |entry - stop|; return = net / entry.
- Win = net R above 0, loss = net R below 0 (a stop-out is always a loss after fees); win rate = wins / (wins + losses), the same convention as his 67.1%.

## What would give a real score

1. His 86-setup list on qriptal.com / Discord with dates, entries, stops and targets (not staged; the operator paste only gives the totals).
2. His Sunday live streams (the weekly plans that carry priced stops; one is staged and holds the only 2 eligible calls) and the uploads still without transcripts, fetched by the daily retry (ids in LEDGER_NOTES.md).
3. A coordinator decision to read the holdout. Not taken here: it would add one plan at most, power stays about 0.

## Reproduce

```
python MyTradingSys/research/qriptal_2026-10-10/test_score_calls.py
python MyTradingSys/research/qriptal_2026-10-10/score_calls.py run      # rewrites this file
python MyTradingSys/research/qriptal_2026-10-10/score_calls.py check    # exit 1 if it differs
```
