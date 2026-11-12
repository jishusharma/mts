# NOT_IN_DATA: tf-g2-tom-feed-triage-1113

**Status:** BLOCKED (caption fetcher locked out on host JIS-NUC)

## Blocker
Running `python scripts/dev/fetch_captions_timed.py --analyst Tom --status` on `2026-11-12T20:19:15Z` (`2026-11-13T01:49:15+05:30`) returned:

```
BLOCKED until 2026-11-13T13:58:11+00:00 (host JIS-NUC, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 0 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 5
```

Because YouTube caption fetching is locked until `2026-11-13T13:58:11+00:00`, the top 12 Tom newest-60 uploads cannot be fetched or extracted in this session.
