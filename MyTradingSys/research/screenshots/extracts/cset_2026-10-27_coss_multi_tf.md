# Multi-TF consistency read, CoinGlass BTCUSDT set (15m/30m/1h/2h), captured ~15:55-16:00Z 2026-10-27
Shots: 14bca069c2b5 (15m) df0d0a3a182b (30m) f05fde8a821d (1h) fcb3e1a769c7 (2h)
Prior: none
Set of one moment read together: BTCUSDT ~80,560-80,630, above 80,250 (reclaimed 12:30Z), below day high 80,705.

## Multi-TF consistency verdict
| TF | Price vs session | RSI(14) zone | StochRSI | Bias (OURS ladder, 15:48Z) |
|---|---|---|---|---|
| 15m | above 80,250, off day low 79,506 | 67.7 bull>60 | K 91 rising, crossed above SMA | GREEN +0.52 |
| 30m | same | 65.7 bull>60 | K 94.5 high, SMA 84.6 | GREEN +0.52 |
| 1h | same | 59.9 neutral high | K 82.6, SMA 80.2 (cross up ~12:00Z, held) | GREEN +0.57 |
| 2h | same | 51.7 mid | K 53 fresh cross up | GREEN +0.74 |

Lower TFs (15m/30m) have moved into StochRSI overbought while 1h/2h momentum is still mid-rising: the recovery of 10-26's event-4 low (79,506 today vs 79,648 10-26 03:15Z) is now 5h+ sustained, not a one-candle reclaim. All four TFs agree in direction (up); no TF shows a bearish cross. The 1d/4d/5d close colours remain RED on the ladder — the short-TF recovery has not flipped the higher-TF close yet.

## Claim rows (one per shot, reproduced from public Binance data)
| id | class | claim | data check |
|---|---|---|---|
| 14bca069c2b5 | MATCH | 15m RSI 67.69 (SMA 62.02), StochRSI K 91.09 | OURS Wilder RSI on public 15m closes: last3 65.49/67.92/68.85 (chart on a forming bar, between last-closed and forming close); StochRSI forming-bar K recompute 98.6, last-closed K 95.6 |
| df0d0a3a182b | MATCH | 30m RSI 65.67 (SMA 54.58), StochRSI K 94.50 | RSI recompute last3 60.21/63.38/66.05; StochRSI forming-bar K recompute 100.0, last-closed K 99.0 |
| f05fde8a821d | MATCH | 1h RSI 59.93 (SMA 47.85), StochRSI K 82.64 | RSI recompute last3 50.16/55.78/60.08; StochRSI forming-bar K recompute 100.0, last-closed K 91.6 |
| fcb3e1a769c7 | MATCH | 2h RSI 56.72 (SMA 45.85), StochRSI K 53.74, green up-cross of BB(20,2) on forming bar | OURS 2h aggregated from public 1h closes: RSI last3 44.54/52.75/52.55; StochRSI forming-bar K recompute 53.4; 2h last-closed RED -0.99% to forming GREEN on the 15:48Z ladder |
| 14bca069c2b5 | NOT_IN_DATA | OI candles 97.15K, CVD step -5.40K, Net Delta -7.13K | no stored CoinGlass OI/CVD series on this tree (oi_1m.csv absent); numbers chart-only |
| df0d0a3a182b | NOT_IN_DATA | OI candles 96.95K, CVD step -7.95K, Net Delta -10.33K | same: OI/CVD/NetDelta not in repo data, chart-only |

## Invalidation / falsify
- 30m/1h StochRSI K at 94-100 = overbought on the short TFs: a 15m/30m flush back under 80,250 with StochRSI K crossing down invalidates the "5h+ sustained reclaim" claim (10-26 03:50Z pattern).
- If 1d closes 10-27 RED the 4d/5d RED streak extends; the recovery then counts as a higher-TF counter-move, not a flip.

## What this set teaches (multi-TF consistency usage)
- The set is one question at four timeframes: direction is the consensus check, overbought/oversold placement is the timing check. This set = direction ALL-UP + timing SHORT-TF-OVERBOUGHT = recovery is real but stretched at the low end.
- Cross-check vs WaveTrend (0c6104038bb5 read, same moment): 1D WT down-cross 10-23 is the higher-TF constraint the CoinGlass set is working under; 4h WT up-cross 10-27 is the first flip on the ladder between them. 2h CoinGlass StochRSI up-cross = the next rung below the 4h.
