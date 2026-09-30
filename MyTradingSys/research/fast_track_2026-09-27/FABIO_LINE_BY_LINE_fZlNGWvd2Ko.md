# FABIO LINE BY LINE - fZlNGWvd2Ko ("best trading session of the month of October")

Status: RESEARCH (Opus analyst, cloud sandbox, 2026-09-30). No market data used. Nothing here is a backtest result.
Fabio is a separate layer, never a Tom filter (PROJECT_VISION.md:94). Source: `raw_transcripts_canonical/fZlNGWvd2Ko_raw.txt`
(173 lines, [0:00]-[6:40]); every line was read in order. `L<n>` below = line n of that file.
Compared against: `extracts/processed/fabio_valentini/fZlNGWvd2Ko/extract_fZlNGWvd2Ko.md` (R1-R7), FABIO_RULEBOOK.md rows
FR-04/05/12/15/24/86/87, FABIO_V3_SPEC.md (S1-S8, models A/B/C, sections 5-6), FABIO_TRADE_MODEL.md, MISSING_PIECES section 1.
Code state: `MyTradingSys/backtest/layers/fabio/fabio_v3.py` does not exist yet; only `pending_test_fabio_v3.py` (spec-derived
tests). The old `fabio_of_model.simulate_trade` (:267) is marked DO NOT REUSE by the spec (section 9). So "code" = NO for every
row below unless the pending v3 contract names the function.

## 0. Why this video, and the answer in short
**Choice.** fZlNGWvd2Ko is the only one of the four unread videos that is a live session walkthrough of his own position: it
narrates entries, reloads, stop moves, a day-P&L floor and the exit reason, in order. Counts of trade-action phrases (entered,
my position, stop loss, break even, closed, reload, scaling in, my trade) per file: fZlNGWvd2Ko 13 in 7.5 KB; FawPrRUGNpk 62 in
55 KB, but it is a liquidity heat-map lecture whose "trades" are hypothetical ("you can say, look, I enter here", L380) and need
L2 data we do not have; 0KyIEdvVKMQ 2 (mental models); LQvv5xgy_ik 1 (risk-management lecture). MISSING_PIECES:43-44 rejected
it as "the same pattern as 0jM5". It is not: it is the **first LONG walkthrough** in our applied readings (0jM5, 8CWK and
jasv3L are all shorts), it contains a **side flip in the same session**, and almost all of it is **position management**, the part
the rulebook atomized.

**Answer (top findings).**
1. Management is event-driven, not distance-driven. Every stop move is triggered by the OTHER side failing: sellers attack and
   get stopped by buyers' big trades -> stop to zero (L110-116), then trail (L121-123), then ratchet again (L132-136). The spec's
   BE is `be_k * D` excursion and its trail is our own side's control bar (FABIO_V3_SPEC.md:133-136).
2. Our own side failing is a de-risk signal while still in the trade ("buyers failed again. So I want to lower my risk", L67-68).
   The spec has no in-trade reaction to our side being absorbed; S8 exits only on opposite control breaking S6 (:82-87).
3. A consolidation inside the trade is NOT an exit when the other side is the one being absorbed: he tightens to risk-free on a
   break of its edge (L97-108). Spec S8(b) exits on any new balance after entry (:85). Conflict.
4. The entry is a failed auction of the side that was pressing: sellers absorbed in the consolidation, then buyers aggress
   (L36-42). In spec terms that is a break AGAINST the S2 pressure sign; S5 only fires WITH it (:73-75), and model B needs a probe
   outside the balance first (:106-108) and then takes a fixed opposite-edge target (:111). He rode it to the top of the day.
5. Risk budget is the DAY's profit, across sessions (London profit funds NY), with a floor at day P&L = 0 and a worst-case day
   P&L that ratchets up ($10k, then $15k). Reloads happen while still at risk, before stop-to-zero. The spec evaluates windows
   independently, has a -3R daily stop and allows adds only after BE funded by the trade's locked profit (:137-142, :157-159).

## 1. Session frame (what the transcript states, and what it does not)
| field | reading | lines |
|---|---|---|
| market | NOT NAMED in this transcript (no instrument, no price, no clock time). Channel context suggests NQ; unverified here | - |
| day P&L before NY | London session made "around $10,000" | L15-17 |
| NY open state | choppy; gave back about $4,500-5,000 | L18-21 |
| loss side | two "continuation short" trades, both failed | L23-26 |
| day floor | "maximum drawdown that is break even": day back to 0 -> stop the session | L28-31 |
| main trade | LONG: failed seller auction + buyer aggression at the consolidation level; first load + 2 reloads + 1 protection level | L36-42, L152-156 |
| risk path | "only risking the profit of the day"; later "$980 to make potential $25,000" | L60-61, L76-77 |
| stop path | risk lowered (L68) -> tight/risk-free plan (L103-104) -> stop to zero (L113) -> below this low, worst case day $10k (L122-125) -> worst case day $15k (L135-136) | as cited |
| exit | explosion from a level + aggression + failed auction -> closed | L142-146 |
| counterfactual | day "pretty directional"; could have been 40-50k (L149), later "50 to 60,000" (L162) | L146-162 |
| data he uses | big trades (incl. where in the candle), aggression, absorption, effort vs result for BOTH sides, consolidation areas, levels a side "protects", "buyers wall", day P&L | throughout |
| data he does NOT mention | CVD, volume profile, VAH/VAL/POC, VWAP, heat map by name, clock time, points/ticks, contract counts | grep count 0 for cvd/profile/value area/vwap/poc/heat |
| unknowns | stop width in points (so no cost ratio), entry prices, reload prices relative to first entry, clock times, trade count of the chop phase beyond "two" | - |

## 2. Decision log (every passage, in order)
Columns: what he looks at | decision | information used | spec coverage (FABIO_V3_SPEC.md line) | code. Coverage: YES / PART /
NO / CONFLICT. Code: "v3-pending" = named in the pending_test_fabio_v3.py contract but not implemented; NO = nowhere.

| id | lines / time | looking at | decision | information used | spec | code |
|---|---|---|---|---|---|---|
| D01 | L1-14 [0:00-0:33] | intro, platform plug | none | - | n/a | n/a |
| D02 | L15-17 [0:35-0:41] | London session result | state: day P&L +~10k before NY | prior-session P&L | NO: windows are independent, day R per window (:155-156) | NO |
| D03 | L18-21 [0:43-0:51] | NY open chop | loses ~4.5-5k back | day type (chop), day P&L | PART: ex-post day type only, never an input (:165-166) | NO |
| D04 | L23-26 [0:57-1:03] | continuation setup | ENTER SHORT twice, both fail | trend-continuation read (details not given) | PART: model A with s=-1 (:95-102); location/trigger not stated in video | v3-pending model_a_trade |
| D05 | L26-31 [1:03-1:15] | day P&L | RULE: keep trading only while day P&L > 0; at 0 stop the session | day P&L relative to 0 | NO: -3R daily stop and stop-after-recovery (:157-159) do not model a floor at day = 0 funded by an earlier session | v3-pending first_leg_allowed (different rule) |
| D06 | L32-36 [1:17-1:26] | "when the buyers want to get aggressive" | WAIT for buyer aggression | aggression (delta, big trades) | PART: S3 control / S4 (:61-72) | NO |
| D07 | L36-39 [1:26-1:33] | consolidation area; sellers absorbed there; buyers wreck it | LOCATION = the consolidation and its absorption level | seller-side absorption inside balance, then buyer control | CONFLICT: seller aggression absorbed in flat price reads as S2 = -1 (distribution, :57-60), but his bias is LONG | NO |
| D08 | L40-42 [1:36-1:43] | failed auction of the seller + buyer aggression at the level | ENTER LONG | absorbed side (-1) then control side (+1) at the same level | PART: model B idea (FR-86 cited at :104) but B requires a close outside the balance and a 5-bar reclaim (:106-108) | NO |
| D09 | L43-49 [1:43-1:55] | this level vs a lower level where sellers are absorbed | STOP PLAN: get to BE fast if this level fails; the lower absorption level becomes the new pivot | level failure; location of seller absorption | NO: BE is by excursion `be_k*D` (:133-134); no "pivot shift" to the next absorption level | NO |
| D10 | L50-52 [1:57-2:02] | payoff | aim for "amazing" R:R, "take the top of the day" | no fixed target | YES for A/C (no target); CONFLICT for B (fixed opposite-edge target, :111) | v3-pending |
| D11 | L53-57 [2:05-2:17] | big trades and aggression | (method statement) | big trades, aggression | YES: S4, S3 | NO |
| D12 | L57-61 [2:17-2:29] | position size vs day P&L | ADD (loading / scaling in) while still at risk; risk capped by the day's profit | day P&L as risk budget | CONFLICT: adds only after stop at/beyond BE, funded by the trade's locked profit (:137-142) | v3-pending add_allowed (stricter) |
| D13 | L62-65 [2:29-2:37] | day P&L +9-10k | keep scaling "as we go" | day P&L | NO | NO |
| D14 | L67-72 [2:41-2:52] | buyers (his side) failed again; a big sell trade | REDUCE RISK before the level is tested | own side effort without result; big sell print as the anchor | NO: no in-trade response to S3 absorbed == s | NO |
| D15 | L74-77 [2:55-3:03] | "really solid aggression" | STOP UP: risk now $980 vs potential $25,000 | own side control bar | PART: trail exists only AFTER BE (:135); here risk is lowered but not zero | v3-pending trail_update |
| D16 | L78-87 [3:06-3:28] | day-level payoff | frame: best day about 2.5x worst day | day distribution | YES: day is the unit (:155) | v3-pending aggregate_day_r |
| D17 | L87-96 [3:28-3:47] | two candidate stop levels; big trades; sellers "protect this level" above | HOLD; on the next breakout of that level, trail the stop into profit | level defended by the opposite side; big trades | PART: trail anchor S6 is our own control bar (:76-78); the level the other side protects is not computed; trail not conditional on breaking it | NO |
| D18 | L97-106 [3:49-4:11] | buyers wall; sellers absorbed; buyers no result -> consolidation in the trade | HOLD; if this consolidation breaks down, be risk-free or very tight, because a breakdown revisits the lower level | both sides no result; which side was absorbed inside; the lower level | CONFLICT: S8(b) exits on any new balance after entry (:85) | NO |
| D19 | L106-109 [4:11-4:18] | (teaching) | manage with stop in profit when you see this | - | n/a | n/a |
| D20 | L110-116 [4:20-4:36] | sell acceleration stops before aggressive buyers | STOP TO ZERO (BE) | opposite side's push absorbed ("sellers got stopped again"); buyers continue | NO: BE trigger is distance, not this event | v3-pending be_update (distance only) |
| D21 | L116-120 [4:36-4:42] | big trades in the body of the candle; effort, no result | WAIT ("who win this battle") | big-trade location inside the bar (body vs wick) | NO: big-trade volume is per bar only (b99_*/b999_*, :17-18); no per-price big-trade data | NO |
| D22 | L121-126 [4:44-4:55] | buyers took control | TRAIL: stop "covered below this low" (the pullback low, a higher low for a long); worst case day $10k, best > $25k | pullback low after buyer control; day worst/best case | PART: S6 = low of the last own control bar (:76-78); worst-case day P&L not tracked | v3-pending trail_update |
| D23 | L127-131 [4:59-5:07] | buyers stopped, sellers no result | mark "potential acceleration level"; HOLD | mutual no-result = micro balance | PART: S1 exists but is only used as an exit (S8b) in trade | NO |
| D24 | L132-136 [5:11-5:20] | sellers took control but stopped on big trades | RATCHET (take more profit off the table; worst case now $15k) | opposite control absorbed by big trades | NO | NO |
| D25 | L137-141 [5:20-5:31] | (teaching) | process: ratchet so the day's profit is not given back | day P&L | NO | NO |
| D26 | L142-146 [5:32-5:40] | market explodes from the level; aggression; failed auction | EXIT (closes the trade) | climax + failed auction at the extreme | PART: S8(a) big trades stop, S8(c) opposite control breaks S6 (:84-86); a failed auction at the extreme after a burst is not a defined exit | NO |
| D27 | L146-152 [5:40-5:55] | day type | ACCEPTS early exit: "day was pretty directional", could have made 40-50k; "prefer to be conservative" with a sniper trade | day type, size of open R | NO: no exit variant by day type or by open R | NO |
| D28 | L152-156 [5:55-6:06] | recap on the chart | first load + reload + reload; one protection level; "took all the bottom" | 3 entries, 1 stop anchor | PART: max 3 adds (:138) but after BE only | v3-pending |
| D29 | L157-167 [6:06-6:28] | after the exit the market "skyrocket up" | none; "best session" because small risk, big day | payoff skew | YES: top-10% share, day metrics (:190-193) | NO |
| D30 | L167-173 [6:28-6:40] | outro | none | - | n/a | n/a |

Tally of decision rows (D02-D29, excluding teaching rows D19/D25): YES 3 (D11, D16, D29; plus D10 for models A/C),
PART 10, NO 9, CONFLICT 4 (D07, D10 for model B, D12, D18).
Management rows (D09, D12, D14, D15, D17, D18, D20, D22, D24, D26, D27): 0 YES, 4 PART (D15, D17, D22, D26: only via the
distance BE, the own-side S6 trail or S8), 2 CONFLICT (D12, D18), 5 NO.

## 3. Trade blocks
### T1 - continuation shorts (loss side)
| field | reading |
|---|---|
| state | NY open, choppy (L18-19); no balance/imbalance detail |
| location / trigger | "continuation short" only; not described |
| side | SHORT, two attempts |
| stop / result | both failed; together with the chop, about $4,500-5,000 given back (L20-21) |
| after | he keeps trading, but under a floor: day P&L back to 0 = stop (L28-31) |
| missing for a sim | location, trigger, stop width, timestamps: UNKNOWN |

### T2 - long from a failed seller auction (the winner)
| field | reading | lines |
|---|---|---|
| state | chop phase over; consolidation where sellers were absorbed | L36-39 |
| location | the consolidation area / the level where sellers were absorbed | L38-39, L42 |
| trigger | failed auction of the seller, then buyer aggression at that level, with big trades | L40-42, L55-57 |
| side | LONG (a flip from T1's short) | L35-42, L156 |
| initial stop | behind "this level"; if it fails, get flat near BE fast; the lower seller-absorption level becomes the next pivot | L43-49 |
| stop width | UNKNOWN in points. Risk framed in $: only the day's profit (about $5k-10k at that time) | L60-63 |
| adds | "loading and scaling in", "continue to scale"; recap: first + 2 reloads; one protection level | L58-65, L152-155 |
| management 1 | own side fails again -> lower risk before the anchor is tested | L67-72 |
| management 2 | solid aggression -> stop up, risk $980 vs $25k potential | L74-77 |
| management 3 | pick between two cover levels; trail into profit on the next breakout of the level sellers protect | L88-96 |
| management 4 | consolidation in trade (buyers wall, sellers absorbed, buyers no result) -> plan: on breakdown be risk-free/tight | L97-106 |
| management 5 | sell acceleration stopped by aggressive buyers -> stop to zero | L110-116 |
| management 6 | buyers took control -> stop below this low; worst case day $10k | L121-125 |
| management 7 | sellers took control but stopped on big trades -> ratchet; worst case day $15k | L132-136 |
| exit | market explodes from the level, aggression + failed auction -> closed | L142-146 |
| rejected | holding for the directional day's full move (40-60k), in favour of locking a "sniper" trade | L146-152, L161-163 |
| information | big trades (and where in the candle), aggression, absorption per side, consolidations, defended levels, day P&L | throughout |

### Day P&L path (spoken numbers only)
London about +10k -> NY chop, gave back 4.5-5k -> T2 scaling while "up again 9,000 ... around 10,000" -> risk $980 for a
potential $25k -> worst case $10k -> worst case $15k -> closed (final figure not stated; "above $25,000" was the best case at
L125-126). Floor throughout: day P&L 0 (L28-31).

## 4. What the extract and the rulebook did to this video
| extract row (extract_fZlNGWvd2Ko.md) | verdict | what was lost or changed |
|---|---|---|
| R1 "Break-even daily stop" (:5-9) | DROPPED CONTEXT | The floor exists because London already made ~10k: NY trades only with the day's profit. FR-04 merges it with a generic "max daily risk" (1%, -3R in spec), which is a different rule |
| R2 "Failed auction plus buyer aggression" (:11-15) | ATOMIZED | Kept the trigger words but not the sequence: chop -> two failed shorts -> side flip -> sellers absorbed IN a consolidation -> buyers aggress. Direction relative to the pressure (long after SELLER pressure failed) is the key and is gone. FR-86 is a one-liner with "failed auction UNDEFINED" |
| R3 "Fast break-even when level fails" (:17-21) | DISTORTED | Rule says "move stop to BE immediately if the level fails; the failed level becomes the new pivot". Transcript: if THIS level fails, the LOWER level where sellers are absorbed becomes the new pivot (L45-50). It is a scratch-and-re-pivot plan, not a BE rule. FR-12 then merges it with 0jM5 "BE after first push", which is the opposite trigger (success vs failure) |
| R4 "Risk only the day's profit" (:23-27) | ATOMIZED | Correct words, but lost that this is the funding of loading/scaling while still at risk (L57-61). FR-05 "scale only on profit" makes it sound like adds after BE; spec 5.2 encoded exactly that |
| R5 "Cut when big trades get stopped" (:29-33) | DISTORTED | Lost the trigger ("buyers failed again", L67) and the action ("lower my risk", L68: de-risk, not cut or exit). Side of the big trade (a SELL print while long) dropped. FR-15 merges it with 0jM5 "big trades stop pushing" (exhaustion of OUR side), a different event |
| R6 "Trail stop in profit after breakout" (:35-39) | ATOMIZED | Lost the conditional: trail only on a breakout of the level the SELLERS are protecting, with two candidate cover levels (L89-96). FR-24 merges with 8CWK "trail aggressively" |
| R7 "Cover behind the new low" (:41-45) | INVERTED CLASS + WRONG GEOMETRY | "covered below this low" is a STOP placement (protection), filed as topic "target"; "new low in the trade direction" is wrong for a long: it is the pullback low under price. FR-87 inherits "target" |
| Unclear (:47-51) | DISCARDED DATA | "$980 to $25,000" dismissed as "not a rule": it is the only R data point in the video (about 1:25 open R) |
| not extracted at all | DROPPED | T1 losing shorts and the side flip (L23-26); in-trade consolidation plan (L97-108); stop to zero on sellers being stopped (L110-116); big trades "in the body of the candle" (L117-118); mutual no-result = acceleration level (L127-131); ratchet on opposite failure with worst-case day P&L $10k -> $15k (L121-136); exit reason, climax + failed auction (L142-146); the counterfactual on a directional day (L146-152); 3 entries + 1 protection level (L152-156) |

Net: 7 rows, of which 3 atomized, 2 distorted, 1 inverted in class/geometry, 1 context-stripped; 9 decision passages never
extracted. None of the 7 carries a sequence position, a side, or a trigger for a management action.

## 5. Patterns
### 5.1 The recurring decision sequence (this video, consistent with 0jM5/8CWK/jasv3L)
1. Balance / consolidation. 2. One side presses and is absorbed (effort, no result). 3. The other side aggresses at the same
level with big trades (effort, result) -> entry on the side that was NOT absorbed. 4. Initial stop behind the level; if the level
fails, scratch and re-pivot to the next absorption level. 5. In trade, re-run steps 1-3 on every pullback:
   - opposite side attacks and is absorbed -> stop to BE / ratchet to that pullback extreme;
   - our side attacks and fails -> de-risk (tighter stop or smaller size);
   - both sides no result -> micro-balance: hold, tight stop on the adverse edge, and treat the other edge as an acceleration level.
6. Exit on climax + failed auction in our direction, or on the stop. 7. Day accounting: the day's profit is the risk budget, the
floor is day P&L 0, the stop is framed as "worst case close for the day".
The same absorbed-vs-control primitive (S3) drives entry, BE, trail, de-risk and exit. In the spec it drives only entry filters,
S6 and S8(c).

### 5.2 Information he uses that we do not compute
| information | where in transcript | available in our bars? |
|---|---|---|
| which side was absorbed inside a balance (vs net pressure sign) | L36-39, L98-101 | yes: per-bar S3 absorbed counts inside W (fp, delta) - not defined |
| opposite side attack absorbed during the trade (event) | L110-116, L132-133 | yes: S3 absorbed == -s after entry - not defined |
| own side effort without result during the trade | L67-68, L117-119 | yes: S3 absorbed == s after entry - not defined |
| level the opposite side protects (resistance for a long) | L93-94 | partly: S6 of side -s / S3 absorbed of side s at a price - not defined |
| big trades inside the candle body vs wick | L117-118 | NO: b99/b999 are per bar, not per price bin (orderflow_bars columns, spec :17-18) |
| "buyers wall" (passive liquidity) | L98 | NO: L2 / heat map not in our data |
| day P&L across sessions, worst-case close of the day | L15-31, L124-136 | yes in a sim: needs cross-window day state |
| climax + failed auction at the extreme | L143-145 | yes: S4 burst + close back inside + S3 absorbed == s - not defined |
| day directional or not, used when choosing exit style | L147-148 | ex-post only (spec :165-166) |

### 5.3 Long vs short symmetry
- Fabio trades both sides in one session: two continuation SHORTS lose, then a LONG from a failed seller auction wins (L23-42).
  The three earlier applied readings were short trades; this is the first long. Nothing in the video suggests a different
  rule for longs; every management sentence is the mirror of the short-side language in 0jM5 ("if these aggressive buyers take
  back control, I want to be out", FABIO_TRADE_MODEL.md:26).
- Our models are sign-symmetric by construction (s = +1/-1 in S2-S8 and models A/B/C). The asymmetry is in the TRIGGER: S5 fires
  only when the break agrees with S2. A long that breaks out after seller pressure was absorbed (this trade) needs S2 = -1 and
  a break up, which no model accepts. Model B only half-covers it (probe outside the balance required). So the spec is
  symmetric in side but covers one of the two pressure-to-break relations.
- Proposal: report every stage-1 and stage-2 table split by side and by relation (break WITH pressure vs AGAINST absorbed pressure).

### 5.4 Missing pieces mapped to FABIO_V3_SPEC.md (proposals; the spec is not edited)
| # | missing piece | evidence | proposed change (section) |
|---|---|---|---|
| M1 | Event BE / ratchet on opposite-side absorption | L110-116, L121-125, L132-136 | 5.2: add `E_opp(i)`: in trade and S3(i).absorbed == -s. On E_opp: stop -> max(BE, extreme of the absorbed push -/+ TICK) (long: min l of the bars since the last own control bar). Keep `be_k*D` as the registered alternative. Needs new tests (mirror T31/T34). |
| M2 | De-risk on own-side failure | L67-72 | 5.2: add `E_own(i)`: S3(i).absorbed == s. Action (grid, 2 cells): stop -> last S6 of side s, or close 50% taker. Not an exit. |
| M3 | In-trade balance is hold-or-exit by who was absorbed | L97-108, L127-131 | S8(b) (:85): exit only if the new balance has S2 == -s or its absorbed bars are of side s; if the absorbed side is -s, HOLD and set stop to max(stop, balance adverse edge - s*TICK). |
| M4 | Break against absorbed pressure (failed auction entry) | L36-42 | 3 (S5) + 4: new S5' = s if S2(i-1) == -s (pressure absorbed: any S3 absorbed == -s in W) and close beyond E_s with S4(s). New model D "failed-auction trend" (or model B variant without the outside-probe requirement), managed like A: no fixed target. Registered trials. |
| M5 | Model B target | L50-52, L142-162 | 4 (:111): add variant "B-trail": no fixed target, section 5.2 management + S8. Registered trial. |
| M6 | Exit on climax + failed auction | L142-146 | S8 (:82-87): add (d): within the last m bars an S4 burst and a new extreme, then a close back inside the prior bar range with S3 absorbed == s. Trial vs hold-to-trail, split by ex-post day type (D27 shows it cost the tail on a directional day). |
| M7 | Day budget across sessions, floor at 0 | L15-31, L60-61, L124-136 | 6: carry closed day R across London and NY windows; if closed day R > 0 at the window open, first-leg risk <= closed day R and no new first legs once closed day R <= 0. Report worst-case day R (closed + open at stops) per bar. Adds before BE allowed iff total open risk <= closed day profit (resolves open item 12.1 as a registered trial). |
| M8 | Trail on the break of the opposite defended level | L88-96 | 5.2: trail candidate = the price of the last S3 absorbed == s bar (where our side was stopped, i.e. the level sellers protect for a long); stop -> previous S6 only after a close beyond that level. Variant of the current S6 trail. |
| M9 | Scratch and re-pivot | L43-50 | 4: after a first-leg stop-out or scratch within k bars, allow one re-entry at the next S3 absorbed == -s level below (long) with the same budget. Registered trial; counts toward the 10 first legs (:159). |
| M10 | Big trades by price inside the bar | L117-118 | 1 (data): add per-bin big-trade volume to the fp string or a new column in orderflow_bars. Data item, not a v3 change. |

## 6. Verbatim quotes (in transcript order)
> "we came from a London session where we did pretty good amount of profit. That was around $10,000"
**Source GPS: fZlNGWvd2Ko | BEGIN** (L15-17, [0:35]-[0:41])

> "we start the session getting caught by a little bit of choppiness here. So we give back $5,000 to the market, around 4,500."
**Source GPS: fZlNGWvd2Ko | BEGIN** (L18-21, [0:43]-[0:51])

> "The first trades that we took was a continuation short and we gave back two trades inside here. We tried this continuation and we failed."
**Source GPS: fZlNGWvd2Ko | BEGIN** (L23-26, [0:57]-[1:03])

> "the trades that we continue to take with a maximum drawdown that is break even. So if we go back to break even, we stop the session."
**Source GPS: fZlNGWvd2Ko | BEGIN** (L27-31, [1:09]-[1:15])

> "this consolidation area got completely wrecked by buyers that took control. The sellers got absorbed here."
**Source GPS: fZlNGWvd2Ko | BEGIN** (L36-39, [1:26]-[1:33])

> "capitalize on the failed auction of the seller and then aggression of the level of the buyers."
**Source GPS: fZlNGWvd2Ko | BEGIN** (L40-42, [1:36]-[1:41])

> "I will be really fast in putting my position to break even if this level failed, okay? Because if this level failed, this one become the new pivot"
**Source GPS: fZlNGWvd2Ko | BEGIN** (L43-46, [1:43]-[1:49])

> "I want to try uh good risk to reward trades and amazing risk to reward trades to take the top of the day."
**Source GPS: fZlNGWvd2Ko | BEGIN** (L50-52, [1:57]-[2:02]; "top" for a long reads as the day's high as the target)

> "I'm loading and scaling in position trying to get my losses smaller and smaller."
**Source GPS: fZlNGWvd2Ko | BEGIN** (L58-59, [2:19]-[2:24])

> "I'm only risking the profit of the day, okay? I'm not risking more."
**Source GPS: fZlNGWvd2Ko | MIDDLE** (L60-61, [2:24]-[2:29])

> "buyers failed again. So I want to lower my risk because if this big trade sell gets stopped out, I don't want to be in the position because we will have a really fast snapback of the market."
**Source GPS: fZlNGWvd2Ko | MIDDLE** (L67-72, [2:41]-[2:52]; which way the snapback goes is ambiguous in the caption; the action, lower risk, is not)

> "the market gives a really solid aggression. My risk goes really low and now I'm risking $980 to make potential $25,000"
**Source GPS: fZlNGWvd2Ko | MIDDLE** (L74-77, [2:55]-[3:03])

> "you can cover behind this level, you can cover behind this level. The buyers took complete control. You can see all these big trades. And you can see that sellers are trying to protect this level. So if we have another breakout, we can trail our stop in profit."
**Source GPS: fZlNGWvd2Ko | MIDDLE** (L89-96, [3:32]-[3:47])

> "we have a buyers wall, they try to push down. The sellers got completely absorbed here and the buyers are not making results in this case. So it's a consolidation area where if we break down this level, I want to be risk free or with a really tight stop loss because if we break down this level, we will probably revisit this level here."
**Source GPS: fZlNGWvd2Ko | MIDDLE** (L97-106, [3:49]-[4:11])

> "the market did a really good acceleration of the sell and stop before these aggressive buyers. Now my position is stop loss to zero. Why? Because we already saw that the sellers got stopped again in the movement and buyers are starting to continue up."
**Source GPS: fZlNGWvd2Ko | MIDDLE** (L110-116, [4:20]-[4:36])

> "big trades in the body of the candle. Again, another effort but still no result."
**Source GPS: fZlNGWvd2Ko | END** (L117-119, [4:36]-[4:40])

> "the buyers took control. Now I'm covered below this low and I'm getting a little bit of profit for the market. So the worst case scenario, I close $10,000."
**Source GPS: fZlNGWvd2Ko | END** (L121-125, [4:44]-[4:52])

> "buyers stopped here. So no result from the buyers but also no result from the sellers. This is a potential acceleration level here"
**Source GPS: fZlNGWvd2Ko | END** (L127-131, [4:59]-[5:07])

> "Again, sellers took control but stopped on these big trades. So I can take other profit from the market. Now the worst case scenario, we close $15,000 for the day."
**Source GPS: fZlNGWvd2Ko | END** (L132-136, [5:11]-[5:20])

> "this is a way to get back your profit from the market as soon as possible and not give back the profit that you make to the market."
**Source GPS: fZlNGWvd2Ko | END** (L138-141, [5:24]-[5:31])

> "the market explode from this level. You see all these aggression and a failed auction and this is the reason I closed my trade."
**Source GPS: fZlNGWvd2Ko | END** (L142-146, [5:32]-[5:40])

> "I remember that the day was pretty directional here."
**Source GPS: fZlNGWvd2Ko | END** (L146-148, [5:40]-[5:44])

> "I could have made 40, 50,000 dollar session but I prefer to be conservative when I have a really good sniper trades."
**Source GPS: fZlNGWvd2Ko | END** (L149-152, [5:47]-[5:55])

> "we loaded the first one here, then we reloaded here, then we reloaded here and this one was our protection level. So we took all the bottom of the up session of the day."
**Source GPS: fZlNGWvd2Ko | END** (L152-156, [5:55]-[6:06])

> "We risk a really small amount of money to make a really banger day."
**Source GPS: fZlNGWvd2Ko | END** (L165-167, [6:22]-[6:30])

## 7. Ambiguities (kept open, not resolved by guessing)
1. L69-72 "if this big trade sell gets stopped out ... fast snapback": either (a) the big SELL print is the trapped side whose
   stop-out would squeeze up (then de-risking is odd), or (b) his anchor is the level that print tested and its failure would
   snap price down through his stop. The action (lower risk) is unambiguous; the reason is not. Do not turn it into a rule.
2. L58-59 "scaling in ... losses smaller and smaller": reload prices relative to the first entry are not stated. "took all the
   bottom" (L156) and the timing (reloads narrated before stop-to-zero at L113) suggest reloads near the base, while still at
   risk. Whether they were adverse (lower) or with the move is UNKNOWN; MISSING_PIECES H2 (adverse ladders) stays untested.
3. L134 "take other profit": either a partial close or a stop ratchet. The next sentence (worst case $15k) fits a ratchet;
   a partial is possible.
4. L52 "take the top of the day" in a long: read as "ride to the day's high". Not a short.
5. Final day P&L: not stated. 40-50k (L149) and 50-60k (L162) are counterfactuals, spoken, inconsistent with each other.
6. Instrument: not named in this transcript.
