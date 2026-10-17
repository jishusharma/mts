# Krown recall check: RESULT (rules fixed before the run) (PRE_REG_KROWN item 3)

Data: Binance spot BTCUSDT 1d and 1w_from_1d, Coinbase BTC-USD 1d (weekly built Monday-start, full weeks), all from
`F:/MTS/data/krown_daily` (DATA_MANIFEST.csv: every zip matched its published checksum). Only bars with open time before
2024-07-01 UTC are loaded (DEV); VALIDATION and HOLDOUT are not read. Detector parameters stay at v0.

**Pass bars (OURS, from PRE_REG_KROWN item 3, restated):**
1. RECALL: detector fires within 2 bars (either side) of the example's target bar for at least 6 examples that verify against klines.
   Strict count = every verified example, an example with no v0 detector counts as a miss. A covered count (verified
   AND a v0 detector is mapped) is shown next to it, never instead of it.
2. FIRE RATE: per setup S1..S9 pooled on Binance 1d DEV, at most 1.0 event per 10 daily bars. Weekly rates are shown for information.
3. Chance baseline per row: share of all bars of that series that have a matching event within 2 bars (so a hit is read against it).

**Verification rule per example** (a caption is not evidence; the klines are). Tolerances are OURS and fixed here:
- R01 VOL-13 weekly low March 2020: target = lowest-low week among weeks opening 2020-02-17..2020-04-13 (Binance 1w); verified if that week's volume >= 2.5x the mean of the prior 20 weeks (he says 3 to 3.5x). Detector: any long event S1-S8, 1w.
- R03 TRL-20 Dec 2018 anchor respected Mar 2020: verified if the Mar 2020 weekly low is above the Dec 2018 weekly low and the Dec 2018 low week volume >= 2x the prior 20 weeks (Binance 1w). A trend line has no price in the caption: only these two facts are checked. Detector: none in v0 (no trend-line detector).
- R04 RNG-05 2018 range, about February to November: span 2018-02-15..2018-11-13 (Binance 1d); verified if max close / min close <= 2.0. Detector: `range_state` non-empty on >= 50% of the span's days (S3 and S4 counts shown).
- R06a-d MAV-16 weekly 200 SMA lows 2015, 2018, 2020, 2022 (Coinbase 1w, the only series long enough): verified if the cycle-low week's low is within +-15% of the weekly SMA200 (a 200-week average needs 200 weeks: 2015 and 2018 lows come before the first Coinbase week that has one = NOT_IN_DATA). Cycle-low weeks: 2020 = lowest low weeks opening 2020-02-17..2020-04-13; 2022 = lowest low among weeks opening 2022-05-01..2022-12-31. Detector: none in v0 (S5 uses the 200 SMA of its own timeframe, not a weekly touch).
- R07 MAV-21 death cross January 2022 (Binance 1d): verified if the SMA50 crosses below the SMA200 on a day in 2021-12-15..2022-02-15 and the SMA200 is lower than 30 days earlier. Detector: S5 short within 2 daily bars of the cross (S5 is the only cross setup; its 21/55 cross is a different pair from his 50/200).
- R09 TOP-12 Bitcoin 2017 weekly top (Coinbase 1w; Binance weekly has only about 17 weeks before December, too few for BBWP): target = highest-high week among weeks opening 2017-09-01..2018-03-31; verified if (a) it opens in December 2017, (b) BBWP (v0 params) >= 85 on at least 8 weeks opening 2017-05-01..target, (c) the target week volume >= 2x the prior 30 weeks, (d) weekly RSI14 (own Wilder) at the target < its maximum over the prior 12 weeks while the target high exceeds all 12 prior highs, (e) own MACD(12,26,9) crosses down within 8 weeks after the target. Detector: S9 short, 1w, Coinbase.
- R10 TOP-32 Bitcoin 2021 weekly top (Binance 1w): target = highest-high week among weeks opening 2021-10-01..2021-12-31; verified if (a) RSI14 at the target < RSI14 at the highest-high week opening 2021-03-01..2021-05-31 while the target high is higher, (b) the target week or the week before is a shooting star on raw bars (upper wick >= 2x body, body in the lower third of the range), (c) own MACD crosses down within 8 weeks after the target. Detector: S9 short, 1w.
- R12 VJZ-50 coming off the 2018 lows, 55 EMA reclaim then break, about 4,000 to 14,000 (Binance 1w, inferred weekly): target = first weekly close above the weekly EMA55 after the lowest-low week opening 2018-11-01..2019-01-31; verified if that close is within 3,000..5,000 and the highest high in the next 26 weeks is within 12,600..15,400. Detector: S2 or S5 long, 1w.
- R13 VJZ-49 about 40,000 to 52,000 (Binance 1d, timeframe inferred daily): low bar = lowest low among days 2024-01-01..2024-02-10; verified if that low is within 38,000..42,000 and the highest high in the next 30 days is within 50,500..53,500. Detector: S2, S5 or S8 long on any day from the low bar to the first day with high >= 50,500 (generous window: the caption names no signal bar).

**Dropped without a read (listed in RECALL.md):** VOL-08 (February 2026 low: HOLDOUT, sealed), SNR-17 (the 100,000 test reached
about 108,000: after 2024-07, sealed), MAV-11/MAV-15 (no date, price or extract cite in the pre-reg row), VJZ-13 (weekly 55 EMA
reclaim given up in two closes: no date or price in the caption), KCM-15 (two BBWP-high dumps: no date or price).


---

## Result

Examples listed 12 (+5 dropped without a read). Verified: 3. Recall hits within 2 bars: **2** strict (of 3 verified), 2 of 3 covered (verified with a mapped v0 detector). Bar: >= 6 strict. **RECALL FAIL**.

| id | rule | extract cite | verdict | klines evidence | result | detector / note |
|---|---|---|---|---|---|---|
| R01 | VOL-13 | `extract_UqAvU1loT_k.md:120-130` | VERIFIED | BTCUSDT_1w_from_1d.csv open_time_ms=1583712000000 (2020-03-09) O=8034.76 H=8179.31 L=3782.13 C=5361.3 V=1224228; vol/mean20 = 3.36x (rule >= 2.5x) | MISS (chance baseline 25%) | any long S1-S8, 1w |
| R03 | TRL-20 | `extract_14bxwxC8gBQ.md:183-192` | NOT VERIFIED | Dec 2018 BTCUSDT_1w_from_1d.csv open_time_ms=1544400000000 (2018-12-10) O=3548.49 H=3610 L=3156.26 C=3228.67 V=249792; vol 0.96x; Mar 2020 low 3782.13 (2020-03-09) | n/a | no trend-line detector in v0 |
| R04 | RNG-05 | `extract_6aA-P4Gvhrc.md:50-57` | VERIFIED | BTCUSDT_1d.csv open_time_ms 1518652800000 (2018-02-15) .. 1542067200000 (2018-11-13); max/min close = 1.97 (rule <= 2.0) | HIT (range_state coverage) | range_state on 56% of 272 days (rule >= 50%); S3+S4 events in span: 10 |
| R06a | MAV-16 | `extract_-NXzJs5JRks.md:157-165` | NOT_IN_DATA | 2015 cycle low precedes the first Coinbase week with a 200-week SMA (COINBASE_BTC-USD_1d.csv(weekly) row 200: open_time_ms=1557705600000, 2019-05-13); BTCUSDT_1d.csv starts 2017-08 | n/a |  |
| R06b | MAV-16 | `extract_-NXzJs5JRks.md:157-165` | NOT_IN_DATA | 2018 cycle low precedes the first Coinbase week with a 200-week SMA (COINBASE_BTC-USD_1d.csv(weekly) row 200: open_time_ms=1557705600000, 2019-05-13); BTCUSDT_1d.csv starts 2017-08 | n/a |  |
| R06c | MAV-16 | `extract_-NXzJs5JRks.md:157-165` | NOT VERIFIED | COINBASE_BTC-USD_1d.csv(weekly) open_time_ms=1583712000000 (2020-03-09) O=8037.73 H=8187.03 L=3858 C=5345.35 V=377127; SMA200w = 5512; low/SMA200w = 0.70 (rule within 0.85..1.15) | n/a | no weekly SMA200 touch detector in v0 |
| R06d | MAV-16 | `extract_-NXzJs5JRks.md:157-165` | NOT VERIFIED | COINBASE_BTC-USD_1d.csv(weekly) open_time_ms=1668988800000 (2022-11-21) O=16252.4 H=16797.3 L=15460 C=16419.9 V=191254; SMA200w = 24070; low/SMA200w = 0.64 (rule within 0.85..1.15) | n/a | no weekly SMA200 touch detector in v0 |
| R07 | MAV-21 | `extract_-NXzJs5JRks.md:197-213` | NOT VERIFIED | BTCUSDT_1d.csv open_time_ms=1642118400000 (2022-01-14) O=42558.3 H=43448.8 L=41725.9 C=43060 V=32641; SMA50 48427 < SMA200 48438; SMA200 30d earlier 46895 | n/a | S5 short, 1d |
| R09 | TOP-12 | `extract_7IxfsuD2wCM.md:126-136` | NOT VERIFIED | COINBASE_BTC-USD_1d.csv(weekly) open_time_ms=1512950400000 (2017-12-11) O=15290 H=19892 L=15200 C=19379 V=202521; conditions a-e = [True, True, False, False, True]; BBWP>=85 weeks 14; vol/mean30 1.62; RSI 90.3 vs prior-12 max 87.2; MACD down-cross 2018-01-22 | n/a | S9 short, 1w, Coinbase weekly |
| R10 | TOP-32 | `extract_7IxfsuD2wCM.md:343-350` | NOT VERIFIED | BTCUSDT_1w_from_1d.csv open_time_ms=1636329600000 (2021-11-08) O=63273.6 H=69000 L=62278 C=65519.1 V=294213; Apr-2021 high week 2021-04-12 H=64854; RSI 68.8 vs 67.6; conditions a-c = [False, False, True] | n/a | S9 short, 1w |
| R12 | VJZ-50 | `extract_vjzy_KxJ_y8.md:458-476` | NOT VERIFIED | low week 2018-12-10 L=3156.26; reclaim BTCUSDT_1w_from_1d.csv open_time_ms=1556496000000 (2019-04-29) O=5309.81 H=5900 L=5178.8 C=5775.62 V=191972; EMA55w 5454; max high next 26 weeks 13970 | n/a | S2/S5 long, 1w |
| R13 | VJZ-49 | `extract_vjzy_KxJ_y8.md:458-476` | VERIFIED | BTCUSDT_1d.csv open_time_ms=1705968000000 (2024-01-23) O=39568 H=40176.7 L=38555 C=39897.6 V=57957; max high next 30 days 52985 | HIT offset +16 (chance baseline 16%) | S2/S5/S8 long on any day low bar..first high >= 50,500 (window, not +-2) |

Dropped without a read: VOL-08 (HOLDOUT), SNR-17 (after 2024-07), MAV-11/MAV-15, VJZ-13, KCM-15 (no date or price); see rules above.

## Fire rate (v0 detectors, DEV bars before 2024-07-01)

| series | bars | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | over 1.0 per 10 bars |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT 1d | 2510 | 1 (0.004) | 92 (0.367) | 30 (0.120) | 38 (0.151) | 17 (0.068) | 66 (0.263) | 1 (0.004) | 77 (0.307) | 46 (0.183) | none |
| BTCUSDT 1w_from_1d | 358 | 0 (0.000) | 15 (0.419) | 0 (0.000) | 0 (0.000) | 1 (0.028) | 14 (0.391) | 0 (0.000) | 9 (0.251) | 2 (0.056) | none |
| COINBASE BTC-USD 1w_from_1d | 467 | 0 (0.000) | 13 (0.278) | 0 (0.000) | 0 (0.000) | 3 (0.064) | 16 (0.343) | 0 (0.000) | 10 (0.214) | 6 (0.128) | none |

Cells: events (per 10 bars). Ceiling applies to the Binance 1d row; weekly rows are for information.
**FIRE RATE PASS** (Binance 1d pooled).

## Decision (OURS)

Recall misses the bar. Only 3 of 12 listed examples verify against klines, so even a perfect encoding could reach 3 hits: the bar of 6 is unreachable on this check set, and the shortfall comes from the examples (caption dates, prices and volume or slope claims that the klines do not show), not from the detectors. Per the card, examples that do not verify are dropped, not fixed, and v0 parameters are NOT retuned to chase hits (no encoding variant is run; the ledger records one iteration, RC-I1, v0 unchanged). Missing v0 detectors surfaced (each needs its own spec and pre-registration before it exists): trend-line anchor (TRL-20), weekly 200 SMA touch (MAV-16), 50/200 SMA cross (MAV-21). Consequence for the Krown G3 step: the recall gate is FAIL on evidence, not a pass.

