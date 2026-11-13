# NOT_IN_DATA: gemini-edge-nk-batch3-1113

**Status:** BLOCKED (caption fetcher locked out on host DESKTOP-F7IU69N)
**Checked at:** 2026-11-13T17:23:04Z (2026-11-13T22:53:04+05:30)

## Blocker
Running `python scripts/dev/fetch_captions_timed.py --analyst Tom --status` returned:

```text
BLOCKED until 2026-11-16T14:21:46+00:00 (host DESKTOP-F7IU69N, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 1 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 5
```

## Affected Video IDs
- `6Er-0OFRSEg` (Title: *Trader vs Investor Psychology 🧠 | NIFTY Market View | Trader, Investor या Accidental Investor?*) — not in `raw_transcripts_canonical/`
- `qUygnfxCUQU` (Title: *Rejection Candle 🔥 | Price Action Trap | Intraday & Swing Trading Strategy*) — not in `raw_transcripts_canonical/`
- `h9Ki-YvpS1k` (Title: *Expiry Day Hedge Strategy Explained | Nifty Hedge 23 || Expiry Day Master Plan || #stockmarket*) — not in `raw_transcripts_canonical/`
- `dm7x3ZY9K9M` (Title: *📉 Stop-Loss कैसे लगाएँ? || Beginners Guide to Safe #trading || #profit बचाने और #loss रोकने का तरीका*) — not in `raw_transcripts_canonical/`
- `cX2GZ7B5Gc8` (Title: *Intraday Trading में Options कैसे Use करें  | Chart Analysis for #beginners | #chart  के साथ समझें |*) — not in `raw_transcripts_canonical/`

Per step 1 of `gemini-edge-nk-batch3-1113`:
> "Run python scripts/dev/fetch_captions_timed.py --analyst Tom --status first. If BLOCKED fetch nothing, write NOT_IN_DATA.md in the output folder with the unlock time and stop."

Caption fetching is locked until `2026-11-16T14:21:46+00:00`. Real captions cannot be fetched, and per instructions, no proxies, cookies, YouTube API, memory, or invented quotes are permitted.
