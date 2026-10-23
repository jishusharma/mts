# LC3 ladder simulator: DEV result (standard DEV 2022-04-01..2024-06-30)

Run 2026-10-20 20:35Z on JIS-NB, `python MyTradingSys/research/levels_confluence_2026-10-14/ladder_run.py`, 180 s. Tests: `python -m pytest MyTradingSys/research/levels_confluence_2026-10-14/test_ladder.py` (9 hand paths, red before ladder.py existed).

## Verdict

**INCONCLUSIVE by the card rule (power_mde.py power 31% < 50 %); FAIL by the sample-sd rule (+0.10 R excluded, power 87%).** Frozen rule (max mean net R among the 240 variants with n >= 200; selection = one trial, the VALIDATION read is the answer): `E1 S2 K5 X0_2R`: n 772, mean net R -0.039 [-0.123, +0.048], max drawdown 40.3 R, win rate 13.5%, mean fee 0.111 R, MDE (sample sd) 0.091 R, power for +0.10 R 87%; power_mde.py (two-point payoff model, rr 8.8): power 31%, MDE 0.337 R.
Robustness: the variant with the highest lower CI is `E0 S2 K5 X0_1R`: n 5775, -0.090 [-0.110, -0.069].

EXPECT (D4_LAYER_DECISION.md, written before this run): fee-net mean R per idea above 0 with the lower 95 % CI above 0 on at least one level class. Verdict rules, written before the run: PASS = frozen rule lower CI > 0; FAIL = upper CI < +0.10 R with power >= 50 % for a +0.10 R effect (OURS plausible effect); otherwise INCONCLUSIVE. Card step 4 (written 2026-10-13, governs): power from backtest/power_mde.py < 50 % reads INCONCLUSIVE; that model assumes a two-point payoff (+rr or -1), which overstates the variance of a many-outcome exit, so the sample-sd figures are given beside it. The frozen rule is read ONCE on VALIDATION by card lc-validation only on PASS; on FAIL or INCONCLUSIVE the operator decides.

## Data, windows, parameters

- Bars: `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-YYYY-MM.csv` (Binance USDT-M perpetual 1m; taker-buy volume = CVD proxy). Decisions 2022-04-01..2024-06-30 (standard DEV, Q79 addendum in levels_hold.md); 70 days of seed bars before each month for bias EMAs/fractals (OURS), 18 days for levels; `load_range(end_ms = 2024-07-01)` asserted. VALIDATION and HOLDOUT unread. event_table.csv / separation.md were NOT used (STALE per Q79 D4: built on VALIDATION-window bars); touches are regenerated here.
- Ideas: first touch per KEEP level per UTC day (8 KEEP families, levels_hold.md; duplicate prices merged), side = previous close vs level (Q79). L2 = next KEEP level beyond L1 against the trade; T1 = first KEEP level in favour; T2 = the second (arm P), else T1 + (T1 - L1).
- Entry filters, pre-registered in separation.md: E0 none, E1 RSI(14) on 5m closes holds 40 (long) / 60 (short), E4 price at the outer Bollinger band (20, 2); both from `event_table._features` (5m bars closed before the touch, from the day start). Note: E1/E4 were selected on the stale VALIDATION-window table; they are kept as pre-registered (no re-selection) and that selection is a known contamination of the VALIDATION read for these two filters.
- Fees SOURCED fees.py: maker 0.0002 (limit fills: entries, L2, targets), taker 0.0005 (stops, ladder exits, time stop). Stop-first inside a bar; no slippage; time stop = last 1m close of the UTC day.
- Stops OURS: K1 beyond the deepest planned entry by max(0.10 %, 0.20 % maker floor; card step 1); K2 0.10 % beyond L2; K3 0.5 x ATR(14) of 1h bars (plain SMA, FORMULAS.md s12) beyond L2; K4 a 15m close beyond L2 (exit at that close, R as K2); K5 0.10 % beyond the day extreme up to the touch bar, pushed beyond L2 when the extreme is inside. R = planned average entry minus stop; full planned size = 1.
- Ladder X2 OURS: half at T1; then per closed 5m bar: exit all on CVD against the trade or the opposite band (BB position >= 1 long / <= 0 short); half of the rest once on a flat bar (|delta| <= 0.25 x median |delta| of the prior 20 bars); stop keeps running.
- Bootstrap: 2000 resamples of UTC days, seed 20261020 (OURS). Max drawdown on ideas in touch order (ideas may overlap in time: per-idea, not a portfolio).
- Variants: 3 entry x 4 scale-in x 5 stops x 4 exits = 240, plus arm P and K0; all pre-registered in PLAN.md. Best-of-240 on DEV is optimistic by construction.

## Counts

| ideas | with L2 | with T1 | long | short | E1 true | E4 true | days |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5976 | 5775 | 5976 | 3081 | 2895 | 788 | 2046 | 818 |

Touches by family (a merged price counts for each family): 4h_fractal_high 1984, 4h_fractal_low 1963, naked_poc 732, prior_day_high 380, prior_day_low 345, prior_day_poc 583, prior_week_high 150, round_1000 831.

## Stops (E0, S0, X1: single entry at L1, all out at the first opposing level)

| stop | n | mean net R [95 % CI] | stop dist % (median) | stopped | BAD | GOOD | NEUTRAL | fee share of R (median planned) |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| K1 | 5976 | -0.462 [-0.502, -0.423] | 0.20 | 64.4% | 29.3% | 69.5% | 1.2% | 20.0% |
| K2 | 5775 | -0.265 [-0.296, -0.232] | 0.42 | 45.2% | 29.6% | 65.5% | 4.9% | 9.6% |
| K3 | 5775 | -0.158 [-0.184, -0.129] | 0.66 | 35.7% | 32.1% | 58.6% | 9.3% | 6.1% |
| K4 | 5775 | -0.234 [-0.308, -0.160] | 0.42 | 34.3% | 18.4% | 76.6% | 5.1% | 9.6% |
| K5 | 5976 | -0.197 [-0.245, -0.145] | 0.18 | 55.6% | 25.5% | 71.8% | 2.7% | 22.2% |

K0 (no stop, measurement): 4790 ideas reached T1 by day end; their maximum adverse excursion from L1: median 0.25 %, 90th percentile 1.27 % (= the winner-safe stop distance), 95th 1.87 %. BAD = stopped, then T1 reached before 1 more R against; GOOD = 1 more R against first; NEUTRAL = neither by day end. The stop is chosen on net R; the bad-stop rate is a diagnostic.

## Scale-in (E0, X1): mean net R [CI] per stop, and paired difference against S0 on the same ideas

| stop | S0 n | S0 L1 full | S1 n | S1 half L1 + half L2 | S2 n | S2 L2 only | S3 n | S3 1/3 L1 + 2/3 L2 | S1 - S0 | S2 - S0 | S3 - S0 |
|---|---:|---|---:|---|---:|---|---:|---|---|---|---|
| K1 | 5976 | -0.462 [-0.502, -0.423] | 5775 | -0.200 [-0.231, -0.168] | 5775 | -0.242 [-0.282, -0.197] | 5775 | -0.207 [-0.239, -0.174] | +0.253 [+0.222, +0.284] (n 5775) | +0.211 [+0.171, +0.254] (n 5775) | +0.245 [+0.213, +0.278] (n 5775) |
| K2 | 5775 | -0.265 [-0.296, -0.232] | 5775 | -0.302 [-0.336, -0.268] | 5775 | -0.429 [-0.487, -0.368] | 5775 | -0.324 [-0.360, -0.287] | -0.037 [-0.045, -0.030] (n 5775) | -0.164 [-0.206, -0.118] (n 5775) | -0.059 [-0.071, -0.047] (n 5775) |
| K3 | 5775 | -0.158 [-0.184, -0.129] | 5775 | -0.165 [-0.193, -0.135] | 5775 | -0.187 [-0.221, -0.152] | 5775 | -0.169 [-0.199, -0.138] | -0.007 [-0.012, -0.003] (n 5775) | -0.029 [-0.044, -0.013] (n 5775) | -0.012 [-0.019, -0.004] (n 5775) |
| K4 | 5775 | -0.234 [-0.308, -0.160] | 5775 | -0.257 [-0.348, -0.166] | 5775 | -0.316 [-0.484, -0.151] | 5775 | -0.268 [-0.371, -0.167] | -0.022 [-0.044, -0.001] (n 5775) | -0.081 [-0.193, +0.031] (n 5775) | -0.033 [-0.068, -0.000] (n 5775) |
| K5 | 5976 | -0.197 [-0.245, -0.145] | 5775 | -0.160 [-0.193, -0.126] | 5775 | -0.247 [-0.305, -0.186] | 5775 | -0.172 [-0.207, -0.136] | +0.046 [+0.011, +0.080] (n 5775) | -0.041 [-0.095, +0.011] (n 5775) | +0.034 [-0.002, +0.070] (n 5775) |

## All variants: n, mean net R [95 % CI] per entry filter

| S | K | X | E0 n | E0 all | E1 n | E1 RSI holds 40/60 | E4 n | E4 outer band |
|---|---|---|---:|---|---:|---|---:|---|
| S0 | K1 | X0_1R | 5976 | -0.441 [-0.475, -0.409] | 788 | -0.482 [-0.564, -0.398] | 2046 | -0.517 [-0.573, -0.459] |
| S0 | K1 | X0_2R | 5976 | -0.441 [-0.484, -0.398] | 788 | -0.519 [-0.625, -0.412] | 2046 | -0.509 [-0.572, -0.442] |
| S0 | K1 | X1 | 5976 | -0.462 [-0.502, -0.423] | 788 | -0.544 [-0.639, -0.441] | 2046 | -0.509 [-0.576, -0.441] |
| S0 | K1 | X2 | 5976 | -0.447 [-0.488, -0.405] | 788 | -0.512 [-0.617, -0.405] | 2046 | -0.485 [-0.554, -0.417] |
| S0 | K2 | X0_1R | 5775 | -0.227 [-0.258, -0.194] | 772 | -0.235 [-0.320, -0.153] | 1967 | -0.282 [-0.334, -0.229] |
| S0 | K2 | X0_2R | 5775 | -0.250 [-0.289, -0.210] | 772 | -0.213 [-0.318, -0.110] | 1967 | -0.312 [-0.376, -0.243] |
| S0 | K2 | X1 | 5775 | -0.265 [-0.296, -0.232] | 772 | -0.276 [-0.366, -0.188] | 1967 | -0.297 [-0.349, -0.242] |
| S0 | K2 | X2 | 5775 | -0.258 [-0.290, -0.225] | 772 | -0.260 [-0.349, -0.167] | 1967 | -0.282 [-0.337, -0.226] |
| S0 | K3 | X0_1R | 5775 | -0.142 [-0.175, -0.106] | 772 | -0.108 [-0.194, -0.016] | 1967 | -0.188 [-0.242, -0.129] |
| S0 | K3 | X0_2R | 5775 | -0.182 [-0.222, -0.141] | 772 | -0.134 [-0.242, -0.027] | 1967 | -0.256 [-0.327, -0.184] |
| S0 | K3 | X1 | 5775 | -0.158 [-0.184, -0.129] | 772 | -0.141 [-0.213, -0.069] | 1967 | -0.206 [-0.250, -0.159] |
| S0 | K3 | X2 | 5775 | -0.155 [-0.183, -0.125] | 772 | -0.135 [-0.208, -0.058] | 1967 | -0.197 [-0.243, -0.148] |
| S0 | K4 | X0_1R | 5775 | -0.213 [-0.284, -0.147] | 772 | -0.152 [-0.323, +0.011] | 1967 | -0.270 [-0.411, -0.141] |
| S0 | K4 | X0_2R | 5775 | -0.221 [-0.306, -0.137] | 772 | -0.087 [-0.292, +0.111] | 1967 | -0.316 [-0.481, -0.162] |
| S0 | K4 | X1 | 5775 | -0.234 [-0.308, -0.160] | 772 | -0.160 [-0.324, +0.008] | 1967 | -0.301 [-0.449, -0.163] |
| S0 | K4 | X2 | 5775 | -0.221 [-0.296, -0.141] | 772 | -0.145 [-0.320, +0.037] | 1967 | -0.279 [-0.434, -0.132] |
| S0 | K5 | X0_1R | 5976 | -0.213 [-0.245, -0.179] | 788 | -0.167 [-0.262, -0.075] | 2046 | -0.222 [-0.276, -0.163] |
| S0 | K5 | X0_2R | 5976 | -0.157 [-0.204, -0.110] | 788 | -0.087 [-0.210, +0.043] | 2046 | -0.149 [-0.223, -0.067] |
| S0 | K5 | X1 | 5976 | -0.197 [-0.245, -0.145] | 788 | -0.153 [-0.282, -0.018] | 2046 | -0.127 [-0.213, -0.042] |
| S0 | K5 | X2 | 5976 | -0.174 [-0.224, -0.117] | 788 | -0.101 [-0.245, +0.050] | 2046 | -0.081 [-0.172, +0.016] |
| S1 | K1 | X0_1R | 5775 | -0.186 [-0.213, -0.159] | 772 | -0.180 [-0.247, -0.111] | 1967 | -0.229 [-0.275, -0.183] |
| S1 | K1 | X0_2R | 5775 | -0.219 [-0.256, -0.181] | 772 | -0.182 [-0.279, -0.090] | 1967 | -0.257 [-0.322, -0.192] |
| S1 | K1 | X1 | 5775 | -0.200 [-0.231, -0.168] | 772 | -0.197 [-0.280, -0.114] | 1967 | -0.243 [-0.294, -0.189] |
| S1 | K1 | X2 | 5775 | -0.194 [-0.226, -0.161] | 772 | -0.186 [-0.272, -0.099] | 1967 | -0.231 [-0.285, -0.175] |
| S1 | K2 | X0_1R | 5775 | -0.283 [-0.307, -0.259] | 772 | -0.298 [-0.362, -0.233] | 1967 | -0.340 [-0.382, -0.297] |
| S1 | K2 | X0_2R | 5775 | -0.271 [-0.307, -0.235] | 772 | -0.275 [-0.369, -0.188] | 1967 | -0.329 [-0.387, -0.269] |
| S1 | K2 | X1 | 5775 | -0.302 [-0.336, -0.268] | 772 | -0.317 [-0.411, -0.219] | 1967 | -0.334 [-0.388, -0.276] |
| S1 | K2 | X2 | 5775 | -0.294 [-0.330, -0.260] | 772 | -0.301 [-0.397, -0.200] | 1967 | -0.320 [-0.378, -0.261] |
| S1 | K3 | X0_1R | 5775 | -0.151 [-0.180, -0.122] | 772 | -0.121 [-0.189, -0.049] | 1967 | -0.215 [-0.260, -0.168] |
| S1 | K3 | X0_2R | 5775 | -0.176 [-0.215, -0.135] | 772 | -0.118 [-0.221, -0.015] | 1967 | -0.220 [-0.279, -0.153] |
| S1 | K3 | X1 | 5775 | -0.165 [-0.193, -0.135] | 772 | -0.145 [-0.221, -0.070] | 1967 | -0.217 [-0.263, -0.169] |
| S1 | K3 | X2 | 5775 | -0.163 [-0.191, -0.132] | 772 | -0.140 [-0.218, -0.063] | 1967 | -0.210 [-0.257, -0.160] |
| S1 | K4 | X0_1R | 5775 | -0.274 [-0.348, -0.208] | 772 | -0.223 [-0.403, -0.069] | 1967 | -0.340 [-0.505, -0.205] |
| S1 | K4 | X0_2R | 5775 | -0.248 [-0.341, -0.162] | 772 | -0.136 [-0.345, +0.060] | 1967 | -0.335 [-0.529, -0.162] |
| S1 | K4 | X1 | 5775 | -0.257 [-0.348, -0.166] | 772 | -0.143 [-0.348, +0.059] | 1967 | -0.334 [-0.517, -0.164] |
| S1 | K4 | X2 | 5775 | -0.240 [-0.333, -0.144] | 772 | -0.124 [-0.341, +0.097] | 1967 | -0.312 [-0.505, -0.132] |
| S1 | K5 | X0_1R | 5775 | -0.137 [-0.161, -0.113] | 772 | -0.112 [-0.181, -0.044] | 1967 | -0.166 [-0.208, -0.122] |
| S1 | K5 | X0_2R | 5775 | -0.123 [-0.161, -0.082] | 772 | -0.088 [-0.192, +0.013] | 1967 | -0.160 [-0.222, -0.097] |
| S1 | K5 | X1 | 5775 | -0.160 [-0.193, -0.126] | 772 | -0.129 [-0.222, -0.028] | 1967 | -0.151 [-0.206, -0.096] |
| S1 | K5 | X2 | 5775 | -0.150 [-0.186, -0.114] | 772 | -0.109 [-0.208, +0.000] | 1967 | -0.134 [-0.194, -0.070] |
| S2 | K1 | X0_1R | 5775 | -0.161 [-0.183, -0.141] | 772 | -0.171 [-0.232, -0.110] | 1967 | -0.214 [-0.254, -0.174] |
| S2 | K1 | X0_2R | 5775 | -0.178 [-0.207, -0.149] | 772 | -0.160 [-0.242, -0.080] | 1967 | -0.229 [-0.277, -0.179] |
| S2 | K1 | X1 | 5775 | -0.242 [-0.282, -0.197] | 772 | -0.244 [-0.357, -0.132] | 1967 | -0.282 [-0.351, -0.211] |
| S2 | K1 | X2 | 5775 | -0.236 [-0.276, -0.191] | 772 | -0.238 [-0.351, -0.128] | 1967 | -0.273 [-0.343, -0.201] |
| S2 | K2 | X0_1R | 5775 | -0.288 [-0.313, -0.264] | 772 | -0.320 [-0.392, -0.247] | 1967 | -0.371 [-0.418, -0.323] |
| S2 | K2 | X0_2R | 5775 | -0.290 [-0.319, -0.263] | 772 | -0.301 [-0.381, -0.220] | 1967 | -0.365 [-0.416, -0.310] |
| S2 | K2 | X1 | 5775 | -0.429 [-0.487, -0.368] | 772 | -0.449 [-0.602, -0.276] | 1967 | -0.459 [-0.553, -0.354] |
| S2 | K2 | X2 | 5775 | -0.421 [-0.479, -0.360] | 772 | -0.439 [-0.595, -0.266] | 1967 | -0.451 [-0.543, -0.348] |
| S2 | K3 | X0_1R | 5775 | -0.122 [-0.143, -0.101] | 772 | -0.117 [-0.180, -0.057] | 1967 | -0.180 [-0.219, -0.139] |
| S2 | K3 | X0_2R | 5775 | -0.146 [-0.179, -0.112] | 772 | -0.094 [-0.184, -0.007] | 1967 | -0.209 [-0.261, -0.151] |
| S2 | K3 | X1 | 5775 | -0.187 [-0.221, -0.152] | 772 | -0.166 [-0.258, -0.076] | 1967 | -0.249 [-0.304, -0.190] |
| S2 | K3 | X2 | 5775 | -0.184 [-0.219, -0.148] | 772 | -0.166 [-0.258, -0.073] | 1967 | -0.241 [-0.299, -0.179] |
| S2 | K4 | X0_1R | 5775 | -0.251 [-0.339, -0.174] | 772 | -0.203 [-0.427, -0.024] | 1967 | -0.352 [-0.567, -0.184] |
| S2 | K4 | X0_2R | 5775 | -0.241 [-0.339, -0.157] | 772 | -0.187 [-0.417, +0.010] | 1967 | -0.308 [-0.530, -0.123] |
| S2 | K4 | X1 | 5775 | -0.316 [-0.484, -0.151] | 772 | -0.084 [-0.462, +0.293] | 1967 | -0.380 [-0.693, -0.082] |
| S2 | K4 | X2 | 5775 | -0.288 [-0.461, -0.112] | 772 | -0.062 [-0.479, +0.343] | 1967 | -0.354 [-0.679, -0.037] |
| S2 | K5 | X0_1R | 5775 | -0.090 [-0.110, -0.069] | 772 | -0.063 [-0.128, +0.000] | 1967 | -0.121 [-0.160, -0.082] |
| S2 | K5 | X0_2R | 5775 | -0.098 [-0.127, -0.070] | 772 | -0.039 [-0.123, +0.048] | 1967 | -0.138 [-0.189, -0.086] |
| S2 | K5 | X1 | 5775 | -0.247 [-0.305, -0.186] | 772 | -0.207 [-0.360, -0.039] | 1967 | -0.225 [-0.312, -0.127] |
| S2 | K5 | X2 | 5775 | -0.237 [-0.296, -0.176] | 772 | -0.191 [-0.348, -0.021] | 1967 | -0.212 [-0.300, -0.108] |
| S3 | K1 | X0_1R | 5775 | -0.208 [-0.230, -0.185] | 772 | -0.214 [-0.276, -0.151] | 1967 | -0.253 [-0.293, -0.210] |
| S3 | K1 | X0_2R | 5775 | -0.217 [-0.253, -0.183] | 772 | -0.209 [-0.301, -0.118] | 1967 | -0.259 [-0.315, -0.202] |
| S3 | K1 | X1 | 5775 | -0.207 [-0.239, -0.174] | 772 | -0.204 [-0.292, -0.117] | 1967 | -0.251 [-0.304, -0.196] |
| S3 | K1 | X2 | 5775 | -0.201 [-0.234, -0.167] | 772 | -0.194 [-0.285, -0.102] | 1967 | -0.240 [-0.295, -0.183] |
| S3 | K2 | X0_1R | 5775 | -0.360 [-0.381, -0.339] | 772 | -0.382 [-0.445, -0.320] | 1967 | -0.424 [-0.463, -0.382] |
| S3 | K2 | X0_2R | 5775 | -0.291 [-0.325, -0.260] | 772 | -0.303 [-0.385, -0.225] | 1967 | -0.352 [-0.405, -0.296] |
| S3 | K2 | X1 | 5775 | -0.324 [-0.360, -0.287] | 772 | -0.341 [-0.440, -0.235] | 1967 | -0.355 [-0.414, -0.294] |
| S3 | K2 | X2 | 5775 | -0.316 [-0.354, -0.279] | 772 | -0.325 [-0.427, -0.217] | 1967 | -0.342 [-0.403, -0.279] |
| S3 | K3 | X0_1R | 5775 | -0.161 [-0.187, -0.136] | 772 | -0.162 [-0.227, -0.098] | 1967 | -0.222 [-0.263, -0.178] |
| S3 | K3 | X0_2R | 5775 | -0.183 [-0.219, -0.142] | 772 | -0.132 [-0.230, -0.033] | 1967 | -0.246 [-0.304, -0.181] |
| S3 | K3 | X1 | 5775 | -0.169 [-0.199, -0.138] | 772 | -0.148 [-0.227, -0.071] | 1967 | -0.223 [-0.271, -0.174] |
| S3 | K3 | X2 | 5775 | -0.167 [-0.196, -0.136] | 772 | -0.144 [-0.225, -0.062] | 1967 | -0.216 [-0.266, -0.164] |
| S3 | K4 | X0_1R | 5775 | -0.337 [-0.409, -0.276] | 772 | -0.298 [-0.470, -0.150] | 1967 | -0.409 [-0.575, -0.273] |
| S3 | K4 | X0_2R | 5775 | -0.276 [-0.370, -0.190] | 772 | -0.179 [-0.395, +0.018] | 1967 | -0.348 [-0.545, -0.170] |
| S3 | K4 | X1 | 5775 | -0.268 [-0.371, -0.167] | 772 | -0.132 [-0.359, +0.093] | 1967 | -0.351 [-0.552, -0.165] |
| S3 | K4 | X2 | 5775 | -0.249 [-0.355, -0.144] | 772 | -0.111 [-0.357, +0.133] | 1967 | -0.328 [-0.545, -0.128] |
| S3 | K5 | X0_1R | 5775 | -0.201 [-0.222, -0.180] | 772 | -0.175 [-0.240, -0.114] | 1967 | -0.229 [-0.266, -0.190] |
| S3 | K5 | X0_2R | 5775 | -0.133 [-0.168, -0.098] | 772 | -0.094 [-0.186, -0.000] | 1967 | -0.170 [-0.223, -0.113] |
| S3 | K5 | X1 | 5775 | -0.172 [-0.207, -0.136] | 772 | -0.139 [-0.237, -0.034] | 1967 | -0.161 [-0.218, -0.102] |
| S3 | K5 | X2 | 5775 | -0.162 [-0.199, -0.123] | 772 | -0.119 [-0.223, -0.005] | 1967 | -0.143 [-0.207, -0.076] |

## Cuts of the frozen rule `E1 S2 K5 X0_2R` by HTF bias and by the other entry filter

| cut | agree n | agree mean [CI] | disagree n | disagree mean [CI] | neutral/none n | neutral mean [CI] |
|---|---:|---|---:|---|---:|---|
| B1_value_area | 93 | +0.141 [-0.154, +0.424] | 291 | +0.027 [-0.089, +0.148] | 388 | -0.133 [-0.249, -0.020] |
| B2_swing_1h | 206 | +0.053 [-0.116, +0.217] | 216 | -0.099 [-0.248, +0.066] | 350 | -0.057 [-0.178, +0.056] |
| B2_swing_4h | 229 | -0.051 [-0.188, +0.089] | 180 | -0.077 [-0.253, +0.108] | 363 | -0.013 [-0.135, +0.105] |
| B2_swing_6h | 220 | +0.042 [-0.086, +0.182] | 184 | -0.062 [-0.206, +0.096] | 368 | -0.076 [-0.212, +0.059] |
| B2_swing_12h | 230 | -0.022 [-0.188, +0.156] | 210 | -0.066 [-0.229, +0.098] | 332 | -0.035 [-0.133, +0.068] |
| B2_swing_1d | 243 | -0.022 [-0.158, +0.104] | 240 | -0.129 [-0.265, +0.019] | 289 | +0.021 [-0.123, +0.171] |
| B3_ema20_1h | 280 | -0.048 [-0.194, +0.092] | 492 | -0.034 [-0.133, +0.068] | 0 | - |
| B3_ema20_4h | 395 | -0.042 [-0.153, +0.074] | 377 | -0.037 [-0.157, +0.085] | 0 | - |
| B3_ema20_6h | 423 | -0.014 [-0.126, +0.091] | 349 | -0.070 [-0.197, +0.057] | 0 | - |
| B3_ema20_12h | 425 | -0.048 [-0.162, +0.064] | 347 | -0.030 [-0.148, +0.087] | 0 | - |
| B3_ema20_1d | 418 | -0.033 [-0.151, +0.084] | 354 | -0.047 [-0.160, +0.064] | 0 | - |
| E1 RSI holds 40/60 (yes / no / unknown) | 772 | -0.039 [-0.123, +0.048] | 0 | - | 0 | - |
| E4 outer band (yes / no / unknown) | 55 | -0.075 [-0.436, +0.283] | 644 | -0.016 [-0.106, +0.076] | 73 | -0.222 [-0.423, -0.018] |

## Fee stress (frozen rule): ideas whose planned fee share of R is at most the cut

| cut | n | mean net R [CI] | mean gross R | mean fee R |
|---|---:|---|---:|---:|
| <= 10% | 66 | -0.101 [-0.563, +0.401] | -0.000 | 0.100 |
| <= 25% | 138 | -0.011 [-0.334, +0.316] | +0.163 | 0.173 |
| <= 50% | 772 | -0.039 [-0.123, +0.048] | +0.072 | 0.111 |
| <= 100% | 772 | -0.039 [-0.123, +0.048] | +0.072 | 0.111 |

Break-even: mean gross R +0.072 against mean fee 0.111 R = the rule pays 0.6 x today's fees (break-even fee share of R = 0.072 R). All-taker stress: every fee leg at 0.0005 raises the mean fee to about 0.159 R.

## Arm P (levels_sizing METHOD.md: one loss budget 0.5 % of 10,000, capped 1:2:3 adds at 0.25/0.5 of a 0.4 % stop, staged exits)

n 5976, mean net R (R = the 50 USD budget) -0.130 [-0.151, -0.107], max drawdown 776.1 R; full 1:2:3 build in 2018 ideas. Paired against S0 K1 X1 on the same ideas: +0.333 [+0.295, +0.371] (n 5976).
Liquidation check (isolated margin, mark = bar low/high, maintenance 0.5 % OURS): max leverage 1.39 x, liquidations 0 (must be 0), stop-to-liquidation distance median 432.8 % of price.
Probe baseline (levels_sizing REPORT.md: -0.216 / -0.195 / -0.210 R, n 117) was measured on 2024-12..2025-03 first-minute-rejection signals, which is VALIDATION-window data under Q79; it is not the same signal set and is not paired here.

| arm P cut | n | mean net R [CI] |
|---|---:|---|
| fee share <= 10% | 0 | - |
| fee share <= 25% | 0 | - |
| fee share <= 50% | 5976 | -0.130 [-0.151, -0.107] |
| E1 yes | 788 | -0.130 [-0.180, -0.082] |
| E1 no | 3728 | -0.138 [-0.164, -0.112] |
| E4 yes | 2046 | -0.140 [-0.175, -0.104] |
| E4 no | 2252 | -0.132 [-0.164, -0.103] |
| random entry, arm P | 5976 | -0.245 [-0.267, -0.222] |
| random entry, S0 K1 X1 | 5976 | -0.373 [-0.410, -0.334] |
| arm P minus its random-entry control (paired) | 5976 | +0.115 [+0.086, +0.143] |

Random-entry control (OURS): the same day, side and level geometry shifted so that L1 is the open of one random 1m bar of the day (seed 20261020 + day); it measures what the level adds over entering anywhere.

## Files

- `frozen_rule.json`: the frozen DEV rule (no edits after); `ladder_ideas_dev.csv`: one row per idea (meta, bias, E flags, net R of the 20 S x K arms at X1, the 4 exits at the frozen S x K, arm P); `research/layer_lab/TRIALS.md`: one row per variant.
- Code: `ladder.py` (simulator, arm P, bias/ATR indices), `ladder_run.py` (this run), `test_ladder.py`.

