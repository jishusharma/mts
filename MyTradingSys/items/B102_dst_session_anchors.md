# B102 - Offline session models anchor NY and London at fixed UTC minutes

Status: CLOSED. Severity: LOW. Opened 2026-10-04.

## Defect

Offline backtest models hardcode the NY cash open at 13:30 UTC and
London at 08:00 UTC, all year. Wrong by one hour on roughly 40 percent
of days.

## Evidence

- backtest/layers/fabio/fabio_of_model.py:44 SESSIONS london 480-810,
  ny 810-1260 (08:00 and 13:30 UTC all year; the docstring at :8 says so).
- backtest/layers/session/session_momentum.py:29 session start = UTC day
  plus fixed minutes.
- backtest/layers/run_t055.py:75 C2 grid session_start_min in (0, 810).
- Materiality measured: BTC 15-minute volume and absolute return peak is
  13:30 UTC on US-DST days and 14:30 UTC on US-standard days, per
  research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md F1.
  A fixed 810 misplaces the NY open by 60 minutes Nov-Mar. London 480
  misplaces the BST open by 60 minutes Mar-Oct.

Affected results: T055_BT_c2 and FABIO_OF_REPORT.

Live path not affected: MarketDataSnapshot.java:765/904/929 use
ZoneId America/New_York. Fabio v3 uses day_gates.ny_open_utc.

## Fix shape

Reuse day_gates.ny_open_utc and day_gates.london_open_utc in any rerun.
Label old C2 and OF results as fixed-UTC.

## Related

- research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md
- MyTradingSys/system/sessions/MTS-2026-10-03-2051Z-APP-ANA-btc-session-sweeps.md

## Receipt

- commit with trailer MTS-Session: MTS-2026-10-04-1233Z-APP-BLD-b102-b103: fabio_of_model.session_sequence, session_momentum (session_start_min="ny"/"london") and run_t055.c2_grid now use day_gates DST rules/anchors; tests fail on pre-change, pass after. Existing T055_BT_c2 and FABIO_OF_REPORT results are fixed-UTC (pre-B102) and were NOT rerun.
# END
