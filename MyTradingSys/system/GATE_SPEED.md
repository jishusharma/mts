# GATE_SPEED - ship gate wall time (2026-10-18, operator: "sessions take too long, the ship gate is the main cause")

## Measured (before)
- 7 full ship gates of one session (ship*.txt, 4 jobs): clean wall 469-636 s (one loaded run 1069 s). Step medians:
  3xt 311 s, 4h 271 s, 3k 270 s, 5b 237 s, 4 (test_turn_meter.py alone) 195 s, 4g 156 s.
- All 30 tree timing logs (4106 step rows): medians 3xt 671, 3k 523, 5b 425, 4b 383, 4g 371 s (gates overlap: 2 slots x 4 jobs).
- Why full: last 200 trunk pushes = docs 112, full 59, smoke 29. That session's ships were full only because `.claude/settings.json`
  changed ("matches no rule"); others: research data (.tsv .gz .err), .gitignore, .aiexclude, scripts/dev non-.py data.
- Late failures: 4d (a 6.6 s step) printed FAIL at +438 s, gate ran on to 469 s; 4g (research_kit line refs) at +152 s, ran to 547 s.
  Each fix = full rerun (~9 min). Fail counts (timing logs): 4c 25, 4b 20, 4h 15, 3sig 12, 3xt 9, 3tl 9.
- Push race: 3 of 4 passing ships lost at least one race; one died on `git fetch ... incorrect old value provided` (shared ref).

## Changes (sync.py ship only; CI, auto_deploy and a bare run_all_tests keep their argv and run every step)
| # | Change | Saves |
|---|---|---|
| D1 | `--precheck`: CHEAP_STEPS (median <= 25 s) + step 4t (pytest of the <= 12 `MyTradingSys/tests` files that reference a changed module or name a changed file, slow files excluded) run first, 2 at a time, no gate slot. Any failure: every other step is NOT RUN. | repeat failure ~9 min -> precheck time |
| D2 | `--fail-fast`: after the first failure in the main phase, steps not yet started are NOT RUN (not timed; the summary fails closed). `--slot`: run_all_tests takes the gate slot around the main phase only. | rest of a doomed gate; slot not held by cheap steps |
| D3 | `--record` (`<worktree git dir>/mts_gate_record.json`): a step that passed on this exact clean tree (untracked files count), same step signature, same python, < 24 h, is not run again. Written atomically, never when HEAD moved mid-gate. Ignored when `CI` is set. | push failed after ALL TESTS PASSED, or one flaky step: rerun = that step |
| D4 | Fetch retried 3x with jitter; ship push 3 -> 5 tries, 1-5 s jitter; a lost race re-runs the gate once only when the incoming commits touch our paths or a module our .py files reference (`race_overlap`). | lost races stop failing |
| D5 | gate_select: research data suffixes (.tsv .gz .err .log .png .svg .parquet .pdf .jpg) = docs; `.gitignore`, `.aiexclude`, `.claude/settings.json`, `scripts/dev/<x>.tsv/.json/.csv/.html` = smoke (ALWAYS + steps whose tests name the file); settings.json adds 3js. A `.txt` on the live path and `run_extra_tests.py` are full. | most "full" ships become smoke |
| D6 | Smoke 3xt runs `run_extra_tests.py --only <extra_subset>` (changed file, its test_<name>, its study folder, folder of a changed shared module, tests that reference or name the change); smoke 5b runs `layer_subset` (changed layer folder + referencing modules; all when a file is directly in layers/, a shared module, or a folder without tests). Closes a gap: `scripts/dev/trace.py` never ran `test_trace.py`. | 3xt 300-670 s, 5b 240-425 s -> seconds |
| D7 | `test_turn_meter.py` calls `turn_meter.handle()` in-process; the garbage-stdin and one output test keep the real hook process. | 195 s -> 7 s |
| 3js | `config_check.py`: settings.json parses, every hook script exists, `.secrets/` and `.env*` stay ignored (now in `.gitignore`). | a broken hook no longer ships on smoke |

## Reviews (Sonnet + Haiku, one-time, 2026-10-18) and what changed
- D3 reuse across trees was unsound (import graph, deleted files): cut to same-tree only. Record atomic with a lock retry.
- Retry re-gate must see semantic overlap, with a cap: `race_overlap` + REGATES = 1. Separate SHIP_PUSH_TRIES (claims keep 3).
- settings.json is read by tests and hooks: 3js plus name-matched steps. Secrets sentinel added. Renames: `--no-renames -z`.
- Fail-fast needs its own NOT RUN state; skipped steps must not be timed. Shared modules (`__init__`, `conftest`, common*, _*) widen.
- Defaults taken (OURS): 2 precheck jobs, 12 targeted files (truncated, the shards still run them), 1 re-gate, 24 h record age.

## Quality guards
Full mode still runs every step (D1 reorders, D2 only stops a run that already failed). CI runs the whole suite on both OSes; it
never passes the ship flags. A failed step is dropped from the record. Linux-only failures stay CI's job (`ci_watch.py`).

## Not done (next)
Machine-wide process budget across concurrent gates; FIFO slot queue; Windows CI on selected steps only.
