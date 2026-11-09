# Tom swing (trendline swings 1-3): NOT_IN_DATA

Status 2026-11-09: captions NOT fetched. No extract, no rule mapping, no PRE_REG written (nothing SOURCED exists to put in them).

- Video found (yt-dlp search, public metadata): `M7ompiwv5co`, "The Easiest Way to Start Trading (Swing Trading for Beginners)", channel Tom Vorwald EN. German original: `eB677a_UQ6E` (channel Tom Vorwald).
- Caption fetch: `fetch_captions_timed.py --analyst Tom M7ompiwv5co` returned HTTP 429 (BLOCKED) on the first and only try; the guard wrote a lockout (level 1, 6 h). Not evaded; no proxy or fallback used.
- No transcript for either id exists in raw_transcripts_canonical/ on this machine.

DECISION (OURS): record NOT_IN_DATA rather than write rules from memory or from the title.

Retry: after the lockout (`fetch_captions_timed.py --analyst Tom --status`), on a machine/IP not blocked:
`python scripts/dev/fetch_captions_timed.py --analyst Tom --out MyTradingSys/research/tom_swing_2026-11-09 M7ompiwv5co`
then continue with done_when steps 2-4 (extract + verify_extract_quotes.py, map to trendline_core.py / TRENDLINE_CONTRACT.md v1, PRE_REG.md for BTC 4h and 1d with fees from MyTradingSys/backtest/fees.py).
