# Tom engine read 2026-10-17 10:03Z (alert #413): ct_long below zone, cvd_aligned, stale swings

Card tom-ctlong-below-zone-cvd-aligned-audit. Report only; no live code touched. Evidence limit: the 10:05:13Z snapshot JSON is runtime data and is not in the repo, so values come from `research/live_reads/2026-10-17_live_market_1017/READ.md:31` (the 10:06Z read); every code claim below is file:line on the checked-in code.

## (1) ct_long at weekly_val 81603.48 stays WAIT_PROOF with price 66 pts below the zone
- Zone is kept: `tierFor` (SetupCandidatesBuilder.java:52-53) uses `abs(price - zone)/price*100`; 66/81537.8 = 0.081% <= 0.1 -> `trigger_ready`. Distance is absolute, so a zone ABOVE price counts as "at the zone".
- `determineSetupType` (SetupCandidatesBuilder.java:441-443): a `val` zone yields `ct_long` for any price; nothing tests whether price is above or below the zone. The only side info is `substate` "below" (line 222), which `verdict.compute_verdict` (MyTradingSys/backtest/verdict.py:106-140) never reads.
- Verdict path: net_rr 3.32 >= floor, tier trigger_ready, proof 1 < 3 -> `WAIT_PROOF "proof 1"` (verdict.py:122). The below_val + falling-CVD guard (verdict.py:132-134) fires only on SETUP_FORMING/SETUP_CONFIRMED, so it is unreachable at proof 1.
- Answer: WAIT_PROOF is the code working as written, but there is no "zone lost / traded through and accepted" state: a long limit at a zone price already lost stays a live candidate (entry 81603.48 is above market). Tom's invalidation is a state (READ.md:44, viT_VzF5Fsw). Design gap, not a crash. OURS rule (engine ct_long is OURS per READ.md:42), no SOURCED quote needed for the finding. Card: tom-ctlong-zone-lost-state.

## (2) cvd_aligned True (candidate proof) vs snapshot cvd_trade_flow_aligned False
- Two different definitions, same name stem:
  - Candidate: SetupCandidatesBuilder.java:841-857 uses main `cvd.slope` first (rising+netDelta>0 or falling+netDelta<0), falls back to `cvd_recent.slope_1h` only when the main slope is flat.
  - Snapshot condition: MarketDataSnapshot.java:320-323 uses `slope_1h` only, no main slope, no fallback. Live-only variant hard-set false at MarketDataSnapshot.java:1202.
  So main slope falling with 1m net delta < 0 (READ.md: flush, taker delta -158 BTC) gives candidate True while slope_1h flat/rising gives snapshot False. Both can be right; the divergence is a definition split, not a runtime fault. PROOF_DIR: no symbol of that name exists in checked-in code; the nearest is `proof_dir_of` (verdict.py:47-63), which is a different thing (proof_direction_status from the math object) and does not use either flag.
- REAL DEFECT (probable): `cvdAligned` carries no trade direction. `countSignals(direction)` adds it with `if (cvdAligned) count++` (SetupCandidatesBuilder.java:600) for longs and shorts alike. Falling CVD + negative net delta = "aligned" with a SHORT, yet it is counted as a proof for the ct_long. Deduction from the read: rejection wick NONE, finished auction false, delta flip false (absorption_detected, line 593, is not shown in the read: unchecked), volume spike not counted (B144, line ~597), speed not counted (D4), so the single proof 1 in READ.md:31 is most likely cvd_aligned; READ.md calls it "speed only", which the code (D4 comment) says cannot be counted. Not verified against the snapshot JSON.
- Card: tom-cvd-aligned-direction-blind (live-path change: test needed for long with falling CVD must count 0).

## (3) stale 15m/1d swing flags
- Flag: MarketDataSnapshot.java:823 `stale = swingHigh < price || swingLow > price`. Swing high/low are close pivots inside a 16-bar (15m) / 7-bar (1d) lookback (lines 806-822), so a flush that closes below the pivot close sets `stale` although the bar range still contains the price. B065 (SetupCandidatesBuilder.java:326-342) then drops that tf's swing zones; 1d is not in that gate (only 1h/15m/5m), 1d stale has no consumer.
- Answer: the flag means "price broke the swing", not "data is old"; the behaviour (dropping a broken swing zone) is consistent with Tom's invalidation. Naming only. Does not touch the weekly_val zone of this read (weekly zones are not gated by it, line 299-301). No defect; note only. The actual stale values at 10:05Z are not in the repo (limit above).

## Defect list
1. tom-cvd-aligned-direction-blind: SetupCandidatesBuilder.java:600 counts CVD alignment for the wrong side (probable, needs snapshot check).
2. tom-ctlong-zone-lost-state: no zone-lost/accepted-through state for ct_long when price is past the zone (design gap).
3. No defect: cvd_aligned definition split (note), stale-flag semantics (note).
