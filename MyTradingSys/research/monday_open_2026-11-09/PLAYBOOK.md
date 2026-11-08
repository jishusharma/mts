# Monday 2026-11-09 open playbook (card monday-open-playbook-1109)

Written Sun 2026-11-08 ~19:00Z, Builder. Data: Binance spot BTCUSDT 1h (data-api.binance.vision) to 18:46Z, held `btc_daily.csv` to 11-06, CBP store rows to 11-08. Numbers: `python MyTradingSys/research/monday_open_2026-11-09/monday_clocks.py` (re-run at 00:05Z; Part 2 refreshes). Analyst calls are Context, never signals. No trade, no order, no forecast stated as fact. Labels: SOURCED = analyst row or data; OURS = our choice.

## 1. Bottom line

| | B straight drop | A small bounce, then drop | C bigger bounce |
|---|---|---|---|
| Ledger row | S009 (likely DOWN) | S010 (NONE) | S011 (NONE) |
| Line | 74,888 before 76,550 | 76,550 first, then 74,888 before 77,000 | 77,900 before 74,888 |
| Same-setup Mondays (n=70) | 23 (33%) | 10 (14%) | 20 (29%) |
| Analyst story | Benjamin, Jala, Krown | Benjamin "false start", Qriptal NY short | Michael needs 78k, vdP bull |
| Lean | most common, tied with C | rarest | tied with B |

- Evidence leans to **B (straight drop) over A**; B vs C is a coin flip (23 vs 20 of 70, noise about +-11 pp). The popular "small bounce then drop" story is the rarest class (10 of 70). Weak lean, OURS.
- **First trigger to watch: Asia 1h close under 75,571 (Sat low).** After it, the Fri low 74,888 went next in 17 of 30 similar Mondays, median 1 h later. So alert at 75,571, not at 74,888.
- Monday sweeps the Fri-Sun low in 34 of 70 similar Mondays (49%) vs 116 of 353 all Mondays (33%). Half of the time it does not (36 of 70).
- Class rule (OURS): from the Sun close, bounce = max high before any sweep; thresholds +0.8% (76,550), +1.4% (77,000), +2.6% (77,900). Window = Monday UTC day. 17 of 70 (24%: no sweep, under +2.6%) were chop: none of the three.

## 2. Krown's "10% more down" checked

| Claim as relayed | What the source says | Verdict |
|---|---|---|
| Krown: lows break, 10% more down | Krown 11-05 (e2-KjJdWbgM): month-breach statistic, median -10.5% under the previous month's low | stat, not a forecast for Monday |
| "on a correlation" | He says 68,100 "correlates to some extent" with a mid-60k target; 73,300 "correlates" with the 200-day | level confluence, not a measured correlation |
| 10-11% after 74.9k breaks | Benjamin 11-06 (szWg0zCAbF0): "additional 10-11% drop pretty quickly" | the 10-11% is Benjamin's |
| ~68k near the 200-week SMA | 68,100 vs 200w SMA 67,766 (ours, 11-08): 0.5% apart | coincidence of two sources |
| Newer Krown view | 11-07 DCA video neutral; 11-08 options video NO_VIEW | newest directional call is 11-05 |

Recount on held csv (Oct 2026 low 76,326 here vs Krown 76,195, venue gap):

| Item | Krown 11-05 | Held csv, since 2011 | Since 2018 |
|---|---|---|---|
| Months / breaches | 188 / 63 | 190 / 64 (34%) | 106 / 40 (38%) |
| p25 undershoot | 3.8% | 4.1% | 3.9% |
| Median | 10.5% | 12.0% | 8.4% |
| p75 | 22.25% | 20.8% | 20.1% |

- Statistic reproduced within about 1.5 pp. Reproduced as stated; it is measured from the previous month's low (76,326), where Nov already sits 1.88% under (74,888).
- Conditional (OURS): months already under the previous low by day 8, n=35. Further drop after the day-8 low: none in 18 of 35 (month low already in), 10% or more in 11 of 35; p75 17.3%. Two humps, not a median. From 74,888: ten percent more = 67,400.
- Krown's own timing: November low "usually comes around the 17th to the 25th" (5 Novembers). Monday is not that window; 68k is a weeks call.
- Two clocks disagree (Bible s.1 vs s.3): depth clock says 57,800 was the bottom; cycle clock says a final or higher low is due by 2026-11-16 (S008).

## 3. Views (CBP rows, latest BTC view per analyst)

| Analyst | Date | Bias | Down level | Up level |
|---|---|---|---|---|
| Krown | 11-05 | BEARISH short term | 73.3k, 68.1k, 65.7k | 81.9k reclaim |
| Benjamin | 11-06 | BEARISH | 74.9k break, 200w | none |
| Jala | 11-06 | BEARISH | 73.2k | 78k half-fib |
| Qriptal | 11-05 | BEARISH | 72k, buy there | NY-open sweep short |
| Michael P. | 11-06 | NEUTRAL | 75k hold, then 71-72.5k | 78k higher low |
| Jason | 11-04 | NEUTRAL | 72.5-73k | 50w MA 76.9k |
| CCU | 11-05 | NEUTRAL | none | none |
| vdP | 11-08 | BULLISH | none | 100k later |

- 4 bearish, 3 neutral, 1 bullish: headcount, Context only. Most downside targets (Krown 200d, Jala, Jason, Benjamin 200d) share one moving average at 73.2k (our 200d SMA 73,229): shared tool, not independent votes.
- Only Krown (stat) and Benjamin (200w) point near 68k. Rows with NO_VIEW or stale (before 11-05) are not counted as fresh.

## 4. Levels (Binance spot, UTC)

| Level | Price | Source |
|---|---|---|
| Fri high / 11-06 high | 76,416 | data |
| Sat high / Sun high | 76,250 / 76,200 | data |
| Sun close (live 18:46Z) | 75,935 | data |
| Sat low / Sun low | 75,571 / 75,656 | data |
| 11-05 low | 75,208 | data |
| Krown weekly-close line | 75,000 | SOURCED Krown 11-05 |
| 11-06 low (the low) | 74,888 | data |
| 200d SMA | 73,229 | cycle_ma_clock.py |
| Support cluster | 72,000-73,200 | Qriptal, Jala, Jason, Michael |
| 200w SMA | 67,766 (rising) | cycle_ma_clock.py |
| Up steps | 76,550, 77,000, 77,900 | OURS, Krown 55d EMA, Michael/Jala |

- Week high 81,196 (11-04), week low 74,888. Sun range so far 75,656-76,200: about 0.7%, a coil (Krown: calm means a bigger move later; he said it of options).

## 5. Monday clocks (UTC)

| When | Observable | Note |
|---|---|---|
| Sun 23:00 | CME reopen | gap not measurable here; schedule not checked |
| Sun 24:00 | weekly, 2-day, 3-day, daily close | Krown 75,000 weekly line; 75,935 now |
| Mon 00:00 | new week/day/4h bar, weekly open | read the 00:00 1h bar first |
| Mon 00-07 | Asia | 65 of 116 all-Monday sweeps (56%) |
| Mon 07-14:30 | EU (London 08:00) | 29 of 116 (25%) |
| Mon 14:30-21 | US cash open 14:30 (DST ended 11-01) | 22 of 116 (19%) |
| Tue 24:00 | 2-day close (epoch anchor) | 5-day: Thu 11-12 (anchor unstated by Krown) |

## 6. Early-catch triggers per session

| Session | B straight drop | A small bounce, drop | C bigger bounce |
|---|---|---|---|
| Sun close | weekly close < 75,000 | weekly close >= 75,000 | same |
| Asia 00-07 | 1h close < 75,571, then 74,888 (57%, median 1 h) | tag 76,416-76,550, 1h close back < 76,200 | 1h close > 76,250, hold |
| EU 07-14:30 | Asia low broken, no 1h close > 76,000 | EU high fails at 76,550-77,000 | 1h closes > 76,550 then 77,000 |
| US 14:30-21 | open spike down through 74,888 | 14:30 spike up, fade < 76,200 | 77,000 held, 77,900 test |
| Kill | 1h close > 76,250 | 74,888 swept first, or > 77,000 | 1h close < 75,571 |
| After | 73,229, 72-73k cluster | then B path | 78,800, 80k (Krown, not this week) |

- Early-catch limit: the Sat-Sun low break to the Fri-low sweep took a median 1 h (max 19 h) over 30 similar Mondays: the break is the warning, not a lead of hours. In 13 of 30 the Fri low did not follow.
- All Mondays since 2020 (n=175 with a lower Fri low): break of the Sat-Sun low 78, Fri low next 32 (41%), median 2 h. Asia first-breaks 44 of 78.
- Decoding the ledger at the score date (2026-11-10 00:00Z, `scenario_ledger.py score`): S009 DOWN = B; S009 UP and S010 DOWN = A; S010 UP and S011 DOWN = middle bounce that failed under 77,900; S011 UP = C. BOTH or NEITHER = not scored.

## 7. What would move the lean

- Toward B: weekly close < 75,000; Asia 1h close < 75,571 with no reclaim.
- Toward C: Asia or EU hold above 76,250 and 1h closes > 76,550.
- Weeks view (not Monday): Q4 low per Benjamin "could drag on until January"; cycle window ends 11-16.

## 8. Caveats

- Base rates: 1h bars, Mondays since 2020 (n=353; 70 in the setup, 42 in the lead-time sample). Within a bar the order of touches is unknown. Counts, not edges; difference B vs C is inside noise.
- Venue: Binance spot here; Krown quotes may use other venues (Oct low 76,195 vs 76,326).
- Not tested here: funding, OI, CVD, CME gap (no stable source this session).
- Quotes below are verified verbatim against the transcripts by `scripts/dev/verify_extract_quotes.py`.

## 9. Evidence (verbatim)

### Krown | 2026-11-05 | e2-KjJdWbgM | Bitcoin Broke the October Low: Is $68,100 Next by December?
evidence: "Bitcoin even set a new low below its October level."
evidence: "three out of four cases reached at least -3.8%. The median, however, was almost -10.5%. Every fourth case fell to -22.25% or worse."
evidence: "The next important area of interest according to this data is 68,100."
evidence: "I think it correlates to some extent."
evidence: "if Bitcoin drops another $10,000-$11,000 from here, that would be a significant move, and I think I personally would be interested in buying a lot"
evidence: "it usually happens around the 17th to the 25th"
evidence: "I expect that summer low to hold again."

### Benjamin | 2026-11-06 | szWg0zCAbF0 | Bitcoin: The Bears Strike Back
evidence: "if it drops below this low near 74.9k, it will most likely return straight to the lower limits of the range or potentially to the 200-week moving average."
evidence: "Bitcoin will get an additional 10-11% drop pretty quickly, like it did in the summer."
evidence: "Could this drag on until January? Yes. Could this happen next week? Certainly."

### Jala | 2026-11-06 | 4Z4wfQEYvHs | Is Democratic Socialism Good for Bitcoin? (Look for 73.2K Soon)
evidence: "So if you see Bitcoin hit $73,200, you saw it here on Hollow Pablo's channel."

### Qriptal | 2026-11-05 | oZtVNVPothk | Bitcoin: Why lower prices are still coming!
evidence: "the highest probability, at least from my point of view, is still that we will see a move towards our massive support around $72,000"

### Michael | 2026-11-06 | WHH4qSfCCyM | Panic Selling Is Exploding
evidence: "On the other hand, if the level of 75 thousand does not hold, this will, of course, be a signal for a further decline in prices."

### Michaal | 2026-11-08 | 4IwClJva4B4 | I Bet Everything On These Altcoins After The Midterms!
evidence: "I predict that the next rally will take Bitcoin to 100k"

### Krown | 2026-11-08 | M4mTHyPxMUM | Theta Gang Sells Every Friday. The Desk on the Other Side Doesn't.
evidence: "Longer periods of calm mean longer periods of explosion"
