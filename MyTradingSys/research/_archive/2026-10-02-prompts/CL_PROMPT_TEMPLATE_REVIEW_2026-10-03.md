# CL PROMPT TEMPLATE REVIEW 2026-10-03

Session: MTS-2026-10-03-1620Z-CLI-BLD-tf5-tom-exec (Task C, read-only). Written 2026-10-03.
No edit to CLAUDE.md, STATUS.md, DSA_SESSION_PROMPT.md or scripts/sched/pick_task.py in this row.
Inputs read: CLAUDE.md (43 lines; rule at :8-12), scripts/sched/pick_task.py:184-228 (compose(), the generator
of every runtime/queue/next_task_*.txt), all 9 queue samples of 2026-10-03, the TF5 operator paste of this session,
SURFACE_POLICY.md (112 lines), DSA_SESSION_PROMPT.md sections 5, 6, 9 (:93-166, :206-246), STATUS.md (65 lines).

Token method: no tokenizer is installed (tiktoken missing), so tokens are estimated as ceil(chars / 4). Characters
and lines are measured [run: python over the files]; the token figures are estimates, the ratios between them hold.

## 1. Current shape

compose() (pick_task.py:193-228) emits 7 blocks. Sample: next_task_20261003T144409Z.txt (TF4).

| block | lines | chars | est. tokens | changes per task? |
|---|---|---|---|---|
| 1 header: session id, surface (2 lines), repo + branch | 1-4 | 351 | 88 | session id only |
| 2 operator signature + directive (3 quotes) | 6-10 | 307 | 77 | no |
| 3 TASK + Blocker/Next (pipeline row) | 12-13 | 474 | 119 | yes |
| 4 READ FIRST (fixed 3 files + row files) | 15-18 | 215 | 54 | row files only |
| 5 T0-T5 contract | 20-28 | 754 | 189 | commit prefix only |
| 6 MARKERS, SPAWNING, DO NOT STOP, STAGE DISCIPLINE | 30-35 | 480 | 120 | no |
| 7 format line (LF, no BOM, UTC, reply 25 lines) | 38 | 90 | 23 | no |
| total (incl. blank lines) | 38 | 2725 | 682 | |

All 9 samples: 37-40 lines, 2305-2725 chars, est. 577-682 tokens. Every sample is over the CLAUDE.md:9 cap of 30
lines. The cap is not enforced: compose() has no length check and scripts/dev/prompt_check.ps1 checks citations and
tokens, not length. The TF5 paste (hand-composed by DSA) is 25 lines, 3125 chars, est. 782 tokens: inside the line
cap only because its lines are long (up to ~330 chars).

## 2. Redundancy

| block | already on disk at | verdict |
|---|---|---|
| 1 surface lines | SURFACE_POLICY.md section 1b ("App first. CLI is fallback") | redundant |
| 1 repo + branch | CLAUDE.md hard rules ("Branch `fast-track`"); the session runs in the repo | redundant |
| 2 signature + directive | standing operator words, identical in every sample (pick_task.py:48-51 constants) | standing: belongs in CLAUDE.md once |
| 4 "CLAUDE.md, STATUS.md, LESSONS_LEARNED.md" | CLAUDE.md:3-4 ("Read first") | redundant; keep the row files |
| 5 T1 ".new ... .pre_<tag>" | CLAUDE.md hard rules ("Staged work is `<file>.new`") | restated hard rule |
| 5 T2 "fail on the pre-change code" | CLAUDE.md gates ("New tests must fail on the pre-change code") | restated |
| 5 T3 run_all_tests --quick | CLAUDE.md gates ("All offline: ...") | restated |
| 5 T0, T4, T5 | DSA_SESSION_PROMPT.md 5b (TASK/DONE/VERIFIED/MISSED); BUILD_PIPELINE "HOW AN ITEM RUNS" | standing contract |
| 6 DO NOT STOP OR KILL | CLAUDE.md hard rules ("builders never stop/restart them") | restated |
| 6 MARKERS, SPAWNING, STAGE DISCIPLINE | nowhere else | standing: move to CLAUDE.md once |
| 7 LF / UTC | CLAUDE.md ("newline='\n'"); DSA_SESSION_PROMPT.md:220 (UTC, LF) | restated |

CLAUDE.md:10-11 says a CL prompt carries no restated hard rules and no restated state. Blocks 1, 2, 4 (fixed part),
5, 6 and 7 break that rule. Only block 3, the row files of block 4, the session id and the commit prefix are task data.
STATUS.md content is not restated by the composer (no queue or git state in the prompt): no redundancy there.

## 3. What the redundancy costs

Per prompt, standing text = everything except the session id, TASK, Blocker/Next and row READ lines: 2044-2051 chars
in all 9 samples [run], est. ~511 of 682 tokens (75 %) in the TF4 sample.
A CL session reads CLAUDE.md anyway (it is loaded by the harness), so each standing line is paid twice per session,
and the copies can drift: the TF5 paste already words the surface line differently from compose() and drops
SPAWNING, DO NOT STOP and STAGE DISCIPLINE, so two live versions of the contract exist today.

## 4. Proposed template

Five lines. Standing text moves once into a CLAUDE.md section named "CL contract" (T0-T5 wording of
pick_task.py:209-217, MARKERS, SPAWNING, STAGE DISCIPLINE, operator signature and directive); hard rules already in
CLAUDE.md are not copied there.

```
Session ID: <id>
TASK: <id> (wave <w>, row <n>) - <slug>
Blocker: <blocker> | Next: <Next cell>
READ: <item doc>, <row files>, BUILD_PIPELINE.md row <n>
CONTRACT: CLAUDE.md "CL contract" (T0-T5, markers, spawning, stage discipline). Commit prefix "<id>: ".
```

A multi-task prompt (like TF5: Tasks A-C) adds one TASK line and one READ line per task; the CONTRACT line is shared.
Row-specific deviations from the contract (for example "no promote", "Build-Check also") go on the CONTRACT line.

## 5. Measured savings

Rendered by script from each queue sample's own id, TASK, Blocker/Next and READ lines [run]:

| sample | now chars / est. tokens | proposed chars / est. tokens |
|---|---|---|
| next_task_20261003T144409Z (TF4) | 2725 / 682 | 797 / 200 |
| next_task_20261003T100921Z (R4-T2) | 2387 / 597 | 458 / 115 |
| 4 samples 101221Z-104409Z | 2305 / 577 each | 377 / 95 each |
| all 9 | 22 093 / 5 524 | 4 738 / 1 185 |

Saving: TF4 -482 est. tokens (-71 %), 38 -> 5 lines; all 9 prompts -4 339 est. tokens (-79 %).
Cost moved, not removed: the CLAUDE.md "CL contract" section (block 2, T0-T5, MARKERS, SPAWNING, STAGE DISCIPLINE,
without the hard rules CLAUDE.md already has) is about 1 400 chars, est. ~350 tokens, loaded once in every code
session, including sessions that never get a CL prompt. Net per session with one CL prompt: about -130 est. tokens;
with n prompts in one session: about -480 n + 350.

## 6. The 30-line cap

Keep it. The rule is CLAUDE.md:9; no operator ruling or measurement on disk supports a different number, so no
sourced change is proposed. The proposed template fits in 5 lines. Two gaps make the cap weak today and are queued
as CC_TASK_LIST_2026-10-03.md row 6.1: (1) compose() is not checked against it and every sample breaks it; (2) the
cap counts lines, so a hand prompt can stay under it with 300-char lines. If a second limit is wanted, a character
budget sourced from a measurement would close (2); none is proposed here.

## 7. Not done

- No tokenizer run: figures are chars / 4 estimates (method note in the header).
- system/sessions/*.md records were listed, not measured: they are outputs of a session, not prompt templates.
- DSA_SESSION_PROMPT.md was read for sections 5, 6 and 9 only.

# END
