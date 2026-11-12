# NOT_IN_DATA: tf-g3-fabio-shorts-partners-1113

- **Card:** `tf-g3-fabio-shorts-partners-1113`
- **Status:** `BLOCKED`
- **Blockers:**
  1. **Missing local Fabio short transcripts:** `F:/MTS/Dumps/wt_rescue/fable-btc-edge-assessment-cbd5aa/raw_transcripts_canonical` (and `F:/MTS/Dumps/wt_rescue/`) does not exist on host `JIS-NUC`.
  2. **YouTube caption fetcher lockout:** `python scripts/dev/fetch_captions_timed.py --analyst Tom --status` returned:
     `BLOCKED until 2026-11-13T13:58:11+00:00 (host JIS-NUC, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 0 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 5`
- **Action:** Cannot copy the 5 Fabio short transcripts or fetch 2 of the 4 partner videos until the transcripts path is available on this host and the YouTube caption lockout clears after `2026-11-13T13:58:11+00:00`.
