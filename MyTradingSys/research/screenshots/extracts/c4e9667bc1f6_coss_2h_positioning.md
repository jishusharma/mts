# CoinGlass BTCUSDT 2h OI/positioning-stack read, captured ~16:07Z 2026-10-27
Prior: cset_2026-10-27_coss_multi_tf.md
Shot: c4e9667bc1f6 (2h, scrolled to the OI/Net-flow/Top-Trader panel stack; same moment as the 15m/30m/1h/2h multi-TF set above).
Operator: "do magic with this." The magic = this image finally shows the OI/Net/Top-Trader panels the multi-TF set had to file NOT_IN_DATA (no stored CoinGlass series). The *shape* of the stack is logged below; the per-bar OI/CVD digits stay chart-only.

## Cross-market at this moment (LIVE, public data via live_cross_read.py, now ~16:11Z, open 13:30Z)
| Series | since-open % | read |
|---|---|---|
| BTC +0.40 / ES +0.45 | gap = -0.05 | TIGHTENED vs the 15:48Z -0.26 |
| NQ +1.01 (leading), VIX -2.01 | risk-on | BTC-ES r1h +0.57 (coupled, n=12) |
| **0.80 widening trigger** | **NOT reached** | gap has *narrowed*; 10-26 03:15Z danger line not re-tested |

Gap = BTC since-open % − ES since-open % (OURS, matches the 15:48Z reading that used the same sign convention). At -0.05 the ES-lag watch that was set up for a possible event #5 has effectively been retired for the open: no event #5.

## Positioning-stack shape read off this 2h image (CHART-ONLY — no stored CoinGlass OI/CVD/Net series)
| Panel (2h) | read | comment |
|---|---|---|
| OI | ~80.5K, flat since the 10-26 drop | no OI expansion into the 10-27 recovery — the bounce is flow-driven, not new-money-driven |
| Net Longs (New) | falling, high-20s → ~13.0K | new long flow has slowed as price recovered |
| Net Shorts (New) | rising, low-20s → ~14.4K | new short flow up into the recovery = hedging against the bounce |
| Top Trader Long/Short (Accounts) | 2.286 flat both | the largest traders: flat, no net add |
| Top Trader L/S (Positions) | 1.96 flat | same, at position-weighting |

OURS inference (labelled, not a chart number): on a price recovery that is *up* with OI flat, new-long flow down and new-short flow up while Top-Trader positions stay flat, the recovery looks driven by **retail/tail flow + hedging, not top-trader or OI expansion**. That is a thinner, less-durable recovery signature — it fits the multi-TF set's "short TFs overbought, higher-TF close still RED" verdict (a higher-TF counter-move, not a flip). This is a read, NOT a trade call.

## Price / RSI anchor on this 2h (REPRODUCED from public Binance 1h closes via data-api.binance.vision)
| metric | last CLOSED 2h (13:00 UTC) | forming 2h (15:00 UTC, now) |
|---|---|---|
| OHLC | 80365.7 / 80415.0 / 79890.0 / 80356.2 | open 80356.2, high 80704.9, low 80244.0, now 80461.3 |
| RSI(14) | 52.55 (prev 42.27/44.54/52.75) | forming 54.60 |
| vs 80,250 | above | above (forming low 80244.0 just tagged it, now back above) |

The chart's on-screen O 80,530.0 / H 80,579.3 / L 80,458.3 / C 80,495.8 are the *displayed* 2h candle values; our public 1h-aggregated 2h reproduces the *last closed* candle as 80365.7/80415.0/79890.0/80356.2 — the chart is on the forming candle, so the two differ by construction (same as the multi-TF set's "forming-bar" note). The 80,705 day-high on the chart matches our public 2h forming high 80,704.9. RSI/price are the reproducible MATCH anchors.

## Claim rows (one per shot id)
| id | class | claim | data check |
|---|---|---|---|
| c4e9667bc1f6 | MATCH | 2h last-closed 13:00Z candle O80365.7 H80415.0 L79890.0 C80356.2, RSI(14) 52.55 (prev 42.27/44.54/52.75) | OURS Wilder RSI on public binance.vision 1h closes aggregated to 2h; forming-bar RSI 54.60, forming high 80704.9 matches chart 80,705 day-high |
| c4e9667bc1f6 | MATCH | price holds above 80,250 on the 2h; 80,244 forming low just tagged 80,250 | public 1h → 2h; since-open gap BTC-ES -0.05 (live_cross_read.py 16:11Z) |
| c4e9667bc1f6 | NOT_IN_DATA | OI ~80.5K flat, Net Longs(New) ~13.0K falling, Net Shorts(New) ~14.4K rising, Top Trader L/S accounts 2.286 / positions 1.96 flat | no stored CoinGlass OI/CVD/Net series on this tree (oi_1m.csv absent) — numbers chart-only; shape logged, digits not reproducible from repo data |

## Invalidation / falsify
- If OI (not reproducible from repo, chart-only) were to expand with the recovery, the "thin flow-driven bounce" read is falsified — next 2h close with OI up + Net Longs back up = recovery is OI-backed.
- If price closes the 2h back under 80,244 (the forming low that tagged 80,250) and StochRSI K (multi-TF set: 30m/1h at 94-100) crosses down, the "5h+ sustained reclaim" is broken — 10-26 03:50Z flush pattern.
- If 1d closes 10-27 RED the 4d/5d RED streak extends (ladder); the 2h up is a higher-TF counter-move, not a flip.

## What this set adds over the multi-TF set
- The multi-TF set answered DIRECTION (all up) + TIMING (short TFs overbought). This 2h positioning panel stack answers FLOW SOURCE: OI flat, new-long down, new-short up, Top-Trader flat = recovery is retail/tail + hedging, not top-trader/OI. Thinner signature, lower durability — consistent with the "counter-move, not flip" verdict.
