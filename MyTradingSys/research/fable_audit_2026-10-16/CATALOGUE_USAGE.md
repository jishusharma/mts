# CATALOGUE_USAGE: Fable 5.1 A3 catalogue + rebuild audit, usage and other sessions (2026-10-16 IST / 2026-10-15 UTC)

Session: JIS-NB, worktree `claude/fable-catalogue-audit-rebuild-679c65`, claim `fable-catalogue-audit-a3-catalogue-rebui`. Deliverable: CATALOGUE_AUDIT.md (same folder).
Operator instruction: zero input; conservative defaults logged as DECISION (OURS) in the audit. Turn cap: A3 text lifts it to 40; the hook's cap-15 notices were overridden by that text.

## Usage (get_usage, all three meters, UTC)
| when | 5-hour | weekly all models | weekly Fable | context tokens |
|---|---|---|---|---|
| start 2026-10-15 19:31Z | 22 % | 35 % | 4 % | 112k of 1M (11 %) |
| end 2026-10-15 19:45Z | 34 % | 37 % | 6 % | 315k of 1M (32 %) |
| delta | +12 | **+2** | +2 | +203k |

Guard: stop at a 6-point rise of weekly all-models or at 95 %. Not reached. Tool turns: 26 (A3 cap 40). Operator turns: 1.
Where the tokens went: the catalogue itself (1219 lines, read in full), 31 quote-context windows, 6 Tom transcripts in full (about 14k words), the 9IliXww64uM captions in full, 60 keyword windows of the DyS79Eb92Ug captions (27.8k words, not read in full), the GPT T2 audit, the Krown catalogue head and overlap table.

## Other active sessions (list_sessions, excluding this one)
### At start (19:31Z): 3 running of 25 listed
| session | state | note |
|---|---|---|
| Fable 5.1 testnet adversarial review (local_816e2518) | running | pinned, remote control on |
| Super session 2: overnight testnet pipeline (local_b8b29390, super-2) | running | |
| Gate speed-up: quick ship check; CI runs the full suite (local_321e164b, gate-speedup) | running | started by the coordinator local_1c4041fd |
| Fable 5.1 model usage and optimization (local_1c4041fd, coordinator) | idle 19:14Z | |
| Mts dispatcher (local_29dc0b76 and 5 older rows) | idle | hourly NOOP ticks |
| Fable 5.1 MTS builder pilot (local_6706d2f7) | idle 18:54Z | the gross-effect PRE_REG session |

### At end (19:45Z): 2 running
| session | state |
|---|---|
| Super session 2 (super-2) | running |
| Gate speed-up (gate-speedup) | running |
| Fable 5.1 testnet adversarial review | idle 19:44Z |
| Fable 5.1 model usage and optimization (coordinator) | idle 19:44Z |

No session was started, messaged or stopped by this one. The claim board at start: candle-close-corrected-rerun (STALE 31 h, JIS-NUC), malkan-captions-fetch-noauth, orderflow-restart-map, super-watchdog; none touched.
