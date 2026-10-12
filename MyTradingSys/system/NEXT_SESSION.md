<!-- relay: go depth=64 id=84ae28de -->
# NEXT SESSION PROMPT (handoff 2026-10-11, Opus operator session "Tom/Fabio transfer probe"; Claude Code Win App, either account; older text below is history)

ONE-MESSAGE RULE (operator 2026-10-10, standard practice): the block below must run with no input from the operator. Every open question carries a default; the session answers itself from Control Room (ArtifactData) and acts. Overwrite this file at each handoff.
PARALLEL (2026-10-12): `sync.py start` prints `WORKTREE: <path>` when the tree is shared/dirty: work only there. `sync.py health` lists collisions. A NEXT_SESSION.md merge collision resolves to origin's text: re-apply your edit.
DIRECTION (operator 2026-10-11): redefine the Tom and Fabio layers completely from today's findings. Road map, STOP list and session plan:
`MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md` (read it before Q1). Do NOT backtest or tune the current Tom/Fabio encoding on BTC.

```
MTS builder session. Read CLAUDE.md, STATUS.md (regenerate first), research/tom_transfer_2026-10-11/ROADMAP.md, then State below.
0. `python scripts/dev/sync.py start`, `sync.py where`, `desk.py list --all`. Push fails: say so in one line, stop.
   Read STATUS.md "Daily Hygiene": a RED there is fixed before new work. One task per session; hand off after the task,
   5 operator turns or 15 tool turns: ship, overwrite this file, `where` clean.
1. Control Room (url in CONTROL_ROOM.md): ArtifactData query decisions + feedback. Apply answered decisions with no `applied`;
   a new unanswered decision: act on its `recommended` option only when older than 24 h.
3. TASK: pick with `python scripts/dev/tasks.py next` (priority order, skips claimed). Q3 (Fabio ledger, one 250 s video window per session) is a background lane: take it ONLY when no p1/p2 SONNET card is ready, otherwise it starves every other task (found 2026-10-11). Q19-Q25 below are the Inbox cards. Its card is the whole brief:
   `python scripts/dev/tasks.py brief <card>` -> `sync.py claim` -> work -> `tasks.py done <card> --result "<number/file>"` -> ship -> release.
   Q4. OPUS (relay skips; operator names Opus) Cards tom-layer-v2-spec (part A: families + sourced rules) then tom-layer-v2-cost (part B: per-market proofs/cost, BTC stop-width transfer rule, Sonnet build cards). OPUS, approved by the operator 2026-10-11, size M each = one card per session; both need Q2. DONE when: TOM_LAYER_V2_SPEC.md parts A and B + Sonnet build cards.
   Q5. OPUS (relay skips; operator names Opus) Cards fabio-layer-v2-spec (part A) then fabio-layer-v2-markets (part B: NQ vs BTC data plan, cost, recall-harness + encode cards). OPUS, approved, size M each; both need Q3. DONE when: FABIO_LAYER_V2_SPEC.md parts A and B + cards.
   Q6. (after Q4 part B) Card tom-encode-spike-fade (Sonnet; needs Q1 + tom-layer-v2-cost). DONE when: RECALL_DAX_V2.md shows recall >= 4/7 (or the honest miss), flag-off BTC output identical.
   Q7. (after Q6) Card tom-dax-backtest (run; needs Q6): `tom_dax_bt.py all --shifts 0,1,2,3`, then `report --read-holdout --shifts 0,1,2,3` once. DONE when: DAX_BT_REPORT.md has dev + holdout rows and the branch named.
   Q8. (after Q7 + Q4 part B) Card tom-probe-prereg (M arms only, needs tom-dax-backtest + tom-layer-v2-cost). DONE when: card done_when holds.
   Q18. (after Q3; same video as Q3, covered there; skip unless Q3 is DONE) card find-more-fabio-trade-recap-videos-yt-dl, ONE video only: Is1HvdfQm5c. DONE when: its ledger rows with frame files are in FABIO_TRADE_LEDGER.csv (or a per-video line saying none shown).
   Q26. host=JIS-NB (after JIS-NB releases its claim, 15h old 2026-10-12) Card tom-holdout-clean-split (Sonnet, p1; C-Cloud N1/N2). DONE when: HOLDOUT_CLEAN.json + dated PRE_REG_DAX.md addendum (ledger days dropped from the DAX holdout, forward holdout from 2026-10-10, design/check split of the ledger) committed BEFORE any encode. Dates only, no outcome reads.
   Q29. host=JIS-NB Card fabio-ledger-minute-timestamps (Sonnet, p2; N4 iii; JIS-NB only. Tried on JIS-NUC 2026-10-12: videos and old sheets ARE on F: there, but its python has no cv2/ffmpeg/PIL, so no full-res frame can be cut; the 960x540 sheet cells show minutes at best and no date. Same block for Q3/Q18 video windows on JIS-NUC). DONE when: ledger rows carry entry_time_utc read from frame clocks, replay-ready count in the .md.
   Q30. (after tom-layer-v2-cost, fabio-layer-v2-markets, Q28) Cards cryptocred-home-fit-audit, malkan-home-fit-audit, positioning-home-fit-audit (Sonnet, p4). CryptoCred first. No backtests.
   Q31. host=JIS-NB (Sonnet, p1; card relay-two-host-standby, NB half): add `--peer-quiet-min 90` to the kick line of the mts-dispatcher prompts on JIS-NB and update the JIS-NB row in scripts/sched/relay_prompts/TWO_HOST.md. DONE when: a JIS-NB dispatcher tick prints `IDLE peer JIS-NUC` or KICK, and relay_runs.jsonl has a JIS-NB row.
   Q34. SKIPPED: Q33 (2026-10-12, research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md) found no surviving cell: no combination survived. Do not wire cross-guidance. Q33b (only if the operator asks) = same catalogue with OI / long-short / funding filters (needs data.binance.vision metrics fetch) and 1m detection with stops, maker entry. DONE when: skipped, nothing to build.
   Q35. DONE 2026-10-12 (both cards ready; build them as b172-template then b172-trim). (Sonnet, p2, any host) Refine raw cards b172-trim and b172-template from research/TOKEN_AUDIT_2026-10-12.md ranked cuts (TASK_REFINEMENT.md); name before/after metrics (cache-read tokens per kick session, ritual turns 21 -> <=12). DONE when: both cards state=ready with done_when and tests named.
   Q36. DONE 2026-10-12 (Sonnet, p2, any host) DSA registry step for commit d9306fe (host= task tag in relay lint/kick): one line in research/apparatus_fixes.md and an append-only entry in system/02c_SESSION_END_SIGNOFF.md, both quoting the hash and the 29 green relay tests. DONE when: both lines are on origin.
   Q37. host=JIS-NB (Sonnet, p2) Left-overs of Q19-Q25: republish the JIS-NB account Control Room page (layout v5), put the Q25 deck link https://claude.ai/artifact/2DXWotLraL8te3xNqo4hWV on Inbox item ggw2vehlbhdnlc4uhd1w, re-run install_backup_task.ps1 and register_cicd_tasks.ps1 in a window (no live-path restart), re-time the quick gate cold. DONE when: each of the four has a one-line result in items/B177.md or DEPLOY_RUNBOOK.md.
   Q38. host=JIS-NUC (after claim non-tom-fabio-layer-evidence-audit is released) Ship the 21 staged files left in F:/MTS/mts-codex (branch nuc/codex-holdout, research/non_core_layer_audit_2026-10-12/, plus untracked tmp/): commit with Result line, `sync.py ship`; do not delete tmp/ unread. DONE when: that directory is on origin/fast-track and `sync.py where` shows mts-codex ok.
   Q39. (Sonnet, p1, any host) Tom ledger audit, ONE card per session, card tom-ledger-canonical-identities DONE 2026-10-12 (already repaired in 2868d6c); tom-ledger-time-provenance DONE 2026-10-12; next card: tom-ledger-instrument-identity (the others, tom-ledger-management-provenance, follow via tasks.py next). DONE when: the card's done_when holds and tasks.py done recorded.
   Q40. DONE 2026-10-12 (cannot pin from code; cause = launch-time App default, see check file). (Sonnet, p2, any host) Pin the dispatcher model: research/DISPATCHER_MODEL_CHECK_2026-10-12.md shows `model: sonnet` frontmatter was NOT honored in 6 of 20 dispatcher runs (Opus). Find the cause (fallback after a Sonnet limit, or the task's own setting) and a pin that holds; check the next two ticks' transcripts. DONE when: the check file has cause + fix + two later runs on Sonnet, or the honest "cannot pin" with the cost estimate.
   Q41. (Sonnet, p4, any host, low priority) Zero-cost idle ticks: a Windows Task Scheduler job runs relay.py kick every 30 min with no model; only on KICK does it wake the App dispatcher. B164 risk (unattended launch needs a click) must be tested, not assumed. DONE when: DEPLOY_RUNBOOK.md has the design, the measured idle-tick cost and the B164 test result.
   Q42. (Sonnet, p4, any host) Refresh the layer map: `python scripts/dev/make_layer_map.py`, add one row to MyTradingSys/system/layer_map.json for each report listed under Freshness that is a real backtest, republish https://claude.ai/artifact/QwsvsN3LaZKNPvD6zPTTAe. DONE when: the Freshness tab lists no real backtest report as unindexed and the artifact shows the new version. Also run `python scripts/dev/make_layers_md.py` (refreshes LAYERS.md, the per-layer index linked from CLAUDE.md).
   Q43. host=JIS-NB (Sonnet, p3) Worktree cleanup, same rules as JIS-NUC 2026-10-12: from a work tree (never the live tree) run `python scripts/dev/sync.py tidy --all` (dry run), read the list, then `sync.py tidy --all --apply`. It removes only worktrees that are clean and fully on origin/fast-track (not the main tree, not the one you stand in); it always keeps the fixed lanes (mts-push, mts-refiner, mts-codex-lab, mts-relay, mts-dsa, mts-codex), anything dirty or with unshipped commits, and the main tree. List what it kept and why (dirty: say what is in it), `git worktree prune`. DONE when: `sync.py where` shows no `ok` session worktree left that `tidy` would remove, and the count removed/kept is one line in this card's result.
   ORDER (C-Cloud research 2026-10-11, BACKTEST_FAILURES_RESEARCH.md): Q26 and Q27 BEFORE tom-layer-v2-cost (Q4 part B) and tom-encode-spike-fade (Q6); Q29 before fabio-layer-v2-markets (Q5 part B). Q6/Q7 pass bar = recall AND fire rate on the held-back CHECK set; DAX holdout excludes ledger days.
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

Older updates: `handoff_history/` beside this file (read only when a task points there).

## Tom ledger repair handoff (2026-10-12, JIS-NUC)
- DONE: tom-ledger-canonical-identities / -instrument-identity / -time-provenance / -management-provenance (12 candidate groups, not certified executions; T5 FDXM vs FDAX and T11 31.08 vs 01-Sep left UNRESOLVED).
- tom-layer-v2-spec released to `refined`; NOT started (Opus only when Jis asks). tom-layer-v2-cost still waits on tom-holdout-clean-split and tom-profile-parity-check.
- Pass `TOM_LEDGER_CANONICAL_GROUPS.csv` (prior exposure) to the tom-holdout-clean-split owner; the split manifest was not touched.

## Fabio ledger audit handoff (2026-10-12, JIS-NUC, Sonnet)
- DONE: lab-audit-fabio-ledger-frames. FIX-FIRST: 72 rows, 3 HIGH (date "2026" contradicts contract NQ-202512; 4 entries disagree with STP labels; F13 outcome -2910 vs stop -1760), 4 MED. Report: research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md. Rows not named in it were checked on arithmetic/provenance only, not frame by frame.
- 3 repair cards created (Sonnet): date-unknown, entry-from-stop-label, F13 outcome. fabio-layer-v2-spec/markets wait on them (Opus only when Jis asks).
- Q29 (fabio-ledger-minute-timestamps) should absorb M4; it needs F: (JIS-NB or JIS-NUC, F: is present on JIS-NUC as of this audit).

## Layer map handoff (2026-10-12, JIS-NUC, Sonnet)
- DONE: layer-backtest-map-artifact. Generator `scripts/dev/make_layer_map.py` + data `system/layer_map.json` + `scripts/dev/layer_map.tpl.html` -> `system/artifacts/layer_map.html`; published https://claude.ai/artifact/QwsvsN3LaZKNPvD6zPTTAe (20 backtests, 21 layers). Cannot run backtests; configurator only writes a Qn card.
- Gaps: only Tom core and Fabio v3 keep per-variant rows; 6 rows were read at header depth only (verdict not read). Q42 refreshes it.


## Layer index (2026-10-12, thread "Tom/Fabio layer visibility")
- DONE: `system/LAYERS.md` (generated by `make_layers_md.py` from `layer_index.json` + `layer_map.json` + cards + lab reports), linked from CLAUDE.md and LAYER_LAB.md; gate step 3ly. Task cards carry `layers` (`tasks.py new --layer <family>`, 25 open cards backfilled; briefs point at the section); tasks.py regenerates the page on every card change. `shot.py done --outcome finding:card:<id>` files a live-read finding as a card (was the old Q43 and Q46).
- Dropped Q44: per-backtest layer lists already live in layer_map.json `backtests[].layers` and now render per family; a TRIAL_REGISTRY column would duplicate them.
- Held: Q45 below (move research/ files only while the Codex track is idle).

## Queued layer-structure cards (2026-10-12, not yet in the block; add when a slot opens)
- Q45. (Sonnet, p4, HOLD until the Codex track is idle: check `codex_run.py status` and `sync.py health`) research/ root holds ~190 flat files: move dated one-offs of each layer family into research/<family>/ and leave a one-line pointer stub at the old path; update layer_index.json and 03_FILE_INDEX.md. DONE when: tests/test_layers_index.py green, grep finds no dead link to a moved file.
