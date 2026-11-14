# CBP Call Extraction Findings: Michael Pizzino (KeMDM3_h-W0)

- Task: gemini-cbp-michael-kemdm3_h-w0-1114
- Date: 2026-11-14 (UTC)
- Analyst: Michael Pizzino (@MichaelPizzino)
- Video ID: KeMDM3_h-W0
- Title: Money Is Rushing for the Exits… Here's Where It's Going
- Source File: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt
- Output File: MyTradingSys/research/cbp_gap_1114/KeMDM3_h-W0/EXTRACT.md

## Extracted Calls and Verifications

All 12 calls below were extracted directly from `raw_transcripts_canonical/KeMDM3_h-W0_raw.txt` and verified with `python scripts/dev/verify_extract_quotes.py`:

1. **Call 1 (US 30Y Bond Yield Resistance Midpoint)**
   - Level: 5.5% [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
   - Quote: > "And if we start to see signs of failure around this midpoint here at about 5.5% it may well lead to this chart here easing off again."
   - GPS: `KeMDM3_h-W0 | BEGIN`

2. **Call 2 (US 30Y Bond Yield Upside Continuation Trigger)**
   - Level: 5.5% [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
   - Quote: > "So for the government bond yields I'm looking at around 5.5% and price action above that level to see this thing continue up which would be putting more pressure on other assets across the board"
   - GPS: `KeMDM3_h-W0 | BEGIN`

3. **Call 3 (US Dollar Index Support Zone)**
   - Level: 101 - 101.5 [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
   - Quote: > "And we were looking at around 101 to 101.5 and we didn't get that trigger which means the preceding trend which is up is more likely going to continue and that's just exactly what we've seen."
   - GPS: `KeMDM3_h-W0 | BEGIN`

4. **Call 4 (US Dollar Higher Pivot / Trigger Level)**
   - Level: 14th of October old top / 101 [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
   - Quote: > "So what I'm looking out for now in the dollar is a break beneath that old top of the 14th of October, followed by some changes in trend. I was previously looking at that 101 level, but now I'm raising that pivot point and I'm raising that trigger to be the lead on the higher-term time frame trend changing."
   - GPS: `KeMDM3_h-W0 | BEGIN`

5. **Call 5 (Bitcoin Key Overhead Resistance / Trend Change Level)**
   - Level: 75k [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
   - Quote: > "And because we've not yet seen any of that strength prevail and a higher low form and a change in trend form above 75k, this preceding trend, which is down, is most likely just going to continue."
   - GPS: `KeMDM3_h-W0 | MIDDLE`

6. **Call 6 (Bitcoin Immediate Support Zone)**
   - Level: 70k - 72k [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
   - Quote: > "Now, we've fallen right into the zone I've been talking about as well, that 70 to 72k where ideally for the bull case, we see a pickup in activity, a pickup in buying, a little bit more volatility, and some stronger closing prices because if we don't see that happen here, there's a good chance price is going to continue down to the next pivot point, which is all the way down at $67,000."
   - GPS: `KeMDM3_h-W0 | MIDDLE`

7. **Call 7 (Bitcoin Downside Pivot Point / Continuation Target)**
   - Level: 67,000 [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
   - Quote: > "So, unless buyers step into the market right here, where we are now, 70 to 72 k, I'm looking out for a further continuation down to $67,000."
   - GPS: `KeMDM3_h-W0 | MIDDLE`

8. **Call 8 (Bitcoin Overhead Resistance Level to Invalidate Bearish View)**
   - Level: 75k [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
   - Quote: > "Now, what needs to happen to change that view is what I was talking about before, and that's some closes and higher lows above 75 k."
   - GPS: `KeMDM3_h-W0 | MIDDLE`

9. **Call 9 (Russell 2000 Support Level)**
   - Level: 6th of November bottom [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
   - Quote: > "The Russell got hit the hardest here. It is still holding above the 6th of November bottom."
   - GPS: `KeMDM3_h-W0 | MIDDLE`

10. **Call 10 (Gold Failed Recovery / Breakdown Resistance)**
    - Level: 4,000 [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
    - Quote: > "We had three consecutive up days and price was also able to reclaim $4,000 per ounce, which was pivotal."
    - GPS: `KeMDM3_h-W0 | END`

11. **Call 11 (Gold Major Downside Support Zone / Midpoint)**
    - Level: 3,600 [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
    - Quote: > "Now, if it does get worse, the major support zone I'm watching is around $3,600 per ounce being a major midpoint."
    - GPS: `KeMDM3_h-W0 | END`

12. **Call 12 (Gold Breakdown Zone / Reclaim Level)**
    - Level: 4,000 [SOURCED: raw_transcripts_canonical/KeMDM3_h-W0_raw.txt:9]
    - Quote: > "For gold, what needs to happen is a fast snapback above the breakdown zone. So the breakdown zone, you can clearly see comes in at just shy of $4,000 per ounce."
    - GPS: `KeMDM3_h-W0 | END`

## Verification Command & Result

Command:
```powershell
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/cbp_gap_1114/KeMDM3_h-W0/EXTRACT.md
```
Output:
- PASS: 0 problem(s) (12/12 quotes verified verbatim with correct thirds position tags)
