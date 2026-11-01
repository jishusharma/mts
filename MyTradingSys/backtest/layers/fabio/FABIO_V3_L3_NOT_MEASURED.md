# Fabio v3 L3: Model B fills scored 0 R as unmanaged

**NOT MEASURED (as reported before the fix):** in the TF8 L3 run, Model B fills still IN_TRADE at the as-of bar were
scored 0 R with tag `unmanaged` (engine.py `_manage` returned None for B; run_v3_l3.py `_run_day` mapped it to 0.0).
Count per the task card: 42 IS fills and 4 OOS fills. Share of Model B fills: not recomputed here (the order-flow data
store F:/MTS/data/orderflow_1m and the run output F:/MTS/data/fabio_v3_bt are absent on this machine, so the per-window
count and the share were not re-derived). The IS-only rerun is pending on a machine with F:.

**Fix:** `scan_model_b` IN_TRADE now returns `probe_idx` and the balance `bal`; `engine._manage` replays `model_b` on
them, so those fills get the spec 5.2 exits. Test: `test_run_v3_l3.py::test_model_b_in_trade_fill_is_managed_not_scored_zero`
(hand number 19/7 R; scored 0.0 on the old code). Models A, C, D unchanged.
