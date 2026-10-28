# turn_of_candle: where it came from, what the research said, how that relates to what runs on testnet (D01, 2026-10-09)

Operator note on D01 ("Cap it to one slot"): "find out why we have this strategy, on what research we found it, then relate the current
issues with the original ideas and research ... about the actual ways in which this works."
Evidence below is from files read this session; every number has its file.

## 1. Where it came from
- Candidate C3 of the T055 proven-setups screen (research/fast_track_2026-09-27/T055b_PROVEN_SETUPS.md:38,51,80): "cheapest to test, klines only".
- Source 1: Shanaev, Vasenin, Stepanov, Heliyon, PMC10015199 (tier T1, peer reviewed): returns concentrate at the open of 15-minute
  candles (minutes 0, 15, 30, 45). FORMULAS.md section 16: "The paper has no cost model" and "direction of the effect is NOT stated".
- Source 2: Kim and Hansen, "The Quarter-Hour Effect", arXiv 2607.09426 (tier T2 preprint): the order imbalance in the opening window
  predicts returns over **4 to 12 hours**, on six perps with trade-level data (T055_BT_c3.md).

## 2. What the project tested
- C3 part 1 (calendar entry, fixed side, 2-minute lead, 2-bar hold, BTCUSDT 2.49 M 1m bars, fee 10 bp + slip 2 bp RT): OOS gross -0.0000 %,
  net -0.1201 %, net Sharpe -1.49, 0 of 2 OOS years positive (T055_BT_c3.md Part 1). Verdict NO EDGE.
- C3 part 2 (the paper's imbalance idea, proxied by taker-buy volume, horizons 1 bar to 12 h): OOS gross about zero at every horizon, net
  -0.106 % to -0.135 % at 4 to 12 h, sign flips between horizons (Part 2). Recommendation written then: no live sampling warranted.
- Result that decided it: gross edge is zero, not "too small to beat fees".

## 3. What actually runs on testnet (the mismatch)
- Live layer `layer:turn_of_candle:` enters at minute 14 close, side fixed, ~1-minute horizon, exits on a time exit (account jishu_1, 20 USD
  size). It is the part-1 calendar entry, the version the research already killed; the 4-12 h imbalance idea of paper 2 was never traded.
- It went live 3.5 hours after C3 found no edge, under a sampling ruling (LESSONS_LEARNED.md around line 134: "8/8 trades lost about the
  round-trip"). Its own provenance audit lists side and lead as NO-SOURCE (LAYER_PROVENANCE_AUDIT.md T03, T04).
- Bigtrade backtest C (research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:125-140, n 105,199 / 17,376): mean net -11.1 to -11.9 bp under all six
  exit policies against a 12 bp assumed cost, i.e. gross about +0.1 to +0.9 bp: **the signal pays its fees and nothing else**; managed exits do not
  change it. Live: 300 of 372 testnet trades, net -3.69 USD, every one a time-out (Control Room D01).

## 4. Relating the issues to the original idea
| Issue now | What the research says | Reading |
|---|---|---|
| 81 % of testnet trades | the effect is a timing concentration of returns, with unknown sign, and the paper has no costs | the live count is a by-product of firing every 15 minutes, not evidence of anything |
| 100 % time-exits, 97 % overall (T085) | a 1-minute hold has no room for a stop or target to work | the exit mechanism is not the defect; the horizon is |
| "crowds out the other layers" (D01 text) | each layer has its own account (auto_trader_config.json accounts: ToC = jishu_1, one position per account) | **ToC does not take slots from other layers**; it crowds only the statistics (share of rows), and costs about 0.37 USD a day in fees |
| capture matrix cannot score it (F-BT-02) | needs 1m ground truth | built (legs_1m / labels_1m on F:\MTS\data\bigtrade, D02) |
| real edge (if any) | paper 2 says 4-12 h order imbalance, trade-level data | not testable on 1m klines; needs aggTrades on disk (T055_BT_c3.md "Limits") |

## 5. Result of the decision
- "Cap it to one slot": already true (one account, one position at a time). No code change is needed or made; no new constant is invented.
- What would change the statistics share without inventing a number: park it with `trade_blocklist_parked` (alerts kept) or keep it as the
  volume generator. That is a different choice from D01's options, so it is asked as a new decision (D08) rather than assumed.
- The only way to test the original idea is the paper-2 variant on real trade data (aggTrades), filed as part of T080 follow-up scope.
