# CC PROMPT: Fabio v3 core, finish it
# Written 2026-10-02 by MTS-2026-10-01-1755Z-DSA-COO.
# Mode: CC (Claude Cloud, Win app Cloud mode).
# Budget: 99 USD cloud credits (account B, expires 2026-11-05).
# Nomenclature: CC = cloud, CL = local.

You are a CC session. One task: finish Fabio v3 core.
Line 1: session ID MTS-YYYY-MM-DD-HHMMZ-CLD-BLD-fabio-v3-core
Line 2: usage percent, or 'unknown'.

## BUDGET AND PARALLELISM

- Subagent cap: 3 total.
- Batch size: 1. Never more than one subagent running at once.
- Ultracode: OFF. If the harness has it enabled, disable it before
  starting. Parallel subagents burned 85 percent of a budget on
  2026-10-01 and cost two waves of work.
- Commit and push between each subagent return. If the container is
  reclaimed, the last push is the resume point.
- Never refuse work for budget. If credits run out, push what is on
  disk with a WIP tag and stop.

## BOOT

- MyTradingSys/system/CLOUD_INBOX.md (all lines).
- CLAUDE.md (full). Hard rules apply.
- MyTradingSys/system/SURFACE_POLICY.md (full).
- MyTradingSys/system/sessions/README.md.
- MyTradingSys/system/sessions/MTS-2026-10-01-1916Z-CLD-BLD-two-cores-int.md.

## READ (verified at HEAD)

- MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md (full; sections 3, 4, 5, 7.1, 10, 11 are load-bearing).
- MyTradingSys/research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md.
- MyTradingSys/research/_archive/loose_2026-10/TWO_CORES_SCAFFOLD_2026-10-01.md sections 1-2.
- MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md.
- MyTradingSys/backtest/layers/fabio/v3/*.py.new (7 files, all staged).
- MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py.
- MyTradingSys/backtest/layers/FORMULAS.md.
- MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py (for cost and fill conventions).

## CURRENT STATE

Seven of ten modules staged under fabio/v3/. They are UNREVIEWED.

Present: signals.py, models.py, fill.py, manage.py, costs.py,
day_gates.py, __init__.py.

Missing entirely: engine.py, tests/, README.md.

The core cannot be invoked. That is the gap this session closes.

## WAVE 1. Review staged modules (1 subagent)

Brief 20 lines or fewer. Read each staged file against its spec
section. Return a table only:

| file | matches spec section | file:line gaps | status OK/FIX |

Do not edit yet. Report only. A review result that says "all OK" for
every row with no file:line cites is a red flag; require cites.

Commit a REVIEW file at MyTradingSys/research/FABIO_V3_REVIEW_<date>.md
with the table. Push.

## WAVE 2. engine.py (1 subagent)

Compose MyTradingSys/backtest/layers/fabio/v3/engine.py.new.

Public API:
  run(bars, config) -> {verdict, model, side, entry, stop, target,
                        management, diagnostics}

verdict vocabulary is an engine convention mirroring FABIO_V3_SPEC
state names. Section 4 defines model A/B/C/D. Config keys come from
section 7.1. No defaults; grid params (NS-grid) are REQUIRED config.

Imports: stdlib plus fabio/v3 siblings plus orderflow_bars plus
fees (B081). No imports from execution/ or layers/alerts/.

Every decision cites a spec section as a comment at the line.
Write "unknown" where the spec is silent.

Stage as engine.py.new. Commit and push.

## WAVE 3. Tests (1 subagent)

Compose MyTradingSys/backtest/layers/fabio/v3/tests/ with one test
file per module:

  test_signals.py.new
  test_models.py.new
  test_fill.py.new
  test_manage.py.new
  test_costs.py.new
  test_day_gates.py.new
  test_engine.py.new

Requirements:
- Hand-built bars, no external data.
- Each test file fails on a deliberately broken copy of its module
  at least once. Show the failing run per file.
- Test names describe the spec rule being checked.
- No mocks of the module under test.

Also: review pending_test_fabio_v3.py. Report what still applies to
v3 and what is stale. Do not modify it.

Commit and push.

## WAVE 4. README (1 subagent)

Compose MyTradingSys/backtest/layers/fabio/README.md.new:
- What this core emits.
- Config keys and required grid params.
- Runner contract: how live_runner_cli or a backtest invokes it.
- What is NOT wired: no live trade path yet. That is the desktop
  runbook's job (see TWO_CORES_SWITCHABILITY_2026-10-02.md).
- Every claim cites file:line.

Commit and push.

## DELIVERABLES

MyTradingSys/research/FABIO_V3_REVIEW_<YYYY-MM-DD>.md
MyTradingSys/backtest/layers/fabio/v3/engine.py.new
MyTradingSys/backtest/layers/fabio/v3/tests/*.py.new (7 files)
MyTradingSys/backtest/layers/fabio/README.md.new
MyTradingSys/system/sessions/<session ID>.md (14 fields, model=see-chat)
MyTradingSys/system/CLOUD_INBOX.md (remove any note for this session; append one line)
MyTradingSys/system/03_FILE_INDEX.md (one row per new file; refresh the # SIZE header)
MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_INBOX.md (one entry)

## CONSTRAINTS

- Read committed refs. No writes to main. No Maven. No LAN. No F drive.
- Live-path files (execution/*, layers/alerts/*) never edited. Fabio
  core is under backtest/.
- Never read .secrets/, .env, keys.
- Every claim carries file:line or FR-NNN.
- Write unknown where evidence is absent. Never infer a rule.
- No new extractions in this task.
- Staged .new throughout. No promotion; that is desktop.
- Stop after wave 4. Print the four-line verify block.

## VERIFY BLOCK
TASK: <one line>
DONE: <one line>
VERIFIED: <mechanical | routed | unverifiable-on-this-surface; name it>
MISSED: <anything dropped, or none>

# END
