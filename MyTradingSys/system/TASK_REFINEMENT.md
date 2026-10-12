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
`id` (registry id, else a slug), `title`, `state`, `prio` 1-5, `lane`, `size` S|M, `goal`, `scope_in`, `scope_out`, `steps`, `commands`,
`tests`, `done_when`, `sources`, `depends_on`, `refs`, `live_path`, `approved_by`, `note`.
- `refs` = registry rows this card closes while they are OPEN. A follow-up of a closed row (B160, B149) has NO refs: `sweep` retires a card whose refs are all closed.
- States: `raw` (captured) -> `refined` (being scoped) -> `ready` (passes the gate) -> `active` -> `done`; `blocked` (operator hold) and `dropped`.
- Lanes (cheapest tier that can do it): `DSA`/`DSA-NB`/`DSA-NUC` run-and-report; `HAIKU`, `SONNET` code and docs; `OPUS` only with `approved_by`; `JIS-NB` live host (desk task); `CODEX` layer lab (needs `kind` audit/run/build, LAYER_LAB.md; hidden from a plain `tasks.py next`).

## Definition of Ready (`tasks.py check`, fail closed; also in the offline gate as `tasks.py lint`)
A card is `ready` only if all hold, and the tool names every miss:
1. goal, done_when (an observable: file, row count, number), at least one scope_in and one step.
2. lane valid; size S or M (an L card is split first: it must fit one ~50k-token session).
3. Code lane: `tests` names the fail-first test. Run lane: copy-ready `commands`. OPUS: `approved_by`.
4. `live_path` cards are lane JIS-NB only (builders never touch the live tree, restart, or open trades).
5. No placeholder text (TBD/TODO/figure out), each field <= 400 chars, rendered brief <= 30 lines (CLAUDE.md prompt rule).
6. Every `depends_on` is a done card or a CLOSED/WONTFIX registry row.
A ready card that later fails (a dependency reopens, someone edits it) is not served by `next`/`brief`/`take`, and `lint` goes red.

## Who refines, and when (the mechanism)
1. **Capture is free and immediate**: any session that finds follow-up work, and Control Room pickup for every Inbox `task`/`requirement`,
   runs `tasks.py new "<title>" [--ref B###] [--from-inbox <id>]`. Raw card, zero scoping cost at that moment.
2. **Refiner session** (Sonnet; Haiku for S cards; reads files, writes no product code): takes raw/refined cards by priority, up to 3 per session:
   read the registry row and its evidence, grep for the files and the source quote, fill the card, run `tasks.py check <id>`. Anything that is
   "run it and read numbers" it delegates as a DSA desk task instead of scoping the answer itself. A question only the operator can answer
   becomes a Control Room decision, and the card waits as `refined` with the reason in `note`.
3. **Trigger**: `tasks.py status` prints `REFINE_NEEDED` when cards wait and fewer than 3 are ready, else `REFINE_OK`. The dispatcher and the
   relay gate read that line; at NEEDED the next fired session is the refiner, not a builder. A relay session also runs `tasks.py next` at
   hand-over: no ready card = refine first, never hand over a vague task.
4. **Builder session**: `tasks.py next` -> `tasks.py brief <id>` is its whole prompt -> `sync.py claim` -> work -> `tasks.py done <id> --result` -> ship -> release.
5. **Retire**: `tasks.py sweep --apply` (Control Room pickup or refiner session; never the live tree) closes cards whose registry rows closed.

## Refiner run (the dispatcher's step 2b; any session can run it by hand)
The dispatcher cannot launch another session (App approval), so it does this inline, only on a tick where the relay step was IDLE.
1. Skip if `~/.claude/mts-relay-stop` exists. Worktree `C:/Users/E-ngineers/IdeaProjects/mts-refiner` (create: `git -C <live> worktree add ../mts-refiner -b jisnb/refiner origin/fast-track`;
   reuse: `git -C <wt> fetch -q origin`, then `git -C <wt> merge -q origin/fast-track`, each its own call). Never the live tree.
2. `python scripts/dev/tasks.py status`. `REFINE_OK`: stop, nothing else to do (this is the common, cheap tick).
3. `REFINE_NEEDED`: `sync.py claim "refine <ids>"`; take at most 3 refinable cards (`tasks.py list --state raw`, then `refined`; priority order). Per card:
   read the registry row + its evidence file, grep for the files and the source quote, fill the card (Edit the JSON), `tasks.py check <id>`.
   - Passes: it is `ready`. Does not pass after your best effort: `tasks.py tried <id>` (a second miss parks it).
   - Needs a fact only the operator has: `tasks.py tried <id> --asks "<one short question>"`; the page shows it, the answer comes in the Inbox.
   - Needs numbers from a run: post a DSA desk task (DSA_DELEGATION.md) and leave the card `refined` with the desk id in `note`; do not run it yourself.
   - Size L: split into S/M cards (`tasks.py new`), drop the parent with a note. A new defect or task still gets its BUGS.md row under that file's rules.
4. Product code is out of scope for the refiner (cards, docs, desk posts only). `tasks.py lint`, `sync.py ship`, `sync.py release <slug>`.
5. One pass per tick, 3 cards max, Sonnet. The brake: a card gets 2 tries, a question parks it at once, and parked cards do not count toward REFINE_NEEDED.

## Operator controls (Control Room > Backlog; no other page)
Per card: Move to top, Hold, Drop, and Approve Opus where a card names Opus. A click writes a `taskops` doc (`task`, `action`, `at`, `applied`)
to the artifact db, exactly like a decision. Pickup applies each unapplied one with `tasks.py apply-op <id> bump|hold|drop|approve [--note ..]`
and sets `applied: "<date>"` on the doc. A held card comes back with `apply-op <id> release`. A card parked on a question (`asks`) shows it on the page; the operator answers in the Inbox, pickup copies the answer into the card `note` and runs `apply-op <id> retry`. Adding a task is the Inbox (kind Task): the
pickup turns it into a raw card and replies with the card id. The operator never edits a card.

## Rules
- The card text is the contract: a builder that needs to ask a question hands the card back as `refined` with the question in `note`.
- Cost: capture costs nothing, refinement is Sonnet/Haiku/DSA, builders get a <= 30-line prompt. Nobody pays to re-derive scope.
- Provenance rule still applies: a card that sets a parameter cites the trader quote + file:line in `sources`, or it is NO-SOURCE.
