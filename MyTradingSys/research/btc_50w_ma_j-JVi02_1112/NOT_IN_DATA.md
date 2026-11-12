# NOT_IN_DATA: j-JVi02_C88 (Bitcoin Falls Below the 50W Moving Average)

- 2026-11-11T20:42Z: `fetch_captions_timed.py --analyst LongShort --max-videos 2 K31xH-6g9Vc j-JVi02_C88` fetched K31xH-6g9Vc, then YouTube answered `HTTP Error 429: Too Many Requests` on j-JVi02_C88 subtitles: row `j-JVi02_C88 BLOCKED`.
- `--status` after the run: `BLOCKED until 2026-11-12T02:41:59+00:00 (host JIS-NB) ; lockout level 1 of 3 (6/24/72 h, OURS)`.
- Not evaded (no proxy, VPN, cookies, `--fallback`). Retry after 2026-11-12T02:42Z with the same command, one video. Card filed: `extract-50w-ma-j-JVi02-retry-1112`.
- No quote from this video exists in the repo, so EXTRACT.md is not written. CHECK.md tests the title claim only ("BTC below the 50W MA") against our own weekly data; nothing in it is attributed to the video's author.

- 2026-11-11T21:46Z retry (card extract-50w-ma-j-JVi02-retry-1112): `fetch_captions_timed.py --analyst LongShort --status` = `BLOCKED until 2026-11-13T13:58:11+00:00 (host DESKTOP-F7IU69N, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS)`. No fetch attempted (step 1: if BLOCKED write the time and stop).
- FETCH rows: `j-JVi02_C88 BLOCKED`, `BB3c8visnkI BLOCKED`, `e83njGZFrPw BLOCKED` (not fetched; lockout). Retry after 2026-11-13T13:58Z, one video first. DECISION (OURS): no re-lane, no evasion; EXTRACT.md still not written (no verifiable quotes).

- 2026-11-12T02:53Z retry (card extract-50w-ma-j-JVi02-retry-1112): `--status` said NOT BLOCKED (level 1), one request `fetch_captions_timed.py --analyst LongShort --max-videos 1 j-JVi02_C88` returned `HTTP Error 429`, row `j-JVi02_C88 BLOCKED`. New status: `BLOCKED until 2026-11-13T02:53:04+00:00 (host JIS-NB); lockout level 2 of 3 (6/24/72 h, OURS)`. No second request, no proxy/VPN/cookies/--fallback.
- `BB3c8visnkI` and `e83njGZFrPw` (Tom): not fetched (lockout). EXTRACT.md and the CHECK.md claims table not written (no verifiable quotes). DECISION (OURS): j-JVi02_C88 goes to the Gemini lane list (captions-or-watch there, never ASR by Claude) if still blocked after the retry time; retry first at 2026-11-13T02:54Z.
