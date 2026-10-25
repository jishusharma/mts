# Pilot 3: Haiku workers on mechanical cards (designed 2026-10-25 by MTS_Doctor as Lead; operator: "do pilot 3 now, one safe time")
Parent plan: research/mts_doctor/PILOT_super_session_2026-10-24.md ("Next pilots"). One change vs pilot 2: workers are Haiku. Coordinator Sonnet.

## Frozen card list (verified: STATE ready, disjoint files, spec-derived test = `verify_extract_quotes.py` exit 0, ~15 turns each)
| Worker | Card | Files held (only these) |
|---|---|---|
| H1 | apply-gpt-fix-audits-gemini-extracts | extracts/gemini_out/-dMWA_bbm3o_audit.md, 1xBWnyr1qe4_audit.md, FIXES_APPLIED_audits.md |
| H2 | apply-gpt-fix-fabio-notes-gemini | extracts/gemini_out/fabio/*_note.md (9), FIXES_APPLIED.md |
| H3 | apply-gpt-review-fix-items-to-gemini-ext | extracts/gemini_out/*_gemini.md (7 named in card), FIXES_APPLIED_tom.md |
Not in pilot: aws-bedrock (needs AWS credentials), research-top-level-declutter (moves 183 files), hook-reminder-* (new hook), lint-lookahead (shipped 14f1703b9, stale), anything live-path.

## What to learn from earlier runs (each is a rule here)
1. Coordinator idled after one Bash call (pilot 2 and tonight): EVERY wait = one background shell that exits on the condition; heartbeat line in `handover/SUPERVISOR_C.md` every 15 min; never end a turn with nothing armed.
2. Ships hang or vanish when piped (`| head`) or backgrounded without a file: ship as ONE background shell writing to a file, no pipes; after exit check `git cherry origin/fast-track` is empty. Never start a second ship while one runs.
3. One ship at a time (gate 2.5 min median vs 50 min parallel).
4. Haiku invents quotes: a worker may not edit a quote it cannot find in the cited raw transcript line; `verify_extract_quotes.py` exit 0 is the ship gate, never "looks right". REJECTED items need a transcript line.
5. Files outside the card's Scope in are untouched (the diff stat checked by coordinator before each ship). No results/*.json, no new top-level files.
6. Card supply/stale: coordinator re-checks each card's state and `file history` for its files before launch.
7. Turn cap: Haiku tool turns allowed = 4M / context (turn_meter.py); a worker over 40 turns stops, writes partial notes.

## Reviews (operator: review before and after, not overdone)
- Before: coordinator reads each card brief once and writes in notes: files, test, the 1-line risk. Nothing else.
- After: for H1 only (smallest), one fresh Sonnet Agent given the diff + the verifier output + 3 randomly chosen edited lines and the raw transcript lines; it says if any edit is unsupported. If it finds one, the Agent samples H2 and H3 too. Coordinator also spot-checks one quote per worker by hand.

## Measured (write to handover/PILOT3_RESULTS.md at the end, one table)
Per worker: Haiku model confirmed (get_session), context tokens at start / mid / end (get_usage context.tokensUsed), tool turns, minutes, verifier exit, Sonnet-review verdict, rework. Fleet: weekly % start/end (login C 43% now), 5 h window peak, gate wait per ship, CI red count.
Context-files changes (card+fixed-form handover, fold-on-ship hook, C1 context gap): designed but NOT on trunk (impact map: context_gap.py NOT_FOUND), so they do NOT apply to Haiku in this pilot; this pilot is the no-change baseline for them.

## Pass rows (decided now)
1 All 3 cards shipped, cherry empty, Result: lines. 2 Verifier exit 0 on all edited files; Sonnet review finds 0 unsupported edits. 3 Ship gate median under 2 min. 4 CI <= 1 red, 0 reverts. 5 Weekly cost for the whole pilot under 2 points, 5 h window under 60%. 6 Worker turns median under 25; context at end per worker recorded. 7 0 operator turns. 8 Rework 0 after 24 h (read later).
Fail on any: name the cause from transcripts/git, one fix, rerun. Hard stop: weekly 67% (operator 2026-10-25 morning: cap is now ~70%, was 50% overnight) -> stop spawning, finish only shipped-in-gate work, write notes. Hard end 90 min.
