# DSA operator guide for a Haiku (or any Claude) session

Read this before you start, test, or babysit a DSA chat. DSA = DeepSeek working the repo through the AIBridge Chrome extension and the local agent. Written 2026-11-10 after the first live test of bridge 0.7.34 lost an hour to avoidable stops.

## 0. Hard rules (never break)
- Use only Claude in Chrome "Browser 1", deviceId `e63ddb91-d95b-47dc-a506-ba62b2e64996` = Chrome Profile 5 = DeepSeek account jishusharma1985.
- Never use Profile 4 or the jishu.awgp account (suspended until 2026-11-11 10:22Z). Never create or use another DeepSeek account.
- Never run `dsa.py start --open`.
- Never print, cat or diff `F:/AIBridge/src/config.json` or `F:/AIBridge/extension/background.js` (they hold the bridge token). Read the repo copy `scripts/aibridge/extension/background.js` instead.
- Stop at once on a DeepSeek logout, captcha, abuse/rate warning or "suspended" text. Report it and do nothing else.
- Do not touch the live trading system. Do not change bridge code (`scripts/aibridge/`, `F:/AIBridge`): the operator owns it.
- Every background shell gets a timeout under 30 min.

## 1. Before you open any chat
1. `cd F:/MTS/b-work && git fetch -q origin && git checkout --detach origin/fast-track`
2. `python scripts/dev/aibridge_health.py`: installed = running = trunk version. If not, stop and report; the operator installs.
3. `python scripts/dev/dsa_watch.py`: baseline for pending / taken / STALLED per lane.
4. Load the Chrome tools in ONE ToolSearch (tabs_context_mcp, navigate, computer, read_page, get_page_text, find, tabs_create_mcp, select_browser, list_connected_browsers). Select Browser 1 only.

## 2. Booting DSA in a chat
1. Open https://chat.deepseek.com in a NEW tab, start a NEW chat.
2. The AIBridge panel label must read `extension X | this page Y | disk Z | agent W - all match`. Anything else is a MISMATCH: press F5 on the chat once; if it persists, report it.
3. Type exactly `Start DSA bridge` and press Enter. The extension fetches the seed from the agent and sends it. Boot takes a minute.
4. **ARM the chat.** Tick the hands-free (auto-run) checkbox in the panel. Without it DeepSeek's `Run` button just waits and nothing reaches the bridge. The boot does not arm by itself (0.7.33+). Do not click `Run` by hand when you are testing the bridge: a manual click hides whether auto-run works.

## 3. Arming refusals and how to clear them
- `second_tab_refused: chat <id> in this browser profile is already armed`: only one armed chat per profile. A silent armed tab expires after 90 s (loop.js `ARM_TTL_MS`), so if you still see it, some tab in that profile is still open and ticked.
  - **Ghost arm (found 2026-11-10):** every page load gets a random tab id (content.js:21) and a reload does not release the arm. After arm then F5 (or a closed tab), the old id holds the slot for 90 s and the new page is refused, often naming a chat id that is really your own earlier load. Do not F5 or retry in a loop: wait 100 s with no clicks, then tick hands-free once.
  - The refusal text can also stay on screen after the cause is gone; an F5 clears it, but start the 100 s wait after the F5.
  - Your browser tools only see tabs your own session opened. You cannot see or close the operator's or an older session's tabs. Ask the operator to close or untick that tab; do not retry in a loop.
- `account_in_use` / lease refused: another machine holds the DeepSeek account lease (one machine per account). Report the exact panel text; do not force it.
- Warning cooldown: the extension stops hands-free on its own after a DeepSeek warning. Leave it off and report.

**Is it armed? Do not trust the red toast.** It can stay on screen after the arm succeeded. Check instead: the Hands-free box is ticked with a counter (0/200), and the bridge audit tail has `EXT-EVENT lease acquire deepseek-default -> ok` (`grep EXT-EVENT` on `F:/AIBridge/src/audit.jsonl`, never print token fields).

## 4. What normal looks like (0.7.34 limits)
- Every auto post is paced: 20 s + 5-15 s jitter since the last post of the profile, max 30 an hour, 200 a day. A "paced" status is not a hang. An hour or day limit stops hands-free; that is the guard working.
- A reply can hold up to 6 command blocks; they run in order and one `[AIRUN RESULT]` comes back.
- One command is a 10-20 s round trip; timeout default 60 s, max 300 s; output cut at 262144 bytes.
- Click-needed commands (forced deletes, hard resets, taskkill, forced pushes) wait for a human click. That is by design, not a stall.
- DSA must not write under `F:\AIBridge` or `scripts\aibridge\`. It works in its own worktree `../mts-dsa-<slug>` on branch `<host>/dsa-<slug>`.

## 5. What to watch every ~10 minutes
- Page text: is a block waiting, running, or has the result come back (`[AIRUN RESULT]`)?
- `python scripts/dev/dsa_watch.py` (pending / taken / oldest_pending, STALLED flag).
- New worktrees and branches: `git worktree list`, `git branch -a | grep dsa`.
- Card state changes in `MyTradingSys/system/tasks/*.json`.
- **Shipping.** DSA commits locally and never pushes by itself. Work is done only when `python scripts/dev/sync.py ship` landed it and `git cherry origin/fast-track <dsa branch>` shows nothing. Yesterday's DSA run left 3 refined cards stranded in a worktree for that reason. If a DSA chat ends with unshipped commits, say so in the report.

## 6. Reporting
Write `MyTradingSys/system/DSA_LIVE_TEST_<date>.md`: one line PASS / FAIL / NOT TESTED per fix (pacing, hourly cap, stop-on-warning, one armed chat, SHIP OWED message, seed boot), exact panel texts, and bugs with evidence. Commit only that file; `git pull --rebase`, push to `fast-track`.

## 7. Known design notes
- An idle armed tab blocks every other chat in the profile until it is unticked or closed (the heartbeat keeps it alive).
- The boot does not arm itself; someone must tick hands-free.
- Stale refusal text survives until F5.
- DSA fixes still open: short boot line, short core prompt, the 11 review prompt fixes, a stall check in dsa_watch, the background-tab timer fix, HALT on the path only.

Spec and limits: `MyTradingSys/system/AIBRIDGE_LANE.md`, `scripts/aibridge/docs/V07_CONTRACT.md`, `DSA_SESSION_PROMPT.md`, `python scripts/dev/dsa.py --help`.
