# us_open_trader RUNBOOK (one US session, testnet module)

Start: `python scripts/dev/sync.py claim us-session-<day>`   (`<day>` = today's UTC date, YYYY-MM-DD)

Follow the steps in order. One command per step. Use Windows PowerShell. Run from the repo root.
"Background shell" = start the command with run_in_background and carry on. Do not make any choice that is not written here.
If a step says "stop and report", end your turn with one line to the supervisor: the step number and the error text.

## Before you start
| Need | How |
|---|---|
| `<day>` | `python -c "import datetime;print(datetime.datetime.now(datetime.timezone.utc).date())"` |
| Arm time | 13:35 UTC (the plan json `arm_utc`; re-read it in step 3). Flat time 16:30 UTC (`flat_utc`). |
| Late? | Now (UTC) is after the arm time = LATE MODE: do steps 1, 2 and 6 to 9 only (record and score, no plan build, no runner). |
| Mode | PAPER unless the supervisor's brief has BOTH the operator's own words for `--said` AND says this tree is the one the coordinator deployed for testnet. You never decide testnet yourself. |

## Steps
| # | Command | Expect | On failure |
|---|---|---|---|
| 1 | `python scripts/dev/sync.py claim us-session-<day>` | line `claimed us-session-<day>` | Says "already claimed": another machine has the day. Stop and report. Other error: retry once, then stop and report. |
| 2 | Background shell: `python MyTradingSys/execution/us_open_trader/recorder.py *> runtime_data/us_open_trader/recorder_<day>.log` | After 1 minute the log has a line `<time> <price> touched ... gaps N` | Retry once. Still no line: skip and note "recorder gap" for step 8, carry on. |
| 3 | `python MyTradingSys/execution/us_open_trader/plan.py --day <day> --out-dir MyTradingSys/research/us_open_trader_<day>` | line `plan <day>: N orders (...)` and files `plan_<day>.json` and `PLAN_US_OPEN_<day>.md` in that folder | Line `PLAN REFUSED`: no plan today, skip steps 3 to 5 and 7, go to step 8 and note the refusal text. Any other error: retry once, then stop and report. |
| 4 | `git add MyTradingSys/research/us_open_trader_<day>` then `python scripts/dev/sync.py ship -m "us_open_trader plan <day>" --result "plan <day> shipped before arm" --next "END: daily us session"` | line `shipped N file(s) to origin/...` | Retry once. Still failing: stop and report (the plan must be on trunk BEFORE the arm time). |
| 5 | Background shell, PAPER: `python MyTradingSys/execution/us_open_trader/runner.py MyTradingSys/research/us_open_trader_<day>/plan_<day>.json --mode paper *> runtime_data/us_open_trader/runner_<day>.log`. TESTNET (only when allowed above): same command with `--mode testnet --said "<the operator's words, exactly as the brief gives them>"`. | The shell ends at flat time and the log ends with a JSON block holding `"how"` | Line `refused:` in the log: no runner today, note the refusal text, go to step 6. Crash: do NOT restart it (restart is the supervisor's call). Note it and go to step 6. |
| 6 | Wait for the runner shell to end (flat time, 16:30 UTC). LATE MODE: wait until 16:35 UTC instead. | The runner shell has ended / the clock passed 16:35 | Runner still running at 17:00 UTC: stop and report. Do NOT kill it. |
| 7 | `python MyTradingSys/execution/us_open_trader/score.py MyTradingSys/research/us_open_trader_<day>/plan_<day>.json \| Tee-Object -FilePath runtime_data/us_open_trader/score_<day>.txt` | a markdown table, then a line `<day>: N trade(s) ...`, then `wrote ...<day>.jsonl` | Retry once after 2 minutes. Still failing: skip and note "score gap" for step 8. A line `(session not finished ...)` is fine: note it. |
| 8 | Add the public summary to the day's plan md (see block below), then `git add MyTradingSys/research/us_open_trader_<day>` and `python scripts/dev/sync.py ship -m "us_open_trader result <day>" --result "<day>: <the summary line from step 7>" --next "END: daily us session"` | line `shipped N file(s) to origin/...` | Retry once. Still failing: stop and report. |
| 9 | `python scripts/dev/sync.py release us-session-<day>` | line `released us-session-<day>` | Retry once. Still failing: note it in the report line. |
| 10 | Report ONE bold line: `**us-session-<day>: <mode>, <N> trades, r_net <sum>, recorder <ok/gap>, score <ok/gap>**` | - | - |

Step 8 block (adds the table to the plan md; use the exact text of the score output, nothing from the runtime files):
```
Add-Content MyTradingSys/research/us_open_trader_<day>/PLAN_US_OPEN_<day>.md "`n## Result (<mode>)`n"
Get-Content runtime_data/us_open_trader/score_<day>.txt | Where-Object { $_ -notmatch '^(wrote|\(session)' } | Add-Content MyTradingSys/research/us_open_trader_<day>/PLAN_US_OPEN_<day>.md
```
If step 7 was a gap, add one line instead: `Add-Content <that md> "`n## Result`nnot scored: <reason>"`.

## Done looks like
- Claim released. Plan files and the result table are on trunk. One bold report line sent.
- A day with no trade is a good day: the table says `no trade`. Do not change anything to force one.

## Files
| File | Where | Shipped? |
|---|---|---|
| `plan_<day>.json`, `PLAN_US_OPEN_<day>.md` (with the Result table) | `MyTradingSys/research/us_open_trader_<day>/` | YES (steps 4 and 8) |
| `readings_<day>.jsonl` (recorder), `<day>.jsonl` (score), `state_<day>.json` (runner) | `runtime_data/us_open_trader/` | NO, git-ignored runtime |
| `recorder_<day>.log`, `runner_<day>.log`, `score_<day>.txt` | `runtime_data/us_open_trader/` | NO, git-ignored runtime |

Never `git add` anything under `runtime_data/`. The recorder runs on its own until 21:00 UTC: leave it running, it stops itself.

## Hard limits
1. Testnet only (Deribit test). No mainnet, ever. Never read `.secrets/`, `.env` or key files.
2. Paper unless the supervisor's brief gives the operator's words for `--said` AND the deployed testnet tree. You never decide this.
3. Never touch `.mts_live`, a HALT file, or any process you did not start. Never stop or restart the runner.
4. No schedulers, no loops of your own, no rebase, reset or force-push. Ship only with `sync.py ship`.
5. Nothing from `runtime_data/` goes into a commit. The plan md carries public numbers only (the score table).

## Started late (after the arm time)
Do steps 1, 2, 6 (wait to 16:35 UTC), 7, 8, 9, 10. No plan build, no runner, no ship before the arm time. If no `plan_<day>.json` is on trunk (`git fetch origin fast-track` then `git ls-tree origin/fast-track MyTradingSys/research/us_open_trader_<day>/`), skip steps 7 and 8 and write "no plan today, record only" in the report line. If it is there, run `git merge origin/fast-track` first so steps 7 and 8 have the files. The record is still wanted. A thin US holiday session is fine: record and report as usual.
