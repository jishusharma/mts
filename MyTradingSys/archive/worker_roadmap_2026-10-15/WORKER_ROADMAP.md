# Worker roadmap: cheap, monitored workers (2026-09-28)

Goal: run the most work on the cheapest tier that can do it correctly, with every result checked by a
machine gate before a more expensive tier looks at it.

## 1. Tiers (cheapest first)
| Tier | Who | Cost / speed (measured this session) | Use for | Never use for |
|---|---|---|---|---|
| T0 | Script | ~0 | anything answerable exactly: counts, cross-checks, gates, static checks (e.g. `test_suite_static.py`) | - |
| T1 | **Qwen3-coder 30B on the NUC** (queue) | free; ~4.4 tok/s; 022 = 1575 s for 791 tokens out; runs one task at a time; sees only packed files | small self-contained edits with EXPECT lines; first drafts of reference implementations; doc edits | being the only reviewer of safety code (its 022 review was shallow and restated the diff); anything that needs to run code |
| T2 | **Haiku subagent** | low | running `queue_tool verify`, sandbox test runs, gates, triage (bug in the implementation vs in the test), mechanical edits, testnet suites (testnet only) | design decisions, safety-code authorship |
| T3 | Sonnet subagent | medium (PBO study 79k tokens; 13 mutation-killing tests 188k) | writing tests, mutation checks, medium edits with a clear contract | final sign-off on execution-layer safety |
| T4 | Opus (coordinator) | high | specs, contract decisions, reviewing **diffs** of safety code, final gate + commit | reading whole files a lower tier already summarised; polling |

Routing rule: if a script can answer it, write the script (T0). Otherwise Qwen drafts (T1), Haiku checks
(T2), and Opus reviews the diff only (T4). Go up one tier when a task FAILs twice at its tier.

## 2. The monitored loop (every job)
1. **Spec** (T4, ~20 lines): TASK / SCOPE (use line ranges for large files) / OUTPUT / EXPECT (at least 2
   lines) / "keep everything else byte-for-byte". Template: `Dumps/workers/NUC-QUEUE/specs/023-026`.
2. **Pack**: `python scripts/worker/queue_tool.py pack NNN-name.md` (it refuses critical files, oversize
   scopes and banned terms).
3. **Wait at zero token cost**: one background shell waits for the last reply file. No agent idles and
   nothing polls.
4. **Verify (T2 Haiku)**: `queue_tool.py verify NNN`, then copy the `.new` files into a temp sandbox and
   run the tests. Report a table of at most 25 lines: verdict | tests pass/total | each failure marked
   bug-in-implementation or bug-in-test with one reason citing the spec.
5. **Gate (T2)**: the area gate from section 3, run on a staged sandbox (`run_staged_tests.py`), never
   on the live tree first.
6. **Review (T4)**: the diff only (`diff -u live .new`). Safety code needs a test that fails without
   the change.
7. **Promote + commit** on `fast-track`: back up to `.pre_<tag>`, rename `.new`, re-run the gate, one
   commit per batch.

Stop and escalate when: verdict FAIL twice; a reply is cut off; the reply invents file names; the gate
is red after one fix attempt; or the task touches the stop/flatten/HALT paths (goes to T4 review, always).

## 3. Gates (exact commands, repo root)
**One command for all offline gates:** `python scripts/dev/run_all_tests.py` (`--quick` skips Maven + backtest).
Exit 0 = green. As of 2026-09-28 steps 1-5 PASS; step 6 (backtest) fails only on Qwen's own wrong test
expectations (fixed by 023/024 + Haiku test rewrites).

- **Execution layer**:
  `python scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline -- test_daily_loss_guard test_daily_loss_monitor test_gh_executor_offline test_gh_retry_offline test_halt_preflight_offline test_kill_switch test_risk_guard test_s1_cap_offline test_s3_unprotected_offline test_s6_orphan_offline test_soak_report test_fix3_offline` -> 116 OK;
  `... --script test_g1g2_offline.py --fake fake_deribit_orders.py=deribit_orders.py` -> 12/12;
  `python MyTradingSys/execution/testnet/test_suite_static.py` -> 5 OK.
- **Testnet** (T2 may run; TESTNET ONLY, never mainnet): requires HALT and HALT_DAILY_LOSS to be absent;
  run probe_account_summary, run_testnet_suite (6/6), g1g2 (6/6 + 4/4), ft2 (+ 4/4).
- **Backtest**: `python -m unittest` in a sandbox of `MyTradingSys/backtest/bt` with the `.new` files
  stripped.
- **Boot build**: `pwsh -File scripts/Build-Check.ps1` -> compile PASS, math 126/126, doc 5/5.

## 4. Backlog, routed (actionable now)
| # | Item | Tier | Status / next action | Gate |
|---|---|---|---|---|
| 1 | 023 PBO band test -> 20-seed aggregate | T1 -> T2 | queued on the NUC | backtest |
| 2 | 024 fix 2 wrong expectations in test_ref_pbo | T1 -> T2 | queued | backtest |
| 3 | 025 L7 daily_loss_guard: unused imports, missing pnl_usd raises | T1 -> T2 -> T4 diff | queued | execution |
| 4 | 026 L4 position_manager timer -> time.monotonic() | T1 -> T2 -> T4 diff | queued (check s3/fix3 fake clocks provide `monotonic`) | execution |
| 5 | 020 ref_pbo / 021 ref_ladder replies | T2 | Haiku triage running | backtest |
| 6 | bt_* `.new` (data, engine, ladder, stats + tests) promotion | T2 runs tests, T4 decides | after 1, 2, 5 | backtest |
| 7 | M7 soak_report: flag unresolved orders on closed/halted plans | T1 draft, T3 test | 027 queued | execution |
| 8 | L5 executor deadline hot loop (sleep after the cancel pass) | T1 | 028 queued (with M8) | execution |
| 9 | M8 document single-plan-only in executor/position_manager docstrings | T1 | executor part in 028 | doc |
| 10 | M4 re-check HALT before every order-creating call | T3 + test, T4 review | after 3-4 land | execution + testnet |
| 11 | L1 G2 "explained" check vs entry fills; L2 sweep target on OrderStateUnknown | T3 + tests, T4 review | - | execution + testnet |
| 12 | M2 HALT_DAILY_LOSS contract (recommend: existence blocks, operator deletes) | T4 decision | one-line decision, then T1 edit | execution |
| 13 | L3 act on B079 post-fill breach; L6 PnL counts deposits / breached_today never resets | T4 design | needs a design note | - |
| 14 | Stale `research/BUGS.md.new` (20 h), `qwen_raw_015_017/*.new` | T2 | diff summary + proposed delete list (deletions confirmed first) | doc tests |
| 16 | backtest_xcheck/test_ref_ladder: Haiku 'fixed' 5 Qwen expectations to match the implementation; test_deadline_cut_off and test_stop_hit_same_bar are now tautological (expect all fills / scan no bars) | T3 | rewrite from spec 021 by hand-computed bars; the ladder cross-check is not trusted until then | backtest |
| 15 | Testnet re-run after any execution-layer batch | T2 | after 3, 4, 10, 11 | testnet |

Suggested order: let the NUC run 023-028 back to back (about 1-2 h) while T3 writes 10 and 11 against the
current tree. Then one T2 pass verifies all four replies, and one T4 diff review plus one commit covers the batch.

## 5. Token rules for the coordinator
- Send workers **paths and line ranges, not file contents**; ask for tables of 25 lines or fewer, not narratives.
- One background waiter per batch; never an agent that sleeps or polls.
- Review diffs, not files. Never re-read what a worker has already summarised; spot-check one claim.
- Batch Qwen tasks (the queue is sequential and free): write every spec at once, pack, and walk away.
- Anything a script can check once gets a script, and the script joins the gate (the D1/D2 lesson).

## 6. Lessons from this session (why the loop looks like this)
- Qwen's own tests are often wrong (019: 2 of its tests had bad expectations; the implementation was right),
  so always sandbox-run and triage implementation vs test before trusting a FAIL.
- Qwen reviews are confirmations, not attacks; adversarial review stays at T3/T4 plus repro scripts.
- A green unit gate missed D1/D2 because nothing executed the suite files; hence `test_suite_static.py`.
- On Windows, Python `open(p, 'w')` writes CRLF; write with `newline='\n'`, or the diffs balloon (the
  queue tool refused a 142 KB diff until line endings were restored).
- `.new` output is never auto-applied; promotion is always backup -> rename -> re-gate -> commit.
