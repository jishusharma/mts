# gemini-lane-fix — 2026-10-28T08:19:56Z

Builder session on JIS-NUC (gateway). Three sub-tasks: A (push race), B (Argon option), C (7 failed NUC cards).

## Task A — "push rejected" race (reproduced, root-caused, fixed, regression-tested)

`scripts/dev/sync.py` `push_claim_commit` retried a lost push race **back-to-back with ~0 s between attempts**,
so two contending claimers re-fetched in lockstep and lost every attempt; `gemini_queue.claim_with_retry`'s 6
outer tries × 3 inner `push_claim_commit` pushes = up to 18 consecutive lockstep re-fetches before giving up.
The `ship()` loop already jitters (`GATE_SPEED D4`, 1–5 s) for the same reason.

Fix: `push_claim_commit` now takes a `sleep=time.sleep` param and jitters `0.5 + 3.5 * random.random()` s between
attempts (sync.py:1353-1357). `claim()` and `release()` thread `sleep` through, so `gemini_queue.claim_with_retry`
already has the jitter on its retry path. Two new tests in `test_sync.py` (`SyncTest`):
- `test_lost_claim_race_retries_after_a_jitter_not_in_lockstep` — spies on `git`, forces a rejected push, asserts a
  single sleep of 0.5–4.0 s fires before the retry.
- `test_claim_and_release_take_a_sleep_arg` — asserts `claim`/`release` forward `sleep` to `push_claim_commit`.

Both tests **fail on pre-change code** (`TypeError: push_claim_commit() got an unexpected keyword argument 'sleep'`)
and **pass on the fixed code**.

Re-queue live confirmation: `sync.py claim extracted-rules-wiring-audit` succeeded on the **first try** through the
new jitter path (previously this card needed all 6 outer + 3 inner retries).

## Task B — Argon option + `:low` effort default

`scripts/dev/gemini_queue.py` `run_job(card, effort, model='flash')` now accepts `model in flash|argon`
(default `flash`); `main()` parses `card[:effort][:model]` in either token order, default effort `low` (was `medium`),
default model `flash`.

Real model ids verified from `agy models` on this NUC (not guessed):
- flash → `gemini-3.8-flash-{low|medium|high}`
- argon → `gemini-4-argon-{low|medium|high}`

### Test card: `analyst-ingest-roman-x` (READY, unclaimed, public-data: Roman Trading public call ingestion)

**flash:low** (`gemini-3.8-flash-low`, EXIT 0 after 34 s):
```
The card `analyst-ingest-roman-x` is already in state `done` and previously shipped:
- `tasks.py tag analyst-ingest-roman-x`: STATE SHIPPED@9ca6a940e
  LATEST ship 2c7197cf7 2026-10-28 ... (commit fd31f8f6b491)
  LATEST ship fd31f8f6b491 2026-10-25 analysts: Roman Trading volume-absorption call ingestion adapter
- Unit tests pass: test_analysts_ingestion_and_scorecard.py (12 tests OK).
- Card status: already marked `done`; working tree clean on branch gemini-q/analyst-ingest-roman-x.
```

**argon:low** (`gemini-4-argon-low`, EXIT 0 after 85 s):
```
Card `analyst-ingest-roman-x` is already implemented (fd31f8f6b491) and closed (9ca6a940e) on this branch;
all 16 unit tests pass.
- Adapter & Ledger: scraper.py (parse_roman_post, parse_inbox_paste, ingest_roman_posts, validate_provenance — OURS)
  wraps parse_social_call with ImbalanceConstruct.VOLUME_ABSORPTION; appends verified records to CALL_LEDGER.csv
  (header-only; 0 fabricated calls per scope_out).
- Tests: test_roman_ingestion.py (4/4 pass — OURS), test_analysts_ingestion_and_scorecard.py (12/12 pass,
  FEE_PER_SIDE = 0.0005 SOURCED: FORMULAS.md:s17).
- Task State: analyst-ingest-roman-x.json state "done" at commit 9ca6a940e54f, clean working tree.
```

Both models reached the correct, safe verdict: card already shipped; no re-work needed; no fabricated calls.

## Task C — 7 NUC cards that failed twice and were skipped (one-line verdict each)

| Card | Queue-log root cause | Card state | Verdict |
|---|---|---|---|
| `extracted-rules-wiring-audit` | Push race (Task A) — 6 outer × 3 inner lockstep re-fetches lost | `refined` (still open) | **Fix is code (Task A); re-queued the claim on JIS-NUC — succeeded first-try via the new jitter path.** |
| `extraction-cross-method-qa` | Push race (Task A) — same lockstep loss | `done` (shipped 0430c00ac) | No re-queue needed; race fix prevents recurrence. |
| `gem-formulas-rederive-8-9` | Push race (Task A) — TIMEOUT after 3 tries | `done` | No re-queue needed; race fix prevents recurrence. |
| `gem-malkan-mtf-lookahead` | Push race (Task A) — TIMEOUT after 3 tries | `done` | No re-queue needed; race fix prevents recurrence. |
| `gem-wavetrend-fixture` | Push race (Task A) — TIMEOUT after 3 tries | `done` | No re-queue needed; race fix prevents recurrence. |
| `yt-gem-fabio-fetch-2` | Git identity not set (SYSTEM@JIS-NUC) — `commit-tree` failed before a544be7e4 | `done` | Fixed in a544be7e4; no code change needed this pass. |
| `gemini-ccu-dxntdn3jftg-check` | Stale claim held by JIS-NUC (64 h) — SKIP at once | `done` | **Released the stale claim; card is now free.** |

DECISION (OURS): `analyst-ingest-roman-x` used as the public-data test card for Task B (READY, unclaimed, scope
in/out are public Roman Trading call data — no live/order data, no mainnet, no secrets read).
