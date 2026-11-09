# CBP alt update, 7 Nov 2026 (Lead C)

Source: the CBP store (`scripts/dev/analyst_levels.py --days 7`), 14 verified rows published 3 to 6 Nov. Context, not signals (cbp-is-the-context-source). Prices: Binance spot 2026-11-07, BTC 76,000, last completed weekly close 78,354.

**1. No alt rows.** All 14 rows since 3 Nov carry `symbols: [BTC]`. None of the seven channels (Krown, Cowen, Jason and Michael Pizzino, Jala, CCU, Qriptal) gave an alt level, an alt buy rule or a dominance call this week. The alt picture in SISTER_NOTE_2026-11-04 (Cowen dominance 60-66 %, van de Poppe DCA, Habib ETH 2,250-2,350) is therefore unchanged by CBP; nothing new to add from them.

**2. The BTC mood turned cautious, which is what moves the alt plan.** 7 of 14 rows bearish, 5 neutral, 2 bullish (Krown 3 Nov "above the October low 90 % green"; Michael 5 Nov short-term only).

| Level | Who | Reads as |
|---|---|---|
| 80,000 daily close | Krown 11-05 | "needs this to be in the best position to reverse" |
| 78,000 higher low | Michael 11-06 | "then some relief" |
| 75,000 weekly close | Krown 11-05, Michael 11-06 | the line in the sand; below it, further decline |
| 74,900 | Cowen 11-06 | below it "straight to the lower range or the 200-week" |
| 72,000 to 73,200 | Qriptal 11-05, Jala 11-06, Jason 11-04 (72.5k = 50 % of the rise) | the support they expect to hold; Qriptal: "the bottom of the bear market is here", long there |
| 65,000 to 66,000 | Krown 11-03 and 11-05 | if the October low goes; "I would be interested in buying a lot" |

**3. What it means for the alt phases (plan of 11-04).**
- Phase 1 (done or running at BTC 77k): BTC is 76k, inside the same zone. Nothing to change.
- Phase 2 (BTC 72,000 to 75,000): now 1 to 5 % away and named as the target by four analysts. It is the next event, not a remote one. Anchors only (ETH, SOL, LINK, HBAR), per the plan.
- Phase 3 (about 60,000): Krown's worst case is mid-60s, not 60k; Cowen points at the 200-week (67.8k, section 5 of the Bible). If that zone prints first, phase 3 waits for the 60k double bottom as written; the 65-68k area is where phase 2 may be topped up, not where phase 3 starts.
- ETH at 2,249 sits at the bottom edge of Habib's 2,250-2,350 buy zone (quoted in the 11-04 note). No new Habib row this week to move it.

**4. Our own clocks (Bible sections 1, 3, 5), same as 11-06.** Depth and MA clocks say July 57,800 was the bottom; the cycle clock's window runs to 16 Nov. Flag today: `CYCLE4 d397 dd-40 % | 5d>80,450 n | wk>=75,000 Y | WAIT`. Breaks the "bottom is in" read: a weekly close under 60,000 or a new low under 57,800.

Noticed: the CBP extractor never emits alt rows because the prompt is BTC-scoped (card `cbp-alt-coverage`, api run 11-04 out.jsonl built the ETH ladder code but posted no alt rows). Until that run is posted to DSA, "CBP on alts" stays empty by construction; alt reads come from ALT_PICKS_2026-11-03 (own measurement), not from CBP.
