# lab-verify-mtf-bias-ladder -- fee-net MTF bias ladder + Malkan RSI 40-60 zone (BTCUSDT)

**Author**: Lab_Analyst (Sonnet/Claude), standing in for the DeepSeek/DSA bridge, which the operator is holding closed. This is an independent Sonnet-derived read computed fresh from real klines; it is **not** a second-vendor cross-check of a prior DeepSeek number (no DSA number exists yet on this card).

## Parameters (labelled)

- Ladder timeframes (grandfather->father->son), higher side: 1w, 5d*, 3d, 2d*, 1d, 12h (SOURCED exchange intervals: 1w/3d/1d/12h; OURS aggregates built from 1d closes: 5d*, 2d*)
- Lower / tradable timeframes tested: 1h, 15m (SOURCED exchange intervals)
- RSI length: 14 (SOURCED, standard Wilder RSI, matches registry script mtf_bias.py); 40-60 zone threshold is SOURCED from the operator's brief (Malkan 40-60 state), not re-derived here
- Fee: 0.20% round trip (SOURCED, given directly in the task's DONE-when)
- Higher-TF history: genesis 2017-08-17 -> 2026-10-28 (as many years as the API gives)
- Lower-TF (1h/15m) history: 2022-01-01 -> 2026-10-28 (DECISION OURS: bounded to keep this single run inside the session's time budget; full history for 1w/3d/1d/12h/5d*/2d* was pulled, the cap only applies to the two expensive lower timeframes used for the forward-return test)
- Bucket scheme and horizons were fixed BEFORE looking at DEV or VALIDATION numbers (trial_count = 1, see trial_ledger.csv) -- no search over alternative bucket edges

## DEV (2022-01-01 -> 2025-05-17)

### 1h -- n=29589 bars, 6 ladder states

| ladder state | n | horizon | gross fwd ret (mean) | fee-net fwd ret | baseline (unconditional) | fee-net edge vs baseline | t-stat (Welch, vs complement) |
|---|---|---|---|---|---|---|---|
| mixed / RSI-few-40-60 | 2928 | 4 | -0.047% | -0.247% | +0.017% (net -0.183%) | -0.064% | -3.18 |
| mixed / RSI-few-40-60 | 2928 | 8 | -0.087% | -0.287% | +0.034% (net -0.166%) | -0.121% | -4.23 |
| mixed / RSI-few-40-60 | 2928 | 16 | -0.117% | -0.317% | +0.069% (net -0.131%) | -0.185% | -4.68 |
| mixed / RSI-many-40-60 | 3372 | 4 | -0.031% | -0.231% | +0.017% (net -0.183%) | -0.048% | -2.94 |
| mixed / RSI-many-40-60 | 3372 | 8 | -0.034% | -0.234% | +0.034% (net -0.166%) | -0.068% | -2.99 |
| mixed / RSI-many-40-60 | 3372 | 16 | -0.043% | -0.243% | +0.069% (net -0.131%) | -0.112% | -3.43 |
| mostly-GREEN / RSI-few-40-60 | 7559 | 4 | +0.050% | -0.150% | +0.017% (net -0.183%) | +0.033% | +3.00 |
| mostly-GREEN / RSI-few-40-60 | 7559 | 8 | +0.105% | -0.095% | +0.034% (net -0.166%) | +0.071% | +4.55 |
| mostly-GREEN / RSI-few-40-60 | 7559 | 16 | +0.194% | -0.006% | +0.069% (net -0.131%) | +0.126% | +5.69 |
| mostly-GREEN / RSI-many-40-60 | 4920 | 4 | +0.019% | -0.181% | +0.017% (net -0.183%) | +0.002% | +0.14 |
| mostly-GREEN / RSI-many-40-60 | 4920 | 8 | +0.033% | -0.167% | +0.034% (net -0.166%) | -0.001% | -0.07 |
| mostly-GREEN / RSI-many-40-60 | 4920 | 16 | +0.084% | -0.116% | +0.069% (net -0.131%) | +0.015% | +0.58 |
| mostly-RED / RSI-few-40-60 | 5854 | 4 | +0.040% | -0.160% | +0.017% (net -0.183%) | +0.022% | +1.43 |
| mostly-RED / RSI-few-40-60 | 5854 | 8 | +0.066% | -0.134% | +0.034% (net -0.166%) | +0.032% | +1.49 |
| mostly-RED / RSI-few-40-60 | 5854 | 16 | +0.101% | -0.099% | +0.069% (net -0.131%) | +0.033% | +1.05 |
| mostly-RED / RSI-many-40-60 | 4956 | 4 | +0.009% | -0.191% | +0.017% (net -0.183%) | -0.008% | -0.61 |
| mostly-RED / RSI-many-40-60 | 4956 | 8 | +0.006% | -0.194% | +0.034% (net -0.166%) | -0.028% | -1.41 |
| mostly-RED / RSI-many-40-60 | 4956 | 16 | +0.009% | -0.191% | +0.069% (net -0.131%) | -0.060% | -2.12 |

### 15m -- n=118354 bars, 6 ladder states

| ladder state | n | horizon | gross fwd ret (mean) | fee-net fwd ret | baseline (unconditional) | fee-net edge vs baseline | t-stat (Welch, vs complement) |
|---|---|---|---|---|---|---|---|
| mixed / RSI-few-40-60 | 11712 | 4 | -0.008% | -0.208% | +0.004% (net -0.196%) | -0.012% | -2.46 |
| mixed / RSI-few-40-60 | 11712 | 8 | -0.019% | -0.219% | +0.009% (net -0.191%) | -0.028% | -3.87 |
| mixed / RSI-few-40-60 | 11712 | 16 | -0.043% | -0.243% | +0.017% (net -0.183%) | -0.060% | -5.86 |
| mixed / RSI-many-40-60 | 13488 | 4 | -0.011% | -0.211% | +0.004% (net -0.196%) | -0.015% | -3.56 |
| mixed / RSI-many-40-60 | 13488 | 8 | -0.022% | -0.222% | +0.009% (net -0.191%) | -0.031% | -5.22 |
| mixed / RSI-many-40-60 | 13488 | 16 | -0.032% | -0.232% | +0.017% (net -0.183%) | -0.050% | -6.05 |
| mostly-GREEN / RSI-few-40-60 | 30235 | 4 | +0.012% | -0.188% | +0.004% (net -0.196%) | +0.008% | +2.82 |
| mostly-GREEN / RSI-few-40-60 | 30235 | 8 | +0.025% | -0.175% | +0.009% (net -0.191%) | +0.017% | +4.25 |
| mostly-GREEN / RSI-few-40-60 | 30235 | 16 | +0.049% | -0.151% | +0.017% (net -0.183%) | +0.032% | +5.83 |
| mostly-GREEN / RSI-many-40-60 | 19680 | 4 | +0.006% | -0.194% | +0.004% (net -0.196%) | +0.002% | +0.57 |
| mostly-GREEN / RSI-many-40-60 | 19680 | 8 | +0.012% | -0.188% | +0.009% (net -0.191%) | +0.004% | +0.84 |
| mostly-GREEN / RSI-many-40-60 | 19680 | 16 | +0.020% | -0.180% | +0.017% (net -0.183%) | +0.003% | +0.47 |
| mostly-RED / RSI-few-40-60 | 23415 | 4 | +0.011% | -0.189% | +0.004% (net -0.196%) | +0.006% | +1.62 |
| mostly-RED / RSI-few-40-60 | 23415 | 8 | +0.020% | -0.180% | +0.009% (net -0.191%) | +0.012% | +2.12 |
| mostly-RED / RSI-few-40-60 | 23415 | 16 | +0.040% | -0.160% | +0.017% (net -0.183%) | +0.023% | +2.90 |
| mostly-RED / RSI-many-40-60 | 19824 | 4 | +0.001% | -0.199% | +0.004% (net -0.196%) | -0.004% | -1.06 |
| mostly-RED / RSI-many-40-60 | 19824 | 8 | +0.003% | -0.197% | +0.009% (net -0.191%) | -0.005% | -1.07 |
| mostly-RED / RSI-many-40-60 | 19824 | 16 | +0.007% | -0.193% | +0.017% (net -0.183%) | -0.010% | -1.40 |

## VALIDATION (2025-05-17 -> 2026-10-28)

### 1h -- n=12681 bars, 6 ladder states

| ladder state | n | horizon | gross fwd ret (mean) | fee-net fwd ret | baseline (unconditional) | fee-net edge vs baseline | t-stat (Welch, vs complement) |
|---|---|---|---|---|---|---|---|
| mixed / RSI-few-40-60 | 1320 | 4 | -0.077% | -0.277% | -0.004% (net -0.204%) | -0.073% | -3.39 |
| mixed / RSI-few-40-60 | 1320 | 8 | -0.129% | -0.329% | -0.008% (net -0.208%) | -0.121% | -4.04 |
| mixed / RSI-few-40-60 | 1320 | 16 | -0.203% | -0.403% | -0.017% (net -0.217%) | -0.186% | -4.53 |
| mixed / RSI-many-40-60 | 1716 | 4 | +0.001% | -0.199% | -0.004% (net -0.204%) | +0.005% | +0.29 |
| mixed / RSI-many-40-60 | 1716 | 8 | -0.008% | -0.208% | -0.008% (net -0.208%) | +0.000% | +0.02 |
| mixed / RSI-many-40-60 | 1716 | 16 | -0.006% | -0.206% | -0.017% (net -0.217%) | +0.011% | +0.32 |
| mostly-GREEN / RSI-few-40-60 | 2640 | 4 | +0.020% | -0.180% | -0.004% (net -0.204%) | +0.024% | +1.65 |
| mostly-GREEN / RSI-few-40-60 | 2640 | 8 | +0.044% | -0.156% | -0.008% (net -0.208%) | +0.052% | +2.53 |
| mostly-GREEN / RSI-few-40-60 | 2640 | 16 | +0.065% | -0.135% | -0.017% (net -0.217%) | +0.081% | +2.76 |
| mostly-GREEN / RSI-many-40-60 | 2064 | 4 | +0.019% | -0.181% | -0.004% (net -0.204%) | +0.023% | +1.63 |
| mostly-GREEN / RSI-many-40-60 | 2064 | 8 | +0.045% | -0.155% | -0.008% (net -0.208%) | +0.053% | +2.53 |
| mostly-GREEN / RSI-many-40-60 | 2064 | 16 | +0.079% | -0.121% | -0.017% (net -0.217%) | +0.095% | +3.13 |
| mostly-RED / RSI-few-40-60 | 2678 | 4 | +0.006% | -0.194% | -0.004% (net -0.204%) | +0.010% | +0.56 |
| mostly-RED / RSI-few-40-60 | 2678 | 8 | -0.001% | -0.201% | -0.008% (net -0.208%) | +0.007% | +0.27 |
| mostly-RED / RSI-few-40-60 | 2678 | 16 | -0.027% | -0.227% | -0.017% (net -0.217%) | -0.011% | -0.30 |
| mostly-RED / RSI-many-40-60 | 2259 | 4 | -0.027% | -0.227% | -0.004% (net -0.204%) | -0.023% | -1.48 |
| mostly-RED / RSI-many-40-60 | 2255 | 8 | -0.055% | -0.255% | -0.008% (net -0.208%) | -0.047% | -2.16 |
| mostly-RED / RSI-many-40-60 | 2247 | 16 | -0.086% | -0.286% | -0.017% (net -0.217%) | -0.070% | -2.31 |

### 15m -- n=50725 bars, 6 ladder states

| ladder state | n | horizon | gross fwd ret (mean) | fee-net fwd ret | baseline (unconditional) | fee-net edge vs baseline | t-stat (Welch, vs complement) |
|---|---|---|---|---|---|---|---|
| mixed / RSI-few-40-60 | 5280 | 4 | -0.017% | -0.217% | -0.001% (net -0.201%) | -0.016% | -2.76 |
| mixed / RSI-few-40-60 | 5280 | 8 | -0.036% | -0.236% | -0.002% (net -0.202%) | -0.034% | -4.35 |
| mixed / RSI-few-40-60 | 5280 | 16 | -0.073% | -0.273% | -0.004% (net -0.204%) | -0.069% | -6.34 |
| mixed / RSI-many-40-60 | 6864 | 4 | +0.001% | -0.199% | -0.001% (net -0.201%) | +0.002% | +0.54 |
| mixed / RSI-many-40-60 | 6864 | 8 | +0.005% | -0.195% | -0.002% (net -0.202%) | +0.007% | +1.10 |
| mixed / RSI-many-40-60 | 6864 | 16 | +0.003% | -0.197% | -0.004% (net -0.204%) | +0.007% | +0.76 |
| mostly-GREEN / RSI-few-40-60 | 10560 | 4 | +0.004% | -0.196% | -0.001% (net -0.201%) | +0.005% | +1.46 |
| mostly-GREEN / RSI-few-40-60 | 10560 | 8 | +0.009% | -0.191% | -0.002% (net -0.202%) | +0.011% | +2.10 |
| mostly-GREEN / RSI-few-40-60 | 10560 | 16 | +0.020% | -0.180% | -0.004% (net -0.204%) | +0.024% | +3.25 |
| mostly-GREEN / RSI-many-40-60 | 8256 | 4 | +0.002% | -0.198% | -0.001% (net -0.201%) | +0.003% | +0.89 |
| mostly-GREEN / RSI-many-40-60 | 8256 | 8 | +0.005% | -0.195% | -0.002% (net -0.202%) | +0.007% | +1.34 |
| mostly-GREEN / RSI-many-40-60 | 8256 | 16 | +0.017% | -0.183% | -0.004% (net -0.204%) | +0.021% | +2.98 |
| mostly-RED / RSI-few-40-60 | 10713 | 4 | +0.001% | -0.199% | -0.001% (net -0.201%) | +0.002% | +0.43 |
| mostly-RED / RSI-few-40-60 | 10713 | 8 | +0.003% | -0.197% | -0.002% (net -0.202%) | +0.005% | +0.84 |
| mostly-RED / RSI-few-40-60 | 10713 | 16 | +0.004% | -0.196% | -0.004% (net -0.204%) | +0.008% | +0.91 |
| mostly-RED / RSI-many-40-60 | 9048 | 4 | -0.005% | -0.205% | -0.001% (net -0.201%) | -0.004% | -1.04 |
| mostly-RED / RSI-many-40-60 | 9044 | 8 | -0.012% | -0.212% | -0.002% (net -0.202%) | -0.010% | -1.91 |
| mostly-RED / RSI-many-40-60 | 9036 | 16 | -0.025% | -0.225% | -0.004% (net -0.204%) | -0.021% | -2.81 |

## Verdict

**NOT WORTH A LAYER on this read**: 0 / 36 VALIDATION cells with n>=30 clear both fee-net-positive AND |t|>=1.96. The ladder state (grandfather/father/son higher-TF bias count, crossed with Malkan 40-60 RSI zone count) does not show a reliable fee-net edge over the unconditional baseline on 1h/15m BTCUSDT forward returns in the VALIDATION window. Close the card; do not open a layer card from this result alone.

Trial count: 1 pre-specified design (see trial_ledger.csv); DEV used only to sanity-check the pipeline runs and produces non-degenerate bucket counts, not to pick thresholds; verdict above is judged on VALIDATION only.

## Run log

```
run start 2026-10-28T06:53Z
fetching 1w/3d/1d/12h from genesis (SOURCED exchange intervals)...
  1w=480 bars, 3d=1120 bars, 1d=3360 bars, 12h=6718 bars
  5d*(OURS)=672 buckets, 2d*(OURS)=1680 buckets
fetching 1h/15m from 2022-01-01 (DECISION OURS: runtime cap) -> now ...
  1h=42270 bars, 15m=169079 bars
DEV window: 2022-01-01 -> 2025-05-17  |  VALIDATION window: 2025-05-17 -> 2026-10-28
```
