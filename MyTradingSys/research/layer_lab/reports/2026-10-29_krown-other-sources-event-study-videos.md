# Krown other sources: event study videos

**Verdict: BLOCKED**

The existing four V2 extracts do not pass the required quote gate in this workspace, and the call ledger cannot be validated against the permitted DEV bars. The requested completion criteria are therefore unmet.

## What I checked

- Source inventory: `MyTradingSys/options/research/KROWN_FREE_VS_PAID.md:37-49` lists the three overbought weekly videos (`V0gjxlaW2Qk`, `sCLLZKY_r8g`, `ZNvLh3JyOco`) and their dates; `:41` identifies the CBP item `OggsnATGbOg` as the September 25 spot event study.
- Method and requirement: `MyTradingSys/research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md`; `MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:10-14` requires item 2 to be a minute-timestamped own-trade ledger split into design/check sets.
- Existing extracts: `extracts/extract_OggsnATGbOg.md`, `extracts/extract_V0gjxlaW2Qk.md`, `extracts/extract_sCLLZKY_r8g.md`, `extracts/extract_ZNvLh3JyOco.md`.
- Existing ledger: `MyTradingSys/research/krown_ta101_2026-10-13/CALL_LEDGER.csv` has 7 rows, dated 2026-09-25 through 2026-10-08. Its date/split column labels two rows `check`, but all rows are post-DEV cutoff.
- Verification command, run separately on each of the four extracts:
  `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_<videoid>.md`

## Findings

| Severity | Evidence | Finding |
|---|---|---|
| HIGH | Quote gate output: `extract_OggsnATGbOg.md` = `FAIL: 3 problem(s)`; `extract_V0gjxlaW2Qk.md` = `FAIL: 3 problem(s)`; `extract_sCLLZKY_r8g.md` = `FAIL: 2 problem(s)`; `extract_ZNvLh3JyOco.md` = `FAIL: 2 problem(s)`. Each failure is `NO-TRANSCRIPT`; the verifier resolves quoted transcripts from `raw_transcripts_canonical/<video_id>_raw.txt` (`scripts/dev/verify_extract_quotes.py:3-5,22-25`). | The canonical transcript inputs for these four extracts are absent in the workspace, so the quotes and GPS thirds cannot be verified. A prior report at `2026-10-30_krown-other-sources-event-study-videos.md` says these passed, but that claim is not reproducible here. |
| HIGH | `CALL_LEDGER.csv` rows 1-7; PRE_REG item 2 at `PRE_REG_KROWN.md:10-14`; data access rule in the task card. | Every ledger date is 2026-09-25..2026-10-08, later than the only allowed DEV bars (open before 2024-07-01). No post-cutoff bars were read. These calls cannot be validated against allowed DEV klines, and the current `design` / `check` labels do not establish a by-date split of eligible historical calls. |
| MED | `CALL_LEDGER.csv:2-8` (header plus seven call rows); `PRE_REG_KROWN.md:10-14`. | The ledger rows are summarized calls, not minute-timestamped entries sourced from video frames. The required item 2 evidence is not established. |

## Transcript acquisition status

No `yt-dlp` fetch was attempted. The task directs Gemini search grounding as the default; `python scripts/dev/gemini_queue.py status` showed no run for this card, and its documented `run` path creates a worktree and invokes the Antigravity CLI. That path was not used because the runner has already claimed this card and the user prohibited git-related/ship actions in this sandbox. No missing video ids were added beyond the four known IDs above.

## Required to unblock

Provide or stage the four canonical raw transcripts under `raw_transcripts_canonical/`, rerun the quote gate, and resolve item 2 using only eligible DEV call examples with timestamped source evidence and a date-based design/check split. Until then, do not use these ledger outcomes as ground truth.

No follow-up cards were created. The card was not marked done because the task explicitly says to leave it open when blocked.
