# F3 RESULT: phase-matched nearest-neighbour analog forecast, 1h BTC, DEV 2022-01-01..2025-06-30

Pre-reg: f3/PRE_REG.md (committed before the run). Run: `python MyTradingSys/research/fractals_2026-10-31/f3/run_f3.py` (10m52s; output f3/output.md). HOLDOUT 2025-07+ never loaded.
1,190 non-overlapping 24-bar queries (split A/B = 595/595 at 2023-11-13); k = 10, agreement >= 70 %, all-taker round trip 0.10 %.

**Verdict: no edge. UNFILT INCONCLUSIVE, PHASE INCONCLUSIVE (frozen rule); both below both controls (p 0.80-0.92).** Honest negative.

| variant | forecasts (A/B) | trades | hit | net %/trade | R/trade | week-boot 95% CI | RW surrogate mean [2.5,97.5] (p) | SHUF mean [2.5,97.5] (p) | meanA / meanB |
|---|---|---|---|---|---|---|---|---|---|
| UNFILT | 1190 (595/595) | 368 | 0.473 | -0.216 | -0.092 | [-0.505, +0.080] | -0.094 [-0.335, +0.166] (0.80) | -0.085 [-0.307, +0.174] (0.84) | -0.507 / +0.069 |
| PHASE (cowen_side x sma200_side) | 1100 (535/565) | 359 | 0.474 | -0.277 | -0.135 | [-0.566, +0.032] | -0.095 [-0.352, +0.214] (0.90) | -0.089 [-0.363, +0.201] (0.92) | -0.360 / -0.204 |

- Holm-adjusted p (4 tests) = 1.00 everywhere. Horizon: H = 24 only, so Holm over horizons has one member.
- Controls average about -0.09 %: a random-direction trade pays the 0.10 % round trip; the analog forecast is no better (hit 47 % vs 50 %), if anything slightly worse.
- Phase filter minus unfiltered: -0.061 %/trade, week-block CI [-0.371, +0.234]. The phase tag does not help; it halves the usable library and adds nothing.
- Split A -0.51 vs B +0.07 (unfiltered) is the sign of noise, not an edge: per-trade sd is 2.7 %, a 0.10 % effect needs about 5,900 trades (harness.power_n) and this study has 368. Even the positive half is far inside the surrogate range.
- Decision rule outcome: the CI upper bounds straddle zero, so FAIL (upper < 0) is not triggered; the study is underpowered to prove a fee-sized negative, but it gives no support for a positive one. No rule, gate or layer is added.

Caveats: single k, agreement fraction, L, H (no tuning, by design). Library is expanding from ~83 days, so early queries see a small library. R is a vol-normalised OURS unit.
