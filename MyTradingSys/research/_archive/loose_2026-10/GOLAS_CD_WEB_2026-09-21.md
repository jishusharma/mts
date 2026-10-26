> Superseded by MyTradingSys/items/B063_divergence.md (2026-09-22). Retained for history.

# GOLAS C and D - WEB RESEARCH

Date: 2026-09-21T18:20Z
Session: MTS-2026-09-21-1328Z
Author: coordinator (this session, web search available)
Purpose: reinforce sections D (GOLAS-C) and E (GOLAS-D) of
DIVERGENCE_AUDIT_AND_RESEARCH.md, which were UNVERIFIED-WEB in that doc.

## METHOD GATE

Question: consensus on divergence tuning for BTC; standard backtest
methodology for signal-study on crypto.
Methodology: search for disclosed-parameter backtests, institutional
research notes, peer-reviewed methodology. Reject marketing.
Source tiers pre-committed: T1/T2 for predictive claims, T3 for
practitioner parameter claims, REJECT for unattributed claims.

## GOLAS-C - BTC TUNING

| Item | Finding | Tier |
| RSI divergence | 14-period RSI, divergence window 5-30 bars, practitioner consensus | T3 |
| MACD divergence | 12/26/9 standard, histogram-based divergence read | T3 |
| CVD divergence | Exchange material treats CVD as flow gauge; divergence rule is practitioner vocabulary | T2 existence, T3 rule |
| OI divergence | No Tom basis; practitioner-only; dictionary hit count 0 | T3 |
| Volatility scaling | ATR-normalized thresholds recommended over absolute | T3 |
| BTC structure | 24/7 tape, 8h funding windows, weekend liquidity thinner; weekend divergence flagged noisier | T3 |
| Filter rules | Volume confirmation, RSI midline, higher-TF context | T3, none validated |

No institutional backtest of divergence edge on BTC was found. Every
predictive claim above is T3.

## GOLAS-D - BACKTEST METHODOLOGY

| Item | Finding | Tier |
| Walk-forward analysis | Standard for time-series strategy validation | T1 |
| Purged K-fold + embargo | Prevents label leakage in overlapping horizons | T1 |
| Label overlap | Adjacent rows non-independent when horizons overlap | T1 |
| Multiple testing | BH FDR at q=0.10 accepted default; Bonferroni conservative | T1 |
| Signal-study vs event-study | MTS verdict path is event-study | T2 |
| Out-of-sample | 70/30 or rolling re-fit; 9-day sample too small for either | T1 |

T1 sources cited as named methods and authors, not URLs:
- Pardo, 2008, Design Testing and Optimization of Trading Systems.
- Lopez de Prado, 2018, Advances in Financial Machine Learning.
- Benjamini and Hochberg, 1995, FDR controlling procedure.

## IMPACT ON BACKTEST_METHOD_2026-09-21.md

- Section 5 (traps) listed "label leakage" and "multiple testing". Both
  are correct and now have T1 backing.
- Section 4 (validation gates) pre-registered FDR q=0.10. Correct.
- New constraint not in that doc: with a 9-day snapshot window, no
  claim can be made that survives walk-forward. Any backtest from this
  data is descriptive, not predictive. This should be stated in the
  backtest doc as a hard limit.

## HARD LIMIT

Every GOLAS-C claim is T3 or lower. To promote any of them to a system
rule requires T1/T2 evidence that does not currently exist on disk.

END