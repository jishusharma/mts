<!-- relay: go depth=50 id=2015094a -->
# NEXT SESSION PROMPT (handoff 2026-10-11, Opus operator session "Tom/Fabio transfer probe"; Claude Code Win App, either account; older text below is history)

ONE-MESSAGE RULE (operator 2026-10-10, standard practice): the block below must run with no input from the operator. Every open question carries a default; the session answers itself from Control Room (ArtifactData) and acts. Overwrite this file at each handoff.
DIRECTION (operator 2026-10-11): redefine the Tom and Fabio layers completely from today's findings. Road map, STOP list and session plan:
`MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md` (read it before Q1). Do NOT backtest or tune the current Tom/Fabio encoding on BTC.

```
MTS builder session. Read CLAUDE.md, STATUS.md (regenerate first), research/tom_transfer_2026-10-11/ROADMAP.md, then State below.
0. `python scripts/dev/sync.py start`, `sync.py where`, `desk.py list --all`. Push fails: say so in one line, stop.
   Read STATUS.md "Daily Hygiene": a RED there is fixed before new work. One task per session; hand off after the task,
   5 operator turns or ~50k tokens: ship, overwrite this file, `where` clean.
1. Control Room (url in CONTROL_ROOM.md): ArtifactData query decisions + feedback. Apply answered decisions with no `applied`;
   a new unanswered decision: act on its `recommended` option only when older than 24 h.
   every weekday fetched; snapshot check MATCH. Nothing to do here.
3. TASK: pick with `python scripts/dev/tasks.py next` (priority order, skips claimed). Q3 (Fabio ledger, one 250 s video window per session) is a background lane: take it ONLY when no p1/p2 SONNET card is ready, otherwise it starves every other task (found 2026-10-11). Q19-Q25 below are the Inbox cards. Its card is the whole brief:
   `python scripts/dev/tasks.py brief <card>` -> `sync.py claim` -> work -> `tasks.py done <card> --result "<number/file>"` -> ship -> release.
   Q4. Cards tom-layer-v2-spec (part A: families + sourced rules) then tom-layer-v2-cost (part B: per-market proofs/cost, BTC stop-width transfer rule, Sonnet build cards). OPUS, approved by the operator 2026-10-11, size M each = one card per session; both need Q2. DONE when: TOM_LAYER_V2_SPEC.md parts A and B + Sonnet build cards.
   Q5. Cards fabio-layer-v2-spec (part A) then fabio-layer-v2-markets (part B: NQ vs BTC data plan, cost, recall-harness + encode cards). OPUS, approved, size M each; both need Q3. DONE when: FABIO_LAYER_V2_SPEC.md parts A and B + cards.
   Q6. Card tom-encode-spike-fade (Sonnet; needs Q1 + tom-layer-v2-cost). DONE when: RECALL_DAX_V2.md shows recall >= 4/7 (or the honest miss), flag-off BTC output identical.
   Q7. Card tom-dax-backtest (run; needs Q6): `tom_dax_bt.py all --shifts 0,1,2,3`, then `report --read-holdout --shifts 0,1,2,3` once. DONE when: DAX_BT_REPORT.md has dev + holdout rows and the branch named.
   Q8. Card tom-probe-prereg (M arms only, needs tom-dax-backtest + tom-layer-v2-cost). DONE when: card done_when holds.
   Q18. (same video as Q3, covered there; skip unless Q3 is DONE) card find-more-fabio-trade-recap-videos-yt-dl, ONE video only: Is1HvdfQm5c. DONE when: its ledger rows with frame files are in FABIO_TRADE_LEDGER.csv (or a per-video line saying none shown).
   Q19. Card b181-control-room-show-status-reply-ref- (Sonnet, p1; card READY 2026-10-12; republish needs the page owner account). DONE when: a rebuilt page shows status + reply + ref for an Inbox item that has no ref, test_make_control_room.py green, changelog line, page republished.
   Q20. Card b178-ci-cd-speed-warm-gate-worktree-or-p (Sonnet, p1; card READY 2026-10-12, runs on any host). Run-lock already shipped (auto_deploy.acquire_lock). DONE when: quick-gate wall time measured before/after on the same SHA, every gate step still runs, backup_snapshot staggered off the deploy slot.
   Q21. DONE 2026-10-12 (JIS-NUC): step 1 shipped, research/TOKEN_AUDIT_2026-10-12.md + token_audit.py + test. Next: refine cards b172-trim and b172-template from its ranked cuts (Sonnet). (was: card b172-token-audit-of-the-sonnet-relay-rit, step 1 = measure only, any host). DONE when: research/TOKEN_AUDIT_<date>.md has per-session token numbers from transcripts + ranked cuts, test_token_audit.py green. Then raw cards b172-trim (context trimmed, before/after counts) and b172-template (relay prompt templated): refine from the audit first.
   Q22. Card b173-hide-python-cmd-console-windows-of- (Sonnet, p2). DONE when: every scheduled job that starts python/cmd registers hidden (pythonw or -WindowStyle Hidden), listed in the commit body; no registration of a live-path process is restarted by this session.
   Q23. DONE 2026-10-12 (JIS-NUC): `desk.py next [--host]` + `desk.py assign` (daily, MTS-DailyHygiene step desk_assign), tests green, DSA_DELEGATION.md updated. (was: card b180-dsa-picks-tasks-by-host-desk-py-nex, Sonnet, p2. DONE when: `desk.py next --host` returns this host's first pending row (test with fixture rows) and DSA_DELEGATION.md names the scheduled assigner.)
   Q24. Card b177-control-room-layer-board-tab-per-ac (Sonnet, p2). DONE when: Layer Board tab renders one row per active layer from the registry, test green, page republished.
   Q25. Card b179-tom-and-fabio-layers-story-as-a-sli (Sonnet, p3). DONE when: a Slides artifact built from the existing Tom/Fabio story doc is published and its link is on the Control Room item.
   Q26. Card tom-holdout-clean-split (Sonnet, p1; C-Cloud N1/N2). DONE when: HOLDOUT_CLEAN.json + dated PRE_REG_DAX.md addendum (ledger days dropped from the DAX holdout, forward holdout from 2026-10-10, design/check split of the ledger) committed BEFORE any encode. Dates only, no outcome reads.
   Q27. Card tom-profile-parity-check (Sonnet, p1; N3; needs F:/MTS/data on the host: JIS-NUC has no F: drive, run on JIS-NB). DONE when: PROFILE_PARITY.md table of >= 6 drawn-vs-computed POC/VAH/VAL levels + verdict (volume proofs usable on Dukascopy DAX, or NOT_IN_DATA).
   Q28. DONE 2026-10-12 (JIS-NUC): PRE_REG_TEMPLATE.md + test + lesson + VISION link. (was: card backtest-readiness-template, Sonnet, p2. DONE when: the 12-item pre-registration template is in MyTradingSys/backtest with its test green + a LESSONS_LEARNED entry.)
   Q29. Card fabio-ledger-minute-timestamps (Sonnet, p2; N4 iii; JIS-NB only: F:/MTS/data/fabio_videos is absent on JIS-NUC). DONE when: ledger rows carry entry_time_utc read from frame clocks, replay-ready count in the .md.
   Q30. (after tom-layer-v2-cost, fabio-layer-v2-markets, Q28) Cards cryptocred-home-fit-audit, malkan-home-fit-audit, positioning-home-fit-audit (Sonnet, p4). CryptoCred first. No backtests.
   Q31. JIS-NB only (Sonnet, p1; card relay-two-host-standby, NB half): add `--peer-quiet-min 90` to the kick line of the mts-dispatcher prompts on JIS-NB and update the JIS-NB row in scripts/sched/relay_prompts/TWO_HOST.md. DONE when: a JIS-NB dispatcher tick prints `IDLE peer JIS-NUC` or KICK, and relay_runs.jsonl has a JIS-NB row.
   ORDER (C-Cloud research 2026-10-11, BACKTEST_FAILURES_RESEARCH.md): Q26 and Q27 BEFORE tom-layer-v2-cost (Q4 part B) and tom-encode-spike-fade (Q6); Q29 before fabio-layer-v2-markets (Q5 part B). Q6/Q7 pass bar = recall AND fire rate on the held-back CHECK set; DAX holdout excludes ledger days.
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

Older updates: `handoff_history/` beside this file (read only when a task points there).
