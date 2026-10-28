# Reusable lab: implementation and pilot result

RESULT (2026-10-16, JIS-NUC): ordered Sol -> Astra plumbing pilot PASS; Claude review PENDING on provider allowance.

Delivered: `system/LAB_RECIPES.md` and `scripts/dev/lab_flow.py` add critical-audit, build-review and run-review
recipes on the existing CODEX lane. Each stage retains the same goal/criteria, a distinct lens and a fixed model
setting. A PASS receipt with criterion results and source/report hashes unlocks the next stage. Goal, scope,
lens or model drift, missing receipts, changed evidence, REWORK and BLOCKED all stop advancement.
Runner-side validation also rejects a hand-edited done flag or an observed effective-model mismatch.

Economy: recipe packs use source indexes and predecessor pointers, without repeated boot/source dumps.
For the pilot card the pack measured 13,837 bytes with the legacy renderer versus 2,270 bytes with the recipe
renderer (83.6% smaller). This measures the initial pack, not total session token savings. Recipe cards bypass
old lab-share/count caps; real allowance headroom, the lock and failure cooldown remain. Ordinary cards keep
their prior behavior. The current Astra-low policy remains until a task-based evaluation justifies changing it.

## Executed model stages

| Stage | Effective model / effort | Acceptance | Seconds | Total tokens | Cached input | Uncached input | Output |
|---|---|---|---:|---:|---:|---:|---:|
| recipe-pilot-1-map | gpt-6.1-sol / medium | C1 PASS, C2 PASS | 73 | 271,628 | 217,600 | 51,997 | 2,031 |
| recipe-pilot-2-challenge | gpt-6-astra / low | C1 PASS, C2 PASS | 115 | 439,278 | 397,440 | 39,232 | 2,606 |
| Total | | | 188 | 710,906 | 615,040 | 91,229 | 4,637 |

Source: the runner's complete JSON rows in local `CODEX_HOME/lab_runs/runs.jsonl`, matched by these exact card ids;
effective models were checked against their CLI headers. Allowance readings moved 13 window points and 2 week
points combined; concurrent account sessions can affect these readings, so they are not an isolated cost attribution.
This table excludes the coordinating Codex session, deterministic tests and shipping time. No API-dollar estimate
is inferred from subscription tokens.

Reports: [Sol evidence map](2026-10-16_recipe-pilot-1-map.md),
[Astra independent challenge](2026-10-16_recipe-pilot-2-challenge.md).
Both original reports say FIX-FIRST because the fixture deliberately contains bad claims; both stage criteria
PASS because the required deliverable is detection of those claims. Acceptance does not label a strategy sound.

Codex independently checked the original observations: 10 + 11 + 9 = 30, mean 10; both model reports catch the
seeded sum 31 and mark the missing fee-net claim NOT_IN_DATA. Verified both stored receipts against current
source/report hashes with `lab_flow.accepted`: True for each. Astra's command log records its independent
calculation before reading the predecessor report. Both cards reached done, shipped and released their claims.

## Verification and limits

- Full offline suite: all 58 steps PASS, including Maven and backtest tests. Later goal/model-drift hardening:
  focused final suite 104 tests PASS, 232 subtests; its ship gate also passed. Sixteen tests cover the new flow
  behavior. Pre-change failures were observed for missing flow support, share-cap optimization, compact packs,
  a forged done flag and current-card goal drift.
- Real pilot: critical-audit only. Build-review/run-review are template-validated and covered by shared plumbing;
  their full real workloads were not exercised here.
- The fixture exposes expected answers and is not a blind quality benchmark. This proves sequence, evidence
  handoffs and missing-data handling, not research alpha or a general benefit from multi-model consensus.
- Reports' criterion statuses remain model attestations; source hashes prove identity, not truth. Claude's
  independent spot-check remains a required separate observation.
- Both models read the unrelated LAYERS catalogue. Updated LAYER_LAB.md to request named sections only for
  cards with a nonempty layers field, and avoid rereading utility implementations during ordinary use.
  This additional economy change is guidance; its token impact has not yet been measured.

## Claude attempt and next action

Explained the design and sent a headless, read-only Sonnet review prompt (no UI control). Provider response:
HTTP 429, `usage_limit_reached`, reset 2026-10-16 **14:30 IST**; zero model tokens consumed. No Claude verdict
was obtained. The exact fallback prompt/argv is in `system/cli_tasks/2026-10-16_claude-recipe-pilot.md`.

Desk request `20261016-065707-reusable-lab-recipes-claude-pilot` targets CLAUDE and is shipped. Its self-contained
handoff is `research/layer_lab/CLAUDE_RECIPE_PILOT_HANDOFF.md`: inspect code, run the focused tests, recompute one
claim/hash and file the Claude review. No operator input or relaunch of accepted model stages is needed.

After that review, the useful next pilot is one already-completed offline MTS report whose consequential numeric
or source claims can be independently reproduced, rather than another synthetic calculation or a new market trial.
Use the cheap deterministic pass first and reserve Sol/Astra filtering for findings that could change a decision.
