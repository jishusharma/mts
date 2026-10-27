# Super run, 2 hours (designed 2026-10-25 by MTS_Doctor as Lead; operator asked "design for 2 hours only")
Runs under SUPER_SESSION.md (D1-D6); this file only sets scope, order and stop rules for ONE 2 h window. Coordinator on Sonnet, workers Sonnet.

## Budget (get_usage 2026-10-25, login C)
5 h window 23 % (resets in 3 h 27 m); weekly 41 % against the 45 % cap (d-weekly-cap-45). Headroom ~4 % weekly: the run is meant to end on the
cap, not on the clock. Check `get_usage` at start, +60 min, +105 min. Stop spawning at weekly 44 % or 5 h window 80 %. Hard end 120 min from start.

## What it removes (blockers first)
Gate speed is the blocker: a test registration forces the 20-50 min full gate, and live-path ships need local `--full`. So lane 1 goes first.

| Lane | Order | Card | est turns | Why now | Files (held by this lane only) |
|---|---|---|---|---|---|
| 1 tooling | 1 | registering-a-test-in-scripts-dev-run-ex | 22 | p1 blocker; CRITICAL: review Agent before ship | run_extra_tests.py, extra_tests.tsv, preship.py, test_gate_select.py, test_run_extra_tests.py |
| 1 tooling | 2 | gemini-queue-claim-release-push-hangs-fo | 10 | p1; NUC claim hangs; makes night burns safe to start | gemini_queue.py, tests/test_gemini_claim_skip.py |
| 2 live parity (JIS-NB, worktree only, never deploys) | 1 | t09-f1-volume-fvg-side-inverted | 12 | live volume_fvg trades opposite side; 0/24 agree. Use NUC proposal `gx4-t09-f1-fvg-side` (fix.patch + test, NUC branch gpt-q/) as a hint only, after the harvest step | alerts/live_layers.py, test_live_runner_layers.py |
| 2 live parity | 2 | t09-f2-live-exits-match-tested-exits | 25 | one bracket for all layers; only if lane 2 card 1 shipped before +60 min | execution/auto_trader.py, auto_trader_config.json, test_auto_trader.py |
| 3 (only if the +60 min check shows weekly <= 43 %) | 1 | statecode-invalid-publish-race | 20 | CRITICAL Java race; disjoint files | StateCodeEmitter.java + test |

Not in this run: t09-f3 (waits for f2, same file), statecode-late-seam-tick (same file as race, after it), super-session-coordinator-stalls (needs
SUPER_SESSION.md editor; next window), sim-dashboard-v1, all raw cards (Session_Planner refines top 5 at boot only).

## Boot sequence (coordinator)
1. `get_usage`; ANNOUNCEMENTS ACTIVE; STATUS.md; read this file. STOP/HOLD wins.
2. Harvest (no builder needed, read-only): ssh the NUC (`ssh -i ~/.ssh/nuc_gate e-ngineers@192.168.29.110 ps < script.ps1`), list `gpt-q/*` branches in F:\MTS\mts-codex-lab, copy patch + report of the three finished GPT jobs
   (gx4-t09-f1/f2/f3) into the scratchpad; attach as `refs` hints in the worker brief. Patches are proposals: the Builder re-derives, tests red-before/green-after.
3. Start 2 workers (lane 1, lane 2) as sessions, `model` sonnet, briefs per SUPER_SESSION Rule 2, each card's own `done_when`; size 22+ cards: stop at 40 turns.
4. Review Agent (Rule 3) on lane 1 card 1 and every lane 2 diff (live path: local `--full` gate, one ship at a time).
5. Lane 3 only on the +60 min budget check, with the justification line in the notes file.

## Stop / end
At 120 min, or weekly 44 %, or CI red (revert only): stop spawning, let running workers finish their ship if gate is already running, else write partial
work to the notes file. End per SUPER_SESSION "End" (git cherry empty, handover/SUPERVISOR_C.md, one docs-only `sync.py ship --release`). Not touched: deploys, restarts,
HALT, mainnet, `.secrets/`. Anything shipped on live-path stays undeployed until the operator or a JIS-NB desk task deploys it.

## Success numbers
Lane 1 card 1 shipped: `len(all_tests())` identical before/after and test registration no longer forces full gate. Lane 2 card 1 shipped: volume_fvg side test red before, green after.
At least 2 of 3 lane cards `done` on trunk (`git cherry` empty, `Result:` in the body) in 120 min, or the notes file says exactly why not.
