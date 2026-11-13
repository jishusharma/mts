# NOT_IN_DATA: gemini-edge-nk-batch1-1113

**Status:** BLOCKED (caption fetcher locked out on host DESKTOP-F7IU69N)
**Checked at:** 2026-11-13T17:30:32Z (2026-11-13T23:00:32+05:30)

## Blocker
Running `python scripts/dev/fetch_captions_timed.py --analyst Tom --status` returned:

```text
BLOCKED until 2026-11-16T14:21:46+00:00 (host DESKTOP-F7IU69N, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 1 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 5
```

## Affected Video IDs
- `omZXqyrWcbI` (Title: *Low Capital से Cash Intraday कैसे करें? | Sequence*) — not in `raw_transcripts_canonical/`
- `MeawsYY-v1E` (Title: *🚀 Pair Trade क्या है? | Options Trading में Pair T*) — not in `raw_transcripts_canonical/`
- `FzNDQm7wC_s` (Title: *Nifty Move After Iran-US News 🔥#niftymovement  Glo*) — not in `raw_transcripts_canonical/`
- `J_BzeTB3PpA` (Title: *Nifty Ka Agla Move 🔥 | Volume Analysis #trendanaly*) — not in `raw_transcripts_canonical/`
- `lmhqooBqJWU` (Title: *Nifty में गिरावट या रैली? 90% लोग Wrong! 🚨 || 90%*) — not in `raw_transcripts_canonical/`

Per step 1 of `gemini-edge-nk-batch1-1113`:
> "Run python scripts/dev/fetch_captions_timed.py --analyst Tom --status first. If BLOCKED fetch nothing, write NOT_IN_DATA.md in the output folder with the unlock time and stop."

Caption fetching is locked until `2026-11-16T14:21:46+00:00`. Real captions cannot be fetched, and per instructions, no proxies, cookies, YouTube API, memory, or invented quotes are permitted.
