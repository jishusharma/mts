# NOT_IN_DATA: gemini-edge-nk-batch2-1113

**Status:** BLOCKED (caption fetcher locked out on host JIS-NUC)
**Checked at:** 2026-11-13T17:35:48Z (2026-11-13T23:05:48+05:30)

## Blocker
Running `python scripts/dev/fetch_captions_timed.py --analyst Tom --status` returned:

```text
BLOCKED until 2026-11-16T14:21:46+00:00 (host JIS-NUC, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 1 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 1
```

## Affected Video IDs
- `zjwCVVkmKCo` (Title: *Nifty next week Up or down   Harmuz open vs close*) — not in `raw_transcripts_canonical/`
- `a8RP5ftOfGo` (Title: *Nifty Ready For Big Move 🚀 Or Massive Crash 📉?  #nifty50  Nifty Bulls vs Bears 🐂🐻 | Crash Ya Rally?*) — not in `raw_transcripts_canonical/`
- `PLJda-dtBIc` (Title: *Life  Experience:200 DMA simple Use For Longterm Stock  Add/Remove/Avg #stockmarket #trading #200DMA*) — not in `raw_transcripts_canonical/`
- `jmwo9IaRr-0` (Title: *Portfolio ko kaise hedge karen ..NIfty View IRAN vs US #nk_sir #news #youtubeindia*) — not in `raw_transcripts_canonical/`
- `IRDWBSJV1KY` (Title: *Profit Lock kyse karen With  Smart Chart Reading Concept . #nk_sir #news #stockmarket*) — not in `raw_transcripts_canonical/`

Per step 1 of `gemini-edge-nk-batch2-1113`:
> "Run python scripts/dev/fetch_captions_timed.py --analyst Tom --status first. If BLOCKED fetch nothing, write NOT_IN_DATA.md in the output folder with the unlock time and stop."

Caption fetching is locked until `2026-11-16T14:21:46+00:00`. Real captions cannot be fetched, and per instructions, no proxies, cookies, YouTube API, memory, or invented quotes are permitted.
