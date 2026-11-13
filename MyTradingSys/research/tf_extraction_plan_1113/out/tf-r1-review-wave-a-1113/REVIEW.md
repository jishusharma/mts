# REVIEW tf-r1: wave A re-check (tf-x1..tf-x5) after the extractor's fixes

Reviewer: Claude (login B, JIS-NUC), 2026-11-13. Different model from the extractor. Each card's own REVIEW.md lists the FIX lines; this file checks they landed (a7022539d, 7d3f5fb29).

## Gate
`python scripts/dev/verify_extract_quotes.py <ANSWERS.md>` re-run on trunk 26c16d526: exit 0 on all five.

## Fix lines applied
| card | what was checked (old text gone or new text present in ANSWERS.md) | applied |
|---|---|---|
| tf-x1 | Q4 Deep Charts study wording removed; Q10 'usual range' and 'Home-run 1:19' removed; table '1:19 planned target'; Q6 'Partials at the sensitive level' removed; Q5 '10 contracts' removed; Q9 row 'big-trade filter (NQ)' renamed | 6 of 6 |
| tf-x2 | Q5 short-stop clause removed, table row NOT_SEEN (contradicted); Q6 'moved past entry' removed; Q12 'R 2.5-3.5' removed, R 1.1 quote added, 'hypothetical 50% at R 1.8'; speaker header rewritten | 7 of 7 |
| tf-x3 | Q8 '30-minute TPO block' removed; Q3 '325 level' quote deleted | 2 of 2 |
| tf-x4 | Q7 guest hours quoted with GUEST labels; Q8 Bitcoin sentence and 'for fair value' rewritten | 3 of 3 |
| tf-x5 | Q9 325 (S&P 500 book) and 676 (ES) split in verdict and table; crude-oil 100 block reworded; Q11 NASDAQ/Nvidia quote deleted and 'ten files' wording fixed; Q4 'gut feel' removed | 6 of 6 |

Total 24 of 24 fix lines applied; 21 by exact-string check, 3 either/or fixes by reading the block.

## Spot check: one fixed block re-read against its transcript
tf-x2 Q12 fix 5 kept the breakout ratio by adding its quote rather than deleting the number:

> "Typical breakout trading riskreward ratio of 1.1."
**Source GPS: UrZ4vpHJ97g | MIDDLE**

## Verdict
**PASS**: wave A answers tf-x1..tf-x5 are ready for the answer ledger (tf-s1-answer-ledger-1113). No open FIX line.
