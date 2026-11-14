# Extract: Andrea Cimi, "Complete Guide on Futures Contracts (Orderflow Full Course Beginner to Advanced EP.1)" (`Vinyl5fKDW8`)

- **Video ID:** `Vinyl5fKDW8`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, free course EP1 "Complete Orderflow Trading Course", playlist PLBVwIU37953qr7DBLMJVXqcaVrJAaQy3D)
- **Market in the video:** CME futures vs CFD explainer (ES, 6E, GC); no crypto. Mostly contract mechanics and marketing; almost no testable rule.
- **Source:** `raw_transcripts_canonical/Vinyl5fKDW8_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### F1. Volume versus aggressor split (SOURCED, definition only)

Rule: volume is the total transaction between supply and demand; order flow adds who was the aggressor (buy at the ask versus sell at the bid). On Binance aggTrades this is computable from the isBuyerMaker flag. No trigger, stop or target: NOT stated. Needs a real centralized-exchange volume feed, which Binance trades are (OURS: note that Binance perp volume is one venue, not the whole market).

> "when we're talking about volume usually we refer to the total transaction between supply and demand usually with order flow we can be more specific about who is more aggressive" [0:03:57]
**Source GPS: Vinyl5fKDW8 | BEGIN**

## Not testable (no rule)

| Item | Why |
|---|---|
| Futures vs CFD, expiry, rollover, tick value, no hedging in one contract, OCO brackets | contract mechanics, not computable from Binance aggTrades/klines; no trading rule |
| Order blocks, fair value gaps, stop runs "seen" in order flow | claimed but no definition or threshold given in this video |
| Marketing (bow and arrow, sniper analogies, platform, prop firms) | skip |
