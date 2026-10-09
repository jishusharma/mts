# B156 Tom alert card: SSOT_THESIS text is stale

Logged 2026-10-09 by the live analysis thread (read R3, shot b5f554a9f68a).

## Evidence
runtime_data/last_alert.json on JIS-NB at 16:30Z, alert #273, TIME 2026-10-09T14:26:11Z, PRICE 83106.5:
SSOT_THESIS line says the prior short thesis (target 76300) was invalidated by "price_current_above 77115, satisfied 30h+" and
"Price ~77600 never printed 76300". The live price in the same card is 83106.5, so the line describes a market ~5500 lower.

## Fix
Find the writer of SSOT_THESIS. Show when the thesis was written and at what price, or leave it out of the card once it is older than
the card's own state. Test: a thesis written at price X with a card at price Y far from X is marked stale or omitted.
Display only: no trade gate reads this text (check before changing).

2026-10-10 close (cc16a73): the writer is start-trading-day.ps1 (SSOT: read current thesis); it read session_state.json whose thesis dates 2026-09-14. thesis_line(state) now appends [written <utc>, <age> old], and an empty text gives no line. Display only: no trade gate reads it. Test: MyTradingSys/tests/test_b156_thesis_line_age.py.
