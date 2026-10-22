# Haiku + Sonnet audit of the whole chat's changes (2026-10-21, read-only reviewers; brief: REVIEW_BRIEF.md)

## Both agree
1. CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50 was added (uncommitted) to the MAIN checkout .claude/settings.json: it makes EVERY session compact at 50%, not only Supervisors (operator rule: only Supervisors compact). A later reset/ff wipes it; doctor HOOKS check flags it as drift. Decide: scope to Supervisor only (launch-time env) or drop; commit the decision.
2. Supervisor 500k nag (turn_meter.py ~:279-281) still repeats every 5 calls and says "hand off per RELAY.md", while supervisor.md says compaction carries it on and handover is `supervisor.py handover`; WORKERS.md:34 says "hand over at 500k" but code only nags. Make code, supervisor.md and WORKERS.md say one thing.
3. Main checkout (C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed, now a5cff0ac8 after operator-ordered reset --hard): tracked MyTradingSys/runtime/orderflow_live/2026-09-29..10-03.csv (and _qhist) show as deleted; cause unknown. Restore (git checkout HEAD -- <files>) or untrack if they are runtime data (.gitignore:176); the operator pre-approved fixing the main checkout.
4. Right: Supervisor context cap, event prompts exempt, compaction ends Opus jobs, doctor HOOKS check, broadcast on trunk (39c858c5c, tests pass), RSI+WaveTrend (2b80ef52b), CI fix (67fb3ce5e, dc9c57fbc). Haiku re-ran the new tests on pre-8557ad144 code: 4 failed, 23 passed (red before confirmed).

## Haiku only
- The Opus block returns decision:block on UserPromptSubmit: the operator's typed message is dropped with no saved copy and no instruction to paste it into a new session. Save the text to a file and say where.
- 8557ad144 rewrote an existing test (old `o3` assertion replaced by a 5-call loop) instead of adding one: re-check it still catches the nag.
- Nobody ran a test of mts-broadcast in this chat; its review card desk_queue/20261021-050751-review-mts-broadcast-implementation.json is pending.
- Studies: WaveTrend FAILED, RSI NOT ENOUGH DATA (about 2 trades a day); test_studies.py "red before" was only a missing module.
- No setting stops non-Supervisors auto-compacting; turn_meter.py:254 only marks Opus.

## Sonnet only
- Supervisor transcript detection reads only the first 60 KB and matches `"You are Supervisor`.
- Sonnet/Haiku get no post-compaction handling (they carry on from a summary).
- Numbers in docs have no source in the repo ("113 of 116 Opus compactions manual", "~250k for every model").
- No check that broadcast is "in action" in the live flow.

## Top fixes (merged)
1 autocompact override: Supervisor-only or drop, committed. 2 restore/explain the CSVs. 3 save a blocked message to a file. 4 fix the 500k nag + WORKERS.md wording + point to supervisor.py handover. 5 post-compaction handover for Sonnet/Haiku; run the broadcast test and review card.
