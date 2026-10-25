# MTS-2026-10-03-0330Z-CLI-BLD-r4-htf-context
surface: CLI | role: BLD | model: claude-sonnet-5-5 | branch: fast-track | lanes: none | status: closed

## T0 contract (quoted)
(a) `MyTradingSys/research/_archive/loose_2026-10/WHY_ENGINE_SILENT_2026-10-03.md:47`: "| R4 | HTF context layer (separate layer, never a Tom filter): 4H/1D balance (Fabio S1), failed-breakout flag, OI delta from Binance openInterestHist | collection-only log for 14 days, then measure | daily row per state; report vs next-day range |"
    Cause #5 (:25): "No higher-timeframe context: the verdict chain never sees multi-day balance, failed breakout, OI".
(b) `balance(bars, i, N, k_bal=0.8, bin_size=50)` signals.py:183 returns `{"H": H, "L": L, "R": R, "poc": poc}` or None
    (R <= k_bal*sqrt(N)*ATR_N(i) AND |c[i]-poc| <= 0.25*R). It works on 1m bars only (contiguity t[i]-t[a]==(i-a)*60000,
    needs "fp"), so "4H/1D balance" = balance() on 1m bars with N=240 / N=1440. NOT directly callable on 4H klines.
(c) No OI source in repo: `open_interest` hits (quad_classify, mts_math, divergence_monitor, backtest_oi_delta_4state)
    only read snapshot JSON fields; none calls openInterestHist. Built here (`/futures/data/openInterestHist`, period 1h).
(d) Log dir `MyTradingSys/research/htf_context/` (new, not imported by any live process; not gitignored).

## Built (new files only)
- `MyTradingSys/backtest/layers/fabio/htf_context_live.py` (writer; `--once` / `--loop`, `--out-dir`).
- `MyTradingSys/backtest/layers/fabio/test_htf_context_live.py` (15 tests; pre-change: ImportError, module absent).
- Output: `research/htf_context/<YYYY-MM-DD>.jsonl` (row per 4H close, the 00:00 close lands in the day just ended),
  `<date>_summary.json` {date, open, close, high, low} rewritten each cycle.
- Row: {timestamp, bal_4h, bal_1d, failed_breakout, oi_delta_1h_pct}. Idempotent per close. OI error / no bars -> no row.

## DEVIATIONS (flag; none tuned)
1. Kline bars have no footprint: one-bin fp at floor(hlc3/10)*10 per 1m bar -> H/L/R exact, poc approximate.
2. N=1440 for 1D is NO-SOURCE (24 h of 1m bars; the 4H N=240 is a spec grid value).
3. failed_breakout = probe (1m close beyond prior-4H-close balance H/L) then last close of the 4H window back inside; no
   absorbed condition, no 5-bar limit (model B has both). No side field (not in the brief).
4. Data is public mainnet USD-M market data (as live_runner_cli does); testnet has no openInterestHist. Read-only.
5. Summary is a separate rewritten file, not an appended line in the jsonl.
6. Rows 12:00/16:00/20:00Z of 10-02 were backfilled after the 00:00Z-10-03 row, so the file is not time-ordered.
7. No persistent process started (loop mode exists; running it is a supervisor/operator step).

## Finding
S1 verbatim at N=240 on BTCUSDT 1m bars: over the last 1260 closes, 4 pass the range test, 0 pass the POC band
(min R/(0.8*sqrt(N)*ATR) = 0.96, median 1.67). bal_4h/bal_1d will be null most of the time. Not tuned (provenance).

## Gate
`run_all_tests.py --quick`: ALL TESTS PASSED. T4: runtime 0.84 s for one 4H cycle.
