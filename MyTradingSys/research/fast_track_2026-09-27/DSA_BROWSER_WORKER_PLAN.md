# DSA browser worker - plan (2026-09-29, supervisor)

Goal: DSA (the chat model in the operator's own logged-in Chrome session) becomes a second queue worker next to
Qwen. It takes packed tasks from the NUC-QUEUE, pastes the prompt into the chat, waits for the answer, and writes a
reply.json in the SAME schema as nuc-worker.ps1, so `queue_tool.py verify` and the hourly gate work unchanged.

## Where it runs: DESKTOP (decision, re-confirmed by operator 2026-09-29; launcher scripts/worker/start-dsa-worker.ps1)
- The queue lives on the desktop (Dumps/workers/NUC-QUEUE); no share latency, no second copy of the repo.
- The desktop is awake 24/7 already. The laptop stays free for you (and can still be an Ollama worker, Track A).
- Uses a SEPARATE Chrome profile (`F:\MTS\dsa\chrome-profile`; downloads + logs under F:\MTS\dsa, operator 2026-09-29) started with `--remote-debugging-port=9222`, so it
  never touches your normal Chrome, and you can watch it work in its own window.

## Ground rules built into the worker
- Your own account, logged in by you by hand once. The worker never types passwords.
- Human-in-the-loop on any challenge: if a login page, CAPTCHA or "verify you are human" screen appears, the worker
  stops, sets heartbeat `needs-human`, and waits. It never clicks or solves a challenge and uses no stealth/anti-detection
  tricks. You clear it, it continues.
- Paced like a person: one task at a time, >= 60 s between tasks, hourly and daily caps in config (default 10/h, 60/day).
  If the site rate-limits or errors 3 times in a row -> stop and write `needs-human`.
- Only tasks packed for the DSA lane. Qwen tasks are untouched.

## Architecture (one Python module + config, ~300 lines)
```
scripts/worker/dsa_worker.py          loop: claim -> run -> reply; pacing; heartbeat_dsa.json; log
scripts/worker/dsa_page.py            ChatPage adapter (Playwright over CDP): new_chat, send, wait_done, read_last, challenge_seen
scripts/worker/dsa_selectors.json     site selectors (input box, send, stop-generating, last answer, copy button, challenge markers)
scripts/worker/test_dsa_worker.py     offline tests with a FakePage (no browser)
Dumps/workers/NUC-QUEUE/incoming_dsa/ the DSA lane (queue_tool pack --lane dsa)
```
Flow per task: move `incoming_dsa/<id>.task.json` -> `claimed/` -> open a fresh chat -> paste `prompt` -> send ->
done when the stop button is gone AND the answer text is unchanged for 5 s (timeout from `num_predict`, cap 15 min)
-> read the answer via the site's copy button (keeps markdown/code fences), fallback innerText -> write
`done/<id>.reply.json` {schema 1, id, worker "dsa-web", host, model "dsa-web", response, done_reason stop|timeout,
worker_status ok|error|needs-human, started/finished_utc, wall_seconds}. On crash: task goes back to `incoming_dsa/`.
Prompt too long for one paste -> fail the task with `error: prompt too long` (pack it smaller; no auto-splitting).

## What to send to DSA vs Qwen
DSA lane: transcript extractions (DSA already did 4 clean ones), formula audits, spec reviews, research summaries -
anything long-context/reasoning. Qwen lane: code implementations from specs (runs offline, no pacing).
Gate is unchanged: quote checker for extractions, spec-derived tests for code, spot-check one claim per report.

## Build steps
| # | Who | Step | Done when |
|---|---|---|---|
| 1 | code mode (Sonnet) | queue_tool `pack --lane dsa` + status line for the lane; dsa_worker.py + FakePage tests | tests pass, fail on pre-change code |
| 2 | code mode | dsa_page.py Playwright adapter + `--calibrate` (prints which selectors match) + `start-dsa-chrome.ps1` | calibrate runs against a local test page |
| 3 | Jishu | `pip install playwright` (no browser download needed: it attaches to your Chrome) | `python -c "import playwright"` ok |
| 4 | Jishu | run `scripts/worker/start-dsa-chrome.ps1`, log in to DSA in that window by hand, leave it open | chat page visible |
| 5 | Jishu + DSA | `python scripts/worker/dsa_worker.py --calibrate`; if a selector misses, right-click > Inspect the element, paste the HTML snippet to DSA, DSA gives the CSS selector, put it in dsa_selectors.json | all 6 selectors OK |
| 6 | Jishu | `python scripts/worker/dsa_worker.py --once` on a tiny test task (`queue_tool pack --lane dsa` a hello spec) | reply.json in done/, verify passes |
| 7 | Jishu | start the loop: `python scripts/worker/dsa_worker.py` (hidden window optional) | status shows `DSA-WORKER idle/running` |
| 8 | supervisor | route the next extraction/audit specs to the DSA lane; compare quality vs Qwen on 3 tasks | note in SUPERVISOR_LOG |

## Risks
- The site changes its HTML -> selectors break -> worker sets `needs-human`; redo step 5 (5 min).
- The provider may limit or ban accounts that automate the web chat; pacing keeps it modest but not risk-free.
  Use it for tasks where losing the lane for a day is acceptable. Qwen stays the fallback for every task.
- Chat answers can be cut off mid-way: `done_reason timeout` + the normal gate catches it.
