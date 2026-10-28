VERDICT: INCONCLUSIVE

Study wlow_bounce_bbrsi60_2026-10-16, DEV only (1h bars from 1m klines, open < 2024-07-01). Rules: PRE_REG.md (committed before this file). Why: n=8 < 10 events on DEV.
Primary cell: V1 (ISO prior-week low, K=4), LONG, h=4 h, cost C=0.14 %. Events with full 24 h forward window: n=8 (triggers before forward-window filter: 8).

## Primary table (R4 = % return, entry open[t+1], exit close[t+4]; day-clustered SE)
| group | n | mean R4 % | SE | net long (R4-C) | net short (-R4-C) |
|---|---|---|---|---|---|
| EVENT (break+bounce+hold) | 8 | -0.293 | 0.116 | -0.433 | 0.153 |
| BASELINE a (hold, no weekly break) | 88 | 0.003 | 0.086 | -0.137 | -0.143 |
| BASELINE b (same hour-of-day) | 160 | 0.020 | 0.114 | -0.120 | -0.160 |

DIFF vs baseline a: -0.296 % SE 0.145 t -2.05 95% CI [-0.580, -0.013] MDE80 0.405 %
DIFF vs baseline b: -0.314 % SE 0.163 t -1.93 95% CI [-0.633, 0.006] MDE80 0.456 %

## Horizons, MFE/MAE, first touch (events | baseline a)
| h | event mean % | event SE | event net long | event net short | base-a mean % | base-b mean % |
|---|---|---|---|---|---|---|
| 1 | 0.017 | 0.036 | -0.123 | -0.157 | -0.013 | 0.018 |
| 4 | -0.293 | 0.116 | -0.433 | 0.153 | 0.003 | 0.020 |
| 12 | -0.093 | 0.419 | -0.233 | -0.047 | -0.083 | -0.113 |
| 24 | 0.710 | 0.475 | 0.570 | -0.850 | 0.210 | -0.058 |
- event: mean MFE 1.464 %, mean MAE -1.618 %; first +-1 % within 24 h: up 2, dn 4, both-in-one-minute 0, none 2 (n=8)
- base-a: mean MFE 1.623 %, mean MAE -1.450 %; first +-1 % within 24 h: up 35, dn 37, both-in-one-minute 0, none 16 (n=88)
- base-b: mean MFE 2.127 %, mean MAE -2.228 %; first +-1 % within 24 h: up 63, dn 78, both-in-one-minute 0, none 19 (n=160)

## Event list (UTC; break bar open, bounce bar open, trigger bar open, prior weekly low)
- 2022-02-14T01:00Z | 2022-02-14T01:00Z | 2022-02-14T15:00Z | W=41540.0
- 2022-05-27T15:00Z | 2022-05-27T15:00Z | 2022-05-28T15:00Z | W=28629.6
- 2022-10-12T12:00Z | 2022-10-12T12:00Z | 2022-10-12T22:00Z | W=18950.8
- 2023-05-25T13:00Z | 2023-05-25T14:00Z | 2023-05-25T22:00Z | W=26335.3
- 2023-06-08T16:00Z | 2023-06-08T16:00Z | 2023-06-08T21:00Z | W=26477.6
- 2023-07-18T18:00Z | 2023-07-18T18:00Z | 2023-07-19T03:00Z | W=29876.6
- 2023-07-28T14:00Z | 2023-07-28T14:00Z | 2023-07-29T04:00Z | W=29400.0
- 2023-09-25T00:00Z | 2023-09-25T00:00Z | 2023-09-25T19:00Z | W=26081.0

## Variants (secondary, no verdict; each is a ledger row)
| variant | events | baseline a n | event mean R4 % | base-a mean R4 % | DIFF | t_DIFF | MDE80 |
|---|---|---|---|---|---|---|---|
| V1_primary | 8 | 88 | -0.293 | 0.003 | -0.296 | -2.05 | 0.405 |
| V2_roll168 | 6 | 109 | -0.546 | 0.093 | -0.639 | -2.43 | 0.736 |
| V3_K3 | 14 | 151 | 0.137 | 0.009 | 0.128 | 0.45 | 0.801 |
| V4_K6 | 4 | 26 | -0.385 | 0.009 | -0.394 | -2.41 | 0.458 |

## Conditioning layers on the V1 events (one at a time; each split side next to the base; NOT_EVALUATED if a side has n < 10)
- L1 open interest: NOT_IN_DATA for DEV (Binance metrics archive starts 2025-09-01). Live-tracking field only.
| layer / split | side | n | mean R4 % | net long | net short | DIFF vs other side | t |
|---|---|---|---|---|---|---|---|
| BASE | all | 8 | -0.293 | -0.433 | 0.153 | - | - |
| L2 CVD change (break->trigger), sign NOT_EVALUATED | up (>0) | 7 | -0.297 | -0.437 | 0.157 | nan | nan |
| L2 CVD change (break->trigger), sign NOT_EVALUATED | down (<=0) | 1 | -0.265 | -0.405 | 0.125 | nan | nan |
| L2 CVD change (break->trigger), median NOT_EVALUATED | high (>median) | 4 | -0.402 | -0.542 | 0.262 | -0.217 | -0.99 |
| L2 CVD change (break->trigger), median NOT_EVALUATED | low (<=median) | 4 | -0.185 | -0.325 | 0.045 | -0.217 | -0.99 |
| L3 net delta (hold window), sign NOT_EVALUATED | up (>0) | 8 | -0.293 | -0.433 | 0.153 | nan | nan |
| L3 net delta (hold window), sign NOT_EVALUATED | down (<=0) | 0 | nan | nan | nan | nan | nan |
| L3 net delta (hold window), median NOT_EVALUATED | high (>median) | 4 | -0.372 | -0.512 | 0.232 | -0.158 | -0.70 |
| L3 net delta (hold window), median NOT_EVALUATED | low (<=median) | 4 | -0.214 | -0.354 | 0.074 | -0.158 | -0.70 |

Layer rule (PRE_REG): no combined stack; a layer matters only if its own side passes the primary bar (n>=30, DIFF vs baseline a CI above 0, fee-net > 0). The base verdict above does not depend on the layers.

## Reading (added after the run; changes no verdict or bar)
- Verdict INCONCLUSIVE is mechanical: n=8 < 10. The nominal DIFF of -0.30 % (4 h, events lower than baseline a) points toward "fails back down" and the short-net readout is +0.15 % at the 4 h cell, but with 8 events (7 distinct weeks, SE uses day clusters) a t of -2.05 is not evidence: MDE80 0.41 % at n=8, and 24 h returns flip sign (+0.71 %). Do not trade it. DECISION (OURS): the short side is a hypothesis for a new PRE_REG, not a finding.
- Sample needed for a decision at MDE80 <= 0.28 % (2C): about 130 events per group; DEV yields about 3 per year. Forward live sampling (status CLI + shadow emitter card) and a looser pre-registered definition on VALIDATION-era data are the only routes; neither is run here.
- Layers: every split has a side with n < 10, so all NOT_EVALUATED. OI is NOT_IN_DATA on DEV (archive from 2025-09-01).

## Promotion check (draft manifest, NOT registered)
`promote.py check candidate_manifest.draft.json` on 2026-10-16: REJECT. Reasons: validation_reads and holdout_reads missing; screen verdict INCONCLUSIVE (need PASS); no BT-TUNED backtest report; fee-net OOS net R 0, CI low 0, n_trades 0 < 30. The PRE_REG-before-verdict date gate and the trial-ledger row count (8) did not raise a reason.

## Live tracking (observation only)
`python -m MyTradingSys.backtest.layers.wlow_bounce.status` on 2026-10-16 read ACTIVE for the 2026-10-15 shape (closed 1h bar 19:00Z: RSI14 56.7, close 0.47 % under the upper BB, prior weekly low 80344.8, OI 93.66K coins). It is a detector reading, not a validated signal.
