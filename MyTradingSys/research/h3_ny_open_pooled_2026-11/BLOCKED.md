# H3 NY-open new-low-holds, pooled BTC+ETH DEV: BLOCKED before freeze (END)

Card route-h3-ny-open-more-symbols. No PRE_REG frozen, no outcome read, no strategy run, no VALIDATION/HOLDOUT read.

- Context: Regime n/a (count-only) / Phase DEV 2022-01-01..2024-06-30 (splits.py) / Session NY / Entry: NY open.
- BTC DEV n = 35 (not 6): see ../h3_ny_open_low_2026-10/BLOCKED.md.
- ETH 1m DEV klines are not on disk (F:/MTS/data/tom_raw/klines is BTC only; DATA_MANIFEST.csv has no ETHUSDT-1m sha; fetch_binance_archive.py is BTC-only). No sha-checked loader exists, so ETH was not counted.
- DECISION (OURS): use the upper bound n = 2 x 35 = 70 (ETH cannot exceed BTC-like day count, 650 NY days each; same event rule). If the bound blocks, the true pooled n blocks too.
- prereg_gate.py --n 70 --sd 1.5 --cost 0.14 --m auto (sd two-point, OURS):
  `n 70 sd 1.5 m 220 z_holm 3.687 MDE 0.812 R + cost 0.14 = 0.952 vs max plausible gross 0.3; n needed 1801` -> exit 1 BLOCK.
- END: pooling two symbols reaches at most n~70 vs 1801 needed. H3 needs ~25x more events (more symbols/sessions, a wider event pre-registered before seeing outcomes) or a lower-variance event definition; neither reaches n>=30 usefully. test_pooled_count.py not written: no loader to test (DECISION OURS, an unused loader would be dead code).