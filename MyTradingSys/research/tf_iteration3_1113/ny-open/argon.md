# Iteration 3: NY / Cash Open Rules Sweep (argon)

| topic | trader | exact quote | video id [mm:ss] | rule in his words | number: SOURCED value or NOT_SEEN | in our code? file:line or NONE |
|---|---|---|---|---|---|---|
| opening range size | Tom | "Open range, meaning the opening range. If it's very large, it likely won't hold. If it's very small, it likely will. That's it. That's all the information you need." | Fj4FDZQxw0I [00:00] | A very large opening range is unlikely to hold; a very small opening range is likely to hold. | NOT_SEEN | NONE |
| opening range break | Tom | "And suddenly we fall lower than the market opening range ever was and we get a fair price area." | 9VN9y2DVtGQ [00:00] | Falling below the market opening range signals a shift to a new fair price area. | NOT_SEEN | NONE |
| cash session open reference | Tom | "where you can read how the market traded during the cash session, the main trading hours, you can see it here. Here was the market opening from the previous day." | zAwEX_tRUfE [00:00] | Market profile is read over the cash session (main trading hours) with the previous day's market opening as a reference. | NOT_SEEN | NONE |
| gap fill myth | Tom | "Every gap will be closed. This is something what other people teach the students. Trust in me. Forget this. Not every gap will be closed." | 96iPFDpXEcU [00:00] | Not every gap will be closed; counter-trading every gap to close it is wrong. | NOT_SEEN | NONE |
| gap fill probability | Tom | "the probability that a gap like this is filled is significantly higher than a gap up here That's also relatively easy to determine if you've been paying attention. With volume profile and such, you know that the fair price is where here." | 96iPFDpXEcU [00:00] | Gap-fill probability depends on location relative to fair price on the volume profile, not a fixed rule. | NOT_SEEN | NONE |
| closing auction to open gap | Guest / Wall Street scalper | "Most of the time in the closing auction, if another extreme is reached there, you'll see a gap down at the open the next day and then things start to reverse. And that's when you can short." | DVZVE9rXGtU [00:00] | An extreme in the closing auction often leads to a gap down at the next day's open followed by a reversal short. | NOT_SEEN | NONE |

## TOP 5
1. **Opening range size (`Fj4FDZQxw0I`)**: Large opening ranges likely fail to hold; small opening ranges likely hold. No numeric threshold is given (`NOT_SEEN`).
2. **Cash session only for profiles (`BB3c8visnkI`, `uFxYcpiaOpw`, `zAwEX_tRUfE`)**: Daily volume/market profiles are built strictly over the cash session (main trading hours), not 24h.
3. **US cash open timing (`rrHj24GSR6M`)**: Big money enters US markets at 15:30 CET (09:30 ET); coded in `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:60`.
4. **Gaps do not always fill (`96iPFDpXEcU`)**: Counter-trading every gap is explicitly rejected; fill probability depends on volume-profile fair price location.
5. **Opening range break (`9VN9y2DVtGQ`)**: Breaking below the market opening range signals a shift to a new fair price area.

## SINGLE BIGGEST HOLE
Our codebase (`MyTradingSys/backtest/layers/fabio/v3/day_gates.py:60`, `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:345`) anchors the NY cash open at 09:30 ET, but has **no** opening-range calculation, **no** opening-range size filter (large vs. small), and **no** gap-fill vs. gap-and-go classification relative to volume-profile fair price.
