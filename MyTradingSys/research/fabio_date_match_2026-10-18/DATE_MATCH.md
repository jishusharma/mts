# Fabio NQ-202512 session (DyS79Eb92Ug / Jpd96fLqr5M): date by price-path match

Verdict: **AMBIGUOUS**. Report only; the ledger is untouched.

Data: Dukascopy USATECHIDXUSD BID 1m, 70 weekdays 2025-09-15..2025-12-19 (69 + 1 retried, 70 with bars, 0 empty, 0 fetch fail in the final run), entry minutes scanned 13:00-15:15 UTC. Offsets only, so the CFD-vs-Dec-futures basis cancels (here CFD about 24752 vs ledger 24914 = about -162 pt on the spoken day).
Scoring (date_match.py): entry level E, then c1 +86.7 pt within 20 min (SOURCED ledger F6 24914.33 -> 25001.00, csv:25-28), c2 stop -30.8 pt (24883.50) not hit before TP (SOURCED), c3 120-min high inside +181..+196 (SOURCED md:95, 25095-25110), c4 +155 pt within 35 min (OURS, F10 TP 25074.25). Windows 20/35/120 min and tolerance 50 pt are OURS. A first run with a 40-min TP window and no c4 tied 8 days at 1.0; I tightened once (c4, 20 min) and the tie remained, so I stopped (no further tuning on the same data).

## Top 5 (all score 1.0; table order = sort order, not a ranking)
| day | entry minute UTC | CFD price at entry | score |
|---|---|---|---|
| 2025-10-15 (spoken day) | 13:47 | 24752.03 | 1.00 |
| 2025-09-18 | 13:47 | 24372.37 | 1.00 |
| 2025-10-13 | 13:35 | 24553.51 | 1.00 |
| 2025-10-17 | 13:49 | 24600.68 | 1.00 |
| 2025-10-23 | 13:24 | 24847.56 | 1.00 |
(also 1.0: 2025-10-30, 2025-11-13, 2025-11-17: at least 8 days; full list in run.log.)

## Reading
- The price pattern alone does not single out a day: +87 pt then +160..190 pt in two hours is common on NQ. The spoken day 2025-10-15 does match and was checked first; its entry minute 13:47 UTC = 15:47 CEST (DST ran to 2025-10-26), consistent with the chart's ~15:45 clock. That is a consistency check, not a unique identification.
- Not tested: the late-session losers F11-F14 (range 25095-25110) as a path constraint, volume, and the 4-lot add-ons. A next card could add those with price-level paths (higher-resolution), or read a date from a video frame.
- Caveat: Dukascopy index CFD, not CME futures; session hours and prices differ by basis.
- Ledger entry_time_utc stays EMPTY; do not fill it from this table.
