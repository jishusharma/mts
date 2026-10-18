# What the DAX tests prove about Tom, and what is missing (2026-10-13, cloud, read-only)

Session: MTS-2026-10-13-1440Z-CLD-ANA-layer-combo. Base: origin/fast-track 28c86374. No code, card or live-path change.
Operator ask (verbatim): "What do you think about the testing on DAX? What does it prove? Does it prove that Tom is wrong? Or does it prove that we have not found a way of back testing and applying the concepts of trading properly? So what is exactly missing to make things profitable?"
Method: 5 parallel evidence readers (DAX chain, Tom fidelity, management, power/method, cross-layer pattern; 91 cited findings), two steelmen (Tom-has-no-edge vs method-is-the-gap), one synthesis. Spot-checked by the parent session against the files: dax_data.py:100-106 (CFD delta forced to 0), RECALL_DAX_V2.md:24-31 and :64, RECALL_DAX.md:3-7, SpikeFadeDetector.java:232-233, k0zm5NYn0IQ_raw.txt:19, TOM_LAYER_V2_SPEC.md:22-30, TOM_CORE_BT.md:275. All matched.
Paths below are relative to MyTradingSys/research/tom_transfer_2026-10-11/ unless given in full.

## Short answer
No. The DAX work does not show that Tom is wrong, and it does not show that he is right either. The only DAX profit table is a one-month pipeline test labelled "NOT a result" (DAX_BT_REPORT.md:1). The newer chain stopped at a matching check before any P&L was computed (RECALL_DAX_V2.md:3-8). What DAX did show is that our code is not Tom yet. The old engine matched 0 of his 7 entries. The new one matched 2 of 5 sessions, and a random clock does that well 16% of the time. Tom says he decides from footprint, delta and the order book, and our DAX data has none of these, so we have only tested the part of his method that candles can show. I can't tell you whether he has an edge at all. There is no verified record, so today's evidence fits "we haven't found it" and "there is nothing to find" equally well.

## What the DAX work has actually done
| Test | Checked | Result | Can prove | Cannot prove |
|---|---|---|---|---|
| Recall v1 (RECALL_DAX.md:3-7) | Does the old engine fire at his 7 entries? | 0 of 7 | The old engine cannot represent his trades on CFD data: it needs 3 proofs and the feed allows at most 2 (DAX_BT_REPORT.md:95) | Anything about Tom. The 0 was certain before the test ran |
| Smoke backtest (DAX_BT_REPORT.md:1, :32, :78) | P&L of the old engine, January 2026 only | Pre-registered rule: 0 trades. Relaxed arms: 4% wins, net -0.53R | That the pipeline runs | Tom's P&L. Its stops were 8-14 points against his 20-63, and an audit found 8 HIGH defects in the harness |
| Recall v2 (RECALL_DAX_V2.md:24-31) | Price-only fade detector at his 5 sessions | Idea alone: 4 of 5 (random 0.3%). With at least 1 proof: 2 of 5 (random 15.7%) | Candles find his *days*, not his *entries* | Edge. The 95% range for 2 of 5 is 5-85% |
| Profile parity (PROFILE_PARITY.md:6-8, :103) | Our CFD volume profile against the profile he draws | NOT_IN_DATA | Nothing yet. Whether they match is unknown | That the two volumes differ. Its one "mismatch" compares unlike ranges |

## Does it prove Tom is wrong?
No. Two claims have to be kept apart.

**Proven: our encoding has no edge on BTC.** Over 4,417 trades it made gross -0.07R, with a 95% range of -0.11 to -0.03 (TOM_CORE_BT.md:337). The test was big enough to detect an edge of about 0.06R. Stops the size of Tom's also lose to BTC fees by arithmetic: costs run 0.39-1.27R per trade against his claimed edge of 0-0.35R (TOM_LAYER_V2_SPEC.md:27-39, :46-48). But that encoding matched 0 of his 7 real trades, so it measured our caricature of him.

**Not proven: Tom has no edge.** No P&L test of anything that fires where he fires has run on his home market (tasks/tom-v2-dax-dev-backtest.json:23, result empty).

**Also not proven: he has one.** The repo holds no record for him (backtest_gap_review_2026-10-13/REPORT.md:179-181). His videos show trades he chose to publish (spec :16-17). His own numbers allow an edge of 0.00R (spec :27-30).

**What would settle it:** a pre-registered run on FDAX (the Eurex DAX future he trades) with:
- real volume, split by buyers and sellers;
- his stop sizes;
- exits priced on the ask side;
- fills counted only when price trades through the level;
- 211-3,059 trades, depending on where in his range the truth sits (REPORT.md:92-99).

A 95% range that excludes his claimed edge counts against him. A lower bound above zero after costs, and above random entry, counts for him.

## What is missing (ranked)
1. **The data he reads.** On the CFD feed, delta is forced to 0 (dax_data.py:100-106). There is no footprint code anywhere (0 hits in src/main/java). The v2 detector marks his core idea and his order-flow proofs as NOT_IN_DATA (SpikeFadeDetector.java:232-233). The idea condition alone fires on 46% of days (RECALL_DAX_V2.md:64), and in his words it is order flow that picks his day (k0zm5NYn0IQ_raw.txt:19).
   - **Fix:** FDAX trade data marked with the aggressor side (whether the buyer or the seller crossed the spread). It also removes an error of about 100 points in converting his futures prices to CFD prices, against a 20-point tolerance (RECALL_DAX_V2.md:84-86).
   - **Cost:** operator money, then Sonnet.
2. **A verified Tom edge.** All we have is a marketing bio (ANGLE_TRADER_SOURCES.md:26-27), and a perfect copy of a method with no edge earns nothing.
   - **Fix:** search for audited results.
   - **Cost:** Sonnet.
3. **Power and a fair verdict.** Power here means the chance of detecting an edge that is really there. The frozen pass bar has 7-35% across most of his range, and a FAIL is final (REPORT.md:92-99; spec :49).
   - **Fix:** write INCONCLUSIVE below 80% power, and pool FDAX with ES (the S&P 500 future) or extend the test forward in time.
   - **Cost:** operator decision, T0.
4. **Ground truth.** There are 12 trade groups and 0 certified executions (TOM_TRADE_LEDGER.md:5). Three of the 5 design sessions had losing first attempts he never logged (spec :135). The check set holds only 2 trades.
   - **Fix:** card tom-check-set-find-frames-only-tom-trade, plus a label for the proof he cites at each entry.
   - **Cost:** Sonnet.
5. **Stand-ins that don't match his words.**
   - Rule A-C2 makes session S3 unreachable at any proof count (SpikeFadeDetector.java:176-177; RECALL_DAX_V2.md:40-41).
   - Proof A-P7 can only be true after the target has already been hit.
   - Bars are bid-only for a family that only shorts, and an order counts as filled when price merely touches it (REPORT.md G2, G4).
   - **Cost:** Sonnet.
6. **His management.** Adding to positions, partial exits and stop moves show up in most of his trades (TOM_TRADE_LEDGER.md:63). None of it was simulated (spec :383). It comes second, because exits cannot create an edge the entries lack (mfe_exit_2026-10-13/REPORT.md:59-63).
   - **Cost:** Sonnet.
7. **The uncomfortable ones.**
   - The edge may be discretionary and not codable at all: "You can't do it with just a candlestick" (n7ZSkjb7JXs_raw.txt:19). He also reads sentiment and news (spec :62, :79).
   - A DAX pass would not trade for MTS, whose mandate is BTC (PROJECT_VISION.md:211). On BTC, stops his size cannot cover fees.
   - **Cost:** operator judgment.

## A decisive next experiment
**Question:** does the order flow Tom names appear at his entries, and only there?

- **Data:** FDAX trades marked with the aggressor side. Cover his 5 design sessions and the 2 check sessions (T11, T12), plus a random sample of other days in the development period on which the idea condition fires. Draw that sample with a fixed seed before reading any data.
- **Proofs, in his words only:**
  - "in these last two candles we had a selling surplus" (in delta);
  - "a lot was simply absorbed up here" (k0zm5NYn0IQ_raw.txt:19).
- **Settings:** where he gives no number, rank within the session (spec :22-23). Take the chart timeframe from his frames. Use his own FDAX prices, so no conversion is needed.
- **PASS** (the spec's existing bar), all three needed:
  - the proof appears within one stop-width of his entry on at least 4 of 5 sessions;
  - random instants do that well no more than 5% of the time;
  - both check sessions hold.

  Then fund the full FDAX P&L run.
- **FAIL:** 2 of 5 or fewer, or random instants do that well more than 5% of the time. Even on the right data, his named triggers would then not pick out his entries. Park the coded layer as discretionary.
- **Otherwise** (3 of 5, or 1 of 2 check sessions): INCONCLUSIVE. Grow the check set first.
- **Cost:** one data purchase (operator) and one Sonnet session. The test removes three excuses at once (wrong data, the price-conversion error, missing proofs) and does not need hundreds of trades.
- **Timing:** I'd run it before the queued profile arm on CFD volume (OPERATOR_DECISIONS.md:333-336). The profile check on that data already came back NOT_IN_DATA.

## Where I could be wrong
- **The one positive may be circular.** The idea alone hit 4 of 5, but that is in-sample: the rules were written from those same sessions (spec :197-201).
- **A rough proxy already failed.** BTC v1 used bar-level buyer/seller proxies on data that does carry the split, and it still lost money. That leans toward "nothing to find".
- **The experiment can fail even if Tom is skilled.** Footprint reading may not reduce to rules. A FAIL would then end the coded route without disproving him.
- **CFD volume may be close enough to FDAX volume.** That is untested, not refuted.
- **The power numbers may be too pessimistic.** They assume his stated reward-to-risk of 1.5-2, but his entries plan about 6 (spec :24). If that holds, a real edge would be easier to detect than I've said.
