# T064 - Timeframe selection and confirmation: Tom + Fabio verbatim extract

Session: MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch (Cloud, offline, static). Item: items/T064_timeframe_selection_confirmation.md.
Corpus: Tom = the 9 transcripts under extracts/processed/tom/ (HySZZSjMxF8, WQ_OAdz-PJ8, zAwEX_tRUfE, 7BQPMJ39WpI, 96iPFDpXEcU,
pgdmKLJ0hhA, gWjHq5UMisY, hQ8sOq67x5o, aursfDVYzUk); Fabio = the 8 transcripts under extracts/processed/fabio_valentini/
(0KyIEdvVKMQ, 0jM5Y31YJak, 8CWKfoSJu3c, FawPrRUGNpk, LQvv5xgy_ik, StaphlRH8NQ, fZlNGWvd2Ko, jasv3L-d8ZE).
Other analysts in raw_transcripts_canonical/ are out of scope. Quotes are cut at sentence boundaries from the transcript text;
auto-caption punctuation is not reliable.

Questions (label on every quote):
- **Q1** which timeframe's absorption/distribution to trade (zone TF vs trigger TF)
- **Q2** what confirmation is required before entry
- **Q3** stop run vs continuation
- **Q4** how far price retraces after a sweep / before it resumes

`file:line` locator: most Tom transcripts are one long paragraph per file (line 7, 9 or 12), so those carry a char offset inside
the line; the long Tom/Fabio caption files carry a real line number plus the caption timestamp `[~m:ss]`.
Gate: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/_archive/loose_2026-10/T064_TF_CONFIRMATION_EXTRACT.md` (run from repo root,
result in section 5). The `scripts/tools/verify_extract_quotes.ps1` named in the brief does not exist on any ref; the python
verifier does and runs on Cloud.

## 1. Answer first (what the quotes support, and what they do not)

| Question | Tom | Fabio | Verdict |
|---|---|---|---|
| Q1 zone TF vs trigger TF | Explicit, top-down. Levels/profile come from the larger frame (daily/1h/30m), are carried down, and trades are "only" executed at those locations; the trigger frame is smaller (15m on 1h, 5m on 30m, 1m for acceptance). | One line only: micro-mechanics "need a confirmation from the higher time frame"; and "I enter without confirming the trend on higher time frame". No frame is named. | Tom: SOURCED, but as a pair of examples, not a fixed ratio. Fabio: frame NO-SOURCE. |
| Q2 confirmation | Reversal signal AT a pre-marked point; volume exhaustion (volume spike at the high, then price trades back below that volume) else "wait"; acceptance on the 1m chart; liquidity goes down then returns. | Aggressive big trades in the trade direction; aggression plus reloaded resting liquidity; two failed pushes into a wall (filled auction); delta effort with ~zero price result. | SOURCED for both, all qualitative. No threshold in any quote. |
| Q3 stop run vs continuation | Impulse + range + breakout of the range = continuation. Indicator traders get "stopped out" around liquidity. Low volume = snag/counter-trade. Above a marked level he still waits for the run back down. | "Book sweeping" at range/session extremes; continuation = break-through plus reload; absorbed + immediate reversal = failed auction, not a break. | Qualitative discriminator exists (reload / acceptance / absorption after the poke). No quote defines a stop run by OI. |
| Q4 retrace depth | No depth. "Retest" is allowed while the new acceptance range holds; extreme + low liquidity -> correction; impulse-duplication is a TARGET rule. | No depth. Target = next liquidity cluster; retracement inside the day bias is normal; retrace expected when resting liquidity is absent. | NO-SOURCE for a depth in ticks/ATR/%. Only a bound (acceptance range holds) and a destination (next node / next cluster). |

Consequence for T063: the study must MEASURE retrace depth; it cannot be taken from either trader. The only sourced anchors are
Tom "retest while the acceptance range holds" (Q4) and Fabio "price usually goes to the next liquidity cluster" (Q4).

## 2. Tom quotes
### T064-Tom-01 [Q1]
> "Multi-time frame simply means looking at different time units and ideally thinking from the top down if you're a day trader. Because the larger a time period is, the more likely it is that the signal will be significant when a technical level is broken, overtraded, or whatever. That's why we traders who use multi-time frame thinking always like to look from the top down. This means, and I'll share my screen with you now, if we locate important price areas in a very high-level time frame, then as day traders, we can expect something bigger in a smaller time horizon"
**Source GPS: HySZZSjMxF8 | BEGIN**
raw_transcripts_canonical/HySZZSjMxF8_raw.txt:38-52. zone TF = top-down from the largest frame; trigger is a smaller one.

### T064-Tom-02 [Q1,Q2]
> "This is the hourly chart now and now I'll do the following and say I want to trade this on the 15-minute chart to define my risk well. And I know now what I'm looking for and where. That means I'm looking here, for example, for the possibility of a short position if the market it was trading above this level and then runs back in. I'm specifically looking for a clear reversal signal here right when the market reaches this critical point as that would confirm my setup for a potential entry"
**Source GPS: HySZZSjMxF8 | END**
raw_transcripts_canonical/HySZZSjMxF8_raw.txt:215-229. worked example: zones on 1h/daily, execution on 15m; confirmation = clear reversal signal AT the pre-marked point.

### T064-Tom-03 [Q1]
> "multi-timeframe is very useful for doing the following things. First, to locate where am I in the overall market environment? So, what can I expect? Second, have there already been breakouts from this large timeframe where I see that rejection was present? That gives me more confidence that the market will initially move back and forth in a sideways phase. And third, I can then very easily locate for myself in the small timeframe where the market is more likely to go"
**Source GPS: HySZZSjMxF8 | END**
raw_transcripts_canonical/HySZZSjMxF8_raw.txt:302-315. three jobs of the higher frame; the small frame only locates the trade.

### T064-Tom-04 [Q2]
> "And usually, when a reversal occurs, the volume also increases accordingly. Either here or here. And when it then trades back down from that increased volume where it started, I've had exhaustion at the top. But if it doesn't trade below this volume here, for example, then I have to wait"
**Source GPS: HySZZSjMxF8 | END**
raw_transcripts_canonical/HySZZSjMxF8_raw.txt:283-292. Tom's confirmation test = volume exhaustion at a pre-marked high; otherwise no trade.

### T064-Tom-05 [Q3]
> "if the market goes above this accordingly, I have a greater possibility in terms of risk that the market will run out here at the top again. But I'm actually still short oriented from the multi timeframe approach. And that means I would wait, for example, if it goes above here to see if it runs down again and makes lower lows for me again"
**Source GPS: HySZZSjMxF8 | MIDDLE**
raw_transcripts_canonical/HySZZSjMxF8_raw.txt:165-175. price above a marked level is not a reason to abandon the HTF bias; he waits for it to run back down.

### T064-Tom-06 [Q1]
> "You should use the setups offered to you here in the small timeframe. But it is vital that you only execute your trades accordingly at locations identified from your larger timeframes"
**Source GPS: WQ_OAdz-PJ8 | END**
raw_transcripts_canonical/WQ_OAdz-PJ8_raw.txt:9 (single-paragraph line, char 10285). small-TF setups, but only executed at locations from the larger TFs.

### T064-Tom-07 [Q1]
> "if you decide to move from a larger time frame down to a smaller one, you should transfer those blue price ranges from the larger time frame over to the smaller timeframe"
**Source GPS: WQ_OAdz-PJ8 | END**
raw_transcripts_canonical/WQ_OAdz-PJ8_raw.txt:9 (single-paragraph line, char 10014). zone transfer rule (30m profile -> 5m chart in his example).

### T064-Tom-08 [Q3]
> "Where there is low volume, there's a higher probability that the market will hit a snag. So, it's suitable for counter trades, for trading against the trend"
**Source GPS: WQ_OAdz-PJ8 | MIDDLE**
raw_transcripts_canonical/WQ_OAdz-PJ8_raw.txt:9 (single-paragraph line, char 5851). low-volume price = counter-trade / snag; high-volume acceptance = continuation.

### T064-Tom-09 [Q3,Q4]
> "Often the market went down here briefly and then up again. And now it comes down to this. If the market is rejected here again, then the big question is, what has changed"
**Source GPS: WQ_OAdz-PJ8 | MIDDLE**
raw_transcripts_canonical/WQ_OAdz-PJ8_raw.txt:9 (single-paragraph line, char 7760). brief poke through an accepted area then resume; the test is whether acceptance changed.

### T064-Tom-10 [Q2]
> "Only when the market clearly demonstrates to you above this specific level that it truly finds solid acceptance, can a significantly longer distance upwards be realistically planned, and a much faster, more decisive breakout be anticipated. And then you can, for example, with such a reliable setup or a stable balance forming above this area, wonderfully find new high probability acceptance on the 1-minute chart, which really helps confirm your next move"
**Source GPS: zAwEX_tRUfE | MIDDLE**
raw_transcripts_canonical/zAwEX_tRUfE_raw.txt:9 (single-paragraph line, char 3313). confirmation = acceptance above the level, found on the 1-minute chart.

### T064-Tom-11 [Q3]
> "Here we also have liquidity. Oh, stopped out, yeah. Above here, oh, now it's running. Oh, it's not running after all. Oh, it's finally running. Oh, it's not running after all. It's not running, stopped out again"
**Source GPS: zAwEX_tRUfE | MIDDLE**
raw_transcripts_canonical/zAwEX_tRUfE_raw.txt:9 (single-paragraph line, char 4673). Tom on indicator traders being stopped out around liquidity (retail side of a stop run).

### T064-Tom-12 [Q4]
> "Now, it is entirely possible that the price might move back down for a retest, but please remember that significant buying power entered the market right here. And as long as this specific price range, this new level of market acceptance, holds firm, the probability remains much higher"
**Source GPS: zAwEX_tRUfE | MIDDLE**
raw_transcripts_canonical/zAwEX_tRUfE_raw.txt:9 (single-paragraph line, char 5673). retrace bound = the new acceptance range holds; no number given.

### T064-Tom-13 [Q4]
> "after such an extreme in combination with low liquidity, a correction follows"
**Source GPS: 7BQPMJ39WpI | MIDDLE**
raw_transcripts_canonical/7BQPMJ39WpI_raw.txt:96-98. extreme + low liquidity -> correction (no depth given).

### T064-Tom-14 [Q4]
> "Whenever it gets very extreme, there's a high probability that the market is exhausted for now, and then the second wave can come"
**Source GPS: 7BQPMJ39WpI | MIDDLE**
raw_transcripts_canonical/7BQPMJ39WpI_raw.txt:197-200. exhaustion then second wave.

### T064-Tom-15 [Q3]
> "Whenever a market has had an impulse followed by a sideways phase and the next impulse arises within such a phase and breaks out of it, which is the case here, then the trend continuation follows with a relatively high probability"
**Source GPS: 7BQPMJ39WpI | MIDDLE**
raw_transcripts_canonical/7BQPMJ39WpI_raw.txt:151-157. continuation signature: impulse, range, breakout of the range.

### T064-Tom-16 [Q4]
> "You can see how large the first impulse stretch was and simply duplicate that onto the second one"
**Source GPS: 7BQPMJ39WpI | MIDDLE**
raw_transcripts_canonical/7BQPMJ39WpI_raw.txt:158-161. target rule (impulse duplication), NOT a retrace depth.

### T064-Tom-17 [Q2]
> "you can additionally look at the footprint chart for liquidity to see if the market has, for example, a so-called unfinished auction down here"
**Source GPS: 7BQPMJ39WpI | END**
raw_transcripts_canonical/7BQPMJ39WpI_raw.txt:301-305. optional footprint confirmation.

### T064-Tom-18 [Q2]
> "But if you just wait a moment until the liquidity goes down and then increases again, then the probability is much higher that you can trade this gap close"
**Source GPS: 96iPFDpXEcU | END**
raw_transcripts_canonical/96iPFDpXEcU_raw.txt:7 (single-paragraph line, char 8631). wait-for-liquidity-return confirmation before the entry.

### T064-Tom-19 [Q1]
> "I'll go into a smaller time frame and note the levels 407 and 435. I'm now transferring them exactly there"
**Source GPS: pgdmKLJ0hhA | MIDDLE**
raw_transcripts_canonical/pgdmKLJ0hhA_raw.txt:7 (single-paragraph line, char 4596). levels are carried from the larger to the smaller frame.

### T064-Tom-20 [Q1]
> "multi-timeframe on the daily, for example, looking for the technical approach. Looking at, for example, a 30-minute or even a 1-hour chart for a corresponding model"
**Source GPS: pgdmKLJ0hhA | END**
raw_transcripts_canonical/pgdmKLJ0hhA_raw.txt:7 (single-paragraph line, char 9158). swing: daily for context, 30m/1h for the model.

## 3. Fabio quotes

### T064-Fabio-01 [Q3]
> "when you have a book sweeping, a fast movement. Specifically, this one you can find really close to all-time high, all-time low of the range. Or if you are really close to the high of the New York session or on the session, the market approach this level and you have a book sweeping usually in this kind of level"
**Source GPS: FawPrRUGNpk | BEGIN**
raw_transcripts_canonical/FawPrRUGNpk_raw.txt:253-261 [~10:35]. book sweeping sits at range / session extremes; Fabio uses it for asymmetric R:R (few ticks of risk).

### T064-Fabio-02 [Q3]
> "You see the break through of this level of liquidity, so you have a continuation at least till here. And you see also that they reload the level of liquidity. So, they are like going down, closing the door to go above and going down"
**Source GPS: FawPrRUGNpk | BEGIN**
raw_transcripts_canonical/FawPrRUGNpk_raw.txt:269-274 [~11:08]. continuation is read from break-through + reload of the level.

### T064-Fabio-03 [Q2]
> "So you want to see maybe big trades confirming that there is an aggression there and that there is intention to go higher"
**Source GPS: FawPrRUGNpk | BEGIN**
raw_transcripts_canonical/FawPrRUGNpk_raw.txt:308-311 [~12:43]. scalper confirmation = aggressive big trades in the trade direction.

### T064-Fabio-04 [Q2]
> "this is the ultimate confirmation you need because you can see that they get aggressive and at the same time they reload fresh liquidity"
**Source GPS: FawPrRUGNpk | BEGIN**
raw_transcripts_canonical/FawPrRUGNpk_raw.txt:340-343 [~13:55]. confirmation = aggression plus reloaded resting liquidity.

### T064-Fabio-05 [Q4]
> "you always needs to be careful because the price usually goes to the next liquidity cluster. And the next liquidity cluster in this case was really close, okay? So, the risk to reward is not the best, but the confirmation that you get here gets respected for four additional times"
**Source GPS: FawPrRUGNpk | BEGIN**
raw_transcripts_canonical/FawPrRUGNpk_raw.txt:355-362 [~14:29]. target/travel = next liquidity cluster (Fabio analogue of Tom's next node).

### T064-Fabio-06 [Q2,Q3]
> "This is a strong confirmation that this is a filled auction, and the price will reverse for the path of least resistance"
**Source GPS: FawPrRUGNpk | MIDDLE**
raw_transcripts_canonical/FawPrRUGNpk_raw.txt:457-460 [~18:02]. two failed pushes into a wall = filled auction, reverse.

### T064-Fabio-07 [Q1,Q2]
> "Remember that this is market micro mechanics, so you always need a confirmation from the higher time frame on what's happening here"
**Source GPS: FawPrRUGNpk | MIDDLE**
raw_transcripts_canonical/FawPrRUGNpk_raw.txt:470-473 [~18:27]. the ONLY Fabio line on the TF hierarchy: micro-mechanics need higher-TF confirmation; the frame is not named.

### T064-Fabio-08 [Q4]
> "I don't see resting liquidity getting hot on the on this level. So, it means that they are not willing to get filled here, but they still have this massive liquidity level on the 27,895. So, there is a probability that we will see a retracement of the market"
**Source GPS: FawPrRUGNpk | END**
raw_transcripts_canonical/FawPrRUGNpk_raw.txt:866-872 [~32:44]. retrace expected when resting liquidity is absent at the level; no depth.

### T064-Fabio-09 [Q4]
> "even if your bias it's on the long side, you still have retracement on the main direction of the day"
**Source GPS: FawPrRUGNpk | END**
raw_transcripts_canonical/FawPrRUGNpk_raw.txt:1031-1034 [~38:35]. retracements inside the day bias are normal; no depth.

### T064-Fabio-10 [Q3]
> "The sellers got absorbed here. So what I'm trying to do is capitalize on the failed auction of the seller and then aggression of the level of the buyers. So I will be really fast in putting my position to break even if this level failed, okay? Because if this level failed, this one become the new pivot"
**Source GPS: fZlNGWvd2Ko | BEGIN**
raw_transcripts_canonical/fZlNGWvd2Ko_raw.txt:38-46 [~1:30]. absorbed sellers = failed auction, long; level becomes the new pivot, stop to break-even if it fails.

### T064-Fabio-11 [Q3]
> "the market explode from this level. You see all these aggression and a failed auction and this is the reason I closed my trade"
**Source GPS: fZlNGWvd2Ko | END**
raw_transcripts_canonical/fZlNGWvd2Ko_raw.txt:142-146 [~5:32]. failed auction = the exit reason, aggression + no acceptance.

### T064-Fabio-12 [Q3]
> "There was no fight of the buyers to break this level. They got absorbed and immediately sellers took back again the upper end"
**Source GPS: 8CWKfoSJu3c | MIDDLE**
raw_transcripts_canonical/8CWKfoSJu3c_raw.txt:107-110 [~4:36]. absorbed and immediately reversed: no sustained break, not a continuation.

### T064-Fabio-13 [Q2]
> "the result of the price for a pressure in by delta was almost zero. So this is a confirmation that the buyers are punching a wall and I want to be short"
**Source GPS: 0jM5Y31YJak | END**
raw_transcripts_canonical/0jM5Y31YJak_raw.txt:4 (single-paragraph line, char 6646). absorption confirmation = delta effort with ~zero price result.

### T064-Fabio-14 [Q1,Q2]
> "I enter without confirming the trend on higher time frame. This is not failure of the market"
**Source GPS: 0KyIEdvVKMQ | MIDDLE**
raw_transcripts_canonical/0KyIEdvVKMQ_raw.txt:4 (single-paragraph line, char 8234). higher-TF trend confirmation is a rule; the frame is not named.

### T064-Fabio-15 [Q3]
> "We are below the low. The next candle can accelerate and sweep"
**Source GPS: jasv3L-d8ZE | END**
raw_transcripts_canonical/jasv3L-d8ZE_raw.txt:169-170 [~9:38]. price below the low read as acceleration/sweep.

## 4. Proposed encoding ("zone TF" / "trigger TF")

Every item carries its source or NO-SOURCE (provenance rule, CLAUDE.md).

| Parameter | Proposal | Source |
|---|---|---|
| zone TF | The higher frame(s) that produce the HVN/LVN/POC/VA and swing levels; absorption or distribution counts only when price is AT a zone from this set. Ladder per Tom: daily -> 1h -> 15m (HySZZSjMxF8) and 30m -> 5m (WQ_OAdz-PJ8), 1h/30m model for a daily context (pgdmKLJ0hhA). | Tom T064-Tom-01/02/03/06/07/19/20 |
| trigger TF | The smaller frame where the signal is read; zones are carried down unchanged. Tom's examples: 15m (HySZZ), 5m (WQ), 1m acceptance (zAwEX). | Tom T064-Tom-02/07/10 |
| zone/trigger ratio | NO-SOURCE. Tom's examples are 4x (1h/15m), 6x (30m/5m); no rule states a ratio. Do not hard-code one; expose as a config pair and test both. | - |
| Fabio zone/trigger frame | NO-SOURCE (FR-55 stays UNDEFINED). Only "confirmation from the higher time frame". | Fabio T064-Fabio-07, -14 |
| confirmation (Tom) | Reversal signal AT the marked point; volume exhaustion = volume spike at the extreme, then price trades back through that volume; no exhaustion -> no trade. | Tom T064-Tom-02/04/10/18 |
| confirmation (Fabio) | Aggressive prints in trade direction plus reloaded passive liquidity, OR repeated absorption of the push, OR delta effort with near-zero price result. | Fabio T064-Fabio-03/04/06/13 |
| confirmation threshold | NO-SOURCE for every magnitude ("big trades", "increased volume", "almost zero"). Keep as flags, not numbers; calibrate by backtest, tagged [CALIBRATED], never [TOM]. | - |
| retrace depth after sweep | NO-SOURCE. Bound = "acceptance range holds" (Tom), destination = next volume node / next liquidity cluster. T063 measures the rest. | Tom T064-Tom-12; Fabio T064-Fabio-05/08/09 |
| stop run vs continuation | Discriminator is behaviour after the poke: reload/acceptance beyond the level = continuation; absorption and immediate return = failed auction. No OI/CVD definition exists in either transcript set. | Tom T064-Tom-11/15; Fabio T064-Fabio-01/02/06/10/12 |

## 5. Verifier result

`python scripts/dev/verify_extract_quotes.py` on this file, run on Cloud 2026-10-05: **PASS: 0 problem(s)** (35 quotes OK, GPS position tags match).

## Citation note: "30 to 40% hit rate" quote (TOM-091 vs TOM-092), 2026-10-05

This extract does not itself cite the quote (grep: no TOM-091/TOM-092 here); the mis-citation named in the brief sits in `research/_archive/loose_2026-10/TOM_FABIO_STORY_2026-10-05.md` (L117, L175) and `conditions/risk_protocol.md` L262.
Checked against `raw_transcripts_canonical/BVpYGKz9PBU_raw.txt` (GPS BVpYGKz9PBU): the quote "even with a hit rate of 30 to 40% you have an average riskreward ratio of greater than three ..." is verbatim there, and it follows "With counter trades, I always have to rely on the math."
The transcript confirms quote and video, not the numeric id. By the registry (`TOM_VERBATIM_INDEX.md`, the declared citation authority) the id is **TOM-091** (TOM-090 = the "rely on the math" line, TOM-092 = the "precisely 3:1" line). Fixed: TOM_FABIO_STORY L117 and L175 now cite TOM-091.
**Not fixed (needs DSA/operator):** `conditions/risk_protocol.md` tags this quote TOM-092 (L262), the math line TOM-091 (L255), the 3:1 line TOM-101 (L271), and carries an extra quote at L209 tagged TOM-090 ("my risk is 45 points") that has no index row. The file ids are shifted from the index by one around here; renumbering them in place would create duplicate ids,
and `verify_rule_citations.ps1` only checks that ids exist, so it passes (PASS, 214 ids) despite the drift. Suggested fix: add an index row for the 45-points quote (new id), then retag risk_protocol 255/262/271 to 090/091/092 and the later ids to the index text.
