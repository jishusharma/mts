# NOT_IN_DATA: gemini-edge-nk-batch4-1113

**Status:** BLOCKED (caption fetcher locked out on host DESKTOP-F7IU69N)
**Checked at:** 2026-11-13T17:19:00Z (2026-11-13T22:49:00+05:30)

## Blocker
Running `python scripts/dev/fetch_captions_timed.py --analyst Tom --status` returned:

```text
BLOCKED until 2026-11-16T14:21:46+00:00 (host DESKTOP-F7IU69N, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 1 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 5
```

## Affected Video IDs
- `3KnEiKNh1pc` (Title: *Intraday Masterclass || Option Buying, Selling, Cash, Crypto & Commodity Market || #trading #nifty*) — not in `raw_transcripts_canonical/`
- `VLR7HiKTQpc` (Title: *Jane Street का Fraud Model और Nifty View || Stock Market || @NKStockTalk #nifty #financialmarket*) — not in `raw_transcripts_canonical/`
- `sbMyohOXRqE` (Title: *NIFTY Long & Short Term View || निफ्टी दीर्घ एवं लघु अवधि दृष्टिकोण || #financialmarket #nifty*) — not in `raw_transcripts_canonical/`
- `B7iGQef_z6I` (Title: *Candle Series || #beginnerseries -3 ||#career #market || @NKStockTalk #financial @NKStockTalk*) — not in `raw_transcripts_canonical/`
- `a-D7Pt3fvls` (Title: *How To Use Price Rejection Candle || #beginnerseries -1 ||#career #market || @NKStockTalk #financial*) — not in `raw_transcripts_canonical/`

Per step 1 of `gemini-edge-nk-batch4-1113`:
> "Run python scripts/dev/fetch_captions_timed.py --analyst Tom --status first. If BLOCKED fetch nothing, write NOT_IN_DATA.md in the output folder with the unlock time and stop."

Caption fetching is locked until `2026-11-16T14:21:46+00:00`. Real captions cannot be fetched, and per instructions, no proxies, cookies, YouTube API, memory, or invented quotes are permitted.
