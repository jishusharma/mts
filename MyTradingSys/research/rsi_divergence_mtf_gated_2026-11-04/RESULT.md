130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)
Verdict: INCONCLUSIVE (underpowered), not FAIL and not PASS. Under Malkan's gate as written (monthly AND weekly RSI >= 60 bull / <= 40 bear, daily SMA200 side) the DEV window is bull in only 25 of 130 weeks and never bear, so 0 bearish setups exist and the 1 / 18 / 43 / 164 aligned bullish setups (1d / 4h / 1h / 15m) cannot detect any plausible effect (prereg_gate BLOCK on all four TFs, BLOCKED.md). 0 of 32 confirmatory cells survived the DEV rule; VALIDATION was not read; HOLDOUT never read.

# rsi_divergence_mtf_gated_2026-11-04 result (DEV 2022-01-01..2024-06-30, fee-net 0.14 %, exit 10 bars, PRE_REG.md frozen first)

- Gate effect, 15m W12 bullish signal entry (n 973 ungated, day-clustered 95 % CI on net): ungated net -0.161 % [-0.229, -0.092]; aligned (bull regime) n 164 / 96 days, gross -0.036 %, net -0.176 % [-0.307, -0.045], excess over bull-regime drift -0.064 % (t -1.0). The gate removed 83 % of events and did not make the signal positive; the CI excludes zero on the negative side.
- 1h aligned: n 43 / 32 days, net +0.111 % [-0.394, +0.615], t 0.43. 4h aligned: n 18, net -0.736 % [-2.58, +1.11]. 1d aligned: n 1 (+15.3 % single trade, nothing to test). Every positive-looking cell has a CI spanning zero by 0.5 to 2.6 points.
- Retest entry (N=10, level = swing B close): fills 126 of 164 (15m), 34 of 43 (1h), 15 of 18 (4h); net -0.130 % [-0.293, +0.034] (15m), +0.123 % [-0.547, +0.793] (1h). No confirmatory cell has a Holm-adjusted p below 0.265 (15m aligned signal).
- Window arms: W12 and W18 give identical event sets on 15m/1h/4h/1d (no swing pair 13-18 bars apart passes the aligned gate); the original windows 3-10 and 5-14 differ by at most 2 events per cell and the same sign. The window choice moves nothing here.
- Bearish side: aligned cells are empty (bear regime 0 weeks). Counter-regime and range bearish setups are shown in dev_cells.csv: 15m net -0.176 % (counter, n 208) and -0.179 % (range, n 810), all negative at t -3 to -5.3; the 1h/4h/1d ones span zero.
- Survivor rule (n >= 30, >= 20 days, net > 0, Holm p < 0.05, excess t >= 2): 0 survivors (dev_survivors.json is []), so VALIDATION stayed unread.

What it says about Malkan's rule as written: the full gate is too rare on BTC 2022-2024 for this signal to be tested (19 % of weeks bull, 0 % bear, monthly RSI low 41.4 in 2022 from a 2020-seeded series, so the bear gate may sit a few points above a longer-history RSI). Where it applies (15m bull) the gated divergence is net negative after 0.14 % cost, as the raw one was. Next powered step would need more symbols or a longer history (monthly RSI from 2017), not another BTC DEV read.
Not a PASS: no VERDICTS row can be PASS without a causal replay test and an independent trade-loop re-run, and no cell cleared the DEV rule.

Files: PRE_REG.md, BLOCKED.md, counts.csv (pre-return counts), dev_cells.csv (256 cells: gate x TF x arm x kind x entry), dev_survivors.json, regime_mix_dev.txt, study.py, test_gate_wiring.py (4 tests; gate test failed on the pre-change stub: `assert [10, 11, 12, 13, 14] == [10, 14]`, 2 failed 2 passed, then 4 passed).
Data: BTCUSDT 1m from F:/MTS/Dumps/backtest (raw_1m_2019, raw_1m_2022, raw), loaded only to 2024-07-01.

Regime mix: 130 weeks DEV: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)
