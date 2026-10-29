# Pre-US Bollinger contraction: what the US session does next (BTCUSDT 15m, 2022-01..2026-09)

Ask (operator, 2026-10-30, shot 0241bf1e7e8d): "just before the US session, price is contracting ... what happens when the price
contracts? ... up, down and sideways ... depending on the phase that Bitcoin is in ... not to find an edge, but just understand."
Script `study.py` (definitions in its header, fixed before the first run, one run). Descriptive, no fees, all thresholds OURS.
Phase = F6 option A (weekly close vs SMA10 and its slope), reused from `research/context_factors_2026-10-16/CONTEXT_FACTORS_SPEC.md`.

Box = the 8 h before the US cash open (13:30Z in US DST, else 14:30Z). Outcome = 15m close 4 h after the open: above the box (UP),
below (DOWN), inside (SIDEWAYS). Squeeze = BandWidth at the open in the lowest 20% of the prior 30 days; wide = top 20%.

| Pre-US state | n | UP | DOWN | SIDEWAYS | Broke both sides | First break held | US range / box range (median) |
|---|---|---|---|---|---|---|---|
| Squeeze | 192 | 29% | 29% | 43% | 23% | 52% | 1.54x |
| Middle | 800 | 25% | 29% | 47% | 16% | 51% | 1.26x |
| Wide | 223 | 18% | 23% | 59% | 4% | 50% | 0.80x |

## What it says
1. **A squeeze predicts size, not side.** After a pre-US squeeze the US 4 h range is about 1.5x the box (0.8x after a wide box).
   Up and down are 29% each.
2. **The first break is a coin flip.** It held to the 4 h close 52% of the time; 23% of squeeze days broke BOTH sides (whipsaw),
   against 4% after a wide box. 10-29 was this case: break up, then the move given back.
3. **Phase (F6) does not change the direction** beyond noise. Squeeze rows: markup 28/35/37 (n=79), markdown 28/24/49 (n=72);
   distribution (n=17) and accumulation (n=21) are too small to read.
4. **Year matters more than phase.** Squeeze UP share: 2022 23%, 2023 14%, 2024 53%, 2025 28%, 2026 22% (n 18-53).
   2024 was the ETF bull year. The trend of the year shows up; the weekly-SMA phase label does not capture it.

## Phases: what is measurable (OURS)
- Trend vs range and bull vs bear can be measured from price (moving averages, slope, BandWidth).
- "Absorption", "distribution" in the Wyckoff sense need flow: OI, CVD, delta at a level. From price alone they are labels.
  F6 calls the weekly state "distribution" but that is a price rule, not real distribution. Testing them needs OI/CVD history.

## Not done
No fees, no out-of-sample split, 15m only, Binance only. 10-29 is outside the archive (ends 2026-09-26).
