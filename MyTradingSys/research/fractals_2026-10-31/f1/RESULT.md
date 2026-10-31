# F1 RESULT: 1h Williams pivots with 4h/daily confluence vs random levels (fee-net)

**Verdict: FAIL.** Confluence pivots do not beat random levels: they lose more, fee-net. PRE_REG.md was committed (41bec4000) before the first run; nothing was tuned. Data BTCUSDT 1m 2022-01-01..2025-06-30 (files after 2025-06 never opened). Fees: all-taker `fees.BINANCE_TAKER` both legs (about 0.17 R per trade at a 1 ATR stop). Fade trade: stop 1 ATR beyond the level, target +1R, 24 h time exit. All parameters OURS (PRE_REG.md).

Gross R before fees is slightly negative as well (stop 3,908 vs target 3,446 of 7,416 real trades), so the loss is not only fees.

## Numbers
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

## Reading
- n is far above 200 in every group (CONF_ANY 2,556); power: 0.10 % needs about 551 per cell, so this is not a thin-data null.
- CONF_ANY net mean R -0.267 [-0.310, -0.225]; random levels with the same distance distribution -0.160; difference -0.106 [-0.143, -0.070]. The CI excludes 0 on the wrong side, so the PRE_REG FAIL rule applies.
- NONE (no confluence) is also negative (-0.226) and also below its random control (-0.137). Confluence is no better than a plain pivot (-0.267 vs -0.226).
- The 3-label shift null does not flag a cell (max gap 0.046 vs threshold 0.059). A binary confluence-vs-none shift null flags confluence, with a negative gap.
- Planted-edge check: +0.3 % on 20 % of confluence events is flagged (cell 1) and nothing is flagged without it. Deviation from PRE_REG, disclosed: this check runs on outcomes with each cell's own mean removed, because on the raw outcomes the real negative confluence gap masks the planted edge (raw run: flagged [1] without injection, [] with it, since the real gap is negative). The verdict does not depend on this check.
- Phase split (descriptive, no verdict): every cowen_side and sma200_side cell is negative for both CONF_ANY and NONE (range -0.21 to -0.29 R); no tag turns confluence positive.

## Caveats
- Fill model is touch = fill at the level (or the open if gapped). This is optimistic for fades; a real limit order could miss or be adverse-selected. It cannot rescue a negative.
- One tolerance (0.5 ATR), one stop/target and one horizon were tested, as pre-registered; other geometry is untested and is not implied by this result. Random levels sit at a different local geometry (not at an extreme), so "random beats pivots" says fading a fresh 5-bar extreme is worse than fading an arbitrary level at matched distance, not that random levels have an edge (they are also negative).
- Shift test and week-block bootstrap treat touch events as independent across weeks; events within a week overlap.

No rule, gate or layer added. Reproduce: `python MyTradingSys/research/fractals_2026-10-31/f1/run_f1.py`.
