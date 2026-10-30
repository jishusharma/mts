# Support break after lower highs: how far does it go? (2026-10-30)

Descriptive counts only: no fees, no edge claim. Definitions in the header of `study.py` (all OURS). Data: Binance BTCUSDT perp 1m rolled to 4h, DEV 2022-01 to 2025-12.

Trigger: the operator (10-30). Analyst Michael (Pizzino) tracked lower highs and named the breakdown targets:
- 10-23 CBP row: "I expect a decline to 78 thousand, with the main support zone at 75 thousand in mind."
- 10-26 CBP row: the major support is the September 15 bottom around $75,000.
- What happened: price broke 10-29 and made a perp low of 76,444 (spot 76,500) on 10-30.

Both rows were in `F:/CryptoScrapper/cbp_store/rows.json` before the break. The Eagle_Eyes reads did not consult them.

## Counts (4h; S = 10-day low; H = pattern height above S)

| Break type | n | Median H | Drop reached 0.5 H | 1 H | 1.618 H | Back above S within 24 h | Median max drop |
|---|---|---|---|---|---|---|---|
| After >= 3 falling 4h highs | 22 | 8.4% | 73% | 36% | 18% | 50% | 0.83 H |
| Any other 10-day-low break (control) | 44 | 8.9% | 48% | 18% | 9% | 70% | 0.47 H |

Reading:
- **A break that follows a lower-high staircase travels further:**
  - It reaches half the pattern height 73% of the time vs 48% for other breaks.
  - It reaches the full height 36% vs 18%.
  - Other breaks were back above support within 24 h 70% of the time, vs 50% after lower highs.
- **The 24 h snap-back did not cancel the move:** lower-highs breaks that closed back above support within 24 h still reached 0.5 H in 73% of cases.
- **n=22 is small.** This is the measuring frame, not a proven rule. Michael's staircase was on the daily (weekly highs 87.4k, 87.2k, 87.0k, 84.4k/84.9k, 81.97k). The daily needs its own count; it will have even fewer cases.

## The 10-29 break, measured in real time with this rule

- Break bar: 4h close 77,992 (10-29 20:00Z) under S = 79,221.
- On the 4h the last three highs were not falling (81.3k, 81.8k, 81.8k), so the 4h rule called it a control break. The staircase was visible only on the daily, where Michael read it.
- Height H = 2,602:
  - 0.5 H = 77,920: hit.
  - 1 H = 76,618: hit (low 76,500).
  - 1.618 H = 75,010: Michael's 75k, not reached so far.
- With the 4h control rates, 1.618 H is a 9% branch. With the lower-highs rates, it is 18%.

## Next

1. **Eagle_Eyes reads analyst levels on every set** (role file updated): `cbp.query(since_days=5)`, quote each analyst's named levels next to the measured break targets.
2. **CBP stopped after 10-28** (stamp: last run 10-28 EU). Card `cbp-daily-firing-gap` records it.
3. **Daily-scale lower-highs count, and score Michael's call** when the 7-day window closes (11-05).
