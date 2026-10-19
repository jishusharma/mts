# TANDEM_3LOGIN - three Supervisors at once (A, B, C), 5 h each (2026-10-19, one-time study)

Start line on every device: `You are Supervisor. <tasks>` (add "Login B" if env MTS_LOGIN is unset). The app cannot message across logins or devices;
they meet only in git: BUDGET signal lines, claims, desk rows, cards, the Pipeliner lease.

## Operating picture
| Step | What happens | Code |
|---|---|---|
| Boot | role v2 loads; `get_usage`; `mts_signal.py budget --login L ...` sends the BUDGET line; reads ANNOUNCEMENTS (STOP/HOLD), SUPER_SESSION boot facts, `handover/SUPERVISOR_<L>.md` | roles/supervisor.md, mts_signal.py |
| Plan | 5 h pacing plan: window target 75% at 4 h 40, SPEND 4 / NORMAL 2-3 / THROTTLE 0 sessions, burn check every wake | role file |
| Pick | `supervisor.py tick` shows `peers` (logins with a BUDGET line < 6 h) and shards `dispatch` over them: card owner = crc32(id) % logins; own cards rank first | tasks.py `shard_of`, supervisor.py `read_peers` |
| No double work | the worker's `sync.py claim` is the lock (atomic push, refuses a taken card or overlapping area); the shard makes a collision rare instead of a wasted worker | sync.py claim |
| Wake | hour 0 = operator turn (full sessions). Later: watcher exit (<= 50 min) and worker notes = event turns: Agents only | supervisor.py wait |
| Window / week limits | 5 h >= 80% or THROTTLE: no Claude spawn, model-free lanes only; weekly state per login in `traffic.py budget` | traffic.py |
| Allocation | the NUC supervisor starts the Pipeliner (lease: one at a time) at boot and every ~2 h; others skip | lease.py |
| Transit | 4 h 40: drain, `handover/SUPERVISOR_<L>.md`, one docs ship, successor via `start_session` on an operator turn, else the operator pastes the line | role file |

## What each device sends where
| Device (typical login) | Claude | GPT / Codex | Gemini | DeepSeek (DSA) |
|---|---|---|---|---|
| JIS-NUC (A, C) | build cards, Lab_Guy, Pipeliner | lab here: `codex_run.py tick/status`, keep 8+ ready CODEX cards | `gemini_queue.py run <card>:<effort>` (agy installed) | bridge here: `--target DSA-NUC` (1h/1d, transcripts, inventories) |
| JIS-NB (B, C) | build cards, live reads, deploy rows | none local (lab is the NUC): ssh gate or signal | none (no agy) | bridge here (0.7.1 installed 2026-10-19, reload needed): `--target DSA-NB` (1m klines, NB trees) |
| DESKTOP-F7IU69N (A, B, C) | build cards only (own clone, committed data) | none | Antigravity app, hand-started on lane CODEX cards (no agy, no F:) | no AIBridge: post rows to DSA-NB / DSA-NUC |
Run-and-report with exact commands goes to DSA first (free). Judgment, live path, or a repo write that must ship is a card.
Cross-vendor rule (ROUTING.md): a result is reviewed by another vendor/model than its producer.

## DSA / AIBridge fit
Evidence: desk board 2026-10-19, 54 closed DSA-lane rows (34 done, 20 failed). Most failures were Pipeliner drains (obsolete, duplicate, wrong channel);
real ones: tool missing (yt-dlp), data throttle (Dukascopy), spec too loose (scored backtest with no script). Bridge = DeepSeek chat + Chrome extension +
loopback agent 127.0.0.1:7181 running PowerShell in roots (IdeaProjects, Temp, F:\MTS, F:\AIBridge): up to 6 blocks per reply, task mode cap 1800 s,
300 s per command, output cap 262144 B, secrets/HALT/.env refused. 0.7.1 (3270e742, node tests 7/7) fixes hands-free stopping after a post; NB agent UP.
| Task type | DSA fit | Post it | Result back | Verified by |
|---|---|---|---|---|
| Existing backtest/probe with new args, stratify a CSV | yes | `desk.py post "<t>" --need "<exact cmds, paths>" --done-when "<file+number>" --target DSA-NB` (1m data) or `DSA-NUC` | `desk.py done` + `sync.py ship`; poster `desk.py wait <id>` / tick `desk` | spot-check ONE number |
| Data fetch (klines, funding, metrics) | yes (G5: 2238 files) | same, `--target DSA-NUC` | row result + coverage file | poster recounts files |
| Inventories, counts, worktree triage, gate run | yes | same | counts file | one count recomputed |
| Source hunt (quote + file:line in transcripts) | yes | same | RESULT.md | `verify_extract_quotes.py <extract.md>` |
| Mechanical audit rows (T01-T10 style) | yes after 0.7.1 | card lane DSA-NB, `desk.py assign` | audit md | Claude reads one finding |
| Second-opinion spec/result review | yes (kurisko, g7 done) | desk row, or CODEX card for GPT/Gemini | review md | Lab_Guy class |
| Bulk classification, doc draft from numbers it ran | yes | desk row, exact input list | file | Claude reviews if it touches rules |
| Screenshot / chart reads | not proven (no vision evidence) | do not post | - | Eagle_Eyes |
| Live-path code, formulas, repo writes needing review, yt-dlp/ASR | no | card SONNET | - | - |
| A step over 300 s | only chunked (per year/symbol) | numbered steps in `--need` | per-step files | last step merges |
Still breaks / operator: reload extension + F5 the chat after install (NB now, NUC pending row 20261019-050232); the chat must stay open and hands-free
armed (cap 50 auto-runs, re-arm); two bridges on one DeepSeek account may stall (open item); block lines must not start with a hash.

## Gaps -> consequence -> cheapest fix
| # | Gap | Consequence | Fix | State |
|---|---|---|---|---|
| 1 | Nothing sent the BUDGET line; login letter unknown | `traffic.py budget` empty, no pacing across logins | `mts_signal.py budget`, MTS_LOGIN or "Login X", role boot step | FIXED (test) |
| 2 | Three identical tick top-8 lists | same card started 3x; workers wasted on claim refusal | shard by login in dispatch + tick peers | FIXED (test) |
| 3 | NEXT_SESSION.md is one overwritten file | last supervisor erases the others' hand-over | `handover/SUPERVISOR_<L>.md` per login | FIXED (docs) |
| 4 | 5 h loop undefined (cadence, stop, transit) | idle or over-spent window | role v2 "Five-hour run" | FIXED (docs) |
| 5 | Long prompt pasted, drifts from the role file | stale rules in 3 places | one-line start; START_HERE s3, SUPER_SESSION | FIXED |
| 6 | NB desk row for 0.7.1 never done | DSA hands-free kept stopping on NB | ran aibridge_install.py, row done f5645f83 | FIXED; operator reload |
| 7 | No wake between watcher exits; start_session refused on event turns | after wave 1 (about 1-2 h) only Agents | none without a scheduler (policy); any operator message restarts waves | LIMIT |
| 8 | Sonnet supervisor ends at 40 tool turns / 10 messages | 5 h = 1-2 supervisors; successor needs an operator turn | card tandem-supervisor-turn-cap-5h | CARDED |
| 9 | Other devices cannot see if a DSA bridge is alive | rows wait on a dead bridge | role rule (stop at oldest > 24 h); card tandem-dsa-bridge-liveness-signal | RULE + CARDED |
| 10 | tick top-8 offers CODEX / Lab_Guy / DSA cards to a device that cannot run them | worker starts and stops | role rule "skip unless NUC"; card tandem-dispatch-host-lanes | RULE + CARDED |
| 11 | codex_run tick and gemini_queue are NUC-only | GPT/Gemini idle with no NUC supervisor | role: ssh gate or signal; card tandem-nuc-lab-from-other-devices | CARDED |
| 12 | Two logins on one machine share MTS_ACCOUNT | look like one sender | none (claims name host + task) | NOTE |
| 13 | MTS_LOGIN set once per device; the signed-in login can change | wrong letter, wrong shard/budget | "Login X" in the start line overrides | OPERATOR |

## Honest answer: three Supervisors for 5 h
YES for the first 1-2 h at full strength (shards, per-login pacing, lanes fed), WITH gaps 7-8 after that: nothing wakes a coordinator except workers and a
50 min watcher, and event turns can start only Agents, so full waves restart only when the operator sends any message; each Sonnet supervisor needs a
successor every 2-3 h. DSA is used on NB and NUC only, after the extension reload; the laptop feeds it through desk rows. Check: `traffic.py budget`.
