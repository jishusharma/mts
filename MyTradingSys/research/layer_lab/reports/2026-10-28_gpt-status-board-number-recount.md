# GPT status board number recount

**Verdict: FIX-FIRST.** I found 9 printed UTC commit-count mismatches (including repeated today/yesterday counts) and a stale worktree input. The board is useful, but its UTC labels are not reliable until its date boundaries use UTC.

## Method and snapshot

I ran `python scripts/dev/status_board.py` once from the claimed scratch worktree at approximately 2026-10-29 20:38Z and preserved the complete output below. I did not read `scripts/dev/test_status_board.py` before recomputing. Independent follow-up reads were at 20:41Z; point-in-time host values may have drifted slightly. Task JSON enumeration, task status, signal lines, git timestamps, disk usage, temp entries, gate history, claims, and worktree count were independently collected. No product code was changed.

## Number-by-number reconciliation

The source reads only top-level MyTradingSys/system/tasks/*.json, not database totals printed by tasks.py status. Independent top-level count at 20:41Z was 617 cards: raw 25, refined 65, ready 115, active 1, blocked 32, done 311, dropped 68. Lane counts were SONNET 410, JIS-NB 28, OPUS 21, CODEX 116, DSA-NUC 13, HAIKU 20, DSA 8, DSA-NB 1. The dashboard does not print a full state or lane breakdown, so those unprinted breakdowns are scope evidence, not output mismatches. tasks.py status reports aggregate done 621/dropped 97; this is a different source scope and is not compared as though it were the top-level glob.

| Printed item | Board value | Independent value / command | Result |
|---|---:|---|---|
| Status week budget up to | 84% | Newest A budget signal says week 84% (`mts_signal.py read`) | Match |
| Login A 5h / week / seen / reset | 41% / 84% / 18:19Z / 2026-10-30 09:00Z | `mts_signal.py read`, newest A line at 1819Z | Match |
| Login B 5h / week / seen / reset | 18% / 51% / 17:57Z / 2026-11-01 17:00Z | `mts_signal.py read`, newest B line at 1757Z | Match |
| Login C 5h / week / seen / reset | 6% / 22% / 17:16Z / 2026-11-03 20:00Z | `mts_signal.py read`, newest C line at 1716Z | Match |
| Cards closed today / yesterday | 8 / 88 | Count top-level task JSON with `state=done` and `closed[:10]` at 20:41Z | Match |
| Commits on trunk today / yesterday | 81 / 672 | Recount `git log origin/fast-track --no-merges --format=%cI`, parsed and converted to UTC: 87 / 537 | **Mismatch (2)** |
| Spend vs output per login | NOT_IN_DATA | No `closed_by_login` field in task-card data; cannot attribute closures | Correctly unavailable |
| Open CRITICAL / CRUCIAL (status banner) | 48 total | Top-level task JSON open `weight` counts: 15 + 33 | Match |
| Trunk commits per UTC day, 2026-10-29 | 81 | UTC parse of `%cI`: 87 | **Mismatch** |
| Trunk commits per UTC day, 2026-10-28 | 672 | UTC parse of `%cI`: 537 | **Mismatch** |
| Trunk commits per UTC day, 2026-10-27 | 228 | UTC parse of `%cI`: 262 | **Mismatch** |
| Trunk commits per UTC day, 2026-10-26 | 265 | UTC parse of `%cI`: 300 | **Mismatch** |
| Trunk commits per UTC day, 2026-10-25 | 273 | UTC parse of `%cI`: 254 | **Mismatch** |
| Trunk commits per UTC day, 2026-10-24 | 119 | UTC parse of `%cI`: 203 | **Mismatch** |
| CI six rows (94c57a6, 9a19241, 7877fdc, f75e053, 46ae9a7, 40f9181) | running, failure, failure, failure, success, success | Independent `ci_watch.fetch()` at 20:41Z: failure, failure, failure, failure, success, success. 94c57a6 completed after the captured board read | Board was point-in-time; later completion explains difference |
| CI red duration | 10 min | Failing streak begins at 20:26:13Z; at the board read near 20:38Z this is about 12 min, consistent with rounded/truncated display | Plausible |
| Gate median and last five ships | 6 s; [1, 1, 1083, 6, 10] | Independently grouped `runtime_data/gate_timing.jsonl`; median 5.83 s, same five values | Match |
| Ships running / stalled over 30 min | 0 / 0 | Captured process snapshot said 0 / 0; not re-sampled after output | Point-in-time only |
| Solved today, top 3 | WaveTrend atlas; Krown quote audit; Cloud unshallow clone | Top 3 task cards sorted by `closed`, same IDs/titles | Match |
| Dedupe/cleanup commits today | 0 | UTC-date scan finds `7fa356aff104` on 2026-10-29; local-midnight scan used by script excludes it | **Mismatch (1)** |
| Stuck active cards >24 h | 1, `bug-burn-cap-stops-all-work` | One top-level active card exceeded 24h from `taken` at snapshot | Match |
| Stale claims >24 h | 29 (first three shown) | `sync.py claims` returned 29 stale claim lines at 20:41Z; first three agree | Match |
| GPT account/plan | NOT_IN_DATA | `codex_usage.json` has null plan | Correctly unavailable |
| GPT 5h / week usage; reading | 0% / 0%; 2026-10-29 20:18Z, age 0.3h | JSON `allowance.window_used=0`, `week_used=0`, `at=20:18:06Z`; age about 0.34h at captured time | Match |
| Gemini usage / reading | NOT_IN_DATA | No Gemini usage source on trunk; output names missing measurement | Correctly unavailable |
| Open CRITICAL / CRUCIAL | 15 / 33 | Top-level JSON open weights: 15 / 33 | Match |
| Parked / raw / blocked | 0 / 25 / 32 | `tasks.py status` parked=0; task JSON states raw=25, blocked=32 | Match |
| C: free | 78.4 GB | Independent `shutil.disk_usage`: 78.3 GB at 20:41Z | Within 0.1 GB and three minutes later |
| D: free | NOT_IN_DATA | `shutil.disk_usage('D:\\')` raised `OSError` | Correctly unavailable |
| F: free | 214.6 GB | Independent `shutil.disk_usage`: 214.6 GB | Match |
| Temp entries / `mts_run_*` | 12703 / 24 | Independent `os.listdir(TEMP)` counts: 12703 / 24 | Match |
| Stray-process kill candidates | 0 | Independent `c_drive_guard.procs_summary()`: 0 KILL candidates | Match |
| Worktrees / unshipped work | 38 / 18 | `git worktree list`: 38; report says 18 but was stamped 2026-10-28 21:34Z, nearly 23h before the board read | Count matches; unshipped count is stale, not current evidence |
| VM bundle | NOT_IN_DATA | Expected `vm_bundles` path absent | Correctly unavailable |
| Sessions running/idle/archived | NOT_IN_DATA | Coordinator-only data absent | Correctly unavailable |
| Compaction count | NOT_IN_DATA | Session transcript not available to this script | Correctly unavailable |
| Sonnet vs Opus value | NOT_IN_DATA | No per-model close attribution | Correctly unavailable |
| Board build duration | 6 s | First run completed in 5.93 s | Match |

**Mismatch count: 9 printed values**: 2 today/yesterday commit cells, 6 daily commit cells, and 1 cleanup count. The first two duplicate the 2026-10-29 and 2026-10-28 daily entries. The date labels are the problem: `git_days()` at lines 261-263 uses `--date=format-local` and a host-local `--since=8.days`; `sec_budget()` and `sec_speed()` label those results with `utc_day()` (lines 270-273 and 130-136). `sec_value()` uses local-midnight `--since=midnight` for a UTC-day label (lines 300-307). On this host, local offsets move commits across the day boundary.

## Section fallbacks

| Section | Failure behavior in source | Audit |
|---|---|---|
| Resources | `build()` catches exceptions per section and emits `NOT_IN_DATA` (`353-360`); no-budget input gets `NOT_IN_DATA` (`62-73`) | Clear for section exceptions and absent budget; git command errors can return empty output without raising (see finding below) |
| Speed and health | CI fetch errors are swallowed in `sec_speed()` (`240-244`); formatter emits `NOT_IN_DATA` when no rows (`130-140`); gate data absence emits `NOT_IN_DATA` (`119`) | CI table fallback is explicit, but top banner has a false-green path below |
| Value added | Section-level catch from `build()` | A failure replaces the section with `NOT_IN_DATA` |
| GPT and Gemini | Missing GPT sources raise into section catch; missing Gemini is explicitly `NOT_IN_DATA` (`168-190`) | Explicit |
| Still missing | Missing `parked=` becomes `NOT_IN_DATA`; section-level catch covers failures (`310-314`) | Explicit for missing regex; task JSON parse errors are silently skipped |
| Hygiene | Disk errors become unavailable; missing/unparsed worktree report states unavailable (`315-343`) | Stale but parseable report is accepted as current |
| Sessions and measurement | Every item states `NOT_IN_DATA` (`217-220`) | Explicit |

## Findings

| Severity | File:line | Evidence | Proposed fix |
|---|---|---|---|
| HIGH | `scripts/dev/status_board.py:261-273, 300-307` | Host-local git dates are labeled UTC. Six daily cells and the duplicated today/yesterday values disagree with parsed `%cI` UTC dates; cleanup misses a UTC-day commit | Query explicit UTC ISO timestamps and filter against UTC midnight boundaries, or label output as host-local |
| MED | `scripts/dev/status_board.py:300-307` | `--since=midnight` is host-local but cleanup line says today; `7fa356aff104` belongs to the UTC day and is omitted | Use the same explicit UTC bounds as the commit table |
| MED | `scripts/dev/status_board.py:333-338` | Parsed unshipped count has no age check; report was dated 2026-10-28 21:34Z while board ran 2026-10-29 20:38Z | Regenerate a same-run report or display it as stale/NOT_IN_DATA after a short age threshold |
| MED | `scripts/dev/status_board.py:39-40, 246-252, 261-263, 223-228, 366-370` | `run()` ignores return code; malformed/unreadable task cards are silently skipped. `main()` converts any CI fetch exception to `red=0`, then `result_line()` prints “CI green” even if speed section reports unavailable | Check return codes; report parse failures; keep CI state unknown on fetch error rather than treating it as green |

The false-green CI path is specifically the outer `main()` catch of `ci_runs()` and `result_line()` using zero to mean green. The `fmt_speed()` section does correctly print `NOT_IN_DATA` for unavailable runs. The report does not claim a false-green occurred in the captured run; it identifies a code path.

## Follow-up

Created follow-up card use-utc-day-boundaries-in-status-board-c in lane SONNET, size S, IMPORTANT, with focused UTC-midnight regression-test steps and the audit report as a source. It remains RAW because the task workflow requires a Lab_Guy review stamp before it can become READY; I did not supply that reviewer stamp. No tests or code fixes were run in this audit.

## Captured board output

```text
**Status: week budget up to 84%; CI red 10 min; 48 CRITICAL/CRUCIAL cards open**
**Resources: budget and what it bought**
| Login | 5h used | Week used | Seen (UTC) | Week resets |
|---|---|---|---|---|
| A | 41% | 84% | 18:19 | 2026-10-30T09:00Z |
| B | 18% | 51% | 17:57 | 2026-11-01T17:00Z |
| C | 6% | 22% | 17:16 | 2026-11-03T20:00Z |
| What it bought | Today | Yesterday |
|---|---|---|
| Cards closed | 8 | 88 |
| Commits on trunk | 81 | 672 |
Spend vs output per login: NOT_IN_DATA (cards carry no login; a `closed_by_login` field would measure it).
**Speed and health**
Trunk commits per UTC day: 10-29 81, 10-28 672, 10-27 228, 10-26 265, 10-25 273, 10-24 119
CI last 6 (newest first): 94c57a6 running, 9a19241 failure, 7877fdc failure, f75e053 failure, 46ae9a7 success, 40f9181 success; red now 10 min
Gate wall time, median of last 5 ships: 6 s [1, 1, 1083, 6, 10]
Ships running now: 0; stalled over 30 min: 0
**Value added**
| Solved today (top 3) |
|---|
| GPT recomputes the WaveTrend atlas z-scores and Holm over 9 cells |
| [GEMINI] Krown 4 yt-burn rule extracts (UHY740h3e-Y SOaAP9vBgM4 -9rAJNUpMsk EQy4HouRMMk):  |
| Cloud ship: unshallow the clone once before extra tests (test_lab_query needs history) |
Dedupe/cleanup commits today: 0
Stuck: 1 active card(s) older than 24 h  bug-burn-cap-stops-all-work
Stale claims (over 24 h): 29  JIS-NB: b197-proposal-b-rename-apparatus-fixes-m (28h); JIS-NB: bug-conflict-2e7c5191bb (28h); JIS-NB: c-drive-guard-frees-only-0-66-gb-c-stays (28h)
**GPT and Gemini**
| Provider | Account/plan | 5h used | Week used | Reading (UTC), age | Source |
|---|---|---|---|---|---|
| GPT (Codex) | NOT_IN_DATA | 0% | 0% | 2026-10-29T20:18Z, 0.3 h old | MyTradingSys/system/codex_usage.json (tree) |
| Gemini (Antigravity) | Google AI Pro | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | GEMINI_START.md:1 |
Gemini usage: NOT_IN_DATA (no Gemini usage file; would measure: gemini_queue run counts per day from its done log)
Gemini facts on trunk: plan Google AI Pro (MyTradingSys/system/GEMINI_START.md:1); lane CODEX cards only (GEMINI_START.md:5); Flash models via agy queue (scripts/dev/gemini_queue.py:10); queue logs F:/MTS/gq/*.log live on the NUC, not on trunk (gemini_queue.py:20).
**Still missing**
Open CRITICAL 15, open CRUCIAL 33, parked (need review / no tries left) 0, raw 25, blocked 32
**Hygiene**
C: free 78.4 GB, D: free NOT_IN_DATA, F: free 214.6 GB; Temp entries 12703; mts_run_* leftovers 24; stray processes 0 kill candidate(s)
Worktrees: 38 (18 with unshipped work, report 2026-10-28 21:34Z)
VM bundle: NOT_IN_DATA: vm_bundles path not present
**Sessions and measurement**
Sessions running/idle/archived: NOT_IN_DATA (coordinator adds)
Compaction count: NOT_IN_DATA (would measure: count compaction events in the session transcript .jsonl)
Sonnet vs Opus value: NOT_IN_DATA (would measure: cards closed per login 5h-% by model)
(board built in 6 s)
```

