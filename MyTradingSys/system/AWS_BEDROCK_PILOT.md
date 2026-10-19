# AWS Bedrock pilot: use the expiring credits for text jobs (operator 2026-10-19)

Why: the AWS free plan ends 2026-10-25 ($96.14 credits, unused credit is lost). Bedrock Playground (us-east-1, Test -> Playground -> Chat,
Claude models listed 2026-10-19) is a plain chat box: no setup, no keys, nothing moves to AWS. Cost to the operator: zero.
Limits: it cannot browse or fetch YouTube, cannot read repo files; everything it works on is pasted in by hand.

## Rules (Session_Planner scoped this; do not widen)
- PUBLIC transcripts and public extracts only. Never paste runtime, order, account, `.secrets/`, `.env` or live-tree data (repo is public).
- No AWS key, no IAM user, no code, no Billing change. Stop on 2026-10-25 (or when credits hit $0): close the tab, nothing to clean up.
- Model: **Claude Haiku 5.5** for jobs 1-9 (cheap, text-only); **Claude Opus 5.5** only for jobs A1-A2. If the picker shows access denied, stop and report that line.
- Output is a DRAFT. A Claude session runs `python scripts/dev/verify_extract_quotes.py <file>` on every extract; any quote not verbatim in
  `raw_transcripts_canonical/<ID>_raw.txt` is deleted, never repaired. Nothing from Bedrock enters a layer, rule or number without that check.
- Save each answer as `extracts/bedrock_out/<ID>_bedrock.md` (new folder, one file per job), then tell the Haiku helper `done <ID>`.

## Helper (open a Claude session on Haiku next to you, paste this once)
```
You are the Bedrock prompt feeder. Read MyTradingSys/system/AWS_BEDROCK_PILOT.md and follow it. Give me ONE job at a time, in order J1..J9, then A1, A2.
For each job print: (1) the transcript path to open and paste after the prompt, (2) the exact prompt block to paste into the Bedrock Playground (after the SYSTEM block).
Wait for me to say "done <ID>" before the next job. When I say "done <ID>", run verify_extract_quotes.py on extracts/bedrock_out/<ID>_bedrock.md and report the count of bad quotes in one line.
Never read .secrets or .env. Keep replies short.
```

## SYSTEM block (paste once per chat, Playground "System prompt" box)
```
You extract trading rules from a YouTube transcript. Zero fabrication. Every claim must carry a verbatim quote copied character for character from the transcript.
If the transcript does not say it, write "NOT STATED". Never add numbers, thresholds or rules the speaker did not say. Do not summarise from memory of other videos.
```

## Per-transcript prompt (J1..J9): paste this, then paste the transcript text under "TRANSCRIPT:"
```
Task: P-EXTRACT-001 style extraction of the transcript below.
Output exactly these sections in Markdown:
## EXTRACTION SUMMARY (video id, speaker as self-identified or "Not stated", topic, counts)
## KEY FINDINGS (max 8 numbered items, each one sentence)
## DETAILED CLAIMS WITH TIER TAGS
For each claim: a tier line `**T5 command | T4 recommendation | T3 calculation | T2 self-check | T1 example**`, then the quote as `> "<verbatim quote>"`,
then `**Source GPS: <VIDEO_ID> | <BEGIN|MIDDLE|END>**` (thirds of the transcript where the quote sits).
## NEGATIVE RULES (things the speaker says not to do, with quote + GPS)
## GAPS DOCUMENTED (things a trader would need to trade this that the speaker never states: exact entry trigger, stop, target, size, session, timeframe)
Quotes: copy exactly, 8 to 40 words, no editing, no joining of separated sentences. Prefer fewer, exact quotes over more, loose ones.
TRANSCRIPT:
```

| Job | Video ID | Transcript file to paste (extracts/pending_raw/tom/new_selected_10/) |
|---|---|---|
| J1 | WQ_OAdz-PJ8 | WQ_OAdz-PJ8_I_Tested_10_Trading_Strategies_Only_THIS_One_Actually_Works_for_Beginners.txt |
| J2 | 7BQPMJ39WpI | transcript_7BQPMJ39WpI.txt |
| J3 | 96iPFDpXEcU | transcript_96iPFDpXEcU.txt |
| J4 | HySZZSjMxF8 | transcript_HySZZSjMxF8.txt |
| J5 | aursfDVYzUk | transcript_aursfDVYzUk.txt |
| J6 | gWjHq5UMisY | transcript_gWjHq5UMisY.txt (no raw_transcripts_canonical copy yet: a Claude session stages it before verify) |
| J7 | hQ8sOq67x5o | transcript_hQ8sOq67x5o.txt |
| J8 | pgdmKLJ0hhA | transcript_pgdmKLJ0hhA.txt |
| J9 | zAwEX_tRUfE | zAwEX_tRUfE_My_Simple_1-Minute_Scalping_Strategy_for_10000Month.txt |

## Audit jobs (second model family, Opus 5.5)
A1: pick one existing extract from `extracts/fresh/` (start with `extract_-dMWA_bbm3o_fresh.md`) and its transcript `raw_transcripts_canonical/<ID>_raw.txt`.
```
Below are a transcript and an extraction of it. List every claim in the extraction that the transcript does not support, every quote that is not verbatim,
and every important rule in the transcript the extraction missed. Reply as three bullet lists, one line per item, each with the quote or the line number. No praise, no summary.
TRANSCRIPT:
<paste>
EXTRACTION:
<paste>
```
A2: same prompt on a second extract (`extract_1xBWnyr1qe4_fresh.md`). Save as `extracts/bedrock_out/<ID>_audit.md`; a Claude session checks each listed miss against the transcript
before any extract is edited (the audit is a lead, not a verdict).

## After the jobs
A Claude session (Sonnet) compares each `_bedrock.md` with any existing extract for the same video, runs the quote verifier, and records the share of verbatim quotes
(OURS, untuned: a model's extracts count as usable only if at least 95% of its quotes verify; judgement, not sourced) in `MyTradingSys/research/STATUS.md` via the usual ship. Nothing else changes.
