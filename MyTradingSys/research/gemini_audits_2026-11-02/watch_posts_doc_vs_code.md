# MATCH: 34, MISMATCH: 2, NOT_IN_CODE: 3

# Doc-vs-Code Audit: `analysts/watch/ROUTINE.md` vs `watch_posts.py`

- **Audit Task**: `gemini-doc-vs-code-watch-posts-1102`
- **Target Document**: `MyTradingSys/research/analysts/watch/ROUTINE.md`
- **Target Codebase**: `MyTradingSys/research/analysts/watch/watch_posts.py`
- **Auxiliary Code Reference**: `scripts/dev/fetch_captions_timed.py`, `MyTradingSys/research/analysts/watch/test_watch_posts.py`

## Summary Counts
- **Total Claims Audited**: 39 (OURS: count of discrete behavioral and schema claims)
- **MATCH**: 34 (OURS: behavior/schema in code conforms to document claim)
- **MISMATCH**: 2 (OURS: code behavior or emitted schema contradicts document claim)
- **NOT_IN_CODE**: 3 (OURS: claim asserted in document has no implementation logic in `watch_posts.py`)

---

## Detailed Claims vs Implementation Audit

| # | Document Claim | ROUTINE.md Ref | Code Implementation / Reality | watch_posts.py Ref | Status | Notes / Provenance |
|---|---|---|---|---|---|---|
| 1 | Routine tracks new posts from Habib (@qriptal) | `ROUTINE.md:3` | `WATCH_CHANNELS = [("Habib", "@qriptal"), ...]` | `watch_posts.py:36` | **MATCH** | Exact handle and analyst match |
| 2 | Routine tracks new posts from Krown (@ECKrown) | `ROUTINE.md:3` | `WATCH_CHANNELS = [..., ("Krown", "@ECKrown")]` | `watch_posts.py:37` | **MATCH** | Exact handle and analyst match |
| 3 | Source 1 is YouTube auto-captions / timed transcripts via `scripts/dev/fetch_captions_timed.py` | `ROUTINE.md:4` | `FETCH_CAPTIONS_SCRIPT = REPO_ROOT / "scripts" / "dev" / "fetch_captions_timed.py"`; invoked in subprocess | `watch_posts.py:31,256-263` | **MATCH** | Exact script invocation |
| 4 | Source 2 is Discord Qriptal `#trading-thoughts` channel via read-only screen reading | `ROUTINE.md:5` | Reads `DEFAULT_DISCORD_MD = ... / "habib_trading_thoughts.md"`; `parse_discord_markdown_table` default `#trading-thoughts` | `watch_posts.py:29,121-124,327,332` | **MATCH** | Staged read-only markdown reader parses `#trading-thoughts` |
| 5 | Source 2 tracks Discord Qriptal `#trading-updates` channel | `ROUTINE.md:5` | Mentioned only in module docstring L2; no parser, input file path, or logic for `#trading-updates` exists | `watch_posts.py:2,29,122,327` | **NOT_IN_CODE** | `#trading-updates` channel is unhandled in code execution |
| 6 | Logged rows recorded in `MyTradingSys/research/analysts/watch/POSTS_LOG.csv` | `ROUTINE.md:7` | `DEFAULT_LOG_PATH = WATCH_DIR / "POSTS_LOG.csv"`; `run_watch` default target | `watch_posts.py:28,295` | **MATCH** | Exact output path match |
| 7 | Schema Header: `seen_utc,post_utc,source,channel,analyst,id_or_url,summary` | `ROUTINE.md:15` | `CSV_HEADER = ["seen_utc", "post_utc", "source", "channel", "analyst", "id_or_url", "summary"]` | `watch_posts.py:33` | **MATCH** | Exact 7-field header match (cite: 7 fields) |
| 8 | `seen_utc`: ISO 8601 UTC timestamp when row observed | `ROUTINE.md:18` | `seen_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")` | `watch_posts.py:126,189,251,307` | **MATCH** | Formats ISO 8601 UTC string upon run |
| 9 | `post_utc`: ISO 8601 UTC timestamp of original post or publication date | `ROUTINE.md:19` | `convert_discord_time_to_utc` returns `%Y-%m-%dT%H:%M:%SZ`; YouTube uses transcript pub timestamp | `watch_posts.py:71,144,201,224,273` | **MATCH** | Formats publication time as ISO 8601 UTC string |
| 10 | `source`: `youtube` or `discord` | `ROUTINE.md:20` | Output dictionary explicitly assigns `"source": "youtube"` or `"source": "discord"` | `watch_posts.py:160,205,228,277,319,339` | **MATCH** | Exact string values |
| 11 | `channel`: channel names `@qriptal`, `@ECKrown`, `#trading-thoughts` | `ROUTINE.md:21` | Code assigns `@qriptal`, `@ECKrown`, and `#trading-thoughts` | `watch_posts.py:36-37,122,161,206,229,278,320` | **MATCH** | Exact channel identifiers emitted |
| 12 | `channel`: schema lists `#trading-updates` as an emitted channel | `ROUTINE.md:21` | Code never outputs `#trading-updates` to the channel column (only `#trading-thoughts`) | `watch_posts.py:33,161,320,340` | **MISMATCH** | `#trading-updates` is documented in schema list but never written |
| 13 | `analyst`: `Habib` or `Krown` | `ROUTINE.md:22` | Output rows set `"analyst": "Habib"` or `"analyst": "Krown"` | `watch_posts.py:36-37,121,162,207,230,279,321,341` | **MATCH** | Exact analyst names |
| 14 | `id_or_url`: YouTube video URL (`https://www.youtube.com/watch?v=...`) | `ROUTINE.md:23` | Formats `"id_or_url": f"https://www.youtube.com/watch?v={vid}"` | `watch_posts.py:208,231,280` | **MATCH** | Exact URL pattern match |
| 15 | `id_or_url`: Discord composite ID (`discord:<analyst>:<utc>`) | `ROUTINE.md:23` | `id_or_url = f"discord:{analyst.lower()}:{post_utc}"` | `watch_posts.py:156` | **MATCH** | Exact composite format match |
| 16 | `id_or_url`: `DISCORD_BLOCKED` when access blocked | `ROUTINE.md:23` | Sets `"id_or_url": "DISCORD_BLOCKED"` | `watch_posts.py:322,342` | **MATCH** | Exact string token match |
| 17 | `summary`: video title or quoted setup/quote | `ROUTINE.md:24` | YouTube uses `title`; Discord formats `"side: ...; quote: ..."` | `watch_posts.py:150-154,209,232,281` | **MATCH** | Exact field usage match |
| 18 | Deduplication against existing `id_or_url` values | `ROUTINE.md:26` | `read_existing_ids` parses existing CSV; filters `r.get("id_or_url") not in existing_ids` | `watch_posts.py:74-84,92-95` | **MATCH** | Deduplication on `id_or_url` |
| 19 | YouTube Guard implemented via `scripts/dev/fetch_captions_timed.py` | `ROUTINE.md:33` | Imports `fetch_captions_timed as ft`; invokes via subprocess | `watch_posts.py:31,114,257,363` | **MATCH** | Delegated guard implementation |
| 20 | Respects `~/.mts/yt_block.json` and fleet signals | `ROUTINE.md:35` | Calls `ft.blocked_until(check_ip=False)` which checks local file and signals branch | `watch_posts.py:110-118` (calls `fetch_captions_timed.py:115`) | **MATCH** | Guard delegation |
| 21 | If block is live, routine exits with code 3 (cite: `ROUTINE.md:36`) | `ROUTINE.md:36` | `if is_youtube_blocked(): ... return 3` | `watch_posts.py:302-304` | **MATCH** | Exact exit code 3 (cite: `watch_posts.py:304`) |
| 22 | If block is live, routine writes zero rows (cite: `ROUTINE.md:36`) | `ROUTINE.md:36` | Returns 3 before `append_rows` or file opening; zero rows written | `watch_posts.py:301-305` | **MATCH** | Early exit guarantees 0 rows (OURS: verified by test) |
| 23 | Max 5 video fetches per run (cite: `ROUTINE.md:37`) | `ROUTINE.md:37` | `watch_posts.py` defaults to `latest: int = 3` per channel (passed via `--latest 3`); does not pass `--max-videos 5` | `watch_posts.py:242,260,298,359` | **MISMATCH** | Doc claims max 5 fetches per run; code defaults 3 per channel (up to 6 total across 2 channels) |
| 24 | 20-second pause between network calls (cite: `ROUTINE.md:37`) | `ROUTINE.md:37` | No sleep or pause logic in `watch_posts.py` (handled internally within `fetch_captions_timed.py:14,19,418`) | `watch_posts.py:1-374` | **NOT_IN_CODE** | Throttle pause not in `watch_posts.py` source |
| 25 | Never evades or uses proxies without verified teardown | `ROUTINE.md:38` | No proxy setup or teardown logic in `watch_posts.py` (handled in `fetch_captions_timed.py:37-41`) | `watch_posts.py:1-374` | **NOT_IN_CODE** | Proxy policy not in `watch_posts.py` source |
| 26 | Read-only screen reading of operator's own login | `ROUTINE.md:42` | Strictly reads local markdown files or receives permission boolean; no interactive write/send commands | `watch_posts.py:2,9,121-167,314-344` | **MATCH** | Completely passive screen reader logic |
| 27 | Prohibition: NO bot tokens | `ROUTINE.md:44` | No token variables, headers, or API tokens anywhere in code | `watch_posts.py:9,1-374` | **MATCH** | No bot tokens |
| 28 | Prohibition: NO third-party scraping/export tools | `ROUTINE.md:45` | Uses standard library only (`re`, `csv`, `datetime`, `pathlib`, `subprocess`) | `watch_posts.py:16-23` | **MATCH** | No third-party scraper dependencies |
| 29 | Prohibition: NO posting, reacting, or chatting | `ROUTINE.md:46` | Read-only parser; zero message post/react network code | `watch_posts.py:9,1-374` | **MATCH** | No outbound Discord mutation APIs |
| 30 | Discord timestamps displayed to operator are local IST (UTC+05:30) (cite: `ROUTINE.md:48`) | `ROUTINE.md:48` | `def convert_discord_time_to_utc(..., tz_offset_hours: float = 5.5)` | `watch_posts.py:10,41` | **MATCH** | Default offset 5.5 hours = UTC+05:30 (cite: `watch_posts.py:41`) |
| 31 | All timestamps converted to UTC (`convert_discord_time_to_utc`) before writing | `ROUTINE.md:49` | Calls `convert_discord_time_to_utc(when_raw, tz_offset_hours=tz_offset_hours)` for all Discord entries | `watch_posts.py:41-71,144` | **MATCH** | Standard conversion applied to all rows |
| 32 | One-time operator approval required for screen interaction | `ROUTINE.md:51` | `run_watch(..., request_access_fn=None)`; checks `if request_access_fn is not None and not request_access_fn():` | `watch_posts.py:296,315` | **MATCH** | Explicit callback parameter for operator gate |
| 33 | If permission denied or headless, log `DISCORD_BLOCKED` in `POSTS_LOG.csv` | `ROUTINE.md:52` | Appends row with `"id_or_url": "DISCORD_BLOCKED"` and explanatory summary | `watch_posts.py:315-324,336-344` | **MATCH** | Blocked placeholder logged |
| 34 | If permission denied, proceed with YouTube processing | `ROUTINE.md:52` | `yt_rows = fetch_youtube_posts(...)` runs at L310 before Discord check at L315 | `watch_posts.py:310,315` | **MATCH** | YouTube execution precedes Discord check |
| 35 | If permission denied, exit cleanly (exit code 0) | `ROUTINE.md:52` | Routine completes logging and returns 0 (cite: `watch_posts.py:349`) | `watch_posts.py:349` | **MATCH** | Clean return 0 (cite: `watch_posts.py:349`) |
| 36 | CLI command: `scripts/dev/fetch_captions_timed.py --analyst dummy --status` | `ROUTINE.md:60` | `fetch_captions_timed.py` accepts `--status` flag without network requests | `scripts/dev/fetch_captions_timed.py:22-23,725` | **MATCH** | Valid CLI invocation |
| 37 | CLI command: `python MyTradingSys/research/analysts/watch/watch_posts.py --status` | `ROUTINE.md:64` | `args.status` delegates to `FETCH_CAPTIONS_SCRIPT ... --status` | `watch_posts.py:357,362-364` | **MATCH** | CLI argument and execution match |
| 38 | CLI command: `python MyTradingSys/research/analysts/watch/watch_posts.py --run` | `ROUTINE.md:69` | `args.run` executes `run_watch(log_path=args.log_file, yt_latest=args.latest)` | `watch_posts.py:356,366-367` | **MATCH** | CLI argument and execution match |
| 39 | Unit test command: `python -m pytest MyTradingSys/research/analysts/watch/test_watch_posts.py -q` | `ROUTINE.md:74` | Unit test file exists and executes 7 tests cleanly (OURS: 7 passed in 0.14s) | `test_watch_posts.py:1-160` | **MATCH** | 7 tests pass (cite: `test_watch_posts.py:25-150`) |


## Claude review note (Lead, 2026-11-02)

- Verified against the files: both MISMATCHes hold (ROUTINE.md:21 lists #trading-updates, code never emits it; ROUTINE.md:37 says max 5 fetches, watch_posts.py:242,298,359 default to 3 per channel, up to 6 over two channels). The NOT_IN_CODE rows (pause, proxy rule, #trading-updates reader) also hold for watch_posts.py itself.
- Gemini wrote SOURCED on code cites; changed to cite: since SOURCED means the trader's words.
- Not re-run: the 7 unit tests claim.
