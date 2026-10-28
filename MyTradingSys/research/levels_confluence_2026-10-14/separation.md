# LC2 feature separation (DEV only)

Outcome label: **good** = first opposing KEEP level touched within the same UTC day; **bad** = not reached. One-at-a-time feature split is feature affirmative/present vs negative/absent; metric is mean forward MFE_R difference (affirmative minus negative). CIs resample whole UTC days (2,000 replicates, seed 20261016). This is descriptive selection on DEV, not a trading rule.

## One-at-a-time results

| Feature | n yes/no | MFE_R yes | MFE_R no | Difference | 95% day-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| E1_rsi_holds_40_60 | 595/386 | 5.231 | 4.042 | +1.190 | [0.414, 2.042] |
| E2_holds_ma | 463/412 | 4.936 | 4.301 | +0.634 | [-0.322, 1.575] |
| E3_cvd_sign | 616/546 | 5.047 | 4.834 | +0.214 | [-0.464, 0.858] |
| E3_footprint_slope | 458/820 | 4.956 | 4.957 | -0.001 | [-1.117, 0.959] |
| E4_outer_band | 405/515 | 5.157 | 4.239 | +0.918 | [0.053, 1.898] |
| B1_value_area | 384/894 | 4.545 | 5.134 | -0.589 | [-1.500, 0.364] |
| B2_swing_1h | 376/902 | 5.038 | 4.923 | +0.115 | [-0.695, 0.969] |
| B2_swing_4h | 355/910 | 5.163 | 4.892 | +0.271 | [-0.781, 1.344] |
| B2_swing_6h | 361/886 | 4.981 | 4.915 | +0.066 | [-0.989, 1.186] |
| B2_swing_12h | 334/862 | 4.183 | 5.311 | -1.128 | [-2.434, 0.159] |
| B2_swing_1d | 292/751 | 4.347 | 4.855 | -0.508 | [-1.549, 0.688] |
| B3_ema20_1h | 656/622 | 5.187 | 4.714 | +0.474 | [-0.381, 1.390] |
| B3_ema20_4h | 649/616 | 4.705 | 5.245 | -0.540 | [-1.564, 0.583] |
| B3_ema20_6h | 631/616 | 4.728 | 5.145 | -0.418 | [-1.343, 0.502] |
| B3_ema20_12h | 609/587 | 4.941 | 5.054 | -0.113 | [-1.179, 1.024] |
| B3_ema20_1d | 522/521 | 4.942 | 4.484 | +0.458 | [-0.601, 1.620] |

## LC3 pre-registration (frozen before LC3)

Selected combinations (max 6): E1_rsi_holds_40_60, E4_outer_band

These are candidate feature filters attached to KEEP levels, not trading rules. No LC3 simulation is included here.

Trials counted: one event-table generation; 16 one-at-a-time feature contrasts. Total **17** analysis arms, logged in `research/layer_lab/TRIALS.md`.
