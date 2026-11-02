# AIBridge root causes, ranked (Builder, 2026-11-02)

Source: `F:/AIBridge/src/audit.jsonl` (3016 rows at start; 1703 carry a command, 1313 do not), repo `scripts/aibridge/`, desk rows.
Audit is agent-side only: extension-side failures (focus, dropped reply, stale extension) leave no row. Status: R = reproduced, E = evidence in data, H = hypothesis (needs the real-page run).

| # | Cause | Evidence | Status | Fix |
|---|---|---|---|---|
| 1 | **Extension/agent version drift is invisible.** Nothing compares the loaded extension to the disk copy or to the agent (`grep mismatch content.js`: none). Unpacked extension needs a hand reload; JIS-NB never installed (b-51fcf3, b-b635db). The 10-22 to 10-29 hole (6 ok rows in 8 days, only probe rows; 10-26 desk row "reload the extension" pending) fits a dead/stale link. | 6 ok rows 10-22..10-29 vs 100-200/day either side; pending operator row 20261026 | E (fit), cause of the hole H | Extension fetches its own disk manifest and agent `/ping`; mismatch = red panel + message in chat; idle + disk newer = self-reload; `aibridge_health.py` prints the same; installer verifies after install. |
| 2 | **Permission walls.** `manual_click_required` 94 (Remove-Item -Recurse -Force, git branch -d, git checkout --, rd), `cwd_outside_roots` 5 (4 for `F:\AIBridge`: DSA cannot test the bridge), `denied_path` 13, `path_outside_roots` 5. Recent clicks (7, 10-30..11-01) are cleanup of DSA's own worktrees. | counts above | E | Narrow allow only inside DSA's own worktrees `mts-dsa*` and temp (delete/branch -d/checkout --); sandbox bridge copy on another port under temp. Everything else unchanged. |
| 3 | **Non-zero exit stops the reply (E5, 0.7.7)**, a read included. Non-zero ok-exits: 22 on 10-31, 18 on 11-01 (before 0.7.7: 0 to 10/day). | audit exit != 0 | E (volume); chain damage H | Run the real-page chain test; receipt must name the unrun blocks (NOT_RUN) so DSA re-sends only those. |
| 4 | **Hidden/covered tab.** Page timers throttle; port tick plus Worker tick were added (0.7.x). DeepSeek's own render may pause when occluded, so reply text never settles ("dropped", "hands-free off, no final answer"). | desk 20261031-095323, 20261101-113539, 20261101-054813; watch log has 3 lines, no proof | H | Needs the real-page run with the tab hidden; measure settle time hidden vs visible. |
| 5 | **Probe noise: 651 `not_found` + 651 write-aborted pairs (43% of the log).** A bare TCP connect (`supervisor.py:1112 _local_bridge`) sends no request line, so the agent logs `not_found` and fails writing the 404. | **R**: one connect+close added exactly 2 rows | R | Supervisor probes `GET /ping`; agent drops an empty request line without an audit row. |
| 6 | **Timeouts 22, truncations 6, `Start` "directory name invalid" 4.** | audit | E | Last: timeout receipts are explicit already; check cwd-missing message. |
| 7 | **Tool defects reported by DSA** (long lines cut, inline ignores repo, inline reports pass on failure, replay of blocks 1-2, output floods chat). | 8 open desk rows, DSA-written | unverified | Verify each by test before fixing (desk row 20261031-100421 rule). |

Also: `aibridge_install.py` has no argparse, `--help` ran an install (fix in ship 1).

Not opened (and why): live self-edit of the running agent, `.secrets`/`.env`/keys, HALT, live tree, Stop-Process/taskkill outside DSA's own children, mainnet, paths outside roots, nested/hidden shells. The page is third-party; anything on it reaches this machine.

## Added after reproduction (0.7.12 to 0.7.16)
| # | Cause | Status | Fix / evidence |
|---|---|---|---|
| 8 | **A short final answer ended the chain.** `ANSWER_MIN_CHARS` was 10: DSA answering "Done." or "ok" (the notice itself says "reply ok") read as a dropped generation: notice, then stop banner, hands-free OFF. Hits the end of any chain with a terse last line. | **R** (fake-chat run) | Threshold 2; `test_short_final_answer_is_an_answer_not_a_dropped_generation` fails with 10, passes with 2. |
| 9 | **`git branch -d` was click-gated by a case-insensitive regex meant for `-D`** (4 of the 7 recent clicks). `git checkout --` in DSA's own `mts-dsa-<chat>` worktree is its own scratch (2 of 7). | **R** | `(?-i:branch -D)`; own-worktree exemption (no cd out, no `..`). 5 other clicks (recursive deletes of other sessions' worktrees) stay clicks. |
| 1b | Version drift now detected: extension compares disk manifest and agent `/ping` every 60 s; panel outline red; `[AIRUN WARNING]` line in every receipt; stale extension reloads itself when idle; an orphaned page reloads itself (idle, max once per 10 min). | fake-chat tests V1/V2 | 0.7.14+; the real-page click-free update is unproven until it runs on the NUC. |
| 3b | Long chain on the fake chat, tab simulated hidden: 54 blocks in 10 replies, b17 exit 1, b33 timeout, one dropped reply: 54 of 54 ran exactly once, notice posted at 46 s, no stop banner. E5 (stop on non-zero) did not break the chain: unrun blocks were reported (`blocks_run=4 not_run=2`) and re-sent. | **R** (fake page only) | `test_aibridge_chain.py`. The real chat.deepseek.com run is still to do. |

Opened: `git branch -d`; `git checkout --` in own worktree; DSA may edit and test a copy of `scripts/aibridge` in its own worktree (prompt change), never `F:\AIBridge`.
Not opened: recursive deletes (all 5 recent were other sessions' worktrees, with variable paths), `F:\AIBridge` as cwd, live self-edit, kills, secrets, live tree.
