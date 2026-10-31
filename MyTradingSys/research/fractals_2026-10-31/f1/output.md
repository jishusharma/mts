| group | n real | net mean R | 95% CI | n random | random mean R | diff (real - random) | diff 95% CI |
|---|---|---|---|---|---|---|---|
| CONF_ANY | 2556 | -0.2665 | [-0.3099, -0.2250] | 5183 | -0.1603 | -0.1062 | [-0.1431, -0.0700] |
| CONF_4H | 1850 | -0.2672 | [-0.3163, -0.2210] | 3732 | -0.1621 | -0.1051 | [-0.1498, -0.0607] |
| CONF_1D | 706 | -0.2646 | [-0.3546, -0.1799] | 1451 | -0.1555 | -0.1091 | [-0.1795, -0.0394] |
| NONE | 4860 | -0.2261 | [-0.2566, -0.1957] | 9774 | -0.1373 | -0.0888 | [-0.1174, -0.0621] |

1h pivots with live window inside DEV: 8746.
Shift null (labels NONE/CONF_4H/CONF_1D, net % per trade): max gap 0.0461 vs 95th pct threshold 0.0594, p_global 0.129, flagged [].
Binary confluence-vs-none shift null on the real outcomes: flagged [1] (cell 1 = confluence; its gap is negative, i.e. worse than none).
Planted edge on cell-demeaned outcomes (+0.3 % on 20 % of confluence events): flagged without [], with [1].
Power: per-trade sd 0.837 %; n needed per cell to see 0.10 % at 80 % power = 551; CONF_ANY n = 2556.

Exit mix (real events):
why      stop  target  time
group                      
CONF_1D   388     313     5
CONF_4H   998     840    12
NONE     2522    2293    45

Phase split (descriptive, NO verdict): group, tag, n, net mean R
| group | tag | n | net mean R |
|---|---|---|---|
| CONF_ANY | cowen_side=above | 1414 | -0.2501 |
| CONF_ANY | cowen_side=below | 1076 | -0.2876 |
| CONF_ANY | cowen_side=inside | 66 | -0.2743 |
| NONE | cowen_side=above | 2645 | -0.2351 |
| NONE | cowen_side=below | 2055 | -0.2118 |
| NONE | cowen_side=inside | 160 | -0.2607 |
| CONF_ANY | sma200_side=above | 1436 | -0.2546 |
| CONF_ANY | sma200_side=below | 1120 | -0.2818 |
| NONE | sma200_side=above | 2778 | -0.2337 |
| NONE | sma200_side=below | 2082 | -0.2159 |

VERDICT: FAIL
