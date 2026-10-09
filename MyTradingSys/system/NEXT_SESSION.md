# NEXT SESSION PROMPT (handoff 2026-10-10, after T092; Claude Code Win App, either account)

ONE-MESSAGE RULE (operator 2026-10-10, standard practice): the block below must run with no input from the operator. Every open question carries a default; the session answers itself from Control Room (ArtifactData) and acts. Overwrite this file at each handoff.

```
MTS builder session. Read CLAUDE.md, STATUS.md (regenerate first), then State below. Worktree only, never the live tree.
0. `python scripts/dev/sync.py start`, `sync.py where`, `desk.py list --all`. Push fails: say so in one line, stop.
   One task per session; hand off after the task, 5 operator turns or ~50k tokens: ship, overwrite this file, `where` clean.
1. Control Room (url in CONTROL_ROOM.md): ArtifactData list decisions + feedback. Apply answered decisions with no `applied`;
   file `new` inbox items per CONTROL_ROOM.md step 3. D13 (session_state thesis on the Tom card) unanswered = no change.
2. DSA results: for every desk task now done, spot-check ONE number against its file, then use it (no redo). Pending DSA tasks stay.
3. TASK (pick first unclaimed, claim it):
   a. T085/T093 4-12h imbalance spec. Another session was writing items/T093 + tests in the main NUC clone (uncommitted, 2026-10-10 02:16).
      Check origin first: if T093 shipped, only post its DSA runs (split by year, <300 s each); if not shipped and no claim, write it.
   b. B157 carried context in screenshot reads (Sonnet): prompt in research/screenshot_context_2026-10-10/REPORT.md section 7.
   c. D11 answered "Yes, download" (2026-10-09 19:43Z): ~9 Malkan public captions with yt-dlp (no video), plus Hindi ones per the note;
      then mark D11 applied. D12 answered "Yes, once a day": record it in system/DSA_DELEGATION.md, mark D12 applied.
   d. B159, B160 (prompts in the T092 REPORT section 7), then B151 gaps, then B158 after D13.
4. Route run-and-report work to DSA (system/DSA_DELEGATION.md); post what the DSA queue lacks before ending.
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

State at handoff

* 2026-10-10 T092 DONE (Opus, JIS-NUC): research/screenshot_context_2026-10-10/REPORT.md. Every screenshot read starts cold;
  session_state.json (the only context store) is dead since 09-14; the engine's archive mode can replay state at a shot's time
  but no read calls it; claim rows are kept as counts only. Filed B157 (HIGH), B158-B161. D13 asks the operator about B158.
* Live mirror still REFUSED on the NUC (no CURRENT under \JIS-NB\MTS-Mirror); desk task 20261009-202832 (JIS-NB) pending.
* Control Room: D09/D10 marked applied (5c5678d). D11 and D12 answered, not yet applied (task 3c).
* DSA: refresh-klines done on JIS-NB (klines to 10-08, funding to 09-30); not spot-checkable on the NUC (cache on JIS-NB only).
  Pending: B154 stratify, NO-SOURCE sweep (taken), transcript inventory, daily gate.
* Main NUC clone (BinanceDataFeed) holds another session's 2 unshipped commits (938d96b, 1ca6e4c: B149/B153) and T093 files: not ours.
* Not shipped, owned by JIS-NB live tree: backtest/bigtrade/, research/bigtrade_2026-10-09/, pm_heartbeats files. Do not edit.
* No git stash in shared clones; do not pass --help to sync.py subcommands.
