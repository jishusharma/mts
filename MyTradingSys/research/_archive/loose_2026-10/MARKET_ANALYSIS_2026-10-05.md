# MARKET ANALYSIS 2026-10-05 (Mon, new-week open): BTCUSDT read + MTS gap list

Session MTS-2026-10-05-0520Z-CLI-ANA-weekopen (Opus, CLI, read-only). No live-path file touched.
Data cutoff: 2026-10-05T05:17:10Z. Every number below is a disk read this session.
Note: the operator prompt said "November"; system date is 2026-10-05 (October). US is on EDT until 2026-11-01,
so today's US cash open is 13:30Z (19:00 IST), 492 min after cutoff (`session_timing.us_equity_open_in_minutes`).

Sources: SNAP = `runtime_data/snapshots/BTCUSDT_2026-10-05_1791177431502.json`; LOG = `runtime_data/apparatus_log.txt`
(3098 parsed rows 10-02..10-05, hourly OHLC from ~1/min samples, not true 1m OHLC); CMS = `runtime/current_market_state.md`;
SC = `runtime/state_code*.json`; LAS = `runtime/live_alert_state.json`; LEDGER = `execution/trade_ledger.jsonl`.

## 1. What happened (tape)

| Window (UTC) | Path | Source |
|---|---|---|
| Fri 10-02 13-19Z | 87050.7 high -> 83860.2 low (NY session sell-off, below weekly VAL) | LOG hourly |
| Sat 10-03 | Flat base 84409.5-84980.8 | LOG hourly |
| Sat 21Z -> Sun 09Z | **Tape hole 11 h** (apparatus not writing); 84667.4 -> 85083.6 | LOG |
| Sun 10-04 20Z -> Mon 01Z | Weekend climb 85354.5 -> **86956.5** (Mon 01Z high) | LOG hourly |
| Mon 00:00Z week open | 86482.8 (= prior_day.close) | SNAP prior_day |
| Mon 03-05Z | Drop 86492.6 -> 85451.2; last 85469.4 (-1.17% vs week open) | LOG |

Reading: the weekend rally tagged the weekly VAH zone (86865.93) / post-funding VAH 86810 and failed; price fell
back through weekly VAL 85814.27 and now sits on daily VAL 85452.34 / 4H VAL 85477.58.

## 2. MTS readings at cutoff

- Profiles: weekly POC 86510.37 / VAH 86865.93 / VAL 85814.27 (TWOPEAK); daily POC 85542.56 / VAH 86550.05 / VAL 85452.34;
  prior-week POC 83896.42. Price: below weekly VA, inside daily VA at its low edge.
- VWAP (00Z anchor) 86229.75, flat; -1s 85801.78, -2s 85373.81. Price is between -1s and -2s.
- Flow: session CVD -2490; CVD 4h delta -2399.7 (falling), 1h -268 (falling); trade-flow 15m +143, 1h -364.
  Short-term buyers are bouncing it; the 4h is seller-driven.
- Book bid/ask 0.7 (ask-heavy). Funding 7.18e-05 (not extreme). OI flat, delta_state neutral. Basis -0.04% (perp discount).
  Flat OI on a ~1.2k drop = not a liquidation flush and not fresh shorts piling in.
- Structure: 1h swing 85277.9 / 86619.0; 4h swing 85354.5 / 86976.1; 1w swing 82500.1 / 87249.6.
- Regime (SC): RANGE, HIGH confidence, 197 cycles since 01:51Z. Quad state A>L (3 bull / 1 bear of 5).
- Tom engine: WAIT_TRIGGER. Rank-1 ct_long @ weekly_val 85814.27 (stop 85277.9, tgt 86700.42, net_rr 1.29);
  rank-2 ct_long @ 1h_swing_low 85277.9 (stop 85107.34, tgt 86510.37, runner 86910.94, net_rr 4.48). Proof: none
  (no rejection wick, absorption, finished auction, delta flip; volume magnitude 0.69; speed quiet).
- Layers (LAS): cryptocred 15m sr_flip_short @86274 fired pre-drop (won +0.1056); fabio 15m bullish_absorption @86512
  (lost -0.11); session_momentum short 15m (lost -0.0342); rsi 15m cross down through 40; ToC sampling 1m.

## 3. Trades 2026-10-04 20:00Z -> cutoff (LEDGER)

| Family | Trades | Wins | Net USD |
|---|---:|---:|---:|
| turn_of_candle (jishu_1) | 35 | 9 | -0.249 |
| cryptocred sr_flip short | 1 | 1 | +0.1056 |
| fabio cvd_absorption long | 1 | 0 | -0.1100 |
| session_momentum short | 1 | 0 | -0.0342 |
| tom #160 short | 1 | 0 | -0.0505 |

During the rally Tom logged WAIT_RR every hour (net_rr -0.09 .. 1.14 < 1.25): the engine saw the move but never traded it.

## 4. Into US open (13:30Z): scenarios (analyst judgement, NOT a validated MTS forecast)

MTS has no tested US-open model (T054 section E: H3 protocol not yet run). The levels are MTS levels; the weighting is mine.

| Scenario | Trigger (acceptance = 1h closes) | Path / targets | Lean |
|---|---|---|---|
| A. Balance rotation (base) | Holds 85277.9 1h low; stays under 85814 | 85300-85900 chop; VWAP -1s 85802 caps | ~50% |
| B. Continuation down | Acceptance < 85277.9, then < 85107 | 85000, prior-day low 84677.3, Sat base 84410-84650 | ~30% |
| C. Reclaim (TOM-011 "came back in, formed acceptance") | Acceptance back > 85814.27 with delta flip | VWAP 86230, weekly POC 86510, HVN 86700 | ~20% |

**Expected price at 13:30Z: 85300-85900, centre ~85550** (daily POC 85542.56). Lean mildly bearish while below
weekly VAL and VWAP with 4h CVD falling; RANGE regime + flat OI argue against a trend day before NY.
US open is the event: Tom's own pattern (TOM-011) is "opened lower, crashed down, came back in" - so a 13:30-14:00Z flush
below 85278 that is reclaimed is the Tom long (rank-2 setup, net_rr 4.48); acceptance below it flips to B.
Invalidations: above 86230 A/B are dead; below 84677 C is dead.

## 5. What is missing for MTS to produce real trades (found this session)

| # | Gap | Evidence | Impact |
|---|---|---|---|
| G1 | Tom net_rr floor blocks almost everything | 10-04/05 every rally hour WAIT_RR; 24h: 28 alerts, 2 entered, 22 rejected (TESTNET_STATUS_2026-10-05) | Core never trades the move it sees. Check floor 1.25 provenance (Tom quote or NO-SOURCE) and target choice (nearest HVN vs POC) |
| G2 | Tape holes over weekend | LOG gap 10-03 21Z -> 10-04 09Z (11 h); 10-01 19:44Z -> 10-02 13:01Z | Blind during gap moves; needs a feed watchdog + alert |
| G3 | HTF context writer stopped | `research/htf_context/` last file 2026-10-02 | No 4H/1D balance / failed-breakout context |
| G4 | 1D structure stale | SNAP structure.1d stale=True (84829.6/84482.8, Oct 1-2) | Daily swing levels wrong |
| G5 | Liquidation clusters + OI breakdown empty | SNAP liquidation_clusters 0.0; oi_breakdown "unavailable" | No liquidity map for US-open sweeps |
| G6 | US-open anchor hard-coded 13:30Z | SNAP session.vwap_anchor_utc; T054 C2/C3 | **Wrong by 1 h from 2026-11-01 (EST = 14:30Z)** |
| G7 | No week-open / month-open / Monday-range levels | not in SNAP | Needs trader source first (provenance rule) |
| G8 | No news/macro calendar | T054 section D unverified | System cannot know a US-open day is "crucial" |
| G9 | turn_of_candle bleeds fees | 35 trades, 9 W, -0.249 since 20Z | Sampling layer; negative expectancy so far |
| G10 | ct_long proposed at a level price is below | rank-1 substate "below" @ weekly_val | Is a reclaim-long Tom-sourced? Verify |
| G11 | No validated forward edge | testnet 24h net negative all families but cryptocred | Need per-setup backtest + live expectancy before real money |

## 6. Roadmap (cheapest tier first)

- P0 (T0 script / T1): feed watchdog for apparatus + HTF writer (G2, G3); fix 1D structure refresh (G4); DST-aware US anchor
  before 2026-11-01 with restart/reset test (G6, live path: stage .new, supervisor restarts).
- P1 (T2 Sonnet, spec+tests): G1 audit - source of the 1.25 floor and target selection, replay 10-04/05 with sourced values;
  G10 provenance check; G5 liquidation/OI-ratio feed (data only).
- P2: G7/G8 only after a trader quote exists; run T054 H3 US-open study on 30 days of orderflow_live; G9 keep/kill decision
  from 7-day ToC expectancy; G11 per-setup expectancy table feeding a go/no-go for real trades.

## 7. US-open update (data cutoff 13:42Z)

Sources: SNAP `runtime_data/snapshots/BTCUSDT_2026-10-05_1791207792987.json`; LOG hourly 05-13Z; LEDGER rows ts >= 05:17Z.

Forecast check (honest): called 85,300-85,900 at 13:30Z, centre 85,550. Actual 13:30Z = 86,068.7 -> MISS by ~170 above range.
Scenario C (hourly close > 85,814) fired at 06Z close 86,182.7; path reached VWAP 86,248 but not 86,510 (high 86,463.6 @08Z).
Then 09-13Z rotated 85,773-86,194 around the new daily POC.

US open tape: 13:30 86,068.7 -> 13:31 **85,786.7** (sweep under weekly VAL 85,824.6 / prior-day VAL 85,798.75 /
4H VAL 85,821.5) -> back inside by 13:32, 85,935.5 at 13:42. Engine 13:41 WATCH ct_long proof 4; 13:42 WAIT_TRIGGER
ct_long @ prior_day_val nrr 2.68.

Readings now: weekly VP POC 86,094.95 / VAH 86,645.67 / VAL 85,824.6 (weekly POC was 86,510 at 05Z -> value migrating DOWN,
Tom money-flow lean bearish). Daily POC 86,039.88 / VAH 86,430.39 / VAL 85,664.39. VWAP 86,106 falling; -1s 85,756, -2s 85,406.
Flow: CVD 1h +313 / 4h +19 (rising), trade-flow 15m -161, 1h +287. Book 0.54 (ask-heavy). Funding 1.76e-05, OI flat, basis -0.05%.
Regime RANGE.

| Rest of US session (to ~20Z) | Odds | Condition | Path |
|---|---|---|---|
| A. Rotate in daily value | 50% | holds 85,800 cluster, stays < 86,170 | 85,800-86,430 around POC 86,040 |
| B. Break down | 30% | 1h close < 85,800 | 85,664 -> 85,406 (VWAP -2s) / 85,369 (4h swing low) |
| C. Up | 20% | 1h close > 86,170 (VWAP + 1h swing high) | 86,430-86,470 -> 86,646 (weekly VAH) |

Tom read: the 13:31 dip under the 85,800 cluster that was bought back inside within one minute is the "failed break back into value"
shape. Long valid only while 85,787 holds; target daily POC 86,040 then VAH 86,430. Lean: neutral-to-bearish (value migrating down,
VWAP falling, book ask-heavy) - long is a rotation trade, not a trend call.

Trades 05:17-13:42Z: turn_of_candle 34 (6 wins, -$0.33); rsi 5 (2 wins, -$0.06); cryptocred 1 (-$0.01). Tom/Fabio/session: none.

New/confirmed gaps:
- G12 (new): at the sweep minute 13:31 the engine logged NO_TRADE (no candidates); the zone touch lasted < 1 cycle (1/min sampling),
  so a Tom-shape reclaim at the exact level was invisible to it. Needs tick/1m-OHLC low, not sampled last price, for zone touch.
- G4 still open: structure.1d swing 84,829.6 / 84,482.8 (stale, 10-01/02). G5 still open: liquidation clusters + OI breakdown = 0.
- G1 confirmed again: 13:19-13:40 every candidate WAIT_RR at nrr 0.2-0.8 vs 1.25 floor.

## 8. Live watch 13:50-13:56Z (1/min polls)
13:48 squeeze 86,002 -> 86,322; 1h flow +863 -> +1,184 BTC by 13:55; price capped 86,345 (13:52), 86,304 at 13:55 = effort without result
under daily VAH 86,430. Daily POC migrated up 86,040 -> 86,255; 4H VA 85,947-86,360. Book flipped 0.35 -> 2.61 -> 0.72 -> 2.23 (unstable).
Engine: WATCH ct_short @ daily_vah 86,430 (proof 4, nrr 1.71); 4h_vah short proof 5 blocked nrr 0.69 + flow contradiction.
Missed: 13:31 reclaim long 85,787 -> 86,345 (+558, ~3x a 190-pt stop) never entered - G12 + G1 in one live example.

## 9. Higher-timeframe context (operator ask 14:0xZ) - daily/weekly/cycle
Source: Binance fapi public klines 1d x400 + 1w x12 (read-only, fetched this session). Local `Dumps/backtest/raw_1d` ends 09-26 (stale).
- Cycle: ATH 126,208.5 (2025-10-06) -> low 57,758.6 (2026-07-01, -54%, 9 months) -> rally to 87,385.1 (2026-09-21) = +29.6k (+51%).
  Price at fetch 86,632 = 31% below ATH, between 0.382 (83,850) and 0.5 (91,983) retrace of the 126.2k->57.8k drop.
- Resistance tested 4x: 87,385 (09-21, 24.5B vol impulse) / 87,247 (09-23) / 87,250 (10-02, rejected to 84,483 close, 19.9B) / 86,976 (today).
  Highs slightly lower; daily lows rising 82,500 (09-28) -> 83,842 -> 84,677 -> 85,369 = compression under 87.0-87.4k.
- Weekly closes 81,144 -> 84,433 -> 86,483 (highest of the rally). Weekly POC 83,896 (prior) -> 86,095 (this week): value moving up.
- Two-week balance 82,500-87,385; we are at its top edge.

Approach to 87.0-87.4k (judgement on MTS levels; MTS has NO HTF model, so these are not MTS outputs):
| Case | Odds (this week) | Tell | Path |
|---|---|---|---|
| 1. First-pass rejection | 40% | wick into 87.0-87.4k, flow up but price stalls (absorption, as seen 13:52-13:55Z at 86.3k), 1h close back < 86,646 | 86,095 -> 85,825 -> 84.5k |
| 2. Sweep + fail (bull trap) | 25% | pokes 87.4-88k (stops over the triple top), 4h/daily close back < 87,250 | 86,095 -> 83,900 (prior wk POC) -> 82,500 |
| 3. Break + retest + hold | 35% | daily close > 87,385, pullback holds 87.0-87.4k, value (POC) builds above | no level above in MTS; HTF 0.5 retrace ~92k |
Bull-trap case: prior cycle bottoms came ~12-13 months after the peak (2018-12, 2022-11); this low came at 9 months, and a 0.382-0.5 retrace
is where 2022's relief rally failed. Bull case: rising lows + rising weekly value + 4th test of one level. Small sample (3 cycles), lore not MTS.
Trade rule of thumb (Tom shape): never buy the first poke above 87.4k; buy the RETEST that holds, or sell the failed break back inside.

Gaps (new):
- G13: MTS has no daily/weekly candle context - no test count at an HTF level, no rising-lows/compression read, no cycle position/ATH distance.
  Only structure.1w swing 87,249.6/82,500.1 exists (and 1w swing high misses 87,385 wick). Needs Tom/Fabio quotes on HTF context first.
- G14: no "break -> retest -> hold" (acceptance above an old high) or "sweep -> fail" setup on daily levels; ties to M4.
- G15: daily kline dump stale since 09-26; refresh job missing.
