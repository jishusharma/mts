# REPORT: liquidation-flush reversal, 10 Bybit perps pooled (edge-oi-flush-1113, 2026-11-13)

**Verdict: FAIL** (pre-registered pass rule, 0 of 10 cells). Closest: 4h-bar flush, 12h/24h hold: VALIDATION fee-net mean positive and CI above zero, but it does not beat the placebo and does not repeat in RECENT. PRE_REG.md was committed before any outcome was computed.

Data (Bybit v5 public): OI 1h start date per coin: BTC 2020-07-20, ETH/LINK/LTC 2020-10-21, ADA 2021-03-18, XRP 2021-05-13, DOGE 2021-06-02, SOL/BNB 2021-06-29, AVAX 2021-09-15 (klines start later for ETH 2021-03-15, SOL 2021-10-15). Events after 24h dedup per coin: 1h bars 1106, 4h bars 262 (summary.json). Events listed in events.csv; full table results.csv (all cells x splits x long/short/both).
Costs: fees.BINANCE_TAKER*2 plus actual funding. Entry = next bar open. Pooled across coins on the same days, so day-cluster bootstrap (5000 reps) is the unit; BH 10% over the 10 primary VALIDATION cells (n<30 -> p=1).

## VALIDATION 2024-07..2025-06, both sides pooled (fee-net mean per event, day-cluster 95% CI)
| TF | exit | n (days) | mean | CI | placebo mean | event minus placebo, CI | BH | verdict |
|---|---|---|---|---|---|---|---|---|
| 1h | 4h | 139 (78) | -0.22% | -0.83, +0.38 | -0.45% | +0.23, -0.41..+0.86 | no | FAIL |
| 1h | 12h | 139 (78) | +0.15% | -0.77, +1.07 | -0.97% | +1.12, +0.17..+2.11 | no | FAIL (CI) |
| 1h | 24h | 139 (78) | +0.89% | -0.53, +2.51 | -0.09% | +0.98, -0.66..+2.74 | no | FAIL |
| 1h | 72h | 139 (78) | +0.15% | -1.47, +1.72 | +0.82% | -0.67 | no | FAIL |
| 1h | bracket 2R | 139 (78) | -0.42% | -0.92, +0.10 | -0.36% | -0.06 | no | FAIL |
| 4h | 4h | 48 (19) | +1.22% | -0.22, +2.99 | +0.55% | +0.80, -3.37..+3.95 | no | FAIL |
| 4h | 12h | 48 (19) | +3.91% | +1.49, +6.40 | +0.63% | +3.45, -2.80..+7.61 | yes | FAIL (placebo CI) |
| 4h | 24h | 48 (19) | +4.48% | +1.20, +7.58 | +2.36% | +2.20, -5.00..+6.79 | yes | FAIL (placebo CI) |
| 4h | 72h | 48 (19) | +3.54% | -0.23, +6.53 | +4.25% | -0.65 | no | FAIL |
| 4h | bracket 2R | 48 (19) | +1.90% | -0.48, +4.63 | -0.55% | +3.00, -0.42..+6.42 | no | FAIL |

## Reading
- 1h flush: no fee-net edge in any split at any hold; RECENT is negative at 24h (-0.75%, n 260). The OI condition adds a small positive amount over placebo at 12h/24h in DEV and VALIDATION (+0.4/+0.7 pp, +1.1/+1.0 pp) but not in RECENT; placebo here is itself negative, so that is the placebo being bad, not the flush being good.
- 4h flush: VALIDATION is 19 days of one market episode; 48 events, many coins on the same day. DEV 12h +1.07% (CI -0.08..+2.39, n 177, 84 days), RECENT 12h +0.39% (n 37), 24h -0.88% (n 37): the effect shrinks as data are added. Placebo diff CI spans zero in every split except DEV 12h (+1.46%, CI lower +0.22, not the pre-registered split for pass).
- Bracket: fee-net negative at 1h in VALIDATION (-0.42%, hit rate 24%); no 4h bracket CI above zero.
- Sensitivity (entry one bar later, outside BH): 4h 12h/24h VALIDATION mean falls to +2.2% (from +3.9/+4.5%); 1h unchanged in sign. So part of the 4h number is the first bar after the flush.
- Long-only and short-only rows are in results.csv, descriptive, not tested for pass.

Regime mix: per-split event counts above; no regime classification was computed (OURS), the VALIDATION window contains the 2024-08-05 crash and the 2025-03/04 selloff, which likely supply most of the 19 days.

Best next test (not run): 4h flush, 12h hold only, adding the 2020-2021 coin history and more coins (top 30) to lift VALIDATION n above ~150 independent days, with per-episode (week) clustering; gate on DEV 12h diff vs placebo.
