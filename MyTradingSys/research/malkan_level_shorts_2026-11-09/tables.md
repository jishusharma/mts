Data: BTCUSDT spot 4h, 2017-08-17 04:00:00 .. 2024-06-30 20:00:00 UTC, 15043 bars, 8 gaps (a gap resets WaveTrend). Sealed: VALIDATION 2024-07..2025-06 and HOLDOUT 2025-07.. not read.

Regime mix: bull 45.7% / bear 38.3% / range 8.1% of 4h bars (daily close vs 200d SMA +-5%); 7.9% warm-up (NOT_IN_DATA).

## Arm summary

| arm (div / basis / trigger) | L1-3 chains | +L4 | +L5 = firings | too tight | non-overlap trades | hit >=1R | target 1R hit | net R/trade 1R exit | CI | net R/trade 2R exit | CI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window 3-10 / close / cross | 163 | 76 | 17 | 0 | 17 | 64.7% | 64.7% | +0.245 | 0.47 | +0.081 | 0.69 |
| window 3-10 / close / cross+RSI<60 | 94 | 36 | 10 | 0 | 10 | 50.0% | 50.0% | -0.051 | 0.66 | -0.328 | 0.79 |
| window 3-10 / wick / cross | 168 | 75 | 15 | 0 | 15 | 66.7% | 66.7% | +0.285 | 0.50 | +0.034 | 0.73 |
| window 3-10 / wick / cross+RSI<60 | 100 | 37 | 9 | 0 | 9 | 55.6% | 55.6% | +0.061 | 0.70 | -0.247 | 0.86 |
| swing-swing / close / cross | 163 | 76 | 16 | 0 | 16 | 62.5% | 62.5% | +0.201 | 0.49 | -0.035 | 0.70 |
| swing-swing / close / cross+RSI<60 | 94 | 37 | 10 | 0 | 10 | 50.0% | 50.0% | -0.051 | 0.66 | -0.328 | 0.79 |
| swing-swing / wick / cross | 159 | 71 | 14 | 0 | 14 | 64.3% | 64.3% | +0.237 | 0.53 | +0.110 | 0.77 |
| swing-swing / wick / cross+RSI<60 | 96 | 36 | 9 | 0 | 9 | 55.6% | 55.6% | +0.061 | 0.70 | -0.247 | 0.86 |

## Per-arm detail

### Arm: window 3-10 / close / cross

Ladder (non-overlapping trades within each tier, 1R exit, fee-net 0.04%/side):

| tier | trades | hit >=1R | target 1R hit | net R/trade | CI |
|---|---|---|---|---|---|
| L1-3 | 145 | 43.4% | 43.4% | -0.145 | +-0.16 |
| L1-4 | 72 | 43.1% | 43.1% | -0.148 | +-0.23 |
| L1-5 (firings) | 17 | 64.7% | 64.7% | +0.245 | +-0.47 |

Firings by regime, 1R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 10 | 80.0% | 80.0% | +0.558 | +-0.53 |
| bear | 6 | 50.0% | 50.0% | -0.060 | +-0.88 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 1R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 1 | 100.0% | 100.0% | +0.968 | +- |
| 2020 | 1 | 0.0% | 0.0% | -1.058 | +- |
| 2021 | 3 | 66.7% | 66.7% | +0.295 | +-1.31 |
| 2022 | 3 | 66.7% | 66.7% | +0.284 | +-1.28 |
| 2023 | 6 | 50.0% | 50.0% | -0.053 | +-0.90 |
| 2024 | 3 | 100.0% | 100.0% | +0.942 | +-0.02 |

Firings by regime, 2R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 10 | 80.0% | 40.0% | +0.280 | +-0.93 |
| bear | 6 | 50.0% | 33.3% | -0.060 | +-1.25 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 2R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 1 | 100.0% | 100.0% | +1.968 | +- |
| 2020 | 1 | 0.0% | 0.0% | -1.058 | +- |
| 2021 | 3 | 66.7% | 33.3% | -0.038 | +-1.96 |
| 2022 | 3 | 66.7% | 33.3% | -0.050 | +-1.95 |
| 2023 | 6 | 50.0% | 33.3% | +0.152 | +-1.20 |
| 2024 | 3 | 100.0% | 33.3% | -0.058 | +-1.94 |

Firings (all, overlapping allowed): 17; kind: 12 sweep / 5 div.

### Arm: window 3-10 / close / cross+RSI<60

Ladder (non-overlapping trades within each tier, 1R exit, fee-net 0.04%/side):

| tier | trades | hit >=1R | target 1R hit | net R/trade | CI |
|---|---|---|---|---|---|
| L1-3 | 87 | 47.1% | 47.1% | -0.068 | +-0.21 |
| L1-4 | 36 | 44.4% | 44.4% | -0.091 | +-0.32 |
| L1-5 (firings) | 10 | 50.0% | 50.0% | -0.051 | +-0.66 |

Firings by regime, 1R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 5 | 80.0% | 80.0% | +0.564 | +-0.79 |
| bear | 4 | 25.0% | 25.0% | -0.567 | +-0.98 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 1R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 0 | | | | |
| 2020 | 1 | 0.0% | 0.0% | -1.058 | +- |
| 2021 | 1 | 100.0% | 100.0% | +0.964 | +- |
| 2022 | 2 | 50.0% | 50.0% | -0.044 | +-1.91 |
| 2023 | 5 | 40.0% | 40.0% | -0.258 | +-0.99 |
| 2024 | 1 | 100.0% | 100.0% | +0.966 | +- |

Firings by regime, 2R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 5 | 80.0% | 40.0% | +0.410 | +-1.33 |
| bear | 4 | 25.0% | 0.0% | -1.067 | +-0.03 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 2R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 0 | | | | |
| 2020 | 1 | 0.0% | 0.0% | -1.058 | +- |
| 2021 | 1 | 100.0% | 100.0% | +1.964 | +- |
| 2022 | 2 | 50.0% | 0.0% | -1.044 | +-0.05 |
| 2023 | 5 | 40.0% | 20.0% | -0.213 | +-1.18 |
| 2024 | 1 | 100.0% | 0.0% | -1.035 | +- |

Firings (all, overlapping allowed): 10; kind: 9 sweep / 1 div.

### Arm: window 3-10 / wick / cross

Ladder (non-overlapping trades within each tier, 1R exit, fee-net 0.04%/side):

| tier | trades | hit >=1R | target 1R hit | net R/trade | CI |
|---|---|---|---|---|---|
| L1-3 | 152 | 42.1% | 42.1% | -0.173 | +-0.16 |
| L1-4 | 72 | 41.7% | 41.7% | -0.175 | +-0.23 |
| L1-5 (firings) | 15 | 66.7% | 66.7% | +0.285 | +-0.50 |

Firings by regime, 1R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 9 | 88.9% | 88.9% | +0.737 | +-0.44 |
| bear | 5 | 40.0% | 40.0% | -0.260 | +-0.97 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 1R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 1 | 100.0% | 100.0% | +0.968 | +- |
| 2020 | 0 | | | | |
| 2021 | 3 | 66.7% | 66.7% | +0.295 | +-1.31 |
| 2022 | 2 | 50.0% | 50.0% | -0.044 | +-1.91 |
| 2023 | 6 | 50.0% | 50.0% | -0.053 | +-0.90 |
| 2024 | 3 | 100.0% | 100.0% | +0.942 | +-0.02 |

Firings by regime, 2R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 9 | 88.9% | 44.4% | +0.429 | +-0.98 |
| bear | 5 | 40.0% | 20.0% | -0.460 | +-1.19 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 2R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 1 | 100.0% | 100.0% | +1.968 | +- |
| 2020 | 0 | | | | |
| 2021 | 3 | 66.7% | 33.3% | -0.038 | +-1.96 |
| 2022 | 2 | 50.0% | 0.0% | -1.044 | +-0.05 |
| 2023 | 6 | 50.0% | 33.3% | +0.152 | +-1.20 |
| 2024 | 3 | 100.0% | 33.3% | -0.058 | +-1.94 |

Firings (all, overlapping allowed): 15; kind: 13 sweep / 2 div.

### Arm: window 3-10 / wick / cross+RSI<60

Ladder (non-overlapping trades within each tier, 1R exit, fee-net 0.04%/side):

| tier | trades | hit >=1R | target 1R hit | net R/trade | CI |
|---|---|---|---|---|---|
| L1-3 | 94 | 45.7% | 45.7% | -0.097 | +-0.20 |
| L1-4 | 37 | 43.2% | 43.2% | -0.116 | +-0.32 |
| L1-5 (firings) | 9 | 55.6% | 55.6% | +0.061 | +-0.70 |

Firings by regime, 1R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 4 | 100.0% | 100.0% | +0.970 | +-0.01 |
| bear | 4 | 25.0% | 25.0% | -0.567 | +-0.98 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 1R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 0 | | | | |
| 2020 | 0 | | | | |
| 2021 | 1 | 100.0% | 100.0% | +0.964 | +- |
| 2022 | 2 | 50.0% | 50.0% | -0.044 | +-1.91 |
| 2023 | 5 | 40.0% | 40.0% | -0.258 | +-0.99 |
| 2024 | 1 | 100.0% | 100.0% | +0.966 | +- |

Firings by regime, 2R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 4 | 100.0% | 50.0% | +0.776 | +-1.44 |
| bear | 4 | 25.0% | 0.0% | -1.067 | +-0.03 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 2R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 0 | | | | |
| 2020 | 0 | | | | |
| 2021 | 1 | 100.0% | 100.0% | +1.964 | +- |
| 2022 | 2 | 50.0% | 0.0% | -1.044 | +-0.05 |
| 2023 | 5 | 40.0% | 20.0% | -0.213 | +-1.18 |
| 2024 | 1 | 100.0% | 0.0% | -1.035 | +- |

Firings (all, overlapping allowed): 9; kind: 9 sweep / 0 div.

### Arm: swing-swing / close / cross

Ladder (non-overlapping trades within each tier, 1R exit, fee-net 0.04%/side):

| tier | trades | hit >=1R | target 1R hit | net R/trade | CI |
|---|---|---|---|---|---|
| L1-3 | 146 | 43.2% | 43.2% | -0.151 | +-0.16 |
| L1-4 | 73 | 42.5% | 42.5% | -0.161 | +-0.23 |
| L1-5 (firings) | 16 | 62.5% | 62.5% | +0.201 | +-0.49 |

Firings by regime, 1R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 10 | 80.0% | 80.0% | +0.558 | +-0.53 |
| bear | 5 | 40.0% | 40.0% | -0.260 | +-0.97 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 1R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 1 | 100.0% | 100.0% | +0.968 | +- |
| 2020 | 1 | 0.0% | 0.0% | -1.058 | +- |
| 2021 | 3 | 66.7% | 66.7% | +0.295 | +-1.31 |
| 2022 | 2 | 50.0% | 50.0% | -0.044 | +-1.91 |
| 2023 | 6 | 50.0% | 50.0% | -0.053 | +-0.90 |
| 2024 | 3 | 100.0% | 100.0% | +0.942 | +-0.02 |

Firings by regime, 2R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 10 | 80.0% | 40.0% | +0.280 | +-0.93 |
| bear | 5 | 40.0% | 20.0% | -0.460 | +-1.19 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 2R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 1 | 100.0% | 100.0% | +1.968 | +- |
| 2020 | 1 | 0.0% | 0.0% | -1.058 | +- |
| 2021 | 3 | 66.7% | 33.3% | -0.039 | +-1.96 |
| 2022 | 2 | 50.0% | 0.0% | -1.044 | +-0.05 |
| 2023 | 6 | 50.0% | 33.3% | +0.152 | +-1.20 |
| 2024 | 3 | 100.0% | 33.3% | -0.058 | +-1.94 |

Firings (all, overlapping allowed): 16; kind: 11 sweep / 5 div.

### Arm: swing-swing / close / cross+RSI<60

Ladder (non-overlapping trades within each tier, 1R exit, fee-net 0.04%/side):

| tier | trades | hit >=1R | target 1R hit | net R/trade | CI |
|---|---|---|---|---|---|
| L1-3 | 88 | 46.6% | 46.6% | -0.079 | +-0.21 |
| L1-4 | 37 | 43.2% | 43.2% | -0.117 | +-0.32 |
| L1-5 (firings) | 10 | 50.0% | 50.0% | -0.051 | +-0.66 |

Firings by regime, 1R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 5 | 80.0% | 80.0% | +0.564 | +-0.79 |
| bear | 4 | 25.0% | 25.0% | -0.567 | +-0.98 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 1R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 0 | | | | |
| 2020 | 1 | 0.0% | 0.0% | -1.058 | +- |
| 2021 | 1 | 100.0% | 100.0% | +0.964 | +- |
| 2022 | 2 | 50.0% | 50.0% | -0.044 | +-1.91 |
| 2023 | 5 | 40.0% | 40.0% | -0.258 | +-0.99 |
| 2024 | 1 | 100.0% | 100.0% | +0.966 | +- |

Firings by regime, 2R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 5 | 80.0% | 40.0% | +0.410 | +-1.33 |
| bear | 4 | 25.0% | 0.0% | -1.067 | +-0.03 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 2R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 0 | | | | |
| 2020 | 1 | 0.0% | 0.0% | -1.058 | +- |
| 2021 | 1 | 100.0% | 100.0% | +1.964 | +- |
| 2022 | 2 | 50.0% | 0.0% | -1.044 | +-0.05 |
| 2023 | 5 | 40.0% | 20.0% | -0.213 | +-1.18 |
| 2024 | 1 | 100.0% | 0.0% | -1.035 | +- |

Firings (all, overlapping allowed): 10; kind: 8 sweep / 2 div.

### Arm: swing-swing / wick / cross

Ladder (non-overlapping trades within each tier, 1R exit, fee-net 0.04%/side):

| tier | trades | hit >=1R | target 1R hit | net R/trade | CI |
|---|---|---|---|---|---|
| L1-3 | 144 | 43.1% | 43.1% | -0.152 | +-0.16 |
| L1-4 | 68 | 42.6% | 42.6% | -0.154 | +-0.23 |
| L1-5 (firings) | 14 | 64.3% | 64.3% | +0.237 | +-0.53 |

Firings by regime, 1R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 8 | 87.5% | 87.5% | +0.709 | +-0.49 |
| bear | 5 | 40.0% | 40.0% | -0.260 | +-0.97 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 1R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 1 | 100.0% | 100.0% | +0.968 | +- |
| 2020 | 0 | | | | |
| 2021 | 2 | 50.0% | 50.0% | -0.040 | +-1.97 |
| 2022 | 2 | 50.0% | 50.0% | -0.044 | +-1.91 |
| 2023 | 6 | 50.0% | 50.0% | -0.053 | +-0.90 |
| 2024 | 3 | 100.0% | 100.0% | +0.942 | +-0.02 |

Firings by regime, 2R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 8 | 87.5% | 50.0% | +0.612 | +-1.04 |
| bear | 5 | 40.0% | 20.0% | -0.460 | +-1.19 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 2R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 1 | 100.0% | 100.0% | +1.968 | +- |
| 2020 | 0 | | | | |
| 2021 | 2 | 50.0% | 50.0% | +0.460 | +-2.95 |
| 2022 | 2 | 50.0% | 0.0% | -1.044 | +-0.05 |
| 2023 | 6 | 50.0% | 33.3% | +0.152 | +-1.20 |
| 2024 | 3 | 100.0% | 33.3% | -0.058 | +-1.94 |

Firings (all, overlapping allowed): 14; kind: 13 sweep / 1 div.

### Arm: swing-swing / wick / cross+RSI<60

Ladder (non-overlapping trades within each tier, 1R exit, fee-net 0.04%/side):

| tier | trades | hit >=1R | target 1R hit | net R/trade | CI |
|---|---|---|---|---|---|
| L1-3 | 90 | 47.8% | 47.8% | -0.055 | +-0.21 |
| L1-4 | 36 | 44.4% | 44.4% | -0.091 | +-0.32 |
| L1-5 (firings) | 9 | 55.6% | 55.6% | +0.061 | +-0.70 |

Firings by regime, 1R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 4 | 100.0% | 100.0% | +0.970 | +-0.01 |
| bear | 4 | 25.0% | 25.0% | -0.567 | +-0.98 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 1R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 0 | | | | |
| 2020 | 0 | | | | |
| 2021 | 1 | 100.0% | 100.0% | +0.964 | +- |
| 2022 | 2 | 50.0% | 50.0% | -0.044 | +-1.91 |
| 2023 | 5 | 40.0% | 40.0% | -0.258 | +-0.99 |
| 2024 | 1 | 100.0% | 100.0% | +0.966 | +- |

Firings by regime, 2R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 4 | 100.0% | 50.0% | +0.776 | +-1.44 |
| bear | 4 | 25.0% | 0.0% | -1.067 | +-0.03 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 2R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 0 | | | | |
| 2020 | 0 | | | | |
| 2021 | 1 | 100.0% | 100.0% | +1.964 | +- |
| 2022 | 2 | 50.0% | 0.0% | -1.044 | +-0.05 |
| 2023 | 5 | 40.0% | 20.0% | -0.213 | +-1.18 |
| 2024 | 1 | 100.0% | 0.0% | -1.035 | +- |

Firings (all, overlapping allowed): 9; kind: 8 sweep / 1 div.
