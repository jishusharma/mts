# Fast-move zones: what Tom and Fabio actually teach (Q32, 2026-10-12, JIS-NUC)

Research only, nothing backtested, nothing wired. Quotes are verbatim from `raw_transcripts_canonical/<id>_raw.txt`
(timestamps stripped, whitespace normalised; each quote was machine-matched, file:line below is where it starts).
Tom's files are one long paragraph, so line 19 or 7 is the whole transcript body.

## 0. The saffron story is NOT a source
"Price moves fast through prices where nobody wants to trade" is the narrator's sentence in
`research/TOM_FABIO_STORY_2026-10-05.md:13-16`. It paraphrases balance/imbalance [TOM-030]. Neither trader says it.
The sourced version of the idea is split in three, and they point in different directions (section 1).

## 1. Sourced rules (S = source id used in the catalogue)

| S | Trader | Rule as taught | Verbatim quote | file:line |
|---|---|---|---|---|
| S1 | Tom | A low volume node is a zone of little volume for the time frame in use, and the market BOUNCES off it. (Not "fast through".) | "these price areas are zones with very low volume for the respective time frame we're looking at. And the market often bounces off these areas." | YmygDgtoxO8_raw.txt:19 [TOM-210] |
| S2 | Tom | Inside an LVN the market fills the empty range with liquidity; stay alive while the last buy area holds. | "we're in the low volume area. That means it's doing nothing other than filling this empty price area with liquidity now." | 4MoNjEQ2Dd8_raw.txt:19 [TOM-211] |
| S3 | Tom | A fast, aggressive leg leaves a space (fair value gap) that is traded quickly. | "This creates a space where the market was ultimately traded quickly and aggressively." | Fj4FDZQxw0I_raw.txt:19 |
| S4 | Tom | A single print is the same thing in profile language: a range never retraced within that move. | "single print areas are in reality nothing more than specific price ranges where the market never actually retraced within this particular move" | Fj4FDZQxw0I_raw.txt:19 [TOM-202] |
| S5 | Tom | Gaps work as levels only with trend stability; in a sideways phase with thin liquidity above they get traded through. | "fair value gaps are great support resistance levels. They are, but only if the market has trend stability." / "volatile fair value gap in a sideways phase. And if liquidity up here isn't high, then there's a good chance it'll just be traded through." | Fj4FDZQxw0I_raw.txt:8 and :19 [TOM-204, 209] |
| S6 | Tom | A trend that left its liquidity behind is "not healthy": price is in low volume and wants to return to high liquidity. This is a REVERSION rule for a fast move. | "this trend isn't entirely healthy." / "there was simply no liquidity left here and the liquidity was down here. That means low volume." | zQTbdEweG3c_raw.txt:19 [TOM-056, 140] |
| S7 | Tom | Outside the Bollinger bands is not a signal by itself. Volume surging outward means an imbalance and the market "won't return" quickly; volume must support the direction. This is exactly the "context decides" point. | "we gain an advantage because this allows us to see whether a market is supported by volume. Only then does it make sense to trade in that direction." / "But now trading volumes are surging outward" / "then the market certainly won't return to that Ballinger band range quickly and definitely not within the same day." | 4VXpUjhKG2U_raw.txt:7 |
| S8 | Tom | Method order: locations first, then context, then order flow for the timing. | "how we connect the dynamic context and then use the order flow to get the timing right." | -dMWA_bbm3o_raw.txt:7 |
| S9 | Tom | Narrow opening range with normal liquidity raises the odds of a trend (compression, in profile terms). Tom's own claim, unverified. | "if something is very narrow, but liquidity is the same as in the previous days, then the probability at a later point in time is much greater that the market will trend." | Ld1dhjGdTCA_raw.txt:19 [TOM-212] |
| S10 | Tom | Side of VWAP sets the bias. | "they're initially more bearishly inclined" (price below VWAP) | 43JaKHRvxHk_raw.txt:19 [TOM-049] |
| S11 | Fabio | After the book sweeps a level, if buyers squeeze the top and the next level is empty, expect a fast move through it. This is the only place a trader says "fast move through an empty level". The trigger is aggression eating the liquidity, not the empty level alone. | "If they squeeze this one on the top and they reach this one, probably, with high probability, they will go for a fast move all the way up because, as you can see, this level is pretty empty" | FawPrRUGNpk_raw.txt:770-776 |
| S12 | Fabio | Fast sweeps happen near the extremes of range/session. | "when you have a book sweeping, a fast movement." | FawPrRUGNpk_raw.txt:253 |
| S13 | Fabio | CVD is the direction read; value area low is a target. | "see what the CVD is telling us" / "reaching the value area low" | FawPrRUGNpk_raw.txt:1048; 8CWKfoSJu3c_raw.txt:141 |
| S14 | Fabio | Hidden pressure inside balance (CVD runs, price flat), effort vs result, big-trade push. Already summarised and sourced by the supervisor. | see `research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md` sections 1-2 (S1-S8 there) | FABIO_TRADE_MODEL.md:9-40 |

### What this means for the idea
1. Tom's LVN teaching is bounce / fill / revert (S1, S2, S6); the "fast through" reading is Tom's FVG/single print
   in a trend-stable phase (S3-S5) and Fabio's sweep-then-empty-level (S11). Fast through a void needs the
   direction to be confirmed by aggression or trend stability; the void alone is not a trigger in either source.
2. Jis's BB point is Tom's own (S7): the band cannot say which side; volume/imbalance does. A short outside the
   upper band in an up-trend is the case Tom names as a trap.
3. Direction filters the sources support: CVD slope (S13, S14), VWAP side (S10), volume support (S7), trend
   stability (S5). Compression: S9 and Fabio's balance (FABIO_TRADE_MODEL S1).

## 2. NO-SOURCE list (Tom and Fabio say nothing; do not present as theirs)
| Item | Status |
|---|---|
| Bollinger bands as a trigger or level | NO-SOURCE. Tom names them only to say they mislead (S7). 0 hits in Fabio transcripts. |
| RSI(14) and the 40-60 regime | NO-SOURCE for Tom and Fabio. RSI belongs to Malkan (`research/malkan_rsi_2026-09-28/`, raw A-CQiV_UFB4, -CBvFi40sIQ). The exact 40-60 wording is NOT verified in this card; Q33 must cite the Malkan file before using it. |
| Open interest, long/short ratio, funding | NO-SOURCE. 0 hits for "open interest", "long short", "funding" in all 113 canonical transcripts. Positioning data is MTS-own (`quad_classify`, positioning layer). |
| Volatility squeeze (BB width, ATR ratio) | NO-SOURCE. "squeeze" in Tom (tS6ZEiHj8gQ) and Fabio (FawPrRUGNpk, 8CWKfoSJu3c) means a short squeeze or a squeeze of a liquidity level, not a volatility state. Closest sourced notions are S9 and FABIO_TRADE_MODEL S1 (range <= k x ATR). |
| ATR as a rule | NO-SOURCE (Fabio's trail "does not trail by bars or ATR"). |
| Every numeric threshold (percentiles, windows, 1.5x volume) | NO-SOURCE. They are grid values, counted in the FDR family, never tuned. |
| LVN as a "fast move" detector | NO-SOURCE as stated. See point 1 above. |

## 3. Should Tom and Fabio guide each other? (c)
Answer from the sources: they describe the same two layers in different words, so they overlap, but neither
tells you to use the other's signal.
- Tom already combines both layers himself: context first, then order flow for timing (S8), and he uses
  absorption (TOM-025, y67l86cSqb8_raw.txt:19: "a very large buyer here who is absorbing everything that's being sold").
- Fabio uses profile concepts: balance, value area low (S13), the volume profile (FawPrRUGNpk_raw.txt:373),
  and then CVD/big trades for timing.
- Direction of help the sources suggest: Tom's map (VA, LVN, FVG, weekly POC) could place Fabio's order-flow
  trigger; Fabio's CVD/absorption is what Tom calls "proof". Both are inside each trader's own method already.
- No passage found where either trader names or endorses the other (the grep list of Fabio-named files was not
  individually verified, so treat this as "none found", not "none exist").
- Repo constraint: `backtest/layers/test_layer_boundaries.py:9` says Tom is never filtered by layers, and the
  audit (GUIDANCE_AUDIT.md) shows no wiring either way. Recommendation: do not wire. Measure as DESCRIPTIVE tags
  in Q33 (same-side agreement vs not), which `tom_bt.py:280-290 fabio_tag` already supports. Only a surviving
  cell would justify the Q34 ruling.
