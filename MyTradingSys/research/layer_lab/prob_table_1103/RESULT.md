# Probability table results

All design choices labelled OURS are experimental choices, not sourced trader rules.

Closed UTC bars only. Fit 2022-01-01 through 2024-06-30; evaluation 2020-01-01 through 2021-12-31. No bars after 2024-06-30 were loaded. VALIDATION and HOLDOUT were not read.
Fees: canonical Deribit all-taker 10 bp round trip before slippage (fees.py). Parameters: BB20/2 population SD, Wilder RSI14, SMA200 regime, Laplace binary smoothing, n<30 fallback to regime parent, EV is mean signed close-to-close return net of fee, weekly block bootstrap 1,000 replicates; all OURS.

Log-loss difference is model minus regime baseline (negative is better). EV difference is model minus baseline net return per eligible bar; 95% weekly block-bootstrap CIs.

| TF | Horizon | Verdict | Fit n | Test n | Model LL | Baseline LL | LL diff [95% CI] | Model EV | Baseline EV | EV diff [95% CI] | Trades model/base | Cells used |
|---:|---:|---|---:|---:|---:|---:|---|---:|---:|---|---:|---:|
| 1h | 4 | KILL | 21685 | 17341 | 0.692440 | 0.693282 | -0.000842 [-0.002250, 0.000604] | 0.003330% | 0.000000% | 0.003330% [-0.009297%, 0.019854%] | 1066/0 | 17302 |
| 1h | 24 | KILL | 21665 | 17321 | 0.693450 | 0.694103 | -0.000653 [-0.003241, 0.001814] | 0.069747% | 0.059550% | 0.010196% [-0.062398%, 0.090137%] | 7907/7121 | 17282 |
| 4h | 4 | KILL | 5269 | 4183 | 0.696760 | 0.692971 | 0.003789 [0.000243, 0.007570] | 0.077909% | 0.143426% | -0.065517% [-0.181186%, 0.046644%] | 1931/2556 | 4163 |
| 4h | 24 | KILL | 5249 | 4163 | 0.689096 | 0.689809 | -0.000713 [-0.008240, 0.007183] | 0.955179% | 1.145623% | -0.190444% [-0.536473%, 0.149559%] | 4163/4163 | 4143 |

Kill line: KEEP requires log-loss difference CI wholly below 0, test EV above 0, and EV-difference CI wholly above 0. Otherwise KILL.
MFE/MAE per evaluation state cell are in cell_quantiles.csv (MFE 50th/90th; MAE 10th/50th percentiles).
Limitations: one asset/venue; no slippage or funding; binary up/down log-loss; the reverse-time fit/evaluation split follows the frozen card. Results are exploratory and do not authorize live trading.
