PASS

Blind re-derivation of `MyTradingSys/research/v_recovery_low_sweep_2026-11-04` from `PRE_REG.md`, `counts.json`, `research_kit.py`, and `scripts/dev/prereg_gate.py` (via `recompute.py`) matches all headline claims in `RESULT.md`.

## Claim Table

| Claim | Recomputed | Stated | Source (`file:line`) | Status |
|---|---|---|---|---|
| Headline verdict | `INCONCLUSIVE` (underpowered; power gate `BLOCK`, exit 1; OURS via `recompute.py`) | `"VERDICT: INCONCLUSIVE (underpowered)"` | `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/RESULT.md:3` | MATCH |
| DEV event count | `435` (SOURCED from `counts.json`) | `"435 events"` | `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/counts.json:2`, `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/RESULT.md:3` | MATCH |
| DEV event-days (`n`) | `195` (SOURCED from `counts.json`) | `"195 event-days"` | `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/counts.json:3`, `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/RESULT.md:3` | MATCH |
| Power gate (`4h`/`24h`/`72h`) | Exit 1 (`BLOCK`) for `n=195`, `m=224`, `z_holm=3.691`, `cost=0.14` (`TAKER_RT_PCT`), `MDE+cost = 0.497 / 0.951 / 1.535 > 0.30` (OURS via `recompute.py`) | `"prereg_gate exit 1 at 4h/24h/72h"` | `MyTradingSys/backtest/research_kit.py:21`, `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/PRE_REG.md:23`, `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/RESULT.md:3` | MATCH |
| Forward returns / mean / CI | None computed (`--pass dev` not run; no `dev.json`; VAL/HOLDOUT unopened; SOURCED `PRE_REG.md`) | `"No forward returns or CI computed; VAL not opened; HOLDOUT never loaded"` | `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/PRE_REG.md:24`, `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/RESULT.md:3` | MATCH |
| Regime mix | `NOT_IN_DATA` (SOURCED `PRE_REG.md`) | `"Regime mix: NOT_IN_DATA (descriptive study, no regime spec frozen)"` | `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/PRE_REG.md:24`, `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/RESULT.md:2` | MATCH |

## Notes

- Raw kline paths (`F:/MTS/data/dev_ext_2019_2021` and `F:/MTS/data/bigtrade` in `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/study.py:19`) are not present on this machine, so `counts.json` (`events=435`, `event_days=195`) was parsed directly rather than regenerated from 1m bars.
- Recomputing `scripts/dev/prereg_gate.py` with `--m 224` (the Holm family size on 2026-11-06 in `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/PRE_REG.md:23`) reproduces `z_holm = 3.691`, `MDE+cost = 0.497 / 0.951 / 1.535`, and `n needed = 970 / 5013 / 14829` identically. Running `--m auto --new-cells 3` as of 2026-11-14 gives `m = 251`, `z_holm = 3.720`, `MDE+cost = 0.499 / 0.956 / 1.544`, `n needed = 983 / 5077 / 15019` (all `BLOCK`, exit 1).
