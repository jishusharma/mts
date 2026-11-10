# Supervisor C handover | written 2026-11-10T20:05Z by L1 (Sonnet, JIS-NB desktop) | hand-written

## Goal
Login C on the desktop runs PLAN_24H_2026-11-10.md section 8 as rolling Sonnet links. You are L2 (20:00Z to 01:00Z). Week reset 2026-11-10T20:00Z: budget is fresh; read get_usage first. One worker at a time per set of files, one ship at a time on this machine; name the model on every start (Sonnet; Haiku for mechanical work).

## Truth (verify each from git/disk)
- Live Aid coach 61be0d9cc is on trunk. OI poller: tree mts-jis-nb-live-aid-oi-poller-all-venues-1110, `git -C <tree> cherry origin/fast-track` still showed unshipped commits at 19:55Z; a Sonnet Agent "Re-ship OI poller" was started 19:50Z (card reship-poller-coach-1110).
- Cards on trunk (fad2f8c82): arch-row1-doc-wording-tests-1110, arch-row2-count-tests-1110. Sonnet Agents for both were started 19:50Z with ship order poller, row 1, row 2. Their results go to L1's chat only; check the trunk history and `git -C <tree> cherry` for their work.
- Row 3 (one gate queue per machine), rows 4+5 (hook lines, stop guard) design notes with adversarial verify are in the notes folder C:/Users/E-ngineers/AppData/Local/Claude-Data/claude_pzs8sxrjxfjjc/side-session-notes/local_0cb8bd0b-848b-4df7-b685-6a6d0f12ab98/ : prep_row3_gate_queue.md, prep_row4_5_hooks_stopguard.md, prep_malkan_t06_paper_rows.md (workflow wf_8e824517-17a; read the Verify section before building). Malkan/T06 paper rows were already shipped by B (d65d17633, e38ac8c03): q-898e30 is satisfied, ack it done.
- Asks told, not answered: q-898e30, q-687012 (fold finding 5 into L3 card dsa-live-test-defects-1110), q-11a6b7 (B took gate-slow-steps-profile-1110 and the test_pulse timeout), b-ea3809 (DSA-NUC chat needs a person), b-d2cb73 (Chrome only Browser 2).
- Stop guard blocks any session ending in the main checkout: 5 commits sit on local jis-nb-trunk (duplicate card 56757382d, 766288d44, others); never commit in the main checkout; someone with merge rights should merge origin/fast-track there.
- git identity: I unset the gemini-queue user.name/email from shared .git/config (q-95ed0d done); gemini_queue.py may write it again.

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-C-2026-11-11-L2`; get_usage; verify poller, row 1, row 2 ships landed (cherry empty); if a gate failed, one retry then report. Ack q-898e30 done.
2. Row 3: one Sonnet worker, full gate, after rows 1 and 2 land (design in the notes file). US prep P4 21:15Z (`us_prep.py --phase P4`), send to the operator. Republish the 3 stale pages (read the live page first; sim_desk is 4.3 MB).
3. At 01:00Z: rewrite this file, ship it, start L3 with the one line "Run MyTradingSys/system/handover/SUPERVISOR_C.md", stop.

## Traps
- Ship from your own worktree, never the main checkout. `--next` must be a card id, a stage or `END: reason`.
- Three ship gates at once time out; the test_pulse live_aid node timeout is a known flake (B fixing).
- Lane trees never removed: mts-app, mts-relay, BinanceDataFeed.registry, mts-push, mts-refiner, mts-codex-lab, mts-codex, mts-dsa, mts-control-room.
- Operator replies: bold result line, table, under 8 lines, only what is new; record every operator decision in OPERATOR_DECISIONS.md the same turn. Chrome only Browser 2.
