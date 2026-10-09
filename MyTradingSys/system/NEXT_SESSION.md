# NEXT SESSION PROMPT (handoff 2026-10-09 night, sync/recovery session; for Claude Code Win App on the PC, second subscription account)

Paste the block below into a new Claude Code session (Win App, bypassPermissions). Overwrite this file at each handoff.

```
MTS builder session. Read CLAUDE.md, STATUS.md, then this file's State section. Worktree only, never the live tree.
0. Start: `python scripts/dev/sync.py start`, then `sync.py where`. If push fails, say so in one line and stop.
1. Tom core backtest phase 2 (plan: research/tom_core_bt_2026-10-09/PLAN.md): build backtest/vp_pivot_probe.py exactly as
   FORMULAS.md section 18, tests first from the worked examples 18.1-18.7 (must fail before the code). Sonnet implements.
   Run on 5m bars from Dumps/backtest raw_1m_2022 + raw klines (2022-01..2026-10-07). >= 300 events per variant; split by year.
2. Control Room: operator answers D08 (turn_of_candle next), D09 (fee gate 0.3 on/off), D10 (heartbeat age limit) live only in the
   artifact db (EoHi2qTMEsbR4VsKWuo2su); account B could not read it on 2026-10-09. Read on the account that owns the page -> apply,
   rebuild + republish. Then B148 part 5 (limit from D10, fail-first test incl. pid reuse), T085 (97 % time exits).
3. Malkan RSI: pulling the ~9 missing Malkan transcripts with yt-dlp needs operator OK first (fgN6QBFY3Ss, TYB7GJODt-k matter most).
End: ship via sync.py ship, `sync.py where` must show 0 unshipped, overwrite this file.
```

## State at handoff
- 2026-10-09 PC session: etg6j0JybfE quotes fixed; v2 extracts for QClPWDJ-BrU, 5Ljfwvtktek, Of_wlv3xaZo, oPyUif2Zrtk shipped (all 9 Tom videos now v2); Tom core backtest phase 1 PLAN.md shipped. aggTrades not on disk: footprint/CVD rules blocked. BinanceDataFeed.registry worktree: sync start hit a .gitignore merge conflict, merge aborted, its own unshipped commit untouched.
- origin/fast-track is the only truth. Everything from the earlier sessions is on it (B148 p5 heartbeat, B146 fee gate 0.3, F-BT-09/14 Java deployed, RSI reclaim/divergence, Kurisko spec,
  pivot-VP sources, Control Room, MTS-Backup task, CI mark-green -> origin/green/fast-track). Recovered this session: Tom v2 extracts ShYS_pD5cxQ, etg6j0JybfE, scripts/dev/extract_fix_gps.py.
- NOT shipped, owned by the JIS-NB live tree: backtest/bigtrade/*, research/bigtrade_2026-10-09/*, pm_heartbeats files. Only on origin/backup/JIS-NB/BinanceDataFeed. Owners must `sync.py ship` them. Do not edit.
- Stale, ignore: origin/backup/JIS-NB/mts-research (old harness/canary files).
- Kurisko: his scalp is "Quad Rotation" (4 stochastics), no source ties him to RSI; "4 RSI" stays NO-SOURCE, no backtest.
- Recovery: `git fetch origin backup/JIS-NB/<name>` then `git restore --source=FETCH_HEAD -- <files>`. Backups are never merged.
- Two subscriptions: credits are per account, nothing else is. Start with `sync.py where`+`start`, end with `where`+`ship`.
