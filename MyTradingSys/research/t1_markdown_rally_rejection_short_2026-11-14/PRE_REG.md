# PRE_REG t1_markdown_rally_rejection_short (2026-11-14; committed before any trade outcome is computed)

Origin: `EDGE_POSTMORTEM_1114.md` section 4, test T1. Labels: S = SOURCED (named document / NK quote), O = OURS. No OURS parameter is the trader's. One frozen cell, no grid, nothing tuned on DEV.

## Context
- Phase: MARKDOWN only. Day label from `F:\MTS\data_cache\mts_brains\phase_daily.csv` (MTS_BRAINS_SPEC s1: c < SMA50, SMA50 slope <= -1%, and cycle BEAR or c < SMA200; closes through d-1 only, lag 1; thresholds O, spec S). Cycle state BEAR/BULL/BASE reported per row. BTC reads MARKDOWN since 2026-11-13, so the idea is live now.
- Idea: in a market-wide MARKDOWN day, a 1h push above the daily pivot P (or R1) that closes back below it, with NK Hilega-Milega in sell state on 30m and price under VWAP, falls to the next pivot below. Short only.
- Prior art on this exact trigger: nk2 1h SHORT-P gross +0.101 R, n 6102, net -0.009 R at 12 bp (stop floor 0.5%, no cycle-phase gate). T1 changes only: MARKDOWN gate, HM + VWAP filters, stop floor 1.2%, exit rule.
- Session: none (any UTC hour).

Regime mix: DEV (2019-01-01..2023-12-31) and VAL (2024-01-01+) MARKDOWN days counted from the phase table by the study before any outcome is computed (prior knowledge from nkp2: MARKDOWN 23.8% of DEV days, about 19% of VAL days; about 343 DEV + 199 VAL days per the post-mortem). RESULT carries days per phase DEV/VAL and signals per phase.

## Rule (frozen)
| Item | Value | Label |
|---|---|---|
| Levels | classic floor pivots from the prior complete UTC day: P=(H+L+C)/3, R1=2P-L, S1=2P-H | S (NK2 PRE_REG, NK pivot class); UTC day O |
| Trigger | 1h bar with high > level and close < level, level in {P, R1}; one signal per coin per bar (the higher level wins if both) | S (nk2 SHORT rule as registered) |
| Phase gate | day label of the signal bar's UTC day == MARKDOWN | S spec, O thresholds |
| HM filter | NK Hilega Milega on 30m: RSI(9) of close; EMA(3) of RSI; WMA(21) of RSI; sell state = WMA21 > RSI and WMA21 > EMA3, read at the 30m bar closing at the 1h signal-bar close (FORMULAS s1, s4, s5) | S (Qdug_K_TNHg 00:23:25-00:39:49) |
| VWAP filter | signal close < VWAP anchored 00:00 UTC (cumulative typical price x volume / volume of 15m bars, through the signal close) | S rule (never trade against VWAP); anchor O |
| Entry | next 1h open, short, taker | O |
| Stop | entry + D, D = max(signal-bar high - entry, 1.0 x ATR14(1h, plain SMA of true range, FORMULAS s12), 1.2% of entry); touch triggers, gap fills at worse of stop and open | S (beyond the level); floor O |
| Target | next pivot below the level: from P -> S1, from R1 -> P; fills at the level. Skip the signal if entry - target < 0.5 x D (target under 0.5 R away) or target >= entry | S target; 0.5R skip O |
| Time exit | close of the 24th 1h bar after entry | O |
| Same-bar stop and target | stop wins | O |
| Position | one open position per coin; signals while open are ignored | O |
| Cost | primary 12 bp round trip = 6 bp of notional per side, in R = 0.0012 x entry / D (taker both legs, fees.py convention). No funding, no slippage modelled (spot-priced bars; perp shorts usually receive funding in a bear, so omission is a stated limit, not a safe side) | task |
| Maker row (sensitivity, not pass-bearing) | 6 bp; entry = limit at signal close, fills only if next bar high > signal close strictly; stop/target rebuilt from fill; unfilled dropped; fill ratio reported | O |
| Split | DEV signal bar open <= 2023-12-31, VAL >= 2024-01-01 | O |

## Data
- Primary (fresh) sample: 20 Binance spot USDT coins not in the 20-coin set of nk2/nkp: EOS NEO IOTA ZEC DASH ZIL VET BAT ICX QTUM ONT ENJ MANA SAND THETA XTZ HBAR AAVE GRT CHZ. 15m klines from data.binance.vision (public) into `F:\MTS\data_cache\binance\t1-markdown-rally-rejection\` with `.meta.json` sidecars. A coin enters only with >= 730 days of history; dropped coins are listed in RESULT. 8 of these (AAVE ENJ GRT HBAR MANA SAND THETA XTZ) appeared in nk5-nyasia (5m session rule, a different rule); disclosed, kept.
- Secondary (seen) sample: the 20 coins in `F:\MTS\data_cache\binance_spot` (BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO), 15m, read-only. Reported separately and pooled; the PASS verdict rests on the primary sample.
- Committed tests must not read F:\ caches or scripts/sched: tests use synthetic bars and hand cases; only the study run reads the cache.

## Statistics and bars (fixed now)
Per sample and per split (DEV, VAL) at 12 bp: n, distinct signal days, win %, break-even win %, gross R, cost R, net R, day-cluster 95% CI of mean net R per trade (5000 bootstrap draws over UTC days, fixed seed), ex-best-5 days net R (drop the 5 days with the largest summed net R, mean of the rest), by symbol, by year, by cycle state. Baselines: (a) same-phase random shorts (1000 draws; for each real trade a random bar of the same coin, same UTC hour, on a MARKDOWN day, same stop-distance % and target-distance %, same exit rule) giving EXCESS = real - placebo mean and p = (1+#placebo >= real)/1001; (b) short-and-hold 24 h from the same entry bars, no stop or target (buy-and-hold baseline, sign flipped); (c) control: same rule on non-MARKDOWN days; (d) filter ablation (no HM, no VWAP, neither), descriptive.

**PASS requires ALL, on the PRIMARY sample, in VAL and in DEV:** net R > 0 at 12 bp; day-cluster CI low > 0; ex-best-5 > 0; EXCESS over same-phase random shorts > 0 with placebo p < 0.05; n >= 150 and >= 40 distinct signal days (UNDERPOWERED if lower, never PASS). The pooled (primary + secondary) set is reported for information. FAIL otherwise. The 6 bp row is not pass-bearing.

- Gate: `prereg_gate.py` run with the measured DEV sd of per-trade R and the independent-day count; output copied into RESULT. If BLOCK, the run still goes (operator order) and RESULT says BLOCK; a BLOCK does not lower any bar.
- Protocol: `study.py dev` first; the DEV table and gate are written, code and DEV files committed (hash stored in `frozen.json`) before `study.py val` runs once. `study.py val` refuses if the code changed since that hash.

## Tests (committed, no F:\ reads)
Causality: pivots use only the prior complete UTC day; phase for day d from data truncated at d-1 (`PHASE_LAG=0` and `STUDY_BUG=1` must FAIL these tests); HM and VWAP at signal time unchanged when bars after the signal are removed or poked. Exit hand cases: stop, gap, tie, target, time exit. Fee formula by hand. Planted-edge unit test (post-mortem s2): on synthetic bars with zero drift gross ~0 and net ~ -fee; with a planted downward drift after random signals the harness reads gross > 0. Three dated trades recomputed independently of the study code (see RESULT).

## Weaknesses stated up front
Phase is BTC-only, so effective n is days (about 540 MARKDOWN days in total, all coins on one tape): the day-cluster CI is the honest unit and may be too wide to pass whatever the mean. nk2 gross +0.10 R must roughly triple to pay 12 bp; the 1.2% floor cuts the fee to about 0.10 R but the 0.5R skip and wider stop also change the R scale. MARKDOWN is one regime per cycle in this data (2019, 2022, 2025-26): a pass would mean surviving those, not a law. Funding and slippage are not modelled.
