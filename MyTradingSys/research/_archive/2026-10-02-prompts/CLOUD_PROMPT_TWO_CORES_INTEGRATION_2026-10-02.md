# CLOUD SESSION PROMPT: TWO CORES INTEGRATION
# Written 2026-10-02 by MTS-2026-10-01-1755Z-DSA-COO.
# Supersedes CLOUD_PROMPT_TWO_CORES_2026-10-01.md for the integration pass.
# Prior readiness + scaffold are on main at 59712b0.

You are a cloud Sonnet session. One task. Checkpoint commits after each wave.
Line 1: session ID MTS-YYYY-MM-DD-HHMMZ-CLD-BLD-two-cores-int
Line 2: usage percent from chat header, or '85 assumed'.

## BUDGET

Never refuse work for budget. Work to completion. If usage is at 95 percent
or above, commit and push immediately, then continue with a commit after
each step. At 1 percent remaining, still work.

## BOOT

- MyTradingSys/system/CLOUD_INBOX.md (all lines).
- CLAUDE.md (full). Hard rules apply.
- MyTradingSys/system/SURFACE_POLICY.md (full).
- MyTradingSys/system/sessions/README.md.
- MyTradingSys/system/sessions/MTS-2026-10-01-1858Z-CLD-BLD-two-cores.md.

Branch: harness assigns claude/<name>. Record as branch_alias.

## READ (paths verified at HEAD)

- MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md
- MyTradingSys/research/_archive/loose_2026-10/TWO_CORES_READINESS_2026-10-01.md
- MyTradingSys/research/_archive/loose_2026-10/TWO_CORES_SCAFFOLD_2026-10-01.md
- MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md
- MyTradingSys/research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md
- MyTradingSys/backtest/layers/alerts/live_runner_cli.py
- MyTradingSys/backtest/layers/fabio/ (list first)
- MyTradingSys/backtest/layers/rsi/ (list first)
- MyTradingSys/execution/auto_trader.py (1-200; note TF_SECONDS at :47)
- MyTradingSys/runtime/math_object_builder.py (380-460; note :399-413)
- scripts/dev/alert_rate_check.py (1-40; note TF_MIN at :23)

## WAVE 1. Readiness top-5 fix pass

One Sonnet subagent. Smallest fix for each. Stage as <file>.new. One-line
acceptance check per fix. Before any .new under */execution/* or
*/layers/alerts/*, append one ownership line to
MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_LOG.md (session ID,
path, expected end). New tests must fail on the pre-change code at least
once. Include the failing run in the fix description.

1. math_object_builder.py:399-413. book_imbalance 0.0 (no data) must not
   count as ask-heavy vs LONG. Live-safety. Stage .new.
2. scripts/dev/alert_rate_check.py:23 (TF_MIN) and
   MyTradingSys/execution/auto_trader.py:47 (TF_SECONDS). Add 3m where
   missing. Confirm 1d is present where the RSI block needs it. Stage
   both .new.
3. MyTradingSys/research/_archive/loose_2026-10/MTS_LAUNCHER_SPEC_2026-10-02.md. Spec for an
   mts.ps1 launcher + status line for live_runner_cli and
   orphan_watchdog_cli. Do not edit scripts/mts.ps1.
4. MyTradingSys/runtime/test_quad_classify.py.new and
   MyTradingSys/runtime/test_regime_classifier.py.new. Fail-first proof.
5. MyTradingSys/tests/java/MarketDataSnapshotTest.java.new (JUnit
   skeleton). Stage only.

Commit checkpoint 1 with trailer. Push.

## WAVE 2. Fabio core compile

One Sonnet subagent. Biggest integration piece.

New directory MyTradingSys/backtest/layers/fabio/v3/ with:
- signals.py   (S1-S9 per FABIO_V3_SPEC section 3, pure functions)
- models.py    (Model A/B/C/D per section 4)
- fill.py      (section 5.1)
- manage.py    (section 5.2)
- costs.py     (section 5.3; import fees from fees.py, B081)
- day_gates.py (section 6)
- engine.py    (run(bars, config) -> verdict + plan)
- __init__.py  (public API)

Every parameter cites FABIO_V3_SPEC section 7.1 (Fabio quote) or is
tagged NS-grid / NS-fixed / SAFETY / SIM.

New directory MyTradingSys/backtest/layers/fabio/tests/ with one test
file per module. Include a signal-level test that fails on a broken copy
once.

New file MyTradingSys/backtest/layers/fabio/README.md: what this core
emits, config keys, runner contract.

Stage everything as .new. Do not touch live_runner_cli.py. Do not wire
the core into auto_trader yet; that is the desktop runbook.

Commit checkpoint 2 with trailer. Push.

## WAVE 3. Consensus writer + RSI observation block

One Sonnet subagent. Two modules.

a. MyTradingSys/backtest/layers/consensus/writer.py
   append_row(snapshot, tom, fabio, rsi) writes one JSONL row to
   Dumps/consensus/consensus_<UTC-date>.jsonl (gitignored). Fields per
   ARCHITECTURE_TWO_CORES section INTEGRATION. Append-only, never edit.
   Never block on IO error; log and return.

b. MyTradingSys/backtest/layers/rsi/observation.py
   read_latest() -> dict keyed by TF {1m,3m,5m,15m,1h,4h,1d} with
   {rsi, ma_sma, ma_ema, support_or_reject, level} from the existing
   rsi_ma_events output. Read-only. No new computations.

c. MyTradingSys/backtest/layers/consensus/README.md: invocation, jsonl
   path, what each core writes.

Commit checkpoint 3 with trailer. Push.

## WAVE 4. Switchability spec (spec only, no code)

One Sonnet subagent. MyTradingSys/research/_archive/loose_2026-10/TWO_CORES_SWITCHABILITY_2026-10-02.md:
- Config block shape: cores {tom: on, fabio: on}; modules {rsi_obs: on,
  consensus: on}. One file, one loader.
- Where it lands: MyTradingSys/runtime/cores_config.json (new).
- auto_trader reads at boot only; live_runner_cli per tick.
- Migration order: (1) core modules land, (2) config + loader, (3)
  live_runner wires Fabio core as a peer, (4) auto_trader routes
  source:fabio-core to the fabio testnet account.
- Backout: flip flag, restart.
- Every claim cites file:line.

Commit checkpoint 4 with trailer. Push.

## STEP 5. DESKTOP RUNBOOK (operator runs; not CC)

Print this section verbatim at the end of the report. It is for the
operator, not you.

1. git fetch; git cherry main <your branch>; resolve any index conflict
   (keep both sides, refresh the # SIZE header in 03_FILE_INDEX.md).
2. .\scripts\Build-Check.ps1 -> STATUS must be PASS.
3. Promote the book_imbalance .new first:
     $b = Get-FileHash MyTradingSys\runtime\math_object_builder.py
     Copy-Item ... math_object_builder.py.pre_bookimbal
     Move-Item math_object_builder.py.new math_object_builder.py
     Get-FileHash math_object_builder.py  (compare hashes)
     git diff --no-index math_object_builder.py.pre_bookimbal math_object_builder.py
4. Run scripts/dev/run_all_tests.py --quick. Report result.
5. Supervisor restarts the runner with the promoted file.
6. Promote the remaining .new files one at a time, each with the same
   four-step proof.
7. Wire the Fabio core into live_runner_cli (supervisor-owned; live path).
8. Route source:fabio-core to the fabio testnet account in auto_trader
   config.
9. Start the loop: .\scripts\core\mode.ps1 -M armed (sanctioned launcher).
10. Watch the first testnet trade; log source (tom | fabio).

## DELIVERABLES

MyTradingSys/system/sessions/<session ID>.md (14 fields, model=see-chat).
MyTradingSys/system/CLOUD_INBOX.md: remove any note addressed to this
  session. Append one line at the end.
MyTradingSys/system/03_FILE_INDEX.md: append one row per new file above.
  Update the # SIZE header at the top to match the new byte count.
MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_INBOX.md: one
  entry (session ID, files staged, migration order summary).

Commit trailer on every commit: MTS-Session: <session ID from line 1>.

## GATES

Run scripts/dev/run_all_tests.py --quick after wave 1 and after wave 2.
Report the result. New tests must fail on pre-change code once.

## CONSTRAINTS

- Read committed refs. No writes to main. No Maven. No LAN. No F drive.
- Live-path files (auto_trader.py, live_runner_cli.py) never edited in
  place. Stage .new only.
- Never read .secrets/, .env, keys. Testnet only.
- Every claim carries file:line or FR-NNN.
- Write unknown where evidence is absent. Never infer a rule.
- No new extractions in this task.
- Stop after wave 4. Print the four-line verify block.

## VERIFY BLOCK (exactly four lines)
TASK: <one line>
DONE: <one line>
VERIFIED: <mechanical | routed | unverifiable-on-this-surface; name it>
MISSED: <anything dropped, or none>

# END
