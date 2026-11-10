# Tom swing (trendline swings 1-3): NOT_IN_DATA

Status 2026-11-09: captions NOT fetched. No extract, no rule mapping, no PRE_REG written (nothing SOURCED exists to put in them).

- Video found (yt-dlp search, public metadata): `M7ompiwv5co`, "The Easiest Way to Start Trading (Swing Trading for Beginners)", channel Tom Vorwald EN. German original: `eB677a_UQ6E` (channel Tom Vorwald).
- Caption fetch: `fetch_captions_timed.py --analyst Tom M7ompiwv5co` returned HTTP 429 (BLOCKED) on the first and only try; the guard wrote a lockout (level 1, 6 h). Not evaded; no proxy or fallback used.
- No transcript for either id exists in raw_transcripts_canonical/ on this machine.

DECISION (OURS): record NOT_IN_DATA rather than write rules from memory or from the title.

Retry: after the lockout (`fetch_captions_timed.py --analyst Tom --status`), on a machine/IP not blocked:
`python scripts/dev/fetch_captions_timed.py --analyst Tom --out MyTradingSys/research/tom_swing_2026-11-09 M7ompiwv5co`
then continue with done_when steps 2-4 (extract + verify_extract_quotes.py, map to trendline_core.py / TRENDLINE_CONTRACT.md v1, PRE_REG.md for BTC 4h and 1d with fees from MyTradingSys/backtest/fees.py).

## Retry 2026-11-10 (tom-swing-retry-1110): still blocked, no request made

- `fetch_captions_timed.py --analyst Tom --status`: BLOCKED until 2026-11-10T13:54:09+00:00 (this host, lockout level 2 of 3: 6/24/72 h, OURS). The wrapper refused locally (`YT_BLOCKED`), so no request left the machine. C's "lockout level reset" is per its own host/IP; this host's guard state is separate.
- Not evaded: no proxy, no state edit, no other fetch path.
- Next retry: at or after 2026-11-10T13:54:09Z on this host, or now on a machine whose `--status` shows clear. Same command as above; then done_when steps 2-4.

DECISION (OURS): stop at the guard, record the new retry time, ship NOT_IN_DATA only.

## Retry 2026-11-10 (tom-swing-A-20261110): HTTP 429 again, stopped

- `--status` said NOT BLOCKED (level 2, budget 0/40). One request for `M7ompiwv5co` via the guard wrapper returned HTTP 429 (BLOCKED). Stopped at once: no second request, no proxy, VPN or other path.
- The guard lockout is now re-armed (see `--status`; level should rise to 3 = 72 h, OURS). No extract, mapping or PRE_REG written (nothing SOURCED).
- Next retry: only after `--status` clears, preferably from a machine/IP that is not YouTube-throttled; same command as above.

DECISION (OURS): honour the 429, record it, ship NOT_IN_DATA only.
