# Shape B counts (DEV 2022-01-01..2024-06-30, no returns)

15m bars 96384 (warm-up from 2021-10-01). Overlap (one trade at a time) NOT removed in this table.

| stage | n |
|---|---|
| 0 C30 H2 trigger | 42 |
| 1 4h ADX>=20 & DI+>DI- | 22 |
| 2 ADX 5-bar slope>=0 | 13 |
| 3 phase not BEAR/PEAK_WINDOW | 9 |
| 4 low in [VAL, POC] | 2 |
| 5 maker fill within 3 bars | 2 |

By phase (cell = triggers that reached that stage):

| phase | s0 | s1 | s2 | s3 | s4 | s5 |
|---|---|---|---|---|---|---|
| ACCUMULATION | 19 | 10 | 5 | 5 | 1 | 1 |
| BEAR | 11 | 4 | 4 | 0 | 0 | 0 |
| BOTTOM_WINDOW | 7 | 5 | 2 | 2 | 0 | 0 |
| TRANSITION | 5 | 3 | 2 | 2 | 1 | 1 |

By ADX state (cell = triggers that reached that stage):

| ADX state | s0 | s1 | s2 | s3 | s4 | s5 |
|---|---|---|---|---|---|---|
| ADX<20 | 6 | 0 | 0 | 0 | 0 | 0 |
| ADX>=20 DI+>DI- | 22 | 22 | 13 | 9 | 2 | 2 |
| ADX>=20 DI- | 14 | 0 | 0 | 0 | 0 | 0 |

By session block (UTC) (cell = triggers that reached that stage):

| session block (UTC) | s0 | s1 | s2 | s3 | s4 | s5 |
|---|---|---|---|---|---|---|
| asia | 7 | 2 | 2 | 1 | 0 | 0 |
| london | 7 | 4 | 1 | 1 | 1 | 1 |
| ny | 23 | 13 | 8 | 6 | 1 | 1 |
| late | 5 | 3 | 2 | 1 | 0 | 0 |

Regime mix: PHASE_LABEL days of DEV = {'ACCUMULATION': 291, 'BEAR': 311, 'BOTTOM_WINDOW': 44, 'BULL': 72, 'TRANSITION': 194} (research_kit.regime_tag not used).
ADX >= 20 share of 4h bars in DEV: 3967/5472 = 72.5 %.

Final n (after maker fill) = 2; gate n >= 30.
