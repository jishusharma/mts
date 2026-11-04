# Spot klines back to 2017-08 (BTCUSDT, ETHUSDT; 15m 30m 1h 4h 1d)

No data in git. Source: data.binance.vision SPOT monthly archive (USD-M futures only start 2019-09). Each zip is checked against its published .CHECKSUM (mismatch rejected, nothing written).

- Data: `F:/MTS/Dumps/backtest/spot_2017/<SYMBOL>/<tf>/klines/<SYMBOL>-<tf>-YYYY-MM.csv` (read with `bt_data.load_klines(<root>/<SYMBOL>/<tf>)`; 2025+ files carry microsecond stamps, the loader converts).
- Manifest (sha256, rows, first/last open, gaps per month): `F:/MTS/Dumps/backtest/spot_2017/manifest.json`
- Fetch (resumable, skips existing months): `python MyTradingSys/backtest/fetch_binance_archive.py --spot-history --start 2017-08-01 --end 2026-10-31`
- Fetched: 111 months (2017-08..2026-10) x 2 symbols x 5 timeframes = 1110 files, 0.18 GB on disk (64 MB zipped). No 404s.
- Gaps: exchange maintenance outages inside the archive, 9-25 per series (largest 2018-02, about 33 h); listed per month in the manifest. Not filled.
- Long-window regime mix (`python MyTradingSys/research/klines_history_2017/regime_mix_long.py`, BTCUSDT daily, weeks 2017-08-21..2026-10-26):
  `Regime mix: 479 weeks: bull 105 (22%) | bear 0 (0%) | range 311 (65%) | n/a 63 (13%)`
  Bear weeks: **0**. The n/a weeks are the first 15 months (monthly RSI14 needs history). Closest miss: monthly RSI 40.4 in 2023-01 (bear band needs both weekly and monthly <= 40 and close below SMA200; monthly RSI14 never reached 40 since 2017-08). Longer history does not add bear weeks under this regime definition.
