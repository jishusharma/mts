# Item 4: offline engine replay of 2026-10-29 (UTC), BTCUSDT 1m

Run 2026-10-29 ~19:40Z (the day was still open: 1,178 bars, 00:00Z to 19:37Z). Engine = `MarketDataSnapshot.fetchHistoricalSnapshot` in archive mode (the same snapshot + `SetupCandidatesBuilder` path the live launcher uses, fed from CSV instead of REST), one call per 1m bar, asOf = bar open + 1 min (no look-ahead). Flags: (a) `-Dmts.pitchfork=true` (the only -Dmts.* in `scripts/core/start-trading-day.ps1`, lines 113, 445, 475), (b) a + `-Dmts.spikeFade=true`. Harness: `ItemFourReplay.java` (built to %TEMP%, src/ untouched), `item4_summarise.py`, `replay_prep_spot_days.py`. Per-bar CSVs: `item4_bars_2026-10-29_hybrid.csv`, `item4_bars_2026-10-29_perpproxy.csv` (about 155 KB each). Raw klines stay in %TEMP%\wave1_replay.

## Data and market labels
| Piece | Source | Market |
|---|---|---|
| 2026-09-10 to 10-21 | local `Dumps/backtest/raw/klines` | USD-M perp (futures/um) |
| 2026-10-22 to 10-27 | data.binance.vision daily zips | perp |
| 2026-10-28, 10-29 | data-api.binance.vision `/api/v3/klines` | SPOT. perp daily zips 404 for 10-28/29 (published next day) and fapi.binance.com times out |
| Run "hybrid" | perp to 10-27, spot after | mixed: spot is about +34 above perp (median close gap on 10-27, 1,440 bars both markets; range 19 to 52) |
| Run "perpproxy" | same, 10-28/29 OHLC minus 34.22 | PROXY for perp, not real perp data |

81,953.7 (Eagle_Eyes notes, BACKTEST_CANDIDATES C14/C15 and SCENARIO_LEDGER) has a 0.1 tick, so it is a perp-style figure. Spot 10-29 high is 81,971.00 at 16:09Z; perp proxy high is 81,936.78; the real perp high is not reproducible here (gap to the quoted figure is 17, inside the 19-52 basis range). The quoted number was not found in any local archive.

## Answers
| Question | Answer |
|---|---|
| Did the family-A fade (SpikeFadeDetector A1) fire near the high? | YES, with spikeFade on: 5 bars, 16:06 to 16:10Z (asOf 16:07 to 16:11), zone 81,900.0 then 81,971.0 (spot) / 81,865.78 then 81,936.78 (perp proxy). Same 5 bars in both runs. Not fired earlier (15:30-16:05) and not after 16:10. |
| Why not earlier 15:30-16:05? | Gate A-C2 (close above prior day's high) failed: closes 81,431 to 81,822 vs 10-28 high 81,823.0 (spot). A-C1 (leg 1.76 to 2.08 % vs median 0.54 to 0.60 %) passed all that time. First pass at 16:06, close 81,826.01 = 3.01 above 81,823.0. |
| Why did it stop at 16:11? | 16:11 close 81,794.0 fell back under 81,823.0: A-C2 failed. |
| Knife-edge? | Yes. A-C2 passed by 3 to 70 dollars only; the market mix (spot vs perp) of the prior-day high decides it. The perp proxy gives the same 5 bars (margin 3.0 at 16:06), but a real perp series could differ by a few dollars. |
| Counts per family, (a) pitchfork only | bars with any candidate 512 of 1,178; core 512; fadeA1/A2/A3/profile 0; pitchfork 0. Winner mix: ct_short 292, tc_long 77, ct_long 60, scalp_short 54, scalp_long 29. |
| Counts per family, (b) + spikeFade | any 517; core 512 (identical to a); fadeA1 5; fadeA2 0; fadeA3 0; profile 0; pitchfork 0. |
| Does spikeFade change the result? | Only on those 5 bars (candidate list differs on 5 of 1,178; core part and its scores differ on 0). In those 5 bars core had 0 candidates, so the fade is rank 1 by default. Fade candidates are appended after the core top-3 (never score-ranked; raw score fixed at 0), so wherever a core candidate exists it keeps rank 1. |
| Winner timeline 15:00-16:30Z (b) | 15:00-15:08 tc_long; 15:09-15:18 none; scattered tc_long at 15:19, 15:21, 15:23; 15:29-15:31 ct_short @81,343.5 (score 50); 15:39-15:43 tc_long; 15:49-15:53 tc_long; 16:01 tc_long; 16:06-16:10 fade_short A1; 16:12-16:13 tc_long; 16:14-16:20 and 16:22-16:27 ct_long @~81,674 down to 81,584 (score 71 to 81); the rest none. (a) is identical except 16:06-16:10 = none. |
| Max-high bar | 16:09Z, high 81,971.0 (spot). With flag on, A1 fires there (zone 81,971.0, rank 1, net R:R 11.31); with it off: no candidate. |
| Why does 16:09 have no core candidate? | Not traced per zone (core zones need distance under cap and a stop swing beyond the zone). Core is empty on 666 of 1,178 bars. |
| Pitchfork | 0 candidates on the whole day. `PitchforkSignalLayer.detect` needs at least 15 4h bars (line 353) but the snapshot supplies `4h` with limit 3 (`MarketDataSnapshot` lines 489 live, 1338 as-of). So `-Dmts.pitchfork=true` is inert in this path, not just on this day. |
| Profile arm A-C3 | 0: not thin on the leg, or volume check. Not traced further. |

## Hand check (spec formulas, not the code)
* Fade net R:R at the 16:09 bar, from the CSV bars with my own script and FORMULAS.md section 17: session open 06:00Z (07:00 Berlin, CET since 10-25) = 80,234.14 (target, A-T1); high 81,971.0 (entry); stop = lowest of the 20 prior Berlin-day highs above 81,971.0 = 82,035.3 (A-S1; max prior 84,875.2); cost = 2 x 0.0005 x 81,971.0 = 81.97; net = (1,736.86 - 81.97) / (64.3 + 81.97) = 11.31. Engine: 11.31. Match. (Gross 27.0: the target at the session open is 1,737 points away, so the R:R figure is not tradeable information.)
* Core score at 16:14 (ct_long @81,674.29): engine score 81, proof_count 3, confluence bonus 10 = 50 + 7 x 3 + 10 = 81. Matches the documented formula (dsa_task_012 / PROVENANCE_AUDIT_TOM A15; constants are NO-SOURCE, OURS). The proof count itself was not recomputed.
* A-C1 at 16:09: leg = (81,971.0 - 80,234.14) / 80,234.14 = 2.1647 %; engine trace 2.1647 %. Median of 20 prior same-clock legs 0.5965 %.

## Blind families (inputs not in public klines)
| Family / item | Missing input | Effect |
|---|---|---|
| Core proof `cvd_aligned` | aggTrades net delta (`trade_flow.net_delta_*` = null, UNAVAILABLE) | never counted: all core scores sit lower than live. Delta-based proofs (absorption, finished auction, delta flip) use kline taker-buy volume (present) |
| Core book_imbalance proof | order book depth | null (not counted by rule B131 anyway) |
| Naked-POC zones | `runtime_data/naked_pocs` (live state, harness cwd is empty) | those weekly-level zones missing |
| Family A proofs A-P1, A-P3, A-P6, A-P8, A-P9, A-P10 and conditions A-C3, A-C4 | tape, order book, OI, sentiment | listed `not_in_data` by the engine; only A-C1, A-C2 and A-P2/P4/P5/P7 from OHLC are tested. Profile arm needs A-C3 (thin leg): 0 emitted |
| Pitchfork | needs 15 4h bars, snapshot has 3 | blind by construction, both live and replay |
| Everything fed by OI, funding, liquidations, basis | not in the historical snapshot | not candidate gates here; `funding_extreme` false, `oi_trend` flat, clusters 0 |
| Perp 10-28/29 prices | perp zips not yet published, fapi unreachable | spot used; proxy shift applied in the second run |

Rerun when the 10-29 perp zip is published (data.binance.vision, normally the next UTC day, so 10-30 ~ 00:00Z+): drop `BTCUSDT-1m-2026-10-28/29.csv` (perp) into `%TEMP%\wave1_replay\raw\klines`, and the full day (to 23:59Z) is covered; run `java -Dmts.pitchfork=true [-Dmts.spikeFade=true] -cp <out;target/classes;jars> datafeed.ItemFourReplay <raw> <out.csv> 2026-10-29 <label>` from an empty cwd.

Caveat on the gate trace: `fade_gate` re-states the detector gates in the harness as a diagnostic; its 5 "PASS" bars equal the 5 engine A1 candidates, bar for bar. Fills are not modelled (a candidate is a signal, not a trade).
