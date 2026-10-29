# Layer Lab Report: gemini-queue-claim-race-fix

**Card**: `gemini-queue-claim-race-fix`  
**Kind**: build  
**Date**: 2026-10-28  
**Goal**: Make the claim step in `scripts/dev/gemini_queue.py` retry-safe on busy trunk pushes (jittered backoff up to 6 times), treat own claims as success, set git user identity (`gemini-queue`) in the throwaway worktree, and log failure reasons.  

---

## 1. Summary of Changes

1. **`claim_with_retry(wt, card, tries=6, sleep=time.sleep)`**:
   - Loops up to `tries` times with 2-10s jittered backoff.
   - Treats own host claims (`already claimed by <HOSTNAME>`) as immediate success (`ok`).
   - Treats other host claims as immediate `skip` without wasting retries.
   - Fails fast on timeout (rc 124) or non-race push failures (`not a race`).
   - Re-runs claim command which internally fetches fresh trunk before retrying push.

2. **Worktree Git Identity**:
   - In `run_job`, configures `user.name = 'gemini-queue'` and `user.email = 'gemini-queue@mts.local'` inside the throwaway worktree so headless jobs under SYSTEM identity have valid git configuration.

3. **Single-Line Failure Logging**:
   - On claim failure, writes `CLAIM FAILED: <card>: <why>` to the job log.
   - On skip, writes `SKIP <card>: <why>`.

4. **Tests**:
   - `scripts/dev/test_gemini_queue.py`: 8 unit tests covering:
     - 3 push rejects followed by success
     - Exhaustion after 6 tries
     - Immediate skip on another holder
     - Immediate ok on own holder
     - Immediate fail on timeout (rc 124)
     - Immediate fail on non-race push errors
     - Git identity setting in worktree
     - Skip logging
   - Registered in `scripts/dev/extra_tests.tsv` line 126.
   - All 8 tests pass in 0.17s.
