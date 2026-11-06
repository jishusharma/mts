# RESULT: H3 NY-open low (set at open+120..150, held >= 30 min), 10-symbol DEV count (BLOCKED)

Context:
- Regime: none, count-only; no regime filter and no returns read.
- Phase: NY-day low over [00:00Z, open+180 min) set at open+120..150 min and held through open+180 (OURS rule of `../h3_ny_open_low_2026-10/BLOCKED.md`); DEV 2022-01-01..2024-06-30 (SOURCED `MyTradingSys/backtest/splits.py:20`).
- Session: NY (open 13:30 UTC in US DST else 14:30, SOURCED `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:60-64`).
- Entry: none; no entry or outcome is defined or read.
Regime mix: NOT_IN_DATA (count-only, no regime tagging run; standard BTC 130-week DEV baseline is bull 25 (19%) | bear 0 (0%) | range 105 (81%), SOURCED `MyTradingSys/research/bb_range_retest_2026-11-04/RESULT.md:1`)

| Symbol | usable days | events | Notes |
|---|---|---|---|
| BTCUSDT | 650 | 35 | SOURCED `MyTradingSys/research/h3_ny_open_low_2026-10/BLOCKED.md:8` (n=35) & OURS |
| ETHUSDT | 650 | 28 | OURS `count_10sym.py` |
| SOLUSDT | 648 | 34 | OURS `count_10sym.py` (2 days dropped: missing bars) |
| XRPUSDT | 648 | 22 | OURS `count_10sym.py` (2 days dropped: missing bars) |
| LTCUSDT | 648 | 22 | OURS `count_10sym.py` (2 days dropped: missing bars) |
| BNBUSDT | 650 | 27 | OURS `count_10sym.py` |
| ADAUSDT | 650 | 21 | OURS `count_10sym.py` |
| DOGEUSDT | 650 | 27 | OURS `count_10sym.py` |
| AVAXUSDT | 650 | 23 | OURS `count_10sym.py` |
| LINKUSDT | 650 | 24 | OURS `count_10sym.py` |
| **Pooled (10 symbols)** | **6494** | **263** | OURS sum across 10 symbols DEV |

All 10 symbols DEV 1m klines are on disk (F:/MTS/data/tom_raw/klines). Pooled n = 263 across 10 symbols DEV (BTC n=35 matches `research/h3_ny_open_low_2026-10/BLOCKED.md:8`). SOL/XRP/LTC drop 2 gap days each (648 usable days vs 650). Only bar times and lows were read; no returns or price outcomes were read.

Gate: `python scripts/dev/prereg_gate.py --n 263 --sd 1.5 --sd-source research/h3_ny_open_low_2026-10/BLOCKED.md --cost 0.14 --m auto`
`n 263 sd 1.5 m 223 z_holm 3.690 MDE 0.419 R + cost 0.14 = 0.559 vs max plausible gross 0.3; n needed 1804` (SOURCED `scripts/dev/prereg_gate.py` run output)
Exit code: 1 (BLOCK: do not freeze)

VERDICT: BLOCKED. Next: END: 1804 events needed vs 263 pooled on 10 symbols DEV; H3 is underpowered by ~6.8x; a wider event definition or additional sessions/symbols must be pre-registered as a new card.
