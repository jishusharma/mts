# NOT_IN_DATA: O5s9zWI0n2s (Tom Vorwald - How to Finally Become a Profitable Trader! (4-Step Framework))

- Status check: `python scripts/dev/fetch_captions_timed.py --analyst Tom --status` reports:
  `BLOCKED until 2026-11-13T13:58:11+00:00 (host JIS-NUC, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 0 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 5`
- No YouTube request attempted (per scope_out rule: "any YouTube request through yt-dlp/fetch_captions*.py while 'fetch_captions_timed.py --status' says BLOCKED").
- Caption fetch is locked until 2026-11-13T13:58:11+00:00 due to earlier 429 lockout. Per policy: never evaded (no proxy, VPN, cookies, or alternate paths).
- No canonical raw transcript (`raw_transcripts_canonical/O5s9zWI0n2s_raw.txt`) exists in the worktree or repository.
- Antigravity / Gemini CLI session does not have direct video stream / YouTube playback tools to generate verbatim line-by-line speech timestamps for `gemini_transcript_O5s9zWI0n2s.txt` without fabricating quotes. Per global MTS policy ("NO ASSUMPTIONS, NO FABRICATIONS!"), unverifiable lines cannot be invented.
- Retry after lockout expires at `2026-11-13T13:58:11+00:00` with `fetch_captions_timed.py --analyst Tom`.
