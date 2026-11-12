# REVIEW tf-x4 Tom session window and profile anchor (reviewer: Haiku, 2026-11-13)

Gate: `python scripts/dev/verify_extract_quotes.py ANSWERS.md` exit 0, 26 quotes OK, PASS: 0 problems.
Blocks checked: Q2, Q7, Q8 (all 3 blocks; quotes read in transcript context).

| block | quote supports claim Y/N | note |
|---|---|---|
| Q2 | Y, with an inference to label | "each of these areas shows me one week" and "70% of the total liquidity for this week" support the weekly frame. The 30/70 sentence sits in the same passage, followed by "This is for example a unit of 1 day", so the frame is weekly then daily. "The stated frame is the weekly profile" is an inference; say so. VxN5 quotes support "over 70%" sideways; no "30% trend" quote is in the block. |
| Q7 | Y for Tom's lines; N for the guest numbers (no quote) | "9 to 12 is a trading time ..." (5Ljf, Tom's reply) Y. "midday period is often 2:00, 3:00, 1:00 p.m." (wPMi) Y. Gap quotes (YopZ, BB3c) Y. Guest hours are real in 5Ljf ("I trade from 6:00 a.m."; "1530 to,600, maybe until 1615"; "I exit at 14:30 at the very latest") but the verdict gives them with no quote. Katherina's own "9 to 12" was not checked. |
| Q8 | Y for most; one sentence too broad | "each of these areas shows me one week", "only show you the period where the so-called cash session is", "value area high of the current day" (wPMi) and "I am a counter trader" Y. "6E ... future product" (5Ljf, Tom's reply) Y. "composite ... for fair value": "fair value" is not in the quote. "Bitcoin appears in these files only as a news/sentiment counter-indicator": in 5Ljf a guest says he trades Bitcoin; the statement holds for Tom's lines only. |

NOT_SEEN grep (keyword pairs, 8 ids):
- Q7 24/7 hours / weekend / overnight / crypto with a clock: 0 hits. Consistent.
- Q7 Asia / Europe / US session with a clock: 2 hits, both in the GUEST (5Ljf) "I trade from 6:00 a.m. ... Asian session". Labelled GUEST, so Tom NOT_SEEN holds.
- Q7 opening range / initial balance minutes: 0 hits. Consistent.
- Q8 forex / crypto / bitcoin near "profile": 1 hit, a guest's "move away from the forex market". Labelled as the forex guest's advice. Consistent.

SOURCED numbers not in a quote: "Christian 6:00 gold", "Frank S&P 15:30 to 16:00/16:15", "Katherina out by 14:30" (all GUEST, so not SOURCED, but unquoted).
GUEST check: Christian, Hines, Frank, Katherina labelled GUEST in the header: correct per 5Ljf. The 9 to 12 line is Tom's.

Verdict: FIX

Exact lines to fix:
1. Q7 verdict: add GUEST-labelled quotes for the guest hours, from 5Ljfwvtktek: "I trade from 6:00 a.m." (Christian), "1530 to,600, maybe until 1615" (Frank), "I exit at 14:30 at the very latest" (Katherina, confirm the speaker before citing). Or delete the three hour figures.
2. Q8 verdict: replace "Bitcoin appears in these files only as a news/sentiment counter-indicator, not profiled." with "In Tom's lines Bitcoin appears only as a news/sentiment counter-indicator (sQ_biBKhPVU), not profiled; a guest in 5Ljfwvtktek says he trades it."
3. Q8 verdict: replace "a composite from the last major high to the last major low for fair value" with "a composite from the last major high to the last major low".

Fixes applied 2026-11-13 by extractor; re-check by tf-r1.
