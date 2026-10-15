"""One-off patch: apply the accepted items of the cold review (drafts/REVIEW.md) to drafts/MAL-BB-RSI-4060.md.
Every replacement must match exactly once or the script stops (so a changed draft is never half-patched)."""
import sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
def rep(old, new):
    global t
    n = t.count(old)
    if n != 1:
        sys.exit("NOT UNIQUE/FOUND (%d): %s" % (n, old[:80]))
    t = t.replace(old, new)

# a17, a18: scope
rep("each SOURCED row has its quote below the table, keyed Q1...Q8.", "each SOURCED row has its quote below the table, keyed Q1...Q7 (Q8, the bearish-engulf line, is in `MAL-BB-MID-ENGULF.md`). Review disposition: section 8.")
rep("(`raw_transcripts_canonical/{W1HrDl70Lhk,A-CQiV_UFB4,-CBvFi40sIQ,2HcJ3NeZmEQ,cQ-y1oULkBw,Wvq1TZh8aF0}_raw.txt`, both language tracks where present)", "(`raw_transcripts_canonical/{W1HrDl70Lhk,A-CQiV_UFB4,-CBvFi40sIQ,2HcJ3NeZmEQ,cQ-y1oULkBw,Wvq1TZh8aF0}_raw.txt`, English caption tracks only: the Hindi `_hi` tracks are Devanagari and were NOT searched with English terms, so NOT FOUND covers the English tracks; divergence, Malkan's core concept, was not among the searched terms: see section 8)")

# a03/a04: rows 3 and 4 (secondary Samco video; primary 2HcJ3 added)
rep("""| 3 | In a bearish market RSI tries to go back to 60 and is rejected there; that is the short moment (O3). Malkan's own words on disk: the bearish stock list wants the DAILY RSI "at around 60" (a host recap of his strategy); "cannot cross 60 in a bearish market" is only in a web blog quote | Q2: `extract_-CBvFi40sIQ.md:106` (host recap, "around" has no tolerance, extract:104); web: `WEB_RESEARCH.md:44-45, 86-87` (elearnmarkets blog, not a transcript) | SOURCED (Malkan) for "daily RSI around 60 in the bearish list"; the "cannot cross 60" sentence is SOURCED-WEB (counted under SOURCED, flagged) |""",
"""| 3 | In a bearish market RSI tries to go back to 60 and is rejected there; that is the short moment (O3). Malkan's own words (primary, uploader Malkansview): inside the zone where monthly and weekly RSI are below 40, "go to daily and look for 60 rise just to sell"; the trigger (touch, close above 60, turn down) is not stated (`extract_2HcJ3NeZmEQ.md:58`). A host recap (Samco, SECONDARY) says the daily RSI must be "at around 60"; the scan's "daily RSI above 60" filter was disabled there. "Cannot cross 60 in a bearish market" is only in a web blog quote | Q7: `extract_2HcJ3NeZmEQ.md:56` (PRIMARY); Q2: `extract_-CBvFi40sIQ.md:106` (SECONDARY host, "around" has no tolerance, extract:104); web: `WEB_RESEARCH.md:44-45, 85` (elearnmarkets blog, not a transcript) | SOURCED (Malkan) for "look for 60 to sell" (Q7); Q2 is the host's (SECONDARY); the "cannot cross 60" sentence is SOURCED-WEB (not counted as SOURCED) |""")
rep("""| 4 | The short is taken only inside an existing downtrend; "a downtrend already in the short term" (O4). Malkan's version: monthly and weekly RSI both below 40, then the daily RSI at about 60 | Q3: `extract_-CBvFi40sIQ.md:96`; stock charts, daily/weekly/monthly, not 1m | SOURCED (Malkan) for the multi-timeframe filter on stocks |""",
"""| 4 | The short is taken only inside an existing downtrend; "a downtrend already in the short term" (O4). Malkan's version: monthly RSI below 40 and weekly RSI below 40 (the "five-star zone"), then the daily at 60 | Q7 area: `extract_2HcJ3NeZmEQ.md:39, 48` (PRIMARY); Q3: `extract_-CBvFi40sIQ.md:96` (SECONDARY host, same filter); stock charts, daily/weekly/monthly, not 1m | SOURCED (Malkan) for the multi-timeframe filter on stocks (primary: 2HcJ3) |""")

# a07
rep("NOT FOUND in Malkan. He names Bollinger Bands as one of his three pillars (Q5) and has a \"Bollinger Bands Father-Son\" video, but no BB rule is spoken in the 6 transcripts.", "NOT FOUND in Malkan. The Bollinger reading of the three-pillars line (Q5) is INFERRED from machine-translation garbles (`extract_A-CQiV_UFB4.md:26`), so it is not a naming; 2HcJ3 says other setups using Bollinger Bands are deferred to a webinar and not explained (`extract_2HcJ3NeZmEQ.md:242`); he has a \"Bollinger Bands Father-Son\" video (no caption); no BB rule is spoken in the 6 transcripts.")
# a09
rep("Closest Malkan: strong trends keep the RSI pinned (Q6 `extract_W1HrDl70Lhk.md:44`, \"overbought in a strong uptrend, nothing happens\", machine translation, uptrend wording only).", "Closest wording: Q6 `extract_W1HrDl70Lhk.md:44`, \"overbought in a strong uptrend, nothing happens\" (machine translation, uptrend wording only, and W1Hr is SECONDARY: uploader Trader Insights, `extract_W1HrDl70Lhk.md:7`); it does not say the RSI stays pinned.")
# a11
rep("| OURS (thresholds, see Row C-/A-/B- variants below); the idea itself OPERATOR |", "| OPERATOR (the cushion idea is his O6); every number is OURS (variants in section 3) |")
# a13
rep("| Q5: `extract_A-CQiV_UFB4.md:22` (price action, momentum RSI, volatility Bollinger Bands = three pillars); the combination rule itself is not stated |", "| `extract_2HcJ3NeZmEQ.md:242` (primary: Bollinger Bands setups exist, deferred to a webinar, not explained); Q5 `extract_A-CQiV_UFB4.md:22` is a machine-translation line whose BB content is INFERRED (`:26`); the combination rule itself is not stated |")
rep("| SOURCED (Malkan) for \"he teaches RSI and Bollinger Bands side by side\" only |", "| SOURCED (Malkan) for \"he has Bollinger Bands setups next to the RSI ones\" only (not explained) |")

# counts
rep("Counts (script `../evidence/count_rule_table.py` parses this table; 15 rows): SOURCED (Malkan) 5 (rows 1, 2, 3, 4, 13; row 3 holds one SOURCED-WEB sentence, row 5's principle quote is not counted as a SOURCED row), OPERATOR 8 (rows 5, 6, 7, 8, 9, 10, 12, 15), OURS 2 (rows 11, 14); rows whose Malkan-evidence cell says NOT FOUND: 10 (rows 5 as to the intraday mapping, 6, 7, 8, 9, 10, 11, 12, 14, 15).",
    "Counts after the cold review (script `../evidence/count_rule_table.py` parses this table; 15 rows): SOURCED (Malkan) 5 (rows 1, 2, 3, 4, 13; rows 1, 2, 3, 4 rest on primary Malkansview videos, Wvq1 and 2HcJ3; row 13 is only \"BB setups exist\"; row 3's SOURCED-WEB sentence is NOT counted as SOURCED; Q2/Q3/Q6 from secondary uploaders are marked SECONDARY and not used as the SOURCED basis), OPERATOR 9 (rows 5, 6, 7, 8, 9, 10, 11, 12, 15), OURS 1 (row 14); rows whose Malkan-evidence cell says NOT FOUND: 10 (rows 5 as to the intraday mapping, 6, 7, 8, 9, 10, 11, 12, 14, 15).")
rep("Q1-Q6 quotes:", "Q1-Q7 quotes:")
rep("""> "It happens that if you are ever overbought in a strong uptrend, nothing happens."
**Source GPS: W1HrDl70Lhk | BEGIN**
""", """> "It happens that if you are ever overbought in a strong uptrend, nothing happens."
**Source GPS: W1HrDl70Lhk | BEGIN**

> "and from there we can go to daily and look for 60 rise just to sell that means that's one that's two and that's three"
**Source GPS: 2HcJ3NeZmEQ | MIDDLE**
""")

# section 1 fixes: net delta panel (b15), CVD
rep("Legend check against the images (the shots were taken mid-bar, so the forming bar's close from the shot is substituted):", "Legend check against the images (the shots were taken mid-bar, so the forming bar's close from the shot is substituted). Net delta caution (cold review b15): our per-bar delta (2 x taker-buy - volume) matches the increments of the CoinGlass CVD panel (13:23 about +1, 13:28 about -512) but NOT the chart's own \"Net Delta\" panel (shot 1 legend -431.9 at the 13:23 forming bar against our +9.5; shot 2 legend -378.968 at 13:28 against our -516.2 final, and that bar opens at -105 on the chart, so the partial-bar explanation does not hold). Those two are different quantities; every delta below is OUR taker delta = the CVD increment.")
rep("final-bar net delta -516.2 (shot is 56 s into the bar) |", "our final-bar delta -516.2 vs the chart's Net Delta panel -378.968 (different quantities, see above) |")

# c05, row side line
rep("Side for all three rows: SHORT (the operator showed the short side only; the mirror long is NOT STATED here).", "Side for all three rows: SHORT is the taught side; the operator's \"most probably bought up\" for outside-band closes (O10) is a long-side reading, kept in row C. The mirror long is NOT STATED by the operator; Malkan states a long version of his RSI setup (monthly about 60, weekly about 60, daily at 40: `extract_2HcJ3NeZmEQ.md:22`), which is a stock filter, not an intraday rule.")
# c02/c03
rep("a push up where price closes between the BB centre line and the upper band (%B between 0.5 and 1: 0.74 at 12:39); RSI crosses up from below 50 toward 60 (\"tried to go above the 60 line crossing from down under\") and turns down without a clean close above 60 (57.3 at the close; about 58-60 on the chart, a pixel read).", "a push up where price closes between the BB centre line and the upper band (operator: price between them; %B 0.74 at 12:39 is our measurement, the %B range is OURS); RSI goes up toward 60 (\"tried to go above the 60 line crossing from down under\") and is rejected there (57.3 at the close; about 58-60 on the chart, a pixel read). \"From below 50\" and any close condition at 60 are OURS (not the operator's words).")
rep("4. **Context he requires.** A downtrend already in the short term (O4). Malkan: monthly and weekly RSI below 40 first (Q3, stocks). \"This is not a hard rule\" (operator).", "4. **Context he requires.** A downtrend already in the short term (O4) and nothing else. For comparison only, not required by the operator: Malkan's stock filter is monthly and weekly RSI below 40 first (Q7, 2HcJ3 primary). \"This is not a hard rule\" (operator).")
# b07, c10
rep("RSI between 34.0 and 44.0 (the 40 line circled on the chart)", "RSI between 34.0 and 44.0 (the circles on the RSI panel sit at about 12:55, 13:00, 13:02 and 13:07 on both shots, i.e. not in this window)")
rep("(%B -0.06 to -0.10)", "(%B -0.04 to -0.10: -0.06, -0.04, -0.07, -0.10)")
# c07: row B instances
rep("Repeat at vertical 13:15 (wick 10 pts over the mid 80525.7, close 80473.2, RSI 40.81 above SMA 37.22 and then 38.0).", "Not taught but ours (cold review c07): the operator describes only the 12:39 and 12:51 verticals; at 13:15 our data shows a similar look (wick 10 pts over the mid 80525.7, close 80473.2, RSI 40.81 above SMA 37.22, then 38.0), added by us as a second look, NOT as taught evidence.")
rep("6. **Evidence.** 2 instances (12:51, 13:15), the same hour, one eye; one is the other's follow-up (not independent).", "6. **Evidence.** 1 taught instance (12:51, same hour as row A's 12:39, one eye); 13:15 is our own extra look, not taught, not independent.")
# d02
rep("FAB-1 (price follows the volume out of the lower-band balance), TOM-6 (speed picks up at the break) | CONFIRMED |", "TOM-6 (speed picks up at the break); FAB-1's precondition (a flat balance with CVD running one way) is NOT met by the falling 12:54-13:25 walk, so FAB-1 fits only the CVD-fall-with-break part | CONFIRMED (delta/OI), catalogue fit partial |")

rep("1. Rule table labels: SOURCED-WEB lines are counted under SOURCED but flagged; the count lists both.", "1. Rule table labels: SOURCED-WEB sentences are NOT counted under SOURCED (changed after the cold review); the count line names the row that holds one.")
t += """
## 8. Review disposition (cold review `REVIEW.md`: AGREE 40, DISAGREE 17, UNVERIFIABLE 6 of 63 claims)

Accepted and fixed in this file (all 17 DISAGREE items are fixed): a03 and a04 (rows 3 and 4 now rest on the primary 2HcJ3 video, Q7; Samco Q2/Q3 are marked SECONDARY, the \"daily RSI above 60 filter disabled\" remark added, web citation line 85), a07 (BB-pillar claim removed: INFERRED), a09 (Q6 gloss and SECONDARY flag), a11 (cushion idea is OPERATOR, numbers OURS: row 11 moved from OURS to OPERATOR), a16 (counts redone: SOURCED 5, OPERATOR 9, OURS 1; the SOURCED-WEB sentence is not counted), a17 (Q1-Q7), a18 (English tracks only), b07 (circle times), b15 (our delta equals the CVD increments, not the chart's Net Delta panel), c02/c03 (invented thresholds relabelled OURS, close condition removed), c04 (Malkan stock filter is not a requirement of the operator), c05 (side line), c07 (13:15 is our extra look, not taught: row B evidence is 1 taught instance), c10 (%B range -0.04 to -0.10), d02 (FAB-1 precondition).
Accepted as new findings, not yet worked: (1) divergence is Malkan's core RSI concept (Wvq1: \"the most powerful divergence come near 60 bearish ... near 40 bullish\", `extract_Wvq1TZh8aF0.md:150`) and the operator's \"RSI rejected at 60\" is not that rule: rows A-C must not be read as Malkan's divergence setup; (2) \"NOT STATED by Malkan\" for stop and target holds for the 2HcJ3 sell setup only (no stop or target words there, `extract_2HcJ3NeZmEQ.md:236-237`); Wvq1 gives stop and target rules for divergence trades.
UNVERIFIABLE items stay open: closes at 13:29-13:31 are outside the charts (our klines show them), our CVD/OI absolute levels cannot be read from the pictures, V1's delta ranking is our series.
Reviewer counts (63 claims): AGREE 40, DISAGREE 17, UNVERIFIABLE 6. Reviewer: a Haiku-class subagent spawned by this session (one subagent, not a session).
"""
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("patched OK")
