# B103 - Backtest funding cost is silently zero outside the loaded range

Status: CLOSED (code fix; 2020+ data fetch and C1 rerun still outstanding, see B127). Severity: MED. Opened 2026-10-04.

## Defect

backtest/layers/positioning/trade_costs.py:24-25 funding_paid returns 0.0
when t_out is at or before the first record, and the loop sums nothing
for records past the last one. No coverage check, no warning.

Local fundingRate on disk holds 2025-09..2026-08. Klines on disk run
2022-01..2026-09-26. The Binance archive has BTCUSDT 8h funding from
2020-01.

## Evidence

- Dumps/backtest/raw/fundingRate: 12 monthly files, 2025-09..2026-08.
- data.binance.vision futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2020-01.zip:
  HTTP 200, 93 records (fetched 2026-10-03 by the MA research session).
- futures/um/daily/metrics BTCUSDT-metrics-2020-09-01.zip: HTTP 200.
- Docs state the gap as a data fact: backtest/layers/FORMULAS.md:370.
  research/fast_track_2026-09-27/T055_BT_c3.md:27.
  items/T058_broken_extremes_sweep_vs_continuation.md:26.

## Effect

T055 C1 (funding-extreme) was tested on about 12 months when about 6
years exist. C2, C3 and every perp trade before 2025-09 or in 2026-09
was scored with zero funding. Multi-day MA and trend holds on perps
understate cost.

backtest/layers/fabio/v3/costs.py funding_r has the same no-coverage
pattern.

## Fix shape

Fetch fundingRate 2020-01.. and metrics 2020-09.. with
fetch_binance_archive.py. Make funding_paid fail closed when the
(t_in, t_out] window is not inside the loaded records span. Label C1
results 12-month-only until rerun.

## Related

- research/_archive/loose_2026-10/BTC_MA_SETUPS_RESEARCH_2026-10-03.md section 4
- MyTradingSys/system/sessions/MTS-2026-10-03-2053Z-APP-ANA-btc-moving-averages.md

## Receipt

- commit with trailer MTS-Session: MTS-2026-10-04-1233Z-APP-BLD-b102-b103: trade_costs.funding_paid raises ValueError when (t_in, t_out] is outside the loaded records' span (empty list = explicit no-funding, still 0.0); test fails on pre-change (0.0 returned), passes after. Existing C1 results stay 12-month-only until rerun; fabio/v3/costs.py funding_r not changed.
# END
