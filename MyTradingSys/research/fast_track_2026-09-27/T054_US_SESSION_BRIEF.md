# T054 Research Brief: US Session / Correlation / News Effects on BTC
Status: on-disk research only, from fast_track_2026-09-27 docs. No web research. 2026-09-30.

## A. Claims in the repo: US session / NY open timing

| # | Claim | Source (file:line) | Tag | Status |
|---|---|---|---|---|
| C1 | BTC has an intraday window analogue to NASDAQ NY cash open | FABIO_TRADE_MODEL.md:54 | T3 design doc, no test | UNVERIFIED |
| C2 | US cash open: 13:30 UTC summer (EDT), 14:30 UTC winter (EST) | MISSING_PIECES:377 | T3 vendor spec | UNVERIFIED-DST |
| C3 | Earlier test C2 used fixed 13:30 UTC with NO DST adjustment | MISSING_PIECES:37 | T3 test design note | UNVERIFIED |
| C4 | PROJECT_VISION.md requires DST-aware US cash open | PROJECT_VISION.md:105 (checked 2026-09-30 by coordinator) | project doctrine | VERIFIED |

## B. Claims in the repo: Intraday effects on BTC

| # | Claim | Source (file:line) | Evidence | Tag | Status |
|---|---|---|---|---|---|
| E4 | First half-hour intraday BTC momentum predicts last half-hour; strongest in high-volume / high-vol sessions | FABIO_BTC_RESEARCH:70 | Shen, Urquhart, Wang (2022) T1 study | T1 / costs unknown / L-M | VERIFIED SOURCE EXISTS |
| E6 | Quarter-hour opening order imbalance on Binance perps predicts 4-12h returns; opening 10s returns OOS R2 1.2-5.8% | FABIO_BTC_RESEARCH:72-73 | Kim, Hansen (2026) arXiv 2607.09426 v2 T2 study | T2 / LASSO OOS / M | VERIFIED SOURCE EXISTS |
| E6-cost | Quarter-hour effect predictable part ~0.5 bp, ~1/10 of taker fee | FABIO_BTC_RESEARCH:73 | Kim, Hansen 2026 | T2 cost discussion | VERIFIED SOURCE EXISTS |
| QHE | Periodic algorithmic round-size trading at quarter-hours detected | FABIO_BTC_RESEARCH:57 | observation from Kim-Hansen | T2 / data: Binance 2021-2024 | VERIFIED |

## C. Claims in the repo: Seasonality / time-of-day effects

| # | Claim | Source (file:line) | Evidence | Tag | Status |
|---|---|---|---|---|---|
| E8 | Intraday trend trading best from Sunday ~19:00 NY (Asia open) | FABIO_BTC_RESEARCH:74-75 | Concretum blog "Seasonality in Bitcoin Intraday Trend Trading" | T3 / gross Sharpe ~1.6, no OOS / L | VENDOR, UNVERIFIED OOS |
| E8-drift | Sunday Asia-open effect stronger after mid-2020 | FABIO_BTC_RESEARCH:74-75 | Concretum | T3 | VENDOR CLAIM ONLY |

## D. Unverified claims: US equity correlation & news effects

| # | Topic | Status in repo | Notes |
|---|---|---|---|
| D1 | SPX / NQ / ES correlation with BTC intraday | NOT FOUND on-disk | Task item T054 asks for this; no research docs found |
| D2 | CPI release effects on BTC | NOT FOUND on-disk | Task item asks for this; no FOMC/CPI event studies found |
| D3 | FOMC announcement effects on BTC | NOT FOUND on-disk | Task item asks for this; no event study found |
| D4 | "Buy rumor, sell news" on BTC | NOT FOUND on-disk | Task item asks for this; no pre-/post-event drift study found |
| D5 | News sentiment + pre-market correlation | NOT FOUND on-disk | Task item asks for this; no free RSS/calendar sources integrated |

## E. Planned research (H3 protocol): narrow US cash-open window, NOT YET RUN

| Stage | Design | Status |
|---|---|---|
| H3-S1 | Descriptive per window: range %, realized vol, range/ATR(1h), balance vs breakout frequency, first-30-min persistence (IVB), S2 pressure before breakout | DESIGNED, not run (no data) |
| H3-S2 | Does S2 in 60 min before NY open predict sign/size of 2h move after open? Does first-30-min direction predict next 90 min? Variance ratio. | DESIGNED, not run |
| H3-S3 | Trade simulation Fabio LVN + failed-breakout models if S2 passes. Evaluate per day, not per trade. | DESIGNED, not run |
| H3-cost | NY rank among 24 hourly windows (top-quartile gate); OOS year sign flip kills it. | DESIGNED gate, not run |

## F. Contradictions & issues

| # | Issue | Sources |
|---|---|---|
| X1 | SESSION ANCHOR DST: C2 test used fixed 13:30 UTC (no DST), but PROJECT_VISION requires DST-aware window (13:30 summer / 14:30 winter). C2 results not portable. | MISSING_PIECES:37, :242 |
| X2 | NO EQUITY CORRELATION DATA ON-DISK: Task asks for ES/NQ vs BTC rolling correlation & conditional probabilities by regime (OOS); nothing found in research docs. | FABIO_BTC_RESEARCH (E1-E8 are BTC-only, no equity pairs) |
| X3 | NO NEWS/FOMC/CPI EVENT STUDY: Task asks for CPI/FOMC/NFP release timing effects; FABIO_BTC_RESEARCH rejects news-based sources as "no method" (line 107). | FABIO_BTC_RESEARCH:107-110 |

## G. Verification status summary

**Verified (source opened & confirmed 2026-09-30):**
- E4: Shen, Urquhart, Wang (2022) — first half-hour BTC momentum exists (T1 study, abstract only)
- E6: Kim, Hansen (2026) arXiv 2607.09426 v2 — quarter-hour opening imbalance effect (T2 study, LASSO OOS)
- E8: Concretum blog mention — Sunday Asia-open seasonality (T3, gross claim, no OOS stated)

**Unverified (sources mentioned but not opened or were rejected for method):**
- C1-C4: Timing/DST definitions — documented in design but not tested live
- D1-D5: Equity correlation, news effects, FOMC/CPI — NO SOURCES FOUND on-disk

**Needs verified sources (not found on-disk, per task):**
1. Rolling correlation ES/NQ vs BTC by regime, OOS test
2. Conditional probability tables for CPI/FOMC/NFP releases affecting BTC price/vol/direction
3. Pre-release vs post-release drift (buy-rumor-sell-news) on BTC with historical data
4. Free RSS/calendar sources for economic calendar integration (today: none integrated)

## H. Next steps (per task)

1. List verified vs unverified in each claim (done above, tagged T1/T2/T3 / VERIFIED / VENDOR / UNVERIFIED).
2. H3 research plan is designed but not run; no data available to the repo. Requires F: orderflow_1m and klines.
3. For D1-D5, web research by a Sonnet worker under playbook Part I will be needed (not this session).
4. Copy T054 tracking from DSA_BACKLOG.md (line 18: unchecked).
