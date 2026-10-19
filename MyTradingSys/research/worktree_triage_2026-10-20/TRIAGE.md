# JIS-NB worktree triage, 2026-10-20 (desk row 20261018-161738)

Method: `sync.py where --all` + `git cherry origin/fast-track` + per-file diff against trunk. Trunk = origin/fast-track 2dbdb81c.

Headline: only ONE tree holds unshipped commits. Every other "UNSHIPPED" flag is uncommitted edits (stale task-json / LAYERS.md / STATUS.md regenerations, scratch files), not commits.

## Trees with unshipped commits
| tree | branch | commits | files | verdict | action |
|---|---|---|---|---|---|
| agent-af8beddd49095a589 | worktree-agent-af8beddd49095a589 | 2 (cb2740af3 Kurisko Quad Rotation module, d53484622 merge) | 13 (quad_rotation.py, stoch_core.py, tests, FORMULAS s24, 3 golden CSVs, LAYERS.md, task json) | SUPERSEDED, partly unique: trunk already has a different implementation (dd001f2a7 "kurisko: causal Quad Rotation layer module"); every shared file differs; only test_stoch_core.py, 3 golden CSVs and the stoch_core split are absent on trunk | KEPT. Owner = kurisko-module agent. Not shipped blindly. If wanted: review the diff against trunk, then `python scripts/dev/sync.py ship` from that tree (expect conflicts in quad_rotation.py/FORMULAS.md: resolve by hand, trunk wins). Otherwise cherry-pick only test_stoch_core.py + goldens |

## Trees with uncommitted changes only (0 unshipped commits) - kept, others' files
| tree | uncommitted | verdict | action |
|---|---|---|---|
| agent-a0f57883f63c890d7, agent-a57561dac40c290b4, agent-af05b772d71edb1cb | LAYERS.md + 1 task json each (wlow-bounce-shadow-emitter, exec-halt-entry-10031, live-loop-one-owner-guard) | SCRATCH (done-marking left by `tasks.py done`, see sync-ship-dirty-layers-md) | keep; owner discards when sure |
| agent-a359277a, a6132a5a, a795b5b9, a90a0f5e | 1 task json each (lc-event-table, fable-h3/h2/h1) | SCRATCH | keep |
| compassionate-herschel-52c7ce, hungry-visvesvaraya-892cea, reader-protocol-g3-b708ef, reverent-wing-466364 | STATUS.md regenerated | SCRATCH (generated file) | keep |
| determined-jones-593ee3 | STATUS.md, qs.txt, scratch_qs.py | SCRATCH | keep |
| qriptal-ledger-53af31, strange-proskuriakova-45c631, upbeat-pasteur-bd60bd | untracked tmp/log files | SCRATCH | keep |
| mts-dsa-jis-nb-1016-0614 | 2 modified | DSA lane, unchecked | keep |
| agent-a9a5adf3, agent-aaa4c1c5 | ignored runtime/wlow_bounce_forward.jsonl | data would be lost | move jsonl to primary Dumps/ first, then retire |

## Clean, 0 unshipped, LANDED (nothing unique)
18 of 20 clean trees were retired (2 remove-failed, locked by a process; retry later) with `sync.py tidy --apply`: agent-a8eee4b2, aa5ed417, ac8b43fc, ae3ed4ae, afb69d20, fabio-transcribe-c09d2b, friendly-tereshkova-a255c3, relaxed-hawking-e5fb45, mts-jis-nb-{cryptocred-htf, dispatcher-t0-precheck, docs-bugs-1018, fable-audit-e4-promotion-variants, g3-pack-code-fixes, planner-1017, planner-2026-10-17, planner-runlanes-1018, planner-sonnet-batch-1018, rv05-h1, tom-direction, weight-field}.

Not touched: live tree, running-session trees, lane trees (mts-app/relay/dsa/...), ci-red-74edd160, trim-super-boot-facts, mts-gemini.
