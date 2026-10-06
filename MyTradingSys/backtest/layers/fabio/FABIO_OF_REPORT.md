> **Fee note (2026-10-06, bug B081 residue):** results in this report were produced with the legacy fee pair
> (3.5 bp taker, -1.5 bp maker rebate, per side), not the fees stated in the text below (taker 5 bp, maker 2 bp). The
> API-verified Deribit schedule (fees.py) is taker 5 bp, maker 0. Correct fees only lower net R, so the 'no edge /
> insufficient n' verdicts stand. A rerun is needed before any reuse of the numbers.

# Fabio on true order flow (aggTrades) - conditional-model test

Modules: `orderflow_bars.py` (aggTrades -> 1m order-flow bars), `fabio_of_model.py` (state/location/trigger/management
simulator), `run_of_model.py` (driver), tests `test_orderflow_bars.py`, `test_fabio_of_model.py`. Raw results (off C:):
`F:\MTS\data\fabio_of\results.json`, `tables.md`. Reproduce: `python -m MyTradingSys.backtest.layers.fabio.run_of_model`.

## Read this first (limits)
- Data: Binance USD-M BTCUSDT aggTrades, 2026-06-01..2026-09-28 (120 days, 1,440 bars/day, no gaps). Big-trade thresholds
  are the 99th/99.9th percentile of aggTrade size over the PRIOR 30 days, so only days with a full window count:
  **2026-07-01..2026-09-28 = 90 days** (IS 62 days Jul 1-Aug 31, OOS 28 days Sep 1-28). June is warm-up only.
- **One regime, 90 days.** OOS is 28 days; most cells have OOS n of 15-90 trades and many are below the n >= 30 verdict floor.
  Nothing here is evidence about other regimes; a positive cell at n = 16 is noise, not a lead.
- Fixed-horizon kline-proxy verdicts (FABIO_L1) are quoted for reference only; units differ (return % vs R), so they are
  not numerically comparable to the tables below.
- Aggressor delta / CVD were ALREADY exact in the kline proxy (taker-buy volume is the aggressor sum). Cross-check vs klines on
  2026-09-01..26: 94% of 1m bars identical (median diff 3e-14); the rest differ by minute-edge attribution (volume diff ==
  delta diff, p99 0.45 BTC, max 12 BTC). What aggTrades ADDS is big-trade flow (size distribution), the per-price footprint
  (real volume profile / POC / LVN) and max single trade. So the "proxy" control below keeps the same delta but drops the
  big-trade confirmation and builds the profile by spreading each bar's volume uniformly over [low, high].

## Why the fixed-horizon method mis-measured this model
FABIO_L1 scored every trigger fire with a symmetric close-to-close return at a fixed horizon (no state, no location, no
stop/breakeven/target), which averages a conditional, asymmetric payoff (only at prior-value locations, fade in balance /
go-with in imbalance, tight stop, BE at +1R, 3R/HVN target, low win rate with large winners) over the ~99% of fires his
location/state filter would have refused; it tests the trigger alone, not the model.

## Model as simulated (order per DSA rulebook "Testable core": location -> context -> trigger -> management)
- Sessions (UTC): Asia 00:00-08:00, London 08:00-13:30, NY 13:30-21:00; prior session = the previous one (Asia's prior =
  previous NY). Prior-session profile from the real footprint (10 USD bins): POC, 70% value area (VAH/VAL), LVNs (interior
  local minima <= 0.5 x median bin), HVNs (local maxima >= 0.6 x POC volume).
- State fixed at the close of the session's first 15 minutes: close > VAH imbalance-up, < VAL imbalance-down, else BALANCE.
  Trades only afterwards (causal). Sessions seen (of 90): Asia balance 55 / up 20 / down 15; London 62 / 15 / 13; NY 48 / 21 / 21.
- Location: VAH, VAL, POC, LVN within 0.1%. Trigger at tf-bar close (5m or 15m):
  - BALANCE fade (absorption): bar approaches the level, bar delta into it >= k x mean |delta| of the previous 20 bars, big-trade
    delta on that side (>= 2 prints at the 99th or 99.9th percentile size, big buy > big sell for an up approach), price fails
    (extreme within 0.1% of the level, close back on the approach side) -> fade.
  - IMBALANCE with-break (aggression): aggression bar closes through the level with delta >= k x mean and big-trade delta the
    same way, then within 6 bars a retest bar touches the level (0.1%) and closes beyond it (holds) -> go with the break.
- Management (1m, bar by bar): stop 1 tick beyond the trigger extreme (break: min/max of aggression and retest bar); +1R -> stop
  to breakeven; target = min(3R, nearest HVN/POC at least 1R away); optional trail 1R behind the running extreme after +2R; exit
  at session end. Stop assumed hit before target inside one bar. Fees: taker 0.05%/side; maker 0.02% for the LIMIT entry variant
  (fades only: limit at the level, fills if touched within 3 tf bars); all exits taker; no slippage. Net R = gross R -
  (fee_in + fee_out) x entry / risk.
- Grid (counted in PBO): tf {5m,15m} x big-trade percentile {99, 99.9} x k {1.5, 2.5} x entry {market, limit} x management
  {plain, trail} x minimum stop {spec tight stop, widened to >= 0.15% of price} = 64 variants (true flow); 32 for the proxy
  control (no percentile). Trades with a stop tighter than 0.02% of price are skipped as untradeable. IS-best variant = highest
  IS net expectancy with >= 20 IS trades, frozen and read out on OOS. PBO = CSCV (S=12) on IS daily net R. Verdict rule as
  FABIO_L1: edge needs OOS n >= 30, OOS net expectancy > 0 and PBO < 0.5; OOS n < 30 is "insufficient n"; else "no edge".
  (A low PBO with every variant negative only means the ranking is stable, not that it is profitable.)

## Results (OOS = 28 days; "avg gross R" is before fees, "exp net R" after; BE share = exits at the breakeven stop)

| flow | model | scope | chosen variant (tf, big pct, k, entry, mgmt, min-stop) | IS n / exp net R | OOS n | win | avg gross R | exp net R | PF | maxDD R | BE share | PBO | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| true | balance_fade | all | 15m, p99, k2.5, limit, trail, floor 0.0015 | 67 / -0.509 | 29 | 24% | -0.031 | -0.498 | 0.40 | 14.4 | 21% | 0.11 | insufficient n |
| true | balance_fade | ny | 15m, p999, k1.5, limit, plain, floor 0.0015 | 33 / -0.196 | 22 | 32% | +0.367 | -0.099 | 0.88 | 8.7 | 14% | 0.28 | insufficient n |
| true | balance_fade | asia | 5m, p999, k1.5, mkt, trail, floor 0.0015 | 117 / -0.489 | 73 | 36% | +0.159 | -0.503 | 0.43 | 36.7 | 14% | 0.31 | no edge |
| true | balance_fade | london | 5m, p99, k1.5, limit, trail, floor 0.0015 | 109 / -0.560 | 39 | 28% | +0.073 | -0.393 | 0.53 | 18.5 | 15% | 0.16 | no edge |
| true | imb_break | all | 5m, p999, k2.5, mkt, plain, floor 0.0015 | 48 / -0.387 | 37 | 24% | +0.088 | -0.426 | 0.53 | 15.9 | 19% | 0.31 | no edge |
| true | imb_break | ny | 5m, p999, k1.5, mkt, plain, floor 0.0015 | 31 / -0.594 | 31 | 29% | +0.260 | -0.265 | 0.67 | 8.2 | 19% | 0.70 | no edge |
| true | imb_break | asia | 5m, p99, k1.5, mkt, trail, floor 0.0015 | 49 / -0.513 | 20 | 20% | -0.020 | -0.575 | 0.37 | 15.2 | 25% | 0.40 | insufficient n |
| true | imb_break | london | 5m, p99, k1.5, mkt, plain, floor 0.0015 | 23 / -0.404 | 15 | 27% | +0.028 | -0.506 | 0.43 | 8.0 | 20% | 0.71 | insufficient n |
| true | combined | all | 15m, p99, k2.5, limit, trail, floor 0.0015 | 89 / -0.513 | 42 | 29% | +0.041 | -0.428 | 0.43 | 18.0 | 24% | 0.12 | no edge |
| true | combined | ny | 15m, p999, k2.5, limit, trail, floor 0.0015 | 22 / -0.198 | 16 | 44% | +0.393 | -0.053 | 0.90 | 4.7 | 19% | 0.20 | insufficient n |
| true | combined | asia | 5m, p999, k1.5, mkt, trail, floor 0.0015 | 147 / -0.495 | 87 | 32% | +0.134 | -0.508 | 0.42 | 44.2 | 18% | 0.14 | no edge |
| true | combined | london | 5m, p999, k1.5, limit, trail, floor 0.0015 | 105 / -0.512 | 47 | 26% | -0.025 | -0.503 | 0.42 | 24.5 | 19% | 0.22 | no edge |
| proxy | balance_fade | all | 15m, p99, k2.5, limit, plain, floor 0.0015 | 56 / -0.343 | 20 | 20% | -0.034 | -0.501 | 0.36 | 10.5 | 30% | 0.00 | insufficient n |
| proxy | balance_fade | ny | 15m, p99, k1.5, limit, plain, floor 0.0015 | 34 / -0.010 | 16 | 38% | +0.539 | +0.072 | 1.11 | 4.8 | 25% | 0.03 | insufficient n |
| proxy | balance_fade | asia | 15m, p99, k1.5, limit, plain, floor 0.0015 | 43 / -0.285 | 21 | 19% | -0.042 | -0.508 | 0.41 | 12.8 | 24% | 0.10 | insufficient n |
| proxy | balance_fade | london | 5m, p99, k1.5, limit, plain, floor 0.0015 | 100 / -0.643 | 30 | 27% | -0.113 | -0.580 | 0.33 | 17.4 | 13% | 0.04 | no edge |
| proxy | imb_break | all | 5m, p99, k2.5, mkt, plain, floor 0.0015 | 50 / -0.540 | 34 | 26% | +0.184 | -0.340 | 0.58 | 13.4 | 21% | 0.56 | no edge |
| proxy | imb_break | ny | 5m, p99, k1.5, mkt, plain, floor 0.0015 | 27 / -0.558 | 31 | 39% | +0.456 | -0.077 | 0.88 | 6.0 | 23% | 0.23 | no edge |
| proxy | imb_break | asia | 5m, p99, k1.5, mkt, trail, floor 0.0015 | 44 / -0.657 | 18 | 17% | -0.117 | -0.654 | 0.33 | 17.6 | 22% | 0.29 | insufficient n |
| proxy | imb_break | london | 5m, p99, k1.5, mkt, plain, floor 0.0015 | 24 / -0.433 | 9 | 22% | -0.464 | -0.953 | 0.07 | 9.3 | 0% | 0.71 | insufficient n |
| proxy | combined | all | 15m, p99, k1.5, limit, plain, floor 0.0015 | 154 / -0.459 | 83 | 25% | +0.072 | -0.390 | 0.50 | 35.5 | 20% | 0.00 | no edge |
| proxy | combined | ny | 15m, p99, k2.5, limit, trail, floor 0.0015 | 20 / -0.059 | 11 | 45% | +0.486 | +0.041 | 1.08 | 3.9 | 27% | 0.02 | insufficient n |
| proxy | combined | asia | 15m, p99, k1.5, limit, plain, floor 0.0015 | 58 / -0.431 | 31 | 16% | -0.052 | -0.520 | 0.38 | 18.2 | 29% | 0.11 | no edge |
| proxy | combined | london | 5m, p99, k1.5, limit, plain, floor 0.0015 | 124 / -0.603 | 39 | 26% | -0.194 | -0.666 | 0.27 | 26.0 | 10% | 0.07 | no edge |

Grid summary (all variants of each group, OOS only): variants / with OOS n >= 30 / of those net exp > 0 / median gross R / median net R

| flow | model | scope | variants | OOS n>=30 | net exp > 0 | median gross R | median net R |
|---|---|---|---|---|---|---|---|
| true | balance_fade | all | 64 | 52 | 0 | +0.183 | -0.574 |
| true | balance_fade | ny | 64 | 20 | 0 | +0.025 | -0.678 |
| true | balance_fade | asia | 64 | 30 | 0 | +0.141 | -0.532 |
| true | balance_fade | london | 64 | 20 | 0 | +0.286 | -0.429 |
| true | imb_break | all | 64 | 40 | 0 | +0.070 | -0.582 |
| true | imb_break | ny | 64 | 16 | 0 | +0.261 | -0.442 |
| true | imb_break | asia | 64 | 0 | 0 | - | - |
| true | imb_break | london | 64 | 0 | 0 | - | - |
| true | combined | all | 64 | 60 | 0 | +0.134 | -0.539 |
| true | combined | ny | 64 | 40 | 0 | +0.144 | -0.554 |
| true | combined | asia | 64 | 36 | 0 | +0.099 | -0.576 |
| true | combined | london | 64 | 36 | 0 | +0.202 | -0.542 |
| proxy | balance_fade | all | 32 | 24 | 0 | +0.116 | -0.690 |
| proxy | balance_fade | ny | 32 | 10 | 0 | -0.022 | -0.710 |
| proxy | balance_fade | asia | 32 | 14 | 0 | -0.022 | -0.781 |
| proxy | balance_fade | london | 32 | 12 | 0 | +0.097 | -0.623 |
| proxy | imb_break | all | 32 | 16 | 0 | +0.191 | -0.524 |
| proxy | imb_break | ny | 32 | 8 | 0 | +0.333 | -0.389 |
| proxy | imb_break | asia | 32 | 0 | 0 | - | - |
| proxy | imb_break | london | 32 | 0 | 0 | - | - |
| proxy | combined | all | 32 | 28 | 0 | +0.109 | -0.772 |
| proxy | combined | ny | 32 | 18 | 0 | +0.185 | -0.495 |
| proxy | combined | asia | 32 | 20 | 0 | +0.032 | -0.715 |
| proxy | combined | london | 32 | 14 | 0 | +0.030 | -0.688 |

## Kline proxy vs true order flow

| Test | Method | Verdict |
|---|---|---|
| FABIO_L1 (kline proxy, 2022-2026, 5m/15m/1h) | every trigger fire, fixed-horizon close-to-close, fees 0.10% RT | no edge in all 6 cvd_absorption / escalation cells (best: escalation 1h +0.113% net, PBO 0.76); FVG = random control |
| This report, proxy control (same conditional model, uniform-spread profile, no big-trade filter), 90 days | conditional model, R multiples | 0 of 32 variants net-positive OOS with n >= 30 in any model/scope; combined all-sessions median net -0.77R |
| This report, true order flow (footprint profile + big-trade confirmation), 90 days | conditional model, R multiples | 0 of 64 variants net-positive OOS with n >= 30 in any model/scope; combined all-sessions median net -0.54R |

## Findings
- **Net of fees nothing survives.** Every variant with OOS n >= 30, in every model and session scope, has negative net
  expectancy for both true flow and proxy. No cell qualifies as "edge"; cells with n < 30 are "insufficient n". The only
  positive net cells (NY balance-fade proxy +0.07R n=16; NY combined proxy +0.04R n=11) are far below n = 30 and IS was
  negative: noise.
- **The gross signal is faintly positive; fee drag is the story.** Median OOS avg gross R across variants is +0.13R (combined,
  all sessions, true flow; +0.14R NY) but the median fee drag (gross minus net) is ~0.66R (range 0.43-2.4R): the spec's stops (1 tick
  beyond a 5m/15m bar extreme) are 0.05-0.2% of price versus 0.10% round-trip taker fees. The widened-stop variants (0.15%)
  are what IS selects, and they still lose. Even maker-in/maker-out (0.04% RT) would cost ~0.2-0.3R, above the gross edge
  seen; not simulated as a headline because stop exits are taker.
- **Shape matches the description** (low win rate, BE scratches): chosen variants win 16-45%, BE-scratch share 10-30%, but PF
  0.3-1.1 (best NY combined 15m true flow PF 0.90 at OOS n=16).
- **True order flow vs proxy:** no demonstrated improvement from big-trade confirmation and the real footprint profile; both are
  negative and n is too small (and the regime single) to say either way.
- **NY (US open) separately:** least-bad scope (median gross +0.14R combined, +0.26R imbalance-break); combined NY 15m limit trail:
  win 44%, PF 0.90, net -0.05R, but OOS n = 16 (insufficient); NY imbalance-break n=31 has PBO 0.70 and -0.27R.
- Not tested: discretionary judgement, order-book/L2 rules (34 of 97 rulebook rows need L2: reload, heat map, walls), the first
  15 minutes of each session (state window), other assets/regimes. Tom-with-Fabio agreement not computed (no offline Tom
  detector on these bars); Fabio stays a separate layer and must not gate Tom.

## Recommendation
Keep Fabio context-only. If sampled, use NY combined 15m with the widened stop as a log-only forward test, expect fees to
dominate, and re-test on >= 6 months across regimes before any weight. The bar files (`F:\MTS\data\orderflow_1m`, csv.gz,
`_progress.log`) can be extended backwards with `orderflow_bars.py --start ... --end ...`.
