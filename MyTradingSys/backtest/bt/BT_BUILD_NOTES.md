# bt/ build notes — NUC builder scorecard + acceptance (2026-09-27, Opus review)
Every module was accepted ONLY against hidden spec tests written by Opus (test_bt_*.py.new), never against the
worker's own tests. Worker: qwen3-coder:30b on JIS-NUC, ~4.4 output tokens/s.

| task | module | worker time | verdict | what was wrong |
|---|---|---|---|---|
| 011 | bt_data.py | 490 s | ACCEPTED WITH FIXES | dropped the first data row of every headerless CSV; metrics timestamps parsed as LOCAL time (5.5 h off on the Windows box). Both fixed (marked "Opus fix"). |
| 012 | bt_engine.py | 1318 s | REJECTED, rewritten | R accounting wrong (target run gave 10R instead of 3R), timeout path wrong; its own tests contradicted the gap-fill rule. |
| 013 | bt_ladder.py | 392 s | REJECTED, rewritten | required the signal bar to be present, dropped rungs filled in the stop bar, popped the wrong rung. |
| 014 | bt_stats.py | 369 s | ACCEPTED WITH FIXES | syntax error (`for i i in oos_indices` in `pbo_cscv`, would not even compile) and a nonexistent method (`NormalDist().icdf`, not a real attribute in Python's `statistics` — should be `.inv_cdf`). Both fixed. Verified in session 5 against `check_bt_stats.py`: 4/4 PASS. |

**Correction 2026-09-28 (verdict provenance, 011-013):** the queue_tool verdicts BLOCKED/FAIL for 011/012/013 were false - a checker bug counted each task's own new output paths as "unknown file names" (DEV_VELOCITY_AUDIT.md finding 1; fixed in queue_tool.py, CREATE: header). The REJECTED decisions above did NOT rest on that verdict: they came from content review (reasons in the table). Re-verify with the fixed tool (compile + run Qwen's own tests) confirms the raw output was genuinely wrong: 012 = 7 failing tests, 013 = 4 failing tests, 011 = compiles (its test file not extracted: malformed `>>>>>>>END FILE` marker). So: checker verdict false, rejections stand, rewrites stand.

## 014 bt_stats — session 5 verification note
014 was NOT still running at handoff as SESSION_4_HANDOFF §4 assumed — it had actually finished at 15:53:35Z (see `Dumps/workers/NUC-QUEUE/done/014-bt-stats.reply.json`), the handoff note was just stale. Raw output did not compile (`for i i in` typo) and used a method name that doesn't exist on `statistics.NormalDist` (`icdf` vs the real `inv_cdf`) — same pattern as 011: small, mechanical bugs, not a design problem. Fixed both; `bt_stats.py.new` + `test_bt_stats.py.new` staged, all 4 hidden spec tests (`check_bt_stats.py`) pass.

Open item (not blocking, flagged for Opus — OPUS_QUEUE item 2, FROZEN.md/PBO review): the worker's own `test_pbo_cscv` (not part of the accepted spec) asserts PBO ∈ (0.2, 0.8) on i.i.d. Gaussian noise across 10 variants and gets 0.93 instead. This isn't necessarily wrong — CSCV/PBO selecting the best in-sample Sharpe among no-skill variants can legitimately show mean-reversion in the OOS rank — but 0.93 is high enough above the naive ~50% null that `pbo_cscv`'s calibration on pure noise should get a real look before it's used to gate anything, rather than being waved through on the hidden-spec pass alone.

Rejected drafts kept in _nuc_rejected/ for the record.
Lesson: the builder is fast enough for small pure functions, but its self-written tests are not evidence. Pack
hidden EXPECT/spec tests with every task and run them before reading the code.

Smoke test on real data (1000 random entries 2025-09..2026-09, 1%/2%/5% geometry, mark stops, Binance funding,
0.05% taker): mean net -0.069 R — this is the random-entry null baseline shape BACKTEST_PROTOCOL §5 expects
(slightly negative = costs). Runtime 1.8 s for 1000 trades.
