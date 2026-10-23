# Codex lab unstick, 2026-10-23: decisions behind the card edits

All decisions are OURS (builder codex-unstick, no operator input). Tries are reset by a REOPENED row in F:/codex_home/lab_runs/runs.jsonl.

## lab-formula-spec-text
- Run 2026-10-22 ended SHIP_FAILED (second ship within 10 minutes; content fine), then BLOCKED on two things.
- F01: the acceptance value 57.8313 (= 48/83 * 100) comes from a SYNTHETIC close series. No 15-close DEV window gives it; the best is 57.8302
  (57.830163407447). DECISION: the tape-based F01 example shows the tape value (cite the 15 bar open times, DEV only); the old closes stay
  only as a second F01 example labelled SYNTHETIC with RSI 57.8313 (hand arithmetic shown), replacing the wrong 57.8125.
- F18-F21 per-sub-id hard cases: moved to lab-formula-spec-recount, so this card can finish.
- One unreproducible number is a MISMATCH finding in the report, not a reason for BLOCKED.

## lab-formula-spec-recount
- Run 2026-10-21 ended SHIP_FAILED (merge conflict in lane_state.json, since resolved) with a BLOCKED claim that sub-ids are undefined.
- They are defined: the bold paragraph openers in FORMULAS.md. grep -n -E '^\*\*(11|18|19|20|21)\.[0-9]+ ' FORMULAS.md gives
  11.1-11.8 (lines 213,242,253,261,280,286,304,313), 18.1-18.7 (415,432,440,445,458,475,479), 19.1-19.8 (489-507),
  20.1-20.4 (513-523), 21.1-21.9 (529-545). The run searched for the string "F11.1" and found nothing.
- A sub-id whose paragraph has no computable number is NOT_APPLICABLE with the paragraph quoted: a finding, not BLOCKED.
- Order: run lab-formula-spec-text first (prio 2 vs 3); no depends_on, because an unfinished dependency makes the card NOT READY.

## lab-planted-error-trial
- Run 1 found zero clean cards (wrong inventory); run 2 found 6 of the required 10 whose originals pass every machine check:
  context-factors-v3-crossvendor-review, gptb-bb-top-reversal-event-table, gptb-funding-extreme-event-table,
  gptb-session-levels-event-table, krown-catalogue-gpt-audit, lab-audit-tom-ledger-frames.
- scripts/dev/planted_error_trial.py exists and raises below 10. DECISION: MIN_CLEAN = 6; 8 shadows (one per error class), clean cards
  taken round-robin (a card may carry two different shadows, one plant each); 10 shadows only if 10 clean cards exist; the report says so.
- scripts/dev/test_planted_error_trial.py does not exist yet: write it first, it must fail on the current script.

## argon-blind-read-7-frames
- agy.exe says "Please sign in" (token expired 2026-10-22 11:30 IST) and the Codex sandbox has no network, so the refresh fails: every CODEX
  run ends INCOMPLETE. DECISION: lane DSA-NUC (a NUC session has network and can refresh the login); steps unchanged.

## t02-f3-fixtures-wlow-session-levels, t02-f3-fixtures-fabio-v3-grid
- Moved SONNET -> CODEX: hand-built bars, one new test file each, no data, no live path, part a (t02-f3-event-forcing-fixtures-for-wlow-b) done.
  Their claim-free state was checked on 2026-10-23 (the only t02-f3 claim is the stale one on part a).
