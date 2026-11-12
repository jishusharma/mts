# REVIEW tf-x5 Tom speed and proof (reviewer: Haiku, 2026-11-13)

Gate: `python scripts/dev/verify_extract_quotes.py ANSWERS.md` exit 0, 35 quotes OK, PASS: 0 problems.
Blocks checked: Q4, Q9, Q11 (all 3 blocks; quotes read in transcript context).

| block | quote supports claim Y/N | note |
|---|---|---|
| Q4 | Y for the quotes; N for one clause | "I need market speed ..." (G0Ci), "What is fast execution and what isn't?" (G0Ci), "relative to the respective product" (vl01), "high speeds / low speeds" (vl01) support the block. "not left to gut feel" is not in any quote; delete it. |
| Q9 | N for the ES example | "Those are 325 contracts" (vl01 BEGIN) is said of the S&P 500 book ("a huge order on the selling side ... of the S&P 500. ... Those are 325 contracts"). The verdict says "ES big orders of 325 and 676". 676 is ES (usho: "Let's focus here on the ES ... an order here with 676 contracts") Y. "a 100 block in crude oil as large" (vl01): the 100 block sentence follows a crude oil comparison ("much, much smaller numbers"), so it is not clearly a crude block; say "in a crude oil comparison". Cumulative delta crude +500 vs Euro stocks (y67l) Y. |
| Q11 | N for one quote; the count in the verdict is wrong | "I have prepared a nice combination with NASDAQ and also with Nvidia" (OUM9) supports no sentence in the block: remove it. "not found in these ten files": the card has eleven ids (nine Tom, two guest). Correct for these files, but "many, many parameters" IS in zQTbdEweG3c (Tom, card tf-x2): "you need many, many parameters that speak in your favor ... First ... idea ... Second ... proof ..." It has no count, so NOT_SEEN for N holds, but the verdict should say where the phrase is. "four-point list ... step 6 (order books)" (3o1V "point 4", "skipped 6") Y. |

NOT_SEEN grep (keyword pairs, 9 Tom ids):
- Q4 speed + seconds / per second / bars: 1 hit (vl01 "a certain speed", no unit). Consistent.
- Q9 "zero" + ticks / percent: 0 hits. Consistent.
- Q9 big / block + contracts: usho gives "blocks of 74 contracts or 48 contracts" on the sell-side book and says they "can be much larger during the main trading hours" of the S&P. These are typical sizes in his words, not a cutoff. Consistent with NOT_SEEN for a universal size, but add the 74/48 example to the table.
- Q11 proof / parameters / conditions with a count: 0 co-occurrence windows in these ids. The count is only in zQTb (no number). Consistent.

SOURCED numbers not in a quote: none beyond the 325/676 mislabel and the crude 100 block (both above).
GUEST check: 4P5WAxyPCis and rFPCtOcfUMI are labelled GUEST: correct. The one "Serge" mention in usho is Tom naming a colleague, not a speaker. Tom ids show no guest speaking.

Verdict: FIX

Exact lines to fix:
1. Q9 verdict: replace "examples he gives are ES big orders of 325 and 676 contracts" with "examples he gives are an S&P 500 book order of 325 contracts and an ES order of 676 contracts".
2. Q9 table row "ES big order": replace "325 and 676 contracts shown as big" with "S&P 500 325; ES 676 (shown as big orders)".
3. Q9 verdict: replace "a 100 block in crude oil as large" with "a 100 block as a large trader's ambition, in a crude oil comparison".
4. Q11 block: delete the quote "I have prepared a nice combination with NASDAQ and also with Nvidia." (OUM9LYwL8eA).
5. Q11 verdict: replace "the phrase \"many, many parameters\" was not found in these ten files" with "the phrase \"many, many parameters\" is not in these nine Tom files; it appears in zQTbdEweG3c (no count)".
6. Q4 verdict: delete "and not left to gut feel".
