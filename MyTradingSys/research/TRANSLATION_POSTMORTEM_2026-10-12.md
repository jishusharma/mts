# TRANSLATION POSTMORTEM: Tom and Fabio layers, for the MTS Layer Lab (GPT), 2026-10-12

Written by Claude (Opus) in cloud session claude/sharp-carson-3xkd36 at the operator's request. Read-only on code.
The first version was printed in chat against origin/fast-track f7ef6d8. This file is revised against f5507dbb
(2026-10-12 14:11 IST) and includes the Codex/GPT revalidation from the same day.
Labels: numbers are quoted from the file named. [checked] = re-verified by this session. [view] = opinion.
[GPT] = stated by Codex/GPT in its app session, not on origin, not verified here.

## 0. Purpose
The operator asked for an independent review of three questions:
1. Do the encoded rules match what Tom and Fabio trade?
2. Can our backtests be trusted, given that backtesting is research and results depend on asset and market phase?
3. What should change, including the layers that were neglected while Tom and Fabio took all the attention?
No method can be guaranteed profitable. The realistic bar: an independently checked experiment that tells three
outcomes apart: a faulty reconstruction, a faulty measurement, and a genuine negative.

## 1. What changed while this session was idle (f7ef6d8 -> f5507dbb, 29 commits) [checked]
| Area | Change | Evidence |
|---|---|---|
| DAX harness | H5 fixed (07:05Z): the primary verdict now uses the per-instrument Java net_rr; gross-only selection removed; 40 tests | layer_lab/reports/2026-10-12_lab-dax-net-fee-verdict.md |
| DAX harness | H2 fixed (07:40Z): a split manifest is required; dev outcomes cannot touch holdout bars; holdout reservation is durable; 47 tests | .../2026-10-12_lab-dax-holdout-boundaries.md |
| DAX harness | H3 fixed (08:11Z): null is session-matched and keeps limit/no-fill mechanics. It needs a sourced session addendum (timezone, hours, Tom quote); none supplied yet. 53 tests | .../2026-10-12_lab-dax-session-null.md |
| DAX harness | H6 claimed and released at 14:00 IST with no delivery; card still ready (cause not recorded; the Codex allowance ran out around then) | commits 3efee7d2, fbcb49b3 |
| Lab queue | Ready: H6, H7 (readiness gate), H8 (trial identity), Fabio ledger audit, Tom ledger audit | layer_lab/INDEX.md |
| Tom ledger audit | Done in the Codex app work tree F:\MTS\mts-codex but NOT shipped (allowance limit). Claim file held by JIS-NUC. Reported in chat: FIX-FIRST, 4 HIGH + 4 MED, missing evidence named per row for all 37 rows [GPT] | system/claims/lab-audit-tom-ledger-frames.md |
| Spec cards | tom-layer-v2-spec and fabio-layer-v2-spec notes now carry the Codex corrections (section 4b). Both still ready, not started | system/tasks/*-layer-v2-spec.json |
| Data | Desk task posted for DSA, pending: DATA_COVERAGE_TOM_FABIO.md (input x market x HAVE/PARTIAL/MISSING, semantics, acquisition options, no purchase) | desk 20261012-071127-data-coverage-... |
| Split | tom-holdout-clean-split claimed (claim file present), not delivered | system/claims/tom-holdout-clean-split.md |
| Other | B163 alpha (NO-SOURCE chatbot spec, daily SMA200 long-flat): CAGR 20.5 / 8.7 / 2.0 % vs buy-and-hold 43.8 %, lower drawdown; no out-of-sample split reported | research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md |
| Control Room | Layer Board added: 3 active layers (Tom v2, Fabio v2, turn_of_candle) | system/control_room.json, B177 |

Tom ledger audit findings reported by Codex in chat [GPT]:
- T4/T9 and T6/T10 are the same chart episodes. This matches this session's check of the CSV [checked].
- T11's screenshot is titled "31.08", but the ledger gives the recording date, 09-01, as the trade date.
- One row claims a stop moved to 24220; the frame it cites shows no such label.
- An outcome row cites an earlier frame that still shows the position open.
- The captions support Tom saying they were stopped out before T3b. The stop fill itself is not on a frame.
- A T5 frame reads Continuous(FDXM)@EUREX (Mini-DAX), while the ledger says FDAX. This matters for contract
  cost and sizing.

## 2. Goal and status
- Goal: a net edge after fees on BTC perps (Deribit). Testnet first.
- Real money only after system/GO_LIVE_BAR.md holds for 30 days: 200 trades from configs that passed walk-forward,
  net > 0, profit factor > 1.2, time exits < 5 %, uptime > 95 %.
- Stages: S1 trustworthy measurements, S2 survive fees, S3 real out-of-sample edge, S4 testnet, S5 go-live.
- No core or layer has passed S3.

## 3. The path in four phases
1. **To about 09-28: extract from transcripts, build a Java engine, run live on BTC testnet.**
   - Engine (SetupCandidatesBuilder.java):
     - zones from volume profile and VWAP;
     - counted "proofs" (wick, absorption, delta flip, finished auction, CVD);
     - verdict ladder WATCH / SETUP_FORMING, gated by a net reward-to-risk value (net_rr).
   - Several gates had no source in Tom's words (NO-SOURCE): 0.1 % stop floor, 2-3.5R target window,
     net_rr floor 2.0, 8-bar time exit.
2. **09-28 to 10-03: provenance rule, then Fabio on BTC.**
   - Tom: 2 of 74 engine parameters trace to Tom's words. A second reader agreed only at kappa 0.446 (below 0.6).
   - Fabio, three attempts:
     - kline-proxy detectors: no edge;
     - order-flow model: 0 of 64 variants positive out of sample (median gross +0.13R, fee drag 0.66R);
     - v3 engine: 0 of 8 numeric parameters sourced; ran in shadow mode and stayed silent live.
   - Live Tom funnel: 25 alerts -> 6 attempts -> 5 limit orders never filled -> 1 fill closed by the time exit.
3. **10-03 to 10-09: unsourced gates removed, reruns, audits.**
   - Removing the stop floor left median stops at 0.082 %, so fees cost about 2.76R per trade (B146).
   - Tom on BTC: gross R -0.15 [-0.29, +0.04] before fees; random entries +0.22.
   - Live rule: 19 signals in an older run, 0 in 4.7 years now. The Tom holdout was read twice (B147).
   - Fabio v3 pre-registered test failed: model C -0.10R per day out of sample; A/B/D had no out-of-sample trades.
   - Big-move capture: 0 of 34 layer/side rows reached lift >= 1.15.
   - Exit policies: 1 of 114 cells positive in both splits.
   - Stop-buffer walk-forward (T081): out-of-fold net R negative in all 8 runs.
   - Measurement bugs found and fixed: volume profile 300-690 points off, naked-POC list frozen,
     live on spot vs backtests on perp.
   - Testnet: 79 % of trades were turn_of_candle, a layer that had failed its backtest; 97 % were time exits;
     uptime about 81 %.
4. **10-10 to 10-12: transfer probe on Tom's home market (DAX).**
   - Recall "0 of 7" on Tom's own DAX trades.
   - Trade ledgers rebuilt from video frames.
   - BACKTEST_FAILURES_RESEARCH.md sorts our failures into 8 classes and proposes a 12-item readiness checklist.
   - STOP list: no more BTC runs of the current encodings.
   - Codex Layer Lab set up as independent checker. Its audit found 8 HIGH + 6 MED harness defects;
     H1-H5 are now fixed. The v2 specs have not started.

## 4. Corrections, in both directions
### 4a. From this review to GPT's 12-Oct summary
1. H4 has shipped, and so have H2, H3 and H5 (section 1).
2. The Tom ledger has about 12 distinct trades, not 14: T4 = T9 and T6 = T10, with conflicting dates [checked].
3. "0 of 7" breaks down as follows:
   - 3 trades never touched within 60 minutes, because the futures-to-CFD price offset was 216-230 points and
     varies by day;
   - 2 trades later had their prices corrected (T2 entry, T3 stop);
   - 2 trades have unverified dates.
   It is a failed experiment, not a reliable fidelity score. Even "0 of 4" is provisional.
4. The current encoding cannot produce a DAX trade. Without aggressor data the proof ceiling is 1, while WATCH
   needs 3 and SETUP_FORMING needs 5. Only a v2 encoding is worth testing on DAX.
5. Profile parity will stay NOT_IN_DATA without FDAX data. The dev frames show no drawn POC/VAH/VAL lines,
   and the price offset varies by day.

### 4b. From GPT's revalidation to this review (accepted)
- Item 8 of the checklist says "a fixed bracket is a lower bound". That is not guaranteed: other management can
  make results better or worse.
- ">= 100 fills" is an administrative threshold, not a power analysis.
- Failed BTC tests describe the implementation and assumptions that were tested. They do not show that the traders
  lack an edge, but they are not without information either. This replaces an earlier line here that called them
  uninformative.
- The specs cover every ledger family; spike-fade is only the first one to implement.
- Separate quoted rules from rules seen in frames and rules we inferred.
- The ledger audits belong to Codex. Null expectations must include fees: a null is not zero net.

## 5. Recurring patterns
- **P1 Encoding fidelity: we test our reconstruction, not the trader.**
  - Tom's most common trade, fading the opening/pre-market spike, is not a candidate type.
  - The proofs Tom reads (profile shape P/b, inside bar, ledge of old highs, "no liquidity above") are not in the code.
  - Fabio's core ideas (hidden CVD pressure, effort vs result) exist only in v3, which is silent.
- **P2 Weak ground truth.**
  - Transcripts get prices wrong (stop "18,258" vs 24257 on the chart).
  - Recall reference values were later corrected; the ledger has duplicate trades and date conflicts.
  - Teaching videos show chosen trades, so they cannot show how often the trader trades, the hit rate, or the
    share of losers.
  - With about 12 Tom and 14 Fabio trades, a recall bar can be met by a rule that fires on every spike.
- **P3 The provenance paradox: the traders give concepts, not numbers.**
  - Sourced parameters: Tom 2 of 74, Fabio v3 0 of 8, other layers 17 of 81. No sourced exit anywhere.
  - Inventing numbers breaks the provenance rule. Deleting them makes the code degenerate: tiny stops, and a net_rr
    gate that lets 79:1 setups through.
  - BT-TUNED (backtests may tune toward big moves, labelled) reopens the door to overfitting.
  - The labels themselves are unstable (kappa 0.446).
- **P4 Market transfer with no theory of transfer.**
  - Tom trades FDAX/ES/GC at the Xetra open and pre-market, with stops of 0.08-0.26 %.
  - Fabio trades NQ at the NY cash open, with a median stop of 10.75 points (0.043 %).
  - BTC perps trade 24/7 with no session open, and cost 0.05 % per taker side.
  - Malkan (daily/weekly/monthly, Indian equities) was tested on BTC 1m-1h. CryptoCred (daily swing) was tested as
    15-minute brackets.
- **P5 Cost geometry.**
  - net_rr favours the setups that are worst after fees: a tiny stop next to a far target.
  - [view] For fees under 0.25R, a stop must be at least 0.40 % with taker fees on both legs, or at least 0.20 % with a
    maker entry and a taker exit. Both traders' native stops are 2-20 times smaller.
  - The Deribit maker fee of 0 is not verified (B146).
- **P6 Management modelled as a fixed bracket.**
  - The backtests use one trade at a time, an unsourced 8-bar timeout, and every match taken.
  - Both traders scale in, move the stop to breakeven, trail, take partials and re-enter.
  - Exit policies applied to the existing fires changed nothing, because the entries have no edge.
- **P7 Bugs in the measurement layer.**
  - B075/B084: look-ahead (live fields leaking into historical runs) and zeroed fields.
  - Missing data read as 0: book imbalance 0.0 read as ask-heavy, OI fail-open, funding silently 0.
  - DST off by one hour; higher-timeframe balance fields null.
  - Volume profile non-conserving, POC list frozen, VWAP anchor mismatched, spot vs perp.
  - On DAX, the missing aggressor split became fabricated half volume, which gives bearish delta labels (H6, open).
- **P8 Fills, nulls and statistics.**
  - Touch fills: CryptoCred's earlier PASS was an artefact of them. [view] P1's "adverse selection 0.02 bp" PASS
    was also measured with touch fills.
  - Nulls were not like-for-like (fixed for DAX by H3).
  - Holdout read twice; DAX holdout contained ledger days (fixed for DAX by H2).
  - Trial counts incomplete; iid bootstrap on clustered intraday trades.
  - False passes: P4 first run, best-of-18 cells, the volume study's DEV pattern.
- **P9 Process.**
  - The same model family wrote the encoding, its tests and its backtests (hence the Layer Lab).
  - Every worker report contained at least one wrong claim.
  - Documents drift from code. Example still live: control_room.json says "Kim & Hansen P4: 8 h window passes",
    void since 075e1c5.
  - About 375 research documents; much activity, little measurement of the trader.
- **P10 Testnet is a sensor, not a proving ground.** Failed layers still fire; the 10 USD minimum contract blocks
  runner splits; most exits are time exits. turn_of_candle is still on the Layer Board as active.
- **P11 Negatives from unfair tests were filed as verdicts** (section 6).

## 6. The neglected layers
| Layer | Home of the source | What we tested | Fair? | Verdict |
|---|---|---|---|---|
| Malkan RSI | Indian equities, daily/weekly/monthly swing | BTC 1m-1d, 10-bar horizon, 1 %/2 % brackets | No | No edge on 1m-1h; 4h n=17 and 1d n=5 are underpowered where Malkan actually trades |
| CryptoCred | BTC, daily/4h swing, invalidation stop | 15m brackets, touch fills | Market yes; timeframe and exits no | Negative. Invalidation-based (ATR) stops are least bad (-0.04 to -0.10R) but still negative |
| Positioning | Thresholds undefined in the source | Grid over thresholds | Source too thin | Out-of-sample -0.045 % |
| Session momentum | Academic, BTC | DST-correct | Yes | Sharpe 0.008 |
| Volume (553 trials), candles (0/108), RSI divergence, OI divergence, P4/T093 imbalance, T087 failed break | BTC-native or literature | Pre-registered, holdouts sealed | Yes | Fair negatives |
| Kurisko, MA ratio, options, VPIN | - | Spec only or partial | - | Untested |
| B163 alpha | Chatbot spec (NO-SOURCE) | Daily SMA200 long-flat | Research-only | Below buy-and-hold CAGR; no out-of-sample split |
One robust positive: volume and VPIN-type measures predict how big the next move is (correlation with next-bar
range 0.42-0.49; VPIN spikes t about 7). They do not predict its direction (correlation 0.01-0.04).
Home-fit audit cards exist for CryptoCred, Malkan and positioning; they are parked behind Tom/Fabio v2 part B.

## 7. Known and unknown
- **Fairly solid:**
  - The current encodings do not reproduce either trader.
  - BTC fees kill stops under 0.2 %.
  - The fair negatives in section 6 hold.
  - Move size is predictable; direction is not.
- **Unknown:** whether Tom or Fabio have an edge that can be encoded on their home markets; Malkan and CryptoCred
  at their own timeframes.
- **Possibly unknowable from the videos:** trade frequency and hit rate; FDAX and NQ volume truth without
  exchange data.
- **Never validated:** the simulator itself. It has no planted-edge or null control and no reconciliation with
  real testnet fills.

## 8. Reframes [view]
1. **Split each layer's question into three, each with its own data and pass bar:**
   (A) fidelity: did we encode the rules right?
   (B) home edge: does the method work where the trader trades?
   (C) transfer: does it survive on BTC after fees?
   BTC runs answered C while A and B were open.
2. **Find where the translation is lost.** Let a vision model read chart states using the written rules and decide
   "would Tom trade here?". Score it on the held-back ledger trades. This separates video -> words from
   words -> code.
3. **Validate the simulator before trusting any result:**
   - hand-calculated fixtures;
   - planted-edge recovery;
   - matched null controls that include fees (not zero net);
   - an independent implementation with a trade-list diff;
   - reconciliation with testnet fills.
4. **State transfer as a falsifiable hypothesis.** Example: scale-invariance in volatility units, using
   higher-timeframe structure and stops >= 0.4 %. Spike-fade at an "open" may have no BTC equivalent.
5. **Use move-size forecasts** as "when not to trade" and sizing layers, not as entry signals.
6. **Run one thing end to end before widening:** one family, one market, one exit model, both fill models.
7. **Strategic question for the operator:** if the edge lives in the open-session microstructure of futures,
   BTC perps may be the wrong instrument for Tom and Fabio. CryptoCred is the only BTC-native trader, and was
   tested least fairly.

## 9. Agreed next steps (MTS and GPT exchange, 2026-10-12)
| Owner | Next delivery | State at f5507dbb |
|---|---|---|
| Codex | Tom and Fabio ledger audits: exact missing evidence (frame, date, price) per row | Tom done locally, unshipped; Fabio ready |
| Codex | H6 unavailable order flow, H7 readiness gate, H8 trial identity | ready |
| Opus | tom-layer-v2-spec (all families, spike-fade first; quoted vs frame-observed vs inferred; unresolved numerics; required inputs), then tom-layer-v2-cost; fabio-layer-v2-spec | ready; notes updated |
| JIS-NB | tom-holdout-clean-split: design/check split grouped by trade, session and video; record prior exposure; done after duplicate and date fixes | claimed |
| DSA | Data coverage for Tom DAX and Fabio v2 proofs | pending |
| Claude refinement | Simulator-validation cards: written fill and event-ordering rules, hand fixtures, planted edge, fee-aware matched null, independent implementation, trade-list diff | NOT filed yet [checked] |
| Operator | Sourced session hours for the H3 null addendum (from Tom's words); FDAX/NQ data purchase only after a named gap | open |

Acceptance criteria to agree before implementation:
- fidelity on eligible check examples;
- false triggers on comparable non-setup periods;
- fire rate;
- touch and trade-through fills;
- uncertainty.

Selected winning examples can test reconstruction. They cannot show precision or profit.

The STOP list stays: no BTC runs of the current encodings, and no profitability claim until the fidelity and
simulator checks pass.

## 10. Open while the Codex allowance is spent
- Ship the Tom ledger audit from F:\MTS\mts-codex when the allowance resets: tasks.py done, codex_run.py index,
  commit, sync.py ship, release. No other session should redo it.
- H6 was released without a delivery; it stays ready.
- Fix the stale P4 "8 h passes" line on the Control Room.

## 11. Questions for GPT
1. Which past results still carry information, and for which question (A, B or C)?
2. With about 12 Tom and 14 Fabio trades, what is a fidelity test that cannot be gamed (precision, fire rate per
   day, design/check split)?
3. How should concept-only parameters get numbers without overfitting?
4. Can Fabio be tested at all without NQ trade data that carries the aggressor side?
5. What would convince you the simulator is correct?
6. Which neglected layer should be tested first on its home terms?
7. What pattern are we repeating that this review misses?

## 12. Files
- research/tom_transfer_2026-10-11/: ROADMAP, BACKTEST_FAILURES_RESEARCH, RECALL_DAX, DIAG_BTC, TOM_TRADE_LEDGER.csv,
  PROFILE_PARITY, PRE_REG_DAX
- research/fabio_transfer/FABIO_TRADE_LEDGER.md; research/P2_FABIO_V3_HOLDOUT_STATUS.md
- research/layer_lab/INDEX.md and reports/
- research/AUDIT_MAJOR_GAPS_2026-10-09.md; research/CONSOLIDATED_ROADMAP_2026-10-09.md;
  research/bigtrade_2026-10-09/FINDINGS.md
- research/LAYER_PROVENANCE_AUDIT.md; research/TOM_FABIO_REVIEW_2026-10-03.md; research/WHY_ENGINE_SILENT_2026-10-03.md
- system/LESSONS_LEARNED.md; system/GO_LIVE_BAR.md; system/LAYER_LAB.md; backtest/PRE_REG_TEMPLATE.md;
  PROJECT_VISION.md (DIRECTION UPDATE)
