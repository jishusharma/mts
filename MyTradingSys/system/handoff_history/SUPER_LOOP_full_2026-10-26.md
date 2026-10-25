# SUPER_LOOP - the five-hour Supervisor loop on every device and login (operator 2026-10-19)

One line on any device, any login: `You are Supervisor. Login <A|B|C>. <tasks>` (tasks optional; no tasks = the dispatch order).
The role file (roles/supervisor.md) is the brief; this file is the design. Code: `scripts/dev/supervisor.py plan|handover|wait|tick`.
Replaces TANDEM_3LOGIN.md (2026-10-19 study by the Sonnet agent; its fit table and gap list are folded in below).

## The loop
| Step | When | What the Supervisor does | Code (T0 output, no reading of docs) |
|---|---|---|---|
| Boot | first turn | `get_usage` (5 h % + reset, week % + reset), then `plan` | `supervisor.py plan --login L --five P --five-reset T --week W --week-reset T` |
| Pace | every wake | `plan` prints mode, slots, target; no thinking about budget | `pace_plan` (below) |
| Work | every wake | start what the SPAWN lines say, run the RUN lines in one Bash call | sessions on operator turns, Agents on event turns |
| Watch/distribute | every wake | PEER/OPERATOR/NOTE lines; the heartbeat goes out inside `plan` | `live_supervisors`, `lane_owner`, `nuc_budget_ok` |
| Wait | end of each wake | one background watcher, end the turn | `supervisor.py wait --timeout 50m --login <L> [--shas ..]` (also wakes on a free slot + ready cards) |
| Transit | TRANSIT time (20 min before the 5 h reset), 5 h >= 80%, or turn cap | `handover --note "<next>"`, one docs ship, successor line | `supervisor.py handover --login L --note ..` |

Login letter: the account email of this session against the CLOUD_ACCOUNTS.md LOGINS table (A jishu.sharma, B jishu.awgp, C jishusharma1985).
`get_usage` does not name the login, and JIS-NB hosts B and C, so env MTS_LOGIN is only a default; the start line wins.

## Automatic vs operator, honestly
Automatic (code, every wake): budget reading kept per login (`~/.claude/mts-superloop/<L>.jsonl`, local); heartbeat sent; pacing mode and slots;
card shard over the live supervisors; host-lane filter (no CODEX/Lab_Guy card on a non-NUC device); one owner per shared lane; DSA rows posted
(`desk.py assign`) by the owner; dead DSA target detected; NUC GPT lab ticked from NB over the SSH gate; one headless NUC worker (`nuc_wake.py`)
when no supervisor runs there and every NUC login has budget; hand-over file written.
Needs the operator (no code can do it):
- Paste the one line on each device/login (once per 5 h, or when a Supervisor ends early). Nothing starts a session by itself (SCHEDULING_POLICY).
- Any message to a Supervisor = an operator turn: only then can it start full sessions. Event turns (worker note, watcher exit) start Agents only.
- OPERATOR lines: DeepSeek chat closed or hands-free unarmed (bridge down), AIBridge agent down, extension reload after an install.
- A Sonnet Supervisor ends at 40 tool turns or 10 operator turns (CLAUDE.md step 5): a 5 h window is one or two Supervisor sessions.
Not possible today: one device starting a Claude session on another (except `nuc_wake.py`, one-shot, headless, NUC only); waking a Supervisor
between watcher exits; reading another login's `get_usage` (only its heartbeat).

## Pacing (all OURS; inputs from get_usage)
- Weekly cap: 75% for B and C on JIS-NB, else 95% (SUPER_SESSION rule 12). Room this window = (cap - week%) / windows left to the weekly reset,
  turned into 5 h points with k = weekly points per 5 h point (measured from two readings in one window, else 0.12 GUESS), at most 80 - 5h%.
- Target = 5h% + room (never above 80). Slots by room: >= 40 -> 4, >= 20 -> 3, >= 10 -> 2, >= 4 -> 1, else 0. `new` = slots - running.
- Burn check: burn since the window's first reading, projected to the reset. Projected > target + 3 -> slots at most running - 1 (start none,
  let one finish); projected < target - 10 -> slots at least running + 1 (max 4).
- Modes: STOP (5h >= 80, or no room, or week over cap), SUPERVISOR-ONLY (>= 70), CRUCIAL-ONLY (>= 60), SPEND (room >= 30), NORMAL.
  STOP and SUPERVISOR-ONLY still run every model-free lane (DSA, GPT lab, CI): something useful always runs while any lane has work.
- Near the weekly reset the room grows on its own (one window left = all weekly room), so the week is spent, not wasted.

## Heartbeat (the only published state)
One BUDGET signal line per wake on branch `mts-signals` (mts_signal.py, no ids, < 200 chars):
`BUDGET login=C 5h=7% week=88% reset=2026-10-20T20:00Z sup=JIS-NB mode=STOP run=0 free=0 end=13:40Z dsa=up`
- `traffic.py budget` parses it as before (extra fields are ignored), so the cross-login budget view stays one source.
- `sup=` marks a live Supervisor; older than 75 min = gone; `mode=ENDED` (sent by `handover`) = gone at once. `free` = workers it can start
  now (0 on CI red, never more than the cards this host can run); `dsa` = its local AIBridge agent (TCP 7181).
- One Supervisor per login at a time (heartbeats, shard and hand-over file are keyed by login). A second session of the same login on another
  device is a successor, not a peer: start it only after the first handed over.
- Nothing else is published: claims, desk rows and cards are the rest of the shared state, all in git.

## Partition without collision
- Claude cards: shard = crc32(card id) over the live Supervisors with free > 0 (`tasks.py dispatch --login L --logins ..`). Own cards rank first;
  a peer's card only when own cards < free slots. A gone or STOPped Supervisor drops out of the shard at once, so its cards are not orphaned.
- The lock stays `sync.py claim` (atomic push; refuses a taken card or overlapping area). The shard only makes a refused claim rare.
- Shared lanes have exactly one owner: GPT/Gemini lab = lowest live login on JIS-NUC, else the lowest live login anywhere; DSA posting
  (`desk.py assign`, idempotent per card), Pipeliner start, `nuc_wake` = lowest live login anywhere. Owners are recomputed every wake.
- Hand-over: one file per login, `MyTradingSys/system/handover/SUPERVISOR_<L>.md`; NEXT_SESSION.md only when the Supervisor is alone.

## Pipeliner (allocator) vs Supervisor
| | Supervisor (one per login, 5 h) | Pipeliner (one at a time, lease.py) |
|---|---|---|
| Does | starts workers on ready cards, verifies their claims, runs lanes it owns | refines/re-lanes cards, drains the desk, edits ROUTING.md |
| Never | builds, edits ROUTING.md, starts a second Pipeliner | starts workers, ships product code |
| Started by | the operator's one line | a Supervisor's SPAWN line (lease free and desk rows pending) |

## Where work goes (fit table; evidence: desk board 2026-10-19, 54 closed DSA rows, 34 done / 20 failed, most fails were drained duplicates)
| Task type | Lane | How | Checked by |
|---|---|---|---|
| Backtest/probe with new args, CSV stratify, data fetch, inventories, gate runs | DSA (free) | `desk.py post .. --need "<exact cmds>" --done-when "<file+number>" --target DSA-NB/DSA-NUC` | one number re-done |
| Source hunt (quote + file:line) | DSA | same; RESULT.md | `verify_extract_quotes.py` |
| Mechanical audit rows, bulk classification | DSA (after 0.7.1, 3270e742) | card lane DSA-NB, `desk.py assign` | Claude reads one finding |
| Second opinion on a spec or result | GPT (Codex) / Gemini | lane CODEX card, `codex_run.py tick` / `gemini_queue.py` on JIS-NUC | Lab_Guy (other vendor) |
| Build, live path, formulas, reviewed repo writes | Claude Sonnet | card SONNET via the shard | Haiku rerun + diff review |
| Scoped mechanical edits, reruns | Claude Haiku | card HAIKU | spot check |
| Screenshot / chart reads | Claude (Eagle_Eyes) | never DSA (no vision evidence) | - |
| One step over 300 s | DSA chunked | numbered steps in `--need` | last step merges |
Bridge limits: DeepSeek chat must stay open with hands-free armed (cap 50 auto-runs); 300 s per command; secrets/HALT/.env refused; laptop
(DESKTOP-F7IU69N) has no bridge and posts to DSA-NB / DSA-NUC. Cross-vendor rule (ROUTING.md): the reviewer is not the producer's model.

Per device: JIS-NUC (A, C) runs Claude cards, Lab_Guy, the GPT lab and Gemini (agy), bridge DSA-NUC. JIS-NB (B, C) runs Claude cards and live
reads, bridge DSA-NB, the GPT lab only through the SSH gate. DESKTOP-F7IU69N (A, B, C) runs Claude build cards only.

## Hand-over format (`supervisor.py handover` writes it; the next boot's `plan` prints its Next line)
```
# Supervisor hand-over, login C (JIS-NB, 2026-10-19T13:40Z)
- Next: <one line from --note>
- Budget at hand-over: 5h ..% (reset ..), week ..% of cap .. (reset ..), mode .., k .. (GUESS|measured)
- Peers live at hand-over: A@JIS-NUC, ...
- Last picks: <card ids>
- Open claims from JIS-NB: <slugs> (finish, hand over in the card, or release by the claim rules)
Successor: `You are Supervisor. Login C. Continue from MyTradingSys/system/handover/SUPERVISOR_C.md`
```
Ship it with one docs-only `sync.py ship`. On an operator turn the Supervisor starts the successor itself (`start_session`, Sonnet);
on an event turn the app refuses that and the operator pastes the successor line.

## Failure modes
| Failure | Seen as | Response (automatic unless marked) |
|---|---|---|
| Login out of budget | mode STOP / week over cap | no Claude worker; model-free lanes only; its heartbeat says free=0, so peers take its shard |
| 5 h window nearly spent | 5h >= 70 | SUPERVISOR-ONLY: verify and hand over, start nothing |
| Device silent | no heartbeat for 75 min | drops out of the shard and lane ownership on the next wake of any peer; its claims stay locked |
| Stuck claim | claim with no commit for 45 min | SendMessage, then stop_session next wake (own workers only); others' claims: leave, report in hand-over |
| Bridge down | oldest pending row on a DSA target > 24 h, or `dsa=down` | OPERATOR line (operator); no more rows to that target; work stays in its card |
| Heartbeat not sent | NOTE line | peers do not count you; claims still lock; next wake retries |
| Signals or fetch unreadable | PEERS UNKNOWN line | no shared-lane action this wake (no double owner); own cards only; NEXT_SESSION.md untouched |
| Headless NUC worker repeated | - | at most one `nuc_wake` per 5 h per machine (local stamp); STOP/SUPERVISOR-ONLY and CI red start no Claude session at all |
| CI red | SPAWN CI RED line | only the pinned ci-* card; nothing else ships |
| NUC budget unknown | no `nuc_wake` line | fail closed: no headless NUC worker until every NUC login has a fresh, non-THROTTLE BUDGET line |
| Fetch/board/dispatch read fails | NOTE line | treated as unknown, never as success; read by hand if it repeats |
