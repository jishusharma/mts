# THE MARKET IS A BAZAAR: Tom and Fabio, told as a story (v2 living book, 2026-10-30)

v2 of the 2026-10-05 story (archived at `research/_archive/loose_2026-10/TOM_FABIO_STORY_2026-10-05.md`, kept as history). Chapters 1-8 are unchanged except the status column in chapter 8. Chapters 9-13 are new: regime, timeframe ladder, proof checklist, Bollinger Bands, and what history says. Every history number is copied from a RESULT file with its file:line and never recomputed. Labels: SOURCED = a teacher's words or a named public definition; OURS = our own choice; UNMEASURED = no number exists yet.

Session MTS-2026-10-05-0520Z-CLI-ANA-weekopen (part 2). A teaching file for the operator. Read-only, no code touched.
Every Tom quote carries its [TOM-NNN] id (`research/TOM_VERBATIM_INDEX.md`, `conditions/*.md`).
Fabio's items come from `research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md` (FTM). The live example uses
`research/_archive/loose_2026-10/MARKET_ANALYSIS_2026-10-05.md` (MA). Anything that is not Tom or Fabio is marked **[convention]**
(a standard market-profile idea) or **[MTS]** (our own build).

---

## Chapter 1. The bazaar

Picture a spice bazaar. One merchant has saffron, and nobody knows its price. He shouts 90. Nobody buys.
He shouts 80. A few people buy. At 70 a crowd forms and saffron changes hands all afternoon. At 60 the sellers
go home because the price is insulting.

That is all a market is: **an auction looking for the price where the most business gets done.**
- Price **moves fast** through prices where nobody wants to trade (90, 60).
- Price **sits still** at prices where everybody trades (70).

Tom says it as balance and imbalance:
> "where the market is in balance, everyone is satisfied. And where the market is out of balance, there is often
> dissatisfaction among the big players." [TOM-030]

Everything below comes from this one idea.

## Chapter 2. The merchant's notebook: the volume profile

At the end of the day the merchant writes down how much saffron sold at each price. If you turn that notebook
sideways, you get a **volume profile**: one horizontal bar per price, and the bar's length is the volume traded there.

```
price
86900 |██                  <- few trades: "unfair" high
86700 |█████
86510 |████████████████   <- POC: the busiest price
86300 |███████████
86000 |████████
85814 |████               <- VAL: bottom edge of value
85500 |██                  <- few trades: "unfair" low
```
(Shape illustrative. The levels are this week's real weekly profile, MA section 2.)

- **POC, the Point of Control**: "the point where the market has accumulated the highest total volume at a given price
  level" [TOM-180]. This is the 70-rupee saffron price, where everyone agreed.
- **VAH / VAL, Value Area High and Low**: the top and bottom edges of the zone where most trading happened. Tom:
  "everything above the value area high and below the value area low is considered an unfair price area" [TOM-183].
  The usual cut is the 70% of volume around the POC **[convention]**. Tom gives the idea; the 70% figure is not from Tom.
- **Inside value** = fair = comfortable. **Outside value** = unfair. Price is out there only briefly, or because
  something has changed.

Why the levels matter: "where high volume occurs, we often see a reaction when a market returns there" [TOM-182].
Traders who did business at the POC remember it. When price comes back, they act again.

Several notebooks are kept at once: **weekly**, **daily**, **prior day** and **4-hour** profiles. MTS computes all of them
(`current_market_state.md`). Tom reads them top-down: weekly first, then daily.

## Chapter 3. The two moods: balance and trend

**Balance (sideways).** Buyers and sellers are both happy. Price swings between VAH and VAL like a pendulum.
> "when supply and demand are balanced, the market will always try to return to that equilibrium." [TOM-031]
> "this is the case in about 70% of market phases" [TOM-044] (Tom's own statistic, not verified)

**Trend (imbalance).** One side is unhappy and chases. Tom names three kinds [TOM-048, TOM-050]:
- **Fast**: almost no pullbacks; it leaves empty gaps (fair value gaps) that often get revisited.
- **Normal**: steady, with pullbacks; price stays on one side of the **VWAP**, the volume-weighted average price of the day.
  "If the price is below it, they're initially more bearishly inclined." [TOM-049]
- **Slow creeping**: grinds along.

**How to see the big picture.** Watch whether the weekly POCs climb, stay flat or fall. That shows which way the big
money is moving [TOM-196]. Today: last week's POC was 83896, this week's is 86510, so the weekly POC is **rising** (MA).

## Chapter 4. The market cycle

The bazaar keeps repeating one loop:

```
 BALANCE ──(pressure builds)──> BREAK OUT OF VALUE ──(acceleration)──> TREND
    ^                                                                    │
    └──────────── new BALANCE at a new price <──(exhaustion, B/P shape)──┘
```

1. **Balance.** Price rotates inside value.
2. **Break.** Price leaves value. "Very often it accelerates at first ... a lot of market participants fall out of balance
   and then they sell their positions" [TOM-186]. The traders who expected more sideways get stopped out, and their
   orders push price further.
3. **Trend** until the chasing side runs out of fuel. A **B-shaped** profile (fat at the bottom with a thin tail on top)
   is "the first sign ... that there has definitely been strong and aggressive selling" [TOM-036].
4. **New balance** at a new price. Right after a big move the market is "sorting itself out" and the right action is
   **WAIT** (`setup_type_rules.md` section 3).

Sometimes the break **fails**. Price pokes outside value, finds no business there, and "came back in, formed acceptance"
[TOM-011]. A failed break back into value is one of the best stories in this whole method.

## Chapter 5. Tom's way: Idea + Proof + Math

Tom is a **map reader**. He trades the edges of the map.

**Step 1, the Idea (a route plan).** Go from one volume node to the next. "I expect a reaction first. And a reaction is
usually a counter at first." [TOM-134] In balance that means:
> "I can definitely look for short trades up here and long trades down here." [TOM-042]
Short at VAH, long at VAL, target the POC or the other edge.

**Step 2, the Proof.** The idea alone is not a trade:
> "I need an idea for a route plan and I need proof that this idea should be put into action right now." [TOM-135]

Proof is the crowd at the zone confirming that it cares about the level:
- **Rejection wick**: price touches the level and gets thrown back.
- **Absorption**: heavy selling into the level, yet price does not fall. Someone big is absorbing it.
- **Finished auction**: "only when auctions are completely finished" [TOM-013]. High volume at the very low means the
  auction is *not* finished yet.
- **Speed**: "the speed with which it rejected this is promising" [TOM-010]. Watch whether speed is "picking up" [TOM-016].

**Step 3, the Math.** Know where you are wrong (the stop goes *below the last liquidity*, `risk_protocol.md` 2.1) and where
you are going (the next node). Tom's whole edge is asymmetry:
> "even with a hit rate of 30 to 40% you have an average riskreward ratio of greater than three and you will be
> incredibly successful" [TOM-091]
> "through your hit rate and the minimum usable risk-reward ratio, you can know, 'I have to trade at least up to
> here, otherwise the whole thing makes no sense.'" [TOM-093]

**Tom's playbook by mood** (reconstructed, `setup_type_rules.md` section 3):

| Mood | Where | Trade |
|---|---|---|
| Balance | at VAH / VAL / prior-day VA edges | Counter-trade back toward the POC |
| Balance about to resolve | at the edge, with proof of direction | Breakout |
| Normal trend | pullback to VWAP or structure | Join the trend |
| Exhausted trend | extreme, with proof of reversal | Counter-trade |
| Sorting itself out | anywhere | **Nothing** |

## Chapter 6. Fabio's way: listening to the engine room

Tom reads the map. Fabio **listens to the footsteps**. Both use the same bazaar; Fabio watches *who is pushing* bar by bar
(FTM section 1):

1. **Balance first.** No direction, so wait.
2. **Hidden pressure.** Inside the balance, price is flat but **CVD** (cumulative buy volume minus sell volume) runs
   hard one way. Flat price with falling CVD means sellers are quietly loading. This is the *leading* signal.
3. **Effort vs result.** Big aggression with no price progress means **absorption** ("punch to the wall"). Aggression that
   moves price means **control**. The trigger is the first bar where pressure finally *gets a result*, with big trades
   behind it.
4. **Tiny stop** just past the absorbed extreme. Move to breakeven as soon as price "explodes".
5. **Add** on each new big-trade confirmation, often risking the first leg's profit.
6. **Trail** the stop behind the last level where Fabio's side showed control, not behind bars or ATR.
7. **Exit** when big trades stop pushing (a new balance forms) or the other side takes control back.
8. **Pick the day.** Press only on volatile, directional days. Fabio's market is the NY cash open.

Fabio's payoff: many scratches and a few winners of 1:5 to 1:19.

**Tom vs Fabio in one line:** Tom asks "*where* will they react?" (profile levels). Fabio asks "*who* is winning right now?"
(order flow). In MTS they stay separate layers. Fabio is never a filter on Tom (CLAUDE.md hard rule).

## Chapter 7. Today, told through both lenses (data cutoff 05:17Z, MA)

- **Map (Tom).** The weekend rally climbed to 86956, into the top of weekly value (VAH 86866), and found no business
  up there. Price fell back through the weekly VAL (85814) and now sits on the daily VAL (85452), *outside* weekly value
  on the low side. The weekly POC is still rising, so the big picture is up while the short-term story is a failed push.
- **Engine room (Fabio).** 4-hour CVD is about -2400: sellers did the work. OI is flat, so no flush and no new short
  crowd. The book leans to the ask. On the 15-minute view, buyers are poking back.
- **Tom's idea.** Long back toward value if the low gets *rejected* (the rank-2 setup is at 85278, stop 85107, target POC 86510).
  Tom's proof for that idea: none yet, so **wait**.
- **Fabio's idea.** Is pressure building inside this morning's small balance? Effort vs result at 85450? Not yet readable:
  v3 is in shadow mode and silent (see M5).
- **The failed-break story (TOM-011).** If the US open flushes below 85278 and price *comes back in and forms acceptance*,
  that is the textbook long. If price stays outside value, the next node down is 84677 to 84400.

## Chapter 8. Teacher's notebook: where MTS loses the plot

Retelling the method this way shows that the gaps are mostly about **translation**, not missing knowledge. Both reviews say
extraction is done: Tom 2 of 74 engine parameters are sourced, Fabio v3 0 of 8 numeric parameters are sourced
(TOM_FABIO_REVIEW_2026-10-03 section 0).

| # | What the teacher says | What MTS does (10-05) | Gap / fix direction |
|---|---|---|---|
| M1 | The minimum R:R comes from **your own hit rate** [TOM-093]; the edge is R:R above 3 at a 30-40% hit rate [TOM-091] | Fixed floor 1.25 (testnet ruling 10-03), no measured hit rate; WAIT_RR blocked every rally hour 10-04/05 | Measure the hit rate per setup and derive the floor from it, as Tom says. Until then the floor is a placeholder, not Tom |
| M2 | The target is the *next volume node*, node to node [TOM-132..134] | Target = nearest POC/HVN. A near target makes R:R small, and the trade dies at WAIT_RR | Test "next node beyond the nearest" as the Tom route; replay 10-04 |
| M3 | Weekly VPOC direction = money flow [TOM-196] | Not computed anywhere (grep: no vpoc-trend feature) | Add weekly POC migration to the snapshot as context (Tom-sourced) |
| M4 | "came back in, formed acceptance" [TOM-011]: the failed-break trade | No acceptance definition and no failed-break setup; rank-1 today is a long at a level price sits *below* | Needs a sourced acceptance test (closes/time back inside VA); flag NO-SOURCE until a quote gives one |
| M5 | Fabio's hidden pressure (S2) and effort vs result (S3) are the core | Built in `backtest/layers/fabio/v3/signals.py` (`pressure`, `effort_result`), but v3 is shadow and has 0 live rows (E6); its tests are not in the gate (E7) | Fix the v3 live silence first; it is the only layer that holds Fabio's real idea |
| M6 | Both traders manage the winner: breakeven, add, trail behind control levels; no clock | Time exit after 8 bars (E2); runner dead at 10 USD size (E3); no pyramiding | Remove the time exit for Tom/Fabio on testnet; trade multiples of the minimum contract so a split and adds can exist |
| M7 | Proof at the zone, entry *when* proof shows (one video shows entry before proof, E5) | Limit orders at the zone that do not fill (E1: 5 of 6); proof rarely completes (E4) | Golden-scenario tests from the line-by-line extracts: fire a trade when the extract says Tom entered |
| M8 | Wait while the market is "sorting itself out"; Fabio presses only on volatile days | turn_of_candle trades every 15 min regardless (35 trades, -0.25 USD since 10-04 20Z) | Keep ToC as a cost/plumbing probe only; a day-selection gate for Fabio needs a Fabio quote first |
| M9 | Fabio's market is the NY cash open | US anchor hard-coded 13:30Z; wrong from 2026-11-01 | DST-aware anchor (MA G6) |

**Short version.** MTS already *knows* the map: profiles, VA, POC, VWAP and regime all work. It does not yet
**take the trade the way the teachers do**. The R:R gate is not Tom's, the targets are too near, there is no failed-break
setup, Fabio's real engine is silent, and execution cuts winners with a clock. Fix the translation in the order M1/M2 and M6
(cheap, they unblock trades), then M5, then M4 (needs sourcing).

---

# NEW IN V2

## Chapter 8b. M1-M9: fixed or open (checked 2026-10-30)

Status comes from what is on disk today, not from the 10-05 text. "Open" means no fix was found; it does not mean nobody is working on it.

| # | Status | Evidence |
|---|---|---|
| M1 hit-rate-based R:R floor | OPEN | `tom_fabio_concepts_2026-10-29/CONCEPTS.md:278` (finding 7): the engine still uses a fixed floor file |
| M2 next-node target | OPEN | no change found; the 10-05 text stands |
| M3 weekly POC migration | OPEN | no weekly-POC-trend feature found in `src/` or `backtest/layers/` (search 10-30) |
| M4 acceptance / failed break | OPEN | `CONCEPTS.md:275` (finding 4): acceptance not implemented; `CONCEPTS.md:192` says MISSING |
| M5 Fabio v3 pressure and effort-vs-result | OPEN | v3 is still a shadow layer (`backtest/layers/alerts/test_live_runner_v3_shadow.py`); no live-rows proof found |
| M6 manage the winner, no clock | OPEN | `CONCEPTS.md:278`: adds are not executed for either trader |
| M7 proof-then-entry golden tests | OPEN | no change found |
| M8 day selection / wait while sorting out | OPEN | no Fabio quote for a day gate added; ToC stays a probe |
| M9 DST-aware US open | FIXED | `src/main/java/datafeed/MarketDataSnapshot.java:933-935` computes 09:30 America/New_York as UTC (13:30Z in EDT, 14:30Z in EST) |

Count: 1 fixed, 8 open.

## Chapter 9. Regime: what kind of day is it?

One idea: **regime is the answer to "do I trade the edges or the breakouts today?"** Tom puts it first: "Whether it's trend or balance because I have to use different setups there" [TOM-065].

Page 1, the plain words. Balance means price rotates inside value. Trend means one side keeps pushing. Tom says about 70% is not trending [TOM-046] (his own statistic, unverified).

Page 2, the live definitions. MTS has several, and they do not agree. Each is labelled.

| Name | Rule | Label | File |
|---|---|---|---|
| Phase A (weekly) | completed weekly close vs the 10-week average of weekly closes, and its slope over 2 weeks: above and rising = markup; above and not rising = distribution; below and falling = markdown; below and not falling = accumulation | OURS (Weinstein-style) | `research/context_factors_2026-10-16/CONTEXT_FACTORS_SPEC.md:135` |
| Phase B (daily) | 30-day return >= +7.5% markup, <= -7.5% markdown, else the position in the 90-day range | threshold SOURCED (tom_bt default), range rule OURS | same file, line 136 |
| Intraday | efficiency ratio of the last 24 hourly closes >= 0.30 = trend, else balance | OURS | same file, line 137 |
| Multi-TF state | efficiency ratio over the last 20 bars >= 0.30 = IMB (trend), else BAL (balance); location HIGH if >= 0.85 of the range, LOW if <= 0.15 | OURS | `research/multi_tf_bias_2026-10-18/RULE.md:16-18` |
| Malkan RSI regime | RSI range over 20 bars: BULL if min >= 40 and max >= 60; BEAR if max <= 60 and min <= 40; else RANGE | 40/60 are Malkan's levels, the 20-bar window is the code default | `backtest/layers/rsi/malkan_40_60.py:24-33` |

Page 3, the trap. Phase A and Phase B agree on only 45.7% of the decision events (`CONTEXT_FACTORS_SPEC.md:140-141`). "Regime" is not one thing, so always say which one.

Page 4, what the Wyckoff names need. "Absorption" and "distribution" in the Wyckoff sense need flow (OI, CVD, delta at a level). From price alone they are labels (`pre_us_squeeze_2026-10-29/RESULT.md:29-30`).

## Chapter 10. The timeframe ladder: which close to wait for

One idea: **a candle is a claim until it closes.** Decide on closed bars only.

Page 1, the ladder. This is OURS: neither teacher gives a rule for it. Where a number exists it is cited.

| Step | Timeframe | What it answers | Wait for | Label |
|---|---|---|---|---|
| 1 | 1D (and 12h, 8h) | trend or balance, where in the range | the daily close | OURS (`multi_tf_bias_2026-10-18/RULE.md:11-13`: 1D sets location, 12h/8h veto only) |
| 2 | 4h | second range, the swing that is running | the 4h close | OURS (same file, line 14) |
| 3 | 1h | flow sign: who was in a hurry | the last completed 1h bar | OURS (same file, line 15) |
| 4 | 15m | the break or the pierce | the 15m close outside the band | OURS (`bb_pierce_force_2026-10-29/RESULT.md:6`) |
| 5 | 5m | the entry | the 5m close back across the mid, then the next 5m close | OURS from the operator's walked rule (`prev_close_break_2026-10-29/RESULT.md:48-49`) |

Page 2, why closes. Tom wants acceptance, "Not with quick spikes but with real acceptance" [TOM-019]. Andrea Cimi (a channel mate of Fabio) entered on the 5-minute close that confirmed a divergence (`fabio_cvd_2026-10-30/CVD_CONCEPTS.md`, section 3).

Page 3, the higher timeframe decides which way a lower swing resolves. On 30m WaveTrend, a sell dot with the 4h WT up was followed by +1% first in 56%, against 47% with the 4h down (n=308 and 157; `wt30_sequence_2026-10-30/RESULT.md:14-15`). Descriptive, fee-free.

Page 4, the multi-TF stack as a trade rule showed no edge: net -6.58 bps per decision, t -1.17, n=1,348 (`multi_tf_bias_2026-10-18/REPORT.md:3`). The ladder is for reading, not yet for trading.

Page 5, how many bars to wait after a close: UNMEASURED. No file measures it.

## Chapter 11. The proof checklist

One idea: **an idea is not a trade until the zone proves it.** Tom: "I need an idea for a route plan and I need proof that this idea should be put into action right now." [TOM-135]

Tick the proofs at one level. Thresholds are given only where a file gives one; otherwise UNMEASURED.

| Proof | Plain words | Threshold | Label / source |
|---|---|---|---|
| Rejection speed | price touches the level and is thrown back fast | UNMEASURED | Tom [TOM-010]; no number in `CONCEPTS.md` A4 |
| Absorption | heavy selling or buying at the level and price does not move | a "large" print is at or above the trailing 99th-percentile size; a large 5m bar is the top or bottom 2% (>= +244.5 BTC or <= -259.2 BTC) | idea Tom [TOM-025]; the cut is OURS (`large_trade_absorption_2026-10-30/RESULT.md:5,13`) |
| Finished auction | only one side printed at the bar edge | UNMEASURED live; the engine's version is a different thing (`CONCEPTS.md:273`, finding 2) | Tom [TOM-009, TOM-013] |
| Acceptance | closes back inside value, not a spike | UNMEASURED; not implemented (`CONCEPTS.md:275`) | Tom [TOM-019, TOM-011] |
| CVD vs price | CVD makes a lower low while price stays level | UNMEASURED; filed as U8 (reversal rate vs matched lows) | Fabio F-CVD3 |
| Delta vs candle | positive delta but a negative close = absorbed buyers | UNMEASURED as a rule | Fabio F-CVD4 |
| Distance to the next level | how much room there is | within 0.5%: level reached 74% (n=156); beyond 1.5%: 13% (n=540) | OURS cuts, counts in `bb_pierce_force_2026-10-29/RESULT.md:12,14` |
| Minimum reward | R:R above 3 at a 30-40% hit rate | the floor must come from your own hit rate; that hit rate is UNMEASURED per setup | Tom [TOM-091, TOM-093]; M1 |
| Number of proofs | how many are enough | NOT STATED by Tom ("many, many", `SETUP_CATALOG.md:320`); the old engine's 3 is OURS | OURS |
| Veto | CVD flipping against the day = no counter-trend long | UNMEASURED | Fabio F-CVD9 |

Rule of the page: a proof with no number stays UNMEASURED until a RESULT file gives one.

## Chapter 12. The Bollinger Bands: size, not direction

One term: **BB (Bollinger Bands).** A moving average with a band two standard deviations either side. It measures how wide the market is. Fabio rates it F tier, "a proxy for volatility" (F-CVD13, `CVD_CONCEPTS.md`, section 3b).

Page 1, what history says: a squeeze predicts size, not side. After a pre-US squeeze (n=192): up 29%, down 29%, sideways 43%, and the US 4h range is 1.54x the box (median). After a wide box (n=223): 18 / 23 / 59 and 0.80x (`pre_us_squeeze_2026-10-29/RESULT.md:12-14`). The first break held 52% of the time, so it is a coin flip (line 21).

Page 2, a pierce of the band: about half close back across the mid first (52% failed, n=1,009; `bb_pierce_force_2026-10-29/RESULT.md:11`). A coil before the pierce did not change reach: 35% vs 37% distance-matched (line 19 of the same file).

Page 3, the dance. After a short starts below the mid and touches the lower band, a close still near the band (%b below 0.25) means about 59-64% get a new low first; a close away from it means 26-32% (n up to 6,360; `bb_dance_2026-10-30/RESULT.md:11-16`). Holding to the mid did not pay more than leaving early: +0.168% vs +0.172% to +0.178% gross, all under 0.2% against the 0.12% round-trip cost (lines 29-38).

Page 4, direction tools are not the band. Fabio's direction tools are delta, big trades and liquidity (S tier); the band is F tier (`CVD_CONCEPTS.md`, section 3b). Our own counts agree (C17: 29 / 29 / 43).

Page 5, the operator's candle rule (a green candle at the BB mid, short on the cross of its close, stop at the prior high) is a spec, not a result. The every-candle version loses after fees on every TF tested: 5m n=20,764 net -0.103%; 15m n=8,130 net -0.090%; 1h n=2,132 net -0.063% (`prev_close_break_2026-10-29/RESULT.md:14-16`).

## Chapter 13. What history says: one box per idea

All boxes are descriptive counts from existing RESULT files. No fees unless the box says "net". Nothing is recomputed. n is the sample; the file:line is where the number sits. "Not a claim" applies to every box.

**Idea 1. Balance: trade the edges back to the POC (Tom, TOM-042).**
Box: UNMEASURED as a fee-net rule on its own. Closest: no anchor level beat a placebo in the volume-profile phase 2 (46 of 48 real-minus-placebo CIs straddle 0, every year negative; `MyTradingSys/system/LAYERS.md:19`).

**Idea 2. Failed break back into value (Tom, TOM-011).**
Box: UNMEASURED (no acceptance definition, M4). Nearest descriptive: after a 2.5% 1m drop and a bounce to the BB mid, the low broke within 4 h in 44% (n=813; `drop_bounce_2026-10-29/RESULT.md:13`).

**Idea 3. Weekly POC direction = money flow (Tom, TOM-196).**
Box: UNMEASURED (M3, not computed).

**Idea 4. The target is the next node, not the nearest (Tom, TOM-134).**
Box: UNMEASURED (M2). Distance matters: level within 0.5% reached 74% (n=156), beyond 1.5% 13% (n=540; `bb_pierce_force_2026-10-29/RESULT.md:12,14`).

**Idea 5. Cross-market divergence (Tom's correlation trick).**
Box: verdict NOT-ADD. DEV net -110 bps (n=35) and -72 bps (n=52); the placebo was at or above the real result in 100% and 59% of draws (`tom_correlation_trick_2026-10-26/RESULT.md:3,14`).

**Idea 6. Hidden pressure: CVD runs one way inside a balance (Fabio, F-CVD2).**
Box: UNMEASURED (U7). The bounce delta share did not change the odds of the low breaking: 43% vs 46% (`drop_bounce_2026-10-29/RESULT.md:27`).

**Idea 7. Absorption: effort without result reverses (Fabio, F-CVD3, F-CVD4).**
Box: on its own it did not reverse. After absorbed big sells (n=95), price went DOWN first more often, 55% vs 36%, about 2 standard errors; absorbed big buys n=99 (`large_trade_absorption_2026-10-30/RESULT.md:15-26`). Fabio's reading needs the level; that count is U1 and is not done. For the failed bounce near the low (n=116), the low broke within 4 h in 43%; with net selling into the fade, 38% (n=47, within noise; `drop_bounce_2026-10-29/RESULT.md:60-62`).

**Idea 8. Open interest shows which side is loading.**
Box: no. Every OI x price cell sat between 48% and 54% up after 60 min (n=35,963 windows; `oi_side_2026-10-30/RESULT.md:24-30`).

**Idea 9. An oversold cascade bounces, and momentum-shift signals call it.**
Box: n=755 triggers, up after 60 min 55.8%; the trigger bar's low was broken within 4 h in 87%. Four of five shift signals sit within 1.7 points of a random bar (`bounce_shift_2026-10-30/RESULT.md:9,18,33`).

**Idea 10. A break after lower highs travels further.**
Box: n=22 after 3+ falling 4h highs reached 0.5 of the pattern height 73%, against 48% for other breaks (n=44). Small sample; a measuring frame only (`lh_break_2026-10-30/RESULT.md:16-17,25`).

**Idea 11. Bollinger squeeze, pierce and the dance.**
Box: see Chapter 12. Size, not direction (`pre_us_squeeze_2026-10-29/RESULT.md:12-21`).

**Idea 12. The multi-timeframe stack.**
Box: net -6.58 bps, t -1.17, n=1,348 (`multi_tf_bias_2026-10-18/REPORT.md:3`).

**Idea 13. Previous-close break (operator).**
Box: loses after fees on 5m, 15m and 1h; 1h is best at -0.063% net (n=2,132; `prev_close_break_2026-10-29/RESULT.md:10,16`).

**Idea 14. WaveTrend 30m dots.**
Box: the dots mark exhaustion of the swing, not trend: sell dot then +1% first 53% (n=465); the 4h decides the resolution (`wt30_sequence_2026-10-30/RESULT.md:13,29-34`).

## Chapter 14. Where to read more

- Map of the 10-29 / 10-30 session: `research/eagle_eyes_picture_2026-10-28/SESSION_MAP_2026-10-30.md`.
- Tom and Fabio as step-by-step concepts: `research/tom_fabio_concepts_2026-10-29/CONCEPTS.md`.
- Fabio on CVD: `research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md` (24 quotes verified).
- Every catalogued setup: `research/setup_catalog_2026-10-15/SETUP_CATALOG.md`.
