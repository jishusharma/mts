# WHY THE ENGINE IS SILENT WHEN THE CHART IS CLEAR - 2026-10-03

Session: Opus CLI (chart read + roadmap). Operator question, verbatim: "Why whenu canso clearly apply the rules that
you have to the charts directly and see what is going on -> Then why our compiled code is not doing anything?"

## 1. What the chart read found (1D + 4H BTCUSDT, Binance, CoinGlass OI / CVD / net delta, to 2026-10-02 ~22:20Z)
- Aug 18-21: 64k -> 80k on CVD 0 -> 70k (real taker buying).
- Aug 21 - Sep 15: balance 77-82.5k; CVD fell ~45k while price held = sellers' effort without result (Fabio S3
  absorption). Resolved up Sep 18-20 to ~87.5k (failed auction of sellers, Fabio model D shape).
- Sep 22-23: OI 112k -> 93k (-15%) with price -3% = long deleveraging, absorbed.
- Sep 24 - Oct 1: balance 82.5k-85.6k; weekly VAL/POC/VAH 82910/83851/85098 (MARKET_ANALYSIS_2026-10-02 section 0).
- Oct 2: overnight breakout with OI 93k -> 100k (new longs), NY high 87123 = Sep 21 high, failed; OI 100k -> 95.3k,
  CVD 14k -> 10.7k, price 84585, back inside last week's balance. Failed breakout -> Fabio model B short;
  far edge = 83851 POC, then 82910/82500. Invalidation: acceptance above 85.1-85.6k.
- Divergence: price higher highs (80k, 87.5k), CVD lower highs (70k, 45k, 17k); 1D net delta at lows (-49.5k).
- The engine's proof-5 ct_short at daily VAH 87064.46 (13:40Z) was right; only the 2.0 floor blocked it.

## 2. Why the code did nothing (ranked by trades lost)
| # | Cause | Evidence | Effect |
|---|---|---|---|
| 1 | Target window [2.0, 3.5]R (NO-SOURCE A08-A10): a candidate with no node inside the window is DELETED | SetupCandidatesBuilder.java:158-183 (`if (c.target == 0) continue`) | Trend legs (node > 3.5R away) produce "NO_TRADE (no candidates)": 40 straight cycles 14:48-15:27Z on 10-02 while price fell 1.8k |
| 2 | Net_rr floor 2.0 (NO-SOURCE, D1(a)) | LOG:18795 "1.62 < 2.0" | Blocked the one proof-5 setup of 10-02 (target hit) and the 10-01 16:46Z long (target hit) |
| 3 | Gross R >= 1.5 hard drop (NO-SOURCE) | SetupCandidatesBuilder.java:191 | More candidates deleted before the verdict sees them |
| 4 | Execution cannot hold a big move: one fixed target at the NEAREST node; breakeven/trail refused pre-flight (R4) | position_manager.py:27 | Even a filled 13:40Z short would have banked 377 of the 1814 points |
| 5 | No higher-timeframe context: the verdict chain never sees multi-day balance, failed breakout, OI | gate chain STD:204-215, VPY:110-137 (no OI, no HTF balance) | What I read on 1D/4H (balance -> failed auction -> flush) does not exist in code |
| 6 | No "reclaim -> trend to far edge" model live: after 13:49Z every candidate was a long fade at swing lows | MARKET_ANALYSIS 4.5 | Engine only fades levels; Fabio model B (the right model on 10-02) runs nowhere |
| 7 | Fabio has no live input: v3 needs 1m order-flow bars, live runner feeds klines; OF files stop 2026-09-28; all 8 params SHADOW | FABIO_V3_SOURCING; Sonnet d023cc8 report | Promoting v3 emits nothing |
| 8 | Reliability: stack down 09-29 -> 10-02, alerts #71-#83 lost, nobody paged | DIRECTION_REVIEW section 2 | 0 Tom testnet trades |

Short answer: the rules exist; the code puts NO-SOURCE gates between the rule and the order (1-3), has no way to hold
the move (4), and has no eyes above the intraday snapshot (5-7).

## 3. Defaults applied now (FLAGGED - operator may override any)
- **D1 [FLAG]** Rip out the [2.0, 3.5]R window and the gross 1.5R drop. Target = nearest sourced node (POC/HVN, TOM-018/102)
  that clears the net_rr floor, else the farthest node in direction. New field `runner_target` = the next node beyond.
- **D2 [FLAG]** NO-SOURCE target members (VAH/VAL, prior-day H/L, VWAP) removed as targets; sourced nodes only.
- **D3 [FLAG]** net_rr floor stays 1.25 in net_rr_floor.json (Ruling 1: testnet value may be anything). No other copy of 2.0 left.
- **D4 [FLAG]** Promote the staged execution/ and layers/alerts/ `.new` files (net_rr single source, v3 shadow emitter).
- **D5 [FLAG]** Restart Java apparatus + auto_trader after the full gate passes and the commit lands.

## 4. Roadmap (in order; each item = one Sonnet build, gated, then restart)
| # | Item | Default chosen [FLAG] | Done = |
|---|---|---|---|
| R1 | D1-D5 above | as listed | trades with target > 3.5R in auto_trades.jsonl |
| R2 | Runner management (big-move capture): 50% at `target`, 50% runner to `runner_target`, stop to breakeven when leg 1 fills; lift R4 for this path only | 50/50 split NO-SOURCE testnet default; BE concept from Fabio P21 "I put my stop loss to break even" | live-path tests: restart/reset state, partial fill, API error, fail closed |
| R3 | Live order-flow bar writer (aggTrades -> 1m OF bars with b99/fp/thr_days); live runner `--limit` >= 300 | Binance aggTrades websocket | v3 shadow rows appear in runtime/alerts with `collection_only` |
| R4 | HTF context layer (separate layer, never a Tom filter): 4H/1D balance (Fabio S1), failed-breakout flag, OI delta from Binance openInterestHist | collection-only log for 14 days, then measure | daily row per state; report vs next-day range |
| R5 | Model B (failed-breakout reclaim) as a shadow alert on 15m/4H using R3 + R4 | shadow until n >= 30 | shadow ledger with outcome R |
| R6 | Canary every 30 min as a Windows scheduled task (testnet_canary.py exists) | needs operator yes (persistent config) | RED reaches inbox |
| R7 | Tom BT re-run on regenerated cache with D1 target rule: measure right-tail capture vs old window | - | table: R distribution old vs new |

## 5. Market now (2026-10-02 ~22:20Z)
Range 82.5-87.5k with a bearish tilt short term: failed auction at 87.1-87.2k (second rejection of that high), overnight
longs flushed (OI -5%), price back inside last week's value. Targets 83851 then 82910/82500; invalidation acceptance
above 85.1-85.6k. Higher-timeframe structure still higher lows (64k, 77k, 82.5k); a break of 82.5k with OI rising and
net delta falling = new sellers, next balance 77-82.5k. Chart read is visual; not engine output.
