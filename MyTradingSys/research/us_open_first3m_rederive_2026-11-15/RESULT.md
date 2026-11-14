# US open first 3 minutes, CONT / FADE, 10 symbols, fee-net (rederive 2026-11-15)

Verdict: **NO EDGE**. Cost 14 bp round trip (research_kit.TAKER_RT_PCT). VALIDATION = 2024-01-01 .. 2026-11-12, DEV = 2021-2023 (descriptive). Rules: PRE_REG.md.

Regime mix: VAL events bull 62% / bear 38% / na 0%; DEV bull 51% / bear 49% / na 0% (BTC close vs SMA200, split reported not gated).

n events per symbol: BTC 1529, ETH 1529, SOL 1492, BNB 1450, XRP 1479, DOGE 1496, ADA 1463, AVAX 1432, LINK 1449, LTC 1477; skipped (gaps): BTC 1, ETH 1, SOL 1, BNB 1, XRP 1, DOGE 1, ADA 1, AVAX 1, LINK 1, LTC 1

| side | min | filter | n DEV | DEV net bp | n VAL | gross bp | net bp | lo95 | win | syms+ | drop5 | Holm p | bull / bear net | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CONT | 27 | all | 7487 | -11.77 | 7309 | -0.96 | -14.96 | -20.22 | 39.6% | 0 | -17.39 | 1.000 | bull n4537 -15.3 / bear n2772 -14.3 | FAIL |
| CONT | 27 | big | 1882 | -2.26 | 1782 | 7.62 | -6.38 | -19.68 | 41.9% | 1 | -15.06 | 1.000 | bull n1155 -14.2 / bear n627 8.0 | FAIL |
| CONT | 57 | all | 7487 | -17.25 | 7309 | 1.52 | -12.48 | -19.99 | 42.8% | 0 | -15.61 | 1.000 | bull n4537 -12.0 / bear n2772 -13.2 | FAIL |
| CONT | 57 | big | 1882 | -18.49 | 1782 | 12.81 | -1.19 | -18.82 | 44.7% | 5 | -13.62 | 1.000 | bull n1155 -7.2 / bear n627 9.9 | FAIL |
| FADE | 27 | all | 7487 | -16.23 | 7309 | 0.96 | -13.04 | -18.31 | 41.3% | 0 | -15.11 | 1.000 | bull n4537 -12.7 / bear n2772 -13.7 | FAIL |
| FADE | 27 | big | 1882 | -25.74 | 1782 | -7.62 | -21.62 | -34.93 | 41.1% | 0 | -28.04 | 1.000 | bull n1155 -13.8 / bear n627 -36.0 | FAIL |
| FADE | 57 | all | 7487 | -10.75 | 7309 | -1.52 | -15.52 | -23.03 | 44.1% | 0 | -18.51 | 1.000 | bull n4537 -16.0 / bear n2772 -14.8 | FAIL |
| FADE | 57 | big | 1882 | -9.51 | 1782 | -12.81 | -26.81 | -44.45 | 45.5% | 0 | -33.59 | 1.000 | bull n1155 -20.8 / bear n627 -37.9 | FAIL |

Big cut (|m3| DEV p75, frozen): BTC 0.223%, ETH 0.279%, SOL 0.405%, BNB 0.265%, XRP 0.298%, DOGE 0.351%, ADA 0.324%, AVAX 0.443%, LINK 0.374%, LTC 0.300%
