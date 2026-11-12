# Gemini collect 1112: three videos, state 2026-11-12T09:30Z

All three NUC Gemini jobs (gq1112, branches gemini-q/<card-id>) FINISHED. Each wrote NOT_IN_DATA.md: 0 quotes PASS. Gemini via agy has no video or caption access, so nothing was extracted; nothing invented (verify_extract_quotes.py not run: no EXTRACT.md exists).

CORRECTION: the card text said captions unlock 2026-11-13T02:53Z. Guard status on every host now says `BLOCKED until 2026-11-13T13:58:11+00:00` (level 3 of 3, ip 49.37.73.158). Retry after 2026-11-13T13:58Z, one video first, with `fetch_captions_timed.py` (real captions), never ASR or evasion. Gemini-only quotes: none exist, so no RE-CHECK list.

| Video | Title (card) | Job state | Quotes PASS | Next |
|---|---|---|---|---|
| j-JVi02_C88 | Bitcoin Falls Below the 50W Moving Average (LongShort) | finished, blocked | 0 | retry fetch after 2026-11-13T13:58Z |
| BB3c8visnkI | Tom Vorwald, How to Use Volume Profile Like a Pro | finished, blocked | 0 | same |
| e83njGZFrPw | Tom Vorwald, LIVE TRADING: DAX Short Using My Correlation Trick (2026-10-23) | finished, blocked | 0 | same |

## Four questions (operator), per video
Teaching content cannot be stated until captions exist; only what the titles and our own data support is written.

| Video | Teaches | We already do | We do NOT do | Should do / learn |
|---|---|---|---|---|
| j-JVi02_C88 | unknown (title: BTC closed under 50W MA) | title claim tested on own weekly data: `research/btc_50w_ma_j-JVi02_1112/CHECK.md`, 7 first breaks, break is a phase marker not a signal; scenario S025 logged | no 50W MA reading in BIBLE.md yet | extract after unlock; append the dated cycle-clock reading; score S025 at 2026-12-01 and 2027-01-26 |
| BB3c8visnkI | unknown (title: volume profile) | Tom volume-profile layers (`tom` family in LAYERS.md) | unknown until extract | extract, then compare with Tom layer rules |
| e83njGZFrPw | unknown (title: DAX short via correlation) | none known for a correlation trick | unknown until extract | extract; check whether the correlation is testable on crypto data |

## NUC cleanup (DECISION OURS)
- Stash on F:\MTS\mts-gemini `stash@{0}` (111523344b1c, "pre-queue-1112"): content = only auto-generated "Open cards" lines of LAYERS.md (one card line removed, one added) that trunk regenerates; trunk is newer. DROPPED (recoverable by sha until gc). `stash@{1}` (WIP on gemini-gap-fix, 2026-10-19) is older and not ours: left in place, no diff vs its base.
- One-shot task gq1112 and F:\MTS\gq\queue1112.ps1 deleted (our own objects). Branch worktrees under F:\MTS\gq\<card-id> left for the operator-side hygiene sweep.
