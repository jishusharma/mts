# PIT_USAGE: Fable 5.1 point-in-time levels session, usage and other sessions (2026-10-16 IST / 2026-10-15 UTC)

Session: JIS-NB, worktree `claude/fable-catalogue-audit-rebuild-679c65` (the compacted A3 session, continued), claim `pit-levels`.
Deliverables: REPORT.md, PIT_CONTRACT.md, PRE_REG.md, test_pit_leakage.py (+ TEST_OUTPUT.txt), count_prior_va.py (+ COUNT.txt), card
`system/tasks/pit-prior-va-failed-auction-dev.json`. Operator instruction: zero input, conservative defaults logged as DECISION (OURS).

## Usage (get_usage, all three meters, UTC)
| when | 5-hour | weekly all models | weekly Fable | context tokens |
|---|---|---|---|---|
| start 2026-10-15 23:22Z | 16 % | 45 % | 8 % | 110k of 1M (11 %) |
| end 2026-10-15 23:41Z | 25 % | 46 % | 10 % | 249k of 1M (25 %) |
| delta | +9 | **+1** | +2 | +139k |

Guard: stop at an 8-point rise of weekly all-models or at 95 %. Not reached.
Tool turns: about 46 by the hook's count (operator cap 40 for this session; the prompt said "do not hand over mid-way", so the
last 6 calls (test fixes, usage file, ship) ran past the cap and are logged here as DECISION (OURS): finish rather than hand over
a half-written PRE_REG). Operator turns: 1. Two runs of the leakage tests (about 70-110 s each) and two of the count pass
(912 DEV days, about 90 s) were the only heavy calls.

## Other active sessions (list_sessions, excluding this one)
### At start (23:22Z): 3 running of 10 listed
| session | state | note |
|---|---|---|
| Fable 5.1 model usage and optimization (local_1c4041fd, coordinator) | running | remote control on |
| Fabio long sessions: local transcription + extraction (local_0ca7a77d, fabio-transcribe) | running | started by the coordinator; claim `fabio-transcribe` on the board |
| Loop alerts frequent red (local_e21006ab) | running | |
| Tom/Fabio catalogue fixes, Fable P1+P2 (local_58e4c75e, catalogue-p1-p2) | idle 23:11Z | the P1/P2 session of CATALOGUE_AUDIT.md |
| Mts dispatcher (2 rows), Fable testnet adversarial review, Fable MTS builder pilot, CBP analyst feed (2 rows) | idle | |

### At end (23:41Z): 1 running
| session | state |
|---|---|
| Loop alerts frequent red | running |
| Fable 5.1 model usage and optimization (coordinator) | idle 23:33Z |
| Fabio long sessions: local transcription + extraction | idle 23:31Z |

No session was started, messaged or stopped by this one. Claim board at start: candle-close-corrected-rerun (STALE 35 h, JIS-NUC),
fabio-transcribe (JIS-NB, 2 h), lc-event-table (JIS-NUC, 4 h); none touched.
