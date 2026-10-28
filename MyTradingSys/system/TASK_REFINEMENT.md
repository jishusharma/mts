# TASK REFINEMENT - how a raw idea becomes a task a fresh session can run with no questions (operator ask 2026-10-10)

Layer cards name their family: `tasks.py new "<title>" --layer tom` (ids in `layer_index.json`); the card then lists under that layer in `LAYERS.md` and its brief points there. Unknown ids fail the Definition of Ready.

Why: sessions are short (one task, ~50k tokens). A registry row is one line, and NEXT_SESSION.md was written by hand at the end of the
previous session, so every session re-derived scope, files and the done-test from scratch, and a vague task cost a whole session.
Refinement moves that scoping work to a cheap, separate step that runs ahead of the builders and keeps a stock of ready work.

## Nothing new to look at, nothing duplicated
| Thing | Stays the owner of |
|---|---|
| `research/BUGS.md` | ids and status (B-/T- rows). A card never carries its own status for a registry row |
| MTS Control Room | the operator's page. Its new **Backlog** section is a view of the cards plus request buttons |
| `desk.py` / DSA | run-and-report jobs. A card with lane `DSA*`/`JIS-NB` becomes (or points at) one desk task |
| `sync.py` claims | who is working on what. `tasks.py take` records state, the claim is still the lock |
| `relay.py` / NEXT_SESSION.md | the hand-over. Its TASK list is now built from `tasks.py next`, not re-written by hand |

New is only: `scripts/dev/tasks.py`, cards in `MyTradingSys/system/tasks/<id>.json`, and the Backlog section of the page.

## The card (one JSON per task, sorted keys, ships with `sync.py ship`)
`id` (registry id, else a slug), `title`, `state`, `prio` 1-5, `lane`, `size` S|M, `est_turns` (int), `worker` agent|session, `goal`, `scope_in`, `scope_out`, `steps`, `commands`,
`tests`, `done_when`, `sources`, `depends_on`, `refs`, `live_path`, `approved_by`, `note`, `latest` (see State tag).
- `refs` = registry rows this card closes while they are OPEN. A follow-up of a closed row (B160, B149) has NO refs: `sweep` retires a card whose refs are all closed.
- States: `raw` (captured) -> `refined` (being scoped) -> `ready` (passes the gate) -> `active` -> `done`; `blocked` (operator hold) and `dropped`.
- Lanes (cheapest tier that can do it): `DSA`/`DSA-NB`/`DSA-NUC` run-and-report; `HAIKU`, `SONNET` code and docs; `OPUS` only with `approved_by`; `JIS-NB` live host (desk task); `CODEX` layer lab (needs `kind` audit/run/build, LAYER_LAB.md; hidden from a plain `tasks.py next`).

## State tag and LATEST (operator ask 2026-10-17: no searching for what is done where)
Optional card fields `latest` (list of `{kind: ship|report|audit|decision|signal, ref: sha or path, utc, line}`, newest first, max 6), `scope_sha`, `refreshed`; code in `scripts/dev/task_state.py`.
- `tasks.py brief <id>` ends with `STATE <tag>` and the newest 3 `LATEST` lines: the last commit over the card's scope paths (ship), the newest .md naming the card or its refs, the newest .md inside scope (audit if its name says so), plus manual ones. Read these before grepping anything.
- Tag (derived, never trusted from the file): `READY`, `ACTIVE@<host>`, `SHIPPED@<sha>` (last commit touching the card JSON), `STALE:<why>` (scope changed after the last refresh, or all refs closed), else the state.
- `tasks.py tag <id> [--refresh] [--add kind:ref --line ".."]` records a pointer (a decision, a signal); `tasks.py check` promotion refreshes, `tasks.py done` adds the ship entry, `tasks.py take` does not (a stale card shows STALE in its brief).
- `tasks.py stale [--refresh]` lists ready/active cards whose scope paths changed since `refreshed` (refresh only after re-reading the card against the change). `lint` fails a ready card never refreshed, or stale longer than 24 h (the refiner refreshes on its hourly line; a fresher lag only shows as STALE).

## Definition of Ready (`tasks.py check`, fail closed; also in the offline gate as `tasks.py lint`)
A card is `ready` only if all hold, and the tool names every miss:
1. goal, done_when (an observable: file, row count, number), at least one scope_in and one step.
   Backtest and audit cards: done_when also says "exports `sim_desk/results/<id>.json`" (schema: research/sim_desk/DESIGN.md).
2. lane valid; size S or M (an L card is split first); for SONNET/HAIKU/OPUS cards `est_turns` (whole number, <= 40, else split) and `worker`: agent only for size S and est_turns <= 15, else session (WORKERS.md; `tasks.py check` enforces it).
3. Code lane: `tests` names the fail-first test. Run lane: copy-ready `commands`. OPUS: `approved_by`.
4. `live_path` cards are lane JIS-NB only (builders never touch the live tree, restart, or open trades).
5. No placeholder text (TBD/TODO/figure out), each field <= 400 chars, rendered brief <= 30 lines (CLAUDE.md prompt rule).
6. Every `depends_on` is a done card or a CLOSED/WONTFIX registry row.
A ready card that later fails (a dependency reopens, someone edits it) is not served by `next`/`brief`/`take`, and `lint` goes red.

## Who refines, and when (the mechanism)
1. **Capture is free and immediate**: any session that finds follow-up work, and Control Room pickup for every Inbox `task`/`requirement`,
   runs `tasks.py new "<title>" [--ref B###] [--from-inbox <id>]`. Raw card, zero scoping cost at that moment.
2. **Refiner session** (runs inside the dispatcher session on its HOURLY line, so on the routine model: Haiku 5.5, set in the App, RELAY.md; reads files, writes no product code): takes raw/refined cards by priority, up to 3 per session:
   read the registry row and its evidence, grep for the files and the source quote, fill the card, run `tasks.py check <id>`. Anything that is
   "run it and read numbers" it delegates as a DSA desk task instead of scoping the answer itself. A question only the operator can answer
   becomes a Control Room decision, and the card waits as `refined` with the reason in `note`.
3. **Trigger**: `tasks.py status` prints `REFINE_NEEDED` when a raw card is over 1 h old, or cards wait and fewer than 3 are ready, else `REFINE_OK`. `relay.py tick` computes
   that line hourly (T0); at NEEDED the dispatcher runs the refiner, not a builder. A relay session also runs `tasks.py next` at
   hand-over: no ready card = refine first, never hand over a vague task.
4. **Builder session**: `tasks.py next` -> `tasks.py brief <id>` is its whole prompt -> `sync.py claim` -> work -> `tasks.py done <id> --result` -> ship -> release.
5. **Retire**: `tasks.py sweep --apply` (Control Room pickup or refiner session; never the live tree) closes cards whose registry rows closed.

## Refiner run (the dispatcher's HOURLY line; any session can run it by hand)
`relay.py tick` does the worktree and status in T0, once per 55 min (`../mts-refiner`: create, or fetch + merge origin/fast-track; then `tasks.py status`).
The model does step 3 only when the tick prints `HOURLY refine=REFINE_NEEDED`; `REFINE_OK` needs nothing. By hand: skip if `~/.claude/mts-relay-stop` exists,
update that worktree (`git -C <wt> fetch -q origin`, then `git -C <wt> merge -q origin/fast-track`, each its own call), run `python scripts/dev/tasks.py status`. Never the live tree.
3. `REFINE_NEEDED`: `sync.py claim "refine <ids>"`; take at most 3 refinable cards (`tasks.py list --state raw`, then `refined`; priority order). Per card:
   read the registry row + its evidence file, grep for the files and the source quote, fill the card (Edit the JSON), `tasks.py check <id>`.
   - Passes: it is `ready`. Does not pass after your best effort: `tasks.py tried <id>` (a second miss parks it).
   - Needs a fact only the operator has: `tasks.py tried <id> --asks "<one short question>"`; the page shows it, the answer comes in the Inbox.
   - Needs numbers from a run: post a DSA desk task (DSA_DELEGATION.md) and leave the card `refined` with the desk id in `note`; do not run it yourself.
   - Size L: split into S/M cards (`tasks.py new`), drop the parent with a note. A new defect or task still gets its BUGS.md row under that file's rules.
4. Product code is out of scope for the refiner (cards, docs, desk posts only). Run `tasks.py stale`: for each listed card re-read the change, then `tasks.py tag <id> --refresh` (or park it with `tried`). `tasks.py lint`, `sync.py ship --release <slug>`.
5. One pass per HOURLY line, 3 cards max, routine model. The brake: a card gets 2 tries, a question parks it at once, and parked cards do not count toward REFINE_NEEDED.

## Operator controls (Control Room > Backlog; no other page)
Per card: Move to top, Hold, Drop, and Approve Opus where a card names Opus. A click writes a `taskops` doc (`task`, `action`, `at`, `applied`)
to the artifact db, exactly like a decision. Pickup applies each unapplied one with `tasks.py apply-op <id> bump|hold|drop|approve [--note ..]`
and sets `applied: "<date>"` on the doc. A held card comes back with `apply-op <id> release`. A card parked on a question (`asks`) shows it on the page; the operator answers in the Inbox, pickup copies the answer into the card `note` and runs `apply-op <id> retry`. Adding a task is the Inbox (kind Task): the
pickup turns it into a raw card and replies with the card id. The operator never edits a card.

## Promotion gate (tasks.py, enforced since commit 35c10e93, 2026-10-18, Opus review of planner batch 3; Lab_Guy owns the stamp for C1+)
- Stamp grammar (both accepted): `REVIEWED:<date> <ACCEPT|T0-ONLY>` (planner) and `REVIEWED: <reviewer> <date>` (legacy). T0-ONLY is machine checks only, not a review.
- `tasks.py check` promotes a card to ready only if: no active HOLD/STOP announcement is named in the note (`HOLD A-...`; clear it with `HOLD-CLEARED A-...` once lifted), and IMPORTANT/C1+ cards carry a real stamp (ACCEPT or reviewer-date). ROUTINE/C0 may stay T0-ONLY.
- `take` and `done` additionally refuse CRUCIAL/CRITICAL or C2/C3 cards without a real stamp; a `live_path: true` card counts as C3.
- Order: planner drafts and proposes weight and class; ONE batched Lab_Guy pass (up to 5 cards, Sonnet, Google pool) confirms or raises the class and writes the real stamp; C2 also needs a non-Claude spec review; C3 also the coordinator. A random sample of C0 cards is checked for under-classification.

## Rules
- The card text is the contract: a builder that needs to ask a question hands the card back as `refined` with the question in `note`.
- Cost: capture costs nothing, refinement is Sonnet/Haiku/DSA, builders get a <= 30-line prompt. Nobody pays to re-derive scope.
- Numbers rule (2026-10-13): a card that sets a parameter labels it SOURCED (quote + file:line in `sources`) or OURS (chosen on DEV, checked once on VALIDATION).
- PRE_REG template (`research/gross_effect_screen_2026-10-15/PRE_REG.md`): before freezing, run `python scripts/dev/verdicts.py check "<family words>"` and paste its output; append your row after RESULT (`verdicts.py backfill`; `verdicts.py count --split DEV` is the m for a Holm adjustment; `prereg_gate.py --m auto --new-cells <N>` uses it, so every PRE_REG has one m: DEV variants + your new cells). Then run `python scripts/dev/prereg_gate.py --n <days> --sd <sd of per-event R, with --sd-source <file:line> unless > 1> --cost <mean(14/stop_i) in R, not 14/median stop> --m <m|auto>`: exit 1 = MDE + cost exceeds the 0.30 R plausible gross (OURS), so do not freeze. Registry: `research/VERDICTS.csv`; exit 1 = a one_run PRE_REG or a FAIL already covers this family.
- Weight and review gate (lab_guy v3.1): `weight` is routine|important|crucial|critical (plus B-SHARED, set automatically) and the optional class is C0-C3 (`class` field or `class=Cn` in the note). The reviewer/planner sets them, never the producer. A card of weight crucial/critical or class C2/C3 cannot be `take`n or marked `done` without `REVIEWED: <who> <date>` in its note, and `done` also needs a non-empty `--result` receipt (`tasks.py review_gate`). routine/important/C0/C1 are not blocked. OPUS-lane cards still need `crucial`.

Result (2026-10-17): the state tag + LATEST block ship with `tasks.py tag|stale`; 33 ready cards were refreshed once, lint stays green.
