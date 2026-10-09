# NEXT SESSION PROMPT (handoff 2026-10-09 night, T088 timeframe session; for Claude Code Win App on the PC, second subscription account)

Paste the block below into a new Claude Code session (Win App, bypassPermissions). Overwrite this file at each handoff.

```
MTS builder session. Read CLAUDE.md, STATUS.md, then this file's State section. Worktree only, never the live tree.
0. Start: `python scripts/dev/sync.py start`, then `sync.py where`. If push fails, say so in one line and stop.
Short sessions: one task per session; hand off when it is done, after 5 operator turns or ~50k tokens (first wins): ship, overwrite this file, check `sync.py where`, stop.
Budget: weekly-reset hold lifted 2026-10-09 (Jis); heavy work may run now.
1. (T090 DONE, research/t090_7h_2026-10-09/RESULT.md: only sourced 7h anchor is 18:00 New York = 22/23 UTC, tool description only; T088 7h lead not robust, closed.)
   T088, T089, T090, T091 are DONE (see State).
2. (T087 DONE, research/t087_session_levels_2026-10-09/RESULT.md: failed first break of prior-day high -> spike retaken first 57-67%, Asia low first 24%; short to the low net negative, no edge, EU cells n<300.)
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
- 2026-10-09 late: DSA delegation shipped (e7d5084). Desk board target DSA holds 5 tasks (B154 stratify, NO-SOURCE sweep, transcript inventory, daily gate, data refresh). Doc: system/DSA_DELEGATION.md; prompt 5e. Claude next: write the T085 spec (4-12h order imbalance from klines taker-buy volume, D08 answer) and post it to DSA; read DSA results via `desk.py list --all`. Operator: D11 (Malkan download) and D12 (daily DSA session) open in Control Room; regenerate SESSION_PASTE so DSA sees 5e.
- 2026-10-09 T087 DONE: backtest/layers/session_levels/ (session_levels.py + runner, 15 tests fail-first), 913 events 2022-2026; no edge, clocks NO-SOURCE. Branch jisnb/t087-session-levels in worktree mts-vpa.
- 2026-10-09 T090 DONE: 7h anchor = 18:00 NY (22/23 UTC) is the only sourced one; 00:00 UTC and epoch stay NO-SOURCE; 7h bullish lead is an anchor/drift artifact (t 1.2 at sourced anchor). Branch jisnb/t088-tf-module.
- 2026-10-09 night: T088 DONE. registry.json + tf_resample.py: 4m, 3h, 7h (day-reset 00:00 UTC, default), 7h_epoch; both 7h NO-SOURCE.
  9 tests fail-first. T089 rerun: 4m no edge, 3h/7h insufficient n, 7h operator bullish lead (46, t 2.11) only on the day-reset anchor.
  Branch jisnb/t088-tf-module in worktree mts-vpa.
- 2026-10-09 night: T089+T091 DONE. backtest/layers/rsi/run_divergence_mtf.py (9 tests); research/rsi_divergence_mtf_2026-10-09/RESULT.md. RSI divergence on all 19 registry TFs 2022-01..2026-10-07, net of taker x2: no edge in any of the 32 cells with >= 300 events (1m-1h), Malkan 3-10 bars or operator 11-60 bars; 2h+ insufficient n on one symbol. Lead only: 6h operator bullish n=54. Branch jisnb/t089-rsi-div in worktree mts-vpa.
- 2026-10-09 late: Tom core phase 2 done (backtest/vp_pivot_probe.py, 26 tests). 48 anchor x level streams 2022-2026: all net -0.19..-0.25 R taker, gross ~0, none beats placebo; pivot anchors no better than calendar ones. Worktree mts-vpa, branch jisnb/tom-bt-phase2.
- 2026-10-09 evening: screenshots 90e55256ec34, 850745dc9d8d, 6188a576411b read and closed (research/screenshots/); T087-T091 filed in BUGS.md + items. The live tree registry is behind origin, so shot.py `done --outcome finding:` refuses new ids there; use note: until the next deploy.
- 2026-10-09 PC session: etg6j0JybfE quotes fixed; v2 extracts for QClPWDJ-BrU, 5Ljfwvtktek, Of_wlv3xaZo, oPyUif2Zrtk shipped (all 9 Tom videos now v2); Tom core backtest phase 1 PLAN.md shipped. aggTrades not on disk: footprint/CVD rules blocked. BinanceDataFeed.registry worktree: sync start hit a .gitignore merge conflict, merge aborted, its own unshipped commit untouched.
- 2026-10-09 JIS-NB: B151 rerun DONE (trade-through on 1m data): all three CryptoCred setups FAIL; earlier PASS verdicts for S/R flip and fib pullback do not survive. B151 remaining gaps: setup2_fib_pullback emits no signal on blow-through (its 0 unfilled is by construction), bt_engine targets fill on touch, open_at_end not printed in the report. sync.py claim now rejects names starting with "--". Branch JIS-NB/cc-rerun in worktree mts-cc.
- origin/fast-track is the only truth. Everything from the earlier sessions is on it (B148 p5 heartbeat, B146 fee gate 0.3, F-BT-09/14 Java deployed, RSI reclaim/divergence, Kurisko spec,
  pivot-VP sources, Control Room, MTS-Backup task, CI mark-green -> origin/green/fast-track). Recovered this session: Tom v2 extracts ShYS_pD5cxQ, etg6j0JybfE, scripts/dev/extract_fix_gps.py.
- NOT shipped, owned by the JIS-NB live tree: backtest/bigtrade/*, research/bigtrade_2026-10-09/*, pm_heartbeats files. Only on origin/backup/JIS-NB/BinanceDataFeed. Owners must `sync.py ship` them. Do not edit.
- Stale, ignore: origin/backup/JIS-NB/mts-research (old harness/canary files).
- Kurisko: his scalp is "Quad Rotation" (4 stochastics), no source ties him to RSI; "4 RSI" stays NO-SOURCE, no backtest.
- Recovery: `git fetch origin backup/JIS-NB/<name>` then `git restore --source=FETCH_HEAD -- <files>`. Backups are never merged.
- Two subscriptions: credits are per account, nothing else is. Start with `sync.py where`+`start`, end with `where`+`ship`.
