# What Is Next

Written: 2026-09-16
Purpose: the remaining work in one place, in the order it makes sense to
do it. Plain names only.

## Rule for reading this file

Each item says what it is, what it needs, and who can start it. Nothing
gets done until the "needs" column is filled. No item is guessed at.

## Stage 1 - Ready now, no outside input needed

These can be closed with one command each from the current session.

| item | what it is | what it needs |
|---|---|---|
| Duplicate function cleanup | A function called Get-Descendants exists in two scripts. Decide: extract to a shared file, or leave. | One decision from you. |
| Structure audit output | Write the structure audit file with current tree, duplicate scan, orphan list, and target tree. | One command to produce a duplicate scan and full file listing. |
| Open-loops sweep output | Write the open-loops sweep file with plain titles and current status for each open item. | One command to print one script body and the middle of the session log. |

## Stage 2 - Needs source documents pasted

These are blocked only because the source material is not in the chat.
Everything is on disk. Each one needs its source pasted before output.

| item | what it is | what it needs |
|---|---|---|
| Schema spec | A spec for sixteen new session fields: names, types, where computed, where written. | Paste: compiled-output audit body, data schema body, project vision body. |
| Gap audit | A list of every concept from the source transcripts that is not yet implemented in the system. | Paste: compiled engine body, six condition file bodies, consolidated rules body. Large; must be sliced. |

## Stage 3 - Pending your decision

Nothing moves on these until you decide.

| item | decision needed |
|---|---|
| Rename or keep the seven live shortcuts | Current recommendation: keep them, they are already documented and used in commands file. |
| Rename or keep open-loop numbers | Current recommendation: keep the number, add a plain title next to it. |
| Folder renames | Current recommendation: plan this session, do next session in a quiet window. |
| Pull duplicate function into shared file | Two copies exist. Extract or leave? |
| Confirm the A, B, E mapping | The letters were shorthand in the task package. Mapping proposed in the name audit. Confirm or correct. |

## Stage 4 - Deferred by design

Nothing to do now. Listed so it is not forgotten.

| item | when | note |
|---|---|---|
| Folder renames | After Stage 3 decision | Each folder move touches many files. Do it in one window with nothing else running. |
| Dumps cleanup | After 2026-09-21 | The large one-time snapshot files stay until then. Check for readers first. |
| Open-loops full sweep | After Stage 2 | Uses the sweep output as input. |

## Order to work in

1. Stage 3 first. Decisions here unblock everything else.
2. Stage 1 next. Each item closes in one command.
3. Stage 2 third. Larger, needs pasting.
4. Stage 4 last. Nothing urgent.

## What "done" looks like

- All four worker output files exist in the research folder.
- Open loops each carry a plain title and a current status.
- Dictionary lists every term used in docs or prompts.
- Renames executed or explicitly rejected.
- Working tree clean, tag matches head.

## End