# prereg_gate.py output, 2026-11-04, long window (before any return; n = distinct days of aligned W12 signal events, m = 48, cost 0.14, unit %)

| Regime | TF | n days | sd (%) | MDE + cost | max plausible | n needed | gate |
|---|---|---|---|---|---|---|---|
| primary bull | 15m | 282 | 0.8 | 0.336 | 0.30 | 424 | BLOCK |
| primary bull | 1h | 94 | 1.9 | 0.947 | 0.30 | 2393 | BLOCK |
| primary bull | 4h | 34 | 4.0 | 2.966 | 0.30 | 10604 | BLOCK |
| primary bull | 1d | 1 | 10 | 41.330 | 0.30 | 66275 | BLOCK |
| P40 bear | 15m | 236 | 0.8 | 0.355 | 0.30 | 424 | BLOCK |
| P40 bear | 1h | 77 | 1.9 | 1.032 | 0.30 | 2393 | BLOCK |
| P40 bear | 4h | 25 | 4.0 | 3.435 | 0.30 | 10604 | BLOCK |
| P40 bear | 1d | 2 | 10 | 29.266 | 0.30 | 66275 | BLOCK |
| primary bear | all | 0 | - | - | - | - | EMPTY (0 bear weeks) |

Reading: the long window moves 15m from 96 to 282 days but still short of 424. DEV table is descriptive; verdict ceiling INCONCLUSIVE.
