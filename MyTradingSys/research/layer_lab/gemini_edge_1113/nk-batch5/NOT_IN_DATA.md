# NOT_IN_DATA: gemini-edge-nk-batch5-1113

**Status:** BLOCKED (caption fetcher locked out on host DESKTOP-F7IU69N)
**Checked at:** 2026-11-13T17:03:54Z (2026-11-13T22:33:54+05:30)

## Blocker
Running `python scripts/dev/fetch_captions_timed.py --analyst Tom --status` returned:

```text
BLOCKED until 2026-11-16T14:21:46+00:00 (host DESKTOP-F7IU69N, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 1 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 5
```

## Affected Video IDs
- `bw_yyi7rrC8` (Title: *Nifty Make or Break ||  @NKStockTalk  #financial #*) — not in `raw_transcripts_canonical/`
- `I4rHEfRhEWM` (Title: *How To Make Career In Stock Market 📊| Complete Roa.*) — not in `raw_transcripts_canonical/`

Per step 1 of `gemini-edge-nk-batch5-1113`:
> "Run python scripts/dev/fetch_captions_timed.py --analyst Tom --status first. If BLOCKED fetch nothing, write NOT_IN_DATA.md in the output folder with the unlock time and stop."

Caption fetching is locked until `2026-11-16T14:21:46+00:00`. Real captions cannot be fetched, and per instructions, no proxies, cookies, YouTube API, memory, or invented quotes are permitted.
