# HANDOFF W1a -> W3 (rsi_divergence, session_levels)
Modules (alerts/, import-only, no edits to live_layers.py): `live_rsi_divergence.py` adapter `adapter` (= `rsi_divergence_layer`),
`live_session_levels.py` adapter `adapter` (= `session_levels_layer`). Both fn(bars)->[{t,event,side,sampling:True,...}], stateless, causal.
Registry lines (key `layer:<layer>:<sub>:<tf>`), proposed size OURS 20/2, both SAMPLING (no edge claimed):
  layer:rsi_divergence:bull:1h  -> live_rsi_divergence.adapter  (events rsi_div_bull -> long)
  layer:rsi_divergence:bear:1h  -> live_rsi_divergence.adapter  (events rsi_div_bear -> short)
  layer:session_levels:pdh_fail:1m -> live_session_levels.adapter (sess_pdh_failed_break -> short)
  layer:session_levels:pdl_fail:1m -> live_session_levels.adapter (sess_pdl_failed_break -> long)
Notes: one adapter emits both sides, so W3 may register once per layer and route by event; session_levels needs 1m bars with >=1400 bars of the
previous UTC day (else no events); grep every TF/family map for tf `1m` + family `session_levels`/`rsi_divergence` (CLAUDE.md rule).
Tests: test_live_rsi_divergence.py, test_live_session_levels.py auto-collected by run_all_tests (layers rglob), 17 tests.
Registry: W1a added 2 WIRE entries in wiring_registry.json (gate requires it); W3 must delete them when wiring.
