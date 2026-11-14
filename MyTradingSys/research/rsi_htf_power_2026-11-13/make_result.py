"""Assembles RESULT.md from tables.md (report.py output) plus the fixed prose below."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
tables = open(os.path.join(HERE, "tables.md")).read()
head = """# RESULT: RSI-HTF extreme power test on new spot data (edge5-rsi-htf-power-1113)

**Verdict: 0 of 6 cells PASS. S1 (operator rule 4h<=12 & daily<30) both exits: UNDERPOWERED (18 signal days < 30). S2 (4h<=15 & d<30) both exits: FAIL. S3 (12h<=20) both exits: FAIL.**

Regime mix: BTC daily close vs 200d SMA (bull above, bear at or below) at the signal bar close of the traded signals, POOL: S1 bull 7 / bear 29 trades; S2 bull 32 / bear 53; S3 bull 64 / bear 146. Underlying BTC day mix: 2017-2019 bull 30% / bear 70%; 2020-now bull 59% / bear 41%.

Data: Binance spot 1h/1d (data-api.binance.vision), all 60 coins loaded (first bars in meta.json; BTC/ETH 2017-08-17). B1 = parent's 20 coins, entries before 2020-01-01 (signals S1/S2/S3 = 5 / 9 / 17). B2 = 40 new coins, full history (31 / 76 / 193). Rules, costs (5 bp taker + 1 bp slippage per side) and exit code are the parent's. Placebo A = same coin, same calendar month, same stop distance; placebo B = same coin, entries only where the last closed BTC daily RSI < 35; 400 draws each. Bonferroni threshold 0.05/6 = 0.0083 on day-bootstrap p and both placebo p. Pre-registered rule: PRE_REG.md.

## What the new data says
- S1 looks strong on B2: mean +1.07R (2R) / +1.45R (time10), trade CI above zero, both placebo p 0.002-0.015. It fails on clustering: day CI [-0.16, +1.53] (2R) and [-0.18, +2.09] (time10), only 18 distinct signal days. One date, 2024-07-05, supplies 14 of the 36 trades and 27.7R of the 33.8R total (82%) at 2R; the best 5 days are 109% of total R (all other days net negative) and without them the mean is -0.19R (2R) / -0.33R (time10), n 16. B1 (2018-2019, n 5) is inconclusive (+0.15R at 2R, -0.20R at time10).
- S2: same shape with more days (34): trade CI [0.05, 0.57] but day CI [-0.20, 0.82]; best 5 days 143% of total R, without them -0.19R. B1 (n 9) is negative (-0.71R / -0.64R, both CIs below zero on the trade view).
- S3 (12h<=20): 2R mean +0.15R, trade CI [-0.01, 0.31], day CI [-0.16, 0.41], placebo B p 0.117 (random 12h closes on BTC-oversold days do as well); time10 exit is negative (-0.06R). Without the best 5 days (2024-08-05, 2026-02-05, 2024-07-05, 2024-04-13, 2022-11-09): -0.23R (2R) / -0.38R (time10).
- Placebo A (month-matched) is easy to beat because the gated cells fire only in crashes; placebo B is the fairer test and S1/S2 pass it, but the day-cluster CI and the 30-day floor bind.
- Parent leads: (a) keeps its sign on new data (+0.9R to +1.2R) but rests on 18 independent days dominated by one flush, so no edge claim; (b) does not replicate (+0.15R at 2R, CI crosses zero, time exit negative).
- Regime: the gated cells earn in bear (S1 bear +1.00R / +1.34R n 29; S2 bear +0.51R / +0.60R n 53) and about zero in bull; S3 at 2R is regime-flat.
- top5 share above 1 means the top 5 signal days sum to more than total R (the remaining days net negative).

## Results table
Verdict is on POOL rows only. per-year = mean R (n) by entry year.

"""
tail = """
## Files
PRE_REG.md (committed before outcomes), pick_universe.py, fetch.py, study.py, report.py, make_result.py, test_power.py (2 tests, not registered), htf_lib.py and rsi_grid_lib.py (parent's, unchanged), cells.csv, trades.csv, tables.md, meta.json.

## Caveats
Spot not perps, no funding; B2 universe chosen by present liquidity (survivorship); the 14-trade date 2024-07-05 is one market observation, so even the day CI may overstate independence; S1 and S2 share trades; Bonferroni over 6 is conservative.

Next: END: leads do not survive the day-cluster view; revisit only with more independent crash days (longer history); no layer promotion.
"""
open(os.path.join(HERE, "RESULT.md"), "w").write(head + tables + tail)
