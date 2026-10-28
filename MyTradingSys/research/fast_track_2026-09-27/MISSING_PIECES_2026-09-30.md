# MISSING PIECES - why our trader extractions do not become tradeable rules (Opus research, 2026-09-30, cloud sandbox)

Scope: Fabio first, then Tom. One applied reading each, three operator hypotheses (H1-H3). Fabio and every other system stay
separate layers; nothing here proposes a filter on Tom (PROJECT_VISION.md:94 "Tom is core ... Modules never gate core behavior").
**Data status:** no market data was used. Every exchange host was refused by the egress policy with a 403 on CONNECT (proxy status
2026-09-30 17:06Z): data.binance.vision, fapi.binance.com, api.binance.com, www.deribit.com, test.deribit.com, api.bybit.com,
api.exchange.coinbase.com, api.kraken.com. The repo holds no BTC price series (only monitor CSVs). Section 4 therefore has
**algebra and synthetic-path MODEL results only, not backtests**. Scripts: scratchpad `opus_rearch/h1_costs.py` and `h2_ladder.py`
(outside the repo). Trial count is in section 4.4.

## 0. Answer (ranked missing pieces)
1. **Our unit of extraction is the rule. The unit of edge is the trade, and for Fabio it is the whole day.** Both traders' trades
   pay many small losses for a rare large winner. Fabio's worst day had a streak of stops, about -9k, and then one 1:20 trade.
   Tom's trade risked 12 ticks to make 97. The rule rows keep none of this, and our gates and simulators cut off exactly that
   right tail. Tom's target window is [2.0, 3.5]R, and the net >= 2 gate raises the floor to 2.67R. The Fabio sim caps targets at
   3R. The MTS plan rules forbid breakeven and trailing stops.
2. **Tom's stop is in the wrong place, and its width ignores costs.** The engine puts the stop at the swing extreme, with a 0.2%
   fallback. Tom says the stop "doesn't belong above the high". The median stop in TOM_CORE_BT is exactly 0.200% in every variant,
   which is consistent with the fallback doing most of the work. The friction model takes a flat 25% off gross R:R whatever the
   stop width. At 0.2% the real round-trip fee is 0.25-0.5R.
3. **Nobody checks portability at extraction time.** A 12-tick ES stop is about 0.04%. At Deribit costs every BTC stop-out that
   tight costs at least 1R in fees. The trade survives only with maker entries and an R:R of about 8.
4. **Entry mechanics are inverted.** Both traders rest limit orders before the touch. Our pipelines enter after confirmation: Tom
   needs proof >= 5 at the zone, and the Fabio limit is placed after the trigger bar.
5. **Day-type state is missing.** Compression vs trend day, dealer gamma, inside day and weekly balance exist as rule rows, but none
   was built into a measurable state. The trader uses that state to turn the trend model on or off.
6. **One-quote extraction corrupts rules.** FAB-jasv3L-d8ZE-R5 is probably inverted (section 1). DSA task 999 is ticked with no
   output. A third Fabio model (IVB, the first 30 min of the cash session) was never picked up as a model.

Hypotheses:
- **H1:** a wider stop does not create edge. Under a driftless null gross expectancy is 0 at any width. But it cuts fee drag from
  0.67R at a 0.15% stop to 0.10R at 1.0% (3R target, taker entry), in exchange for a lower R:R when the target is a fixed level.
  It is worth testing on real MAE/MFE.
- **H2:** adding against the move raises win rate and leaves expectancy unchanged under a random walk. The worst-case loss is
  2.3-3.3x the first-rung risk, and the ladder loses to single entries under trend drift. It helps only if BTC mean-reverts at the
  ladder's scale. It is the opposite of Fabio's practice. Not recommended until H3 stage 2 measures mean reversion.
- **H3:** a sound protocol. The one earlier session test (C2) anchored a fixed 13:30 UTC with no DST adjustment and held 24 h with no
  stop, so it did not test the trader's trade. Design is below; nothing was run.

## 1. Fabio applied reading: jasv3L-d8ZE ("worst trading session of the month")
**Why this one.** Both applied readings so far (0jM5Y31YJak, 8CWKfoSJu3c) are best-case sessions. The model needs the loss side too,
and this is the only held Fabio video that walks a live losing day end to end, from drawdown to recovery.
- Rejected: 0KyIEdvVKMQ (interview and mindset), FawPrRUGNpk (liquidity lecture), LQvv5xgy_ik (risk-management lecture) and
  fZlNGWvd2Ko (best session of October, the same pattern as 0jM5).
- fZlNGWvd2Ko and LQvv5xgy_ik are used only as cross-checks. The Fabio transcripts carry `[m:ss]` stamps, and the GPS tags follow
  `verify_extract_quotes.py`.

### 1.1 Trade reconstruction (template of section 3.2)
| field | reading |
|---|---|
| market / session | NQ futures, NY session (a price level of 24,932 is quoted; no BTC anywhere, FABIO_BTC_RESEARCH:15-17) |
| day type | compression all session. He names it the worst condition for his strategy, and his trend model takes a streak of stops |
| location | a horizontal range low (24,932) tested again and again; each test weakens it ("wall") |
| leading signal | seller volume building inside the range, big short positioning, dealer gamma (long gamma = compression) |
| trigger | break of the range low with aggressive sellers |
| initial stop | $600 on the add ("Set up here the stop loss $600", [4:02]). Width in points is not stated, so stop % is UNKNOWN |
| management | risk to about zero first, then add 2 contracts WITH the move, stop to zero, stop into profit, lock the gain |
| exit | protective stop in profit as sellers re-engage; flat at +12k floating; stops for the day |
| day P&L shape | about -9k from a streak of stops, recovered by one trade of about 1:20; closes positive (spoken totals conflict: 2,330 vs 10,000) |
| horizon | whole session; one short held from before the video midpoint to the end |
| does NOT | trend-follow on compression days; overexpose in drawdown; keep trading after the recovery |
| portability | stop width unknown, so no cost ratio. Payoff geometry: a stop streak plus one fat winner, so it must be evaluated per day |

Verbatim quotes:
> "Every movement got absorbed in the first two hours. This is the worst market condition you can get for my strategy."
**Source GPS: jasv3L-d8ZE | BEGIN** ([0:07]-[0:18])

> "So my trend following model took a straight stop loss. We are at $9,000 in draw down for the day."
**Source GPS: jasv3L-d8ZE | BEGIN** ([1:42]-[1:47])

> "Today there is a lot of volume. So I need to bigger filter."
**Source GPS: jasv3L-d8ZE | BEGIN** ([1:17]-[1:22])

> "The only positive stuff is that with this movement, I can put risk to almost zero."
**Source GPS: jasv3L-d8ZE | BEGIN** ([3:39]-[3:44])

> "We can scale other two contract here on the way down."
**Source GPS: jasv3L-d8ZE | BEGIN** ([3:51]; this is a short, so "on the way down" is WITH the move)

> "if we can break this low, this horizontal level, probability that we go down it's exponential."
**Source GPS: jasv3L-d8ZE | MIDDLE** ([5:07]-[5:15])

> "every time you hit it gets weaker and weaker"
**Source GPS: jasv3L-d8ZE | MIDDLE** ([6:18]-[6:26])

> "Look at this 18 contract from the top with risk-to-reward 1 to 20."
**Source GPS: jasv3L-d8ZE | END** ([8:44]-[8:55])

> "Now the market maker are long gamma. So they will try to compress volatility."
**Source GPS: jasv3L-d8ZE | END** ([9:18]-[9:24])

> "we locked in $12,000 and we are out of the position."
**Source GPS: jasv3L-d8ZE | END** ([10:28])

> "take what the markets gives you is not the day to trade trend following."
**Source GPS: jasv3L-d8ZE | END** ([11:48]-[11:53])

Cross-checks:
> "in the worst session that I can make, I lose around 5,000, 10,000."
**Source GPS: fZlNGWvd2Ko | MIDDLE** ([3:10]-[3:13])

> "the best session of the month it's two times and a half bigger than the worst session of the month."
**Source GPS: fZlNGWvd2Ko | MIDDLE** ([3:16]-[3:23])

> "the bottom of the first 30 minutes is giving a lot of value in the direction of the day"
**Source GPS: LQvv5xgy_ik | END** ([31:53]-[31:57], "the IVB")

### 1.2 What is NEW compared with FABIO_TRADE_MODEL.md
1. **The loss side belongs to the model.** On balance days the trend model is expected to take a stop streak. The edge only shows
   up per day: his best day is about 2.5x his worst day (fZlNGWvd2Ko). Per-trade win rate and per-trade kill criteria will judge
   this model wrongly. Evaluate daily P&L, with the drawdown before the winner.
2. **Day-type classifier, including dealer gamma.** He keys "not the day to trade trend following" to compression and to market
   makers being long gamma. FR-89 and FR-91 hold these as CONTEXT rows with no threshold (FABIO_RULEBOOK.md:93,95,161-162). For BTC,
   dealer gamma can in principle be built from Deribit BTC options, our own venue. Whether historical options OI is available on F:
   is unknown.
3. **The big-trade threshold adapts within the day** ("need bigger filter" on a high-volume day). S4 in FABIO_TRADE_MODEL.md:36
   uses a 30-day percentile only.
4. **Adds come after risk is at zero, not only after profit.** He moves the stop to zero and then adds in the direction of the move.
   The model already says he adds on confirmation and never low in the curve (FABIO_TRADE_MODEL.md:17-19). This sharpens the order:
   first the stop goes to breakeven, then he adds.
5. **Session stop after recovery.** He quits once the drawdown is recovered, even though flow still confirms. The rulebook row for
   this looks inverted (next item).
6. **Extraction error.** FAB-jasv3L-d8ZE-R5 reads "Do not cut profit early on choppy days" and quotes "it's always bad to cut in
   profit and stop the day because ... your focus lowers" (extracts/processed/fabio_valentini/jasv3L-d8ZE/extract_jasv3L-d8ZE.md:29-32).
   His action (he locks in and stops, [10:28]), his stated reasons (focus drops, positive gamma compresses) and his conclusion
   ([11:53]) all say to cut and stop. The word "bad" is very likely a slip or a caption error. FR-90 inherits the inversion.
7. **A third model and two risk geometries.** IVB means first-30-min direction (LQvv5xgy_ik [31:42]-[31:57]; also StaphlRH8NQ [7:26]-[8:16],
   whose speaker attribution is disputed at FABIO_BTC_RESEARCH:16). It rests on equity upside skew, so it may not port to BTC.
   Separately, LQvv5xgy_ik [10:58]-[11:08] prescribes a high-win-rate 1:1 geometry for prop accounts and "sniper" R:R for personal
   accounts. Our Fabio tests never said which geometry they emulate.

## 2. Tom applied reading: yRvMW6lgN1o ("I risk $250 to earn $1,212")
**Why this one.**
- It is on Tom's channel (extracts/fresh/extract_yRvMW6lgN1o_fresh.md, channel @tom_vorwald_en).
- It is one live trade walked end to end. It states risk and result, stop and target in ticks, and the order type of both legs.
- It has no applied reading; "applied reading" appears only in FABIO_TRADE_MODEL.md and SUPERVISOR_LOG.md.
- Rejected: tS6ZEiHj8gQ (conceptual short after a squeeze), n7ZSkjb7JXs (pre-market DAX, mostly commentary), 4MoNjEQ2Dd8 (a
  multi-trade session, 4.3k words).
- The transcript has no timestamps, so the GPS tag is the third of the file.

**Instrument (inference, not stated).** The levels 6,763/6,768 and the 2025-11-19 publish date fit S&P 500 futures. If that is
ES (tick 0.25): stop 12 ticks = 3 pts, about 0.044% of 6,790; target 97 ticks = 24.25 pts, about 0.36%; R:R 8.1. The money figures
(EUR 250 risk, EUR 1,212 won = 4.85R) do not match 8.1R, so either the size or the risk base differs. Numbers below use ticks.

### 2.1 Trade reconstruction
| field | reading |
|---|---|
| market state | weekly profile shows a range after a trend ("trend now seems to be flattening out"); inside day; all-time high pre-market |
| location | "smart" support and resistance, built from value areas plus older single prints grouped into zones; upper boundary = the highest equilibrium of the last 2 days in context with the VAHs |
| leading signal | the market heads down with a spike that shows volume stability below |
| trigger | a RESTING sell limit "right below the last volume step" of the profile, placed in advance; "we let the market decide" |
| initial stop | inside the range at the largest-volume footprint level, NOT above the high; 12 ticks (about 0.04% if ES) |
| target | prior-week POC area (6,763-6,768), 97 ticks, 8.1R; an optional "quick hands" partial at yesterday's POC, which he calls not optimal |
| management | none: set and forget; entry and exit both limit orders |
| exit | target limit |
| horizon | "intraday swing trade" on a 5m chart; explicitly not a short-term trade |
| does NOT | stop above the high; chase; need a high hit rate ("lose four to five trades ... and still make money") |
| portability | a 0.044% stop on BTC: maker entry plus taker stop-out costs 0.05%/0.044% = 1.1R. Breakeven win rate at 8.1R about (1+1.1)/(8.1+2.1) = 21%, which is near his own "lose 4-5 and still make money" (about 17-20%). Viable only if the stop scales to BTC volatility and entries stay maker |

> "In this trade, I entered with a limit order and simply had a sell order here."
**Source GPS: yRvMW6lgN1o | BEGIN**

> "we had a so-called inside day trading completely within the previous day's range."
**Source GPS: yRvMW6lgN1o | BEGIN**

> "these smart support levels are simply a combination of the value areas and the corresponding single print areas from the past."
**Source GPS: yRvMW6lgN1o | BEGIN**

> "I would place a limit order specifically right below the last volume step of the corresponding price profile"
**Source GPS: yRvMW6lgN1o | MIDDLE**

> "It doesn't belong above the high. Why is that? I can explain that to you very clearly as well. Because the probability of a strong acceleration above the high is always high."
**Source GPS: yRvMW6lgN1o | MIDDLE**

> "This is a so-called intraday swing trade, and I'm going to let it run."
**Source GPS: yRvMW6lgN1o | END**

> "theoretically you can lose four to five trades with this trading style and still make money."
**Source GPS: yRvMW6lgN1o | END**

> "with a stop-loss up here, we now have a risk of 12 ticks. We have a profit of 97 ticks."
**Source GPS: yRvMW6lgN1o | END**

> "Both were done with limit orders. So you could have basically ignored the market"
**Source GPS: yRvMW6lgN1o | END**

Consistent elsewhere: TOM-094 "stop loss ... 10 ticks ... profit run ... 70 ticks ... riskreward ratio of seven"
(TOM_VERBATIM_INDEX.md:107); TOM-099 "risk reward ratio is gigantic" (:112). The small-stop, large-R:R, limit-order geometry is
Tom's normal trade, not a one-off.

### 2.2 Mapping to the verdict.py / SetupCandidatesBuilder gates
| Tom field | our gate (file:line) | verdict |
|---|---|---|
| state: weekly balance, inside day | classifyState/determineDirections (SetupCandidatesBuilder.java:57-61); no inside-day or weekly-balance field | MISSING |
| location: grouped VA + single prints | zones = VP levels, swings, naked POC, VWAP, FVG (Java:340-430); no single prints, no composite grouping, no "last volume step" | MISSING |
| entry: resting limit, pre-placed | tier trigger_ready <= 0.1% (Java:71), then proof >= 5 (verdict.py:116-121), then a limit at the zone (MTS_USER_GUIDE.md:172-173) | OVER-FILTER / LATE: proof requires the reaction to have already happened |
| stop: inside, at max-volume level, not above the high | short stop = swing high (above); fallback zone x 1.002; floor 0.1% resets to 0.2% (Java:111-124) | CONTRADICTS Tom |
| target: 8R to prior-week POC | nearest level with distance in [2.0, 3.5] x risk, else the candidate is dropped (Java:149-176) | OVER-FILTER: his trade is outside the window |
| R:R gate | net = gross x 0.75 >= 2.0 (Java:182-184; ExecutionMathConstants.java:34; verdict.py:110-111), so gross must be in [2.67, 3.5] | MIS-SPECIFIED: friction does not depend on stop width |
| proof count | 7 one-minute proofs; book imbalance cannot be rebuilt, so max 6 (TOM_CORE_BT.md:14) | NOT HIS TRADE: he uses footprint to place the stop, not to count proofs |
| management | fixed stop, no trail, no BE (MTS_USER_GUIDE.md:151) | MATCH |
| horizon | sim timeout 12 h (sim.py:31) | MATCH |

Code facts behind the verdicts (read from code, not docs):
- **WAIT_RR is partly a selection artefact.**
  - The target chosen is the NEAREST level inside [2.0, 3.5]R (Java:154-170).
  - WAIT_RR then fires whenever that nearest level sits in [2.0, 2.67)R, even when a farther level in [2.67, 3.5]R would pass.
  - Of 120,892 snapshots, 80,847 were WAIT_RR (TOM_CORE_BT.md:14). Nearest-first selection alone biases toward it, and any
    target past 3.5R is never considered.
- **The stop is mostly the fallback.**
  - The median stop distance is 0.200% in all four variants (TOM_CORE_BT.md:84, 331, 461). That equals the fallback and floor-reset
    value (Java:113, 116, 123).
  - So the backtest largely measures an arbitrary 0.2% stop, not Tom's stop. The fallback share needs counting on F: data.
  - At 0.2%, fees are 0.22-0.23R per trade (TOM_CORE_BT.md:84, 331), which matches the H1 table (0.25R per stop-out with a maker
    entry).
- **The null result fits a geometry problem.** Random entries with the same stop and target are at least as good as the setups
  (p(null >= real) = 0.995, TOM_CORE_BT.md:343). With a 0.2% stop and a 2.7-3.5R target, location barely matters to the outcome;
  noise decides.

**DSA task 999.**
- It is ticked at DSA_BACKLOG.md:16. DSA_GATE_LOG.md (6 lines) has no 999 row, and no merged master list exists.
- The 16 rules are real: 7 in extracts/processed/tom/new_selected_10/extract_WQ_OAdz-PJ8.md and 9 in extract_zAwEX_tRUfE.md.
- It matters for this reading. T-zAwEX_tRUfE-R5 ("stop below the last low on 1-minute often gives reward-to-risk below 1") and
  R8 ("exit on re-acceptance of old equilibrium") bear directly on the stop and exit contradictions above, and they are invisible
  to builders reading the master list.
- Recommendation: untick 999 until it has output and a gate row.

## 3. Gaps: why rule synthesis fails (pipeline level)
### 3.1 Causes, with evidence
| # | cause | evidence |
|---|---|---|
| G1 | unit = rule, not trade | FABIO_RULEBOOK.md:3 columns (rule/topic/class/data/overlap): no sequence, stop width, horizon, order type or payoff |
| G2 | rules become AND gates | Fabio signal stack (FABIO_BTC_RESEARCH:50-51); Tom 19 SETUP_FORMING in 4.7 y (TOM_CORE_BT.md:14) |
| G3 | right tail cut | Fabio target min(3R, HVN) (FABIO_BTC_RESEARCH:47-49); Tom window 3.5R (Java:151); plan rules forbid BE/trail (MTS_USER_GUIDE.md:151) |
| G4 | cost vs stop never checked | flat 25% friction (ExecutionMathConstants.java:34); two fee sets in repo: sim.py:18-20 taker 5 bps / maker 0 ("verified 2026-09-26 via public/get_instrument"), fabio_of_model.py:40-44 taker 3.5 / maker -1.5 bps (from T055b "internal arithmetic", T055b_PROVEN_SETUPS.md:20-24) |
| G5 | entry after confirmation | Tom proof >= 5 before entry; Fabio limit armed after the trigger bar (FABIO_BTC_RESEARCH:43-46) |
| G6 | context state unbuilt | FR-89/91 no threshold (FABIO_RULEBOOK.md:161-162); no inside-day or weekly-balance field in Tom |
| G7 | one-quote rules lose meaning | FAB-jasv3L-d8ZE-R5 inversion (1.2 item 6) |
| G8 | walkthroughs are best-case | 0jM5 and 8CWK are both winning sessions; losing sessions never reconstructed |
| G9 | instrument scale ignored | Tom and Fabio stops are ticks on ES/NQ/DAX; ours are % of BTC. Portability needs stop / ATR(trader's TF) and cost / stop |
| G10 | no null at design time | Tom real <= random null (TOM_CORE_BT.md:343, 473) |
| G11 | wrong session anchor | C2 session start = UTC day + fixed minutes (session_momentum.py:29), no DST; PROJECT_VISION.md:105 requires a DST-aware US cash open |

### 3.2 Verdict on the extraction template: KEEP "trade reconstruction", with 7 additions
The operator's fields (market state, location, leading signal, trigger, stop %, management, exit, day selection, horizon, does NOT,
portability) found the stop and target contradiction and the payoff shape above, which the rule rows missed. Add:
1. **Instrument line:** name, tick value, stop in ticks and in ATR(the trader's chart TF). Percent alone does not port.
2. **Order type per leg** (maker/taker), and when the order was placed (before or after the touch).
3. **Outcome:** R won or lost; for multi-trade sessions, every trade plus the day P&L and day type.
4. **Gate replay:** what verdict.py or our layer would have done with this trade (entered? stop? target?).
5. **Portability arithmetic:** breakeven win rate at Deribit costs, using the fee source of truth once G4 is fixed.
6. **Ambiguity flags:** quotes whose literal words contradict the action (as R5 does).
7. **Coverage rule:** each trader needs at least 1 losing session reconstructed per 2 winning ones.

The rule rows stay as an index into reconstructions, not as the spec builders implement. Builders get the trade (sequence) plus
one measurable definition per field.

## 4. Hypotheses
### 4.1 H1 wider stop
**Design (full test, needs F: data).**
- Replay one MAE/MFE surface per event: for each Tom WATCH/SETUP episode (n = 4,849 signals) and each Fabio S5 event, record the
  path to the horizon.
- Evaluate every stop and target combination from that surface without re-simulating:
  - stops 0.15, 0.3, 0.5, 0.75, 1.0, 1.5% and ATR(tf) x 0.5, 1, 2, 3;
  - targets: fixed level, fixed R, trail;
  - entry: maker or taker.
- Report for each cell: survival (not stopped by the horizon), target-hit rate, expectancy net in R and USD, and the R:R actually
  realised.
- Report the same-geometry random null for each cell. Register the whole grid up front (about 60 cells) and apply DSR/PBO.

**What ran (MODEL; RESULT 2026-09-30, cloud sandbox, no market data; algebra plus a driftless Brownian null).**
- Costs, base: sim.py (taker 0.05%, maker 0). Opt: fabio_of_model.py (3.5 / -1.5 bps). Stress: base + 2 bps per taker leg.
- The null win probability for a target at distance T and stop at s is s/(s+T).

A. Fixed 3R target (MTS style), base costs:
| stop % | fee R per stop-out (maker in / taker in) | breakeven win % (maker in / taker in) | null win % | null net R (taker in) | notional for 25 USD risk |
|---|---|---|---|---|---|
| 0.05 | 1.00 / 2.00 | 40.0 / 60.0 | 25.0 | -1.75 | 50,000 (above the 10,000 cap) |
| 0.15 | 0.33 / 0.67 | 30.8 / 38.5 | 25.0 | -0.58 | 16,667 (above the cap) |
| 0.30 | 0.17 / 0.33 | 28.0 / 32.0 | 25.0 | -0.29 | 8,333 |
| 0.50 | 0.10 / 0.20 | 26.8 / 29.3 | 25.0 | -0.18 | 5,000 |
| 0.75 | 0.07 / 0.13 | 26.2 / 27.9 | 25.0 | -0.12 | 3,333 |
| 1.00 | 0.05 / 0.10 | 25.9 / 27.2 | 25.0 | -0.09 | 2,500 |
| 1.50 | 0.03 / 0.07 | 25.6 / 26.4 | 25.0 | -0.06 | 1,667 |

B. Fixed target LEVEL 1.5% away (Tom/Fabio style); widening the stop shrinks R:R. Taker entry.
| stop % | R:R | breakeven win % base / opt / stress | null win % | skill needed above null (pp, base) | null net R |
|---|---|---|---|---|---|
| 0.15 | 10.0 | 14.7 / 12.9 / 16.9 | 9.1 | +5.6 | -0.64 |
| 0.30 | 5.0 | 21.6 / 20.0 / 23.5 | 16.7 | +5.0 | -0.31 |
| 0.50 | 3.0 | 29.3 / 27.8 / 30.9 | 25.0 | +4.3 | -0.18 |
| 0.75 | 2.0 | 37.0 / 35.7 / 38.4 | 33.3 | +3.6 | -0.11 |
| 1.00 | 1.5 | 43.1 / 42.0 / 44.4 | 40.0 | +3.1 | -0.08 |

(A 0.75% target level gives the same pattern: at a 0.3% stop, skill needed is 7.8 pp; at 0.5%, 6.2 pp.)

C. Survival: P(stop touched within the horizon), driftless, with an ASSUMED sigma_day of 2% (3% in brackets). Replace with the
measured value.
| stop % | 15m | 1h | 4h | 24h |
|---|---|---|---|---|
| 0.15 | 46 (62) | 71 (81) | 85 (90) | 94 (96) |
| 0.30 | 14 (33) | 46 (62) | 71 (81) | 88 (92) |
| 0.50 | 1 (10) | 22 (41) | 54 (68) | 80 (87) |
| 1.00 | 0 (0) | 1 (10) | 22 (41) | 62 (74) |

**Verdict H1: PARTLY SUPPORTED as a cost fix; NOT an edge source.**
- Widening from 0.15% to 1.0% cuts fee drag per stop-out from 0.67R to 0.10R.
- Against a fixed level target, it lowers the directional skill needed above the null only modestly (5.6 to 3.1 pp), because R:R
  falls from 10 to 1.5.
- Survival rises steeply with width. Under the assumed volatility, a 0.15% stop is touched within 1 h about 71-81% of the time.
- Whether survival turns into target hits is an empirical MAE/MFE question.
- **Floor rule for every layer:** stop >= about 0.3% (fee <= 0.33R with a taker entry), unless both entry and target are maker and
  the planned R:R is >= 8.

Risks:
- The null is continuous-time. Real bars add gap and slippage.
- sigma is assumed.
- Plan cap: 25 USD risk cannot be sized below a 0.25% stop without breaching the 10,000 USD notional cap (MTS_USER_GUIDE.md:149).

### 4.2 H2 scaling into adverse moves
**Geometry (algebra, inverse-contract USD PnL per FORMULAS.md 11.6, average entry per 11.4).**
- Long, hard stop 1.0% below the first entry.
- Adds at -0.33% and -0.67% of the first entry.
- All sizes are multiples of 10 USD, as the plan rules require.

| ladder | total USD | avg entry vs first | stop distance from avg | breakeven distance from last rung | loss at hard stop, all filled | x first-rung-only loss |
|---|---|---|---|---|---|---|
| single 10 | 10 | 0 | 1.00% | - | 0.100 USD | 1.00 |
| 10+10+20 | 40 | -0.417% | 0.585% | +0.251% | 0.234 USD | 2.34 |
| 10+20+30 | 60 | -0.445% | 0.557% | +0.223% | 0.334 USD | 3.34 |

**Model (MODEL, RESULT 2026-09-30, cloud sandbox, synthetic 1m paths, 24 h horizon, sigma_day ASSUMED 2.5%, n = 4,000 paths per row).**
- Fees: entries and targets maker 0; stop and time exits taker 5 bps.
- R = the loss at the hard stop with every rung filled. For the confirmation ladder, R = the first-rung risk.
- Target: average entry +0.3%, re-armed after each fill.
- conf_112 adds WITH the move at +0.33% and +0.67%. Its stop moves to entry, then to +0.33%. Its target is +2%.

| process | strategy | win % | mean R [95% CI] | avg win / avg loss R | P(-20R within 200 trades) |
|---|---|---|---|---|---|
| random walk | single 40 | 76.1 | -0.022 [-0.040, -0.004] | +0.30 / -1.05 | 0.054 |
| random walk | adverse 10+10+20 | 81.5 | -0.033 [-0.049, -0.018] | +0.20 / -1.09 | 0.051 |
| random walk | adverse 10+20+30 | 82.7 | -0.034 [-0.050, -0.019] | +0.19 / -1.09 | 0.050 |
| random walk | confirm 10+10+20 | 9.6 | +0.021 [-0.043, +0.085] | +6.30 / -0.64 | 0.432 |
| drift -1%/d (against) | single 40 | 71.6 | -0.083 [-0.102, -0.064] | +0.30 / -1.05 | 0.399 |
| drift -1%/d | adverse 10+20+30 | 78.5 | -0.084 [-0.101, -0.067] | +0.19 / -1.09 | 0.391 |
| drift -1%/d | confirm 10+10+20 | 6.9 | -0.187 [-0.242, -0.132] | +6.29 / -0.66 | 0.879 |
| drift +1%/d (with) | single 40 | 80.0 | +0.030 [+0.013, +0.047] | +0.30 / -1.05 | 0.001 |
| drift +1%/d | adverse 10+20+30 | 85.0 | -0.008 [-0.022, +0.007] | +0.18 / -1.09 | 0.006 |
| drift +1%/d | confirm 10+10+20 | 13.3 | +0.295 [+0.222, +0.369] | +6.31 / -0.62 | 0.058 |
| mean-reverting (OU, half-life 2 h) | single 40 | 84.7 | +0.094 [+0.079, +0.109] | +0.30 / -1.05 | 0.000 |
| OU | adverse 10+20+30 | 89.8 | +0.069 [+0.056, +0.082] | +0.20 / -1.09 | 0.000 |
| OU | confirm 10+10+20 | 0.5 | -0.542 [-0.558, -0.526] | +6.31 / -0.57 | 1.000 |

With a +0.6% target under OU, the adverse ladders beat the single entry (+0.18R vs +0.13R). That is the only cell where they win.

**Verdict H2: NOT SUPPORTED as proposed; testable only as a mean-reversion layer.**
- Under a random walk every ladder has zero gross expectancy; the optional-stopping result holds and the model agrees within the CI.
  Adverse adds lift the win rate (76% to 83%) by making winners smaller (0.30R to 0.19R). The loss per stop-out is unchanged (-1.09R).
- This is the high-win-rate, rare-large-loss shape the brief warned about. With a hard stop the per-trade tail is bounded, but the
  real exposure is 2.3-3.3x what the first rung suggests.
- Adverse adds win only under mean reversion at the ladder's scale. Confirmation adds win only under trend.
- The external evidence favours trend at multi-hour horizons, and 15m reversal is smaller than fees (FABIO_BTC_RESEARCH:65-80, E1-E4
  vs E7). That leans against adverse ladders at intraday scale.
- Fabio contradicts it: he adds with the move after risk is at zero (FABIO_TRADE_MODEL.md:17-19; jasv3L [3:39]-[4:12]). FR-03 says
  no size-up after a loss (FABIO_RULEBOOK.md:7), and an adverse add is a size-up into an open loss.

**What MTS plan rules would have to change** (MTS_USER_GUIDE.md:145-153):
- The stop is a % from the AVERAGE entry (FORMULAS.md 11.6 with E from 11.4), so the stop slides down as rungs fill. A fixed-price
  hard-stop mode is needed.
- Unfilled ladder rungs cancel after 10 minutes (MTS_USER_GUIDE.md:128-129). Rungs would need to rest for hours.
- The max-loss check must use all rungs filled (2.34x / 3.34x).
- One plan at a time and multiples of 10 USD already fit.
- Confirmation adds (Fabio) would need breakeven and stop moves, which "no trailing, no breakeven" forbids today.

### 4.3 H3 narrow windows first (staged protocol; NOT RUN, no data here)
- **Stage 0, definitions.**
  - Window W = the US cash open, DST-aware: 13:30 UTC in summer, 14:30 UTC in winter (PROJECT_VISION.md:105), then +0-60 and
    +60-120 min.
  - Placebo windows = the same 2 h block starting at each of the other 23 hours.
  - Data: F: 1m klines 2022-01..2026-09, about 1,180 weekday sessions (price-only stages). F: orderflow_1m 2024-12..2026-09, about
    480 weekday sessions (S2 stages).
- **Stage 1, descriptive (no trades).** Per window:
  - range %, realised volatility, and range / ATR(1h);
  - frequency of balance then breakout, using S1 and S5 from FABIO_TRADE_MODEL.md:33-37;
  - whether the first-30-min sign persists (IVB idea);
  - how often S2 (pressure in balance) precedes the breakout.
  - Output: NY's rank among the 24 hourly windows for each statistic. The placebo rank is the multiple-testing control.
- **Stage 2, predictive.**
  - Does S2 in the 60 min before the open predict the sign and size of the 2 h move after the open?
  - Does the first-30-min direction predict the next 90 min?
  - Report the variance ratio at 5, 15 and 60 min inside W. This settles H2: VR < 1 means mean reversion.
  - Kill if NY is not in the top quartile of placebos, or if the OOS year sign flips.
- **Stage 3, trade reconstruction simulation, only if stage 2 passes.**
  - Fabio LVN-pullback and failed-breakout models (FABIO_BTC_RESEARCH:27-32).
  - Maker entries armed before the touch; the stop width from H1.
  - Management: breakeven, then adds on confirmation, then an order-flow trail.
  - Evaluate per day (1.2 item 1) with a daily stop.
- **Stage 4.** Widen to London and Asia opens only after stage 3 passes OOS. Register every added window as a trial.
- **Prior evidence.**
  - C2 tested fixed 810 min UTC starts (T055_BT_c2.md:34-43). All IS variants were negative and OOS failed. But C2 was momentum
    with a 24 h hold and no stop, not the balance-to-breakout trade.
  - E4 (FABIO_BTC_RESEARCH:70) supports first-half-hour information.

**Verdict H3: SOUND; highest value per cost.** Stages 1-2 need only klines and existing detectors. They also answer H2's mean-reversion
question and give H1 its window-specific volatility.

### 4.4 Trial count
- Market-data trials: 0.
- Model configurations: H1 44 cost cells (A 14, B 30; the survival grid in C is descriptive). H2 28 path configurations (4 processes
  x 7 strategy-target pairs).
- Total 72. H2 was re-run twice after fixing the confirmation-ladder R definition and adding CIs. No variant was selected, so PBO
  does not apply. None of these numbers is evidence of edge on BTC.

## 5. Next steps (ranked by evidence, then cost)
1. **Tom stop and target audit (proposal only; Tom logic changes need an operator ruling and Rule 32).** Owner: desktop with F:
   tom_snapshots.
   - Count stop source (swing / fallback / floor reset).
   - Recount WAIT_RR with the farthest qualifying level and with no 3.5R cap.
   - Re-run the watch_episode sim with a Tom-style inside stop as sensitivity.
   - Done when: a 3-row table of verdict counts plus mean net R with CI per variant, with the null.
2. **H3 stages 1-2.** Owner: NUC Qwen implements, Haiku writes tests from this spec, desktop runs on F:. Done when: NY rank among
   24 windows for 6 statistics, plus variance ratios, with the OOS year split.
3. **H1 MAE/MFE surface** on Tom episodes and the random null, grid registered first. Owner: desktop with F: (Sonnet builder). Done
   when: a per-cell table with DSR/PBO; a floor stop proposed for all layers.
4. **One fee source of truth.** Reconcile sim.py:18-20 with fabio_of_model.py:40-44 against Deribit public/get_instrument (testnet
   is allowed). Owner: DSA or desktop. Done when: FORMULAS.md has one cost section cited by both files.
5. **Re-extract with the trade-reconstruction template** (3.2): 3 Tom and 3 Fabio walkthroughs, including one losing session each
   (candidates: Tom kXhIAug0Gh8 "a lot of stop losses", dh-ysRR8f-M "biggest loss"). Owner: DSA template, NUC Qwen extraction,
   verify_extract_quotes gate. Done when: 6 reconstructions pass the quote gate, each with a gate-replay line.
6. **Fix the extraction defects.**
   - The operator listens to jasv3L-d8ZE at [11:16]-[11:53] and corrects R5/FR-90.
   - Untick DSA 999 or run it with a gate row.
   - Owner: DSA. Done when: the rulebook row is corrected and DSA_GATE_LOG has a 999 row.
7. **Day-type classifier** (compression vs trend; BTC dealer gamma from Deribit options if history exists). Owner: cloud design,
   then desktop. Done when: a data availability check plus one event study of day type vs trend-model P&L.
8. **H2 adverse ladder as a separate mean-reversion layer**, only if stage 2 shows VR < 1 at the ladder scale. It needs the plan
   rule changes in 4.2. Owner: DSA spec. Done when: an OOS test reports the loss tail and risk of ruin, not win rate.

## 6. Open questions for the operator
1. Is yRvMW6lgN1o an ES trade, and was EUR 250 the full-size risk? The ticks give 8.1R; the money gives 4.85R.
2. May the Tom stop and target logic be changed at all (inside-structure stop, farthest level, no 3.5R cap), or only studied as
   sensitivity?
3. Which Deribit fee schedule is canonical: taker 5 / maker 0 (sim.py) or 3.5 / -1.5 bps (fabio_of_model.py)?
4. May layer plans get breakeven, stop moves and fixed-price hard stops? Fabio's model and any ladder need them.
5. For H2: is the goal a higher win rate or higher expectancy, and is 2.3-3.3x the first-rung risk acceptable?
6. Approve the trade-reconstruction template (3.2) as the primary extraction product, with rule rows as an index?
