# PRE_REG - Jala 400D close trigger study (FROZEN before any forward return was computed)

Card: jala-400d-close-trigger-study. Only event COUNTS (count_events.py) were seen before this freeze; no returns.

## Quoted source (method_jala.md, SOURCED)
- L4-6: "We are nestled between the 400 daily and the 100 weekly. ..."
- L16-17: "Of course, the iron dome is the 200 to 400 simple day moving averages crossing over."
- L22-23 (also L79): "A close under the 400. Now, this is crucial. If we close beneath the 400, then that very well may indicate and confirm a failed cup and handle." Invalidation = "daily close under 400 SMA / loss of Iron Dome".
- L10-11: "if we pass this 400 ... and we keep it as a support line" (close over = support).

## Parameters
| Item | Value | Label |
|---|---|---|
| SMA lengths | 200 and 400 daily, simple | SOURCED |
| Trigger "under" | close[t] < SMA400[t] and close[t-1] >= SMA400[t-1] | OURS (first-close definition of "close under") |
| Trigger "over" | close[t] > SMA400[t] and close[t-1] <= SMA400[t-1] | OURS |
| Trigger "golden" | SMA200 crosses above SMA400 (diff>0, prev<=0) | OURS reading of "200 to 400 crossing" |
| Trigger "death" | SMA200 crosses below SMA400 | OURS |
| Traded side | under, death = short; over, golden = long | OURS |
| Entry/exit | entry at the trigger day close, exit at close t+h | OURS |
| Horizons h | 10, 30, 60 calendar days | OURS |
| Round-trip cost | 0.20 % (spot taker 0.1 % x 2), fee-net = side*ret - 0.002 | OURS |
| Universe | BTC; 20 alts: ETH BNB XRP ADA DOGE SOL DOT LTC LINK BCH XLM TRX ETC ATOM VET FIL ALGO AVAX MATIC UNI (large caps listed on Binance spot by 2020-10; chosen with 2026 hindsight, survivorship bias acknowledged, no delisted coins) | OURS |
| Data | Binance spot 1d klines (data.binance.vision), UTC day close | public |
| Window | DEV 2022-01-01 .. 2024-07-01 (splits.py). Events must be in DEV and exit t+h < DEV_END. Bars before 2022-01-01 (from 2020-06) are used ONLY to compute the SMAs. VALIDATION/HOLDOUT never loaded (fetch stops 2024-06-30). | SOURCED (splits.py) |
| Null | 2000 draws; per draw, for each symbol pick as many random eligible days (DEV, SMA400 defined, exit in DEV) as the symbol has events, same side and h; compare pooled mean fee-net | OURS |
| CI | 2000-draw bootstrap of ISO-week blocks of events, 95 % percentile | OURS |
| Seeds | null 7, CI 11 | OURS |

## Test
Cells: universe {BTC, alts pooled} x h {10,30,60} x triggers {under, over, golden, death} = 24 (card said 2 triggers; the Iron Dome cross is split into golden/death and close-over added: DECISION OURS, m is larger = more conservative). m = 24 Holm family.
Statistic: mean fee-net forward return of events minus the null; p = two-sided share of null means at least as far from the null mean as the event mean; Holm over m=24.
Verdict per cell: PASS = Holm p < 0.05 AND event mean fee-net > 0 AND CI lower > 0. FAIL = CI upper <= 0 OR (n_events >= 20 and Holm p >= 0.05 and mean <= 0). Otherwise INCONCLUSIVE. Cells with fewer than 5 events (all BTC cells, n=1-2) are reported as n only: INCONCLUSIVE (underpowered), no inference.
Not tested: any parameter other than the above; no post-hoc trigger, side, horizon or universe changes.

## Gate
Events (DEV, count only): alts under 155/146/146, over 158/155/155, golden 25/24/24, death 20/20/20 at h10/30/60; BTC 1-2 each.
`prereg_gate.py --n 20 --sd 0.27 --cost 0.002 --m 24`: MDE 0.237 + cost 0.002 = 0.239 < 0.30 -> PASS (n 24 -> 0.218, n 146 -> 0.090). sd 0.27 = OURS assumed 60-day crypto return sd (0.035 daily x sqrt(60)), not measured from this data.
Caveat (stated before the run): events cluster in a few bear-market weeks (2022), so effective independent n is far below the raw counts; the week-block CI is the honest read.
