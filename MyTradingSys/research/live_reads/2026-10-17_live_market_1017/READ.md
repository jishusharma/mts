# 2026-10-17 live market read (child of NB planning thread; observe, compare, log; zero screenshot reads)
<!-- Process: LIVE_MIRROR.md read. Testnet only; live tree, HALT files and orders untouched. No chart marks (G3 blind-marks rule: draw rebuild not done). -->

Source: `live_mirror.py brief` + _mirror files, all `mirror@2026-10-17 07:11Z` (git 06ba449b); BTC 1h klines from public Binance (free market data), fetched ~07:15Z.

## Now (mirror@2026-10-17 07:11Z)
- Price 81,594-81,612 (alert #409 07:07Z: NO_TRADE, no candidates, STATE TWOPEAK/in_va -> above_vah; QUAD flat: 1h price +0.11%, cvd +4, oi -0.010%).
- Daily VP poc 81,566.85 / vah 81,604.55 / val 81,498.98 (TWOPEAK). Weekly VP poc 83,422.12 / vah 83,879.91 / val 81,603.48: price sits at weekly VAL, ~1.8k under weekly POC. Prior-week POC 83,007.82.
- Session asia_europe_overlap, US open in ~382 min. 1h range 07Z: 81,620-81,654, volume 65 BTC (thin).
- Flags: HALT true, HALT_DAILY_LOSS true, AUTO_PAUSE false. daily_loss_monitor: breached_today false, 18 accounts at day-start equity 59.9998582 (flat, no positions/PnL movement). Auto-trader: every layer fire is `skipped_halt` (turn_of_candle toc_m14 1m: 06:15 long, 06:30 short, 06:45 short, 07:00 long; bracket_source SAMPLING). No trades opened.
- Supervisor loop_state 07:10:38Z: ok, wrapper/sm/java up, snapshot age 26 s, restarts_24h 0. Poll log: all kline layers alerts=0 errors=0 (cryptocred, fabio cvd_absorption 15m/1h silent).
- Tom: last alert present but keys unrecognised (B156, thesis text may be stale); snapshot tom/fabio fields null; consensus dump 05:23Z Tom WAIT_RR scalp_short 81,584 / 81,600 / 81,539.

## Compare with yesterday (2026-10-16; NEXT_SESSION AUTOPILOT-3, 10-15 live notes)
- Yesterday's last live thread note (10-15 12h swing map): price on the 12h lower BB (80,571), RSI 36.9; 1m bearish RSI-div after the 14:10 squeeze (~81.3k).
- Price path: 10-16 11Z spike to 82,941, 17Z flush to 80,809 (1.65k BTC volume), then recovery to 81.2-81.7k and a flat, low-volume grind (1h volumes 165-440 BTC) overnight to 81,654. Net: 24h range 80,809-82,941; price is +785 off the 17Z low, still under 10-16 midday.
- State changes: HALT still on since 10-15 08:00:19Z (operator clears it; NEXT_SESSION). HALT_DAILY_LOSS now also raised, but breach is false and equity flat; commit 57849029 makes testnet clear its own blind halt after 30 min of clean reads, so this flag may self-clear (not verified here). Code: live on 32077514 (AutoDeploy 10-16 06:01Z); CI green 2101fcec.
- Unchanged: layers fire only turn_of_candle, all skipped; no position exposure; recorder restart still open for operator.

## Report-level marks
- Layers applicable: turn_of_candle (fires, skipped by HALT), Tom (stale/unrecognised keys), Fabio cvd_absorption (silent), cryptocred (silent). Blind-marks: NONE placed (G3 audit rerun / draw rebuild pending). No claims row, no shots.
- Defaults taken (logged, not asked): no screenshots read; HALT left as is; HALT_DAILY_LOSS self-clear not tested.

## 10:00Z update (mirror@2026-10-17 10:01Z): 15m + 5m shots 8dc83a2a31ed / ac1adc2a255f
- Read: SET_8dc83a2a31ed_ac1adc2a255f.md (13 MATCH, 0 MISMATCH, 2 NOT_IN_DATA). Last read id: ac1adc2a255f. Open MISMATCH cards: none new.
- Moment: 09:59 flush 81,671 -> 81,550 in the last 19 s of the 15m bar (taker delta -158 BTC, OI +72), 5m RSI 35.18 under 40 with MA 51.4, price under 5m lower BB and day VWAP 81,574.9, under weekly VAL 81,603.5.
- HALT + HALT_DAILY_LOSS still raised; rsi 5m short and turn_of_candle long both `skipped_halt` at 10:00:31Z. Tom rejected (tom#411 net_rr, tom#412 WAIT_PROOF).
- Defaults taken (logged, not asked): shot.py engine not run (no scratch raw dir); fapi 1m klines fetched directly, closed bars + forming minute.

## 10:06Z Tom-concept read (operator ask: MTS engine read now, Tom concepts, correlate with the 15m/5m shots) mirror@2026-10-17 10:06Z
- Engine (snapshot 10:05:13Z, alert #413 10:03:13Z): TWOPEAK, price in daily VA (poc 81,537.95 / vah 81,657.01 / val 81,484.76), under weekly VAL 81,603.48 (weekly poc 83,422.12). Tom verdict WAIT_PROOF, ct_long @ weekly_val, entry 81,603.48, stop 81,500.5, target 82,297.86 (prior-day POC), gross/net R:R 6.74/3.32, proof 1 (speed only); rejection wick NONE, finished auction false, delta flip false, volume spike false (mag 0.59). Quad new_shorts (1h price -0.15%, cvd -232, OI +0.06%, nd15 -168). Scalp-short candidates at VWAP / +1s have net R:R -0.22 / 0.24 (gate fails).
- Daily POC drift: 81,566.85 (07:11Z) -> 81,568.35 (10:01Z) -> 81,537.95 (10:05Z); Tom's "two lower VPOCs after balance = no counter trades" (VOiy8mAALWA) is UNTESTED from one snapshot.
- Card filed: tom-ctlong-below-zone-cvd-aligned-audit (ct_long pending while price is below the zone; cvd_aligned True vs cvd_trade_flow_aligned False; stale 15m/1d swings).

## 10:15Z engine vs catalogue Tom setups (operator: "engine is the old code, we have new setups")
- Operator is right: engine ct_long/ct_short/scalp_* are OURS (SETUP_CATALOG TOM-2 gap list: "engine ct_short/ct_long at VAH/VAL zones and the 3 proofs bar"; LAYERS.md tom_core: STOP, no edge in 6 backtests, "being redefined as Tom v2"). The catalogue setups (G2) are not coded as live detectors yet (tom-btc-encode raw, tom-btc-eye-read blocked); only an eye read can apply them.
- By eye, TOM-7 (flat VWAP, balance): price at VWAP 81,575 = mid-range, "everything in between is noise" (4VXpUjhKG2U); edges are +1s 81,651 / day high 81,733 for shorts and -1s 81,498 / -2s 81,421 / day low 81,373 for longs. Engine's ct_long zone 81,603.48 sits at 64% of today's range (81,373-81,733), not at the bottom. 65% of volume since 10-16 18:00Z (25.3K of 38.7K BTC, OURS measure by bar typical price) traded below 81,603.48: a lower balance already formed there (TOM-2 "lower balance after rejection").
- Invalidation is a state (viT_VzF5Fsw: traded through and accepted); no finished auction at any edge in the data. Open: STR BVpY quote "below value low, short" vs engine direction rule below_val -> long only (unverified quote).

## 10-18 14:53-14:57Z multi-TF set (operator: resume observing; "observe how bias changes with each timeframe, we need a way to form the right bias") mirror@2026-10-18 14:51Z
- Shots: 2da0ed270ed8 (6h, read: SHOT_2da0ed270ed8.md, 9 MATCH 1 NOT_IN_DATA, tag LAB-VERIFY). 4h, 1h, 8h, 12h, 1D pasted mid-turn: not yet landed in the store (hook lands them at the next prompt); classify/read owed, numbers below already checked against fapi.
- All six headers reproduce from fapi 1m at ~14:56Z (H 82,268.7 / 82,100.3, L 80,987.6, C 81,037-81,047). CVD steps: 1h -1,678 (fapi -1,677), 4h -3,852 (-3,860), 8h -1,842 (-1,842), 12h -3,880 (-3,860), 1D +610 (+635). OI L 92.891K = oi_1m 92,890.8 at 13:58:56Z.
- Bias by timeframe (eye read, OURS words):
  | TF | state | location | flow | read |
  |---|---|---|---|---|
  | 1D | balance since 10-08, 79,732-84,340 | lower half (38%) | 1D delta +635 today; taker sum since 10-08 -14.4K | balance, seller-leaning flow |
  | 12h / 6h | same balance; 10-18 00:00 up-rotation (+4,495) fully given back (12:00 bar -3,860) | lower half | down | failed up-rotation |
  | 8h | compression: highs 84,340 > ~83.9K > 82,900 > 82,268.7; lows 79,732 < 80,751 < 80,987.6 | middle of a narrowing range | -1,842 this bar | coiling, no edge yet |
  | 4h | broke below the 10-17 4h balance (VA 81,068-81,644, POC 81,486) | at its VAL, near weekly VAL 80,868 | -3,860, OI up after 13:58 | short-term imbalance down |
  | 1h | two impulsive red bars 13:00, 14:00 (81,952 -> 81,044) | at engine -2s 81,064; 10-17 low 80,751 under | -1,860 then -1,677; OI -1.9K (longs out) then +0.8K (new shorts) | down, extended |
- Why the bias "changes": two causes. (a) Real: each TF answers a different question; HTF says WHERE we are (lower half of an 11-day balance), LTF says WHAT is happening now (sell impulse). They do not conflict: a 1h sell-off inside a 1D balance is a move toward the balance low. (b) Artifact: the TradingView VWAP is built from the chart's own bars, so "price vs VWAP" changes with TF alone: 1D 81,431 / 8h 81,533 / 4h 81,661 / 1h 81,674 / 12h 81,694 (fapi bar-hlc3 recompute matches each to <2 pts); engine 1m VWAP 81,676. A bias rule must use one VWAP.
- Engine: state S 4/0, classification `trend_healthy` only because price < daily VAL (mts_math.py:354-355, OURS); Tom WAIT_PROOF both sides (tom#446 short, #448 long); alert #449 NO_TRADE. HALT + HALT_DAILY_LOSS raised; auto-trader restarted 06:43:48Z with both; all fires skipped_halt.
- Method proposal (OURS, untested): fixed stack 1D -> 4h -> 1h. Highest TF = location (balance edge / middle / outside), middle TF = state of the current auction, lowest TF = timing. Lower-TF momentum toward a higher-TF edge = continuation only until that edge; at the edge it becomes a failed-auction watch (TOM-2 / TOM-7). "Middle of HTF balance" = no bias. Card: multi-tf-bias-stack-one-written-rule-tha (raw, SONNET).
- Tags: LAB-VERIFY x2 sent to DSA (engine trend_healthy vs 6h balance; ct_long zone from 10-17). Watch next: 4h/6h close vs weekly VAL 80,868 and the 10-17 low 80,751 (acceptance below = new state) or a wick back into 81.5-81.7K.
