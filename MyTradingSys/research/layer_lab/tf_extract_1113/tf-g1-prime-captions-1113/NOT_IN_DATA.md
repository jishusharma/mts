# NOT_IN_DATA: tf-g1-prime-captions-1113

## Blocker
YouTube caption fetching is currently rate-limited / locked out on this host (`DESKTOP-F7IU69N`):

```text
python scripts/dev/fetch_captions_timed.py --analyst Tom --status
BLOCKED until 2026-11-16T14:21:46+00:00 (host DESKTOP-F7IU69N, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 1 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 5
```

## Affected IDs
- `O5s9zWI0n2s` (Tom 4-step framework) — not in `raw_transcripts_canonical/`
- `VHhvg96W6lc` (Fabio start from zero) — not in `raw_transcripts_canonical/`
- `9IliXww64uM` (channel/title metadata check for Q13) — blocked on caption/metadata fetch

Per `tf-g1-prime-captions-1113.json` and `BRIEF_GAP_EXTRACT.md`, no watch-the-video notes or invented quotes are permitted; this card is blocked until after `2026-11-16T14:21:46+00:00` (or on an unlocked host).
