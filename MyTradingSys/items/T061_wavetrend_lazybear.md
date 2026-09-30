# T061 WaveTrend with Crosses [LazyBear]

Opened 2026-10-01. Status OPEN. Severity MED.

## Operator ask (verbatim)

I need wave trend indicator integration into MTS as a separate layer.

Source: https://in.tradingview.com/v/jFQn4jYZ/  (LazyBear, Pine v2, public domain code with author attribution)

## Parameters (from source)

- Channel Length n1 = 10
- Average Length n2 = 21
- Overbought Level 1 = 60
- Overbought Level 2 = 53
- Oversold Level 1 = -60
- Oversold Level 2 = -53

## Math

ap    = hlc3 = (high + low + close) / 3
esa   = EMA(ap, n1)
d     = EMA(abs(ap - esa), n1)
ci    = (ap - esa) / (0.015 * d)
tci   = EMA(ci, n2)
wt1   = tci
wt2   = SMA(wt1, 4)
plot  wt1, wt2, wt1-wt2 area, cross(wt1, wt2) markers, barcolor on cross

## Classification

- Layer type: indicator / read-only module.
- Doctrine: PROJECT_VISION.md lock 2026-09-23. Modules never gate core. Switchable on/off. Display alongside or compute as separate read.
- Source tag: [SCREENER] until the admission gate. Not Tom, not CT, not a Tom filter.
- Admission: per playbook Part I, T3 practitioner content. No engine rule on this item alone.

## Planned shape (design only, not built)

- One offline module under MyTradingSys/backtest/layers/wavetrend/ with a driver that reads the archived klines.
- Compute wt1, wt2 on each timeframe already present in the snapshot (5m, 15m, 1h, 4h, 1d).
- Emit cross events (wt1 x wt2) with the four threshold levels as tags.
- Backtest with the same method as FABIO_L1: IS/OOS 70/30, fees 0.10% RT, PBO.
- If verdict passes, a live alert layer may be added. Never a filter on core verdict.

## Next step

Write the FORMULAS.md entry for this layer, then spec the driver. No code yet.
