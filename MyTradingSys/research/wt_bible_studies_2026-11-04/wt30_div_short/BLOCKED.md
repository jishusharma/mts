# BLOCKED: power gate (2026-11-06), wt30-lower-high-divergence-short
`prereg_gate.py --n 183 --sd 1.8 --cost 0.14 --m auto --new-cells 14` -> m 234, MDE 0.604 + cost 0.14 = 0.744 > 0.30 plausible, n needed 2611 event-days; DEV has 183 (best case, unconditional). n=118 (largest marginal cell) also exit 1.
No returns were computed. Unblock only by more independent event-days (more symbols with full DEV coverage, e.g. ETH/SOL 1m DEV data, ~14x BTC events needed) or a lower repo-wide m. `study.py --pass dev` is written and ready to run as a descriptive table.
