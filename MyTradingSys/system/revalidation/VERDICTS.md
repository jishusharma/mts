# Revalidation verdicts (second eyes), 2026-10-12, JIS-NUC

Prompts: `RV01..RV08_*.md` here, rules `_COMMON.md`. Cards: `python scripts/dev/tasks.py next --lane CODEX` (GPT lab, `MTS-CodexLab` tick
on JIS-NUC picks them up, gpt-6-astra for audits, gpt-6-luna for bulk/run) and `--lane SONNET` for the tooling items (the lab scope
excludes the relay and dev tooling, LAYER_LAB.md "Scope"). DSA bridge = `desk.py post ... --target DSA-NUC` (DSA_DELEGATION.md); nothing
here needs judgment-free run-and-report except the RV04 klines fetch, which sits inside its Codex run card.

## Ranking (risk = how much a hidden defect costs x how little independent checking it had)
| # | item | why | host= | runner | status 2026-10-12 |
|---|---|---|---|---|---|
| RV03 | sync.py tidy (+claim, hot-file resolve) | deletes directories; tests encode the hazard | any | card rv03-tidy-safety-revalidate-and-fix-sync, owned by thread "Fix tidy and recover lost data" | RAN (mine): 2 defects CONFIRMED, fix in that thread |
| RV01 | Tom ledger repairs | sole evidence base for Tom v2; 76 rows rewritten by the author | JIS-NUC | Codex audit rv01-tom-ledger-repairs | RAN mechanical (mine): 3 defects; frame pass QUEUED |
| RV02 | DAX harness fixes H1-H8 + holdout isolation | burning the holdout is irreversible; fixes self-verified | JIS-NUC | Codex audit rv02-dax-harness-fixes | tests re-run 62 green; deep audit QUEUED |
| RV04 | Q33 matrix | negative verdict closed Q34 | JIS-NUC | rv-dsa-q33-rerun (DSA-NUC, BLOCKED on klines re-fetch; rv04 closed as duplicate) | numbers cross-checked (mine): MATCH; independent re-run waits for the klines |
| RV05 | Fabio ledger frames | first audit read 4 sheets of 62 images | JIS-NUC | Codex audit rv05-fabio-ledger-frame-pass | QUEUED |
| RV06 | live-read claims | MISMATCH lines become engine cards | JIS-NUC | Codex audit rv06-live-read-claims (luna) | QUEUED |
| RV07 | layer tooling + shot.py guards | navigation layer; 2 guard gaps found | any | Sonnet card rv07-layer-tooling-revalidate | RAN partly (mine): 2 defects, paths clean; rest QUEUED |
| RV08 | relay host= tag | wrong IDLE/KICK costs a session | any | Sonnet card rv08-relay-host-tag-edge-cases | 30 tests green; edge cases QUEUED |
Fix card from RV01: rv-fix-tom-ledger-date-column (Sonnet, p2).

## Defects found this session (each re-checked a second way before listing)
| ID | Sev | Where | What | Evidence |
|---|---|---|---|---|
| D1 | HIGH | scripts/dev/sync.py:325-366 `tidy` | A worktree that has no commit of its own (just started, or holding only its claim) is clean and its branch is an ancestor of origin/fast-track, so `tidy --apply` removes it. test_sync.py:162-176 asserts exactly this removal for "done". A session that has not committed yet is indistinguishable from a finished one. | `sync.py tidy --all` dry run from mts-reval listed 5 worktrees "would remove", incl. mts-jis-nuc-s1012-164721 (last commit 22:23 +0530, hours old) and mts-live-8h |
| D2 | HIGH | same | the porcelain status listing omits ignored files and `git worktree remove` deletes them without complaint (reproduced in a scratch repo: Dumps/klines.csv gone, status 0 lines). Dumps/, runtime_data/ are ignored (.gitignore:19). | scratch repro 2026-10-12 |
| D3 | MED | MyTradingSys/system/DEVICES.md (72c2090) | Says the 2.5M-bar 1m klines are on JIS-NUC, in a gitignored Dumps/ of the fetching worktree. `find` over IdeaProjects (14 worktrees) and F:/MTS found no raw_1m_2022; F:/MTS/data/bigtrade/spot_raw holds spot 1m only. Q33 cannot be reproduced here without a re-fetch. Probable cause D2 (not proved). | find output; DEVICES.md |
| D4 | MED | TOM_TRADE_LEDGER.csv `date` | T5 (2026-05-19), T6 (2026-06-02), T7 (2026-03-19) keep an ISO date while trade_date_status = NOT_IN_DATA; T9, T10, T11 hold prose in the date cell; T6 and T10 (one canonical group) disagree (06-02 vs 06-08); T11 UNRESOLVED vs T11-x 2026-09-01. Any consumer that splits or sorts by `date` treats assumed/unknown values as facts. | python read of the CSV, 37 rows |
| D5 | MED | scripts/dev/shot.py:527 | The 20-char MISMATCH guard is `kind == "noaction"` only; `note:<8+ chars>` closes a shot that has MISMATCH claims. | code reading |
| D6 | LOW | shot.py:503 | `outcome_exists` for F-BT-/FEAT- ids is `git grep -F` substring: `FEAT-1` matches `FEAT-11`. | code reading (regex FEAT-\d+ accepts FEAT-1) |
| D7 | LOW | PRE_REG_Q33.md item 11 vs matrix_q33.py `half = N // 2` | "First half 2022-2024 / second half 2025-2026" is really split at bar N/2 = about 2024-05-22. Does not change the verdict (0 survivors either way). | arithmetic 167,520 bars x 15 min |
| D8 | LOW | TOM_TRADE_LEDGER.csv `side` | Management rows carry action words (`stop_tighten`, `partial_exit`, `short(add)`) in a column consumers read as long/short. | CSV |

| D9 | MED | scripts/sched/handoff_lint.py | Nothing guarded duplicate `Qn` ids; threads reused Q43-Q47 on 2026-10-12 (layer index, tidy, audit handoff). Fixed here: lint now errors on an id used twice in the block (test_duplicate_task_id_is_a_lint_error, red first, 31 relay tests green). Not caught: a number reused over time with different text across handoffs (needs the previous handoff); the block was unique after origin's renumbering, Q47 mine became Q48. | lint code + new test |

## Checked and clean (so nobody repeats it)
- Q33: every number in MATRIX_REPORT.md matches MATRIX_CELLS.csv (336 cells = 186 + 89 + 61; 0 positive net means at 60 min; 3 positive at 240 min,
  best +0.039 %, q 0.62; event counts per trigger; per-trigger all-filter means). BH step-up and placebo code read: no look-ahead found
  in F1, F3, RV median (prior days only), FVG first/second test (decided at close of the test bar).
- layer_index.json: all referenced paths exist; layer_map.json: 32 backtests, 1 non-path `n` ("see TRIAL_REGISTRY.csv").
- Tests re-run on JIS-NUC: test_sync 19, test_make_layer_map 2, test_make_layers_md 4, test_shot 26, test_tasks 29, test_relay 30,
  test_tom_dax_bt 62 (+122 subtests): all green. Green tests did not catch D1/D5: they assert the behaviour.
- Tom ledger structure: 37 unique ids, 12 canonical groups, every row in exactly one group, n_rows matches, canonical_id consistent, short/long geometry of ENTRY rows consistent.

## Not done (limits of this session)
- No frame was opened by me (no cv2/PIL on JIS-NUC python): frame-level claims in RV01/RV05 wait for the GPT lab.
- RV02 holdout-isolation trace, RV06 recomputation, RV08 edge cases: prompts ready, not run.
