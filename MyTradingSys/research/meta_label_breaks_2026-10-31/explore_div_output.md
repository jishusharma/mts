# EXPLORATORY, DEV only: Malkan divergence at entry and as exit on the tf_break trades

## 15m (DEV trades 5235; held to the first divergence against the trade or 24 bars)
| exit | trades | net % | 95 % CI | win % | PF | net % without best 5 % | median bars held |
|---|---|---|---|---|---|---|---|
| fixed 4 bars (meta.py) | 5235 | -0.104 | -0.121..-0.089 | 38 | 0.56 | -0.177 | 4 |
| fixed 24 bars | 5235 | -0.072 | -0.104..-0.039 | 47 | 0.85 | -0.247 | 24 |
| RSI divergence against, same TF | 5235 | -0.078 | -0.108..-0.046 | 47 | 0.82 | -0.235 | 24 |
| CVD divergence against, same TF | 5235 | -0.087 | -0.115..-0.057 | 46 | 0.78 | -0.237 | 24 |
| RSI divergence against, lower TF | 5235 | -0.075 | -0.101..-0.048 | 49 | 0.81 | -0.209 | 21 |
| CVD divergence against, lower TF | 5235 | -0.089 | -0.115..-0.064 | 41 | 0.71 | -0.206 | 9 |

At entry (fixed 4-bar trades): a divergence known in the last 10 bars
| divergence | role | share of all trades | share of best 5 % | net % with | n with | net % without |
|---|---|---|---|---|---|---|
| RSI bullish, same TF | with | 6 % | 5 % | -0.112 | 297 | -0.103 |
| CVD bullish, same TF | with | 12 % | 11 % | -0.091 | 624 | -0.106 |
| RSI bearish, same TF | against | 4 % | 5 % | -0.121 | 234 | -0.103 |
| CVD bearish, same TF | against | 12 % | 10 % | -0.142 | 640 | -0.099 |
| RSI prd, same TF | with | 1 % | 1 % | -0.079 | 30 | -0.104 |
| RSI nrd, same TF | against | 1 % | 1 % | -0.019 | 37 | -0.105 |
| RSI bullish, lower TF | with | 15 % | 16 % | -0.114 | 761 | -0.102 |
| CVD bullish, lower TF | with | 27 % | 24 % | -0.115 | 1406 | -0.100 |
| RSI bearish, lower TF | against | 11 % | 13 % | -0.101 | 596 | -0.104 |
| CVD bearish, lower TF | against | 28 % | 23 % | -0.119 | 1462 | -0.098 |
| RSI prd, lower TF | with | 3 % | 6 % | -0.085 | 143 | -0.105 |
| RSI nrd, lower TF | against | 1 % | 3 % | -0.073 | 76 | -0.104 |
| RSI bullish, same TF | against | 4 % | 6 % | -0.160 | 214 | -0.102 |
| CVD bullish, same TF | against | 10 % | 10 % | -0.165 | 539 | -0.097 |
| RSI bearish, same TF | with | 6 % | 5 % | -0.161 | 296 | -0.101 |
| CVD bearish, same TF | with | 14 % | 10 % | -0.139 | 714 | -0.098 |
| RSI prd, same TF | against | 1 % | 2 % | -0.161 | 57 | -0.103 |
| RSI bullish, lower TF | against | 11 % | 14 % | -0.087 | 551 | -0.106 |
| CVD bullish, lower TF | against | 26 % | 26 % | -0.119 | 1355 | -0.099 |
| RSI bearish, lower TF | with | 15 % | 16 % | -0.084 | 773 | -0.107 |
| CVD bearish, lower TF | with | 28 % | 29 % | -0.111 | 1476 | -0.101 |
| RSI prd, lower TF | against | 2 % | 3 % | -0.132 | 90 | -0.103 |
| RSI nrd, lower TF | with | 2 % | 4 % | -0.069 | 127 | -0.105 |

## 1h (DEV trades 1376; held to the first divergence against the trade or 24 bars)
| exit | trades | net % | 95 % CI | win % | PF | net % without best 5 % | median bars held |
|---|---|---|---|---|---|---|---|
| fixed 4 bars (meta.py) | 1376 | -0.053 | -0.120..+0.017 | 48 | 0.87 | -0.206 | 4 |
| fixed 24 bars | 1376 | -0.062 | -0.206..+0.087 | 51 | 0.94 | -0.413 | 24 |
| RSI divergence against, same TF | 1376 | -0.141 | -0.281..+0.000 | 50 | 0.85 | -0.450 | 24 |
| CVD divergence against, same TF | 1376 | -0.046 | -0.150..+0.068 | 49 | 0.94 | -0.347 | 23 |
| RSI divergence against, lower TF | 1376 | -0.115 | -0.250..+0.015 | 54 | 0.85 | -0.364 | 15 |
| CVD divergence against, lower TF | 1376 | -0.042 | -0.148..+0.066 | 49 | 0.92 | -0.248 | 6 |

At entry (fixed 4-bar trades): a divergence known in the last 10 bars
| divergence | role | share of all trades | share of best 5 % | net % with | n with | net % without |
|---|---|---|---|---|---|---|
| RSI bullish, same TF | with | 6 % | 9 % | +0.124 | 84 | -0.065 |
| CVD bullish, same TF | with | 10 % | 10 % | -0.103 | 143 | -0.047 |
| RSI bearish, same TF | against | 6 % | 6 % | +0.199 | 76 | -0.068 |
| CVD bearish, same TF | against | 14 % | 16 % | +0.041 | 186 | -0.068 |
| RSI bullish, lower TF | with | 15 % | 17 % | -0.087 | 213 | -0.047 |
| CVD bullish, lower TF | with | 33 % | 43 % | -0.065 | 460 | -0.047 |
| RSI bearish, lower TF | against | 16 % | 29 % | -0.032 | 225 | -0.057 |
| CVD bearish, lower TF | against | 36 % | 46 % | -0.036 | 491 | -0.063 |
| RSI prd, lower TF | with | 5 % | 13 % | +0.121 | 65 | -0.062 |
| RSI nrd, lower TF | against | 3 % | 4 % | +0.276 | 35 | -0.062 |
| RSI bullish, same TF | against | 4 % | 3 % | +0.045 | 53 | -0.057 |
| CVD bullish, same TF | against | 13 % | 7 % | +0.045 | 175 | -0.067 |
| RSI bearish, same TF | with | 7 % | 4 % | -0.103 | 90 | -0.050 |
| CVD bearish, same TF | with | 14 % | 10 % | -0.096 | 192 | -0.046 |
| RSI bullish, lower TF | against | 14 % | 10 % | +0.001 | 192 | -0.062 |
| CVD bullish, lower TF | against | 32 % | 28 % | +0.068 | 438 | -0.110 |
| RSI bearish, lower TF | with | 18 % | 14 % | -0.036 | 251 | -0.057 |
| CVD bearish, lower TF | with | 36 % | 28 % | -0.024 | 489 | -0.069 |
| RSI prd, lower TF | against | 2 % | 1 % | -0.230 | 34 | -0.049 |
| RSI nrd, lower TF | with | 4 % | 1 % | +0.015 | 58 | -0.056 |

## 4h (DEV trades 523; held to the first divergence against the trade or 12 bars)
| exit | trades | net % | 95 % CI | win % | PF | net % without best 5 % | median bars held |
|---|---|---|---|---|---|---|---|
| fixed 4 bars (meta.py) | 523 | -0.157 | -0.336..+0.008 | 46 | 0.82 | -0.468 | 4 |
| fixed 12 bars | 523 | -0.013 | -0.295..+0.256 | 49 | 0.99 | -0.526 | 12 |
| RSI divergence against, same TF | 523 | -0.048 | -0.316..+0.203 | 48 | 0.96 | -0.524 | 12 |
| CVD divergence against, same TF | 523 | +0.011 | -0.263..+0.277 | 49 | 1.01 | -0.470 | 12 |
| RSI divergence against, lower TF | 523 | -0.132 | -0.445..+0.170 | 51 | 0.89 | -0.531 | 12 |
| CVD divergence against, lower TF | 523 | +0.029 | -0.187..+0.242 | 48 | 1.03 | -0.377 | 6 |

At entry (fixed 4-bar trades): a divergence known in the last 10 bars
| divergence | role | share of all trades | share of best 5 % | net % with | n with | net % without |
|---|---|---|---|---|---|---|
| CVD bullish, same TF | with | 8 % | 11 % | +0.232 | 42 | -0.191 |
| RSI bearish, same TF | against | 6 % | 4 % | +0.330 | 30 | -0.186 |
| CVD bearish, same TF | against | 15 % | 7 % | -0.191 | 78 | -0.151 |
| RSI bullish, lower TF | with | 16 % | 11 % | -0.398 | 84 | -0.111 |
| CVD bullish, lower TF | with | 31 % | 30 % | -0.181 | 163 | -0.146 |
| RSI bearish, lower TF | against | 18 % | 26 % | -0.069 | 95 | -0.176 |
| CVD bearish, lower TF | against | 37 % | 33 % | -0.165 | 191 | -0.152 |
| RSI prd, lower TF | with | 7 % | 19 % | +0.493 | 36 | -0.205 |
| RSI bullish, same TF | against | 7 % | 15 % | +0.248 | 36 | -0.187 |
| CVD bullish, same TF | against | 7 % | 15 % | -0.119 | 38 | -0.160 |
| RSI bearish, same TF | with | 6 % | 0 % | -0.744 | 31 | -0.120 |
| CVD bearish, same TF | with | 15 % | 7 % | -0.094 | 77 | -0.167 |
| RSI bullish, lower TF | against | 16 % | 22 % | +0.043 | 85 | -0.195 |
| CVD bullish, lower TF | against | 33 % | 30 % | -0.255 | 175 | -0.107 |
| RSI bearish, lower TF | with | 16 % | 15 % | -0.167 | 83 | -0.155 |
| CVD bearish, lower TF | with | 35 % | 48 % | -0.153 | 184 | -0.159 |
| RSI nrd, lower TF | with | 6 % | 15 % | +0.322 | 32 | -0.188 |
