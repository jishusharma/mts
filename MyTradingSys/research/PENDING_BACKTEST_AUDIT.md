# PENDING - BACKTEST AUDIT + PLANNING DOC
# Written 2026-09-21T12:50Z by MTS-2026-09-21-0729Z close.
# Status: DELIVERED AS DRAFT 2026-09-21 (research/BACKTEST_METHOD_2026-09-21.md, written from excerpts, no commands run).
# SUPERSEDED 2026-10-09 by research/bigtrade_2026-10-09/PLAN.md. Fixed under F-BT-03.

## GOAL

Deliver MyTradingSys/research/BACKTEST_METHOD_2026-09-21.md,
titled "MTS Back Testing with Historical Data".
Planning document only. No code.
After the doc lands, the next session enters live mode (mts-live).

## METHOD

Next session dispatches ONE worker per live_session_protocol R1-R5.

Worker scope:
- MTS files: verdict function, snapshot format, outcome_labels.json,
  math_object_builder.py, outcome_labeler.py, schema_v5.1.0_spec.md.
- Internet research: backtesting methodology. Walk-forward, label
  leakage, look-ahead bias, event-study vs signal-study, multiple
  testing. Source tiers per playbook Part I.

Coordinator duties:
- Run every disk read. Paste excerpts with file path + line range.
- Run web searches on a surface that has the tool, or mark
  UNVERIFIED-WEB if no such surface exists.
- Do not allow the worker to claim any executed command.

Worker output:
- No "checks executed" section.
- Every disk-derived claim tagged "per dispatch excerpt N".
- The word "Confirmed" is forbidden in worker output.

## DELIVERABLE SECTIONS

1. Data inventory. What exists, what is missing, what is usable.
2. Method options. At least two. Cost, evidence quality, limits each.
3. Chosen method. One. Why the other is rejected.
4. Validation gates. Numbers, not adjectives.
5. Known traps. Label leakage, verdict drift, snapshot cadence,
   missing labels, multiple testing.
6. Code spec. Inputs, outputs, files, dry-run command. No code.
7. Open questions for the operator.

## OUT OF SCOPE

- Writing the backtest code. Separate task after doc approval.
- Touching the live loop. No Rule 32 debt from this task.

END