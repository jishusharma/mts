# ROUTING: which kind of work goes where (canonical, owner: Pipeliner role, operator 2026-10-18)

One table: kind of work -> machine -> channel -> model -> who checks. Other files point here for routing; they keep their own
procedures (how to post a desk row, how the lab runs a card). Changes come from the operator through the Pipeliner session
(ROLES.md row Pipeliner); a change that alters how sessions behave also gets an ANNOUNCEMENTS.md entry and one signal line.

## Changes (newest first)
- 2026-10-20 roles merged (DOCTOR-NB-1020): Traffic_Controller folded into Pipeliner (any device, one at a time by lease); Q&A_Helper + Network_Admin_Guy -> Admin_Guy (also takes BACKLOG intake: card via `tasks.py new`, lane per this table, one signal line); Artifacts_Guy -> 1985Artifacts_Guy; old names are aliases.
- 2026-10-19 Pipeliner opening 5 (`DRAIN_2026-10-19.md` s4): decided C7 myself. The 7 DSA-NB audit rows stay on DSA-NB (not re-routed to cards); they wait on the 0.7.1 install and go to cards if still untaken 24 h after both installs. NUC copy of AIBridge reads 0.7.1; the `extension.pre_0.7.1` backup is missing (operator to confirm).
- 2026-10-19 Pipeliner (operator: DSA stops between turns, hands-free unchecks): cause is that AIBridge v0.7.1 (3270e742, handsfree test 7/7) is on trunk but F:/AIBridge/extension is still 0.7.0 on NUC (NB row 20261018-170620 pending 12 h). Posted a JIS-NUC install row. C7 decision: the 7 DSA-NB audit rows stay on DSA lanes and resume after the install; if untaken 24 h after both installs, re-route to cards.
- 2026-10-19 Pipeliner opening 4 (`DRAIN_2026-10-19.md` s3): sweep only, no row closed; 7 DSA-NB audit rows now 75 h untaken (C7 unchanged, operator answer still needed); raw card `rsi-cross-unmapped-and-pivot-stack` routed to lane SONNET, waits on a Lab_Guy ACCEPT (T0-ONLY stamps no longer pass the promote gate).
- 2026-10-19 Pipeliner opening 3 + Session_Planner YT pass (`DRAIN_2026-10-19.md`): aligned YouTube/video tasks with `GROUND_LEVEL_YOUTUBE_EXTRACTIONS_STRATEGY_2026-10-18.md` (dropped 4 saturated/429-blocked scraping cards, closed 2 delivered cards, unblocked `krown-other-sources-event-study-videos`, created `malkan-w1hr-local-whisper-asr` and `malkan-gfs-btc-htf-prereg`); drained 5 desk rows (21 -> 16 pending: closed T02, T03, Fable run 2, Krown P3rDSh187TE, and converted Trend-Line review row to card `trendline-audit-gaps-disposition`).
- 2026-10-18 Pipeliner opening 2: routed RU3-RU9, ship-gate fast path and tasks.py fill (section 'Routed open items' at the bottom); sweep: 9 DSA-NB audit rows 65 h old, 1 stale NB claim.
- 2026-10-18 created by Pipeliner from HOW_MTS_RUNS.md (2026-10-15), CLAUDE.md Cost and routing, DSA_DELEGATION.md, WORKERS.md (10-17/18),
  SCHEDULING_POLICY.md (10-17), ANNOUNCEMENTS A-20261018-3/-4/-6/-7, GEMINI_START.md (10-18), LAB_RECIPES.md (10-16),
  research/lab_guy/TANDEM_PLAN_2026-10-18.md. Where two disagreed the newer operator-dated rule was taken; conflicts are at the bottom.

## Channels (what each one is)
| Channel | What it carries | Picked up by |
|---|---|---|
| Card (`tasks.py new`, lane field) | any build, code, test, refine, audit or study work; the default for anything that needs judgment | lane HAIKU/SONNET/OPUS: a Claude session or Agent the coordinator starts (WORKERS.md); lane CODEX: `codex_run.py` (GPT lab) or Gemini; lanes DSA*/JIS-NB: run cards, `desk.py assign` turns ready ones into desk rows |
| Desk row (`desk.py post --target T`) | one run-and-report job with exact commands, or a job that needs a specific machine | target DSA / DSA-NB / DSA-NUC: the DeepSeek bridges (`desk.py next`); target JIS-NB / JIS-NUC: a Claude session on that machine (the super-session coordinator sweeps them); target CLAUDE: any Claude session (a DSA task that failed twice) |
| `gemini_queue.py run <card>:<effort>` | a CODEX-lane card that needs Gemini to run commands (search, transcript fetch, video read) | Gemini Flash in a throwaway worktree `F:/MTS/gq/<id>`, branch `gemini-q/<id>`; a Claude session reviews the branch and ships it |
| **Gemini-designated card** | a CODEX-lane card whose title starts `[GEMINI]` (Argon blind-reads, vendor cross-reviews, audit and doc cards); the dispatcher adds the tag when it creates or refines the card, GPT cards carry none | a Gemini builder lists them with `python scripts/dev/tasks.py list --lane CODEX --state ready` and takes the ones tagged `[GEMINI]`; `codex_run.py` skips them | the dispatcher (Claude coordinator) |
| `codex_run.py tick / next` | CODEX-lane cards for GPT, one at a time (lab.lock), spend guard 10 runs per 5 h | the super-session coordinator on wake (no scheduler, SCHEDULING_POLICY.md) |
| Signal (`mts_signal.py send --kind note|ask`) | one line between machines/logins; points to a desk row, card or board entry; never carries the task | every session (hook shows it within ~5 min) |
| Board (ANNOUNCEMENTS.md) | durable INFO / DO-NOW / CONTINUE / HOLD / STOP for many sessions; STOP and HOLD need operator OK (PROPOSED until then) | every session at boot |
| Control Room Inbox | the operator's questions and ideas; Admin_Guy files decisions in OPERATOR_DECISIONS.md | Admin_Guy; run-and-report items become desk rows, builds become cards |

## The table
| Kind of work | Machine | Channel | Model | Who checks |
|---|---|---|---|---|
| Live-path code (auto_trader, position manager, Java feeds, safety checks), new strategy logic, formula tests | any Claude machine (work tree) | card, lane SONNET (OPUS only per WORKERS.md rule 6) | Sonnet | diff-only review Agent before ship (SUPER_SESSION rule 11); CI |
| Deploy to the live tree, process checks, HALT state reads | JIS-NB | desk row `--target JIS-NB` (or the NB coordinator's deploy step, DEPLOY_RUNBOOK.md) | Sonnet session on NB | operator for anything that restarts trading; coordinator checks health after |
| Screenshot and chart reads, live-market watch | JIS-NB (live files); any device via `live_mirror.py brief` (stale-stamped `mirror@<utc>`, no verdicts from STALE) | Eagle_Eyes / live watcher session; `shot.py` | Sonnet | Eagle_Eyes logs each read; LAB-VERIFY items go on as below |
| Eye-read flag that needs a DEV-data check (LAB-VERIFY) | JIS-NUC | card in the lab (lane CODEX or SONNET, weight set), not a desk row (see conflict C4) | GPT luna / Sonnet | Lab_Guy class per `roles/lab_guy.md` |
| Fetch of 1m klines / Dukascopy / anything needing NB disks or NB's open network | JIS-NB | desk row `--target JIS-NB` (Claude) or `--target DSA-NB` (DeepSeek) when commands are exact | Sonnet / DeepSeek | poster spot-checks one count |
| Fetch of public data into F:/MTS/data (daily, 1h, funding, metrics) | JIS-NUC | desk row `--target DSA-NUC`, or a CODEX/SONNET card when a new script is needed | DeepSeek / Sonnet | poster spot-checks one count |
| Run an existing script with new args, inventories, counts, stratify an existing CSV | JIS-NUC (lab data) or the machine holding the data | desk row `--target DSA-NUC` / `DSA-NB` / `DSA` | DeepSeek | Claude spot-checks ONE number (DSA_DELEGATION.md) |
| Lab cards: audits, re-derivations, planted-error trial, retro-audit, spec-derived tests | JIS-NUC | card lane CODEX -> `codex_run.py` (order per A-20261018-3) | gpt-6-luna medium; Sol 6.1 / Astra per LAB_RECIPES.md; astra only for `crucial` | Lab_Guy: C0 machine checks, C1+ cross-vendor review + independent re-derivation (A-20261018-1) |
| Cross-vendor review of a Claude or GPT result | JIS-NUC | card lane CODEX for Gemini (`gemini_queue.py`) or GPT (`codex_run.py`); a reviewer never the producer's model | Gemini Flash (Argon for C2/C3) / GPT | Lab_Guy; producer != reviewer (GEMINI_START rule 8) |
| Cross-vendor review of a Gemini result | JIS-NUC | card lane CODEX for GPT, or a Claude Sonnet Agent | GPT / Sonnet | Lab_Guy |
| YouTube / video / transcript search and caption fetch | JIS-NUC (search) / JIS-NB (local Whisper ASR) | `gemini_queue.py` (Gemini search grounding, no anonymous yt-dlp loops that hit HTTP 429); local Whisper ASR (`asr_transcribe.py` on JIS-NB) for Hinglish/uncaptioned audio on disk; halt saturated Tom/Fabio/TA101 meta scraping (`GROUND_LEVEL_YOUTUBE_EXTRACTIONS_STRATEGY_2026-10-18.md`) | Gemini Flash / faster-whisper | `verify_extract_quotes.py` on every extract; edge-before-extraction HTF pre-reg before new video batches |
| Card refinement, ranking, weight tags, stale blocks | the machine with a running super session | Session_Planner pass inside the coordinator | Sonnet medium | the coordinator reads the dispatch table |
| Scoped mechanical edits, lookups, registry upkeep, is-it-on-trunk checks | any | one-use Haiku Agent from the session that owns the task (max 5 at once; Pipeliner max 2) | Haiku | the session spot-checks one claim |
| Docs, routing, board, desk drains, allocation across logins | any device (Pipeliner, one at a time by lease) | ROUTING.md, ANNOUNCEMENTS.md, desk rows, cards | Sonnet | operator for STOP/HOLD |
| Published pages (MTS Home, Control Room, Layers, Research Map) | any device signed in as the jishusharma1985 login | 1985Artifacts_Guy; a desk row asks for it | Sonnet | 1985Artifacts_Guy opens every link |
| claude.ai login-side jobs (routines, pages owned by one login) | the machine where that login is signed in | desk row `--target JIS-NUC` or `JIS-NB` naming the login; the operator does Share steps | Sonnet | operator |
| AI health, process audit | any | MTS_Doctor (by hand) | Sonnet | Haiku + fresh Sonnet agents |
| Console-window, launcher, network faults | the host it happens on | Admin_Guy (Part C); card `Network:`; deploy by desk row `--target JIS-NB` | Sonnet | fail-first test |
| Operator questions and decisions | any | Control Room Inbox -> Admin_Guy -> OPERATOR_DECISIONS.md | Sonnet 5.5 medium; judgement goes up as a card | operator decides |

Rules that apply to every row: work in the printed worktree, never the live tree; share only by `sync.py ship`; no scheduler or routine starts
anything (SCHEDULING_POLICY.md); cheapest first (T0 script, DeepSeek, Haiku, Sonnet; Opus only when the operator names it or WORKERS.md rule 6);
build or code work is a card, never a desk row; a desk row needs exact commands and one observable done-when.

## Conflicts for the operator (newer rule applied until you say otherwise)
- C1 Where DeepSeek run-and-report goes: DSA_DELEGATION.md (10-09) routes by data location (1m klines only on JIS-NB -> DSA-NB; 1h/1d, transcripts -> DSA-NUC). A-20261018-4 (10-18) says run-and-report for the lab goes to the NUC by `--target DSA`, but `DSA` is taken by whichever bridge boots first, NB or NUC. Applied: data location decides (DSA-NB / DSA-NUC); `--target DSA` only when either machine can run it.
- C2 GPT lab host: HOW_MTS_RUNS.md and A-20261018-4 put Codex/GPT on JIS-NUC (`F:/MTS/mts-codex-lab`); the NUC signal of 2026-10-18 15:48Z calls the stalled lab "NB host". `codex_run.py status` reports STALLED (16 ready, nothing ran for 17 h). Applied: NUC. Needs one answer: which machine runs `codex_run.py tick` today.
- C3 Daily desk assigner: DSA_DELEGATION.md says `desk.py assign` runs daily via MTS-DailyHygiene; SCHEDULING_POLICY.md (10-17) retired that task. Applied: the super-session coordinator runs `desk.py assign` by hand on wake.
- C4 LAB-VERIFY routing: ROLES.md Eagle_Eyes row says `desk.py post --target DSA`; but `DSA` means the DeepSeek bridges, and the item needs a DEV-data study with judgment (lab, Lab_Guy class). Applied: it becomes a lab card on the NUC; Eagle_Eyes may still post the desk row, Pipeliner converts it.
- C5 Gemini model names: LAB_RECIPES.md (10-16) names "Gemini 2.5 Pro" for build-review; GEMINI_START.md (10-17/18) says the AI Pro login has only Antigravity models (Gemini 3.8 Flash, Gemini 4 Argon) and `gemini_queue.py` is Flash only. Applied: Flash, Argon for C2/C3.
- C6 HOW_MTS_RUNS.md (10-15) still says the live tree changes only through MTS-AutoDeploy and lists dispatchers as running (marked RETIRED in place); SCHEDULING_POLICY.md and CLAUDE.md (manual or coordinator deploy) win.
- C7 DeepSeek bridges: 11 DSA-NB rows (the DSA audit T01-T10 batch, posted 10-16) and older DSA rows have not been taken for 2+ days; no file says whether the bridges are still run daily (decision D12 "once a day"). Applied: rows stay on DSA lanes; the operator starts a DSA session when wanted.

## Routed open items (Pipeliner, 2026-10-18; all lane SONNET, any Claude machine, JIS-NUC first)
| Item | Card | Worker / est | Host and order | Checker |
|---|---|---|---|---|
| RU3 shot.py bundle (Eagle_Eyes) | ru3-eagle-eyes-shot-py-bundle-evidence-p | session / 25 | any; independent | diff-only review Agent |
| RU4 role_loader.py lint | ru4-mts-doctor-role-policy-lint-roles-md | agent / 14 | any; independent | fixture with known contradiction |
| RU5 lab pre-check in tasks.py | ru5-lab-guy-zero-token-lab-pre-check-in- | agent / 12 | any; FIRST of the tasks.py trio | fail-first test |
| RU6 content-bound review receipts | ru6-lab-guy-content-bound-review-receipt | session / 28 | after RU5 ships (same file) | diff-only review Agent |
| RU7 operator_questions.py pending | ru7-q-a-helper-operator-questions-py-pen | agent / 12 | any; independent | fixture log |
| RU8 nowin.py audit | ru8-network-admin-guy-nowin-py-spawn-dia | agent / 12 | any; independent | fixture spawn |
| RU9 artifacts.py audit-links | ru9-artifacts-guy-artifacts-py-audit-lin | agent / 14 | any; independent | fixture registry |
| Ship gate fast path (<60 s) | ship-gate-fast-path-under-60s | session / 35 | any; ask NB by signal for the unshipped NB agent branch first | review Agent; CI full suite |
| `tasks.py fill` subcommand | tasks-fill-raw-card-fields | agent / 14 | after RU5 and RU6 (same file) | fail-first test |
Gate speed: GATE_SPEED.md D1-D7 landed (precheck, fail-fast, record, targeted tests; clean full gate still 544 s). The affected-tests-only
fast path with CI-owned full suite and red-CI-blocks-next-ship is NOT on trunk (no commit, branch or card found by topic words), hence the card.
