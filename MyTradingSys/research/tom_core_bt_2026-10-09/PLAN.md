# Tom core backtest on the v2 extracts: plan and phase 1 (2026-10-09)

Ask: NEXT_SESSION.md task 3 (T082 re-run on the fixed volume profile / naked POC, profiles anchored at pivots).
Inputs: the 9 Tom v2 extracts in `extracts/v2/tom/`, `research/vp_pivots_2026-10-09/SOURCES.md`, `backtest/layers/FORMULAS.md` section 18.
Phase 1 (this file) = rule inventory, data check and phase order. No code, no numbers. Budget hold: phases 2-4 wait for the weekly reset (Sun 2026-10-11 22:30 IST).

## 1. Data on disk (JIS-NB, checked 2026-10-09)
- BTCUSDT USD-M 1-minute klines: `Dumps/backtest/raw_1m_2022/klines` (monthly, 2022-01 .. 2025-08, 44 files) + `Dumps/backtest/raw/klines` (daily, 2025-09-01 .. 2026-10-07, 56 files). Enough to build 5m / 15m / 1h / 1d bars and volume profiles (FORMULAS 8, 18.1).
- `Dumps/backtest/raw/aggTrades`: empty. So no trade-side volume: footprint, delta, CVD, finished/unfinished auction cannot be backtested. Every rule that needs them is out of scope until aggTrades are fetched (desktop, `fetch_binance_archive.py`).

## 2. Rule inventory: what a naked BTC OHLCV backtest can test
Rule ids are the section 3.7 ids in each extract. "Testable" = every input computable from 1m klines; NO-SOURCE parts are measurement choices, flagged in FORMULAS, never tuned.

| Rule | Claim (short) | Testable on OHLCV | NO-SOURCE parts | Phase |
|---|---|---|---|---|
| SOURCES Q1 + R-oPyU-1 | profile from last major high to last major low; price returns to the high-volume area | yes (FORMULAS 18.4 A1) | pivot width n, size k, bin width | 2 |
| R-QClP-2 | target = next high-volume node, just below it | yes | "slightly below" distance | 3 |
| R-QClP-3 | stop below last high-volume station / last swing low | yes | buffer, swing width | 3 |
| R-5Ljf-4 | counter long at VAL of a balance after re-acceptance, stop below PDL, target POC then VAH | yes without the footprint confirmation | re-acceptance test, balance vs trend classifier | 3 |
| R-5Ljf-5 | entry back at the setup's highest-volume price | yes | setup window | 3 |
| R-5Ljf-7 | profile POC sits mid candle bodies, VA edges at body top/bottom | yes (a measurement, not a trade) | body-cluster definition | 2 |
| R-Of_w-5 | trend profile -> POC is the reference; balance -> VAH/VAL | yes once a classifier exists | classifier | 4 |
| R-Of_w-1 / R-Of_w-2 | first 30 min of the NY cash open; open width -> trend vs counter | shape yes | applying the NY cash clock to BTC is NO-SOURCE (Tom never does) | not planned |
| R-QClP-1 | VPOC at the top + single print -> long bias | VPOC yes; single print needs TPO from 30m bars | "at the top" fraction | 4 |
| R-oPyU-2, R-oPyU-4, row 17 of 5Ljf | exhaustion / finished auction / selling surplus / CVD | no (needs aggTrades) | - | blocked |
| R-Of_w-7 | no speed of tape | design rule, respected | - | - |

Statistics rules that bind every phase (Tom's words, not choices): report win rate together with average R:R and EV per trade (R-5Ljf-8, R-QClP-5: break-even = 1/(1+R:R), EV = p x R:R - (1-p)); report the longest losing streak (5Ljfwvtktek row 3); a verdict needs at least 300 events per variant (Of_wlv3xaZo "well over 300 trades", 5Ljfwvtktek "250 300 trades for each strategy"); split results by bull / bear / sideways phase (ShYS R-ShYS-5, Of_wlv3xaZo row 7). The phase labels themselves are NO-SOURCE (no definition in any extract).

## 3. Phases
1. (done, this file) Inventory, data check, order.
2. (done 2026-10-09, `PHASE2_RESULT.md`: no anchor has an edge, none beats placebo) Pivot-anchored profile touch study exactly as FORMULAS 18 (build `backtest/vp_pivot_probe.py` + tests whose expected numbers are the worked examples in 18.1-18.7; Sonnet implements, tests first). Families session, prior_day, prior_week, weekly, A1(n,k), A2(n,k) and the 18.6 placebo. Add the R-5Ljf-7 body-midpoint vs POC measurement as a side table. Output: per family hit / stop / timeout, mean net R with day-block bootstrap CI, longest losing streak, split by year.
3. Trade rules on the winning anchor from phase 2: R-QClP-2/3 targets and stops, R-5Ljf-4/5 counter long at VAL. Needs FORMULAS entries first (target = next node above, stop = node below / PDL).
4. Profile-shape classifier (trend vs balance) and R-Of_w-5 / R-QClP-1. Needs a sourced definition; if none is found it stays NO-SOURCE and is reported as a varied choice.
Footprint rules wait for aggTrades.

## 4. Stop point for this session
Phase 2 is code + tests + a multi-year run on 5m bars: token-heavy, so it is not started before the reset. Nothing here changes the live system.
