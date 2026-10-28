# OPUS QUEUE — what still needs Opus (and what does not)
Rewritten by Opus 5.5, session 4, 2026-09-27 ~16:00Z. Supersedes the Sonnet version of this file from ~14:30Z,
which was wrong on two points: D1-D7 were ALREADY ruled (D1_D7_DECISION_BRIEF.md "OPERATOR RULINGS"), and
Maven was not the blocker it reported — Maven Central is reachable from the linked-computer shell, and a
JDK 17 + Maven 3.9.9 toolchain now lives there ($HOME/tools, outside the repo).

## DONE this session (Opus items closed)
- C3 review: APPROVE — C3_OPUS_REVIEW.md (3 non-blocking findings R1-R3).
- L1 file-source adapter design review: GO with constraints — L1_ADAPTER_REVIEW.md.
- G1 post-entry management + G2 reconciler v2: code staged (position_manager.py.new, reconciler.py.new),
  offline logic proof 12/12 PASS (testnet/offline/), testnet cases staged (run_testnet_suite_g1g2.py.new).
- C5 (D5 + D6a/b text): compiled_engine.md.new, +22 lines, two [SYSTEM] blocks, no rule changes.
- Backtest method: BACKTEST_PROTOCOL.md (freeze + trial registry, holdout, walk-forward, purge/embargo, DSR, PBO,
  random-entry null, cost/ambiguity stresses, minimum-evidence bar).

## STILL NEEDS OPUS (in order)
1. G1/G2 testnet evidence review — after the operator runs run_testnet_suite_g1g2.py (G1b answers the open
   question: does Deribit clamp or reject an oversized reduce-only order). Mainnet gate stays closed until then.
2. FROZEN.md review before the first holdout run (BACKTEST_PROTOCOL §1, §8), and the first full REPORT.md.
3. C3-R1 fix design (finished-auction newest-first) once the operator accepts C3.
4. Tom-vs-Fabio override ruling follow-through: once the operator rules, Opus writes the layer contract
   (which slot each source may define) before any CC-1..CC-5 code.
5. T052 SETUP_CONFIRMED trigger definition (research; needs the 39 unextracted Tom transcripts first — that
   extraction itself is Sonnet/NUC work).

## NOT Opus (routing)
- Sonnet: L1 adapter build + P0/P1/P1b/P2 gates; L2-L4 wiring; B077-B079 rows in BUGS.md after the session-2
  BUGS.md.new is resolved; Tom transcript extraction (39 missing); W5 folder moves.
- NUC builder: bt_data / bt_engine / bt_ladder / bt_stats (tasks 011-014) and further mechanical pieces.
- Operator only: four-step proof + commit of the staged .new batch; testnet runs (key stays on the desktop);
  Tom-vs-Fabio override ruling; aggTrades parity download (long-running; cannot run from the bridge shell).
