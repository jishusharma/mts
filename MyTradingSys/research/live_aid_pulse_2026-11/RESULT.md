# RESULT: Live Aid pulse SETUP FORMING vs matched null, DEV only, BTCUSDT perp 1m, fee-net 14 bp (one run per PRE_REG.md)

**Verdict: FAIL. The SETUP FORMING flag is a coin flip beyond being near a level: at 30 min, n = 10093, gross -0.1 bp [-0.7, 0.6], fee-net -14.1 bp [-14.7, -13.4]; the flag minus the near-level null is 0.0 bp [-0.7, 0.7].** FAIL means stop: no coaching claim from the SETUP FORMING flag on BTC perp 1m-4h with these thresholds; a threshold tune needs its own PRE_REG and the VALIDATION read.

Regime mix: window 2022-02-01..2024-06-30, 881 UTC days: bull 261 (29.6 %), bear 185 (21.0 %), range 435 (49.4 %); signals: bull 2889, bear 1866, range 5338 (trailing 30-day close return, +-10 %).

Split: DEV only; VALIDATION (2024-07 onward) and HOLDOUT never opened (loader opens files up to 2024-06 and asserts every bar is before 2024-07-01). Tape: Binance USD-M perp 1m (proxy for the page's spot feed). Decisions every 5 min; entry open of next 1m bar + 1 bar; cost 14 bp (10 fee + 4 slippage); CI = 95 % day-clustered bootstrap (4000 draws, seed 7). Raw setups 52087, signals after the 60-min same-side cooldown 10093, missing-bar drops 0.

## Verdict arms
| arm | n | mean | SE | cost | verdict |
|---|---|---|---|---|---|
| pulse SETUP FORMING minus near-level null, h30, all sessions | 10093 | 0.0002 | 0.0036 | 0.14 | FAIL |

mean and SE in percent of notional (signal gross minus null gross); t = 0.06. Net of 14 bp the signal itself loses 14.1 bp.

## Horizon 15 min, by session (bp; CI 95 %, day-clustered)
| scope | n | gross | net 14 bp | signal - near-level null | signal - random-time null | signal - lean-only null | short share |
|---|---|---|---|---|---|---|---|
| ALL | 10093 | -0.4 [-0.9, 0.1] | -14.4 [-14.9, -13.9] | -0.3 [-0.8, 0.1] | -0.4 [-0.9, 0.1] | -0.4 [-1.0, 0.2] | 0.57 |
| Asia | 3423 | -0.7 [-1.4, 0.1] | -14.7 [-15.4, -13.9] | -0.6 [-1.4, 0.1] | -0.7 [-1.4, 0.1] | 0.1 [-0.8, 0.9] | 0.57 |
| Europe | 2204 | -0.5 [-1.6, 0.6] | -14.5 [-15.6, -13.4] | -0.5 [-1.5, 0.6] | -0.4 [-1.5, 0.6] | -0.4 [-1.6, 0.8] | 0.58 |
| US | 3365 | -0.2 [-1.3, 0.8] | -14.2 [-15.3, -13.2] | -0.2 [-1.3, 0.8] | -0.3 [-1.3, 0.8] | -0.8 [-2.1, 0.4] | 0.57 |
| Late | 1101 | 0.4 [-1.1, 1.8] | -13.6 [-15.1, -12.2] | 0.4 [-1.0, 1.9] | 0.5 [-1.0, 1.9] | -0.2 [-1.8, 1.4] | 0.58 |

### Horizon 15 min, by regime
| regime | n | gross | net 14 bp | signal - near-level null | signal - lean-only null |
|---|---|---|---|---|---|
| bull | 2889 | -0.4 [-1.4, 0.6] | -14.4 [-15.4, -13.4] | -0.1 [-1.1, 0.9] | -0.8 [-2.0, 0.5] |
| bear | 1866 | -0.2 [-1.7, 1.3] | -14.2 [-15.7, -12.7] | -0.2 [-1.6, 1.3] | 0.8 [-0.8, 2.4] |
| range | 5338 | -0.4 [-1.0, 0.2] | -14.4 [-15.0, -13.8] | -0.4 [-1.0, 0.2] | -0.6 [-1.3, 0.1] |

## Horizon 30 min, by session (bp; CI 95 %, day-clustered)
| scope | n | gross | net 14 bp | signal - near-level null | signal - random-time null | signal - lean-only null | short share |
|---|---|---|---|---|---|---|---|
| ALL | 10093 | -0.1 [-0.7, 0.6] | -14.1 [-14.7, -13.4] | 0.0 [-0.7, 0.7] | -0.0 [-0.7, 0.7] | -0.2 [-1.1, 0.6] | 0.57 |
| Asia | 3423 | -0.8 [-1.8, 0.2] | -14.8 [-15.8, -13.8] | -0.7 [-1.7, 0.4] | -0.8 [-1.8, 0.2] | 0.0 [-1.2, 1.2] | 0.57 |
| Europe | 2204 | 0.4 [-0.9, 1.8] | -13.6 [-14.9, -12.2] | 0.5 [-0.8, 1.9] | 0.5 [-0.8, 1.9] | 0.8 [-0.8, 2.3] | 0.58 |
| US | 3365 | 0.2 [-1.3, 1.6] | -13.8 [-15.3, -12.4] | 0.2 [-1.3, 1.6] | 0.1 [-1.3, 1.6] | -1.1 [-2.8, 0.6] | 0.57 |
| Late | 1101 | 0.7 [-1.1, 2.4] | -13.3 [-15.1, -11.6] | 0.8 [-1.1, 2.5] | 0.8 [-1.0, 2.5] | -0.2 [-2.6, 2.0] | 0.58 |

### Horizon 30 min, by regime
| regime | n | gross | net 14 bp | signal - near-level null | signal - lean-only null |
|---|---|---|---|---|---|
| bull | 2889 | -0.1 [-1.5, 1.2] | -14.1 [-15.5, -12.8] | 0.5 [-0.9, 2.0] | -1.0 [-2.8, 0.7] |
| bear | 1866 | -0.6 [-2.7, 1.6] | -14.6 [-16.7, -12.4] | -0.6 [-2.7, 1.6] | 1.0 [-1.2, 3.4] |
| range | 5338 | 0.2 [-0.6, 0.9] | -13.8 [-14.6, -13.1] | 0.2 [-0.6, 1.0] | -0.2 [-1.3, 0.8] |

## Horizon 60 min, by session (bp; CI 95 %, day-clustered)
| scope | n | gross | net 14 bp | signal - near-level null | signal - random-time null | signal - lean-only null | short share |
|---|---|---|---|---|---|---|---|
| ALL | 10093 | 0.7 [-0.2, 1.7] | -13.3 [-14.2, -12.3] | 0.9 [-0.1, 1.9] | 0.8 [-0.2, 1.8] | 0.4 [-0.8, 1.6] | 0.57 |
| Asia | 3423 | -0.1 [-1.6, 1.5] | -14.1 [-15.6, -12.5] | 0.1 [-1.4, 1.6] | -0.1 [-1.6, 1.5] | 0.9 [-0.9, 2.6] | 0.57 |
| Europe | 2204 | 1.6 [-0.3, 3.6] | -12.4 [-14.3, -10.4] | 1.8 [-0.2, 3.8] | 1.7 [-0.2, 3.7] | 1.6 [-0.7, 3.8] | 0.58 |
| US | 3365 | 1.1 [-0.8, 3.1] | -12.9 [-14.8, -10.9] | 1.1 [-0.7, 3.1] | 1.1 [-0.8, 3.1] | -0.2 [-2.6, 2.4] | 0.57 |
| Late | 1101 | 0.5 [-2.1, 3.1] | -13.5 [-16.1, -10.9] | 0.8 [-1.8, 3.3] | 0.8 [-1.8, 3.3] | -1.9 [-5.3, 1.2] | 0.58 |

### Horizon 60 min, by regime
| regime | n | gross | net 14 bp | signal - near-level null | signal - lean-only null |
|---|---|---|---|---|---|
| bull | 2889 | 0.0 [-1.8, 1.9] | -14.0 [-15.8, -12.1] | 1.3 [-0.7, 3.2] | -1.1 [-3.3, 1.0] |
| bear | 1866 | 1.2 [-1.5, 4.1] | -12.8 [-15.5, -9.9] | 1.3 [-1.4, 4.2] | 3.4 [0.3, 6.7] |
| range | 5338 | 1.0 [-0.3, 2.2] | -13.0 [-14.3, -11.8] | 1.0 [-0.2, 2.3] | 0.1 [-1.5, 1.7] |

## Reading
- No horizon, session or regime cell has a fee-net mean above zero; the best net is about -12 bp, the cost alone is 14 bp. The pooled gross effect is within about +-1 bp of zero at 15 and 30 min and +0.7 bp [-0.2, 1.7] at 60 min.
- Against the near-level null (the PRE_REG primary control) every CI contains 0 at 15 and 30 min; at 60 min the pooled difference is +0.9 bp [-0.1, 1.9], Europe +1.8 bp [-0.2, 3.8]. Neither passes the PRE_REG rule (PASS_GROSS_ONLY needs a CI wholly above 0 at the primary 30 min cell).
- One secondary cell has a CI above zero: 60 min, bear regime, signal minus lean-only null +3.4 bp [0.3, 6.7]. It is one of about 70 secondary contrasts printed here (24 cells x 3 nulls) (Holm family m = 236 on DEV) and does not survive that correction; it is a lead for a PRE_REG, never a finding.
- 57 % of signals are SHORT (lean down plus a bearish divergence is found more often than the mirror); the SHORT/LONG mix is copied into the null, so it does not bias the contrast.
- The flag fires at 62 % of the 5-min decision times that are near a level (52087 of 84348): it is not selective, so a coin flip on it is what the operator should expect from the coaching.
- Divergence adds nothing measurable over the lean alone (signal minus lean-only null: all pooled CIs contain 0).

## Caveats (not hidden)
- Perp tape, not spot; CVD is perp taker flow. Only part of the page's level ladder exists historically (PDH/PDL/PDC, DO, WO, PWH/PWL, Asia high/low); analyst, VAL/POC/VAH, MA-strip and VWAP levels and the Home direction are NOT_IN_DATA, so the page may flag places this study never tested.
- Events overlap (5-min cadence, several levels, 60-min cooldown per side only); n overstates independent samples, which is why the CIs are day-clustered.
- Thresholds P stay OURS; nothing here tunes them. No VALIDATION read, no trade claim.
