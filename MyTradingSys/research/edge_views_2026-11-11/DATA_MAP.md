# Market data map for edge research (inventory 2026-11-11)

Read-only inventory of market data on this machine. Roots checked: `C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed` (MyTradingSys, runtime_data, sim_desk), `F:/MTS`, `F:/CryptoScrapper`.

Method: one Python one-off per data group (`python -I`), streaming reads. First and last dates come from the data's own timestamps. Rows are distinct bars or timestamps, not raw lines, because monthly and daily files overlap in several folders. Dates are UTC. "inferred" means the venue or symbol is not stated in the file and was worked out from price or volume scale.

## 1. Data inventory

| data kind | symbol(s) | venue | bar size | first date | last date | rows | path |
|---|---|---|---|---|---|---|---|
| Candles | BTCUSDT | Binance perp (inferred from volume) | 1m | 2022-01-01 | 2026-09-26 | 2,491,200 | F:/MTS/data/tom_raw/klines/ (89 monthly csv) |
| Candles | BTCUSDT | Binance perp | 1m | 2025-09-01 | 2026-10-21 | 599,040 | F:/MTS/Dumps/backtest/raw/klines/ (70 files, daily + monthly overlap, deduped) |
| Candles | BTCUSDT | spot | 1m | 2022-01-01 | 2026-10-07 | 2,506,960 | F:/MTS/data/bigtrade/spot_raw/ (64 monthly csv) |
| Candles | BTCUSDT | not stated | 1m | 2020-01-01 | 2021-12-31 | 1,052,640 | F:/MTS/Dumps/backtest/raw_1m_2019/klines/ (folder name says 2019, data starts 2020) |
| Candles | BTCUSDT | not stated | 1m | 2022-01-01 | 2025-08-31 | 1,928,160 | F:/MTS/Dumps/backtest/raw_1m_2022/klines/ (44 files) |
| Candles | BTCUSDT | Binance perp (mark price) | 1m | 2025-09-01 | 2026-09-26 | 563,040 | F:/MTS/Dumps/backtest/raw/markPriceKlines/ (46 files) |
| Candles | BTCUSDT | spot (2017 history) | 15m | 2017-08-17 | 2026-10-31 | 322,270 | F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/15m/ (30m, 4h, 1h, 1d also here) |
| Candles | BTCUSDT | spot | 1h | 2017-08-17 | 2026-10-31 | 80,581 | F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/1h/ |
| Candles | BTCUSDT | spot | 4h | 2017-08-17 | 2026-10-31 | 20,160 | F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/4h/ |
| Candles | BTCUSDT | spot | 1d | 2017-08-17 | 2026-10-31 | 3,363 | F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/1d/ |
| Candles | BTCUSDT | not stated | 1d | 2020-01-01 | 2026-09-26 | 2,461 | F:/MTS/Dumps/backtest/raw_1d/klines/ (106 files) |
| Candles | ETHUSDT | Binance perp (inferred) | 1m | 2022-01-01 | 2026-09-30 | 2,496,960 | F:/MTS/data/tom_raw/klines_eth/ (57 monthly csv) |
| Candles | ETHUSDT | spot (2017 history) | 1h | 2017-08-17 | 2026-10-31 | 80,581 | F:/MTS/Dumps/backtest/spot_2017/ETHUSDT/1h/ (1d: 3,363; 15m, 30m, 4h also here, not counted) |
| Candles | ETHUSDT | spot (inferred from price) | 5m | 2019-01-01 | 2026-11-10 | 826,496 | F:/MTS/data/edge_1111_5m/ (95 monthly json, field src=spot) |
| Candles | ADAUSDT, AVAXUSDT, BNBUSDT, DOGEUSDT, LINKUSDT, LTCUSDT, SOLUSDT, XRPUSDT | Binance perp (inferred) | 1m | 2022-01-01 | 2024-06-30 | 1,306,080 to 1,313,280 each | F:/MTS/data/tom_raw/klines_<sym>/ (30 monthly csv each) |
| Candles | BTCUSDT, ETHUSDT, SOLUSDT | not stated | 1d and 4h | 2020-01-01 | 2024-06-30 | about 1,643 daily and 9,858 4h bars per symbol | F:/MTS/data/fable_run6_klines/ |
| Candles | BTCUSDT | Binance spot (inferred) | 5m | 2026-08-01 | 2026-11-04 | 27,360 | F:/MTS/data/bigcandle_cache/k5/ (about 96 days) |
| Candles | BTCUSDT | Binance perp (klines + OI) | 1m | 2026-10-20 | 2026-11-03 | 18,720 | F:/MTS/data/flow_state_1m/BTCUSDT_*.json |
| Candles | BTC-PERPETUAL | Deribit | 1m | 2024-05-01 | 2024-05-31 | 44,640 | F:/MTS/data/deribit/ (1 file) |
| Candles | BTCUSDT | Bybit perp | 1m | 2026-10-28 | 2026-10-28 | 1,440 | F:/MTS/data/flow_state_1m/bybit_BTCUSDT_2026-10-28.json |
| Candles | BTCUSDT | Binance (repo sample) | 5m / 15m / 1h | 2026-09-20 | 2026-10-20 | 500 each (capped) | C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/MyTradingSys/market_data/klines/ and data/klines/ |
| Candles | GER40 (index CFD, not crypto) | not crypto | 1m | 2024-10-01 | 2026-10-09 | 684,940 | F:/MTS/data/dax_archive/klines/ (excluded from crypto work) |
| Funding rate | BTCUSDT | Binance perp | 8h | 2020-01-01 | 2026-09-30 | 7,395 | F:/MTS/Dumps/backtest/raw/fundingRate/ (81 monthly csv; eh_* folders are copies) |
| OI + long/short ratios | BTCUSDT | Binance perp | 5m | 2022-01-01 | 2026-11-04 | 509,339 | F:/MTS/data/metrics/BTCUSDT/ (1,769 daily csv; ratio columns blank in early rows) |
| OI + long/short ratios | BTCUSDT | Binance perp | 5m | 2022-01-01 | 2025-12-31 | 420,635 | F:/MTS/data/binance_metrics/ (1,461 daily csv; overlaps the row above) |
| OI + long/short ratios | ETHUSDT | Binance perp | 5m | 2022-01-01 | 2026-11-04 | 509,339 | F:/MTS/data/metrics/ETHUSDT/ (1,769 daily csv) |
| OI + long/short ratios | BTCUSDT | Binance perp | 5m | 2025-09-01 | 2026-09-26 | 112,608 | F:/MTS/Dumps/backtest/raw/metrics/ (391 daily csv); copy of 2022-01 to 2024-06 in F:/MTS/data/oi_pivot_2026-10-26/ (912 files) |
| OI (live poll) | BTCUSDT | Binance perp | about 1m | 2026-10-21 | 2026-10-22 | 1,094 | C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/MyTradingSys/runtime/oi_live/oi_1m.csv |
| Order book depth (+-5% buckets, not full book) | BTCUSDT | Binance perp | not a fixed bar | 2025-09-01 | 2026-09-26 | 1,083,060 timestamps (12,242,976 rows) | F:/MTS/Dumps/backtest/raw/bookDepth/ (391 daily csv) |
| Aggressor order flow (1m buy/sell volume, delta, CVD, large-trade buckets) | BTCUSDT (inferred) | Binance perp (built from aggTrades) | 1m | 2024-12-02 | 2026-09-28 | 959,021 | F:/MTS/data/orderflow_1m/ (666 daily csv.gz) |
| Order flow (1m delta) | BTCUSDT | Bybit perp | 1m | 2026-10-28 | 2026-10-28 | 1,440 | F:/MTS/data/flow_state_1m/bybit_BTCUSDT_2026-10-28.json |
| Order flow (live mirror) | BTCUSDT (inferred) | Binance perp | 1m | 2026-10-21 | 2026-10-22 | 2,073 | C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/runtime_data/_mirror/MyTradingSys/runtime/orderflow_live/ (2 daily csv) |
| Options trades | BTC and ETH options (Deribit-style instrument names, venue not stated) | options | trade level | 2021-01-01 | 2026-10-08 | 22,769,945 trades | C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/MyTradingSys/options/data/hist/trades/ (2,107 daily jsonl.gz, 556 MB) |
| Volume-profile snapshots (not an order book) | BTCUSDT | derived | 15m steps | 2022-01 | 2026-09 | 120,892 snapshots | F:/MTS/data/tom_snapshots/ (57 monthly jsonl.gz) |
| Analyst calls (CBP) | 62 videos; analysts Benjamin 14, Krown 14, Michael 12, Jason 6, Qriptal 5, Jala 4, CCU 3, Michaal 2, Rekt 2 | n/a | per video | 2026-10-21 | 2026-11-10 | 62 verdicts | F:/CryptoScrapper/cbp_store/verdicts.json |
| Analyst calls (CBP) | structured rows | n/a | per call | 2026-11-06 | 2026-11-10 | 15 rows | F:/CryptoScrapper/cbp_store/rows.json (ingestion log: 1,480 lines, window end 2026-11-11, fetch incomplete for 7 analysts) |

Not counted in full: ETH 15m, 30m and 4h spot-2017 files (dates from file names only); options trade files (row total from the manifest).

Excluded as not market data: F:/MTS/data/tom_videos, fabio_videos, dax_* raw; F:/MTS/data/bigtrade/fires (signal events, 22 files); F:/MTS/data/bigtrade/cache (derived npz); F:/MTS/api_runs/liquidations-mirror (agent run log).

## 2. Kinds with under 90 days of history (too short to test)

| kind | symbol | span | note |
|---|---|---|---|
| Bybit order flow and klines | BTCUSDT | 2026-10-28 (1 day), klines 2026-10-20 to 2026-11-03 (14 days) | flow_state_1m |
| OI poll (repo) | BTCUSDT | 2026-10-21 to 2026-10-22 (1,094 rows) | runtime/oi_live |
| Order flow live mirror | BTCUSDT | 2026-10-21 to 2026-10-22 | runtime_data/_mirror |
| Deribit perp 1m | BTC-PERPETUAL | 2024-05 only (1 month) | data/deribit |
| Repo kline samples | BTCUSDT | 500 bars each (about 3 to 4 weeks) | capped samples |
| Analyst calls (structured rows) | all | 2026-11-06 to 2026-11-10 (15 rows) | rows.json; verdicts.json covers 21 days |
| BTC 5m spot k5 cache | BTCUSDT | 96 days (2026-08-01 to 2026-11-04) | just over 90 days; listed for completeness |

## 3. Kinds missing entirely

| kind | status |
|---|---|
| Funding rate for ETH or alts | missing (BTC only, 2020 to 2026) |
| Open interest for alts | missing (BTC and ETH only) |
| Liquidation history (forceOrder) | missing. The recorder code exists (research/liq_mirror_2026-11/liq_mirror.py) and expects runtime_data/liq_events, which is not on disk. Only CoinGlass screenshots exist. |
| Raw aggTrades | missing. F:/MTS/Dumps/backtest/raw/aggTrades is empty. Only the 1m aggregates in orderflow_1m survive (2024-12 to 2026-09). |
| Full order-book snapshots | missing. bookDepth is a +-5% aggregate for BTC for about one year. tom_snapshots are volume-profile state, not book. |
| Order flow before 2024-12 | missing as aggressor data. Klines carry taker-buy volume since 2017 (spot) and 2020 (perp), usable as a coarser proxy. |
| Order flow for ETH or alts | missing |
| Bybit history beyond one day | missing |

## Notes

- Use `Dumps/backtest/raw/klines` and `tom_raw` with care: both mix monthly and daily files, so count bars, not files.
- The same BTC funding and OI history appears in several folders (eh_* copies, oi_pivot_2026-10-26). Use one source.
- The F:/MTS/data/orderflow_1m daily progress log shows about 1.6M trades per day, which fits BTCUSDT perp, but the file does not name the symbol.
