# NEXT_SESSION

Task: mid-turn-image-intake-gap (card on disk: `python scripts/dev/tasks.py brief mid-turn-image-intake-gap`).

Steps, no operator input needed:
1. `python scripts/dev/sync.py start mid-turn-image-intake-gap`, then `sync.py claim "mid-turn-image-intake-gap"`.
2. Find the 2026-10-18 ~14:57Z session transcript jsonl and check whether the 5 mid-turn images are in it (queued-command or attachment record) versus the user record `ingest_transcript` accepts (scripts/dev/shot.py ~246).
3. Present: extend `ingest_transcript` plus a fixture test that fails on old code. Absent (DEFAULT, OURS): add a KNOWN LIMITS row to MyTradingSys/methodology/screenshot_intake.md (~line 85: mid-turn images never reach disk, re-paste as a new prompt) and the notice line, with a test that the notice text exists.
4. `python scripts/dev/test_shot.py`, `tasks.py done mid-turn-image-intake-gap --result "..."`, `sync.py ship --release <slug>`.

Done earlier this session (pilot C, 2026-10-22): shot-py-store-path-nuc (manifest 452->454 rows), gate-quarantine-expiry-cap (already in c8e5fe3fd, card closed).
