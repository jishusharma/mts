# B090 - cloud credit approval plan (two buckets)

Status: OPEN. Severity: HIGH. Opened 2026-10-03.

## Defect

Cloud credit on the awgp account, ~$100, expires 2026-11-05 (corrected 2026-10-03 12:35Z).
The 2026-10-03 roadmap proposes eight items C1-C8. Two of them
(C2, C6) point at sources cloud cannot reach: gitignored runtime
data and F:\ filesystem data. Two more (C3, C5) can write but not
promote. Without a precondition step per item, roughly $32 of the
planned $90 cannot run on cloud as written.

An approval plan was prepared this session. It splits spend into
two buckets and names the precondition per contingent item.

## Evidence (revalidated 2026-10-03)

Paths verified 2026-10-04; committed at a8b8fcf:
  research/_archive/loose_2026-10/REVALIDATION_ACTIONS_2026-10-01.md                       270 lines
  research/_archive/loose_2026-10/TWO_CORES_READINESS_2026-10-01.md                         63 lines
  research/fast_track_2026-09-27/MAINTAINER_REPORT_2026-09-29.md
  research/fast_track_2026-09-27/MAINTAINER_REPORT_2026-09-30.md
  research/_archive/loose_2026-10/W3_KAPPA_REPORT_2026-10-01.md                            147 lines
  Fabio v3 tree, 14 files, plus pending_test_fabio_v3.py
  T054, T055, T058, T060, T061 item docs

Gitignored (cloud cannot see):
  MyTradingSys/execution/auto_trades.jsonl
  MyTradingSys/execution/trade_ledger.jsonl
  MyTradingSys/runtime/alerts/1m.jsonl
  MyTradingSys/execution/plans/*.json

Not on any commit (cloud cannot reach):
  F:\MTS\data\orderflow_1m
  F:\MTS\data\tom_bt

Inconsistency to name for the fixer:
  .gitignore line 4 is *.new; four tracked .new files
  (rsi/observation.py.new, consensus/writer.py.new and their
  tests) are on origin. Ignore rule does not affect
  already-tracked files; the rule and the tracking disagree.

Cloud reach, exact quote:
  MyTradingSys/system/SURFACE_POLICY.md line 17:
  "CLD cloud (free pool) | pushed git refs only; no LAN,
   no gitignored files | offline research, specs, reviews,
   docs, backtests on committed data"

## The plan (two buckets)

BUCKET A - $50 / 50 percent - run today on cloud

  A1. C1 audit-reconcile.  Est $8.
  A2. C8 second-reader.    Est $6.
  A3. C4 fabio-v3.         Est $15.
  A4. C7 research-pack.    Est $15.
  Subtotal $44. Buffer $6 for overrun.

BUCKET B - $49 / 49 percent - contingent on one desktop step each

  B1. C2 no-trade-funnel.  Est $10.
      Precondition: desktop commits a sanitized dump at
      MyTradingSys/research/funnel_input_2026-10-03.jsonl.
  B2. C3 w1-review.        Est $12.
      Precondition: none, but promotion stays local per
      CLAUDE.md staging rule.
  B3. C5 bug-batch.        Est $12.
      Precondition: operator confirms cloud writes .new only.
  B4. C6 backtest-dsr.     Est $12.
      Precondition: a committed 30-day corpus slice, or move
      C6 to local.
  Subtotal $46. Buffer $3.

RESERVE - $1 unspent.

## Fix

Claude approves, amends, or rejects each bucket. Operator runs
Bucket A items today, one session each, cap 3 subagents, commit
and push between batches. Bucket B stays reserved until its
precondition is met.

## Receipt
2026-10-03 12:35Z: expiry claim corrected. Cloud session credits 99 of 100 USD,
Expires 1:29 PM GMT+5:30, November 5. Roadmap header 'expires today' was
wrong. Pro weekly pool resets Sun 22:30, session limit 0%. Urgency removed;
Bucket A and B can be sequenced over the next 33 days.
# END
