# NEXT SESSION PROMPT (handoff 2026-10-10, DSA delegation session; Claude Code Win App, either account)

ONE-MESSAGE RULE (operator 2026-10-10, standard practice): the block below must run with no input from the operator. Every open question carries a default; the session answers itself from Control Room (ArtifactData) and acts. Overwrite this file at each handoff.

```
MTS builder session. Read CLAUDE.md, STATUS.md (regenerate first), then State below. Worktree only, never the live tree.
0. `python scripts/dev/sync.py start`, `sync.py where`, `desk.py list --all`. Push fails: say so in one line, stop.
   One task per session; hand off after the task, 5 operator turns or ~50k tokens: ship, overwrite this file, `where` clean.
1. Control Room (url in CONTROL_ROOM.md): ArtifactData list decisions + feedback. Apply answered decisions with no `applied`;
   file `new` inbox items per CONTROL_ROOM.md step 3. D11 (Malkan yt-dlp) unanswered = do NOT download. D12 unanswered = no change.
2. DSA results: for every desk task now done, spot-check ONE number against its file, then use it (no redo). Pending DSA tasks stay.
3. TASK (pick first unclaimed, claim it): 
   0. T092 (operator 2026-10-10, ask answered in its own session): run on OPUS, brief = items/T092_screenshot_context_gap.md. Deliverable = research/screenshot_context_2026-10-1x/REPORT.md + filed items; no code. Mirror first: `live_mirror.py pull && brief`.
   a. T085 spec: 4-12h order-imbalance after the turn of candle (D08 answer), from klines taker-buy volume (no aggTrades on disk),
      BTCUSDT 2022-2026, windows 4h/8h/12h, net of taker fees x2, source = research/TURN_OF_CANDLE_ORIGIN_2026-10-09.md paper.
      Write items/T085 + tests derived from the spec (fail first), then `desk.py post ... --target DSA` for the runs (split by year, <300 s each).
   b. B151 gaps: setup2_fib_pullback emits no signal on blow-through; bt_engine targets fill on touch. Sonnet implementation, fail-first tests.
   c. B156 Tom alert card stale SSOT_THESIS price text.
4. Route run-and-report work to DSA (system/DSA_DELEGATION.md); post what the DSA queue lacks before ending.
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

## State at handoff
- 2026-10-10 DSA delegation DONE (e7d5084, cd8117f): desk board target DSA, system/DSA_DELEGATION.md, prompt 5e + step 0 gate + block format, CLAUDE.md inbox/delegation lines. Guard test 14 passed.
- DSA queue (all pending at 2026-10-10 start, DSA has not run yet; needs a fresh SESSION_PASTE from the operator): B154 stratify, NO-SOURCE sweep B142-B145, transcript inventory, daily gate, data refresh.
- Control Room: inbox items answered; D08 answered (replace with 4-12h imbalance test; T085 spec not yet written = task 3a); D11 Malkan download and D12 daily DSA session wait for the operator.
- Operator manual steps: `setx MTS_ACCOUNT sharma` on the NUC; republish of the Control Room page only from its owning account (db changes are live without it).
- B151: CryptoCred rerun on 1m data done on JIS-NB (bb4a6bc): all three setups FAIL under trade-through fills.
- Earlier state (T087-T091 research all no edge after fees, Tom phase 2 no anchor edge, Kurisko = Quad Rotation not RSI): see research/STATUS and items; origin/fast-track is the only truth.
- Not shipped, owned by JIS-NB live tree: backtest/bigtrade/*, research/bigtrade_2026-10-09/*, pm_heartbeats files (origin/backup/JIS-NB/BinanceDataFeed). Do not edit.
- No git stash in shared clones; do not pass --help to sync.py subcommands.
