"""Builds RESULT.md = fixed header + tables from report.py + reading + limits."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
t = subprocess.run([sys.executable, os.path.join(HERE, "report.py")], capture_output=True, text=True, encoding="utf-8",
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
head = """# RESULT: daily trend-following, long and short, 60 coins (edge7-daily-trend-follow-1113)

**Verdict: no rule passes. 0 of 10 combined books pass; every one fails the CI test (VALIDATION mean daily return CI lower bound below 0) and the Sharpe >= 1.0 test, and none survives BH 10 %. Following the daily trend on 60 coins does not give a fee-and-funding-net edge here either.**

Regime mix: BTC daily close vs 200d SMA, 2021-01-01..2026-11: bull 49 % / bear 38 % / range 13 %; 2024-01-01..now (VALIDATION): bull 56 % / bear 29 % / range 15 % (from edge6 capitulation_breadth RESULT.md; the BTC 200d gate of rules 8-10 uses the strict close above/below the SMA).

Data: Binance public spot daily klines (60 coins, PRE_REG.md universe), 2020-07-18 (first day the BTC 200d SMA exists = DEV start) .. 2026-11-12 (last closed bar; the newest bar is excluded). DEV 2020-07-18..2023-12-31, VALIDATION 2024-01-01..2026-11-12 (1047 days). Funding: Bybit v5 linear history for 59 of 60 coins (SHIB not found under SHIB/1000SHIB/10000SHIB, charged by the flat rule); a real record exists for 77-81 % of held coin-days, the rest (before a perp existed, SHIB) take the flat 0.01 %/8 h charge against longs, nothing credited to shorts. Costs: 2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 per round trip. Placebo: 1000 draws each (combined = random direction per run; single side = random start date).

## Main table (as pre-registered)
Returns are fractions of equity, additive over days, NOT capped: the pre-registered sizing (1 % risk per coin, 60 coins) runs average gross exposure 1.3x to 10.8x (column "avg gross" below), so "ann. return" and "max DD" are in units of that leverage; max DD above 100 % means the additive curve fell by more than the starting equity, i.e. the book as sized is not survivable. Compare rules by Sharpe, not by raw return. "vs basket" = strategy VAL Sharpe AND mean both above the equal-weight buy-and-hold basket (Sharpe -0.05, -3.5 % a year: the basket lost, so beating it is easy).

"""
tail = """
## Reading
- Nothing reaches the CI gate: every combined book has a VALIDATION CI of the mean daily return straddling 0 (lower bounds -0.22 % to -1.67 %), and the one-sided p is 0.22-0.44 for all ten (BH rejects none). VALIDATION Sharpe is 0.02-0.48 (best combined: rule 5 ADX14, 0.48), never 1.0. DEV Sharpe is above 0 for all 10 combined books (0.43 to 1.23; 1.0 or more for rules 1, 2, 3, 5, 6, 8, 9, 10) but VALIDATION does not hold it.
- The long side carries it and the short side does not: long-only books are positive in VALIDATION for 9 of 10 rules (best: rule 9 GATED-TSM30 and rule 10 GATED-ADX14, Sharpe 0.85 each, placebo p 0.001, CI still crossing 0), while short-only books lose for rules 1, 4, 8, 9, 10 (the BTC-gated shorts are the worst: Sharpe -0.33 / -0.38 / -0.52). Survivorship flatters longs and hurts shorts, so the long side is an upper bound.
- The placebo is not the binding gate: 7 of 10 combined books beat the random-direction placebo (p <= 0.05; rules 2, 3, 5, 7, 8, 9, 10 at 0.002-0.044; rule 1 at 0.051). The signal has direction information; it is too small and too lumpy to clear the CI and Sharpe gates.
- Concentration: the best 5 coins make 38-92 % of VALIDATION profit for rules 1, 2, 3, 5, 7, 8, 9, 10 (rules 4 and 6: 205 % and 834 %, i.e. the other 55 coins lose), and the best 10 days exceed 100 % of VALIDATION profit for every rule (159-4176 %): without them the book is negative. Without the best 5 coins the annualised return is -25 % to +97 % (rule 3 stays +97 %, rule 4 -24.5 %, rule 6 -12.9 %).
- Per year: no rule is positive in every year. Rule 9 loses only 2025 (-11.5 %) and rule 2 only 2026 (-12.8 %); gross exposure 4.6x and 1.3x.
- Last 90 days (to 2026-11-12, sum of daily returns, leveraged units): rule 1 +63.8 %, 2 +7.5 %, 3 +0.6 %, 4 -469 %, 5 +110.7 %, 6 -13.7 %, 7 +329.9 %, 8 +65.5 %, 9 +95.8 %, 10 +85.6 %. Most trend books are positive now, but that is 90 days, not a validation; rule 4 -469 % is the weekly-rebalanced 90-day TSM on a sharp reversal.
- Rule 7 (MA 20/50) trades 1471 times a year at 9.7 days average hold with 10.8x gross: +129 % a year on Sharpe 0.17 is leverage and noise, not edge.

## Gates and descriptives (combined book)
"""
i = t.index("Gates (combined")
lim = """
## Limits
Survivorship (PRE_REG.md): long numbers are upper bounds, short numbers lower bounds. Spot prices stand in for perp prices. The sizing and the no-gross-cap rule are pre-registered and drive the leverage and drawdown figures; a gross-capped book would have a smaller return and drawdown at the same Sharpe (Sharpe is scale-free, so the verdict does not depend on it). One universe, one run, no tuning; seed 20261113.
"""
open(os.path.join(HERE, "RESULT.md"), "w", encoding="utf-8").write(head + t[:i] + tail + t[i:] + lim)
