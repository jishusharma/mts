# NKN-02 context design (frozen before results)
Frozen 2026-11-14. No backtest run, no outcome data seen. The common block of NK55_RULES_1114.md (splits, 12 bp, gates, BH, placebo, one value per OURS parameter) applies unchanged unless stated here.
Paths: REPO = <local-path> ; CACHE = <local-path>

- **Phase tested:** ONE primary cell per side = a regime TURN (not continuation). NK's words are about confirming a flip (a8RP5ftOfGo 00:08:50, PLJda-dtBIc 00:13:25), so the draft's "2 closes above SMA20 AND above SMA200" (fires in established uptrends) is demoted to a control.
  - **Long cell L-TURN:** cycle state at the day BEFORE the first confirming close is not BULL (BEAR or BASE; cycle = BTC state M shared by all coins, from `CACHE/mts_brains/phase_daily.csv` column `cycle`; BEAR = DD<=-20% and close<SMA200, BULL = close>W200 and DD>-20%, else BASE) AND coin trend phase at that same prior close is DOWN or RANGE (20d MA slope with 5-day lag plus ADX14>=20 DI direction, else RANGE; code = REPO/research/nkp1-session-rules-phase-1114_2026-11-14/phases.py, reuse, do not rewrite).
  - **Short cell S-TURN:** cycle BULL at the day before the first of the two closes under SMA20, coin phase UP or RANGE at that prior close.
  - Long and short are separate rows, never pooled. De-overlap: one open trade per coin. Cluster by day (BTC cycle is shared, so 20 coins overstate n).
  - **Controls (reported separately, never pooled):** see Cells table. Key control = same cell with a 1-close trigger (NK's own "trap" claim).
  - **Claim test (primary):** in L-TURN and in S-TURN, is the day-cluster CI low of the 2-close V0 above that of the 1-close V0? Verdict gates are the common-block gates on the 2-close rows only.
  - **Episode gate (OURS):** need >=15 independent turn episodes (distinct BTC-cycle turn dates; entries within 10 days of each other = one episode) across coins on DEV, else the cell is UNDERPOWERED. VAL regime-mix block must report episode count, not only signal count.

- **Context conditions:** (S = SOURCED video+time, O = OURS one value)
  1. S: two consecutive daily closes under SMA20 = bear flip (a8RP5ftOfGo 00:08:50; IjU9PpqvrI8 00:14:58, breakdown needs >=2 closes). Short trigger.
  2. S: an SMA200 break counts only if it holds 10-12 days (a8RP5ftOfGo 00:09:40). Use 10. Reading frozen: ALL 10 closes (t-9..t) < SMA200 ("sustain" = strict; the final-close-only reading is rejected). No run at 12 (second parameter).
  3. S: long re-entry after a drop under the 200 needs 2 daily closes above SMA200 and SMA50 (PLJda-dtBIc 00:13:25). Long trigger: close[t-1] and close[t] both > SMA20 and > SMA50, and close[t] > SMA200. The SMA20 leg is OURS (mirror of the sourced short trigger; NK states SMA20 only for the bear side). SMA = simple, not EMA (FzNDQm7wC_s 00:02:39).
  4. O: "after a drop" arming = close < SMA200 on at least 10 of the 30 days ending day t-2 (the day before the first confirming close). One value, no grid. (The 60-bar "any close" variant from the CONTEXT angle is rejected: one stray close arms it.)
  5. O: phase and cycle gates above, read at the prior close (look-ahead-free). The -20% and W200 thresholds come from the MTS BRAINS spec (OURS, not NK).
  6. S: stop = two closes back against the position (lmhqooBqJWU 00:07:26): long exits after 2 consecutive daily closes < SMA20, short after 2 closes > SMA20. This is also the "regime flips back" exit. Exit at the next daily open. O: 60-day time stop.
  7. O: R = max(structural, 0.5% of price, 0.6 x ATR14 daily). Structural = long: lowest low of the 10 daily bars ending at the signal day; short: highest high. R is the normalising unit; PRIMARY P&L is the close-based exit path (no intraday stop). A second non-gating column shows P&L with an intraday hard stop at 1R. Report per cell how often the floor beat the structural level.
  8. NOT_STATED by NK, not invented: index filter for this rule, time of day, VWAP, gap, volume.
  9. Weekly-close alternative (PLJda-dtBIc 00:14:26): control row only.

- **Crypto translation:**
  - Session/open: UTC daily bar, signal at the 00:00 UTC close, entry at the next 00:00 UTC open (OURS; Asia open, no quiet seam). Daily bars are a pure function of closed data, so one session only; NY-close daily NOT run (extra cell, no gain). The 1h control row uses UTC days, no session split.
  - Gap: NKN-02 has no gap element, nothing to replace. Weekly expiry, option chain, Nifty legs: do not translate, dropped.
  - Funding (8h, `CACHE/binance_futures/nkp1/<COIN>_funding.csv`, cols ts,rate; BTC starts 2020-01-01, verified): crowding veto as a CONTROL filter only. Skip long if mean funding of the 3 prior completed UTC days > its trailing 90-day 90th percentile; short mirror at the 10th percentile. OURS, one value. If the 2-close vs 1-close ordering is unchanged by the veto, drop the veto.
  - OI (`<COIN>_oi_daily.csv`, cols ts,oi; BTC starts 2020-09-02, verified): descriptive column only (5-day OI change before entry), never a gate.
  - BTC market filter: control row for alt longs only: BTC close > SMA200(BTC). NK's own index filter (SMA20/SMA50) belongs to NKN-03, not used here. Shorts: no BTC filter (cycle gate is already BTC-based).
  - CBP lean (4 bearish / 1 neutral / 1 bullish) and the Bible cycle clock: labels for the regime-mix line only, never gates.
  - Does NOT translate: NSE 15:30 session close, gap, expiry, index-futures/option legs. NK's 10-12 day hold was tuned to a stock tape (weak port, flagged).
  - Data: daily bars for the 20 coins = aggregate to UTC days from `CACHE/binance_spot/<COIN>_15m.npz` (keys t,o,h,l,c,v; verified, 20 coins, from 2019-01); 5 majors also have `CACHE/binance_spot_htf/<COIN>_1d.json` (rows [ts,o,h,l,c,v]) as an aggregation cross-check.

- **Layer agreement:** daily bars only; signal day = day of the second confirming close; every read uses data up to that close. Max 3 variants.
  - **V0** rule alone (conditions 1-7 inside the cell).
  - **V1** V0 + daily ADX agreement. Code `REPO/backtest/layers/adx/adx.py` `adx_di(high, low, close, n=14)` (verified exists). Long: ADX14>=20 and +DI>-DI at the signal close; short: ADX14>=20 and -DI>+DI. OURS: threshold 20, DI sign. Caveat: same indicator family as the phase label (read two bars earlier), so V1 may add little; run anyway to expose the dependency.
  - **V2** V1 + daily RSI14 Malkan regime. Code `REPO/backtest/layers/rsi/rsi_core.py` `rsi_core(closes, 14)` then `REPO/backtest/layers/rsi/malkan_40_60.py` `malkan_regime(rsi, 40, 60, 20)` (verified; labels BULL / BEAR / RANGE; BULL = min>=40 and max>=60 over 20 bars; BEAR = max<=60 and min<=40). Long needs BULL at the signal close, short needs BEAR. RSI 40/60 SOURCED (Malkan); the 20-bar lookback is the function default (OURS).
  - Dropped: WaveTrend (`backtest/layers/wavetrend/` exists but is an extension oscillator that reads overbought right after a flip, so it is anti-aligned by construction); funding as a layer (`funding_cvd_fade` closed FAIL; funding is used only as the context veto above); Tom/Fabio order-flow, pitchfork/trendlines, anchored volume profile (no daily history, discretionary pivots, or closed). No 144-cell grid on this rule.

- **Level type:** ONE level = daily SMA200 (SOURCED level: FzNDQm7wC_s 00:02:39, PLJda-dtBIc 00:13:25), computed through the signal-day close.
  - D = |close_signal - SMA200_signal| / ATR14_signal (ATR14 Wilder, daily).
  - AT-LEVEL: D <= 1.5 (OURS, one value; nothing about "near the 200" is SOURCED). AWAY-FROM-LEVEL: D > 1.5 (exact complement).
  - Pre-registered hypothesis: edge, if any, sits AT-LEVEL. The split runs on V0 2-close rows only and is DESCRIPTIVE (control rows, not extra primaries). Also report per cell: median SMA20-SMA200 gap in ATR, and days since the close crossed SMA200 (exposes that at-level longs may just be "recently flipped").
  - Pivot / value-area / buy-zone levels: not used (no NK link to this rule; the BTC-today map has no history).

- **Timeframes:** native DAILY is the rule (all primary rows). 15m and 4h: NOT expressible (the rule is defined on daily closes and daily SMA20/SMA200); no cells. 1h: only NK's own separate 1h SMA200 switch (a8RP5ftOfGo 00:13:14) as one control row (long while 1h close > SMA200(1h), exit on 1h close back under; entry next 1h open; descriptive, weak port). Weekly: one control row (PLJda-dtBIc 00:14:26), weekly close = Sunday 00:00 UTC close, daily SMA20/50/200 values at that close.

- **Cells:** all daily and 2-close unless stated; DEV/VAL split as the common block. PRIMARY = verdict plus BH family of 6. CONTROL = descriptive, never pooled, not in BH.

| # | Cell (phase x cycle) | Variant | Level | TF | Side | Trigger | Role |
|---|---|---|---|---|---|---|---|
| 1 | L-TURN | V0 | all | 1d | long | 2-close | PRIMARY |
| 2 | L-TURN | V1 | all | 1d | long | 2-close | PRIMARY |
| 3 | L-TURN | V2 | all | 1d | long | 2-close | PRIMARY |
| 4 | S-TURN | V0 | all | 1d | short | 2-close | PRIMARY |
| 5 | S-TURN | V1 | all | 1d | short | 2-close | PRIMARY |
| 6 | S-TURN | V2 | all | 1d | short | 2-close | PRIMARY |
| 7 | L-TURN | V0 | all | 1d | long | 1-close | CONTROL (key, trap claim) |
| 8 | S-TURN | V0 | all | 1d | short | 1-close | CONTROL (key, trap claim) |
| 9 | continuation UP x BULL (draft original, no drop-arming) | V0 | all | 1d | long | 2-close | CONTROL |
| 10 | continuation DOWN x BEAR (draft original short) | V0 | all | 1d | short | 2-close | CONTROL |
| 11 | L-TURN cell, mismatched direction | V0 | all | 1d | short | 2-close | CONTROL |
| 12 | S-TURN cell, mismatched direction | V0 | all | 1d | long | 2-close | CONTROL |
| 13 | random same-cell placebo (matched cycle + phase) | n/a | all | 1d | long | none | CONTROL |
| 14 | random same-cell placebo | n/a | all | 1d | short | none | CONTROL |
| 15 | MARKDOWN (BRAINS spec), descriptive | V0 | all | 1d | short | 2-close | CONTROL |
| 16 | L-TURN | V0 | AT | 1d | long | 2-close | CONTROL |
| 17 | L-TURN | V0 | AWAY | 1d | long | 2-close | CONTROL |
| 18 | S-TURN | V0 | AT | 1d | short | 2-close | CONTROL |
| 19 | S-TURN | V0 | AWAY | 1d | short | 2-close | CONTROL |
| 20 | L-TURN + funding veto | V0 | all | 1d | long | 2-close | CONTROL |
| 21 | L-TURN + funding veto | V0 | all | 1d | long | 1-close | CONTROL |
| 22 | S-TURN + funding veto | V0 | all | 1d | short | 2-close | CONTROL |
| 23 | S-TURN + funding veto | V0 | all | 1d | short | 1-close | CONTROL |
| 24 | L-TURN alts + BTC>SMA200 | V0 | all | 1d | long | 2-close | CONTROL |
| 25 | unconditioned draft (no phase/cycle) | V0 | all | 1d | long | 2-close | CONTROL |
| 26 | unconditioned draft (no phase/cycle) | V0 | all | 1d | short | 2-close | CONTROL |
| 27 | 1h SMA200 switch | V0 | all | 1h | long | 1h close > SMA200 | CONTROL |
| 28 | weekly-close re-entry (>SMA200 and >SMA50) | V0 | all | 1w | long | 1 weekly close | CONTROL |

  **total cells tried: 28 ; primary cells: 6**

- **Underpowered rule:** a cell with n VAL < 100 trade rows is UNDERPOWERED, not FAIL. For 100 <= n < 200 the cell may FAIL on the gates but can never PASS (common block n>=200 for PASS). Also UNDERPOWERED if DEV episodes < 15. Expect S-TURN, AT-level, 1h, weekly and V2 cells to land here; VAL is bear-heavy so L-TURN may be thin or one episode.

- **Open doubts:**
  1. The angles disagreed on the long trigger (SMA20 mirror vs NK's "200 and 50"); frozen as the union (both closes > SMA20 and SMA50, second > SMA200), stricter than either and possibly rare. If DEV L-TURN signals < 60 total, report that and do NOT loosen it.
  2. Whether NK's 200-DMA hold applies to longs or only validates shorts: Part 1 shows only the short side. Cycle gate and drop-arming (10 of 30) are OURS.
  3. 10 vs 12 day hold: only 10 run. "Sustain" read as every close; NK may mean only the latest.
  4. The close-based stop (open item in the synthesis) is now exercised, but SMA20-based, not structural; floor-vs-structural frequency must be reported.
  5. Fresh 10-coin holdout: NO OHLCV for fresh coins found in `CACHE/binance_fresh` (only `nk5_nyasia`) or `CACHE/binance_futures/nkp1` (funding/OI only, 46 coins). Bars must be fetched before the holdout row can run; until then verdicts rest on the 20 coins plus forward days.
  6. Funding/OI exist only from 2020; the 90-day percentile needs a warmup, so veto rows lose early DEV.
  7. V1 is nearly redundant with the phase gate (same ADX family); V2 may collapse n.
  8. `phases.py` was not read for exact look-ahead behaviour; the 11-14 review flagged a partial-day phase and a dead `phase_next_day` field in earlier studies. The programmer must confirm phase uses only completed days.
  9. Transfer of Indian-equity swing behaviour to 24/7 crypto is unproven. Prior phase fixes all FAILed; expected outcome is FAIL or UNDERPOWERED, and this design makes that decidable, not rescues the rule.
