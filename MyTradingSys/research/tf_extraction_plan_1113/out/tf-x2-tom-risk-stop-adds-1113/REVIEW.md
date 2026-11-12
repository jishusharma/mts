# REVIEW tf-x2 Tom risk, stop, adds, target (reviewer: Haiku, 2026-11-13)

Gate: `python scripts/dev/verify_extract_quotes.py ANSWERS.md` exit 0, 69 quotes OK, PASS: 0 problems.
Blocks checked: Q5, Q6, Q10, Q12 (all 4 blocks; quotes read in transcript context).

| block | quote supports claim Y/N | note |
|---|---|---|
| Q5 | N for the short-side sentence; Y for the long side | "stop ... above the last high for a short": the card's own quote (yRvMW6lgN1o) says "It doesn't belong above the high. Because the probability of a strong acceleration above the high is always high." That is the opposite of the sentence. The table note "not just above the high where size sits" is not in the quote. Long side (below the last low, kXhI / QClP / UrZ4) is supported. Two-tick overshoot (kXhI): supported. 12-tick and 35-tick numbers are one trade or one example each, labelled as examples: fine. |
| Q6 | Y for the rules; N for "past entry" | Add, partial and trail quotes check out. "A stop moved past entry means 'I won't lose any more money'": T6hD says "Once it moved to $650, I won't lose any more money." The entry price is not in the quote, so "past entry" is not shown. UOBg quote "you'd have made much more money if you'd taken your profits" supports "takes the planned target" (he gives 60 of 100 trades as target hits). |
| Q10 | Y | "must never ever delete this predefined target" (UrZ4) and "a few ticks off" (4MoN) support the block. "Predefined before entry" is a fair reading of "you've decided in advance". |
| Q12 | Y for most; 3 numbers without a quote | 0.5% (UrZ4 "how I arrived at the figure of 0.5%") Y. 0.7% swing with 12.9% drawdown Y (quote in gate). EV 0.414R at 35% and 3.04 Y (QClP). "R 2.5-3.5": UrZ4 has "2.5 to 1" only; 3.5 is not quoted. "breakout ... R about 1.1": the words "riskreward ratio of 1.1" are in UrZ4 but not in any quote in this block. "day trading 50% at R 1.8": the quote is "I'll claim we have a win rate of 50%", a hypothetical; the verdict should say so. |

NOT_SEEN grep (keyword pairs, 14 ids):
- Q5 stop + ticks/bps/%: 5 windows, all specific trades (40 ticks, 12 ticks, 35 ticks, 2-tick overshoot). No buffer rule. Consistent.
- Q6 partial fraction (half/third/%): 0 hits. Consistent.
- Q6 break-even trigger: UrZ4 "break even point ... 12 full points ... every day" is about the business, not a stop trigger. Consistent.
- Q12 daily loss limit: 0 hits. Consistent.
- Q12 yearly return %: 0 hits. Consistent.

SOURCED numbers not in a quote: R 2.5-3.5 (3.5), R about 1.1 (block has no quote).
GUEST check: no guest speaks in the 14 ids. Patrick and Fabio appear only as names he mentions. But the intro names the host differently across files (hQ8sOq67x5o, WSCIURybK3U, dh-ysRR8f-M, T6hDJcHrVBM and others use other names; likely ASR), so "Tom Vorwald in every file" is not verified by this review. Label as Tom with a note, or check the voice.

Verdict: FIX

Exact lines to fix:
1. Q5 verdict: delete "above the last high for a short" from "(below the last low for a long, above the last high for a short, outside the area where the idea is no longer valid)". Replace with "for a short, the cited quote says the stop 'doesn't belong above the high' (yRvMW6lgN1o); the short placement is NOT_SEEN until a quote supports it."
2. Q5 table row "Stop placement (short)": change "SOURCED" to "NOT_SEEN (contradicted by yRvMW6lgN1o; see note)".
3. Q6 verdict: replace "A stop moved past entry means \"I won't lose any more money\"" with "A stop moved to $650 means \"I won't lose any more money\" (entry price not stated in the quote)".
4. Q12 verdict: replace "0.7% (swing, R 2.5-3.5)" with "0.7% (swing; R 2.5 to 1 in the quote)".
5. Q12 block: add the quote "Typical breakout trading riskreward ratio of 1.1." (UrZ4vpHJ97g) or delete "R about 1.1".
6. Q12 verdict: replace "day trading 50% at R 1.8" with "a hypothetical 50% at R 1.8 (\"I'll claim we have a win rate of 50%\")".
7. Header line "Speaker: Tom Vorwald (channel Tom Vorwald EN) in every file": replace with "Speaker: Tom in every file (intro names differ across files, ASR; same-voice not checked)".

Fixes applied 2026-11-13 by extractor; re-check by tf-r1.
