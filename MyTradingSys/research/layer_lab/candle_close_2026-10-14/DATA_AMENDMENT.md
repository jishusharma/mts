# Data-quality amendment, before outcome inspection

2026-10-14: initial load stopped with `ValueError: missing minutes; do not bridge gaps`; no events or result probabilities were produced. All 30 archive hashes matched Binance checksums. Log this as an aborted data-check attempt, not a hidden strategy run.

Keep complete candles only. Require contiguous previous two signal bars, complete parent 4h/day/week levels, 31-day regime history without missing daily observations, and every minute from reference entry through the 60min endpoint. Preserve missing parent periods as NaN so no stale level is carried over a gap. Write exact missing-minute spans to gaps.json. No prices interpolated; all 126 definitions and thresholds unchanged.

Additional regression test `test_gap_cannot_bridge_forward_window` failed before correction and passes after. This amends implementation handling of invalid data, not the research hypothesis. Calendar days remain in bootstrap even when no events exist.
