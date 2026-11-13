UNVERIFIABLE

# Blind Review: `h3_ny_open_pooled_2026-11` and `h3_ny_open_10sym_2026-11`

## 1. Claim Recount Table

| Claim | Claimed Value | Recounted Value | Status |
|---|---|---|---|
| `h3_ny_open_pooled_2026-11/BLOCKED.md:6` BTC DEV `n` | `35` | `NOT_IN_DATA` (`F:/MTS/data/tom_raw` absent on this machine) | UNVERIFIABLE |
| `h3_ny_open_pooled_2026-11/BLOCKED.md:8` pooled upper bound `n` | `70` (`2 x 35`) | `70` (`2 * 35 = 70` arithmetic; base `35` unverifiable) | MATCH |
| `h3_ny_open_pooled_2026-11/BLOCKED.md:10` `prereg_gate.py --n 70 --sd 1.5 --cost 0.14 --m auto` | `m 220 z_holm 3.687 MDE 0.812 R + cost 0.14 = 0.952 vs max plausible gross 0.3; n needed 1801` (exit 1) | `m 248 z_holm 3.717 MDE 0.817 R + cost 0.14 = 0.957 vs max plausible gross 0.3; n needed 1825` (exit 1) | MISMATCH |
| `h3_ny_open_10sym_2026-11/RESULT.md:12-21` per-symbol `usable days` / `events` (10 symbols) | BTC 650/35, ETH 650/28, SOL 648/34, XRP 648/22, LTC 648/22, BNB 650/27, ADA 650/21, DOGE 650/27, AVAX 650/23, LINK 650/24 | `NOT_IN_DATA` for all 10 symbols (`count_10sym.py` run on this machine) | UNVERIFIABLE |
| `h3_ny_open_10sym_2026-11/RESULT.md:22` pooled `usable days` / `events` | `6494` / `263` | `pooled_n 0` (`F:/MTS/data/tom_raw` absent; table column sums `6494` and `263` are arithmetically consistent) | UNVERIFIABLE |
| `h3_ny_open_10sym_2026-11/RESULT.md:27` `prereg_gate.py --n 263 --sd 1.5 --cost 0.14 --m auto` | `m 223 z_holm 3.690 MDE 0.419 R + cost 0.14 = 0.559 vs max plausible gross 0.3; n needed 1804` (exit 1) | `m 248 z_holm 3.717 MDE 0.421 R + cost 0.14 = 0.561 vs max plausible gross 0.3; n needed 1825` (exit 1) | MISMATCH |

Note on `prereg_gate.py` mismatches: `--m auto` counts existing studies in the repo, which grew from `220`/`223` to `248`; both gates still exit `1` (`BLOCK: do not freeze`).

## 2. Look-Ahead Hunt

- Both studies are **count-only** pre-registration power checks; no entry, exit, or return is computed (`h3_ny_open_pooled_2026-11/BLOCKED.md:3`, `h3_ny_open_10sym_2026-11/RESULT.md:4,7`, `h3_ny_open_10sym_2026-11/count_10sym.py:1-2`).
- In `count_10sym.py:17-29`, `day_event(date, lows)` uses 1m bar `open_ms` timestamps over `[00:00:00Z, ny_open_utc(date) + 180 min)` (`count_10sym.py:22-24`) via `ny_open_utc` (`MyTradingSys/backtest/layers/fabio/v3/day_gates.py:60-64`).
- `low_t = min(ts, key=lambda t: (lows[t], t))` (`count_10sym.py:27`) finds the first 1m bar achieving the window minimum low, and `120 <= off <= 150` (`count_10sym.py:29`) checks that the low was set at `open+120..150 min` and held through `open+180 min`.
- No look-ahead bug exists in the count itself because no trading decision or outcome is simulated.

## 3. Fee / Slippage Hunt

- No backtest, trade simulation, or return calculation exists in either folder (`RESULT.md:4,7`, `count_10sym.py:2`).
- The only cost parameter is `--cost 0.14` passed to `scripts/dev/prereg_gate.py` (`BLOCKED.md:9-10`, `RESULT.md:26-27`), representing a round-trip cost assumption in R-multiples rather than a per-side fee/slippage model.
