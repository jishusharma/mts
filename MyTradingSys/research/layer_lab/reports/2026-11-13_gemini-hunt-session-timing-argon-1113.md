# Report: Gemini Hunt Session Timing Argon 1113

- **Date:** 2026-11-13 (UTC)
- **Task ID:** `gemini-hunt-session-timing-argon-1113`
- **Output Artifact:** `MyTradingSys/research/tf_iteration3_1113/hunt_session_timing/argon.md`
- **Verification Command:** `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tf_iteration3_1113/hunt_session_timing/argon.md`
- **Verification Result:** PASS (0 problems)

---

## Findings Summary

1. **Layer Under Investigation:**
   - Catalogued in `MyTradingSys/system/LAYERS.md:130-148` as `Session / timing (session levels, turn of candle, session momentum) (session_timing)`.
   - Implementation:
     - `MyTradingSys/backtest/layers/session/session_momentum.py:1-118`
     - `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:1-75`
     - `MyTradingSys/backtest/layers/session_levels/session_levels.py:1-123`
   - Specifications & Results:
     - `MyTradingSys/backtest/layers/FORMULAS.md:380-405`
     - `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:1-43`
     - `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:1-43`
     - `src/main/java/datafeed/MarketDataSnapshot.java:933-995`

2. **Key 5-Pattern Gap Findings:**
   - **Pattern 1 (Our number labelled as his):**
     - Academic paper (Shanaev et al. 2023) has no direction or cost model; repo hardcoded `side = "long"` (`NO-SOURCE`) and traded every 15 minutes (`MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:59`), generating 81% of testnet trades (`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:33`) that paid fees and nothing else.
     - `MyTradingSys/backtest/layers/session_levels/session_levels.py:22-25` hardcodes `ASIA_END_MIN = 480` (08:00 UTC), `US_OPEN_MIN = 840` (14:00 UTC), `FAIL_WINDOW_MIN = 60`, `FEE = 0.0005`, `MIN_PREV_BARS = 1400` as synthetic placeholders (`OURS`).
     - `src/main/java/datafeed/MarketDataSnapshot.java:933-995` invents unsourced `0.5` and `0.7` day-range ratios (`OURS`).
   - **Pattern 2 (Named often, never coded):**
     - The 30-minute sit-on-hands gate at cash open (15:30 to 16:00 CET) taught extensively by Tom (`Of_wlv3xaZo`) and Fabio (`DyS79Eb92Ug [04:14]`) has zero implementation in backtest layers.
     - Initial Balance regime classification (narrow IB rubber-band trend day vs wide IB opening hedging balance play) (`K8qtT2_axPo`, `1utSjHs_Mq8`, `StaphlRH8NQ [08:10]`, `k0zm5NYn0IQ`) is completely uncoded.
     - Break below IB invalidating longs (`Khgj5q1-ln8 [10:35]`) is uncoded.
     - Candle close confirmation of volume delta dominance and absorption (`Is1HvdfQm5c [1:58:11]`, `Pz8f0wWW12M [15:16, 18:15]`) is uncoded.
   - **Pattern 3 (One word, many claims):**
     - "Session momentum": academic Shen et al. 2022 first-half-hour to last-half-hour sign drift vs Fabio's order-flow breakout momentum above session high (`DyS79Eb92Ug [18:52]`).
     - "Turn of candle": academic Shanaev et al. 2023 minute-0 calendar spike vs Fabio's candle-close confirmation of absorption/dominance (`Is1HvdfQm5c`, `Pz8f0wWW12M`).
     - "Initial balance": 30m cash open range for trend/balance prediction (`StaphlRH8NQ`, `K8qtT2_axPo`) vs Fabio's IVB directional breakout framing (`cUTsoU-15Tc [10:50]`, `Khgj5q1-ln8 [10:35]`) vs Java snapshot's 00:00 UTC midnight range (`src/main/java/datafeed/MarketDataSnapshot.java:933-995`).
   - **Pattern 4 (Method lost in translation):**
     - Causal PDH/PDL probe and failure: Tom checks whether overnight/London price enters outside previous day range and fails to accept, quickly traversing yesterday's balance (`Of_wlv3xaZo`). Our code in `MyTradingSys/backtest/layers/session_levels/session_levels.py:1-123` tested a mechanical tick touch + 60m close back below level on 1m BTC bars without checking acceptance, volume delta, or value area boundaries.
     - Candle timing: Fabio waits for the candle to close to verify that delta absorption or aggression completed dominance before acting (`Is1HvdfQm5c [1:58:11]`, `Pz8f0wWW12M [15:16]`). Our code in `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:1-75` entered 1 minute before the 15m candle open (`lead_minutes = 1`) or at minute 0 blindly without looking at the tape.
   - **Pattern 5 (Transfer assumed):**
     - Transfer of equity cash session dynamics (US 15:30-22:00 CET, DAX 08:30-17:35 CET) directly onto 24/7 continuous Bitcoin perpetual futures anchored to 00:00 UTC midnight (`MyTradingSys/backtest/layers/session/session_momentum.py:1-118`, `MyTradingSys/backtest/layers/session_levels/session_levels.py:1-123`).
     - Ignoring Tom's explicit warning: 24-hour profiles distort the balance vs trend classification because overnight low volume distorts the Value Area calculation (`Of_wlv3xaZo`).

3. **Verifications & Citations:**
   - All 35 transcript quotes verified verbatim against canonical text in `raw_transcripts_canonical/` (`Of_wlv3xaZo`, `DyS79Eb92Ug`, `cUTsoU-15Tc`, `StaphlRH8NQ`, `K8qtT2_axPo`, `1utSjHs_Mq8`, `k0zm5NYn0IQ`, `Khgj5q1-ln8`, `Pz8f0wWW12M`, `T6hDJcHrVBM`, `BB3c8visnkI`, `zAwEX_tRUfE`, `QClPWDJ-BrU`, `9IliXww64uM`, `5Ljfwvtktek`, `Is1HvdfQm5c`).
   - All file:line citations validated by `verify_extract_quotes.py`.
