# Layer integration: the 12 steps to live (pointers only, no rule text copied)

Stitched from LAYER_REBUILD_PLAN s2, PRE_REG_TEMPLATE, PROMOTION_PIPELINE, QUICK_ANSWERS:24, PROJECT_VISION:223-262,
PLUGIN.md (full stitch: `MyTradingSys/research/mts_doctor/LAYER_REALITY_2026-10-25.md:31-37`).

1. G0/G1 sources + verbatim-quote extraction: `MyTradingSys/research/layer_rebuild_2026-10-15/LAYER_REBUILD_PLAN_2026-10-15.md:13-14`; checker `scripts/dev/verify_extract_quotes.py:1`.
2. G2 setup catalogue (entry/stop/target in his words, NOT STATED where silent): `MyTradingSys/research/layer_rebuild_2026-10-15/LAYER_REBUILD_PLAN_2026-10-15.md:15`.
3. G3 blind marking is DROPPED per operator 2026-10-28 (NOT the old two-reader blind-mark rule): `MyTradingSys/system/REQUIREMENTS.md:9` (R-03). Stale source, superseded: `MyTradingSys/research/layer_rebuild_2026-10-15/READER_PROTOCOL.md`.
4. G4 encode; recall AND fire rate pass before any P&L: `MyTradingSys/research/layer_rebuild_2026-10-15/LAYER_REBUILD_PLAN_2026-10-15.md:17`; `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:29`.
5. Label every parameter SOURCED/OURS; OURS tunes on DEV only: `MyTradingSys/system/MOVED_RULES.md:6`.
6. Pre-register (12-item template, count-only power check): `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:1`; gate script `scripts/dev/prereg_gate.py:1`.
7. G5 DEV event study, fee-net, same-window placebo, trial ledger: `MyTradingSys/research/layer_rebuild_2026-10-15/LAYER_REBUILD_PLAN_2026-10-15.md:18`; one-file-per-layer convention `MyTradingSys/research/sim_desk/PLUGIN.md:3`.
8. Record: `MyTradingSys/system/layer_map.json:1`, `MyTradingSys/research/VERDICTS.csv:1`, `scripts/dev/make_layers_md.py:1`, `MyTradingSys/system/layer_index.json:1`, `MyTradingSys/system/wiring_registry.json:1`.
9. One VALIDATION read, then one holdout read, each logged once: `MyTradingSys/system/MOVED_RULES.md:6`.
10. Live code with a parity test (tested exit, not the generic bracket) and restart/reset, balance-move, API-error, fail-closed tests: parity test `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T09/test_layer_signal_parity.py:1`; live-path test rule `MyTradingSys/system/MOVED_RULES.md:14`.
11. Promotion: `promote.py check` (fee-net OOS > 0, CI low > 0, n >= 30), then `register --mode shadow`, testnet only with `size_overrides`: `MyTradingSys/system/PROMOTION_PIPELINE.md:15,23,25-26`; checker `MyTradingSys/backtest/layers/promotion/promote.py:143`.
12. Confluence: a layer gates another only after passing S3 alone: `MyTradingSys/PROJECT_VISION.md:262`.
