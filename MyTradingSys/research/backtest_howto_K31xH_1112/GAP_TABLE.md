# GAP_TABLE: K31xH-6g9Vc (How to Backtest, Long & Short Ep. 12) vs our backtests

Steps S1-S12 from EXTRACT.md (SOURCED). Our-practice column cites repo files (OURS reading). Status: DONE = we do it at least as strictly; PARTIAL = we do part; SKIPPED = we do not; N/A = does not apply to BTC perps/spot.

| Step | What the video teaches | Our practice (file) | Status | What we should do / learn |
|---|---|---|---|---|
| S1 | Hypothesis -> method -> code -> run -> analyse log | PRE_REG before any result: `MyTradingSys/research/btc_orderflow_map_1112/PREREG.md`; verdict log `scripts/dev/verdicts.py` | DONE (stricter) | Nothing; we freeze the hypothesis before the run, the video does not. |
| S2 | Narrow it (long-only) | Signed arms fixed in PREREG ("Trade side" column) | DONE | Keep. |
| S3 | LLM writes the strategy code, defaults accepted | We write code with Claude too, but new tests must fail on pre-change code (CLAUDE.md Gates); formulas from `MyTradingSys/backtest/layers/FORMULAS.md`, never from code | DONE (stricter) | Lesson: LLM defaults are hidden parameters; ours are labelled SOURCED/OURS. |
| S4 | Fixed size, fills on bar close | Entry = next 1m bar open after the event bar (PREREG "Entry"); fill model `MyTradingSys/backtest/layers/fabio/v3/fill.py` | DONE (stricter) | Bar-close fill on the signal bar itself is optimistic; we fill on the next open. |
| S5 | Equity vs buy-and-hold; long vs short contribution | Placebo with same hour histogram and same long/short count (PREREG "Placebo"); long/short not always split in RESULT tables | PARTIAL | Add a long-side vs short-side line to every RESULT (cheap, descriptive). Buy-and-hold baseline is weaker than our placebo. |
| S6 | Sanity-check log entries against the chart before metrics | Indicator values are checked on TradingView (VERIFIED-TV marks in FORMULAS.md); trade fills are not spot-checked against a chart | PARTIAL | Add: print 5 latest trades with entry/exit bars and match them to the 1m klines before any metric (a "log sanity" step). Card filed. |
| S7 | Fixed metric list computed from the log | Per-cell n, mean net, sd, t, share positive, session, regime mix (PREREG "Per cell report") | DONE | Keep; ours is fixed before the run. |
| S8 | Year x month P&L table | `Regime mix:` and session split; no per-year row in most RESULTs | PARTIAL | Add a per-year line: one bad year (his 2021) can hide in a pooled mean. |
| S9 | Back-adjust continuous futures | BTC perps have no expiry roll; spot/perp klines need no stitching; funding is netted instead (FORMULAS.md line ~358) | N/A | Applies only if we ever test CME BTC futures or dated Deribit futures. |
| S10 | Pick parameters by best return | Forbidden in ours: frozen params, Holm/Bonferroni over repo-wide m (`scripts/dev/prereg_gate.py`), DEV/GAP/VALIDATION/HOLDOUT (`MyTradingSys/backtest/splits.py`, `SPLIT_ALIGNMENT_2026-10-17.md`) | DONE (we reject this step) | Lesson: his S10 is the overfitting path; his own S11 admits no OOS split. |
| S11 | No IS/OOS or walk-forward in the tool; export two periods | DEV, 30-day GAP, VALIDATION, sealed HOLDOUT with read log (PREREG "Splits") | DONE (stricter) | No walk-forward yet (we use one fixed split). Walk-forward is a later option for a cell that passes VALIDATION; not filed (OURS: phase-first rule prefers testnet-forward). |
| S12 | Backtest is no guarantee | Testnet-forward after a LEAD/PASS (phase-first method) | DONE | Keep. |

## What the video does NOT do that we do (OURS, from EXTRACT.md "Not in the video")
- Fees and slippage: absent in the demo; ours nets 0.10 % round trip + slippage (FORMULAS.md lines 352-358). A fee-free 118 % on 331 trades over 5.9 years would lose about 331 x fee-rt.
- Placebo / random-entry baseline, multiple-testing correction, minimum n, pre-registration: absent; ours has all four.

## Net for us (OURS)
- Two cheap additions: (1) a trade-log sanity print vs 1m klines before metrics, (2) per-year and long/short split lines in RESULT tables.
- Nothing in the video should loosen our gates; S10 is the anti-pattern.
