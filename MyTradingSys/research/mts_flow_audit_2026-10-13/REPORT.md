# MTS end to end: the mistake at each step, and whether to buy FDAX data (2026-10-13, cloud, read-only)

Session: MTS-2026-10-13-1654Z-CLD-ANA-flow-audit. Base: origin/fast-track ff9dfa1a. No code, card, decision or live-path change.
Operator ask (verbatim): "So We need to buy DATA! Ask what that will prove? And then we have to apply what exactly for BTC?
Intent behind DAX testing was an understand what we are fundamentally doing wrong! So i an now thinking twice abt if we should
get into buying data on proving something on DAX rather than focusing on BTC! So what you think abt this? Second - I think you
need to research properly on each possible mistakes we are making in each step of what we are doing! The complete flow and the
whole idea of what MTS is and what is does that culminates into the need for testing and back-testing trades strategeies/idea/data."
Builds on, does not repeat: tom_dax_what_is_proven_2026-10-13/REPORT.md, backtest_gap_review_2026-10-13/REPORT.md (G1-G8),
layer_combo_verdict_2026-10-13/REPORT.md, tom_transfer_2026-10-11/BACKTEST_FAILURES_RESEARCH.md (C1-C8), and
TRANSLATION_POSTMORTEM_2026-10-12.md (P1-P11; on branch claude/sharp-carson-3xkd36, never merged into fast-track).
Labels: [checked] = re-read or recomputed in this session. [search] = web search snippet, page not opened (WebFetch cannot
resolve hosts from this container). [estimate] = my number, not measured. [view] = opinion. "New" = not in the five reviews above.

## 0. Answers

### 0.1 Buy FDAX data? Not now. [view]
- **What it would prove.** Whether Tom's own named order-flow signals ("selling surplus" in delta, "a lot was simply absorbed")
  sit at his entries on 5 design and 2 check sessions. That is a fidelity test: did we read Tom right? It cannot show that Tom
  has an edge (7 trades he chose to publish), and it does not produce a BTC strategy.
- **What we would then apply on BTC.** The spec already says it (TOM_LAYER_V2_SPEC.md part B; NEXT_SESSION.md Q4): Tom's fade
  entry, order-flow proofs from Binance aggTrades, and a minimum stop of 0.40 % of price all-taker or 0.20 % with a maker entry;
  narrower = no trade. Tom's own stops are 0.08-0.26 % (spec :27-39). So the BTC version has a stop 2-5 times his, on a market
  with no opening auction for the spike he fades. It is a new strategy that needs its own BTC test, and that test does not
  need FDAX data: BTC already carries the aggressor side for free.
- **How far a PASS is from a BTC trade.** Four gates: FDAX fidelity, FDAX profit run (211-3,059 trades for 80 % power,
  backtest_gap_review G1), BTC transfer at the wider stop, testnet. No source has passed a profit gate (S3) yet.
- **Money is not the issue.** Databento sells Eurex trades (dataset XEUR.EOBI) with a side field that marks the aggressor,
  history from 2025-03-10, $5/GB usage pricing [search]. Every Tom ledger date (2025-12-22 onward, all still unverified)
  falls inside that window [checked dates]. Seven sessions plus control days is a few dollars of trade data [estimate].
  The cost is attention: the Tom chain is the project priority (NEXT_SESSION.md:10) with 15 open cards (LAYERS.md, Tom section) [checked].
- **Recommendation.** Answer q11 with "No, park Tom as discretionary now" for the BTC mandate. Keep the spec and the ledger
  as reference. The FDAX one-shot stays available and cheap if you later want closure on "can a trader's words be coded at all".
  The same logic applies to Fabio, whose home market is NQ.

### 0.2 What are we fundamentally doing wrong?
DAX already answered the question it was started for. In one sentence: **we start from a person and build forward
(source, rules, engine, live trading, backtest) and check whether the idea can work at all last.** Every check that would
have stopped a build came after the build, one at a time, each found by a failure:
- Does the source have a verified record? Asked 2026-09-30; still no.
- Does our data hold what he reads? Found 10-11 (no aggressor split on DAX CFD).
- Do BTC fees allow his stop? Computed 10-11.
- Does our code fire on his trades? First checked 10-11: 0 of 7.
- Can the test detect his claimed edge? Computed 10-13: 7-35 % power.

The clearest example [checked]. On 2026-10-09 you asked to score Qriptal, a crypto caller who posts entries, stops and targets:
"just place trades that he says! and do see his past record - verify" (research/BUGS.md:275). That job needs no translation,
no engine and only free Binance klines. It is still not done. It was claimed for 30 h with no result, then stopped because an
unrelated Java build check was red (commit fb7a3daf). In the same days the hardest route, a German DAX trader read from
AI-translated captions, became priority 1.

## 1. What MTS is, as a flow [checked]
| # | Step | What happens | Where |
|---|---|---|---|
| 0 | Goal | Trade BTC perps with a proven net edge after fees; stages S1-S5 | PROJECT_VISION.md:211-214 |
| 1 | Choose sources | Tom (core), Fabio (core), Malkan, CryptoCred, FlowHorse, Krown, Qriptal, published rules | PROJECT_VISION.md "Sources we listen to"; system/LAYERS.md |
| 2 | Get their material | YouTube captions (Tom's machine-translated from German), video frames since 10-11 | raw_transcripts_canonical/ (121 files) |
| 3 | Extract rules | quotes with file:line, provenance rule, NO-SOURCE flags | extracts/, scripts/dev/verify_extract_quotes.py |
| 4 | Encode | Java engine (zones, proofs, verdict ladder, net_rr); Python layers | src/main/java/datafeed/SetupCandidatesBuilder.java; backtest/layers/ |
| 5 | Feed data | Binance feed, 15-minute snapshots, recorders; Dukascopy CFD for DAX | src/, runtime/, backtest/dax_data.py |
| 6 | Backtest | simulators, fees, fills, nulls, pre-registration, holdouts | backtest/*.py, backtest/PRE_REG_TEMPLATE.md |
| 7 | Decide | S3 bar, park or promote, operator decisions | system/GO_LIVE_BAR.md, system/OPERATOR_DECISIONS.md |
| 8 | Run live | auto_trader on Deribit testnet, loss monitor, go-live bar | execution/ |
| 9 | Run the project | DSA, Claude (CL, CC, cloud), Codex lab, NUC, relay, cards, claims, Control Room | system/ |

## 2. Mistakes, step by step

### Step 0. Goal
| # | Mistake | Evidence | Status |
|---|---|---|---|
| 0a | The instrument (BTC) and the sources (Tom, Fabio) were fixed separately. Nobody checked first that the sources' methods can work on BTC. | Goal: BTC (VISION:211). Tom is core (VISION:16). Tom's stops (0.08-0.26 %) cost 0.39-1.27 R per trade in BTC fees, against his claimed edge of 0-0.35 R (spec :27-39). That arithmetic takes two lines and was done 10-11, after the engine, the live trader and three BTC backtests. | Known since 10-11. New as a step-0 error. |
| 0b | The goal sets no feasible horizon, stop size or order type. | Taker fee is 0.05 % per side (backtest/fees.py:23). Keeping fees under 0.25 R needs a stop of at least 0.40 % with taker legs, or 0.20 % with a maker entry [checked arithmetic]. Every intraday encoding we built sits below that. Over 1,000 registered trials, mostly at holds of 8 h or less, found nothing that survives (gap review s7); the median Q33 cell's gross at 60 min is +0.0003 % (layer_combo_verdict s1). | The gross-edge gate was proposed 10-13 and is not adopted. |
| 0c | The doctrine contradicts itself. | VISION:16 "TOM IS CORE ... Non-negotiable" (from your 09-23 statement). VISION:221 "Promotion to core uses the S3 bar, never opinion". Tom has not passed S3 and is still core, which keeps his chain first in the queue (NEXT_SESSION.md:10). | New |

### Step 1. Choose sources
| # | Mistake | Evidence | Status |
|---|---|---|---|
| 1a | Sources were admitted without a track record. | Tom: marketing bio only (ANGLE_TRADER_SOURCES.md:26-27). Fabio: vendor bio, "audited >500 % in a year", not verified (FABIO_BTC_RESEARCH_2026-09-30.md:18-19). The scorecard (B162) came on 10-09, after both were cores, and was never applied to them. | Known (gap review E4). Open. |
| 1b | Most sources trade a different market. | Tom FDAX, Fabio NQ, Malkan Indian equities on daily/weekly/monthly, FlowHorse with undefined thresholds. CryptoCred is BTC-native but trades swings (BACKTEST_FAILURES s4). | Known (C8, P4) |
| 1c | The queue puts the BTC-native sources last. | CryptoCred's home-fit audit is p4 and last in the plan (NEXT_SESSION.md:34, Q30, after Tom and Fabio part B). Qriptal scoring has been unstarted since 10-09 (fb7a3daf). | New |
| 1d | "Codable" was never a selection test. Educators teach judgement from chosen trades. | "You can't do it with just a candlestick" (n7ZSkjb7JXs_raw.txt:19). A source is codable when it gives explicit numbers, dated calls and inputs we can observe. No source was screened for that before its build. | New as a criterion |
| 1e | You are not measured as a source. | Your charts carry BB(20,2), RSI and StochRSI, and none is computed in code (GUIDANCE_AUDIT.md:18, :34). The missed-trade pipeline that would log your reads with minute timestamps exists, and adoption is the first next step on its roadmap (missed_trades/ROADMAP.md:41-42); I can't see its store from here. Your reads are the only source with exact BTC timestamps and complete data. Whether they carry edge is unknown. | New |

### Step 2. Get the material
| # | Mistake | Evidence | Status |
|---|---|---|---|
| 2a | Audio was used for a visual craft. | Captions only until 10-11; a transcript price was wrong ("18,258" vs 24257 on the chart) (ROADMAP F2) | Known (C2); frames now used |
| 2b | The translation is unchecked. | Tom's captions are machine-translated. check_spec_quotes proves the English string is in the file, not that Tom said it (gap review E1). | Known. Open. |
| 2c | Videos show selected trades. | No trade frequency and no loss share; losing first attempts are missing from the ledger (spec :135) | Known (N8) |

### Step 3. Extract
| # | Mistake | Evidence | Status |
|---|---|---|---|
| 3a | Traders give concepts, not numbers. | Tom 2 of 74 engine parameters sourced, Fabio v3 0 of 8 (TOM_FABIO_REVIEW_2026-10-03.md:10); second-reader agreement kappa 0.446. The provenance rule then leaves two bad choices: invent numbers (forbidden) or run degenerate code (tiny stops). | Known (P3) |
| 3b | His decision is one picture (location + context + order flow + timing). We code it as separate "proofs" counted to a threshold. The counting was our idea. [view] | RECALL_DAX_V2.md: price idea alone 4 of 5; one counted proof 2 of 5 | Partly known (P1) |
| 3c | Nothing checks extraction coverage (rule missed, rule extracted wrong). | PROJECT_MAP.md SRC focus line | Known. Open. |

### Step 4. Encode
| # | Mistake | Evidence | Status |
|---|---|---|---|
| 4a | The engine was built before any ground truth existed. | Engine and live trader by about 09-28. First ledger of Tom's own trades 10-11, first recall check 10-11: 0 of 7 (postmortem s3; RECALL_DAX.md). | Known (C1). The order is the mistake. |
| 4b | One model family wrote the code, its tests and its backtests. | Every worker report had at least one wrong claim (postmortem P9). Codex lab added 10-12. | Known. Mitigated. |
| 4c | Tom's most common trade, the opening-spike fade, had no candidate type until 10-13. | SpikeFadeDetector.java, NEXT_SESSION.md Q6 | Known |

### Step 5. Data
| # | Mistake | Evidence | Status |
|---|---|---|---|
| 5a | Inputs were checked after the encoding needed them. | DAX CFD has no aggressor split, so delta is set to 0 by design (backtest/dax_data.py:100-106) [checked] | Known |
| 5b | Missing values read as zero, plus look-ahead. The volume profile was 300-690 points off. | B075, B084, B136, B103, B102, B141 (C3, P7) | Mostly fixed |
| 5c | Free data was not fetched. | OI metrics from 2020-09, bookDepth from 2023 (gap review G5) | Fetch posted 10-13 |
| 5d | Snapshots every 15 minutes, for traders who act on 1-5 minute bars and footprint. | PROBE_PLAN S4 arm | Known. Open. |

### Step 6. Backtest
| # | Mistake | Evidence | Status |
|---|---|---|---|
| 6a | The main simulators have never been shown to find a planted edge. Every "no edge" from them assumes they would see one. | Planted-edge tests exist only in research/test_p4_corrected.py and the candle pilot. There are none in backtest/ (tom_bt.py, tom_dax_bt.py, sim.py) [checked by search]. | Known (postmortem 8.3). Card never filed [checked] |
| 6b | Touch fills, bid-only DAX bars, testnet fills taken as truth, stop slippage 0, backtest venue differs from execution venue. | Gap review G2-G4, G7, G8 | Known. Cards ready for G1, G4, G6 |
| 6c | Tests run away from the trader's market were filed as verdicts. | Postmortem P11 | Known |

### Step 7. Decide
| # | Mistake | Evidence | Status |
|---|---|---|---|
| 7a | The rules are too strict and too loose at the same time. Too strict: a FAIL at low power is final (spec :49; power 7-35 % at Tom's numbers, G1). Too loose: the same 5 design sessions are reused for each redesign. | v1 engine 0 of 7. v2 price arm 2 of 5. Now the profile arm, with recall re-run as a new trial (q10). Each pass is another look at the same answer key. | New as a pair |
| 7b | No trial count across the project. | Gap review G6 | Known; card ready |
| 7c | No source has a point where it stops getting work. | Tom has had v1, v2 part A, part B, and 15 open cards | New |
| 7d | Findings repeat, but the decisions they point to are not made. | At least five reviews in three days (10-11 failures, 10-12 postmortem, 10-12 non-core audit, 10-13 gap review, 10-13 combo verdict, 10-13 DAX) reach the same core conclusions. The postmortem never reached fast-track. Mostly not made: park, reorder, the gross-edge gate, the INCONCLUSIVE rule. | New |

### Step 8. Run live
| # | Mistake | Evidence | Status |
|---|---|---|---|
| 8a | The exit was built before the entrance: a live testnet stack runs, and no strategy has passed S3. | 79 % of testnet trades came from turn_of_candle, which failed its backtest and "pays its fees and nothing else" (bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:140). 97 % of exits are time exits (GO_LIVE_BAR.md status). Its safety rules slow research code: never edit a file it imports, only the supervisor restarts, halt q2 still open. | Parts known (P10). Framing new. |
| 8b | The go-live bar counts synthetic testnet fills. | Gap review G3 | Known. Your decision is open. |

### Step 9. Run the project
| # | Mistake | Evidence | Status |
|---|---|---|---|
| 9a | The apparatus has outgrown the research. | 1,246 non-merge commits on fast-track, 10-01 to 10-13. By subject keyword: about 44 % bookkeeping (claim, release, lane health, relay, sync, desk), about 20 % research, backtest or extraction, about 13 % prompts and process docs [checked; keyword regex, approximate]. The OPS group holds 760 of 1,722 files (PROJECT_MAP.md). 426 research .md files, 125 cards. NEXT_SESSION.md is mostly coordination: worktrees, relay kicks, token audits. | Partly known (P9). Counts new. |
| 9b | Simple jobs fail on unrelated gates. | Qriptal scoring was stopped by a red Java build check (fb7a3daf) | New |
| 9c | Attention goes to coordination first. | The handoff note on 10-13 reads "budget: Jis ~5% of Claude weekly left" (NEXT_SESSION.md:2) | New |

## 3. The pattern, and the fix
Five patterns run through the steps:
- **F1. Build first, check feasibility last.** Steps 0, 4, 5 and 8.
- **F2. Person first, market second.** Steps 0 and 1.
- **F3. A long translation chain, measured only at its end.** It runs video, caption, machine translation, extract, rule,
  Java, 15-minute snapshot, simulator, verdict. That is 8 hops, and the first per-hop check (recall) came on 10-11.
- **F4. Decision rules both too strict and too loose.** Step 7.
- **F5. Apparatus over measurement.** Step 9.

The fix is a gate answered in writing before anything is built. A "no" at any line stops the build. Proposed as items 0a-0f
ahead of PRE_REG_TEMPLATE item 1:
1. **Cost.** What is the smallest stop or target this idea uses? On BTC, fees stay under 0.25 R only with a stop of at least
   0.40 % with taker legs, or 0.20 % with a maker entry. Smaller: no build.
2. **Gross.** Does a cheap fixed-horizon check on existing data show a raw move of at least 2 times the round-trip cost?
   (layer_combo_verdict s5)
3. **Record.** Does the source have dated calls or trades we can score on BTC data? Score them first (B162 is the template).
   No record means the source is a hypothesis, never a core.
4. **Data.** Does BTC history hold every input the source reads? A missing input is NOT_IN_DATA, and nothing is built on it.
5. **Power.** How many trades does the dev window give, and what edge can that detect? If that edge is larger than the claimed
   one, write INCONCLUSIVE in advance, or don't run.
6. **Kill.** What result ends this source for good, and how many redesigns are allowed before it?

## 4. What to apply for BTC, ranked [view]
1. **Score Qriptal's posted calls (B162).**
   - Why first: BTC, explicit entry/stop/target (no provenance gap), dated calls, free klines, no engine.
   - His self-reported numbers: 86 setups, 67.1 % wins, average win 3.99 %, average loss 0.63 % (BUGS.md:275). That works out
     to about +2.5 % per trade before fees [checked arithmetic]. That is implausibly high, which is exactly why it is scored
     before anything else.
   - Stops near 0.6 % pass the cost gate.
   - Cost: one Sonnet or DSA session. It is a script on klines, so it does not need the Java build gate.
2. **CryptoCred at home.**
   - BTC, daily and 4h bars, invalidation stops, price structure only (no order flow needed).
   - Card cryptocred-home-fit-audit exists (refined, p4). Raise it to p1.
   - Caveat: daily bars since 2019 give few setups, so power (G1) applies.
3. **Your own reads.**
   - Adopt the missed-trades capture: minute, side, invalidation and target for every read.
   - After a few weeks that gives a hit rate and MFE/MAE on BTC with exact timestamps.
   - Compute the indicators you actually use (BB, RSI, StochRSI) so each read can be reproduced.
4. **Order-flow ideas as a BTC-native layer.**
   - The ideas: Tom's "selling surplus" and "absorbed", Fabio's CVD pressure.
   - Run them with stops of at least 0.20 %, maker entry and trade-through fills (G4 first).
   - Fabio's order-flow model had a median gross of +0.13 R and a fee drag of about 0.66 R at his tight stops
     (backtest/layers/fabio/FABIO_OF_REPORT.md:127-128). The same signal has never been tested at a stop the fees allow.
   - Labels: rules from their words; BTC numbers NO-SOURCE, rank-based within the session.
5. **Move size, not direction.**
   - Volume forecasts the size of the next bar's move, not its direction
     (volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:12: correlation 0.42-0.49 with move size).
   - Use it for sizing and for skipping quiet periods.
   - A Deribit options volatility trade would be a NO-SOURCE research test. It works only if our forecast beats implied
     volatility.

**Stop or pause:**
- the Tom v2 DAX chain (Q6, Q7, the profile arm);
- the Fabio NQ home-market test;
- new intraday taker encodings;
- further review documents, this one included, until the decisions in section 5 are made.

## 5. Decisions for you (not filed)
I left these off OPERATOR_DECISIONS.md on purpose. A session acts on an unanswered decision's recommended option after 24 h
(NEXT_SESSION.md step 1), and these change direction. Tell me which to file.

| # | Decision | Recommended |
|---|---|---|
| d1 | q11: buy FDAX trades for Tom's 7 sessions? | No, park Tom as discretionary now |
| d2 | Re-order the queue | Qriptal scoring (B162) and cryptocred-home-fit-audit to p1; pause the Tom v2 and Fabio v2 home-market chains |
| d3 | Adopt the six-line gate (section 3) as items 0a-0f of PRE_REG_TEMPLATE | Yes |
| d4 | Doctrine: your 09-23 "Tom is core" vs the 10-10 "promotion to core uses the S3 bar, never opinion" | Let S3 decide what is core. Changing the doctrine is your edit only (VISION change rule, :5). |
| d5 | Merge TRANSLATION_POSTMORTEM_2026-10-12.md into fast-track | Yes. It is the only review with the simulator-validation list. |
| d6 | File the simulator-validation card: planted edge in tom_bt/sim, a null that includes fees, a trade-list diff | Yes |

## 6. Where I could be wrong
- FDAX data is cheap. If you value knowing whether Tom can be coded at all, the one-shot costs dollars and one session.
  My "not now" is about attention, not money.
- Qriptal and CryptoCred may have no edge either. Scoring them answers that cheaply; it does not promise a pass.
- The commit categories come from keyword matching on commit subjects. The split is approximate, and 12 % fell into "other".
- The process may be heavy because three machines and several AI lanes need it. I can't tell from here which parts are
  optional.
- The Databento coverage and pricing come from a search snippet. The page did not open from this container.
- The "+2.5 % per trade" takes Qriptal's self-reported averages at face value. Real fills, fees and missed entries will lower it.

## 7. Sources
- Databento, "Eurex now available": https://databento.com/blog/eurex-now-available [search]
- Databento catalog, XEUR.EOBI FDXM: https://databento.com/catalog/xeur/XEUR.EOBI/futures/FDXM [search]
