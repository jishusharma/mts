# NUC builder test — 4 tasks, 2026-09-27 (Sonnet)

Queued 4 self-contained tasks to the live NUC worker (qwen3-coder:30b) via
queue_tool.py: 007 (E3, deribit error codes), 008 (G4, BUGS.md rows F10-F12),
009 (G1, FILE_INDEX EXECUTION/BACKTEST sections), 010 (G4, BUGS.md rows F7/F9).
All 4 completed and replied within ~4 minutes total.

## Mechanical verdicts (queue_tool.py verify)
007: PARTIAL / REVIEW (6/6 EXPECT matched, 0 unknown names)
008: BLOCKED / FAIL (4/4 EXPECT matched, 1 unknown name, 3 out-of-scope file writes refused)
009: BLOCKED / FAIL (4/4 EXPECT matched, 15 "unknown" names)
010: BLOCKED / FAIL (3/3 EXPECT matched, 1 unknown name, out-of-scope file writes refused)

## What the mechanical verdicts actually mean (read every reply in full - do not trust the FAIL label alone)
Every single content verdict above is a **false alarm about my own task packing, not
a model quality problem**. Read verbatim, all four replies were textually correct,
followed every instruction, invented nothing, and matched every EXPECT line:

- 007's proposed content was byte-perfect (all 6 corrected codes, the
  "multiples of 10" note, the unverified-heartbeat note) - the only issue is
  it output a whole-file FILE block for a file it was only shown lines 73-152
  of, so the mechanical diff shows -113/+10 (looks destructive). That is a
  spec-writing mistake on my side (should have asked for a text delta, not a
  FILE block, given the narrow SCOPE, or scoped the whole file - it's only
  ~200 lines).
- 008 and 010: same root cause for BUGS.md (I scoped only ~20 of its 157
  lines). The 5 new bug rows and 5 item-doc stubs it drafted are all
  individually correct - right IDs, right severities, right citations, right
  format (010 dropped the trailing "| - |" receipt cell, a real small
  formatting slip, the only actual defect found). The "unknown file name:
  CORE_READINESS_PLAN.md" flag fired because that file wasn't literally in
  SCOPE even though the task text told the worker its exact name to cite -
  the verifier can't distinguish "cites a real file by name" from "invents a
  file name," which is by design (T049's stated purpose) but produces a
  false positive here.
- 009: 0 proposals, STATUS: DONE, and the reply text is the two new
  FILE_INDEX table sections verbatim-correct, including "?" for every Size
  cell exactly as instructed (told explicitly not to invent sizes - it
  didn't). All 15 "unknown file name" flags are the filenames I dictated to
  it as data (execution/backtest module names) for the Purpose column, not
  claims of having read those files. Same verifier limitation as above.

## What I did about it
Read every raw reply.json/diff, hand-verified nothing was invented against
CORE_READINESS_PLAN.md section 2 and the actual repo, then built four proper
non-destructive .new files myself from the worker's verified-good content
(never applying its raw FILE-block proposals, which would have gutted BUGS.md
and deribit_api_research.md to a handful of lines):
- research/BUGS.md.new (+5 rows: B072-B076, receipt cells normalized)
- items/B072..B076_*.md.new (5 new stub docs)
- research/_archive/loose_2026-10/deribit_api_research.md.new (error table + heartbeat note)
- system/03_FILE_INDEX.md.new (two new sections inserted after MTS/RUNTIME/)
All await your review/commit per the four-step proof, same as B1's files.

## Scorecard
- Content accuracy: 4/4 tasks, zero invented facts, zero wrong citations,
  100% EXPECT-line coverage.
- Instruction-following: high - it correctly inferred and reused the
  items/ doc house style (header block, "Opened: DATE by session ...")
  from the one example file I gave it in scope, unprompted.
- Format fidelity: 1 minor slip across 4 tasks (010 missing a trailing
  "| - |" receipt cell on 2 of 5 total rows) - fixed by hand.
- Failure mode: 100% of the "FAIL/BLOCKED" verdicts were packing mistakes
  (narrow SCOPE + FILE-block output on a partially-scoped file) or verifier
  false positives (dictated filenames flagged as invented) - not model
  mistakes. Once you account for that, the worker's actual hit rate on these
  four tasks is 4/4 clean.

## Recommendation on Phase 5 (compiled_engine.md rule-tagging)
Cautiously yes, with one packing-protocol fix first: never ask the worker
for a FILE-block replacement of a file it's only shown a slice of. For
compiled_engine.md (critical, four-step proof, large file) the existing
task 005/006 pattern already does this correctly - it asks for a single
proposed EDIT LINE plus a separate index row, never a whole-file FILE block.
Keep using that pattern (not the one I used for 007/008/010) for any future
compiled_engine.md work, and the demonstrated content accuracy here supports
moving forward with slice 2 of the rule-tagging work.
