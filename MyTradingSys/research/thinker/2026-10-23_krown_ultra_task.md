# Krown ultra task: confluence S2-S6 as one Sonnet Workflow (pilot 2 of 2, after CBP)

Operator ask (2026-10-23): "prepare a pilot run on Krown-related workflow and layers" as a Sonnet ultra (multi-agent Workflow) run.
Written by Supervisor C. Plan source: `research/krown_audit_2026-10-22/FABLE_CARD_CONFLUENCE.md` s4 (step table), s5 (design prompt),
s6 (success test), and `LAYER_CONFLUENCE_DESIGN.md` s9 (v2, supersedes s0.3c/0.6/3-7). This file only says how one Workflow runs it.

## Facts checked (origin/fast-track @ 80c9df1a7, 2026-10-23 12:45Z)
- S0 registry: shipped in 5025e79ba (krown G1->G2, STATE.md, F1/F2); card `confluence-s0-registry` still reads ready: P0 closes it.
- S1 context table + counts: worker running on JIS-NB (branch JIS-NB/confluence-s1, krown_context.py + COUNTS.md staged, not shipped).
  **The run starts only after S1 is on trunk** (`run/COUNTS.md` and frozen `run/bands.json` on origin/fast-track).
- S2-S6: card `confluence-s2-s6-chain` (raw). The card names Fable 5.1 for S2/S5; this pilot is Sonnet-only (operator: "sonnet ultra"),
  so S2/S5 run on Sonnet and get an Opus diff-only review (SUPER_SESSION rule 11). DECISION (OURS).
- Related, NOT in this run: `krown-dev-event-study` (H-V1..H-T1, own pre-reg), `krown-data-cme-btc-volume`, `lc-validation`.
  One run = one Holm family; mixing in the event study would change the family after the fact.

## (a) Phase plan (pipeline; no two writers on one file)
| phase | agent | model | writes | done_when |
|---|---|---|---|---|
| P0 preflight | Pre | haiku | nothing (reads) | S1 files on trunk; CI line green or claimed; no STOP/HOLD; `sync.py claim confluence-s2-s6-chain` held; closes S0 card |
| P1 design (S2) | D | sonnet | `FABLE_DESIGN.md`, `PRE_REG_CONFLUENCE.md` | FABLE_CARD s5 items 1-6 answered from COUNTS.md only; no outcome column read |
| P1r review | R | opus | `run/REVIEW_PREREG.md` | diff-only review: SOUND / SOUND WITH FIXES / UNSOUND; D applies fixes once |
| P1c commit | D | sonnet | git | PRE_REG commit lands on trunk BEFORE any P2 agent opens `run/sealed/` (git order is the proof) |
| P2 context read (S3) | C | sonnet | `run/CONTEXT_READ.md` | (a) D1 vs naive baseline, (b) BBWP -> next-24 h vol; DEV + DEV_EXT; week-clustered; verdict per PRE_REG |
| P3 trials (S4) | T | sonnet | `run/DEV_RESULTS.md`, `research/layer_lab/TRIALS.md` rows | every PRE_REG test reported incl. failures; branches gated on (a) exactly as PRE_REG says |
| P3x re-derive | X | haiku | `run/REDERIVE.md` | 3 numbers from DEV_RESULTS recomputed from FORMULAS.md by hand script; match within 1e-6 or flagged |
| P4 verdict (S5) | V | sonnet (fresh, read-only on code) | `FABLE_VERDICT.md` | what goes to the ONE VALIDATION read (pooled trial), what dies, alert-only tags; no VALIDATION bar opened |
| P5 ship (S6) | S | haiku | git | `sync.py ship --release confluence-s2-s6-chain`; commit body `Result:`; `git cherry origin/fast-track` empty |
All files under `research/krown_audit_2026-10-22/` unless named. P2 and P3 are sequential (P3's branches depend on P2 (a)).

## (b) Agent prompt skeleton
Each starts: "You are <agent> of the Krown ultra run (research/thinker/2026-10-23_krown_ultra_task.md). Do exactly your phase row.
Read FABLE_CARD_CONFLUENCE.md s<n> and LAYER_CONFLUENCE_DESIGN.md s9 first. DEV and DEV_EXT only: never open VALIDATION or HOLDOUT bars.
Label every number SOURCED (quote + file:line) or OURS. Never read .secrets/.env. Testnet only. No scheduler. git -C, never chained cd.
Repo is public: no transcripts, no runtime data. Report: files written, the numbers, sha if you committed."
D gets the FABLE_CARD s5 prompt verbatim (its "Fable" wording stands; it runs on Sonnet).

## (c) Fail-first tests
- `test_krown_context.py` (S1) stays green; T adds `test_confluence_trials.py` for any new scorer: hand numbers from FORMULAS.md,
  one test that fails on a 1-bar look-ahead join, one that fails if a sealed outcome column is read before the PRE_REG commit time.
- `python scripts/dev/run_all_tests.py --quick` green before P5.

## (d) Verify (inside P4 V and P5 S)
V gets only trunk files, not the builders' reports. Must paste: `git log --format=%h\ %ci` proving PRE_REG precedes CONTEXT_READ and
DEV_RESULTS; the quick test tail; grep that no VALIDATION/HOLDOUT date range appears in any loader call; TRIALS.md row count vs PRE_REG
test count (equal, or the gap named). A claim without command output = NOT MET.

## (e) Cost (OURS, agent-turns)
P0 3, D 25 (cap 30), R 8, C 15, T 25, X 5, V 10, S 3 = ~94 expected, 110 ceiling; ~3-4 h wall. Weekly-cap stop: FABLE_CARD s8
(ship what exists if the all-models weekly reading rises 6 points during the run).

## (f) Kill criteria (OURS numbers; adopted by pasting the launch line)
- COUNTS.md shows fewer than 2 trigger layers TESTABLE (week-clustered MDE <= 0.10 R): stop after P1, ship the design as DESCRIPTIVE only.
- R scores UNSOUND twice: stop, ship the review, no trials.
- Context read (a) fails: run only the PRE_REG "if (a) fails" branch (no sizing arm, no pooled D3 read); this is a result, not a kill.
- 110 agent-turns reached: ship what exists, verdict says PARTIAL.

## (g) Launch line (paste into a NEW Sonnet session in the Code tab, after the CBP run ends and S1 is on trunk)
```
You are the Krown Orchestrator. Use a workflow: run MyTradingSys/research/thinker/2026-10-23_krown_ultra_task.md phases P0-P5 exactly, with the section (f) kill numbers adopted as written; never ask, take the file's defaults.
```

## (h) Pre-run checklist (the Orchestrator's P0 does these; listed so a human can check)
1. `git ls-tree origin/fast-track MyTradingSys/research/krown_audit_2026-10-22/run/COUNTS.md` prints a line (S1 shipped).
2. CBP ultra run finished (one ultra run per login at a time: two Workflows on one machine compete for the 2 gate slots).
3. No live claim on `confluence-s2-s6-chain` (`sync.py claims`).
