# RESULT: phase-matched trade types (edge9-phase-matched-trades-1114)

**VERDICT: FAIL. 0 of 4 matched rows pass any gate, all four are powered (n 1,719 to 10,585), and the matched cell does NOT beat the mismatched cells.** The operator's principle (right trade in the right phase) is not supported by these four rule definitions: every cell is net-negative on VALIDATION, matched or not.

PRE_REG: PRE_REG.md (commit affb29839) unchanged. Data: Bybit v5 public linear, 20 coins, 1h + 1d to 2026-11-13 19:00Z (daily phase through 2026-11-12). Fees 12 bp round trip + funding. DEV to 2023-12-31, VALIDATION 2024-01-01 on. Total trades simulated: 378,610 (all cells, all exits). Test file: 7 tests pass; with `PHASE_LAG=0` (phase of the same day used for earlier bars of that day) test_phase_decided_with_previous_day_only FAILS, as required.

## Key reading
- Matched minus best mismatched cell (VALIDATION mean R, day-clustered diff): T1 -0.042 (se 0.033), T2 -0.017 (se 0.046), T3 -0.336 (se 0.323), T4 -0.058 (se 0.049). None positive.
- Costs are the killer: cost = 0.22 to 0.34 R per trade for T1/T2/T3 (stops are only 0.5 to 1.4 % away), while gross R before costs is about -0.08 to -0.16 (post-hoc descriptive, VALIDATION). T4 (stop at the 1h swing high, median 4 % away) has cost 0.04 R and gross about 0, so it sits near zero net: T4/RANGE +0.010 is the only positive cell, and it is a mismatched cell, not significant.
- Win rates (2R rows) 29 to 31 % against a 33 % break-even before costs.
- T4 observed mean net % is -0.57 % vs random -0.13 % (random p = 1.0): the few very distant swing-high stops lose large percentages; R-weighted mean looks mild (-0.05 R) but per-trade pct is worse than random entries.
- Caveat: only these four OURS rule definitions were tested; a failure here does not refute the phase idea, it says these entries with 12 bp costs have no edge in either matched or mismatched phase. No parameter was tuned after seeing outcomes.

```
Regime mix: pooled 37536 coin-days: UP 23.1% DOWN 31.4% RANGE 45.5%; VALIDATION days: UP 22.0% DOWN 32.1% RANGE 46.0%; BTC all: UP 31.8% DOWN 27.6% RANGE 40.6%
BTC today: {"last_closed_day": "2026-11-12", "close": 71435.0, "ma20": 77301.185, "ma20_5ago": 79409.955, "adx": 23.297724422258433, "pdi": 11.038687302919657, "mdi": 27.7779601272498, "phase": "DOWN"}
BTC last 10 daily labels: ['DOWN', 'RANGE', 'DOWN', 'RANGE', 'RANGE', 'RANGE', 'DOWN', 'DOWN', 'DOWN', 'DOWN']

MATRIX VALIDATION mean net R (n, win%) -- exit: primary
type | exit | UP | DOWN | RANGE
T1 | 2R | -0.340 (n=8341, 31.0%) [DEV -0.313 n=7365] | -0.383* (n=10585, 31.0%) [DEV -0.349 n=7481] | -0.420 (n=17225, 30.2%) [DEV -0.329 n=11553]
T2 | 2R | -0.336* (n=6640, 30.9%) [DEV -0.277 n=4729] | -0.319 (n=11616, 31.0%) [DEV -0.293 n=7602] | -0.411 (n=16085, 29.0%) [DEV -0.281 n=9463]
T3 | mid | -0.104 (n=978, 17.3%) [DEV -0.490 n=1016] | -0.535 (n=972, 12.4%) [DEV -0.374 n=628] | -0.440* (n=1719, 16.1%) [DEV -0.363 n=1275]
T4 | 2R | -0.053 (n=1559, 44.1%) [DEV -0.085 n=1258] | -0.047* (n=2465, 41.1%) [DEV -0.039 n=1742] | 0.010 (n=3377, 46.2%) [DEV -0.046 n=2395]

MATRIX VALIDATION mean net R (n, win%) -- exit: 1R
type | exit | UP | DOWN | RANGE
T1 | 1R | -0.404 (n=9508, 41.3%) [DEV -0.376 n=8450] | -0.449 (n=12092, 41.6%) [DEV -0.398 n=8637] | -0.473 (n=19744, 40.6%) [DEV -0.395 n=13303]
T2 | 1R | -0.382 (n=7582, 42.2%) [DEV -0.334 n=5387] | -0.367 (n=13293, 42.1%) [DEV -0.339 n=8751] | -0.434 (n=18385, 40.4%) [DEV -0.329 n=10832]

MATRIX VALIDATION mean net R (n, win%) -- exit: PD
type | exit | UP | DOWN | RANGE
T1 | PD | -0.208 (n=7266, 16.4%) [DEV -0.241 n=6371] | -0.207 (n=9241, 14.9%) [DEV -0.197 n=6545] | -0.318 (n=14995, 15.0%) [DEV -0.171 n=10052]
T2 | PD | -0.297 (n=5907, 16.1%) [DEV -0.139 n=4299] | -0.224 (n=10313, 16.7%) [DEV -0.235 n=6743] | -0.302 (n=14284, 15.4%) [DEV -0.163 n=8561]
(* = matched cell)

BTC ALONE VALIDATION mean net R primary exit (n)
T1 | -0.371 (n=451) | -0.433 (n=399) | -0.464 (n=755)
T2 | -0.430 (n=370) | -0.418 (n=482) | -0.463 (n=646)
T3 | -0.015 (n=83) | 0.133 (n=58) | -0.523 (n=124)
T4 | -0.030 (n=94) | -0.008 (n=102) | -0.083 (n=149)

GATES matched rows (VALIDATION, primary exit)
row | n | win% | meanR | CI trade | CI day | random p | cluster p | BH | ex-best-5 | matched-minus-best-mismatch (diff, se)
T1/DOWN | 10585 | 31.0 | -0.383 | [-0.410, -0.356] | [-0.431, -0.333] | 0.448 (obs -0.122% vs rand -0.124%) | 1.0000 | N | -0.396 | DOWN vs UP -0.340: -0.042 (se 0.033)
   gates: {'n': True, 'ci_trade': False, 'ci_day': False, 'rand': False, 'bh': False, 'ex5': False} -> FAIL
T2/UP | 6640 | 30.9 | -0.336 | [-0.368, -0.304] | [-0.401, -0.270] | 0.872 (obs -0.135% vs rand -0.106%) | 1.0000 | N | -0.361 | UP vs DOWN -0.319: -0.017 (se 0.046)
   gates: {'n': True, 'ci_trade': False, 'ci_day': False, 'rand': False, 'bh': False, 'ex5': False} -> FAIL
T3/RANGE | 1719 | 16.1 | -0.440 | [-0.601, -0.261] | [-0.630, -0.232] | 0.990 (obs -0.327% vs rand -0.132%) | 1.0000 | N | -0.578 | RANGE vs UP -0.104: -0.336 (se 0.323)
   gates: {'n': True, 'ci_trade': False, 'ci_day': False, 'rand': False, 'bh': False, 'ex5': False} -> FAIL
T4/DOWN | 2465 | 41.1 | -0.047 | [-0.084, -0.008] | [-0.141, 0.043] | 1.000 (obs -0.574% vs rand -0.134%) | 0.8395 | N | -0.105 | DOWN vs RANGE 0.010: -0.058 (se 0.049)
   gates: {'n': True, 'ci_trade': False, 'ci_day': False, 'rand': False, 'bh': False, 'ex5': False} -> FAIL

VERDICT: FAIL (0 of 4 matched rows pass)
```

## Notes
- Phase of BTC today: last closed day 2026-11-12, close 71,435 below MA20 77,301 (MA20 falling vs 79,410 five days ago), ADX 23.3, +DI 11.0 < -DI 27.8: **DOWN**. Last 10 daily labels: DOWN, RANGE, DOWN, RANGE, RANGE, RANGE, DOWN, DOWN, DOWN, DOWN. DOWN-phase matched trades (T1 short rally, T4 breakdown) would be the ones allowed today, but both are net-negative on VALIDATION.
- Random-entry control compares mean net % per trade vs random bars of the same coin, phase, side, holding time.
- BH family = the 4 matched rows (primary exit); 1R and PDL/PDH exits are descriptive only.
- Raw data and trades.npy live in runtime_data (git-ignored).
