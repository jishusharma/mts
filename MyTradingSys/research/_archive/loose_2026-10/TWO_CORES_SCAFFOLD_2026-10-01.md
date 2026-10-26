# Session MTS-2026-10-01-1858Z-CLD-BLD-two-cores: TWO CORES SCAFFOLD (spec only, no code)
Doctrine: research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md. Every claim cites file:line; "unknown" where the clone shows nothing. Written by a single parent pass (85% budget row).

## 1. Current state of each core
Tom core
- Engine: runtime/math_object_builder.py (verdict + contradictions, :396-415); alert is written for the desktop loop; auto_trader reads runtime_data/last_alert.json (execution/auto_trader.py:45) and builds source "tom" (auto_trader.py:150, config "tom" block auto_trader.py:55-57 region, min_net_rr 2.0).
- Writer of last_alert.json: scripts/core/start-trading-day.ps1:766 writes a last_alert.json under $LogDir; whether $LogDir equals runtime_data is unknown.
- Verdict vocabulary Tom: ARCHITECTURE_TWO_CORES_2026-10-01.md:22 (WAIT_*, SETUP_FORMING, SETUP_CONFIRMED); auto_trader accepts SETUP_FORMING/SETUP_CONFIRMED (auto_trader.py DEFAULT_CONFIG "verdicts").
- Known live defect: book_imbalance 0.0 vs LONG (math_object_builder.py:399,413).
Fabio
- Spec: research/fast_track_2026-09-27/FABIO_V3_SPEC.md (signals S1-S9 at :63-103, models A-D at :104-136, costs :168, provenance :189-232).
- Code today: loose layer detectors only, backtest/layers/fabio/{fabio_cvd_absorption,fabio_escalation,fabio_volume_fvg,fabio_of_model}.py, registered in backtest/layers/alerts/live_runner_cli.py (fabio entries ~:131-170: cvd_absorption 1h/15m, escalation, volume_fvg 1h/15m). No v3 module (only backtest/layers/fabio/pending_test_fabio_v3.py).
- Routing: source "layer:fabio:<sub>:<tf>" (auto_trader.py:208) maps to account "fabio" via auto_trader.py:67 accounts map.
- Fabio emits alerts, not verdicts, trade plans or ledger rows of its own: unknown beyond layer alerts (auto_trader layers block gives a fixed 1% bracket, auto_trader.py:58-61).

## 2. What makes each a compiled core
Tom (smallest change; "stays as-is", ARCHITECTURE:78-80)
1. Name the input contract: list snapshot fields math_object_builder reads (unknown: not enumerated in this pass).
2. Add a core.enabled flag read at the point auto_trader.py:507 (tom_signal) and at alert emission; no rule change.
3. Ledger: source "tom" already flows to trade_ledger.py:129. Nothing to add.
Fabio
1. New module backtest/layers/fabio/fabio_core.py (pure; input = bars + orderflow per FABIO_V3_SPEC.md:24-38; output = verdict, model, side, entry, stop, target). Build from spec S1-S9 and models A-D only; params flagged NO-SOURCE in FABIO_PROVENANCE_AUDIT_2026-10-01.md (P25,P29,P30,P31,P34,P35,P39; P29/P30 SAFETY-exempt) must not be tuned (CLAUDE.md Provenance).
2. Own verdict vocabulary per spec models (names: unknown; spec defines state machines :104-136, no verdict strings read in this pass).
3. Trade plan emitter: spec 5.1-5.2 (:138-167) gives fills and management; wire as a "fabio" signal in auto_trader with its own stop/target instead of the layers block (auto_trader.py:58-61).
4. Per-core flags: enabled true/false, mutually independent. Acceptance in ARCHITECTURE:82-90.
5. Backtest gate before enabling live: FABIO_V3_SPEC.md:249-268 (section 8); TRIAL_REGISTRY.csv for the grid does not exist yet (FABIO_V3_SPEC.md:234).
Owner rule: execution/ and layers/alerts/ edits need a SUPERVISOR_LOG ownership claim and stage .new only (CLAUDE.md).

## 3. Consensus writer design
- File: MyTradingSys/runtime/consensus/consensus_<YYYYMMDD>.jsonl (ARCHITECTURE:33 says consensus_<UTC>.jsonl; directory is a proposal, unknown if the runtime dir is gitignored). Append-only, LF.
- Fields exactly as ARCHITECTURE:33-41: snapshot_id, utc_timestamp, price, tom{verdict,setup,side,entry,stop,target,net_rr}, fabio{verdict,model,side,entry,stop,target}, rsi{1m,3m,15m,1h,4h,1d}, notes.
- Hook point (proposal): a read-only post-step after an alert is formed: Tom side at the point auto_trader.py:507 reads the new Tom alert, Fabio/RSI side at live_runner_core.py:149 where alert = format_alert(...) is built. Which side owns the write, and the snapshot_id source, is unknown: no snapshot_id exists in math_object_builder.py (grep of "snapshot_id" empty).
- Must not gate: write inside try/except, failure logged only; auto_trader behaviour identical with the writer off.

## 4. RSI observation block design
- TFs: 1m,3m,15m,1h,4h,1d (ARCHITECTURE:39). Gaps: TF_SECONDS lacks 3m (auto_trader.py:47); alert_rate_check TF_MIN lacks 3m and 1d (scripts/dev/alert_rate_check.py:23); live runner registers rsi at 1h/5m (live_runner_cli.py ~:143-152); 1m/3m/1d bars availability in live_runner: unknown. Per CLAUDE.md: grep every TF map before adding a TF.
- Fields per TF (proposal): value (rsi_core, backtest/layers/rsi/rsi_core.py:7, period 14), zone vs 40/60 band (malkan_40_60.py), optional rsi_ma (rsi_ma.py). Existing attach point: format_alert(..., rsi_value, rsi_ma_value) at live_runner_core.py:149-150, but only for the alert's own TF.
- Snapshot position: computed on the latest closed bar of each TF at alert time; never feeds a gate (PROJECT_VISION: modules never gate core).
- Source flag: layer:rsi:40_60, layer:rsi:ma_60 (ARCHITECTURE:48).

## 5. Switchability config block (proposal)
Add to execution/auto_trader_config.json (DEFAULT_CONFIG is auto_trader.py:53-70; file read via --config auto_trader.py:543):
  "cores":   { "tom": {"enabled": true}, "fabio": {"enabled": true} },
  "modules": { "rsi_observation": {"enabled": true}, "consensus_writer": {"enabled": true} }
Defaults per ARCHITECTURE:70-74. Existing overlap: "tom".enabled and "layers".enabled and "disabled_layers" (auto_trader.py:55,59,66); cores.fabio should map to disabled_layers prefix "fabio" or its own signal: choice unknown.
Edge: a core off stops only its own alerts (ARCHITECTURE:73).

## 6. Migration order
1. Safe first: book_imbalance LONG fix (READINESS priority 1) and tests for quad_classify/regime_classifier; add consensus writer in observe-only mode with Tom + RSI only (no Fabio dependency).
2. Second: TF maps for 3m/1d across live_runner_cli, alert_rate_check, auto_trader, audits; RSI observation block in the consensus row.
3. Third: Fabio core module from FABIO_V3_SPEC after the spec's section 8 backtest, then its own signal + account routing in auto_trader; then per-core flags and the four acceptance tests (ARCHITECTURE:82-90).
