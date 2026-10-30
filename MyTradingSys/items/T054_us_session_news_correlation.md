# T054 - US SESSION / PRE-MARKET ALERT, US-EQUITY CORRELATION, NEWS SENTIMENT

Convention: one item, one doc. Verbatim ask at top. Updates appended, newest last.
Related: T040 tick anomalies; research/_archive/loose_2026-10/event_probability_layer_DESIGN.md (parked; liquidity-run event).

## VERBATIM ASK (operator, 2026-09-28)
in tick based system our goal is not to store data but rather identify the known list of anomalies when they occur - and thus we poll for anomalies of diff thresholds. Then we need to research how we can use these with any other indicator or idea like liquidity runs around the US session start.
Then we need an alert of the US pre market(Good and bad sentiments change BTC behavior as well and thus we need to also research the correlations (US Stock Markets & BTC) and their probabilities of occurrence by actually testing the historical data + regular news that affect BTC - Remember there are things like "buy the rumor sell the news" so we need to be careful on how we can gauge this! A paid subscription of news streams is also an option in the future! But we can get started by polling to the best available free sources.

## STATE
2026-09-28 OPEN, on fast-track (operator). Nothing built.
Plan: (1) T040 anomaly tiers first; (2) study anomalies + liquidity runs around the US cash open (13:30 UTC, DST-aware)
and pre-market (08:00-13:30 UTC); (3) US-equity link: NQ/ES (free daily/intraday sources) vs BTC - rolling correlation,
conditional probabilities by regime, OOS; (4) news: free sources (RSS/calendar: CPI/FOMC/NFP dates, crypto news RSS),
event-study around scheduled releases, "buy the rumor, sell the news" = pre- vs post-event drift; (5) US pre-market alert
(context only, never gates Tom).

## VERBATIM ASK (operator, 2026-10-03, session-open sweeps)
Is it true that when BTC makes a move in opposite direction before breaking out of the current range thereby garbing liquidity and changing to actual direction.
	This above context may apply or hold better when BTC is trading in certain sessions like US or Eur when the moves are likely to be valid.
	There is another 'phenomenon' that i have noticed - There is a certain change when US session opens. The first 10-15 mins are crucial.
	They say for US stock market exchanges that - "the first 10 mins or perhaps 15 decides the day!". For BTC this analogy could also be seen at the US session start!
	These moves are specially visible during the start of the US session. We need intel on this phenomenon because I need to trade this volatility and possible in both directions.
	So a research is needed. Perhaps we can engage Cloud AI services for this?

	Now - taking this further - I have noticed that after the new daily candle starts(UTC), BTC transitions to Asian and European sessions and there are also some moves available there.
		And these moves are somehow related to the opening of the US session. BTC might sweep highs and come back down before US session start - sweep the lows and then climb up and continue green!
		Sometimes it is the opposite! I have a hunch that MTS's Tom and Fabio books could be applied to this and tested on historical data to see what/which logic/ideas hold and their success rates!
		The task requires fresh analytical and reasoning lenses and active || researches to keep it aligned to the goals!

## STATE (cont.)
2026-10-04 RESEARCH DONE (MTS-2026-10-03-2051Z-APP-ANA-btc-session-sweeps): research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md
(+ BTC_SESSION_EXTERNAL_2026-10-04.md; study research/session_sweeps/session_open_study.py, 1178 NY days 2022-01..2026-09, DST-aware).
 Step 2 (US-open window) S1-descriptive DONE: BTC volume/|return| peak = the NY cash open bucket (x2.5-2.8 vol, x1.9-2.0 |ret|),
 moving 13:30 -> 14:30 UTC with US DST (H). First 10/15/30 min do NOT predict rest-of-session direction (49-50%, placebo
 range 45-54%, sign flips by year). Pre-US sweeps (London vs Asia range; prev-day H/L) carry no US-session direction.
 Tom opening-range rule not supported on BTC (trend days 29/31/33% small/mid/large IB). 12:30 UTC (08:30 ET) secondary
 peak in summer = macro-release hint for step 4 (news), untested. Cloud AI: not needed now; if used, CLD per SURFACE_POLICY s1,
 APP recommended (s1b). Next: N1 OOS replication on 2019-09..2021-12; N3 context-only "US open in N min" alert line.
 Defect filed: B102 (fixed-UTC session anchors in offline models).

## VERBATIM ASK (operator, 2026-10-30, news module)
I think what is missing from the dashboard is also news. ... yesterday we saw the market sell-off, and there was some Binance hack of $6 billion. So we never could catch it, not early, not late. ... do a proper research on this, especially for Bitcoin. ... What are the things that we can scan every day? Keep scanning, keep polling ... What are the feeds for this? What are the plugins for this ... how MTS can also be prepared for that.

## STATE (cont.)
2026-10-30 step 4 (news) RESEARCH DONE: research/news_feeds_2026-10-30/REPORT.md. Tree News REST (free, CORS *,
timestamped, importance score) had the hack at 20:39:00 UTC, 15 min after the 20:24 on-chain drain and before the
20:40-20:45 main leg (Deribit 5m); CoinDesk RSS 21:12 = after the low. Normal day 5-9 items at importance >= 7, hack day 42.
Cards: live-aid-news-panel (N1/N2/N6), live-aid-macro-calendar (N3), news-hot-wallet-watch (N4), news-event-study (N5).
