# BLOCKED: rederive-nkp2-levels-phase-gemini4-1114

Cannot independently re-derive the headline numbers of `MyTradingSys/research/nkp2-levels-phase-1114_2026-11-14` from `PRE_REG.md` and `FORMULAS.md` because the required raw data cache and phase spec are not present on this machine.

## Missing inputs
- `F:\MTS\data_cache\mts_brains\phase_daily.csv` (referenced in `MyTradingSys/research/nkp2-levels-phase-1114_2026-11-14/PRE_REG.md#L9`) — `F:\` drive does not exist on this machine (`Get-PSDrive -PSProvider FileSystem` shows only `C:\`).
- `F:\MTS\data_cache\binance_spot` (15m spot bars for 20 coins, `PRE_REG.md#L31`) — not present.
- `F:\MTS\data_cache\binance\nkp2-levels-phase-1114\` (spot 1h klines with taker-buy volume, futures/um monthly fundingRate, futures/um daily metrics `sum_open_interest_value`, `PRE_REG.md#L32`) — not present.
- `MTS_BRAINS_SPEC_1114.md` (`PRE_REG.md#L3`) — not found in `MyTradingSys/research`.

## Checked local cache
- `C:\Users\e-ngineers\MTS_data_cache` contains only `binance_spot_1d`, `binance_spot_4h`, and `bybit_funding` — insufficient to build 1h bars, 1h NK2/NK3 signals/stops/exits, 1h taker-buy delta (C6), OI (C4), or Binance futures funding (C5).
