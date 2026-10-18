# ARCHITECTURE - how the MTS dev system fits together (MTS_Doctor, 2026-10-19)

Scope: the machinery that builds MTS, not the trading engine. Docs in MyTradingSys/system/, role files, scripts/dev,
the hooks in .claude/settings.json, task cards, desk and relay, research/ folders. Something broke: DEBUGGING.md.
Numbers below were measured on origin/fast-track 2026-10-19 (bytes/4 = tokens); GUESS marks what was not measured.

## 1. Layers (each layer may call only the ones below it)
| Layer | What | Where | Rule |
|---|---|---|---|
| 1 Hooks | run on every session event, inject a few lines | `.claude/settings.json` -> scripts/dev/{shot,turn_meter,mts_signal,ci_watch,c_drive_guard,role_loader,stop_guard,model_guard}.py | never block a turn; shot, turn_meter, mts_signal log errors to a `hook_errors.log` |
| 2 Tools | deterministic scripts (T0) | scripts/dev/*.py; scripts/sched/ only for the live host | one script per concern; wired in wiring_registry.json |
| 3 Roles | a workflow loaded by name | MyTradingSys/system/roles/*.md, index ROLES.md | a role calls tools and reads docs; it never restates a rule |
| 4 Docs | the rules, one owner each | MyTradingSys/system/*.md | one source per concern (section 2); other files point, never copy |

## 2. One source of truth per concern
| Concern | Canonical | Others only point at it |
|---|---|---|
| boot and hard rules | CLAUDE.md (code), DSA_SESSION_PROMPT.md (DSA chat), AGENTS.md (Codex) | |
| start, ship, claims, worktrees | PARALLEL.md + `sync.py -h` | |
| hand-over | CLAUDE.md boot step 4 (overwrite NEXT_SESSION.md, ship; the coordinator starts the next session) | 01_AI_BEHAVIOR, DSA_SESSION_PROMPT |
| NEXT_SESSION.md format | RELAY.md "Task list standard" + `relay.py lint` (RELAY's dispatcher parts are retired) | QUICK_ANSWERS |
| scheduling | SCHEDULING_POLICY.md: no scheduled tasks or routines anywhere | every doc that names a retired task |
| worker type, turn and context budget | WORKERS.md (rule 5: turn cap = 4M / context) | CLAUDE.md, SUPER_SESSION, SUPERVISOR, roles |
| card fields, Definition of Ready, promotion gate | TASK_REFINEMENT.md | session_planner.md, lab_guy.md |
| roles | roles/*.md, index ROLES.md | |
| deploy | DEPLOY_RUNBOOK.md (manual hand deploy since the AutoDeploy task retired) | SURFACE_POLICY, HOW_MTS_RUNS, DSA_SESSION_PROMPT |
| machines, logins, lanes | HOW_MTS_RUNS.md, DEVICES.md, CLOUD_ACCOUNTS.md | |
| debugging | DEBUGGING.md | QUICK_ANSWERS.md |
| layers | LAYERS.md, layer_index.json | |
| operator decisions | OPERATOR_DECISIONS.md, CONTROL_ROOM.md | |

## 3. Measured map (2026-10-19)
- Docs: 61 top-level system/*.md before and after (61 - 2 archived + ARCHITECTURE + DEBUGGING), 9 role files. Largest: 03_FILE_INDEX
  19.6k tokens, OPERATOR_DECISIONS 16.7k, LESSONS_LEARNED 10k, 01_AI_BEHAVIOR 8.8k (one inbound reference), LAYERS 7.6k.
- Scripts: 101 non-test scripts/dev/*.py; wiring_scan: LIVE 309, DEV-TOOL 54, TEST-ONLY 129, ORPHAN 113 files repo-wide.
  The 12 NO-READER warnings all have real readers (research notes, cards, tests, promote.py): none is dead. Only dead
  pair found: dsa_eval.py + dsa_eval_scenarios.py (readers: their own test and one 2026-10-09 session note).
- scripts/sched: 25 entries. The relay machinery (relay.py 13k tokens, tick, dispatch_gate, go, autogo, run_worker,
  pick_task, register_*.ps1, relay_prompts/) is retired by SCHEDULING_POLICY but JIS-NB may still run legacy tasks until
  card `host-legacy-tasks-unregister` lands, so it is not provably dead yet (card `retire-relay-machinery`).
- Hooks: 8 scripts, median 366 tokens injected per session over 60 transcripts (max 11k). Small; not the cost.
- Boot (code session): CLAUDE.md 1.7k + STATUS 1.4k + ANNOUNCEMENTS 1.5k + NEXT_SESSION 2.0k = 6.6k tokens. Role extras:
  Pipeliner +17.4k (24.1k), Lab_Guy +12.6k, Eagle_Eyes +6.5k, Session_Planner +5.6k, Supervisor +3.2k, Q&A_Helper +2.7k,
  MTS_Doctor +1.4k, Network_Admin_Guy +0.6k, Artifacts +0.5k. token_audit (2 days): first-turn input about 48.7k.
- Cards: 398 (raw 21, refined 29, ready 66, blocked 7, done 247, dropped 28); 181 lack worker/est_turns; 275 closed
  cards still sit in tasks/. Desk queue 98 rows, claims 26, sessions/ 95 files (history, no new files).
- research/: 119 folders and 183 loose files, 121 of them dated .md.

## 4. What is wrong (findings)
1. Contradictions: docs still describe retired schedulers as running. SCHEDULING_POLICY says none run. Fixed in this
   change: DSA_SESSION_PROMPT (AutoDeploy, mts-dispatcher), CLOUD_ACCOUNTS ("recreate mts-dispatcher" would re-create a
   scheduler), SURFACE_POLICY, DSA_DELEGATION (MTS-DailyHygiene assigner), PARALLEL (MTS-Backup, daily tidy),
   QUICK_ANSWERS, 01_AI_BEHAVIOR, CLAUDE.md (relay KICK, MTS-Backup), AGENTS.md. Left as a card: DEPLOY_RUNBOOK body.
2. Duplicates: the "Promotion gate" block sat verbatim in session_planner.md and lab_guy.md (about 250 tokens each);
   the turn-budget rule is restated in 6 files; 5h pacing in 3. The CODEX_START / GEMINI_START overlap is kept on
   purpose (each lane reads only its own file).
3. Dated one-off docs in system/ with no live reader (archived, section 5).
4. Boot weight sits in role boots (Pipeliner 17.4k extra), not in hooks or CLAUDE.md.
5. Debugging had no single entry point: the right command was spread over QUICK_ANSWERS, MTS_DOCTOR, PARALLEL and
   script docstrings. DEBUGGING.md is now that entry point, with a test that fails when it names a missing path.

## 5. Deletions and merges
| Item | Action | Proof |
|---|---|---|
| BACKLOG_REFINE_2026-10-17, NB_HANDOFF_2026-10-16 | git mv to MyTradingSys/archive/system_2026-10-19/ | 0 inbound refs on trunk; one-off reports |
| Promotion gate block (session_planner, lab_guy) | merge into TASK_REFINEMENT.md, pointer left | identical text; role_loader retoken + check |
| dsa_eval.py, dsa_eval_scenarios.py, test_dsa_eval.py | git mv to _archive/2026-10-19-scripts-dev/ | no caller outside its own test, one session note and 03_FILE_INDEX; never run (no dsa_eval_history.jsonl, no Dumps sheet) |
| retired-scheduler sentences (section 4.1) | rewrite to the current procedure | SCHEDULING_POLICY.md |
| kept: DSA_AUDIT_RUN_PROMPTS_2026-10-17 (all 10 dsa-audit cards still ready), PLAN_4H_2026-10-18 (read by NEXT_SESSION, LENOVO_SETUP), HOST_WORKTREES_2026-10-15 (refs of operator decision 17), OPERATOR_GUIDE_LOG (open HALT question), PLAN_5H_2026-10-19, LAYER_MAP_NULLS_2026-10-19, fable_run_* briefs, LEFTOVERS_2026-10-15, PLAN_2026-10-17_NEXT_5H (cited as an example), HOST_TASKS_2026-10 | keep | live readers |

## 6. Savings (GUESS until token_audit re-measures)
- Promotion-gate merge: about 200 tokens off each Session_Planner and Lab_Guy boot (1 KB block, 0.2 KB pointer, measured).
- Archived docs: no boot read named them; the gain is fewer glob/grep hits and fewer wrong reads. GUESS 0-2k a session.
- The large lever is the role boots: Pipeliner diet (GUESS -8k to -10k on 24.1k), SUPER_SESSION rules to pointers
  (GUESS -2k for Supervisor and Pipeliner). These are follow-up cards because the files are in the traffic-controller lane.
- Not a lever: hooks (366 median), CLAUDE.md (1.7k, already capped).

## 7. Follow-up cards (worker, est_turns)
| Card | Worker | Turns | Why not here |
|---|---|---|---|
| retire-relay-machinery: archive scripts/sched relay files and relay_prompts/, full gate | session | 30 | needs `host-legacy-tasks-unregister` first |
| pipeliner-boot-diet: boot reads to pointers, target under 12k | agent | 10 | pipeliner.md is in the traffic-controller lane |
| super-session-rules-to-pointers, numbering kept | agent | 12 | collision with the traffic-controller lane |
| roles-md-index-slim | session | 15 | after traffic-controller and ru4 |
| tasks-sweep-closed-cards (`tasks.py sweep --apply`) | agent | 8 | 275 closed cards; separate ship |
| research-top-level-declutter + index | session | 30 | 183 loose files need per-file owner reading |
| deploy-runbook-manual-world: AutoDeploy text becomes history, manual deploy becomes the procedure | session | 15 | live-path procedure, own review |
| ai-behavior-fold-or-archive (01_AI_BEHAVIOR, 8.8k, one reader) | agent | 12 | rules must be checked against CLAUDE.md one by one |
| banner-test-retired: test_integrity test_6 also catches RETIRED banners | agent | 6 | RELAY.md and DEPLOY_RUNBOOK must move first |
| card-worker-fields: add worker/est_turns to 181 cards | agent | 10 | Session_Planner duty |

## 8. Review record (2026-10-19)
Reviewers: (a) Sonnet read-only agent: pytest on every test that names a changed file (358 passed), role_loader check,
hooks, DSA prompt build, CI and deploy readers; (b) GPT via `ask_model.py gpt`, read-only, on the full diff.
| # | Finding | Verdict |
|---|---|---|
| S1 | nothing breaks: no code reader of the moved files; roles ok; DSA prompt asserts pass | - |
| S2 | DEBUGGING said `tasks.py check` is read-only; it is in MUTATING (can demote) | accepted: row uses `tasks.py brief` |
| S3 | `echo {} \| <hook> hook` can bump a hook counter | accepted: noted in DEBUGGING section 2 |
| S4 | turn_meter.py:27 comment still quotes "40 tool turns" | rejected: a code comment, not a rule; no code ship for it |
| G1 | `tasks.py dispatch` may start work | rejected: its help says "ranked snapshot", it writes nothing |
| G2 | `desk.py sweep` mutates; short path | rejected (docstring: read-only dry run); accepted: full path written |
| G3 | `ci_red_card.py` files a card | accepted: marked dry run, `--apply` files it |
| G4 | hand-over canonical named RELAY.md, edits point at CLAUDE.md step 4 | accepted: section 2 split into hand-over and format rows |
| G5 | blanket "errors go to hook_errors.log" | accepted: only shot, turn_meter, mts_signal log errors |
