# MTS critical-path review, 2026-11-03

Review snapshot: origin/fast-track `5fb3ce500`; observations below are repository evidence, not live engine status. Prepared by Sol under the operator's end-to-end MTS instruction. Claude review requested; this document is not a signed stage exit or a new rule.

## Where we are

| Measure | This checkout | Evidence and limit |
|---|---:|---|
| Roadmap stage | S0 | `research/v1_plan_2026-10-20/D7_ROADMAP.md`, `Now:` line. Today's amendments lift parking and the ready-card cap; the older ANNOUNCEMENTS S0 entry still quotes that cap. Do not reimpose the superseded parking rule. |
| Promoted configurations | 0 | `execution/promoted_setups.json`: `entries=[]`. This is a register count, not an independent audit of every result. |
| Top-level task states | 729 done, 130 refined, 142 dropped, 28 ready, 30 blocked, 15 raw | JSON files directly in `system/tasks/`, excluding archive. Ready lanes: SONNET 12, JIS-NB 7, HAIKU 4, CODEX 4, OPUS 1. A ready state alone does not mean unclaimed or runnable. |
| Verdict register | 118 rows | `research/VERDICTS.csv`: FAIL 55, INCONCLUSIVE 40, UNPARSED 13, BLOCKED 8, PASS 2. Rows are arms, not 118 independent setups. |
| Published claims | 40 | `sync.open_claims(Path.cwd())` at this snapshot. Includes old legacy claims; not a count of 40 active workers. Start output shows many STALE entries. Foreign ownership needs reconciliation, not blanket release. |
| Registered worktrees on this machine | 57 | `git worktree list --porcelain`, count of `worktree ` records. Includes permanent, foreign and active trees; not 57 safely removable directories. |
| STATUS freshness | Stale | `research/STATUS.md` generated 2026-10-30. Its CI, budgets, ready counts and live information cannot establish today's state. |

Reproduction: Python `Counter` over each top-level task's `state`, and `lane` for state `ready`; `csv.DictReader` over VERDICTS grouped by `verdict`; count git worktree porcelain records. Counts are a snapshot and will move while workers claim and ship.

## Critical work now, in order

1. Independently attack the research method. Fresh Luna chat is assigned `mts-audit-1103-independent-recheck`, after current claim checks. It must implement its own entry/stop/walk loop, use causal pivots and next-bar orders, enforce the DEV file cutoff before loading, and prove sections 1 and 3-7 separately. Sol reviews source and evidence. Until then the producer's Pitchfork EXACT result is a producer claim, not independently reproduced here.
2. Close the probability experiment without falsifying accounting. Existing clean tree `F:/MTS/mts-jis-nuc-codex-prob-table-1103` contains four unshipped commits through `205876397`; the seven targeted tests pass and the four arms remain KILL after the excluded-month loader fix. `tasks.py done` requires an official run receipt that interactive execution did not produce. A separate fresh Luna diagnostic is checking current tracked workflow and asking Claude for a legitimate closure path. No fabricated receipt, environment bypass, guard edit or redundant experiment for accounting. Preserve this tree until shipped.
3. Finish evidence-backed hygiene. Completed chats may be archived without deleting their outputs or commits. Remove only this work's completed disposable trees after ship proof, claim release, and hash-preservation of valuable ignored files. Other-session or unshipped trees remain protected. The fleet-wide 8-tree exit requires the owning stations, not unilateral deletion here.
4. Claude to review the existing research PASS guard card and take or delegate it: `research-pass-needs-rerun-gate` is ready SONNET and unmodified by this reviewer. Its current steps cover a register row but not the whole D7 condition (causal replay and independent trade-loop rerun). Review the coverage gap before treating that test as enforcing the complete PASS rule. Existing known-offender allowances must not silently certify evidence.
5. Advance existing funnel work only with a clear gate and a free slot. `lc-validation` and `rsi-deep-run-dev` remain refined; no sealed read is authorized by this review. Claude should reconcile their current dependencies and choose the next eligible study, preserving WIP=2. Do not restart already failed arms without a new reason on their card.

## S3 evidence disposition

| Roadmap item | Current card/evidence | Next action |
|---|---|---|
| Meta-label 1h | done, extension FAIL; n303, mean -0.199%, CI -0.411..-0.017 | Keep failed encoding closed. |
| Fabio C stand-in | done, saved-file verdict recheck shipped (`dc8e33291`, merged `da4654566`) | Frozen PASS stands only as pre-DEV hypothesis. Keep setup parked; no promotion. |
| LC validation | refined, result empty | Owner to establish frozen rule, base trust and one-read eligibility before execution. |
| CryptoCred 4h/1d | done with prereg power BLOCKED, n207 and MDE+cost above 0.30R | No outcome read or PASS inferred. |
| RSI deep-buy DEV | refined, result empty | Owner checks prerequisites before run. |
| Tom v2 gross-first | done, FAIL, placebo difference CI crosses zero | No repeat without a new reason. |
| Reclaim close-stop | done, 4h n114 and 1D n13 INCONCLUSIVE; validation unread | Preserve scope; inconclusive is not a promotion. |

## Sol review of the shipped meta-label recheck

Read `layer_lab/meta_label_recheck_1103/RECHECK.md`, the frozen `meta_label_dev_ext_2026-10-31/PRE_REG_EXT.md` and saved `numbers.json`. Independently evaluated the Boolean decision: n_top=139 is not below 100; top mean=0.4296087377R; 95% CI lower=0.0284020010R; spread=0.6447628513R exceeds placebo p95=0.5214348375R. The conditional insufficient-power clause requires a CI spanning zero, which is false. Thus literal PASS STANDS agrees with the frozen rule despite n139 below the realized floor401.

Independent arithmetic: conservative m=2 adjustment `2*(7/301)=0.0465116279`; using the saved delta_min, `ceil(139*(0.5092890999/0.30)^2)=401`; using prior sd2.3817, `ceil(7.849*(2.3817/0.30)^2)=495`. The exact extension-window second family p-value is not saved, so the adjusted value is conservative, not a newly observed exact BH family q. The 97.5% interval crosses zero. This review does not replicate the trade generator or justify changing the parked action.

## Claude review requested

Please review this priority order, the meta-label scope, the legitimate probability receipt closure, and PASS-guard coverage. Reconcile the superseded ANNOUNCEMENTS cap against D7 without growing machinery. Route any reassigned implementation through a claimed card. Live engine state, uptime, HALT/restart drills and operator signatures are NOT_IN_DATA in this review; no station budget is used to infer Codex capacity.
