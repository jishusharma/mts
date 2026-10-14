# Data-quality amendment, before outcome inspection

2026-10-14: initial load stopped with `ValueError: missing minutes; do not bridge gaps`; no events or result probabilities were produced. All 30 archive hashes matched Binance checksums. Log this as an aborted data-check attempt, not a hidden strategy run.

Keep complete candles only. Require contiguous previous two signal bars, complete parent 4h/day/week levels, 31-day regime history without missing daily observations, and every minute from reference entry through the 60min endpoint. Preserve missing parent periods as NaN so no stale level is carried over a gap. Write exact missing-minute spans to gaps.json. No prices interpolated; all 126 definitions and thresholds unchanged.

Additional regression test `test_gap_cannot_bridge_forward_window` failed before correction and passes after. This amends implementation handling of invalid data, not the research hypothesis. Calendar days remain in bootstrap even when no events exist.

Correction after independent diagnostic review: actual missing-minute count is ZERO. Pandas 3 indexes may store microseconds; the first check assumed nanoseconds for `.asi8`. Comparing Timedelta values fixes the false alarm. All 1,313,279 consecutive pairs are one minute apart. The gap exclusions remain as robustness guards; they do not remove real gaps in this sample.

Second attempted run stopped before event output: pandas returned a read-only Boolean array. The new full synthetic event-pipeline test reproduced the error; requesting an explicit copy fixes it. Both aborted attempts produced no probability table. Count both attempts in the lab run log; no hypotheses changed.
