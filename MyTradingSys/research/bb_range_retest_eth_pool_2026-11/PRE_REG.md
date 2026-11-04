# PRE_REG: Bollinger band retest-LEVEL arm, BTCUSDT + ETHUSDT pooled (frozen 2026-11-04, before any return was computed)

Card `ms-bb-range-retest-eth-pool`. The source study `bb_range_retest_2026-11-04` (BTCUSDT spot) is INCONCLUSIVE: prereg_gate BLOCKed all 9
family cells (146-186 days vs 478-1783 needed). This study re-runs the SAME frozen arm (rule, grid, family, survivor rule; no retuning) on
BTCUSDT and ETHUSDT USD-M futures 1m and pools them, to see whether pooled days clear the gate and whether net stays negative. Code
`study.py` reuses the source study by path (events, level-arm fill, bracket, session-range tag, cell stats). Tests `test_pool.py`
(4 tests; on the stub all 4 failed with NotImplementedError / missing dev_cells.csv, then the 3 loader tests passed before any return).

verdicts.py check "bollinger range retest" exits 1 on bb_range_to_range / bb_long_window FAILs (signal entry, BTC spot). Why this is a
different hypothesis: those kill_scopes say "nothing about other symbols" and cover the signal entry; this run is the level arm, whose
family is INCONCLUSIVE (not killed), on ETHUSDT plus a BTC futures reproduction row.

## Parameters (every one labelled; all copied from the source PRE_REG unless marked new)

| Parameter | Value | Label |
|---|---|---|
| Bands, signal, re-entry (M = 10), touch (k {0.25, 0.5, 1.0} x ATR(14), N = 10), exit (opposite band, stop 0.5 x distance, 24-bar time-out) | as the source PRE_REG | OURS |
| Range gate | research_kit regime == "range" as-of the signal-bar close; context bars = each symbol's own SPOT 1d history from 2017 (F:/MTS/Dumps/backtest/spot_2017), weekly = Monday buckets, monthly = calendar months (new: the futures files start 2022-01, too short for monthly RSI(14)) | band 60/40 SOURCED Malkan, SMA200 SOURCED-in-repo, spot-for-context OURS |
| Session, session-range tag | as the source PRE_REG (tag history starts 2022-01 here, so the first ~10 sessions per name are untagged) | OURS |
| Data | BTCUSDT and ETHUSDT USD-M futures 1m, F:/MTS/data/tom_raw/klines (new; the source used BTC spot) | OURS |
| Cost | 0.14 % round trip (research_kit.TAKER_RT_PCT, as the source; decides the verdict); second column at 2 x fees.BINANCE_TAKER = 0.10 % | SOURCED |
| Statistics | net = gross - cost; day-clustered SE with cluster = (symbol, UTC day of the fill bar) (new), 95 % CI = mean +- 1.96 SE | SOURCED research_kit; symbol-day cluster OURS |
| Confirmatory family | POOL x 15m x {asia, london, ny} x k grid, range gate, tagged, sides pooled = 9 cells, Holm m = 9 | OURS |
| Per-symbol cells | BTCUSDT and ETHUSDT family cells, Holm m = 9 each: descriptive, never a verdict | OURS |
| DEV survivor | as the source: n >= 30, >= 20 days, net > 0, Holm p < 0.05, tagged-range minus tagged-all-regime t >= 2 | OURS |
| BTC reproduction tolerance | REPRO_N_TOL: BTC futures n within 25 % of the shipped spot n per family cell, same net sign (test_btc_row_reproduces_shipped_n) | OURS |
| Windows | DEV only: signal-bar closes in [2022-01-01, 2024-07-01); the loader raises on an end after 2024-07-01 and never opens a later file. VALIDATION and HOLDOUT are not read in this study | SOURCED backtest/splits.py |
| Verdict ceiling | prereg_gate BLOCKs all 9 pooled cells (BLOCKED.md: 300-385 symbol-days vs 600-1944 needed), so FAIL is not available: best case INCONCLUSIVE | OURS |

## Power gate (scripts/dev/prereg_gate.py, run BEFORE any return; counts.csv POOL rows)

BTC futures counts reproduce the shipped spot counts (n 174-241 vs 175-244, within 3 %). Pooled days 300-385 per cell; every cell BLOCKs
(full output in BLOCKED.md). Regime mix of the DEV window (regime_mix_count.txt): BTCUSDT 130 weeks bull 25 (19%) | bear 0 | range 105
(81%); ETHUSDT 130 weeks bull 11 (8%) | bear 0 | range 119 (92%); POOL 260 weeks bull 36 (14%) | bear 0 (0%) | range 224 (86%) | n/a 0.

## What the result will say

1. RESULT.md first lines = `Regime mix:` line, then the verdict.
2. BTC reproduction row (futures vs shipped spot), then per-symbol and pooled family tables: n, days, fill rate, gross, net at 0.14 and 0.10, CI, Holm p, vs_ungated t.

## Context
Regime: range only, via research_kit.regime_tag (range gate research_kit) on each symbol's spot 1d context; compared against the all-regime arm.
Phase: none, because as the source study the entry itself is the phase (excursion beyond the band, re-entry close, retest of the band).
Session: asia / london / ny (confirmatory) and late (descriptive) via research_kit.session_tag of the signal-bar close, plus the OURS session-range tag.
Entry: return-to-band limit k x ATR (re-entry close inside the band, then touch of level +- k ATR within N bars; research_kit.retest_entry).

FROZEN_UTC: 2026-11-04T21:21:21Z
