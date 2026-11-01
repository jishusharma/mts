# EXT_RESULT: meta-label 1h lead on fresh 2020-2021 data (2026-11-01, JIS-NB)

Card `meta-label-1h-dev-ext-check`. Rules frozen in `EXT_PRE_REG.md` (commit fcb733008) before any 2020-2021 outcome was scored.
Frozen 15-feature logistic (`meta.py`), fit on all 1,078 DEV 1h trades (2022-01..2024-06), scored once on 822 BTCUSDT 1h tf_break trades
from 1m bars 2020-01..2021-12 (1,052,640 bars; 1,108 events, 286 dropped for the missing 200-day SMA, as in DEV). VALIDATION and HOLDOUT
unread. Cost 0.10 % round trip, no slippage, no funding. Raw numbers: `F:/MTS/runs/meta_label_breaks/ext.json`.

## Answer: **FAIL.** The DEV 1h lead did not carry to fresh years. Every third loses after fees.
| third (cut from DEV scores) | n | gross % | fee-net % | 95 % week-block CI |
|---|---|---|---|---|
| top (the pre-registered best third) | 303 | -0.099 | **-0.199** | -0.411..-0.017 |
| middle | 257 | -0.099 | -0.199 | -0.414..+0.014 |
| bottom | 262 | +0.090 | -0.010 | -0.172..+0.147 |
| all | 822 | -0.039 | -0.139 | -0.252..-0.033 |

- Label-shuffle p = 0.811 (200 shuffles). The top third did 0.060 % worse than all trades; the lift in DEV was +0.096 %. The ranking has
  no out-of-time skill: the bottom third is the best one, the opposite of what the model says.
- Top third by year: 2020 -0.225 % (n 105), 2021 -0.185 % (n 198). Same sign.
- Pass rule: top third net > 0 with CI lower > 0 and p <= 0.05. Top third net is -0.199 %, CI upper -0.017 < 0. Verdict FAIL. Even the
  best of the three thirds (bottom, -0.010 %) is not above zero.
- Power: the gate gave a minimum detectable top-third net of 0.19 % + cost at n about 260; the observed top third (n 303) is negative by
  more than that, so this is not a "too few trades" miss.

## Limits
Spot-format klines for 2020-2021 (futures symbol history differs); no funding, no slippage; one frozen specification, one run, no
re-tuning. The 15m and 4h arms were not part of this card. It says nothing about other features or exits.
