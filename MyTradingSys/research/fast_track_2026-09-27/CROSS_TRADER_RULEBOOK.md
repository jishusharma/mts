# CROSS-TRADER RULEBOOK (CryptoCred + The Flow Horse)
Built for DSA_BACKLOG item A. Same table as FABIO_RULEBOOK.md plus a last column "built as layer" (checked against MyTradingSys/backtest/layers/ on 2026-09-30). Descriptive only: Tom is core; these are separate layers, never Tom filters. Tom overlap column is descriptive, not a proposal.

## 0. Scope, counting and caveats
- Inputs read in full: extracts/processed/cryptocred/ (5 files, 66 source rules), extracts/processed/flowhorse/ (3 files: Oy2Z-FQ77NM 11 rules, zMM9QgxfEFI 8 rules, UcPp0gFI5M8 0 rules + 4 principles P1-P4 and 10 future concepts), extracts/fresh/ flow_horse (UrnES-HzQ6w, izZyd-HrTSE).
- Source id format: CC-<video>-R<n>, FH-<video>-R<n> (Part J extracts); FH-UcPp0gFI5M8-P<n> = principle alignments of the intro video (not rules). The two extracts/fresh files are raw transcripts with no rule ids and no Part J extraction: rows citing FHT-<video> are my reading of the whole transcript, unverified, speaker claims not tested. Treat as lower grade until extracted.
- Rows merge source rules that say the same thing; every source rule is covered by at least one row. No quotes are used (paraphrase only), so verify_extract_quotes.py has nothing to check.
- Built column: "yes" = module implements the rule, "partial" = implements a simplified part, "no" = not implemented. Data codes: KLINES, AGGTRADES, L2, OI, FUNDING, LIQ (liquidation feed), TICK (sub-second trades), NONE.
- All built CryptoCred code is in MyTradingSys/backtest/layers/cryptocred/ (cc_structure.py, cc_retest.py, cc_setups.py, cc_bt_adapter.py which only wires cc_setups signals into bt_engine/runner). Its own docstrings cite cluster ids (C07/C08/C10) from research/_archive/loose_2026-10/cross_trader_consolidated.md, not these extract ids. No Flow Horse module exists anywhere under layers/ (grep for flow horse, VAH, LVN, liquidation, FTA finds only Fabio volume-profile helpers and generic alert code).
- Implementer parameters not from the extracts: swing fractal 2/2, stop buffer 0.1%, target 1.5R (setups 1,2) and 2.0R (setup 3), retest tolerance 0.15%, expiry 200 bars, failure lookback 20 bars.

## 1. CryptoCred rule table (47 rows)
| id | rule (one line, my words) | source rule ids | topic | class | data needed | Tom overlap | built as layer |
|---|---|---|---|---|---|---|---|
| CCR-01 | Swing points: fractal high/low, prefer recent, obvious, large follow-through move | CC-BHwoN7VPrBE-R1 | zones | CONTEXT | KLINES | NONE | partial: cryptocred/cc_structure.py find_swings (fixed-width body fractal; no recency/size ranking) |
| CCR-02 | Market-structure break = sequence of LH violated by a HH (bull) or HL violated by a LL (bear) | CC-BHwoN7VPrBE-R2 | entry | SIGNAL | KLINES | NONE | yes: cryptocred/cc_structure.py classify_msb |
| CCR-03 | Structure is a context tool, not a stand-alone mechanical system | CC-BHwoN7VPrBE-R3 | proof | CONTEXT | NONE | NONE | no (principle) |
| CCR-04 | Do not treat every MSB as significant (that is breakout chasing) | CC-BHwoN7VPrBE-R4 | entry | PSYCH | NONE | NONE | no |
| CCR-05 | Swing significance rises with confluence: SR, old highs/lows, monthly/weekly/daily opens | CC-BHwoN7VPrBE-R5; CC-BHwoN7VPrBE-R11 | zones | CONTEXT | KLINES; FUNDING; OI | COMPLEMENT | no |
| CCR-06 | Setup 1: after MSB, enter the pullback to the broken level (SR flip) | CC-BHwoN7VPrBE-R6 | entry | SIGNAL | KLINES | NONE | yes: cryptocred/cc_setups.py setup1_sr_flip (+ cryptocred/cc_retest.py) |
| CCR-07 | MSBs mid-range are noise; only range-extreme MSBs count | CC-BHwoN7VPrBE-R7 | zones | CONTEXT | KLINES | NONE | yes: cryptocred/cc_structure.py is_range_extreme / classify_msb filter_range_noise |
| CCR-08 | MSB timeframe sets expected move size (weekly > intraday) | CC-BHwoN7VPrBE-R8 | target | CONTEXT | KLINES | NONE | no |
| CCR-09 | Counter-trend: shorter hold, min R:R 2 instead of 1.5, smaller size | CC-BHwoN7VPrBE-R9 | risk | RISK | KLINES | NONE | partial: cryptocred/cc_setups.py setup3 target_r=2.0 only (no hold limit, no sizing) |
| CCR-10 | Do not auto cut-and-reverse after invalidation | CC-BHwoN7VPrBE-R10 | management | RISK | NONE | NONE | yes (constraint): cryptocred/cc_setups.py never chains setup1/2 stop into setup3 |
| CCR-11 | Structure built from candle bodies; break needs a close on the same TF as the anchor | CC-BHwoN7VPrBE-R12; CC-inqHN8q57X4-R3 | entry | SIGNAL | KLINES | NONE | partial: cryptocred/cc_structure.py use_body + close break (single TF only, no MTF alignment) |
| CCR-12 | Setup 2: enter at SR structure inside 0.618-0.786 retrace of the breakout leg | CC-BHwoN7VPrBE-R13 | entry | SIGNAL | KLINES | NONE | partial: cryptocred/cc_setups.py setup2_fib_pullback (fib zone only, no SR-structure test) |
| CCR-13 | Setup 3: failed MSB (no follow-through, back through broken level) = reversal | CC-BHwoN7VPrBE-R14 | entry | SIGNAL | KLINES | NONE | yes: cryptocred/cc_setups.py setup3_failed_msb_reversal |
| CCR-14 | Gradual loss of trend (LL -> equal/higher lows) is a warning, not a trade | CC-BHwoN7VPrBE-R15 | proof | CONTEXT | KLINES | NONE | no |
| CCR-15 | Every trade idea must be falsifiable; invalidation comes from the idea and sets the stop | CC-XeQV2ECtZVQ-R1; CC-XeQV2ECtZVQ-R2 | stop | RISK | NONE | NONE | partial: stop = broken level +/- fixed 0.1% buffer in cc_setups.py (buffer is implementer choice) |
| CCR-16 | Stop strictness inverse to move size: precise for LTF, wide for HTF swings; never mix | CC-XeQV2ECtZVQ-R3; CC-inqHN8q57X4-R8 | stop | RISK | KLINES | NONE | no |
| CCR-17 | Hard stop (market, full close) for precise setups; soft stop for swing; beginners hard | CC-XeQV2ECtZVQ-R4 | stop | RISK | NONE | NONE | no |
| CCR-18 | Size = portfolio x risk% / distance to invalidation | CC-XeQV2ECtZVQ-R5 | risk | RISK | NONE | NONE | no (not in cryptocred/) |
| CCR-19 | Risk per trade scales with setup EV and frequency; milk high-freq high-EV edge until it breaks | CC-XeQV2ECtZVQ-R6 | risk | RISK | NONE | NONE | no |
| CCR-20 | Remaining R:R evolves as price moves; manage so near-target trades do not round-trip | CC-XeQV2ECtZVQ-R7; CC-_ndAoizXy64-R8 | management | RISK | KLINES | OVERLAP (evolving R credited to Tom Dante in source) | no |
| CCR-21 | Beginners: conservative target (FTA) and set-and-forget; over-managing is the likelier error | CC-XeQV2ECtZVQ-R8 | management | PSYCH | NONE | NONE | no |
| CCR-22 | Judge streaks per setup, not globally; do not drop a working setup after a few losses | CC-XeQV2ECtZVQ-R9 | risk | PSYCH | NONE | NONE | no |
| CCR-23 | Break-even stops and partials are mostly comfort; manage only from the trade idea | CC-XeQV2ECtZVQ-R10; CC-XeQV2ECtZVQ-R11; CC-_ndAoizXy64-R9 | management | PSYCH | NONE | NONE | no |
| CCR-24 | Leverage only sets collateral/liquidation distance; P&L is set by position size | CC-XeQV2ECtZVQ-R12 | risk | RISK | NONE | NONE | no |
| CCR-25 | Alts dump with BTC/ETH; multiple alt positions stack downside risk | CC-XeQV2ECtZVQ-R13 | risk | RISK | KLINES | NONE | no |
| CCR-26 | FTA = nearest opposing S/R; take-profit FTA is on the same TF as the idea (avoid crumbs) | CC-Yp0k8HD5xro-R1; CC-Yp0k8HD5xro-R2; CC-Yp0k8HD5xro-R13 | target | SIGNAL | KLINES | NONE | no |
| CCR-27 | Management FTA = interim obstacle one TF lower (monthly->weekly->daily->intraday) | CC-Yp0k8HD5xro-R3; CC-Yp0k8HD5xro-R4; CC-_ndAoizXy64-R2 | management | CONTEXT | KLINES | NONE | no |
| CCR-28 | Price fails the management FTA = weakness, close or brace for retest of entry | CC-Yp0k8HD5xro-R5 | management | SIGNAL | KLINES | NONE | no |
| CCR-29 | Price breaks the management FTA = idea on track: add, or move stop to the broken FTA, or hold | CC-Yp0k8HD5xro-R6 | management | SIGNAL | KLINES | NONE | no |
| CCR-30 | Low conviction at a level: enter on break of the nearby FTA instead of at the level | CC-Yp0k8HD5xro-R7 | entry | SIGNAL | KLINES | NONE | no |
| CCR-31 | Entry-FTA should sit close to the level; management-FTA needs room after a real move | CC-Yp0k8HD5xro-R8 | entry | CONTEXT | KLINES | NONE | no |
| CCR-32 | Match move expectations to level TF; LTF levels give small moves | CC-Yp0k8HD5xro-R9 | target | CONTEXT | KLINES | NONE | no |
| CCR-33 | First test best test: hold through a retest of entry; no BE on the first HTF reaction | CC-Yp0k8HD5xro-R10; CC-Yp0k8HD5xro-R11 | management | SIGNAL | KLINES | NONE | no |
| CCR-34 | Classify a level by the highest TF on which it is clearly visible, no higher | CC-Yp0k8HD5xro-R12 | zones | CONTEXT | KLINES | NONE | no |
| CCR-35 | Manage on entry TF plus one lower; too low over-manages, too high misses signals | CC-_ndAoizXy64-R2; CC-_ndAoizXy64-R11 | management | CONTEXT | KLINES | NONE | no |
| CCR-36 | Reassess evidence continuously; if price contradicts the thesis, cut before full stop | CC-_ndAoizXy64-R1; CC-_ndAoizXy64-R3; CC-_ndAoizXy64-R4; CC-_ndAoizXy64-R6 | management | SIGNAL | KLINES | NONE | no |
| CCR-37 | Trap/momentum/SR setups have time expiry; stalling shifts odds to failure | CC-_ndAoizXy64-R5 | management | SIGNAL | KLINES | NONE | no |
| CCR-38 | Profit-taking: trail under swings in trends, fixed targets (range edge/ATR) in ranges | CC-_ndAoizXy64-R7 | target | SIGNAL | KLINES | NONE | no |
| CCR-39 | Trade the chart, not P&L or trade history; defer to the system | CC-_ndAoizXy64-R10; CC-_ndAoizXy64-R13; CC-_ndAoizXy64-R12 | management | PSYCH | NONE | NONE | no |
| CCR-40 | Dead zone between stop and target: nothing to manage, let it play | CC-_ndAoizXy64-R11 | management | PSYCH | NONE | NONE | no |
| CCR-41 | A break is not validated by a retest; break of structure is the event | CC-inqHN8q57X4-R1 | entry | CONTEXT | KLINES | NONE | yes: cryptocred/cc_retest.py find_retest returns None when no retest (optional) |
| CCR-42 | Breakout entry = fill but worse R:R; retest entry = better R:R but no fill guarantee; do not split | CC-inqHN8q57X4-R2; CC-inqHN8q57X4-R5 | entry | CONTEXT | KLINES | NONE | no |
| CCR-43 | Rounded retest (time and space since break) is cleaner than immediate retest | CC-inqHN8q57X4-R4 | entry | SIGNAL | KLINES | NONE | yes: cryptocred/cc_retest.py classify_retest_timing |
| CCR-44 | Expect retests only if the instrument has been giving them; fast impulses after ranges often do not | CC-inqHN8q57X4-R6; CC-inqHN8q57X4-R9 | entry | CONTEXT | KLINES | NONE | no (cryptocred/cc_retest.py docstring lists precedent and hidden HTF retests as not implemented) |
| CCR-45 | Big break already used the target space: skip chase without retest (R:R decides) | CC-inqHN8q57X4-R7 | entry | RISK | KLINES | NONE | no (cryptocred/cc_retest.py lists as not implemented) |
| CCR-46 | Ranges: fade extremes, do not chase breaks; strong trend traps counter-trend failed breaks | CC-inqHN8q57X4-R10; CC-inqHN8q57X4-R11 | entry | CONTEXT | KLINES | NONE | no |
| CCR-47 | Retest after an HTF level was hit in between is low probability | CC-inqHN8q57X4-R12 | entry | CONTEXT | KLINES | NONE | no |

## 2. The Flow Horse rule table (32 rows)
| id | rule (one line, my words) | source rule ids | topic | class | data needed | Tom overlap | built as layer |
|---|---|---|---|---|---|---|---|
| FHR-01 | Volume profile says where business was done, nothing about who or intent; the rest is assumption | FH-Oy2Z-FQ77NM-R1; FH-UcPp0gFI5M8-P1 | proof | CONTEXT | AGGTRADES | COMPLEMENT | no |
| FHR-02 | Profile relevance decays with age: recent sessions for positioning, old profiles are context only | FH-Oy2Z-FQ77NM-R2; FH-Oy2Z-FQ77NM-R9 | zones | CONTEXT | AGGTRADES | COMPLEMENT | no |
| FHR-03 | Zone trust falls with each test: 1st/2nd test at VAH/VAL actionable, 3rd-5th is pressure build-up | FH-Oy2Z-FQ77NM-R3 | zones | SIGNAL | AGGTRADES | COMPLEMENT | no |
| FHR-04 | Longer sideways compression (incl. DVOL down, barcoding) means a bigger response on resolution | FH-Oy2Z-FQ77NM-R4; FH-zMM9QgxfEFI-R2 | proof | CONTEXT | KLINES; AGGTRADES | NONE | no |
| FHR-05 | Head fake: sweep of level on low volume/absorption then back into value = fade | FH-Oy2Z-FQ77NM-R5 | entry | SIGNAL | AGGTRADES | COMPLEMENT | no |
| FHR-06 | After a high-volume break outside profiles, buy the first throwback that re-accepts on the break side | FH-Oy2Z-FQ77NM-R6 | entry | SIGNAL | AGGTRADES | COMPLEMENT | no |
| FHR-07 | LVN = rejection zone on return; prior-session LVN matters more than old LVN | FH-Oy2Z-FQ77NM-R7 | zones | SIGNAL | AGGTRADES | COMPLEMENT | no (note: fabio/fabio_volume_fvg.py has build_profile/value_area/lowest_volume_level, a Fabio FVG rule, not this one) |
| FHR-08 | Profile gives areas; order flow decides whether to act there | FH-Oy2Z-FQ77NM-R8 | proof | CONTEXT | AGGTRADES | COMPLEMENT | no |
| FHR-09 | Composite profiles only when tight overlap; in loose markets extremes beat value area | FH-Oy2Z-FQ77NM-R10 | zones | CONTEXT | AGGTRADES | NONE | no |
| FHR-10 | POC can shift with platform/tick size; marginal HVN differences are not significant | FH-Oy2Z-FQ77NM-R11 | zones | CONTEXT | AGGTRADES | NONE | no |
| FHR-11 | Heavy selling (news, big seller) with price holding = seller exhaustion/absorption; buyers not implied | FH-zMM9QgxfEFI-R1; FH-zMM9QgxfEFI-R8 | proof | SIGNAL | AGGTRADES | COMPLEMENT | no |
| FHR-12 | Extended balance + high-volume break: range height is the minimum measured-move target | FH-zMM9QgxfEFI-R3 | target | SIGNAL | KLINES; AGGTRADES | NONE | no |
| FHR-13 | Inside a range only rotations; real change is outside the extremes where one side is offside | FH-zMM9QgxfEFI-R4 | zones | CONTEXT | KLINES | NONE | no |
| FHR-14 | After a high-volume break, the break candle low is the hard invalidation | FH-zMM9QgxfEFI-R5 | stop | SIGNAL | KLINES | NONE | no |
| FHR-15 | Shallow pullback after the break = legitimate continuation; deep = failure risk | FH-zMM9QgxfEFI-R6 | proof | SIGNAL | KLINES | NONE | no |
| FHR-16 | One day of tight balance after the break = building for the next leg | FH-zMM9QgxfEFI-R7 | proof | CONTEXT | KLINES | NONE | no |
| FHR-17 | Course intro: profile and flow are tools not strategies; always locate developing value and who is in control | FH-UcPp0gFI5M8-P1; FH-UcPp0gFI5M8-P2; FH-UcPp0gFI5M8-P3 | zones | CONTEXT | AGGTRADES | COMPLEMENT | no (intro video, 0 actionable rules per its own assessment) |
| FHR-18 | Trade only at contextual risk/reward edges (VAH/VAL/POC), not no-man's-land | FH-UcPp0gFI5M8-P4 | zones | RISK | AGGTRADES | NONE | no |
| FHR-19 | Liquidation cascade: after a record liquidation/OI wipe with a blown-out low, buy the first green bar after the first pause | FHT-UrnES-HzQ6w | entry | SIGNAL | LIQ; OI; TICK; L2 | NONE | no |
| FHR-20 | Cascade target = origin of the breakdown; take most size off there | FHT-UrnES-HzQ6w | target | SIGNAL | KLINES | NONE | no |
| FHR-21 | Precondition: sharp OI jump in a short time through a key level (more than absolute OI); stops cluster at obvious swings | FHT-UrnES-HzQ6w | proof | CONTEXT | OI; LIQ | NONE | no |
| FHR-22 | Cascade signature: wide range on huge volume, spreads blown out, cross-exchange basis dislocated, first rebound on about half the volume | FHT-UrnES-HzQ6w | proof | SIGNAL | TICK; L2; multi-exchange | NONE | no |
| FHR-23 | Stops: place beyond obvious swings by 1.5-2 ATR to survive the sweep | FHT-UrnES-HzQ6w | stop | RISK | KLINES | NONE | no |
| FHR-24 | News event: first trade mechanical, market in on the direction of the equity-index jump at release, ignore the print and local levels | FHT-izZyd-HrTSE | entry | SIGNAL | TICK; SPX feed; calendar | NONE | no |
| FHR-25 | Event first trade exits at a pre-set 200-300 bp bracket by selling into the ask; no hard stop, scratch if price returns to entry | FHT-izZyd-HrTSE | exit | SIGNAL | TICK | NONE | no |
| FHR-26 | Event second move (unwind of fresh, late positioning) is larger; size up on it after momentum wanes, 30-60 min window | FHT-izZyd-HrTSE | entry | SIGNAL | TICK; AGGTRADES | NONE | no |
| FHR-27 | If a trade is not immediately in profit, scratch it (high standard for speed); re-enter if it then shows what is wanted | FHT-izZyd-HrTSE | management | PSYCH | NONE | NONE | no |
| FHR-28 | Front-run the obvious exit level; never wait for the last tick of it | FHT-izZyd-HrTSE | exit | PSYCH | NONE | NONE | no |
| FHR-29 | Post-event: move beyond 1.2-2 SD VWAP band then reclaim of band = continuation long; do not buy/sell after a long run past the bands | FHT-izZyd-HrTSE | entry | SIGNAL | KLINES | NONE | no |
| FHR-30 | Structure break with bearish catalyst: cover on pops, add into breakdown/weakness, target the lows through value gap | FHT-izZyd-HrTSE | management | SIGNAL | KLINES; AGGTRADES | NONE | no |
| FHR-31 | Volume stuck above a wick high = trapped, short; burp (spread blows, tape speeds) without a follow-through puke = exit | FHT-izZyd-HrTSE | proof | SIGNAL | TICK; L2 | COMPLEMENT | no |
| FHR-32 | Pennant/funnel after event: move extends at least the funnel mouth (measured move) | FHT-izZyd-HrTSE | target | SIGNAL | KLINES | NONE | no |

## 3. Trade sequence: CryptoCred
Fields: state -> location -> trigger -> stop width -> management -> exit.
- State: present. Trend vs range, MSB with range-extreme filter, counter-trend flag (CC-BHwoN7VPrBE-R2, R7, R9; CC-inqHN8q57X4-R10, R11).
- Location: present. Broken level (SR flip), 0.618-0.786 retrace, confluence with opens/old highs (CC-BHwoN7VPrBE-R5, R6, R13); HTF level classified by highest visible TF (CC-Yp0k8HD5xro-R12).
- Trigger: present. Pullback/retest of the broken level; failed MSB back through the level; or break of the nearby FTA when conviction at the level is low (CC-BHwoN7VPrBE-R6, R14; CC-Yp0k8HD5xro-R7; CC-inqHN8q57X4-R4).
- Stop width: qualitative only. Stop = invalidation derived from the idea, strictness inverse to move size, hard stop for beginners (CC-XeQV2ECtZVQ-R1 to R4). The only numbers are a worked sizing example (2% risk, 5% stop) and counter-trend min R:R 2 vs 1.5. No rule gives a width in ATR or percent. The 0.1% buffer in cc_setups.py is an implementer choice, not from the source.
- Management: present but absent from code. Manage on entry TF plus one lower, FTA break/fail, evolving R, thesis-failure cut before stop, time expiry, dead zone, no automatic break-even (CC-_ndAoizXy64, CC-Yp0k8HD5xro-R3 to R6, R10, R11; CC-XeQV2ECtZVQ-R7, R10).
- Exit: present. FTA on the same TF as the idea, trailing under swings in trends vs fixed range/ATR target in ranges (CC-Yp0k8HD5xro-R2; CC-_ndAoizXy64-R7); beginners set-and-forget at FTA (CC-XeQV2ECtZVQ-R8).
- Gap that matters: the source sequence is complete, but the built layer keeps only state + location + trigger + a fixed-buffer stop + a fixed 1.5R/2R single target. None of the management or FTA exit rows are built (of the management-topic rows only the no-auto-chain constraint is honoured), so the backtest of these setups tests entries, not the trader's method.

## 4. Trade sequence: The Flow Horse
No single end-to-end trade in the Part J extracts. Per source:
- Profile extracts (Oy2Z-FQ77NM, zMM9QgxfEFI): state (balance/compression vs break) and location (value edges, LVN, throwback) are described; trigger is partly described (head fake signature, throwback re-acceptance, shallow pullback); stop width MISSING except zMM break-candle low as invalidation (FH-zMM9QgxfEFI-R5), no distance; management MISSING; exit only measured move target (FH-zMM9QgxfEFI-R3). Order-flow trigger detail (how much absorption, delta threshold) MISSING; the profile extract defers it to "order flow" without numbers.
- Intro video (UcPp0gFI5M8): no sequence; topic list only (76% value rule, heavier aggressor, fake-out unwinds, double distribution, oxygen reversal, etc. are flagged FUTURE, not extracted).
- Liquidation cascade transcript (UrnES-HzQ6w): state (record liquidation, OI wipe), location (blown-out low), trigger (first green bar after first pause) and exit (origin of breakdown, most size off there) are stated. Stop width MISSING: no stop or invalidation is given (the speaker uses stink bids and adds manually); management beyond take-most-off MISSING; size not given.
- NFP transcript (izZyd-HrTSE): state and location are explicitly ignored; trigger is release time plus equity-index jump direction; exit is a 200-300 bp bracket or return to entry (scratch); no hard stop; later trades use VWAP SD bands and volume pockets with scale in/out. Stop width MISSING as a number; position size only relative (second move sized larger, first trade small).
- Gap that matters: Flow Horse material has triggers and targets but no stop widths and almost no management rules, and the two richest trade descriptions are raw transcripts. None is built, and most need LIQ/OI/TICK/L2 data we may not have for backtest (AGGTRADES covers the profile and absorption rows only).

## 5. Counts
| trader | rules (rows) | source rules covered | yes | partial | no |
|---|---|---|---|---|---|
| CryptoCred | 47 | 66 | 7 | 5 | 35 |
| The Flow Horse | 32 | 19 + 4 principles + 2 transcripts | 0 | 0 | 32 |
