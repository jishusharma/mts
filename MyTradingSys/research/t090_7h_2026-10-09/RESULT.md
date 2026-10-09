# T090 7h research + T088 lead robustness (2026-10-09)

## Sources (standard web search + page fetch 2026-10-09; no YouTube video found that discusses 7h)
- TradingView "MCS HTF Po3 (printed from 1800)" https://www.tradingview.com/script/PizcXAAP-MCS-HTF-Po3-printed-from-1800/ : closed-source; text: "Designed to view AM trades 7H candles as they print on the lower time frame." / "Customisable HTF candles that reset and print at your chosen time". 18:00 is only in the title; no time zone, market or test.
- TradingView "7Hour Levels" https://www.tradingview.com/script/KXQfNGf1-7Hour-Levels/ : "Asia 18:00 -> London 01:00 -> NYAM 08:00 -> NYPM 15:00 (New York time)", "The trading day begins at 18:00 New York time". 7 h = spacing of session opens (ICT day), not a candle study.
- Playbook tier: T3 at best (indicator descriptions). No backtest, no crypto-specific 7h evidence found. 7h is an ICT session-spacing idea for FX/futures, not a crypto convention.

## Anchor decision
- Only sourced anchor: 18:00 New York = 22:00 UTC (EDT) / 23:00 UTC (EST). 00:00 UTC day-reset (T088 default) and epoch have no source: flags updated in registry.json, both stay NO-SOURCE; the 18:00-NY variant is `7h` shifted +22h/+23h (probe script, not yet a registry key because it needs DST handling).
- Pick for any later 7h test: 18:00 NY (22/23 UTC), not 00:00 UTC.

## Robustness of the T088 lead (operator bullish long-range RSI divergence, net of taker x2, horizon 10 bars, BTCUSDT 2022-01..2026-10)
Only BTCUSDT is on disk (no ETH). Anchor shift = 1m bars shifted by h hours then the registry resample rule.

| cell | n | net mean h10 | t | hit |
|---|---|---|---|---|
| 7h@00 | 46 | +1.09% | 2.11 | 70% |
| 7h@18 | 47 | +0.15% | 0.25 | 55% |
| 7h@22 | 45 | +0.65% | 1.18 | 58% |
| 7h@23 | 43 | +0.46% | 1.23 | 58% |
| 7h@03 | 55 | +1.89% | 3.45 | 73% |
| 7h@05 | 48 | +0.57% | 0.87 | 56% |
| 7h@12 | 47 | +0.43% | 0.64 | 53% |
| 6h@00 | 54 | +1.57% | 2.99 | 69% |
| 6h@01 | 46 | +0.43% | 0.79 | 61% |
| 6h@02 | 47 | +1.03% | 1.87 | 57% |
| 6h@03 | 45 | +0.55% | 1.15 | 51% |
| 6h@04 | 39 | +0.38% | 0.69 | 56% |
| 6h@05 | 48 | +0.29% | 0.44 | 56% |
| 8h@00 | 35 | +1.02% | 1.42 | 60% |
| 8h@01 | 37 | +0.69% | 0.94 | 51% |
| 8h@02 | 38 | +1.23% | 1.74 | 61% |
| 8h@04 | 38 | +0.61% | 0.98 | 53% |
| 8h@06 | 37 | -0.17% | -0.23 | 46% |

Verdict: NOT robust. Of 18 anchor cells, 3 reach t>2 (7h@03 t3.45, 6h@00 t2.99, 7h@00 t2.11); 17 of 18 are positive (mean ~+0.7%), so the bullish operator signal on 6-8h carries a common positive drift, and the "best" cell moves with the anchor. Picking the best of 18 explains the 7h@00 result. At the sourced anchor (22/23 UTC) the 7h lead is t 1.2: no edge. It is the same 6h/8h-type effect shifted, not a 7h-specific one. All cells n 35-55 (< 300): no verdict either way. Not wired, not queued; closing the 7h lead.
Script: backtest/layers/rsi/run_t090_anchor_probe.py; data anchor_probe.json.
