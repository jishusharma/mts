# NEXT SESSION PROMPT (handoff 2026-10-09 late, Tom core phase 2 session; for Claude Code Win App on the PC, second subscription account)

Paste the block below into a new Claude Code session (Win App, bypassPermissions). Overwrite this file at each handoff.

```
MTS builder session. Read CLAUDE.md, STATUS.md, then this file's State section. Worktree only, never the live tree.
0. Start: `python scripts/dev/sync.py start`, then `sync.py where`. If push fails, say so in one line and stop.
Short sessions: one task per session; hand off when it is done, after 5 operator turns or ~50k tokens (first wins): ship, overwrite this file, check `sync.py where`, stop.
Budget: weekly-reset hold lifted 2026-10-09 (Jis); heavy work may run now.
1. T089 multi-TF RSI divergence capture (+T091 long-range column, operator idea, NO-SOURCE), then T088 (add 4m, 3h, 7h), T090 7h research
   under playbook PART I. Detail: items/T088_all_timeframe_module.md.
2. T087 session-levels observation layer (prior-day / Asia / EU highs-lows, failed first break, backtested odds). items/T087_*.md.
3. D09 (fee gate 0.3 on) and D10 (heartbeat 10 min) are already applied on origin (B146, B148 part 5 in code). Left: D08 -> apply,
   then T085. Rebuild + republish Control Room only from the account that owns it.
4. Tom core phase 3 is parked: phase 2 found no anchor edge (research/tom_core_bt_2026-10-09/PHASE2_RESULT.md); Tom's confirmations
   need aggTrades. Ask Jis before fetching aggTrades or re-running with other barriers.
Open questions for Jis (asked in the project thread 2026-10-09): D08 park turn_of_candle (alerts kept) or keep it as the volume
generator (default until answered: keep, no change); OK to pull ~9 Malkan transcripts with yt-dlp?; 7h candle anchor
(default taken: restart at 00:00 UTC each day, like TradingView, last bar of the day 3h; flagged NO-SOURCE).
End: ship via sync.py ship, `sync.py where` must show 0 unshipped, overwrite this file.
```

## State at handoff
- 2026-10-09 late: Tom core phase 2 done (backtest/vp_pivot_probe.py, 26 tests). 48 anchor x level streams 2022-2026: all net -0.19..-0.25 R taker, gross ~0, none beats placebo; pivot anchors no better than calendar ones. Worktree mts-vpa, branch jisnb/tom-bt-phase2.
- 2026-10-09 evening: screenshots 90e55256ec34, 850745dc9d8d, 6188a576411b read and closed (research/screenshots/); T087-T091 filed in BUGS.md + items. The live tree registry is behind origin, so shot.py `done --outcome finding:` refuses new ids there; use note: until the next deploy.
- 2026-10-09 PC session: etg6j0JybfE quotes fixed; v2 extracts for QClPWDJ-BrU, 5Ljfwvtktek, Of_wlv3xaZo, oPyUif2Zrtk shipped (all 9 Tom videos now v2); Tom core backtest phase 1 PLAN.md shipped. aggTrades not on disk: footprint/CVD rules blocked. BinanceDataFeed.registry worktree: sync start hit a .gitignore merge conflict, merge aborted, its own unshipped commit untouched.
- origin/fast-track is the only truth. Everything from the earlier sessions is on it (B148 p5 heartbeat, B146 fee gate 0.3, F-BT-09/14 Java deployed, RSI reclaim/divergence, Kurisko spec,
  pivot-VP sources, Control Room, MTS-Backup task, CI mark-green -> origin/green/fast-track). Recovered this session: Tom v2 extracts ShYS_pD5cxQ, etg6j0JybfE, scripts/dev/extract_fix_gps.py.
- NOT shipped, owned by the JIS-NB live tree: backtest/bigtrade/*, research/bigtrade_2026-10-09/*, pm_heartbeats files. Only on origin/backup/JIS-NB/BinanceDataFeed. Owners must `sync.py ship` them. Do not edit.
- Stale, ignore: origin/backup/JIS-NB/mts-research (old harness/canary files).
- Kurisko: his scalp is "Quad Rotation" (4 stochastics), no source ties him to RSI; "4 RSI" stays NO-SOURCE, no backtest.
- Recovery: `git fetch origin backup/JIS-NB/<name>` then `git restore --source=FETCH_HEAD -- <files>`. Backups are never merged.
- Two subscriptions: credits are per account, nothing else is. Start with `sync.py where`+`start`, end with `where`+`ship`.
