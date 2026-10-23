# CBP actionable-6 profile (card cbp-actionable-6-extraction-profile-rekt)
CBP commit: 50e71c3 (F:/CryptoScrapper, branch cloud/work, pushed). Files: cbp_v2/analysts.json (`profile`, `active_profile`), fetch_latest.py `--profile`, tools/detect_new.py, extract_prompt.md, actionable_prompt.md, tools/test_profile.py.

- ON (profile actionable): Rekt, Jason, Krown, Michael, Michaal, Qriptal.
- OFF by default (profile thesis): Benjamin, Bob, Jala, CCU (Malkan, IA already disabled). Refresh by hand: `python cbp_v2/fetch_latest.py --profile all` (no scheduler).
- Bytes (store now, 2026-10-23): all enabled 3,075,457 B; actionable-6 462,719 B; saving 85% in the current store (the card's 35% was on 1,198,159 B). Command: sum `raw_transcripts_canonical/*_raw.txt` sizes grouped by `# Analyst:` header.
- Quote format: extractions.md already carried one `evidence:` line in 69 of 70 blocks (mean block 1,019 B). The profile keeps that format, so per-block change = 0 B. Per-video token change after a new extraction run: NOT_IN_DATA; command: `python cbp_v2/tools/latest_blocks.py | wc -c` before and after the next run.
