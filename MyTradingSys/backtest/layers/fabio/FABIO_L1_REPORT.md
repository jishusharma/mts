# Fabio L1 backtest - CVD absorption, escalation breakout, volume FVG

Driver: `MyTradingSys/backtest/layers/fabio/run_backtest.py` (tests: `test_run_backtest.py`). Raw results
(gitignored): `Dumps/backtest/runs/fabio_l1/{5m,15m,1h}_result.json`, `summary.json`. Runtime 19m47s (full grid).
Data: BTCUSDT 1m, 2022-01-01..2026-09-26 (2,491,200 bars, `Dumps/backtest/raw_1m_2022` + `Dumps/backtest/raw`),
resampled to 5m/15m/1h (tbv summed per bucket; CVD/delta exact from taker-buy volume).
Split: chronological 70% IS / 30% OOS per timeframe. Chosen parameters = best IS mean return at h=5 among
grid points with >= 5 IS events, then frozen and applied to OOS. PBO = `bt/ref_pbo.ref_pbo_cscv` on IS daily-bucketed
h=5 returns over the whole grid (no-signal days = 0, S=12 blocks). Fees: 0.10% round trip, subtracted from
mean return ("net"). Horizons h = 1, 5, 20 bars. All thresholds are UNDEFINED in the video, hence the grids:
- CVD absorption (FAB-007/008): swing width left=right in {2,3,5} x price_tolerance in {0.05,0.1,0.2,0.5}% (12 variants).
- Escalation (FAB-002/003): level_tolerance {0.1,0.2}% x aggression_k {1.5,2,3} x record_lookback {20,50} (12 variants).
- Volume FVG (FAB-005/006): fixed (20 bins, 70% VA, swings 2/2, first touch within 200 bars); no grid, so no PBO.
  Real (lowest-volume VA bin) is compared against a random-VA-bin control; both trade readings reported.

Verdict rule: "edge" needs OOS n >= 30, OOS net mean > 0 at h=5 and PBO < 0.5; "insufficient n" if OOS n < 30;
otherwise "no edge". Baseline (buy every bar, OOS) mean return is ~0.000% at every horizon and tf.

## Caveats (read before trusting a number)
- Escalation is O(swings x bars) in the committed detector (each level is scanned to the end of the series;
  infeasible at 5m). The driver runs it on disjoint 1000-bar chunks with 500 bars of warm-up, so a level lives at
  most ~1500 bars. This is a deviation from the spec'd "unbounded" level life.
- Events overlap (h=5/20 windows of neighbouring events); n is not independent samples. No stop/target simulation:
  fixed-horizon close-to-close returns only (the L1 methodology).
- FVG "touch" side is not defined in the source, so both readings are reported (bounce = fade the touch,
  through = continuation); they are exact mirror images, so one is always the loser.
- No regime split; the OOS period (last ~30% of 2022-2026) is one market regime.

## Rules x timeframe (OOS = frozen IS-best params; mean = gross mean forward return, net = minus 0.10%)

| Rule | TF | Chosen params | IS n / h5 mean | OOS n / h1 | OOS h5 (gross / net) | OOS h20 (gross / net) | OOS hit h5 | PBO | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| cvd_absorption | 5m | w5, tol 0.1% | 3373 / +0.005% | 1639 / +0.001% | +0.000% / -0.100% | +0.001% / -0.099% | 48.2% | 0.683 | no edge |
| cvd_absorption | 15m | w3, tol 0.2% | 2146 / -0.002% | 982 / +0.003% | +0.001% / -0.099% | -0.009% / -0.109% | 48.2% | 0.330 | no edge |
| cvd_absorption | 1h | w5, tol 0.05% | 228 / +0.067% | 109 / +0.023% | -0.042% / -0.142% | +0.001% / -0.099% | 45.9% | 0.333 | no edge |
| escalation | 5m | lt 0.2%, k 3, lb 50 | 16999 / +0.016% | 7908 / -0.007% | -0.004% / -0.104% | +0.029% / -0.071% | 46.1% | 0.657 | no edge |
| escalation | 15m | lt 0.1%, k 1.5, lb 50 | 2526 / +0.039% | 1095 / -0.024% | -0.069% / -0.169% | -0.139% / -0.239% | 42.6% | 0.174 | no edge |
| escalation | 1h | lt 0.2%, k 1.5, lb 50 | 378 / +0.146% | 182 / +0.141% | +0.213% / +0.113% | -0.000% / -0.100% | 48.4% | 0.756 | no edge (fails PBO; see below) |

IS h1 / h20 means for the chosen combos: cvd 5m -0.002%/-0.010%, 15m +0.003%/+0.032%, 1h -0.027%/+0.213%;
escalation 5m -0.000%/+0.010%, 15m +0.020%/+0.048%, 1h +0.036%/+0.276%. OOS h20 n is the same as h5 n minus
<= 5 tail events. Every gross mean at 5m/15m is within a few hundredths of a percent of zero, i.e. 3-100x smaller
than the 0.10% fee.

Only cell with positive OOS net at h5: escalation 1h (+0.113% net, n=182, hit rate 48.4%, so a few large winners).
It is not called an edge because PBO = 0.756 (in 75.6% of CSCV splits the IS-best variant ranks at or below the median OOS), h20 falls to zero, and it does not repeat at 5m/15m (where the same rule is negative OOS).
Treat it as a hypothesis for a longer/other-asset retest, not a result.

## Volume FVG (real lowest-volume bin vs random-VA-bin control; gross mean return, no PBO: no grid)

| TF | Legs | Reading | Real IS n / h5 | Real OOS n / h5 | Control IS n / h5 | Control OOS n / h5 | Verdict |
|---|---|---|---|---|---|---|---|
| 5m | 58482 | bounce | 2660 / -0.013% | 1228 / +0.011% | 2699 / -0.004% | 1222 / -0.003% | no edge (real ~ control ~ 0) |
| 5m | | through | 2660 / +0.013% | 1228 / -0.011% | 2699 / +0.004% | 1222 / +0.003% | no edge |
| 15m | 19782 | bounce | 823 / +0.004% | 377 / -0.002% | 825 / +0.010% | 379 / +0.027% | no edge |
| 15m | | through | 823 / -0.004% | 377 / +0.002% | 825 / -0.010% | 379 / -0.027% | no edge |
| 1h | 5000 | bounce | 186 / +0.062% | 93 / +0.274% | 189 / +0.134% | 91 / +0.130% | no edge (IS real < control; OOS n 93) |
| 1h | | through | 186 / -0.062% | 93 / -0.274% | 189 / -0.134% | 91 / -0.130% | no edge |

The real level never beats the random-bin control consistently: at 1h the real bin is BELOW control in IS
(+0.062% vs +0.134%) and above only in OOS (+0.274% vs +0.130%, n=93), which is sign-unstable; at 5m/15m both are
zero. h1 and h20 (in the JSON) tell the same story. The low-volume-bin premise (FAB-006) is not supported.

## Answer: is Fabio producing quality setups?

No, not as coded here on BTCUSDT 5m/15m/1h. None of the three rules produces a return that survives 0.10% round-trip
fees out of sample with PBO < 0.5. CVD absorption and volume FVG are indistinguishable from zero (and from their
random controls). Escalation breakout is the only one that shows anything: a positive OOS net at 1h, but with PBO
0.76 and n=182 it does not qualify, and it is negative at 5m/15m. Caveat: these are the mechanical readings of
transcript rules with guessed thresholds and fixed-horizon exits; Fabio's discretionary judgement (context, session,
stops/targets, size) is not tested, so this says "the mechanical signals have no standalone edge", not "Fabio has none".

Tom comparison: not done. There is no Tom setup detector in Python under `MyTradingSys/backtest/layers` (Tom rules live
in the core/live system, not reproducible offline here), so "Tom with vs without an agreeing Fabio signal" cannot be
computed; Fabio stays a separate layer per PROJECT_VISION.

## Recommended live-trading params for the testnet auto-trader (recommendation only; execution/ untouched)

| Fabio rule | TF | Recommendation | Params if sampled | Rationale |
|---|---|---|---|---|
| cvd_absorption | 5m, 15m, 1h | disable | - | OOS gross <= +0.003%, all net negative, 5m PBO 0.68 |
| volume_fvg | 5m, 15m | disable | - | real = random control = 0 |
| volume_fvg | 1h | disable (or log-only) | - | real < control in IS; n=93 OOS |
| escalation | 5m, 15m | disable | - | negative OOS at both (15m -0.069% gross h5) |
| escalation | 1h | sample live at minimum size, log-only or 1 lot, as a forward test | level_tol 0.2%, aggression_k 1.5, record_lookback 50, horizon 5 bars, no wider than 1h | only positive OOS net cell (+0.113%, n=182) but PBO 0.76: needs ~6 months of live-forward n>=100 before any weight |

Also: size for expected gross move well under 0.10% - any Fabio signal on 5m/15m is fee-negative by construction;
do not let Fabio gate or filter Tom entries.
