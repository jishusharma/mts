Regime mix: 360 weeks long DEV (2017-08-07..2024-06-24): bull 73 (20%) | bear 0 (0%) | range 222 (62%) | n/a 65 (18%) | bear weeks: primary Malkan (weekly AND monthly <=40) 0, proxy P40 (weekly <=40 alone, below SMA200, OURS) 57
Verdict: INCONCLUSIVE (underpowered), not FAIL and not PASS. Long window (BTCUSDT SPOT 2017-08..2024-06, PRE_REG_LONG.md frozen first) triples the sample but prereg_gate (m = 48) still BLOCKs every timeframe (15m closest: 282 days vs 424 needed). 0 of 48 confirmatory cells survived the DEV rule (dev_survivors_long.json is []); VALIDATION not read; HOLDOUT never loaded.

# rsi_divergence_mtf_gated long-window DEV pass (fee-net 0.14 %, exit 10 bars, day-clustered 95 % CI, Holm m = 48)

## Findings

- Malkan bear gate never fires: 0 bear weeks in 360 (monthly RSI14 never <= 40 since 2017-08; closest 40.4 in 2023-01). The first 65 weeks are n/a (SMA200 and monthly RSI14 need history). Longer history adds no bear weeks under the definition as written; the definition was NOT changed. Primary bearish aligned cells are empty (0 events on every TF).
- Primary bull gate, aligned long vs run 1 (same sign pattern, bigger n): 15m signal n 482 / 282 days, net -0.080 % [-0.216, +0.055], excess over bull drift +0.027 % (t 0.40); run 1 was n 164, net -0.176 % [-0.307, -0.045]. The CI now spans zero, the point estimate improved by about 0.10 points, but a gate-vs-ungated gap is not established: ungated 15m long net -0.102 % [-0.160, -0.045] (n 2091).
- 15m retest (N=10): n 345, net -0.205 % [-0.346, -0.065] (run 1: n 126, -0.130 % [-0.293, +0.034]); Holm p 0.185.
- 1h aligned long: signal n 125 / 94 days, net -0.066 % [-0.495, +0.364]; retest n 93, +0.097 % [-0.458, +0.652]. 4h aligned long: n 36, +0.185 % [-1.40, +1.77]; retest n 25, -0.437 % [-2.50, +1.63]. 1d: n 1 (a +15.2 % single trade, nothing to test). All CIs span zero.
- Bear proxy P40 (OURS, never Malkan's), aligned shorts: 15m signal n 434 / 236 days, net -0.158 % [-0.278, -0.039], excess -0.013 % (t -0.23); retest n 330, -0.222 % [-0.386, -0.059]. The raw p is 0.009 / 0.008 but the net is NEGATIVE (shorts lose after cost); Holm 0.38 / 0.32. 1h: n 101, +0.057 % [-0.439, +0.553]; 4h: n 26, +0.893 % [-0.661, +2.448], excess t 1.53 (positive, spans zero, n below the 30 floor). 1d: n 2, net +16.3 % with Holm p 0.013 / 0.000: an artifact of two clustered trades (n < 30 so it cannot survive; no weight on it).
- Ungated bearish divergence stays negative at 15m (n 2358, -0.179 % [-0.227, -0.131]), 1h (-0.275 %) and 4h retest (-1.385 % [-2.32, -0.45]), as in run 1.
- Window arms: W12 and W18 give identical aligned cells everywhere except one P40 1h cell (101 vs 102 events); C3_10 15m long signal n 478 (net -0.075 %), C5_14 n 187 (net -0.156 %): the window choice moves nothing.
- Survivor rule (n >= 30, >= 20 days, net > 0, Holm p < 0.05, excess t >= 2): 0 survivors. No cell is positive net with excess t >= 2; the only one with t >= 2 is the n = 2 artifact.

## Per cell, run 1 (DEV 2022-01..2024-06, futures 1m) vs long (2017-08..2024-06, spot), W12 aligned, signal entry

| Cell | Run 1 n / net [CI] | Long n / net [CI] | Reading |
|---|---|---|---|
| 15m bull long | 164 / -0.176 [-0.307, -0.045] | 482 / -0.080 [-0.216, +0.055] | less negative, now spans zero |
| 1h bull long | 43 / +0.111 [-0.394, +0.615] | 125 / -0.066 [-0.495, +0.364] | sign flipped, noise |
| 4h bull long | 18 / -0.736 [-2.58, +1.11] | 36 / +0.185 [-1.40, +1.77] | sign flipped, noise |
| 1d bull long | 1 / +15.25 (single trade) | 1 / +15.19 (same trade) | nothing to test |
| 15m/1h/4h/1d bear short, Malkan gate | 0 | 0 | gate never fires |
| 15m bear short, P40 proxy | not run | 434 / -0.158 [-0.278, -0.039] | negative |
| 1h bear short, P40 proxy | not run | 101 / +0.057 [-0.439, +0.553] | zero |
| 4h bear short, P40 proxy | not run | 26 / +0.893 [-0.661, +2.448] | n < 30, spans zero |
| 1d bear short, P40 proxy | not run | 2 / +16.3 (artifact) | n = 2 |

## What it says

Tripling the history still does not make the full Malkan gate testable on BTC: bull setups are rare (73 of 295 tagged weeks), the strict bear gate never occurs, and the best-powered cell (15m aligned long) is net negative or zero after 0.14 % cost with excess over drift indistinguishable from zero. The weekly-only bear proxy gives 57 bear weeks but no net-positive, powered short either. Not a PASS and, because every cell is underpowered, not a FAIL: INCONCLUSIVE. The next step would be more symbols, not another BTC DEV read.

## Data and honesty notes

- Spot, not futures: different series from run 1 (no splice). Events before 2022-01 (the new DEV data, PRE_DEV in splits.py terms, declared in PRE_REG_LONG.md) and the run-1 DEV window are pooled; the run-1 window was already seen in run 1, so the new-data-only effect is not isolated here (a fresh-vs-old split was not pre-declared and is not computed).
- Exchange-maintenance gaps in the spot archive (9-25 per series) are not filled; "10 bars" counts bars present.
- Data loaded only to 2024-07-01 (splits.DEV_END, exclusive); VALIDATION unread; HOLDOUT never loaded.

Files: PRE_REG_LONG.md, BLOCKED_LONG.md, counts_long.csv, dev_cells_long.csv (all cells incl. regime_def column), dev_survivors_long.json, regime_mix_dev_long.txt, study_long.py, test_long_wiring.py (6 tests; the two proxy tests failed on the pre-change code with the proxy branch disabled: `assert 'range' == 'bear'`, 2 failed 4 passed, then 6 passed).
