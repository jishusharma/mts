Live one-page mock v4 (operator review 2026-11-04: "84,000 everywhere" was a 31-day-old file shown as now). Snapshot at build; re-run to refresh.
- Market now: public Binance spot BTCUSDT klines at build (24h move, net bought from taker volume, sweep + recovery, levels, 5 daily rows).
- Timeframes: same klines, 15m-1d: RSI 14 (rsi_core) vs 40/60, WaveTrend (PRE_REG_C30 formula), 21-bar average; backtest box from c30_validation_verdict.json.
- Positions/testnet: empty state on purpose; testnet trades live on desktop-f7iu69n (live_mirror.py brief), no order data in the public repo.
- Analysts & calls: CBP store rows + verdicts.json (bias by video day, levels within 12% of price), Habib Discord from research/analysts/watch/POSTS_LOG.csv.
- Layers: LAYERS.md head + newest dated line per layer, STATUS.md gate board; plain wording table PLAIN in the generator (OURS).
- Health: feed freshness (price, CBP stamp.json + ingestion.log, Discord log, orderflow file, STATUS.md age).
- To go live: run this builder on a schedule-free trigger (the CBP run or a session), or fold it into the mts_home generator.
- SAMPLE badges: none (v3 SAMPLE-POS removed; Positions shows nothing rather than guess).
- Build: python MyTradingSys/system/artifacts/_gen_live_onepage_mock.py [--fragment <artifact copy>] [--offline]; private unregistered review page "Live feed one page".
