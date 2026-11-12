# NOT_IN_DATA — tf-g1-prime-captions-1113

**Status:** BLOCKED (captions locked on JIS-NUC)
**Checked at:** 2026-11-12T20:30:40Z (2026-11-13T02:00:40+05:30)
**Command:** `python scripts/dev/fetch_captions_timed.py --analyst Tom --status`
**Output:**
```
BLOCKED until 2026-11-13T13:58:11+00:00 (host JIS-NUC, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 0 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 5
```

## Blocker
- YouTube caption fetching on host `JIS-NUC` (`49.37.73.158`) is in lockout level 3 of 3 until `2026-11-13T13:58:11+00:00` (~17.5 hours from now).
- Per `tf-g1-prime-captions-1113` card instructions: do not use "watch the video" notes or memory; before caption unlock, write `NOT_IN_DATA.md` and stop.
- Re-run after `2026-11-13T13:58:11Z` on JIS-NUC (or after `2026-11-13T02:53Z` on desktop) to fetch `O5s9zWI0n2s`, `VHhvg96W6lc`, and metadata for `9IliXww64uM`.
