# Supervisor C runbook: 24 h super session on the desktop (2026-11-11 13:14Z to 11-12 13:14Z)

Written 14:20Z by the Fable Supervisor for the Sonnet model that takes over THIS session (operator order 14:16Z: "I will change
the model from Fable to Sonnet in this session - make sure Sonnet follows your 24 hr work plans"). Same session, same role
(`roles/supervisor.md`), same worktree. Read this file at every wake after a compaction; `plan` output outranks it where they differ.

Operator order 13:35Z: "Get latest DSA fixes on Desk - Start using all LLMs for the next 24 hour super session you will run
from here." Recorded in OPERATOR_DECISIONS.md (2026-11-11 13:20Z entry).

## 0. Fixed facts
| Item | Value |
|---|---|
| Login, machine | C, hostname JIS-NB = the desktop |
| Work period | ends 2026-11-12T13:14Z. No hand-over inside it; the 5 h stop is a pause, not an end |
| Weekly cap | 85 % (reset 2026-11-17T20:00Z). At 14:16Z: 5 h 17 %, week 7 % |
| Ship from | `C:/Users/E-ngineers/IdeaProjects/mts-jis-nb-supervisor-c-2026-11-11-l5` (ship refuses in the main checkout) |
| Main checkout update | `git -C C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed merge --no-edit origin/fast-track` (other merge spellings are denied) |
| Workers | background Agents, `model: sonnet` (haiku for mechanical), 2 chained cards each. Never start_session, never Fable, Opus only if he names it |
| Asks to the operator | only money, mainnet, going private, deleting data, live-tree change |

## 1. Every wake (operator turn, worker note, watcher exit): the loop
1. `get_usage`.
2. One Bash call in the main checkout:
   `python scripts/dev/supervisor.py plan --login C --five <5h%> --five-reset <5h resetsAt> --week <week%> --week-reset 2026-11-17T20:00:00Z --running <n> --hours 24`
   (`n` = your Agents still running; `--five-reset` changes every 5 h, copy it from get_usage).
3. Do every `RUN` and `SPAWN` line in one message. Copy `OPERATOR` lines into the reply.
4. If the watcher is not running: `python scripts/dev/supervisor.py wait --timeout 50m --login C` with run_in_background (no `--running` arg).
5. LAST call: `python scripts/dev/supervisor.py watchcheck --login C`; end the turn only on exit 0.
The Stop guard blocks a turn end with no `plan` in the last 10 min: steps 1-2 and 5 run before EVERY turn end, also after an Agent note.

## 2. The four model lanes (keep all of them fed, in this order of cost: cheapest first)
| Lane | State 14:20Z | How to feed it | Check |
|---|---|---|---|
| Gemini (NUC) | running `tom-fabio-rebuild-from-beginner-videos-1109:low` (task c_gem_tf_1111, log `F:\MTS\gq\c_gem_tf_1111.log`) | section 3 | Supervisor B on the NUC reviews and ships Gemini output; you only launch |
| DeepSeek (DSA, desktop bridge) | bridge 0.7.38 up; chat not armed until the operator reloads the extension | `python scripts/dev/desk.py post ... --target DSA` for run-and-report cards (DSA_DELEGATION.md) | `python scripts/dev/aibridge_health.py`; `python scripts/dev/dsa_watch.py` |
| Claude (login C) | `plan` decides; 1 new worker per wake | SPAWN lines | section 4 |
| GPT / Codex (lab host) | DOWN: Codex login 401 for 280+ h | nothing until the operator logs in on the NUC | `plan` prints the lane state |
| Paid API credit | NOT started. Money decision: only after he says "use the credit" (expires 2026-11-17) | `api_job.py --engine api` | - |

## 3. Gemini on the NUC (do it yourself, never hand the operator a command)
- Always `<card>:low`. One `gemini_queue.py run` at a time. Lane floor: at least 4 ready `[GEMINI]` cards; `plan` prints
  `LANE LOW GEMINI <n>` and a `RUN Session_Planner (Agent, sonnet)` line when it is under: run that Agent.
- Launch: copy the scratchpad pattern below to a `.ps1` (every statement on ONE line; here-strings and multi-line blocks do nothing
  over the gate), then `ssh -i ~/.ssh/nuc_gate -o BatchMode=yes -o ConnectTimeout=10 e-ngineers@192.168.29.110 ps < file.ps1`.
```
$n = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'gemini_queue\.py run' -and $_.Name -match 'python' }).Count; "gemini_queue procs: $n"
$l = @('Start-Transcript -Path F:\MTS\gq\<name>.log -Force', 'Set-Location F:\MTS\mts-gemini', 'git fetch -q origin', 'git merge --ff-only origin/fast-track | Out-Null', 'foreach ($c in "<card1>","<card2>") { "CARD $c"; & C:\Users\E-ngineers\AppData\Local\Programs\Python\Python314\python.exe scripts\dev\gemini_queue.py run ($c + ":low"); "EXIT $c $LASTEXITCODE" }', 'Stop-Transcript')
if ($n -eq 0) { Set-Content -Path F:\MTS\gq\<name>.ps1 -Value $l -Encoding ASCII; schtasks /Create /TN <name> /TR "powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File F:\MTS\gq\<name>.ps1" /SC ONCE /ST 23:59 /RU e-ngineers /IT /F; schtasks /Run /TN <name>; "LAUNCHED" }
```
- Read progress: a one-line `.ps1` with `Get-Content F:\MTS\gq\<name>.log -Tail 20` through the same gate. Delete the finished
  one-shot task (`schtasks /Delete /TN <name> /F`) in the next launch script.
- YouTube work needs captions fetched and `verify_extract_quotes.py` exit 0 (B checks this at review).
- After a batch: B posts "NUC queue empty" on the signal board; launch the next cards from `tasks.py next` tagged `[GEMINI]`.

## 4. Verifying an Agent note (before you believe it)
1. `python scripts/dev/role_loader.py verify --text - --role Builder` with the note on stdin (0 = ok).
2. `git merge-base --is-ancestor <sha> origin/fast-track` exits 0 and the commit body has `Result:`.
3. `git -C <its worktree> cherry origin/fast-track` is empty. An Agent that ends on "waiting for the ship" has NOT shipped:
   SendMessage to its agent id with "finish the ship as one blocking call" (this happened at 14:01Z).
4. Live-path or gate-script change: a diff-only review Agent (sonnet) before the ship.
CI RED on trunk: the author reverts within 10 min; never forward-fix.

## 5. Open items at 14:20Z, in order
| # | Item | Done when |
|---|---|---|
| 1 | Builder Agent a1aa09248a181caad re-shipping AIBridge 0.7.39 (DSA defects card dsa-live-test-defects-1110; OI poller backed out) from worktree `mts-jis-nb-builder-c-poller-dsa-1111` | sha on trunk, verified per section 4 |
| 2 | Then install it on the desktop: merge the main checkout, `python scripts/dev/aibridge_install.py F:/AIBridge --restart-agent`, `python scripts/dev/aibridge_health.py` shows 0.7.39 everywhere; `python scripts/dev/mts_signal.py ack q-136c7a done` | health line all 0.7.39 |
| 3 | Tell the operator once (YOU DO): (withdrawn: no Chrome until the operator names a deviceId) chrome://extensions, Reload AIBridge, F5 the DeepSeek chat, type `Start DSA bridge` | `dsa_watch.py` shows the chat armed; then `mts_signal.py ack b-ea3809 done` |
| 4 | Once DSA is armed: post 3-5 run-and-report cards to DSA | desk shows them taken |
| 5 | Session_Planner Agent (sonnet): seed `[GEMINI]` cards to 4 or more ready, `[CODEX]` to 8 | `plan` no longer prints LANE LOW |
| 6 | Republish stale pages mts_layer_map and mts_home with ONE Haiku Agent (Artifact read without `path` dumps the whole page: never do it in this session), then `python scripts/dev/artifacts.py publish-record --slug <slug>` and ship registry.json | `artifacts.py` status not STALE; note to B |
| 7 | 14:45Z: [US open prep] session local_835a44e0 reports its P3 result; relay one line; archive it and local_c937b49d (Live Aid helper, done e4cc3940e) when idle | both archived |
| 8 | Live Aid helper's finding: one Live Aid link is manual (its 14:15Z report). File a raw card if no twin exists | card id |
| 9 | Each wake: `mts_signal.py read`; answer asks first (ask > HIGH > normal); B's notes about C's pages or Gemini are work for you | no overdue ask on C |

## 6. Hard limits (never)
Testnet only. Never read `.secrets/`, `.env`, keys; never print `F:\AIBridge\extension\background.js` or `F:\AIBridge\src\config.json`.
Repo is public: no runtime, order or account data. No rebase, reset, force-push, stash. No schedulers except the one-shot `/IT`
NUC task above. Never build, deploy, restart live processes, touch HALT or the live tree. Never the 61 execution tests.
Chrome: withdrawn until the operator names a deviceId. Ship only with `sync.py ship` and `Result:` / `Next:` lines (hook, role, start paths also `Reach: Q1-Q8`).

## 7. Replies to the operator
Bold result first; a table for rows; `YOU DO` (max 3) only when he must act; under 8 lines; plain words; only what is new since
the last reply. Do implied work at once, never "want me to?". Record every chat decision in OPERATOR_DECISIONS.md the same turn.

## 8. End of the work period (after 2026-11-12T13:14Z, or when `plan` prints TRANSIT NOW)
Stop spawning, drain, `get_usage` + `plan`, then `python scripts/dev/supervisor.py handover --login C --note "<next step>"`,
one Session log line in SUPER_SESSION.md, one docs-only `sync.py ship --release supervisor-C-2026-11-11-L5`. Leftovers to name:
NUC one-shot tasks to delete, NUC task `mts-winwatch-once`, CI verdicts not awaited on 66c1b631, e1323dcb, 975ecf30, e5e13371.
