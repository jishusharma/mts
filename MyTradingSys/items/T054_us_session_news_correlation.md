# T054 - US SESSION / PRE-MARKET ALERT, US-EQUITY CORRELATION, NEWS SENTIMENT

Convention: one item, one doc. Verbatim ask at top. Updates appended, newest last.
Related: T040 tick anomalies; research/event_probability_layer_DESIGN.md (parked; liquidity-run event).

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
