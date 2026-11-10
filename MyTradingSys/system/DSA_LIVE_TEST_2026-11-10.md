# DSA live test 2026-11-10 (AIBridge 0.7.33 / 0.7.34 fixes)

Host JIS-NUC, Browser 1 (Chrome Profile 5), DeepSeek account jish********985 (checked in Settings). Profile 4 and jishu.awgp not touched. No `dsa.py start --open`. No other DeepSeek account used.

Result: run did NOT reach the 60-minute watch. Arming was refused at about 07:12Z, so the live DSA queue never ran. Most fix checks are NOT TESTED, not PASS.

## Verdict per fix

- pacing (20 s + 5-15 s jitter): NOT TESTED. No bridge calls were made (no AIRUN block ran).
- hourly cap (30/h): NOT TESTED.
- stop-on-warning: NOT TESTED. No warning or logout was seen.
- one armed chat: FAIL-as-observed in the sense that a second chat is refused while chat 2tlfo1 is armed in this profile. The refusal itself works (see bug 1). Whether 2tlfo1 is a leftover from an earlier run is unknown.
- SHIP OWED message (dsa.py): NOT TESTED.
- seed boot: the seed's boot block did not run by itself. Design note, not a FAIL (per B): a chat only auto-runs once armed. Observed: after the message was sent (06:49Z), the reply showed `reply complete, 1 block(s) waiting: click Run` at 07:00Z and no `[AIRUN RESULT]`. No `mts-dsa-jis-nuc-1110-*` worktree was created.

## Timeline

- 06:49Z: `Start DSA bridge` sent in a new chat. Panel: `all match` 0.7.34.
- 06:49:55Z: baseline `dsa_watch.py`: DSA pending=1 taken=2 oldest 60.4 h STALLED; DSA-NB OK; DSA-NUC pending=4 taken=2 oldest 61.5 h STALLED.
- 07:00:06Z: `dsa_watch.py` unchanged (DSA 60.6 h, DSA-NUC 61.6 h STALLED). `bridge_last_call=0.2h ago`.
- 07:0xZ: peer request: pull fast-track. Pulled; `3dda96f69` (close `dsa-refine-raw-cards-1107`) is on `origin/fast-track`.
- about 07:12Z: peer request: tick the Hands-free / auto-run checkbox. Ticked. Panel refused (text below). Stopped per instruction.

## Bugs and evidence

1. Arming refused by the panel (not a bug in the refusal itself). Exact panel text, read from the AIBridge panel: `second_tab_refused: chat 2tlfo1 in this browser profile is already armed. One armed chat per DeepSee...` (truncated by the reader). Chat 2tlfo1 was not identified. Action needed from the operator: find and disarm the other armed chat in Profile 5, then re-arm this chat.
2. DSA's own commits: none reached `origin/fast-track` during this run, because no DSA work ran. Recent task-file commits on trunk are `3dda96f69` and `bd246127e` (not DSA-run). This is the SHIP OWED question still open, not answered.
3. Stale STALLED queues: DSA 60.6 h and DSA-NUC 61.6 h with pending cards unchanged. No card moved during the run (`dsa-refine-raw-cards-1107` was closed by a peer commit, not by DSA).

## Next step

Operator: disarm the other armed chat (2tlfo1) in Profile 5, or tell me to continue on a different chat. Then re-run the arm step and the full 60-minute watch.

## Retry after operator closed chat 2tlfo1

Operator reported 2tlfo1 disarmed and closed in Profile 5. Retried arming the DSA chat (Hands-free ticked). Panel still shows, exact text:
`second_tab_refused: chat 2tlfo1 in this browser profile is already armed. One armed chat per DeepSee` (truncated by the reader).
The panel line may be stale; the arm state could not be confirmed. Run stopped again. Nothing was clicked on Run.

Verdict stays: pacing NOT TESTED, hourly cap NOT TESTED, stop-on-warning NOT TESTED, SHIP OWED NOT TESTED, seed boot design note only.

Design note: an idle armed tab blocks every other chat on that profile with no time limit; the refusal names the old chat id but there is no timeout to clear it.

## Second retry after F5 (operator reload)

- Operator pressed F5 on the chat (refusal line from 2tlfo1 cleared). Seed boot block: result #1 `rid=rupjnp-mwadart2-3` ran at 07:27:24Z with `note: run manually by the operator`. The bridge did not run it on its own, the operator pressed Run. Boot banner completed: worktree `mts-dsa-jis-nuc-1110-0727`, `dsa.py boot` ok, DSA waiting for an order (no "go" sent).
- Ticked Hands-free. Panel refused with exact text: `second_tab_refused: chat rupjnp in this browser profile is already armed. One armed chat per DeepSee` (truncated by the reader). The refused chat is this chat itself (rupjnp), so the holder may be stale or self-referencing. Not resolved; stopped per instruction.
- Design note: the refusal names the chat that was refused, so the armed holder is not identified in the line. Needs operator check in Profile 5.
- Verdicts unchanged: pacing NOT TESTED, hourly cap NOT TESTED, stop-on-warning NOT TESTED, one armed chat: refusal fires (observed twice), but holder unclear, SHIP OWED NOT TESTED, seed boot: bridge did not run it on its own (operator Run needed), design note not FAIL per B.

## Guide check (DSA_HAIKU_GUIDE.md, read at 07:3xZ) and gaps for the operator

Followed guide section 3: reloaded the chat, ticked Hands-free again. Still `second_tab_refused: chat rupjnp in this browser profile is already armed. One armed chat per DeepSee` (naming this chat). Stopped; no `go`, no Run.

Gaps the guide does not cover (for the next guide update):
1. The seed's first block did not run by itself. The result header said `note: run manually by the operator`. Guide 2.3 says the extension sends the seed and boot takes a minute; add that the seed block waited for a Run click in this run.
2. Guide 3 says a silent armed tab expires after 90 s. Our 2tlfo1 refusal persisted for hours until its tab was closed by the operator. Note the TTL did not clear it.
3. Guide 3 covers refusals naming another chat. It does not cover a refusal that names THIS chat's own id (rupjnp), which persisted after F5 and re-tick. Cause unknown; needs an operator check of the armed state in Profile 5.
4. Guide 1.1 says checkout detached origin/fast-track. Works, but `git pull --ff-only` on a detached HEAD fails without a branch; use `git pull --ff-only origin fast-track` or the checkout form.

## Retry after 100 s wait (no F5, one tick)

- Waited 100 s with no clicks, then ticked Hands-free once. Toast (read from screenshot): `second_tab_refused: chat rupjnp in this browser profile is already armed. One armed chat per DeepSeek account; untick there first.` The Hands-free checkbox appears ticked in the bottom-right panel. Stopped per instruction.
- Peer's cause (not verified here): content.js:21 gives each page load a random tab id; nothing releases the arm on reload (no pagehide handler). The earlier arm of this chat (rupjnp) can ghost for 90 s after F5 and then refuse the new page. Suggested bridge fix: release the arm on pagehide. This is a bridge defect to log; DSA must not change bridge code.
- Still NOT TESTED: pacing, hourly cap, stop-on-warning, SHIP OWED. The 60-minute watch has not run because arming was never confirmed.
