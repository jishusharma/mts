# Analyst Posts Watch Routine (Haiku / MTS)

This routine tracks new posts and trade statements from **Habib** (@qriptal) and **Krown** (@ECKrown) across two sources:
1. **YouTube** auto-captions / timed transcripts via `scripts/dev/fetch_captions_timed.py`.
2. **Discord** Qriptal `#trading-thoughts` and `#trading-updates` channels via read-only screen reading of the operator's login.

Logged rows are recorded in `MyTradingSys/research/analysts/watch/POSTS_LOG.csv`.

---

## Output Schema (`POSTS_LOG.csv`)

Header:
```csv
seen_utc,post_utc,source,channel,analyst,id_or_url,summary
```

- `seen_utc`: ISO 8601 UTC timestamp when the row was observed by the routine.
- `post_utc`: ISO 8601 UTC timestamp of the original post or publication date.
- `source`: `youtube` or `discord`.
- `channel`: Channel name (`@qriptal`, `@ECKrown`, `#trading-thoughts`, `#trading-updates`).
- `analyst`: `Habib` or `Krown`.
- `id_or_url`: Unique post URL, video URL (`https://www.youtube.com/watch?v=...`), composite ID (`discord:<analyst>:<utc>`), or `DISCORD_BLOCKED`.
- `summary`: Video title or quoted setup/quote.

Deduplication: Rows are deduplicated against existing `id_or_url` values.

---

## Operating Procedures & Guard Rules

### 1. YouTube Caption Guard
- Guard implementation: `scripts/dev/fetch_captions_timed.py`.
- **Lockout and Block Rules**:
  - Respects `~/.mts/yt_block.json` and fleet signals.
  - If a block is live, the routine **exits with code 3** and writes **zero** rows.
  - Max 5 video fetches per run, 20-second pause between network calls.
  - Never evades or uses proxies without verified teardown.

### 2. Discord Read-Only Screen Reading Procedure
*(Copied from `MyTradingSys/research/imbalance_qriptal_2026-10-16/discord/README.md`)*
- Read-only screen reading of the operator's own Discord login.
- **Strict prohibitions**:
  - NO bot tokens.
  - NO third-party scraping/export tools.
  - NO posting, reacting, or chatting.
- **Timezone conversion**:
  - Discord timestamps displayed to the operator are local Indian Standard Time (IST, UTC+05:30).
  - All timestamps MUST be converted to UTC (`convert_discord_time_to_utc`) before writing to `POSTS_LOG.csv`.
- **Computer-use permission**:
  - One-time operator approval required for screen interaction.
  - If permission is denied or running in a headless/unattended environment, log `DISCORD_BLOCKED` in `POSTS_LOG.csv`, proceed with YouTube processing, and exit cleanly.

---

## How to Run

### Check YouTube Guard Status (No Network)
```powershell
python scripts/dev/fetch_captions_timed.py --analyst dummy --status
```
or:
```powershell
python MyTradingSys/research/analysts/watch/watch_posts.py --status
```

### Execute Routine
```powershell
python MyTradingSys/research/analysts/watch/watch_posts.py --run
```

### Run Unit Tests
```powershell
python -m pytest MyTradingSys/research/analysts/watch/test_watch_posts.py -q
```
