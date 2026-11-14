# RESULT: long-only BTC-gated trend, gross cap 1.0x, 60 new coins (edge8-long-gated-trend-newcoins-1114)

**Verdict: FAIL on both rules. On 60 coins the parent never saw, neither GATED-TSM30 nor GATED-ADX14 clears any of the six gates (CI, Sharpe >= 1, basket, placebo, Bonferroni, robustness). The parent's lead did not confirm. With the 1.0x cap the books are survivable-looking (max drawdown 55-74 %) but the drawdown is large for a return of 16-25 % a year, and the profit rests on a few days.**

Regime mix: VALIDATION days 2024-01-01..2026-11-12 (1047), BTC close vs 200d SMA (bull > +5 %, bear < -5 %, else range): bull 56.1 % / bear 29.4 % / range 14.5 % (recomputed from the BTC data used; matches the 56/29/15 stated in PRE_REG.md).

PRE_REG.md was committed (448ea2880) before any return was computed. Data: new coins = Bybit v5 linear daily klines + real funding history (59 of 60 coins have funding records; funding coverage 100 % of held coin-days), BTC gate = Binance public spot (as the parent), last closed day 2026-11-12. 57 of the 60 coins entered the book at some point in VALIDATION for rule 9 (56 for rule 10); IDOL (1 bar) and the youngest listings never did. Everything else per PRE_REG.md; seed 20261114.

## Main table: the 60 NEW coins (this is the confirmation)
Returns are fractions of equity (additive), never above 1.0x gross. VALIDATION unless noted.

| rule | trades | VAL ann. | VAL Sharpe | CI of mean daily (95 %) | max DD (VAL) | placebo p | one-sided boot p | w/o best 10 days (ann.) | w/o best 5 coins (ann.) | beats basket | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 9 GATED-TSM30 | 363 | +16.3 % | 0.32 | [-0.098 %, +0.195 %] | 74.2 % | 0.377 | 0.275 | -18.7 % | -1.1 % | no | FAIL |
| 10 GATED-ADX14 | 267 | +25.1 % | 0.70 | [-0.041 %, +0.181 %] | 55.5 % | 0.094 | 0.113 | -6.4 % | +9.0 % | no | FAIL |

Equal-weight buy-and-hold basket of the same 60 coins (VAL, no cost): Sharpe 0.74, +60.2 % a year. The basket beats both rules; the new coins mostly went up on their way to being the most traded today (selection bias, see below), and the capped books were invested only 61 % / 53 % of days at 0.43x / 0.24x average gross.

Gates (all must be Y): g1 CI lower bound > 0, g2 Sharpe >= 1, g3 beats basket, g4 placebo p < 0.05, g5 Bonferroni (one-sided p and placebo p <= 0.025), g6 positive without best 10 days and without best 5 coins.

| rule | g1 | g2 | g3 | g4 | g5 | g6 |
|---|---|---|---|---|---|---|
| 9 GATED-TSM30 | n | n | n | n | n | n |
| 10 GATED-ADX14 | n | n | n | n | n | n |

## Descriptives, new 60
| rule | days invested | avg gross | max gross | coins in book (avg) | avg hold (d) | DEV Sharpe | last 90 d sum | best-10-days share of VAL profit | top 5 coins |
|---|---|---|---|---|---|---|---|---|---|
| 9 GATED-TSM30 | 60.8 % | 0.43x | 1.00x | 8.7 | 26.2 | 1.71 | +53.9 % | 213 % | 1000PEPE ENA QNT ONDO JCT |
| 10 GATED-ADX14 | 53.1 % | 0.24x | 1.00x | 5.3 | 21.0 | 1.32 | +72.7 % | 125 % | Q VIRTUAL MNT ENA 1000PEPE |

Per-year return (sum of daily returns): 2023 is partial (only the few coins with data by then; the early new-coin DEV window is about one year, so DEV Sharpe means little).

| rule | 2023 | 2024 | 2025 | 2026 (to 11-12) |
|---|---|---|---|---|
| 9 GATED-TSM30 | +102.2 % | -8.1 % | +1.0 % | +53.9 % |
| 10 GATED-ADX14 | +59.8 % | +29.1 % | -29.7 % | +72.7 % |

## NOT-CONFIRMATION row: the parent's own 60 coins (already seen, same capped rules)
Not evidence: the parent chose these rules because they looked best on these coins.

| rule | trades | VAL ann. | VAL Sharpe | CI of mean daily | max DD | placebo p | w/o best 10 days (ann.) | w/o best 5 coins (ann.) | avg gross | uncapped parent (VAL ann. / Sharpe / gross) | gates passed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 9 GATED-TSM30 | 680 | +16.3 % | 0.33 | [-0.105 %, +0.217 %] | 83.5 % | 0.058 | -17.9 % | +1.9 % | 0.53x | +215.9 % / 0.85 / 2.18x | 1 of 6 (basket) |
| 10 GATED-ADX14 | 412 | +26.8 % | 0.66 | [-0.064 %, +0.232 %] | 62.5 % | 0.004 | -6.8 % | +3.3 % | 0.36x | +102.9 % / 0.85 / 0.81x | 2 of 6 (basket, placebo) |

(The uncapped columns reproduce the parent's RESULT.md numbers: +215.9 % / 0.85 and +102.9 % / 0.85, trades 680 and 412, so the copied code and data match.) Capping at 1.0x lowers VAL Sharpe from 0.85 to 0.33 / 0.66 on the same coins probably because the cap bites in the up-moves when many coins signal together and every weight is trimmed pro rata, and each trim costs turnover.

## Reading
- No confirmation. On unseen coins VAL Sharpe is 0.32 / 0.70, the CIs straddle 0 (lower bounds -0.10 % and -0.04 % a day), one-sided p 0.28 / 0.11.
- The signal does not beat a random start date on the same coin for rule 9 (placebo p 0.38) and only weakly for rule 10 (0.094). On the parent's seen coins rule 10 beat the placebo (0.004), but that did not carry over.
- It does not beat buying and holding the same coins: the new-coin basket made 0.74 Sharpe with no timing at all. The gate and the exits take the book out of a lot of the rally (invested 53-61 % of days).
- It rests on a few days: the best 10 days are 125-213 % of VAL profit; without them the mean is negative for both rules. Without the best 5 coins rule 10 is still +9 % a year, rule 9 is -1 %.
- Concentration in 2025: rule 10 lost -29.7 % in 2025 on new coins, rule 9 made almost nothing; 2023 numbers use very few coins.
- The one sign that this family is not empty: both rules are positive on VAL (+16 % and +25 % a year, fee and funding net) and recent 90 days are strongly positive. But a positive mean whose CI includes zero, below the basket, is not an edge.

## Caveats in plain words
- The 60 coins are today's most-traded coins. Coins rank high today largely because they moved or got popular recently, so the sample is tilted toward winners and away from coins that faded or delisted; long-side numbers are upper bounds, and the basket (+60 % a year) shows how tilted. A FAIL on a tilted-favourable list is a stronger negative than a PASS would be a positive.
- Most contracts launched in 2025-2026, so VALIDATION is mostly a 2025-2026 window with 5-9 coins in the book on average; the DEV window for these coins is essentially 2023 only. Statistical power is low; a real small edge would not be detected either, so this says "not shown", not "proven absent".
- Perp prices here, spot prices for the parent row and the BTC gate. No intraday stops. The placebo moves each run to a random start without the BTC gate (the parent's method), so it is a loose benchmark.
- The gross cap trims pro rata and the trim is charged as turnover (registered in advance). Not a claim about live profitability. Two rules, one run, nothing tuned after seeing results.

Files: PRE_REG.md, study.py (parent trend_lib.py copied unchanged; study functions copied from the parent except the cap, long-only builder and robustness gates), fetch.py, select_universe.py, universe.py, test_trend.py (9 tests; the cap-not-applied and one-bar-look-ahead mutants fail as intended), results.json, run.log.
