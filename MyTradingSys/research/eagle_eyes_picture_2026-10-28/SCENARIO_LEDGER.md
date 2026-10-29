# Scenario ledger (Eagle_Eyes, BTCUSDT perp, Binance)

Every A/B map Eagle_Eyes gives the operator, scored after the fact. Purpose: measure whether the "if up / if down" maps anticipate anything, before any of it goes into MTS. Levels and rules are OURS; outcomes read from the operator's CoinGlass shots (pixel reads).

| Given (UTC) | Map | Confirm / kill as written | What happened | Score |
|---|---|---|---|---|
| 10-29 ~02:20 | A: down to 79,542 then 78,000. B: squeeze to 80.4k then 81.0-81.3k | A killed by reclaim 81.3-81.6k with OI up and CVD up | 14:30Z push 79.9k to 81,953.7 with OI 95K to 98K and CVD up: A killed, B hit and overshot by about 650 | B right on direction, size under-called; A (marked more likely) wrong |
| 10-29 16:55 | A: break-and-retest toward 80.8k / 80.4-80.6k as longs unwind. B: 81.2k buyer holds, retest 81.6-81.95k | A confirms on 5m close < 81.1k with net delta red and OI falling | By 18:57Z: 80,577 at the 5m lower BB; OI 98K to 93.73K; net delta 2K to 102; CVD +2.5K to -1.07K | A right (more likely, confirmed as written) |
| 10-29 20:05 | A: sweep the US-window low 79,916 (then reclaim or not). B: back above the US high 81,971 first | MEASURED base rate (`us_rally_fade_next24h.py`, n=137): low first 64%, high first 24%, neither 12%; 24h close up 52% (coin flip) | 20:47Z low 78,297 swept 79,916 by 1.6k; the bounce topped at 79,811, never near 81,971 | A right (the side the base rate favoured); the 24h close part is a coin flip and not scored |
| 10-29 21:47 | Base rates only, no side marked more likely: bounce faded back near the 78,297 low; low breaks within 1h 16%, within 4h 43% (followup.py, n=116). 23:05-23:38 OI build-up with flat price: next +/-0.5% 38/39 (oi_side study) | none (descriptive) | 23:45Z spot low 77,916: broke about 2h after the read, after a 5m BB squeeze 22:30-23:30 with OI +1K into the drop | Inside the 43% branch; not counted in the more-likely tally (no side was called). Coil and OI said a move was loaded, not its direction |

Running count: 3 maps, the "more likely" side right 2 of 3. Too few to mean anything; the ledger exists so the count grows.

Observation logged with the second row: OI ended (93.73K) below its pre-rally level (about 96.5-97K at 13:30Z) while price held about +0.4% above the pre-rally base. More positions closed than the rally opened.
