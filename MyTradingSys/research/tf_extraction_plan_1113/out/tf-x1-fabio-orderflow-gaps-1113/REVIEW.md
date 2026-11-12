# REVIEW tf-x1 Fabio order-flow gaps (reviewer: Haiku, 2026-11-13)

Gate: `python scripts/dev/verify_extract_quotes.py ANSWERS.md` exit 0, 64 quotes OK, PASS: 0 problems.
Blocks checked: Q4, Q5, Q6, Q7, Q10 (5 of 6 blocks, quotes read in transcript context); Q9 checked for the big-trade line.

| block | quote supports claim Y/N | note |
|---|---|---|
| Q4 | Y for the quotes; N for the first sentence | Quotes support "speed of tape" as a hold/fakeout check. "a separate Deep Charts study ... (bubbles that are green or red ...)": "bubbles" occurs 0 times in Is1HvdfQm5c; "speed of tape" is read off aggression candles (ASR, 2:06:37 "this is not the delta it's the speed of tape"). "Separate study" is not stated. |
| Q5 | Y | "super small stop", "below the aggression of the buyers", and the "squeeze" quote support the placement rule. The "$3,150 (NQ short, 10 contracts)" line: "10 contracts" is not in the quoted 8CWKfoSJu3c sentence (it is elsewhere in that video: "loaded with 10 contracts"); "NQ" is not said, he says NASDAQ. |
| Q6 | Y for the quoted rules; N for the partials sentence | 0jM5 "went to break even immediately" and Pz8f "3 minutes after" check out. "Partials at the sensitive level" has no quote in this block. Is1HvdfQm5c 1:07:34-1:08:06 has a partial example ("take another one to one point five ... you close seven point five") that is not cited. |
| Q7 | Y | NY-only line (Pz8f 29:00), London quotes (06R, fZlN, Is1H ASR), and "closed the session around four" (0jM5) are in context. CONTRADICTION verdict is fair. |
| Q10 | N for two sentences | "1:2.5 to 1:5 as the usual range": no quote says usual or typical; "1 to 2.5" appears only in cUTs as a single example. "Home-run runs reached 1:19 with a trailed stop": 8CWKfoSJu3c says "Final target is 27,600 for 1 to 19 risk-to-reward. This is not common." That is a planned target; the transcript does not say it was reached. |

NOT_SEEN grep (keyword pairs, all 8 ids):
- Q4 speed + second/minute/threshold: 0 hits.
- Q5 stop + ticks/bps/%: only a 3-tick slippage (Pz8f) and a 2-tick overshoot; neither is a buffer rule. Consistent.
- Q6 break-even + ticks/points: Is1HvdfQm5c 1:07:44 "one point five ... seven point five" is a partial, not a break-even trigger. NOT_SEEN for the trigger holds; the partial example should be cited (see table).
- Q7 clock / lunch / overnight: 0 real hits (regex matched only [m:ss] markers). Consistent.
- Q9 "zero" + ticks/percent: 1 hit (o-w5 "zero results", no number). Consistent.
- Q10 "points short of level": 0 hits. Consistent.

SOURCED numbers not in a quote: 1:19 and 1:2.5 (Q10), 10 contracts (Q5, in video but not in the quote), "NQ" for the 60 big-trade filter (Q9 table; the quote is ASR and does not name the product).
GUEST check: no second speaker in the 8 ids (grep for Hoffmann, Nill, Cimi, Serge, Patrick: 0 hits as speaker). Speaker label Fabio is fine. Note the ASR in Is1HvdfQm5c ("fate setup" = fade, "Presection"); quotes are labelled ASR, which is right.

Verdict: FIX

Exact lines to fix:
1. Q4 verdict: replace "a separate Deep Charts study that he reads by eye (bubbles that are green or red, loading, dry, shy, \"really high\")" with "read by eye off the tape and aggression candles (\"loading\", \"dry\", \"shy\", \"really high\"); no separate study or bubble display is stated."
2. Q10 verdict: replace "1:2.5 to 1:5 as the usual range" with "1:2.5 to 1:5 as the range he quotes (no usual or typical wording)", and replace "Home-run runs reached 1:19 with a trailed stop" with "a 1:19 target was set on one trade (\"Final target is 27,600 for 1 to 19\", 8CWKfoSJu3c [3:31]); he does not say it was reached".
3. Q10 table row "target multiple": replace "1:19 maximum seen" with "1:19 planned target (8CWKfoSJu3c, not stated as reached)".
4. Q6 verdict: either add the Is1HvdfQm5c 1:07:34 quote (partial at 1.5) to the block or delete "Partials at the sensitive level".
5. Q5 verdict: delete "10 contracts" unless a quote from 8CWKfoSJu3c with "10 contracts" is added; replace "NQ" with "NASDAQ".
6. Q9 table row "big-trade filter (NQ)": change to "big-trade filter (product not named in the quote; ASR)".

Fixes applied 2026-11-13 by extractor; re-check by tf-r1.
