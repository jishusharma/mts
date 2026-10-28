# GPT cross-vendor review: Gemini Tom extracts J1-J9

Date: 2026-10-24. Card: `yt-gpt-review-tom-extracts`. Task: `gx2-review-tom-extracts`.

Verdict: **2 APPROVE, 7 FIX**. All nine verifier runs pass: **107/107 quote blocks OK**, zero reported problems. **45/45 randomly sampled detailed claims match the supplied transcript wording and immediate context**. The independent caption-body check finds **105/107 matches**: two quotes occur only in description metadata. Nine GPS tags also differ when measured against caption bodies rather than wrapped canonical text. Six finding groups remain: three HIGH, three LOW; zero CRITICAL. Quote fidelity does not establish summary fidelity or trading validity.

## Scope and method

Reviewed every `extracts/gemini_out/*_gemini.md` and all nine corresponding files in `extracts/pending_raw/tom/new_selected_10`. The two `_audit.md` files in gemini_out are outside the card's explicit producer-output glob. Read full transcript bodies, including prose outside sampled passages, and reviewed key findings and documented gaps. No transcript fetch, model call, formula implementation import, code/test/card edit, task close, commit, sync, or push was performed. The user overrides the card's commit/ship/close steps; those remain for the harvester.

Reproduce all machine checks and regenerate these reports from the repo root:

```powershell
python -X utf8 MyTradingSys/research/gpt_burn_2026-10-24/gx2-review-tom-extracts/audit.py
```

The script invokes `python scripts/dev/verify_extract_quotes.py <file>` separately for each extract, captures complete stdout/stderr, and counts parsed statuses before reporting totals. The verifier uses `raw_transcripts_canonical/<id>_raw.txt`; the separate local-token check finds 105 of 107 quotes in the card's pending_raw caption bodies after removing description/metadata. Matching ignores case/punctuation/whitespace, spoken fillers, and immediate repeated words; it does not invent synonyms. GPS pass/fail comes from the required verifier. No zero-quote pass is accepted.

Sampling is OURS: sort files by Python path order, then take five without replacement from the detailed-claims section using `random.Random("20261024:" + video_id).sample(claims, 5)` and display by source line. Negative rules receive the exhaustive quote check and full-context read, but are excluded from the five-claim sampling population. The tables below record each actual sample, its exact quote, and its raw source line; PASS describes source fidelity, not endorsement of a predictive claim. These AI-translated/auto-caption transcripts are the review boundary: no claim of independent speaker identity or video/chart validation. Several transcripts have their entire body on line 8; quoted text disambiguates those citations.

## Per-file verdicts and required verifier results

| File in extracts/gemini_out | Verdict | Detailed claims | All quotes | Verifier | Sample checks | Findings |
|---|---|---:|---:|---|---:|---|
| 7BQPMJ39WpI_gemini.md | FIX | 10 | 11 | PASS, exit 0, 0 problems | 5/5 PASS | F6 |
| 96iPFDpXEcU_gemini.md | FIX | 10 | 13 | PASS, exit 0, 0 problems | 5/5 PASS | F1 |
| aursfDVYzUk_gemini.md | APPROVE | 9 | 12 | PASS, exit 0, 0 problems | 5/5 PASS | None identified |
| gWjHq5UMisY_gemini.md | FIX | 9 | 12 | PASS, exit 0, 0 problems | 5/5 PASS | F2, F5, F6 |
| hQ8sOq67x5o_gemini.md | FIX | 9 | 11 | PASS, exit 0, 0 problems | 5/5 PASS | F6 |
| HySZZSjMxF8_gemini.md | FIX | 9 | 12 | PASS, exit 0, 0 problems | 5/5 PASS | F3, F4, F6 |
| pgdmKLJ0hhA_gemini.md | APPROVE | 10 | 12 | PASS, exit 0, 0 problems | 5/5 PASS | None identified |
| WQ_OAdz-PJ8_gemini.md | FIX | 10 | 12 | PASS, exit 0, 0 problems | 5/5 PASS | F6 |
| zAwEX_tRUfE_gemini.md | FIX | 10 | 12 | PASS, exit 0, 0 problems | 5/5 PASS | F6 |

## Findings

### F1 — HIGH: Volume acceptance is promoted to a breakaway signal without the subsequent upside breakout

Location: `extracts/gemini_out/96iPFDpXEcU_gemini.md:40` (also the shortened context at line 32).
The summary says substantial opening-gap volume "signals a breakaway gap rather than a gap fill."
The transcript first treats that volume as acceptance, then requires observing the direction of the next breakout.
Evidence: `extracts/pending_raw/tom/new_selected_10/transcript_96iPFDpXEcU.txt:8`:
"you just have to see in which direction is the market breaking out now" followed by
"And should it break out to the upside, then you know the following."
The extract's own claim at lines 63-64 preserves the first condition, but its key finding removes it.
Impact: a reader implementing only the summary could classify an accepted opening range as a confirmed continuation before a directional break.
Reproduce: rerun the audit command below; inspect the complete raw line 8 around "substantial" and "should it break out" against extract line 40.
Fix: describe volume as acceptance/P structure, retain the subsequent upside-break condition, and preserve the need to evaluate the fundamental story.

### F2 — LOW: 32% is slightly profitable, not the exact break-even rate

Location: `extracts/gemini_out/gWjHq5UMisY_gemini.md:16`.
The summary says a 2.2 reward/risk setup "breaks even theoretically without fees at a 32% win rate."
Evidence: `extracts/pending_raw/tom/new_selected_10/transcript_gWjHq5UMisY.txt:291` through line 300 says
"slightly in the black with a win rate of 32%" and "0.6R per trade" at 50%.
The extract quotes the former correctly at line 58; the error is the key-finding paraphrase.
Independent reproduction: gross_R from `MyTradingSys/backtest/layers/FORMULAS.md:468`, averaged by the arithmetic-mean definition at line 77:
32 wins at +11/5 R and 68 losses at -1 R per 100 trades give `(32*11/5-68)/100 = 0.024R`.
Solving the same weighted mean for zero gives `p=1/(1+11/5)=5/16=31.25%`.
At 50%, `(11/5-1)/2=0.6R`, consistent with the transcript and extract line 17.
Reproduce: rerun the audit command below; its independent arithmetic is printed in the report.
Fix: say "slightly profitable at 32%, before fees; exact break-even 31.25% under the stated fixed-payoff assumptions."

### F3 — HIGH: Waiting for exhaustion confirmation is changed into abandoning the setup

Location: `extracts/gemini_out/HySZZSjMxF8_gemini.md:17`.
The key finding says that if price fails to trade back through elevated volume, "the trade setup must be abandoned."
Evidence: `extracts/pending_raw/tom/new_selected_10/transcript_HySZZSjMxF8.txt:284` through line 286:
"But if it doesn't trade below this volume here, for example, then I have to wait."
The actual abandonment condition is a different structural price point, stated at raw lines 226-231.
The extract's negative rule at lines 74-75 correctly says to wait, making its summary internally contradictory.
Impact: the summary converts an unconfirmed but still pending setup into an invalidated one.
Reproduce: rerun the audit command; compare extract lines 17 and 74-75 with raw lines 226-231 and 281-286.
Fix: retain "wait for confirmation" and keep structural invalidation separate.

### F4 — LOW: A mirrored long-stop rule is presented as sourced despite only a short example

Location: `extracts/gemini_out/HySZZSjMxF8_gemini.md:15`.
The summary adds "or below swing lows for long trades" to the demonstrated short-stop placement.
Evidence: `extracts/pending_raw/tom/new_selected_10/transcript_HySZZSjMxF8.txt:252` through line 259:
"my next stop loss is positioned just above this level" and "where the market previously set that swing high."
The full transcript supplies no corresponding long-stop example or instruction. Its demonstrated setup remains short oriented.
Impact: a plausible symmetric inference is attributed to the speaker without the required inference label.
Reproduce: rerun the audit command; read the full 322-line raw transcript, particularly lines 215-259; the quoted stop example is short only.
Fix: restrict the finding to the short example, or label the long-side mirror OURS/inferred and requiring validation.

### F5 — HIGH: Two attributed negative-rule quotes come from the description, not the caption body

Location: `extracts/gemini_out/gWjHq5UMisY_gemini.md:70` and `:75`.
These quote blocks attribute "Most traders completely mix up these two concepts" and
"If you don't understand this one point, you won't make money long-term, even with the best setup."
to BEGIN transcript speech. Both complete quotes occur in the description at
`extracts/pending_raw/tom/new_selected_10/transcript_gWjHq5UMisY.txt:6`, before its body marker at line 7.
Neither complete quote occurs in its caption body, lines 8-370. Raw lines 14-15 contain the shorter
"Because many people mix up these concepts", which supports a related idea but not the submitted quote.
Impact: description copy is presented as verified spoken evidence. The quoted marketing claim at extract line 75 is unsupported as speech in the supplied transcript.
Reproduce: rerun the audit command. It strips metadata through the pending transcript's `# ---` marker before independently matching quotes:
gWjHq5UMisY has 10/12 body matches; all other files match every quote. The two missing body quotes match the header description.
Why the required verifier misses this: `raw_transcripts_canonical/gWjHq5UMisY_raw.txt:6` is an outer `# ---`, followed by a nested metadata header whose description is line 12.
`scripts/dev/verify_extract_quotes.py:43` removes only the first header, leaving the nested description in its search body.
Fix: replace these blocks with actual caption-body quotations or explicitly label them description metadata, without a spoken Source GPS.

### F6 — LOW: Nine Source GPS tags drift when located in the requested caption bodies

Locations and reproduction numbers are listed below. The quoted words are present, but their tagged thirds describe the canonical wrapper rather than the caption bodies requested by the card. The required verifier passes every tag against its own input representation. To reproduce the mismatch, rerun the audit script: it removes pending_raw metadata through `# ---`, normalizes the actual caption text, and classifies the first quote occurrence using `min(2, 3*offset//body_length)`, the verifier's own thirds convention. Offsets and lengths below are normalized characters, not timestamps. Impact: a reader following BEGIN/MIDDLE/END within the supplied transcript is directed to the wrong third. Fix: normalize to the caption body consistently and re-tag, or explicitly document canonical-wrapper coordinates; do not silently treat the two coordinate systems as interchangeable.

| Extract quote line (GPS is next line) | Raw source line | Tagged | Caption-body third | Offset / length | Quoted evidence |
|---|---|---|---|---|---|
| `extracts/gemini_out/7BQPMJ39WpI_gemini.md:63` | `extracts/pending_raw/tom/new_selected_10/transcript_7BQPMJ39WpI.txt:97` | MIDDLE | BEGIN | 2953 / 10519 | The first thing I always do when I look at gold is to identify impulses, and you can see that very clearly right here. |
| `extracts/gemini_out/7BQPMJ39WpI_gemini.md:83` | `extracts/pending_raw/tom/new_selected_10/transcript_7BQPMJ39WpI.txt:197` | END | MIDDLE | 6409 / 10519 | Often we have candles when it speeds up that are very trend stable. Why are they trend stable? Because they show us that they aren't often marked by large spikes and wicks |
| `extracts/gemini_out/7BQPMJ39WpI_gemini.md:88` | `extracts/pending_raw/tom/new_selected_10/transcript_7BQPMJ39WpI.txt:206` | END | MIDDLE | 6737 / 10519 | I can select very well that it makes sense to play these trends. Provided that we are not in a sideways phase, and therefore, I simply recommend the following. |
| `extracts/gemini_out/gWjHq5UMisY_gemini.md:28` | `extracts/pending_raw/tom/new_selected_10/transcript_gWjHq5UMisY.txt:96` | MIDDLE | BEGIN | 2856 / 11988 | the VPOC, that is the volume weighted point of control, the balance of turnover is already below this price range. |
| `extracts/gemini_out/gWjHq5UMisY_gemini.md:33` | `extracts/pending_raw/tom/new_selected_10/transcript_gWjHq5UMisY.txt:128` | MIDDLE | BEGIN | 3934 / 11988 | I've checked that off here as well and say reversal short, reversal long. |
| `extracts/gemini_out/hQ8sOq67x5o_gemini.md:43` | `extracts/pending_raw/tom/new_selected_10/transcript_hQ8sOq67x5o.txt:8` | BEGIN | MIDDLE | 4147 / 12372 | You already need 25% just to get back to zero because 1% of 80,000 is 800 euros risk per trade and no longer 1,000 euros risk per trade, so it takes you longer. |
| `extracts/gemini_out/HySZZSjMxF8_gemini.md:33` | `extracts/pending_raw/tom/new_selected_10/transcript_HySZZSjMxF8.txt:99` | MIDDLE | BEGIN | 3168 / 10558 | Because, and this is very, very important, always keep an eye on the closing prices. |
| `extracts/gemini_out/WQ_OAdz-PJ8_gemini.md:78` | `extracts/pending_raw/tom/new_selected_10/WQ_OAdz-PJ8_I_Tested_10_Trading_Strategies_Only_THIS_One_Actually_Works_for_Beginners.txt:252` | END | MIDDLE | 8186 / 12332 | if you now have such an impulse again with a subsequent sideways phase, meaning acceptance of this price range, then you will also realize that there is a high probability that the market will trade through here again |
| `extracts/gemini_out/zAwEX_tRUfE_gemini.md:23` | `extracts/pending_raw/tom/new_selected_10/zAwEX_tRUfE_My_Simple_1-Minute_Scalping_Strategy_for_10000Month.txt:104` | MIDDLE | BEGIN | 3075 / 9291 | And that's why you must, even if you trade on the 1-minute chart, always understand the context. |

## Independent arithmetic and interpretation limits

From FORMULAS.md:468 gross R and :77 arithmetic mean, with fee terms set to zero only because the source explicitly says "without fees": RR = 11/5 = 2.20000000; E(32%) = 3/125 = 0.02400000R; break-even = 5/16 = 31.25000000%; E(50%) = 3/5 = 0.60000000R. All inputs are SOURCED to transcript_gWjHq5UMisY.txt:262-275 and :291-300; the weighted-mean algebra is independently computed here.

For pgdmKLJ0hhA, the SOURCED entry 406, stop 394, target 435 in transcript_pgdmKLJ0hhA.txt:8 yield R = (435-406)/(406-394) = 29/12 = 2.41666667. The extract's quoted 2.41 preserves the speaker's coarse precision; the idealized zero-fee break-even derived the same way is 12/41 = 29.26829268%. "Below 35%" is an illustrative sourced statement, not evidence that every lower win rate profits. No empirical win-rate, fee-net profitability, market-regime percentage, or return projection has been validated. FORMULAS.md:403-404 and :468 define explicit cost deductions; zero fees in the arithmetic above are an audit scenario, not an execution assumption.

## Reproducible five-claim checks

### 7BQPMJ39WpI

Extract: `extracts/gemini_out/7BQPMJ39WpI_gemini.md`. Raw source: `extracts/pending_raw/tom/new_selected_10/transcript_7BQPMJ39WpI.txt`.

| Extract line / claim | Raw line | Result | Quoted evidence |
|---|---:|---|---|
| 53: Claim 1: Gold market failure for unprepared traders | 8 | PASS | The ultimate gold trading strategy for the year 2026. Gold is currently one of the most exciting markets out there, but at the same time, it is where most traders fail. |
| 58: Claim 2: Gold favors breakout and trend continuation over counter-trading | 45 | PASS | This means that for counter traders, gold is a dangerous game. For trend continuation and breakout traders, gold is excellent. |
| 63: Claim 3: First step is impulse identification | 97 | PASS | The first thing I always do when I look at gold is to identify impulses, and you can see that very clearly right here. |
| 78: Claim 6: Market exhaustion after extreme moves | 191 | PASS | Whenever it gets very extreme, there's a high probability that the market is exhausted for now, and then the second wave can come. |
| 83: Claim 7: Trend-stable candles without large spikes or wicks | 197 | PASS | Often we have candles when it speeds up that are very trend stable. Why are they trend stable? Because they show us that they aren't often marked by large spikes and wicks |

### 96iPFDpXEcU

Extract: `extracts/gemini_out/96iPFDpXEcU_gemini.md`. Raw source: `extracts/pending_raw/tom/new_selected_10/transcript_96iPFDpXEcU.txt`.

| Extract line / claim | Raw line | Result | Quoted evidence |
|---|---:|---|---|
| 53: Claim 1: Gap fill probability inside prior day range | 8 | PASS | I can tell you one thing right now, the probability that a gap like this is filled is significantly higher than a gap up here |
| 73: Claim 5: Commodity gaps resist quick closure | 8 | PASS | you can forget about such markets closing such a price gap extremely quickly. Why is that? Quite simple. The hedgers, that is, those who carry out the hedging transactions, they have to hedge themselves |
| 78: Claim 6: Political stock market gaps have short legs | 8 | PASS | if this gap has to do with political stock markets, and then I don't care about the direction, the probability is high that the market will close this gap again. |
| 88: Claim 8: Decreasing liquidity indicates buyer exhaustion | 8 | PASS | you can read that right down here. Now comes the break upwards and the liquidity decreases. What does that mean? It means that many market participants no longer have any interest up there |
| 98: Claim 10: Favorable risk-to-reward ratio after liquidity cycle | 8 | PASS | But if you just wait a moment until the liquidity goes down and then increases again, then the probability is much higher that you can trade this gap close with a great risk reward ratio. |

### aursfDVYzUk

Extract: `extracts/gemini_out/aursfDVYzUk_gemini.md`. Raw source: `extracts/pending_raw/tom/new_selected_10/transcript_aursfDVYzUk.txt`.

| Extract line / claim | Raw line | Result | Quoted evidence |
|---|---:|---|---|
| 23: Claim 1 | 8 | PASS | It simply shows us where prices are fair and where they are unfair. |
| 28: Claim 2 | 8 | PASS | The absolute equilibrium level is called the VPOC in the volume profile and the point of control in the market profile, the time-weighted moment where the market has spent the most time within the relevant time frame. |
| 38: Claim 4 | 8 | PASS | As a rule, you use 68.2 or 70% of all trades of the day and say that where 70% of the highest trading volume occurred is the so-called value area. |
| 43: Claim 5 | 8 | PASS | This value area for me means the price range in which the market is fairly priced. |
| 58: Claim 8 | 8 | PASS | if the market moves into unfair price areas, there is a high probability that it will eventually return to a fair price level, because it wants to do business at fair prices. |

### gWjHq5UMisY

Extract: `extracts/gemini_out/gWjHq5UMisY_gemini.md`. Raw source: `extracts/pending_raw/tom/new_selected_10/transcript_gWjHq5UMisY.txt`.

| Extract line / claim | Raw line | Result | Quoted evidence |
|---|---:|---|---|
| 23: Claim 1 | 90 | PASS | Here, for example, was the value of the previous week, so the equilibrium. |
| 28: Claim 2 | 96 | PASS | the VPOC, that is the volume weighted point of control, the balance of turnover is already below this price range. |
| 33: Claim 3 | 128 | PASS | I've checked that off here as well and say reversal short, reversal long. |
| 43: Claim 5 | 147 | PASS | naturally, relatively small stop losses that I set based on the setups and depending on the structure, also quite good risk-reward ratios. |
| 53: Claim 7 | 274 | PASS | That means for me, I have a risk reward ratio of 2.2. |

### hQ8sOq67x5o

Extract: `extracts/gemini_out/hQ8sOq67x5o_gemini.md`. Raw source: `extracts/pending_raw/tom/new_selected_10/transcript_hQ8sOq67x5o.txt`.

| Extract line / claim | Raw line | Result | Quoted evidence |
|---|---:|---|---|
| 23: Maximum Strategy Drawdown Ceiling | 8 | PASS | To really understand the professional trader's path, you must never have a strategy that has a drawdown of more than 20%. |
| 28: Contextual Strategy Selection | 8 | PASS | Consequently, it is absolutely essential and necessary not to trade just any random setups, but to know exactly which strategy with the highest probability can be found in the market right now. |
| 38: Intraday Swing Trading Market Regime Suitability | 8 | PASS | Intraday swing trading makes sense in both market phases. You just have to understand when the market is in balance or not. |
| 48: Risk-Reward Ratio Stop Loss and Target Geometry | 8 | PASS | That means your stop loss is, for example, 10 points, and your profit target is 40 points. |
| 53: Enduring Extended Losing Sequences | 8 | PASS | 16 losing trades in a row very few people can actually handle that. |

### HySZZSjMxF8

Extract: `extracts/gemini_out/HySZZSjMxF8_gemini.md`. Raw source: `extracts/pending_raw/tom/new_selected_10/transcript_HySZZSjMxF8.txt`.

| Extract line / claim | Raw line | Result | Quoted evidence |
|---|---:|---|---|
| 23: Claim 1 | 32 | PASS | Multi-time frame simply means looking at different time units and ideally thinking from the top down if you're a day trader. |
| 28: Claim 2 | 35 | PASS | Because the larger a time period is, the more likely it is that the signal will be significant when a technical level is broken, overtraded, or whatever. |
| 43: Claim 5 | 185 | PASS | So, I'm going to go ahead and transfer these specific price ranges over to the chart, and then I'll carefully observe where all of this might actually take place. |
| 53: Claim 7 | 232 | PASS | And so by doing this, I can build a really great risk reward ratio for myself. |
| 63: Claim 9 | 281 | PASS | And when it then trades back down from that increased volume where it started, I've had exhaustion at the top. |

### pgdmKLJ0hhA

Extract: `extracts/gemini_out/pgdmKLJ0hhA_gemini.md`. Raw source: `extracts/pending_raw/tom/new_selected_10/transcript_pgdmKLJ0hhA.txt`.

| Extract line / claim | Raw line | Result | Quoted evidence |
|---|---:|---|---|
| 33: Multi-Timeframe Lower-Chart Refinement | 8 | PASS | And now, and this is something that's crucially important, I'll go into a smaller time frame and note the levels 407 and 435. |
| 38: Execution Patience Requirement | 8 | PASS | And then, and now comes the decisive part, having the patience to truly let this trade run accordingly once it's entered. |
| 43: Asymmetric RRR Calculation | 8 | PASS | I'll show you in a moment how you can shorten the whole thing even My result is therefore, I have a risk-reward ratio of 2.41. |
| 48: Low Win Rate Profitability Criterion | 8 | PASS | In fact, even though the win rate is below 35%, I would still be profitable using this particular method. |
| 68: Intraday Setup Execution Framing | 8 | PASS | Looking at, for example, a 30-minute or even a 1-hour chart for a corresponding model that works logically and sensibly in terms of the setup. |

### WQ_OAdz-PJ8

Extract: `extracts/gemini_out/WQ_OAdz-PJ8_gemini.md`. Raw source: `extracts/pending_raw/tom/new_selected_10/WQ_OAdz-PJ8_I_Tested_10_Trading_Strategies_Only_THIS_One_Actually_Works_for_Beginners.txt`.

| Extract line / claim | Raw line | Result | Quoted evidence |
|---|---:|---|---|
| 53: Claim 1: Simple strategy prevents beginner overwhelm | 13 | PASS | Especially for beginners, it's essential and necessary to use a relatively simple strategy so as not to be overloaded with this multitude of a thousand pieces of information. |
| 58: Claim 2: Volume reveals market acceleration probability | 111 | PASS | The most essential thing is to have a model from the start where you can select for yourself, \"Is there a higher probability that the market is accelerating or not? But how can you do that? Quite simply through the volume. |
| 73: Claim 5: Retest of fast move zone favors continuation | 227 | PASS | the probability, if it runs up here again, is initially high that it will continue long |
| 83: Claim 7: P and B profile structures are mirrored logic | 289 | PASS | If you take this P and simply flip it into a B, you will find that you have exactly the same logic. Just applied in the completely reversed direction |
| 98: Claim 10: Volume profile vs footprint chart precision | 324 | PASS | It is obviously not quite as precise as this particular concept here. And frankly, it is not quite as high performance or granular as the specialized footprint charts |

### zAwEX_tRUfE

Extract: `extracts/gemini_out/zAwEX_tRUfE_gemini.md`. Raw source: `extracts/pending_raw/tom/new_selected_10/zAwEX_tRUfE_My_Simple_1-Minute_Scalping_Strategy_for_10000Month.txt`.

| Extract line / claim | Raw line | Result | Quoted evidence |
|---|---:|---|---|
| 23: Mandatory Context Requirement | 104 | PASS | And that's why you must, even if you trade on the 1-minute chart, always understand the context. |
| 28: Market Profile Context Foundation | 55 | PASS | When we look for trades on the 1-minute chart, we always look at what is the context. |
| 38: Disequilibrium Structure Identification | 246 | PASS | This means this upper edge here shows me that the market is becoming unbalanced, just like here. |
| 43: Mathematical Advantage at Low Win Rates | 220 | PASS | You also have a mathematical advantage, so even with just a 50 or 60% win rate, you can make money with this. |
| 48: Defined Risk and Hit Rate Relationship | 252 | PASS | This approach will significantly increase my overall hit rate, and at the same time, it will improve my risk-reward ratio, especially if I clearly define where I am getting out of the position. |

## Complete verifier receipts

```text
python scripts/dev/verify_extract_quotes.py extracts/gemini_out/7BQPMJ39WpI_gemini.md
OK       7BQPMJ39WpI_gemini.md:53
OK       7BQPMJ39WpI_gemini.md:58
OK       7BQPMJ39WpI_gemini.md:63
OK       7BQPMJ39WpI_gemini.md:68
OK       7BQPMJ39WpI_gemini.md:73
OK       7BQPMJ39WpI_gemini.md:78
OK       7BQPMJ39WpI_gemini.md:83
OK       7BQPMJ39WpI_gemini.md:88
OK       7BQPMJ39WpI_gemini.md:93
OK       7BQPMJ39WpI_gemini.md:98
OK       7BQPMJ39WpI_gemini.md:107
PASS: 0 problem(s)
exit_code=0
stderr=(empty)
```

```text
python scripts/dev/verify_extract_quotes.py extracts/gemini_out/96iPFDpXEcU_gemini.md
OK       96iPFDpXEcU_gemini.md:53
OK       96iPFDpXEcU_gemini.md:58
OK       96iPFDpXEcU_gemini.md:63
OK       96iPFDpXEcU_gemini.md:68
OK       96iPFDpXEcU_gemini.md:73
OK       96iPFDpXEcU_gemini.md:78
OK       96iPFDpXEcU_gemini.md:83
OK       96iPFDpXEcU_gemini.md:88
OK       96iPFDpXEcU_gemini.md:93
OK       96iPFDpXEcU_gemini.md:98
OK       96iPFDpXEcU_gemini.md:107
OK       96iPFDpXEcU_gemini.md:112
OK       96iPFDpXEcU_gemini.md:117
PASS: 0 problem(s)
exit_code=0
stderr=(empty)
```

```text
python scripts/dev/verify_extract_quotes.py extracts/gemini_out/aursfDVYzUk_gemini.md
OK       aursfDVYzUk_gemini.md:23
OK       aursfDVYzUk_gemini.md:28
OK       aursfDVYzUk_gemini.md:33
OK       aursfDVYzUk_gemini.md:38
OK       aursfDVYzUk_gemini.md:43
OK       aursfDVYzUk_gemini.md:48
OK       aursfDVYzUk_gemini.md:53
OK       aursfDVYzUk_gemini.md:58
OK       aursfDVYzUk_gemini.md:63
OK       aursfDVYzUk_gemini.md:70
OK       aursfDVYzUk_gemini.md:75
OK       aursfDVYzUk_gemini.md:80
PASS: 0 problem(s)
exit_code=0
stderr=(empty)
```

```text
python scripts/dev/verify_extract_quotes.py extracts/gemini_out/gWjHq5UMisY_gemini.md
OK       gWjHq5UMisY_gemini.md:23
OK       gWjHq5UMisY_gemini.md:28
OK       gWjHq5UMisY_gemini.md:33
OK       gWjHq5UMisY_gemini.md:38
OK       gWjHq5UMisY_gemini.md:43
OK       gWjHq5UMisY_gemini.md:48
OK       gWjHq5UMisY_gemini.md:53
OK       gWjHq5UMisY_gemini.md:58
OK       gWjHq5UMisY_gemini.md:63
OK       gWjHq5UMisY_gemini.md:70
OK       gWjHq5UMisY_gemini.md:75
OK       gWjHq5UMisY_gemini.md:80
PASS: 0 problem(s)
exit_code=0
stderr=(empty)
```

```text
python scripts/dev/verify_extract_quotes.py extracts/gemini_out/hQ8sOq67x5o_gemini.md
OK       hQ8sOq67x5o_gemini.md:23
OK       hQ8sOq67x5o_gemini.md:28
OK       hQ8sOq67x5o_gemini.md:33
OK       hQ8sOq67x5o_gemini.md:38
OK       hQ8sOq67x5o_gemini.md:43
OK       hQ8sOq67x5o_gemini.md:48
OK       hQ8sOq67x5o_gemini.md:53
OK       hQ8sOq67x5o_gemini.md:58
OK       hQ8sOq67x5o_gemini.md:63
OK       hQ8sOq67x5o_gemini.md:69
OK       hQ8sOq67x5o_gemini.md:73
PASS: 0 problem(s)
exit_code=0
stderr=(empty)
```

```text
python scripts/dev/verify_extract_quotes.py extracts/gemini_out/HySZZSjMxF8_gemini.md
OK       HySZZSjMxF8_gemini.md:23
OK       HySZZSjMxF8_gemini.md:28
OK       HySZZSjMxF8_gemini.md:33
OK       HySZZSjMxF8_gemini.md:38
OK       HySZZSjMxF8_gemini.md:43
OK       HySZZSjMxF8_gemini.md:48
OK       HySZZSjMxF8_gemini.md:53
OK       HySZZSjMxF8_gemini.md:58
OK       HySZZSjMxF8_gemini.md:63
OK       HySZZSjMxF8_gemini.md:70
OK       HySZZSjMxF8_gemini.md:75
OK       HySZZSjMxF8_gemini.md:80
PASS: 0 problem(s)
exit_code=0
stderr=(empty)
```

```text
python scripts/dev/verify_extract_quotes.py extracts/gemini_out/pgdmKLJ0hhA_gemini.md
OK       pgdmKLJ0hhA_gemini.md:23
OK       pgdmKLJ0hhA_gemini.md:28
OK       pgdmKLJ0hhA_gemini.md:33
OK       pgdmKLJ0hhA_gemini.md:38
OK       pgdmKLJ0hhA_gemini.md:43
OK       pgdmKLJ0hhA_gemini.md:48
OK       pgdmKLJ0hhA_gemini.md:53
OK       pgdmKLJ0hhA_gemini.md:58
OK       pgdmKLJ0hhA_gemini.md:63
OK       pgdmKLJ0hhA_gemini.md:68
OK       pgdmKLJ0hhA_gemini.md:74
OK       pgdmKLJ0hhA_gemini.md:78
PASS: 0 problem(s)
exit_code=0
stderr=(empty)
```

```text
python scripts/dev/verify_extract_quotes.py extracts/gemini_out/WQ_OAdz-PJ8_gemini.md
OK       WQ_OAdz-PJ8_gemini.md:53
OK       WQ_OAdz-PJ8_gemini.md:58
OK       WQ_OAdz-PJ8_gemini.md:63
OK       WQ_OAdz-PJ8_gemini.md:68
OK       WQ_OAdz-PJ8_gemini.md:73
OK       WQ_OAdz-PJ8_gemini.md:78
OK       WQ_OAdz-PJ8_gemini.md:83
OK       WQ_OAdz-PJ8_gemini.md:88
OK       WQ_OAdz-PJ8_gemini.md:93
OK       WQ_OAdz-PJ8_gemini.md:98
OK       WQ_OAdz-PJ8_gemini.md:107
OK       WQ_OAdz-PJ8_gemini.md:112
PASS: 0 problem(s)
exit_code=0
stderr=(empty)
```

```text
python scripts/dev/verify_extract_quotes.py extracts/gemini_out/zAwEX_tRUfE_gemini.md
OK       zAwEX_tRUfE_gemini.md:23
OK       zAwEX_tRUfE_gemini.md:28
OK       zAwEX_tRUfE_gemini.md:33
OK       zAwEX_tRUfE_gemini.md:38
OK       zAwEX_tRUfE_gemini.md:43
OK       zAwEX_tRUfE_gemini.md:48
OK       zAwEX_tRUfE_gemini.md:53
OK       zAwEX_tRUfE_gemini.md:58
OK       zAwEX_tRUfE_gemini.md:63
OK       zAwEX_tRUfE_gemini.md:68
OK       zAwEX_tRUfE_gemini.md:74
OK       zAwEX_tRUfE_gemini.md:78
PASS: 0 problem(s)
exit_code=0
stderr=(empty)
```

## Input fingerprints and parsed inventory

| Video | Raw lines | Raw whitespace words, including metadata | Extract SHA-256 | Raw SHA-256 |
|---|---:|---:|---|---|
| 7BQPMJ39WpI | 317 | 2316 | 2332d69bcd560747ce5916a5935ef19a3bf020f031964841c9b9a6d705889fc8 | 6ad6e1ceefb9231b1f0f5bdaaa6771ee14f2ba8614042ba23e298482b224743d |
| 96iPFDpXEcU | 8 | 1890 | c4d6871fd2042e81ded0a07bbb7f596509acad69ac5ed3618243a8b43bdfdb15 | 27948553bfe69893bd2121f2206485a184988186f65cf3f8354b1e341af3fda8 |
| aursfDVYzUk | 8 | 3167 | 75a68d3a736b27aaede5a4009b1ecfcef0086c753884e3824aaf14100b377d36 | 3b15add875948aac817edf56d7710746efa93abbb76c05250ebab90fa12b3e00 |
| gWjHq5UMisY | 370 | 2593 | 54a6dc640168abbb10cbaaa394735cf78987058e81a6220fb43149320ba38643 | ca55f3fa2988154906b237aa9dfb678042be15fcd199e30a5741cf6d399e37e6 |
| hQ8sOq67x5o | 8 | 2613 | 793de6dd9d922a39f493effa99f9d65855fe7fac80812dc50c7fa4f0cd932d29 | eec1d5a8fbc04808c7117516080b2ab8eda98a822b359c16ed1bc5f325d8d818 |
| HySZZSjMxF8 | 322 | 2361 | f08d70e5cee4734be06e652d85469b22e651a81b03a88b704c121ea164a16897 | d3b8769db4608536dc4aaa21b69853fec9adeccc39ef0035a4a7967f8237e7f1 |
| pgdmKLJ0hhA | 8 | 2403 | c5800f52aad2595d2405cba9027c302c3a92ae77f35c29f3df7accf6ee45e5d4 | e4285edcb3402b6c0179ddc85325b5d889cf3e7e82f0418bf77b79c5956e1e17 |
| WQ_OAdz-PJ8 | 369 | 2269 | 3a446af03fa22effbac789135a7d9fa927f5b9a819ea8ba7062bc93b80e1d65a | 14c26b9d022ef498a6a30cdbed69a566db6b3f0bc65e6e69fa7b79aa96f3cd4f |
| zAwEX_tRUfE | 285 | 1740 | dce163228145871dffe6f44b1852f39bba240bb012088d7e5e58ce715f5b1877 | d8a30a908f4a5d1f4a65ef240660dc0923c2c26389dbe350ad9ecae8340680c9 |

Inventory derived by parsing the actual files: 9 extracts, 9 source transcripts, 86 detailed quote blocks, 107 total quote blocks, 45 sampled claims. Metadata word-count labels were not trusted. Counts do not infer an in-vivo-code count from the number of quote blocks.

Result: 2 APPROVE, 7 FIX across 9 Gemini outputs; 107 verifier passes, 105 caption-body matches, 45 sampled claims checked, 9 GPS discrepancies; 3 HIGH and 3 LOW finding groups.
