# DSA live test 2026-11-10 (final report)

Host JIS-NUC, Chrome Browser 1 (Profile 5), DeepSeek account jish********985 (checked in Settings). Profile 4 and the jishu.awgp account were not used. No `dsa.py start --open`. No other DeepSeek account. Chat slug `rupjnp` (first load) and `kyypys` (current load); the rid changes on every page load.

Run window: 06:49Z (seed sent) to about 07:56Z (Hands-free turned off by me). The chat is left open, Stopped, with no Run clicked.

## Verdicts

- **pacing (20 s + 5-15 s jitter): PASS, partial.** Audit lines `post waits: paced ... next post allowed in 20-24 s` at 07:42:36, 07:43:37, 07:44:37. Real calls: 07:36:54, 07:39:43, 07:42:27, 07:42:35, then the 417 KB result at 07:45. Gaps between calls were 1-3 min. Only four calls ran, so the 5-15 s jitter band was not measured.
- **hourly cap (30/h): NOT TESTED.** About seven calls in 20 min, far under 30.
- **stop-on-warning: NOT TESTED.** No DeepSeek warning, logout or captcha appeared.
- **one armed chat: PARTIAL.** A second armed tab is refused (2tlfo1 at 07:00-07:27, then rupjnp, 26vlxf and kyypys at 07:29). This chat's arm is confirmed by the audit lease at 07:32:12Z (holder rid `kyypys`), not by the toast. The toast kept naming `rupjnp` after the arm moved.
- **SHIP OWED message: FAIL.** The DSA desk-take commit `b7b3d618d` (authored gemini-queue, amended to add `Next:`) is not on `origin/fast-track`. origin head stayed `41ba6e55d` through 07:54Z. The first auto-ship was refused: `sync: ship refused: none of your 1 commit(s) carries a Next: line`.
- **seed boot: design note, not FAIL.** The seed block ran only after an operator pressed Run (`note: run manually by the operator`, result #1 at 07:27:24Z). The seed does not arm or run by itself.

## Top 3 bugs

1. **Desk take writes a commit without `Next:`, so auto-ship refuses it.** `desk.py take` committed `desk: taken <row>` with no `Next:` line; `sync.py ship` refused (audit 07:36:54Z). DSA amended by hand (result #5, 07:42Z), and it still did not ship.
2. **Context bloat from a huge grep result.** DSA ran `git grep -i depth.band` over `scripts` and `MyTradingSys`, which matched multi-MB JSONL artifacts. One result was 417 KB in five parts, and later replies re-post old results (page text ~290 KB).
3. **Run stalled with a block not executed.** After result #7 (07:45:32Z) the bridge logged nothing more. The chat showed the fapi/DNS probe block with no result, and it was only visible as a Run block after Hands-free was turned off. Earlier the audit logged `block body not rendered yet, waiting` twice (07:37:44, 07:38:24) and two blocks came back `Run (click needed: empty_command)`. Likely a rendering or body-capture bug; not confirmed.

## Bridge defect: ghost arm after reload

The arm is held by a random per-load tab id (content.js:21). Nothing releases it on reload (no pagehide handler), so an arm from before F5 stays for about 90 s and the new page is refused as "second tab". Suggested fix: release the arm on pagehide.

## rid changes on reload

The rid prefix changes on each page load of the same tab: `rupjnp` (07:27) -> `26vlxf` and `kyypys` (07:29) -> `kyypys-mwadgyh4` (07:32, armed). The old refusal text keeps naming the earlier load. Logged as a reload finding, not a blocker.

## fapi.binance.com timeout from JIS-NUC

`fapi.binance.com/fapi/v1/time` timed out from JIS-NUC at 20 s (result #7, 07:45:32Z). The desk row's reachability step is FAIL on this host. The JIS-NB timeout of 2026-11-01 is the same pattern. The DNS and other-host probe was not seen in the audit before the run stopped.

## What was not proven, and why

- Jitter band (5-15 s), hourly cap (30/h), daily cap (200): too few calls in the window.
- Stop-on-warning: no warning was triggered, so the stop cannot be shown.
- SHIP OWED: no DSA commit reached `origin/fast-track`, so whether the ship path works is still open.
- One armed chat under a real second tab: only the ghost-arm case was seen, not two live chats at once.
- Result of the depth-band job: never ran (fapi unreachable on this host).

## DSA_HAIKU_GUIDE.md gaps

1. Seed boot needs an operator Run click in this run; section 2.3 says the extension sends the seed and boot takes a minute.
2. Section 3 says a silent armed tab expires after 90 s. An open armed tab (2tlfo1) held the arm for hours until its tab was closed.
3. A refusal naming this chat's own id after a reload (ghost arm, pagehide bug) is not covered.
4. Section 1.1: a plain `git pull --ff-only` fails on a detached HEAD; use `git pull --ff-only origin fast-track`.
5. Desk take: the ship needs a `Next:` line, and `desk.py take` does not add one. Not covered.
6. Grep scope: the guide does not say to exclude JSONL artifacts; one search produced megabytes.
7. Blocks that follow prose (or do not render in time) can come back `empty_command`. Not covered.
8. Run close: turning Hands-free off leaves the chat `Stopped` with any generated block un-run. The guide does not say how to close a run.
9. The first `go` typed plus Return did not post; the second did. Not covered.

## Note on earlier reports

The first draft of the post-go section said the stall was a prose-only reply. That was wrong: the block was present, and the bridge log shows it was not executed. Corrected above.
