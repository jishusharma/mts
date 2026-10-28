# Lab_Guy flow table, NUC tandem block 2026-10-18

Facts only. Every row cites a commit or file; anything not found in the repo, the findings files or `F:/codex_home/lab_runs/runs.jsonl` is marked UNVERIFIED.
Read at origin/fast-track b7073e8c (2026-10-18 04:18 +0530). Plan: `MyTradingSys/research/lab_guy/TANDEM_PLAN_2026-10-18.md`. Hand-over: `MyTradingSys/system/NEXT_SESSION.md` (NUC-TANDEM-1018).

File name note: `FLOW_2026-10-18.md` already holds the findings ledger of session lab-guy-1018 (ae143428), so this table is a separate file and overwrites nothing.

Key. Producer for every GPT card below = `gpt-6-luna` / medium via `codex_run.py` (runs.jsonl `model`, `effort`). Free machine checks = the offline gate `sync.py ship` runs (`--quick`), the card's own tests, and `tasks.py check`. Cross-vendor owed = a Gemini/Argon high-effort review (NEXT_SESSION item 3).

| card | class / weight | producer | checks run | defects found, by whom | final state | commit |
|---|---|---|---|---|---|---|
| lab-data-pin-hash | not recorded in the files read (UNVERIFIED) | luna / medium, run 2026-10-17T20:17Z, DONE, 79 s | own tests 22 passed (report `2026-10-17_lab-data-pin-hash.md`); Haiku check PASS per NEXT_SESSION (no Haiku report file found: UNVERIFIED beyond that line); cross-vendor: none recorded | none recorded | done | 26a97049 |
| lab-machine-checks-extra | not recorded (UNVERIFIED) | luna / medium, 20:19Z, DONE, 205 s | own tests 73 passed + 307 subtests (report `2026-10-17_lab-machine-checks-extra.md`); Haiku check PASS per NEXT_SESSION (UNVERIFIED beyond that line); cross-vendor: none recorded | none recorded | done | 9208815d |
| lab-crossvendor-stage | not recorded (UNVERIFIED) | luna / medium, 20:26Z, DONE, 192 s | own tests 24 passed (report `2026-10-17_lab-crossvendor-stage.md`); independent check FAIL per NEXT_SESSION | same-vendor hole: the gate compares model id, not vendor (NEXT_SESSION; no findings file, UNVERIFIED beyond that line). Found by the NUC coordinator's check; the producer's report says "24 passed" and "Follow-up cards created: none" | done, hole carried to lab-crossvendor-same-vendor-gate | 0c068635 |
| lab-weight-enforce | C2 (stamp commit says "C2 cross-vendor review still owed", 4300f939) | luna / medium; run 1 20:25Z INCOMPLETE, card rewritten to v3.1 vocabulary, run 2 20:30Z DONE | own tests (commit Result says 47 OK; report says 57 OK after the 34ecf46a fix); Sonnet reviewer ACCEPT stamp 4300f939; cross-vendor OWED, not done | (a) tests were defined after `unittest.main()` and never ran, CLI test helper did not capture refusal text: fixed in 34ecf46a (Claude). (b) later independent review of the gate found 3 HIGH + 2 MEDIUM + LOW/INFO, see "What the flow caught" | done, hardening card open | 324cc560 (code), 4300f939 (stamp), 34ecf46a (test fix) |
| lab-holdout-access-control | C2, CRUCIAL (report: "CRUCIAL/C2 card") | luna / medium; run 1 20:33Z BLOCKED, run 2 20:37Z BLOCKED (no reviewer stamp), 86 s / 92 s | own tests 27 passed (report `2026-10-17_lab-holdout-access-control.md`); independent Claude review; cross-vendor OWED | two defects found by independent Claude review (NEXT_SESSION; reopen note in runs.jsonl; commit 67244dbf): unsupported extension not fail-closed, seconds-epoch timestamps not normalised. Fixed in run 2 (`lab_flow.py:36-93`, tests `test_lab_flow.py:250-279`) | done, REVIEWED stamp | fe7ef08e (code), 67244dbf (reopen), 60634304 (close) |
| lab-formula-spec-text | C2, IMPORTANT (card note) | luna / medium; runs: 20:41Z BLOCKED, 20:48Z BLOCKED, 21:53Z SHIP_FAILED, then BLOCKED (3c4addfa) | run 1 coverage check was grep-only; run 3 `test_formula_spec.py`; independent Claude review; Haiku re-derive and Argon high owed per card note; cross-vendor OWED | run 1 spec REJECTED by independent Claude review: worked examples off the DEV tape, wrong arithmetic F01 57.8313, F11.4/F11.5 62751.9875, F11.6 -0.399847, grep-only coverage (runs.jsonl REOPENED note; commit 507fcf1b). Run 3 test had an `else: got=val` echo fallback so F11/F18-F21 sub-ids passed without a recount (`test_formula_spec.py:11`, report `2026-10-17_lab-formula-spec-text.md`); the producer itself flagged this, so it is a producer-reported gap | NOT done: card `ready`, partial; follow-up card below | 3c4addfa (BLOCKED), 1e2d6189 (follow-up card) |
| lab-formula-spec-recount | C2, IMPORTANT (card note) | luna / medium, 22:33Z, SHIP_FAILED then BLOCKED | offline gate failed at "Step 3xt: Extra tests" (runs.jsonl); expectedFailure decorator keeps trunk green (b4d4dd54); no review yet | none yet; remaining gap = sub-ids F11, F18-F21 still echo expected values (card note) | NOT done: card `ready` | bc1dbe2b (BLOCKED), b4d4dd54 |
| lab-crossvendor-same-vendor-gate | C1, IMPORTANT, reviewer slot Gemini Flash high (card note); ledger scan in `FLOW_2026-10-18.md` argues C2 | luna / medium, 22:37Z, SHIP_FAILED then committed DONE | own tests 28 passed (Result line); no independent Claude review and no REVIEWED stamp found (UNVERIFIED that none exists elsewhere); cross-vendor owed if reclassified C2 | none recorded | done (card state), unreviewed | 3bc336e6 |
| lab-review-gate-harden | weight blank on the card | not built; card written by Claude Sonnet 5.5 as output of the 34ecf46a review | none (card only); claimed by JIS-NUC at 04:18 | n/a | ready, claimed | 9eb507e3 (card), b7073e8c (claim) |
| review of 34ecf46a (`tasks.py` review_gate) | Rule-11 review of a C2 gate | reviewer: Claude Sonnet 5.5, blind first, read-only, mutations in a scratch copy | blind expectation vs code; 9 mutations on ReviewGateTest (2 survive) | 3 HIGH, 2 MEDIUM, 1 LOW sub-item, 2 LOW, 1 INFO (below) | findings filed, fixes not yet made | 9eb507e3 (`findings/2026-10-18_review_34ecf46a.md`) |

Also shipped by the same lane, not in the requested list: `codex_run.py ask --mutation-check` flag (7b5ef86c, 63 tests OK, 3 new tests failed first; Claude) and the DEV-only rescope of gap-g2-dax-ask-candles (e7aeed1c, per NEXT_SESSION).

## What the flow caught

Defects the producer's own check passed and independent Claude review found. File:line from `findings/2026-10-18_review_34ecf46a.md` unless stated. The producer of the gate (lab-weight-enforce) reported its own tests green.

- Stamp forgeable (HIGH): `tasks.py:552` (REVIEWED_RE), `:572`. Any token, any position in the note, invalid date `2026-13-45` and placeholder `<reviewer>` all pass; a producer can write it via `apply-op --note` (`tasks.py:645`).
- Planner stamp format refused (HIGH): `tasks.py:555-566`; `REVIEWED:2026-10-18 ACCEPT` refused at 34ecf46a (the findings say 35c10e93 fixes it; verify the tip).
- `live_path: true` not treated as C3 (HIGH): `tasks.py:568-570` (added later in 35c10e93 per the findings).
- Class field downgrades the note (MEDIUM): `tasks.py:557-563`; `class = C2` and `class=C10` silently ignored (fail-open).
- Ungated close paths (MEDIUM): `tasks.py:604-607` (flow branch), `lab_flow.py:283`, `lane_health.py:317`, `tasks.py:661` (sweep). Also `done` accepts any card state (LOW, `tasks.py:604-611`).
- Two surviving mutations: whitespace-only receipt and lowercase-weight bypass are killed by no test (findings "Test vacuity" table).
- Same-vendor hole in lab-crossvendor-stage (0c068635): found by the Claude check, closed by card lab-crossvendor-same-vendor-gate (3bc336e6). Source NEXT_SESSION; no findings file.
- Holdout gaps and formula-spec errors (off-tape prices, F01/F11.4-F11.6 arithmetic): found by independent review, evidence in runs.jsonl REOPENED notes (no separate findings files, so no file:line beyond the lines cited in the table).
- Tally: NEXT_SESSION states the Claude spot-check caught real defects 3 of 5 times (same-vendor gate, holdout gaps, formula spec) that the lab's own self-check passed; the 34ecf46a review is a fourth case.

## Still owed

- Cross-vendor (Gemini / Argon, high effort) reviews on every C2 card closed or touched today: lab-holdout-access-control, lab-weight-enforce, lab-formula-spec-text (and lab-formula-spec-recount when it lands). All carry Claude-only stamps (NEXT_SESSION item 3); none recorded as done in the files read.
- lab-formula-spec-text / lab-formula-spec-recount: not done. Needs independent Haiku re-derivation (at least 12 ids), stamp, `tasks.py done`; then release lab-planted-error-trial.
- lab-crossvendor-same-vendor-gate: no independent review or stamp found; class arguably C2.
- lab-review-gate-harden: unbuilt; re-run the review against tip 35c10e93 or later (findings, candidate card 4).
- Haiku checks for lab-data-pin-hash and lab-machine-checks-extra are cited only from NEXT_SESSION: UNVERIFIED.
