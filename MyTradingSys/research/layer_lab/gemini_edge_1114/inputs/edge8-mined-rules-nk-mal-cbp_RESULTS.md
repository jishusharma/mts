Regime mix: VALIDATION 150 weeks: bull 84 (56%) | bear 46 (31%) | range 20 (13%) | n/a 0 (0%) | DEV 197 weeks: bull 89 (45%) | bear 66 (34%) | range 14 (7%) | n/a 28 (14%) (BTC weekly close vs 200d SMA +-5 %)

Verdict: FAIL / no edge. 0 of 9 cells PASS; CBP-R05 NOT_TESTABLE.

| rule | cell | TF | trades DEV/VAL | win rate VAL | mean R VAL | CI day-cluster | CI per-trade | placebo (mean R, p) | mean R w/o best 5 days | BH | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MAL-R05 | MAL-R05_short_W12 | D | 4 / 9 | 0.444 | +0.394 | [-0.732, +1.916] | [-0.716, +1.878] | +0.142, 0.275 | -1.042 | no | UNDERPOWERED |
| MAL-R05 | MAL-R05_long_W12 | D | 20 / 7 | 0.143 | -0.602 | [-1.071, +0.292] | [-1.067, +0.289] | -0.468, 0.340 | n/a | no | UNDERPOWERED |
| MAL-R05 | MAL-R05_short_W18 | D | 4 / 9 | 0.444 | +0.394 | [-0.732, +1.916] | [-0.716, +1.878] | +0.120, 0.205 | -1.042 | no | UNDERPOWERED |
| MAL-R05 | MAL-R05_long_W18 | D | 20 / 7 | 0.143 | -0.602 | [-1.071, +0.292] | [-1.067, +0.289] | -0.482, 0.300 | n/a | no | UNDERPOWERED |
| NK-R04 | NK-R04_WIN | 15m | 936 / 951 | 0.180 | -3.685 | [-7.218, -1.348] | [-7.333, -1.468] | -3.514, 0.775 | -4.090 | no | FAIL |
| NK-R04 | NK-R04_ALL | 15m | 21579 / 25177 | 0.184 | -2.043 | [-2.347, -1.765] | [-2.332, -1.777] | -2.065, 0.260 | -2.097 | no | FAIL |
| NK-R05 | NK-R05_WIN | 15m | 845 / 1043 | 0.178 | -2.247 | [-3.229, -1.597] | [-3.124, -1.607] | -2.191, 0.590 | -2.438 | no | FAIL |
| NK-R05 | NK-R05_ALL | 15m | 20156 / 23430 | 0.159 | -3.181 | [-3.626, -2.772] | [-3.616, -2.774] | -3.030, 0.985 | -3.236 | no | FAIL |
| NK-R11 | NK-R11_BB | 15m | 45230 / 49922 | 0.255 | -0.236 | [-0.257, -0.215] | [-0.245, -0.227] | -0.216, 1.000 | -0.245 | no | FAIL |
| CBP-R05 | - | 1h/D | - | - | - | - | - | - | - | - | NOT_TESTABLE |

Descriptive (VALIDATION): MAL-R05_short_W12 hold 3.1 bars (placebo 2.7), median stop 2.85%, median R -1.014, mean net -0.642% per trade; MAL-R05_long_W12 hold 6.3 bars (placebo 5.9), median stop 3.95%, median R -1.030, mean net -1.276% per trade; MAL-R05_short_W18 hold 3.1 bars (placebo 2.7), median stop 2.85%, median R -1.014, mean net -0.642% per trade; MAL-R05_long_W18 hold 6.3 bars (placebo 5.9), median stop 3.95%, median R -1.030, mean net -1.276% per trade; NK-R04_WIN hold 2.0 bars (placebo 2.0), median stop 0.15%, median R -1.523, mean net -0.139% per trade; NK-R04_ALL hold 1.9 bars (placebo 2.0), median stop 0.17%, median R -1.506, mean net -0.109% per trade; NK-R05_WIN hold 2.0 bars (placebo 2.0), median stop 0.15%, median R -1.555, mean net -0.116% per trade; NK-R05_ALL hold 1.8 bars (placebo 1.9), median stop 0.13%, median R -1.729, mean net -0.118% per trade; NK-R11_BB hold 3.0 bars (placebo 2.9), median stop 0.70%, median R -0.421, mean net -0.114% per trade

Costs: 2 x BINANCE_TAKER + SLIPPAGE_RT_S13 = 12 bp round trip. Data end 2026-11-13 19:45 UTC. Coverage (15m start dates): BTC 2020-03-25, ETH 2021-03-15, SOL 2021-10-15, XRP 2021-05-13, DOGE 2021-06-02, BNB 2021-06-29, ADA 2021-03-18, LINK 2020-10-21, LTC 2020-10-21, AVAX 2021-09-15, DOT 2021-03-18, TRX 2021-08-31, ATOM 2021-10-11, NEAR 2021-10-11, UNI 2021-11-30, ETC 2021-06-29, BCH 2020-12-14, FIL 2021-06-29, AAVE 2021-05-13, XLM 2021-08-31.

## Caveats in plain words
- **Verdict: none of the tested rules shows an edge; 0 of 9 cells pass.** The four NK 15m cells and the Bollinger breakout lose money net of costs, and each does no better than random entries with the same stop and exit (placebo p 0.26 to 1.00); the lead-worthy "beats placebo" test is failed everywhere.
- **MAL-R05 is UNDERPOWERED, not refuted.** The weekly-divergence-then-third-daily-candle filter leaves only 7 to 9 VALIDATION trades (20 coins, 2024 on). The W12 and W18 rows are identical because no extra 13-18 week pairs produced a trade. Short: mean +0.39 R, CI spans zero widely; long: -0.60 R. Nothing can be said beyond "too rare to test on this universe"; a longer or wider (stocks, indices) history would be needed.
- **NK-R04 / NK-R05 are PARTIAL tests and transplanted.** Only one of NK's "three conditions" is in the extract (15m RSI 14 at 30/70); the other two and the 10m/5m confirmation are NOT_STATED and untested. The rule predicts an overnight gap at the NSE close; crypto has neither, so the WIN variant tests the time-of-day label only. The stated stop (low or high of the signal bar) is very tight on 15m (median 0.13-0.17 % of price), so the 12 bp cost alone is about 0.8 R and the trade usually ends within 2 bars on the previous-candle trail; mean net per trade is -0.11 to -0.14 %, i.e. gross about zero. A failure here is a failure of the transplant and of this stop reading (OURS), not of NK's full method.
- **NK-R11 (Bollinger breakout, long)** uses OURS values for band width (2.0), the 4-bar arming window and the 15m timeframe; median stop 0.70 %, hold 3 bars, mean -0.24 R (-0.11 % net). The breakout candle high then previous-candle-low trail gives up the move too early on 15m; a coarser timeframe ("scaled by timeframe") was not tested (would be a new pre-registration).
- **CBP-R05 NOT_TESTABLE:** one dated BTC episode with absolute price levels (N = 1), no generic definition; inventing a sweep rule was ruled out by the card. Needs the operator or a Habib-style written rule before a test.
- VALIDATION window 2024-01 to 2026-11 is 56 % bull, 31 % bear, 13 % range weeks on BTC; DEV is 45/34/7 (14 % no data); no regime gate was applied.
- Limits: Bybit perps, no funding, 20 correlated coins (day-cluster CIs account for part), 15m coverage starts 2020-03 (BTC) to 2021-11 (UNI), NK cells share events so tests are not independent. R is cost-sensitive when the stop is tiny, so mean R is dominated by costs; the mean net % column in the descriptive line is the cleaner read.
- Tests: `test_rules.py` (9 tests) include a one-bar look-ahead variant and an entry-at-signal-close variant that the suite catches (each failed once during development, before the fix to the test data).
