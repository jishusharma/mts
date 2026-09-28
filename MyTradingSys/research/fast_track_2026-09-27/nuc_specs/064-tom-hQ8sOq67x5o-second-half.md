TASK: Extract every concrete Tom Vorwald trading rule from the second half of transcript hQ8sOq67x5o (approximately words 1100-2214 of 2214). This is part (b) of a split task; part (a) covers the first half.
SCOPE: raw_transcripts_canonical/hQ8sOq67x5o_raw.txt
OUTPUT: One FILE block, full content: extracts/processed/tom/new_selected_10/extract_hQ8sOq67x5o_second_half.md. Nothing else.
OUTPUT_TOKENS: 6000
EXPECT: Source GPS: hQ8sOq67x5o
EXPECT: ## Rules
EXPECT: ### R

Context: Task 054 was cut off at 4000 output tokens. This is part (b): extract rules only from the second half of the hQ8sOq67x5o transcript (approximately words 1100-2214). Part (a) covers the first half.

Only rules that are concrete and testable: zones (volume profile POC/VAH/VAL, business zones, VWAP bands), order-flow proof (CVD, delta, absorption), PBD logic, entry triggers, stops, targets, trade management, session timing, risk rules. Skip motivation, marketing, sponsor talk and personal stories. Format: a "# Tom extract hQ8sOq67x5o (second half)" title, then "## Rules", then one block per rule:
### R<n>: <short rule name>
- Rule: <one sentence, plain, testable>
- Topic: <zones | proof | entry | stop | target | management | session | risk | other>
> "<verbatim quote from the transcript, max 40 words, copied exactly>"
**Source GPS: hQ8sOq67x5o | <BEGIN|MIDDLE|END>**
Never invent a rule or quote. If two statements conflict, record both. End with "## Unclear" listing statements that sound like rules but are too vague to test.

Answer from the SOURCE blocks only. Start with the five lines TASK, STATUS, SUMMARY, FINDINGS, NEXT.
