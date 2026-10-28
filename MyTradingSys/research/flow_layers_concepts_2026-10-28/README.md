# Flow layers as concepts: CVD, net delta, OI, net longs/shorts, top-trader ratios (BTCUSDT, 2026-10-28)

Author: Eagle_Eyes (observer; no trade advice, no edge claim, no VALIDATION or HOLDOUT).
Operator intent (relayed by the Malkan RSI divergence detector session): see how the layers used before (CVD, net delta) combine with
net longs/shorts and the top-trader ratios, around the US open. Simple facts first; correlations and deviations are CONCEPTS to test later.

Source: CoinGlass tv pages, Binance BTCUSDT perpetual, UTC axis. Shots are in the local shot store (not in the repo).
Tags: OBSERVED = read off a shot (id cited). NOT_IN_DATA = not in any shot or file I read.
Values are legend or pane readings, not recomputed: the Binance fapi fetch timed out from this host five times today (legends UNVERIFIED).
Units of the CoinGlass net longs/shorts panes are not shown on the pages (NOT_IN_DATA); I compare direction, not size.

## 1. The 13:49 / 13:50Z moment as ONE set

Shots 25118992aa7b (13:49:39Z, countdown 00:21) and 2404e2409c2c (13:50:31Z, countdown 00:29): complementary panes, same window 12:50 to 13:55Z, 52 s apart.

| Pane | Plain reading |
|---|---|
| Price | 80,435.4 then 80,435.7; fell from the 13:35-13:36 high (about 80,890) to a new low; below VWAP 81,152.8 (legend) since about 12:15 |
| BB(20,2) | 80,413.1 / 80,672.3 / 80,931.6; price at about 4% of the band, on the lower edge after leaving it downward at about 13:45 |
| RSI14 / SMA14 | 31.43 / 46.78; peaked with price at 13:35-13:36, crossed under the 40 line at about 13:45-13:46 |
| StochRSI | 2.94 / 0.98, at the floor |
| Volume | one large red bar at about 13:47; SMA9 7.486M |
| Open interest | 96.994K, window high; one big step up at the 13:30 bar, flat through the drop, up again on the last bars |
| CVD candles | -1.093K; rose from about -1.2K to about -0.4K between 13:30 and 13:36, then fell to -1.093K |
| Net delta | -2.189K; red bars through the drop, red bars also at 13:31-13:32 while CVD was rising |
| Net Longs (New) | 696.516, up on the last bar after a large green bar at 13:30 |
| Net Longs (open) | -221.182, unchanged across all four legend values |
| Net Shorts (New) | 600.886, up on the last bar (green) |
| Net Shorts (open) | 634.741, up on the last bar (green) |
| Top trader accounts | 2.0350 (candles 2.0404); steps up between about 13:25 and 13:41, flat after |
| Top trader positions | 1.8340 (candles 1.8335); steps up at about 13:30 and 13:35, flat after |

## 2. Simple facts

| # | Fact | Tag |
|---|---|---|
| F1 | Price, RSI and CVD candles all topped in the same bar (13:35-13:36) and fell together to 13:50 | OBSERVED 2404e2409c2c |
| F2 | RSI went under 40 in the same bar where price left the lower BB downward (about 13:45-13:46) | OBSERVED 2404e2409c2c |
| F3 | At the 13:30 bar CVD candles and net delta moved opposite ways: CVD up, net delta red | OBSERVED 2404e2409c2c, a1afe7a835c8. What differs between the two series is NOT_IN_DATA |
| F4 | OI stepped up in the 13:30 bar (about 96.4K to 96.8K) and stayed up while price fell 13:36-13:50 | OBSERVED 2404e2409c2c, a1afe7a835c8 |
| F5 | OI window high (96.994K) at the price low; in the 12:15-12:30 drop OI fell to about 96.0K instead | OBSERVED 2404e2409c2c, a1afe7a835c8 |
| F6 | All four net longs/shorts series rose from 13:21 to 13:41 (price +48) and Net Longs (New), Net Shorts (New), Net Shorts (open) rose again 13:41 to 13:49 (price -304); Net Longs (open) stayed flat at -221.182 | OBSERVED d53ffeabb69b, 73ed3923c61b, 25118992aa7b |
| F7 | Top-trader accounts and positions rose with the 13:30 bounce (1.9900 to 2.0350 and 1.8070 to 1.8340, 13:21 to 13:41) and did not step down in the 13:41-13:50 drop of about 300 points | OBSERVED d53ffeabb69b, 73ed3923c61b, 25118992aa7b |
| F8 | Price at 13:50 is below its 12:30 low; the top-trader ratios are well above their 12:30 level (accounts about 1.92-1.94 read from pane position there; 2.0350 now) | OBSERVED 73ed3923c61b (the 12:30 level is a pane reading, not a legend) |
| F9 | The 08:30 spike (price to about 81,700) came with Net Shorts and Net Shorts (New) dropping sharply for about 5-10 minutes, then recovering | OBSERVED 73ed3923c61b, 44f3baea8a55 |
| F10 | Lead/lag in minutes between the top-trader steps and price: the ratios step at the source period, so lead/lag finer than that is NOT_IN_DATA; no step led price by a readable amount at 1m | NOT_IN_DATA |
| F11 | CVD and net delta values from shots with different left edges (13:41 shot starts 08:30, 13:50 shots start 12:50) are not like-for-like if the series is anchored to the visible window. My earlier "CVD -355.6 to -1.093K" comparison is withdrawn; only within-shot moves are used here | NOT_IN_DATA (anchor of the series) |
| F12 | Whether any of these layers led price at the 13:30 move: the first 1m bars of the 13:30 candle show OI, CVD and price moving in the same bar; no layer is seen leading by a bar | OBSERVED 2404e2409c2c |

## 3. Earlier shots, grouped by phase (10-28 unless stated)

### Prior day, context (10-27 16:07Z)
| Shot | Line |
|---|---|
| c4e9667bc1f6 (2h) | Top-trader accounts 2.2860, positions 1.9600, falling from a peak around 10-27 12:00; Net Longs (New) -13.029K, Net Shorts (New) 14.287K; price 80,495.8. OBSERVED |

### Pre-US-open (before 13:30Z)
| Shot | Time Z | Line |
|---|---|---|
| 15f7d1cc4742 (15m) | about 10:44 | Price 81,528.6, above where the window started (about 80,000 on the 27th) while top-trader accounts fell from the left edge to 1.9330 and positions to 1.7720 (a step down near 28th 00:00). Net Longs (New) 2.206K, Net Shorts (New) 4.306K. OBSERVED |
| 42a1dabbd4ba (5m) | about 10:45 | Same panes at 5m: accounts 1.9330, positions 1.7720, flat; net series slightly positive at the right edge. OBSERVED |
| d6bcf9a2908a (1m) | about 10:51 | Price 81,502.7 in a narrow band (BB 81,464.6-81,565.3), RSI 47.16 vs SMA 55.37, StochRSI 4.85/25.89 falling; OI 96.56K rising slowly; CVD +82.9; net delta -864.5. OBSERVED |
| fdd8e33fad4c (1m) | about 11:14 | Price 81,344.1 under VWAP 81,404.5; Net Longs (New) 523.989 sliding; accounts 1.9300 and positions 1.7650 (a step down at about 10:30). OBSERVED |
| 44f3baea8a55 (5m) | about 13:16 | Price 80,671.3 under VWAP 81,105.2 after the 12:15-12:30 drop; Net Longs (New) -2.731K and Net Shorts (New) -1.148K, both recovering from a dip at 12:15; accounts 1.9900, positions 1.8070. OBSERVED |
| d53ffeabb69b (1m) | about 13:21 | Price 80,691.5; Net Longs (New) 288.91 (red); accounts 1.9900, positions 1.8070 (rising since about 12:30). OBSERVED |

### US open (13:30Z and the next 15 minutes)
| Shot | Time Z | Line |
|---|---|---|
| a1afe7a835c8 (1m) | about 13:41 | Bounce from about 80,533 to 80,889 then 80,763.5; OI 96.859K (step up at 13:30); CVD -355.63; net delta -2.086K, stepping down at 13:30 while CVD rose; RSI 54.07 / SMA 55.45; StochRSI 51.43 / 59.15 turning down. OBSERVED |
| 73ed3923c61b (1m) | about 13:41 | Net Longs (New) 662.4 and Net Shorts (New) 466.4 rising into the bounce; accounts 2.0350, positions 1.8340 at their highest of the visible window. OBSERVED |

### After (13:36Z onward)
Section 1 and facts F1-F8.

## 4. Candidate CONCEPTS to test later (no edge claim, no trade advice)

1. When OI rises while price falls into the lower Bollinger Band, the move is new positions rather than closing, and when OI falls in the same kind of drop it is closing; the two drops today (12:15-12:30 and 13:36-13:50) show both cases.
2. CVD and net delta are two separate flow series that can disagree on the same bar (13:30), so which of the two the other layers follow needs testing before either is used alone.
3. The top-trader long/short ratios move slowly and opposite to the hours-long price swing (down while price rose from 10-27 16Z to 10-28 10:45Z, up while price fell since), and they did not react to the 1-minute drop at 13:36-13:50; test their lead/lag against price on 15m to 2h bars before looking at them on 1m.

## 5. Gaps

- Legends are not recomputed (Binance fapi unreachable from this host); band symmetry only.
- The anchor and units of CVD, net delta and the net longs/shorts panes are not shown on the pages.
- Engine, HALT and Tom state are NOT_IN_DATA here (live mirror points at another host).
- The heatmap shots (1H to 1D) show a different layer and are not used here.
- One session, one day; nothing here is evidence of an edge.
