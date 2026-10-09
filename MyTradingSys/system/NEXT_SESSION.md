# NEXT SESSION PROMPT (handoff 2026-10-09 night, sync/recovery session; for Claude Code Win App on the PC, second subscription account)

Paste the block below into a new Claude Code session (Win App, bypassPermissions). Overwrite this file at each handoff.

```
MTS builder session (second account, PC). Read CLAUDE.md, STATUS.md, then this file's State section. Worktree only, never the live tree.
0. Start: `python scripts/dev/sync.py start`, then `sync.py where`. Account B needs GitHub write access (CLOUD_ACCOUNTS.md); if push fails, say so in one line and stop.
1. Fix 2 non-verbatim quoted fragments in extracts/v2/tom/etg6j0JybfE_v2.md (lines 40, 158) against raw_transcripts_canonical/etg6j0JybfE_raw.txt;
   rerun verify_extract_quotes.py (must be 0 problems).
2. Re-extract the 4 remaining Tom videos (inbox 3b25rvpra36evfyzc5rz) as extracts/v2/tom/<id>_v2.md, same format as ShYS_pD5cxQ_v2.md:
   QClPWDJ-BrU, 5Ljfwvtktek, Of_wlv3xaZo, oPyUif2Zrtk. Sonnet workers; run extract_fix_gps.py then verify_extract_quotes.py. Aim: rules that apply on a naked BTC chart.
3. Then Tom core backtest on those rules in phases (T082 re-run on the fixed volume profile / naked POC), using volume profiles anchored at pivots
   (research/vp_pivots_2026-10-09/SOURCES.md, FORMULAS.md). Expected numbers from FORMULAS.md only.
4. Control Room: operator answers D08 (turn_of_candle next), D09 (fee gate 0.3 on/off), D10 (heartbeat age limit) -> apply, rebuild + republish.
   Then B148 part 5 (limit from D10, fail-first test incl. pid reuse), T085 (97 % time exits).
5. Malkan RSI: steps 1-3 done (backtest/layers/rsi). Pulling the ~9 missing Malkan transcripts with yt-dlp needs operator OK first (fgN6QBFY3Ss, TYB7GJODt-k matter most).
End: ship via sync.py ship, `sync.py where` must show 0 unshipped, overwrite this file.
```

## State at handoff
- origin/fast-track is the only truth. Everything from the earlier sessions is on it (B148 p5 heartbeat, B146 fee gate 0.3, F-BT-09/14 Java deployed, RSI reclaim/divergence, Kurisko spec,
  pivot-VP sources, Control Room, MTS-Backup task, CI mark-green -> origin/green/fast-track). Recovered this session: Tom v2 extracts ShYS_pD5cxQ, etg6j0JybfE, scripts/dev/extract_fix_gps.py.
- NOT shipped, owned by the JIS-NB live tree: backtest/bigtrade/*, research/bigtrade_2026-10-09/*, pm_heartbeats files. Only on origin/backup/JIS-NB/BinanceDataFeed. Owners must `sync.py ship` them. Do not edit.
- Stale, ignore: origin/backup/JIS-NB/mts-research (old harness/canary files).
- Kurisko: his scalp is "Quad Rotation" (4 stochastics), no source ties him to RSI; "4 RSI" stays NO-SOURCE, no backtest.
- Recovery: `git fetch origin backup/JIS-NB/<name>` then `git restore --source=FETCH_HEAD -- <files>`. Backups are never merged.
- Two subscriptions: credits are per account, nothing else is. Start with `sync.py where`+`start`, end with `where`+`ship`.
