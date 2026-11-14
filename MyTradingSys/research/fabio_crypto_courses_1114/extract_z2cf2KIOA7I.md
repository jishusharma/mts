# Extract: Andrea Cimi, "Full MBO Orderflow Guide [Complete Beginner Course EP3]" (`z2cf2KIOA7I`)

- **Video ID:** `z2cf2KIOA7I`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, free course EP3 "Complete Orderflow Trading Course", playlist PLBVwIU37953qr7DBLMJVXqcaVrJAaQy3D)
- **Market in the video:** CME futures market-by-order (MBO) feed, ES examples; no crypto. Mostly matching-algorithm and iceberg mechanics that need order IDs.
- **Source:** `raw_transcripts_canonical/z2cf2KIOA7I_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### M1. Market makers pull liquidity around macro releases (SOURCED, filter)

Rule: around scheduled macro releases (NFP, CPI) the book thins out and price moves further, partly because market makers withdraw; treat the minutes around releases as a different regime. Computable only as a calendar filter plus range/volume regime from klines (no book). Stop and target: NOT stated; no numeric threshold or window beyond "milliseconds right before and right after" (OURS: window for BTC untested).

> "market makers usually withdraw their order from the order book in the milliseconds right before and right after a macroeconomic data release" [0:05:25]
**Source GPS: z2cf2KIOA7I | MIDDLE**

> "in the seconds before and after news you will see the book almost completely empty" [0:05:48]
**Source GPS: z2cf2KIOA7I | MIDDLE**

### M2. Absorption at a level: large executed volume, little shown in the book (SOURCED, partly computable)

Rule: an iceberg shows as hundreds of contracts executed at one price while the book shows very few, the level holds, and price later moves back. Proxy from aggTrades: large aggressive volume at one price tick with no price progress (OURS, threshold NOT stated; the "book shows few contracts" half needs depth data). Entry idea for a sell at an iceberg: sell limit at the level, stop one tick above, target gives about 1:2 to 1:4 reward to risk; this is a micro-scalp for tick-sized stops (OURS: on BTC tick size and fees change the maths).

> "we can already see that hundreds of contracts has been executed at this level" [0:07:25]
**Source GPS: z2cf2KIOA7I | MIDDLE**

> "if you place your stop loss right at the tick above and say you're going to put a take profit here this trade will be like 1 to 31 to 4 this trade will be a one to two" [0:09:52]
**Source GPS: z2cf2KIOA7I | END**

## Not computable (needs CME MBO)

| Item | Why |
|---|---|
| Native vs synthetic iceberg (same order ID reloaded vs different IDs) | needs order IDs from market-by-order feed; Binance gives none |
| FIFO and FIFO-with-lead-market-maker matching, queue position | exchange matching rules, not testable here |
| Market-by-price vs market-by-order data feed explanation | data-feed description; no rule |
| "Buy a $100 per month MBO feed only if you scalp" | cost advice, skip |
