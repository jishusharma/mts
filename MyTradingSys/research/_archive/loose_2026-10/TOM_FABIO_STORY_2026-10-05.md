# THE MARKET IS A BAZAAR: Tom and Fabio, told as a story (2026-10-05)

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

| # | What the teacher says | What MTS does | Gap / fix direction |
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
