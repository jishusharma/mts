# CBP Call Extraction Findings: Krown (jI8dKkBSPuQ)

- Task: gemini-cbp-krown-ji8dkkbspuq-1114
- Date: 2026-11-14 (UTC)
- Analyst: Krown (@ECKrown)
- Video ID: jI8dKkBSPuQ
- Title: Bitcoin Is Oversold: Bounce Now, or the $65,000 Line by December?
- Source File: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt
- Output File: MyTradingSys/research/cbp_gap_1114/jI8dKkBSPuQ/EXTRACT.md

## Extracted Calls and Verifications

All 11 calls below were extracted directly from `raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt` and verified with `python scripts/dev/verify_extract_quotes.py`:

1. **Call 1 (BTC Downside Target / 200 SMA Breakdown)**
   - Level: 65,000 [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
   - Quote: > "11% from that moving average to the downside would put Bitcoin I mean that would actually put Bitcoin down at around $65,000"
   - GPS: `jI8dKkBSPuQ | BEGIN`

2. **Call 2 (BTC Options Put Spread Position)**
   - Level: 72,500 long put / 65,000 short put [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
   - Quote: > "I am long the $72,500 put 20 times, and I am short the $65,000 put strike 20 times against that"
   - GPS: `jI8dKkBSPuQ | MIDDLE`

3. **Call 3 (BTC Put Spread Take Profit Zone)**
   - Level: 67,000 - 68,000 ($68,67,000 bucks) [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
   - Quote: > "basically, if I see Bitcoin somewhere down around like $68,67,000 bucks, I'm going to close this position and take the money and run"
   - GPS: `jI8dKkBSPuQ | MIDDLE`

4. **Call 4 (BTC November Low Timing Window)**
   - Level: Day 17 to Day 25 (November 17-25) [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
   - Quote: > "when we see negative Novembers, generally you see the day of the low of the month come between the 17th and the 25th of this month"
   - GPS: `jI8dKkBSPuQ | MIDDLE`

5. **Call 5 (BTC Downside Zone From October Low Breakdown)**
   - Level: 65,000 - 68,000 [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
   - Quote: > "anywhere between about 68,000 bucks on the upper end, 5,000 bucks on the lower end, it's kind of where I'm looking for on this move"
   - GPS: `jI8dKkBSPuQ | MIDDLE`

6. **Call 6 (BTC Monthly Green 55 EMA Support Level)**
   - Level: 65,500 [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
   - Quote: > "green 55 EMA on the monthly time frame here as well, which is more or less at about 65,500"
   - GPS: `jI8dKkBSPuQ | MIDDLE`

7. **Call 7 (Gold Bearish Below Key Resistance)**
   - Level: 4,100 [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
   - Quote: > "heavily ultra [&nbsp;__&nbsp;] bearish as long as you're below 4,100 at this point"
   - GPS: `jI8dKkBSPuQ | MIDDLE`

8. **Call 8 (Gold Macro Multi-Year Downside Targets)**
   - Level: mid-to-low 3,000s / 2,500 [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
   - Quote: > "sometime in the next six months, I think you see like, you know, mid to low 3,000s and then maybe fast forward like a year or two, you see like 2,500"
   - GPS: `jI8dKkBSPuQ | MIDDLE`

9. **Call 9 (SPY Overhead Resistance Level to Reclaim)**
   - Level: 7750 [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
   - Quote: > "the 7750 high from last Tuesday uh would be the relevant area of interest. So as long as you're below there, I can't love it necessarily"
   - GPS: `jI8dKkBSPuQ | END`

10. **Call 10 (Nasdaq Lower High Reclaim Level)**
    - Level: 30,200 [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
    - Quote: > "for me to get bullish on, I need to see it reclaim about, well, whatever last week's high or sorry, not last week's high, but uh whatever this lower high was here at about 30,200 or so"
    - GPS: `jI8dKkBSPuQ | END`

11. **Call 11 (Bitcoin Daily 200 SMA Level)**
    - Level: 73,080 [SOURCED: raw_transcripts_canonical/jI8dKkBSPuQ_raw.txt:9]
    - Quote: > "Bitcoin one closing below that 200 simple, which is $73,080"
    - GPS: `jI8dKkBSPuQ | END`

## Verification Command & Result

Command:
```powershell
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/cbp_gap_1114/jI8dKkBSPuQ/EXTRACT.md
```
Output:
- PASS: 0 problem(s) (11/11 quotes verified verbatim with correct thirds position tags)
