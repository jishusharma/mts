# prereg_gate.py output, long window, 2026-11-04 (before any return; n = distinct event-days, pooled with-trend, signal entry, m = 48 incl. the proxy arm, cost 0.14 %, sd OURS)

| Cell | days | sd (%) | MDE + cost | max plausible | n needed | gate |
|---|---|---|---|---|---|---|
| 15m none (optimistic bound) | 580 | 0.9 | 0.294 | 0.30 | 537 | PASS |
| 15m rsi | 413 | 0.9 | 0.322 | 0.30 | 537 | BLOCK |
| 30m none | 331 | 1.3 | 0.434 | 0.30 | 1120 | BLOCK |
| 30m rsi | 247 | 1.3 | 0.481 | 0.30 | 1120 | BLOCK |
| 1h none | 196 | 1.9 | 0.699 | 0.30 | 2393 | BLOCK |
| 1h rsi | 144 | 1.9 | 0.792 | 0.30 | 2393 | BLOCK |

Only the unconfluenced 15m bound passes; no confirmatory (rsi / div / proxy) cell does. The long-window DEV table is DESCRIPTIVE; verdict ceiling INCONCLUSIVE (underpowered).
