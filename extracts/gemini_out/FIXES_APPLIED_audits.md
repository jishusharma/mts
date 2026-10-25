# FIXES APPLIED to Gemini audits (GPT review items 1-8)

Source: MyTradingSys/research/gpt_burn_2026-10-24/gx2-review-audits-fabio/report.md lines 31-58. Line numbers below are the original audit file lines.

## -dMWA_bbm3o_audit.md

- Item 1 (HIGH, missed rules :26 single print, :32 large orders, :35 absorption, :41 fast trend): APPLIED, bullets removed. Already explicit in extract_-dMWA_bbm3o_fresh.md :111/:114, :149, :146, :76. Raw line 7 confirms the same wording.
- Item 1 (:29 route planning): APPLIED, reworded to partial omission. Extract :143 keeps route planning and price ranges; only the four-item enumeration is missing.
- Item 1 (:38 lethargic counter-trading): KEPT, unchanged (real omitted relationship).
- Item 2 (:20-21 splice at line 143): APPLIED. The old quote was verbatim raw but not extract :143. Raw has 73 whitespace-split words between "I know exactly" and "where I have which route planning". The audit now quotes the two fragments separately, both verbatim in raw line 7, and states the 73-word gap (not 49).

## 1xBWnyr1qe4_audit.md

- Item 3 (:6-8 guest named as unnamed German/Swiss): APPLIED. Guest is addressed as Serge; raw line 7 "Thank you very much, Serge." added as quote. Nationality and "online forum" claims removed.
- Item 4 (:12-14 floor access as risk-system gap): REJECTED as a contradiction. Raw line 7 ("they can crash the company") is a floor-access precaution anecdote, not sizing or exposure limits. Bullet removed; extract :144 stands.
- Item 5 (:15-17 entry triggers): APPLIED, reworded. Exact numeric criteria are unspecified (extract :137); qualitative speed rule is present at extract :58 and :131. Quote is verbatim in raw line 7.
- Item 6 (:18-20 retail stop hunting): REJECTED. Extract :62 and raw line 7 ("not interested for the retailer stops", "I think it's a misconception") agree. Bullet removed.
- Item 7 (:29-31 "fabricated broker dialogue"): APPLIED, reworded to compressed non-verbatim quote. Raw line 7 has "Why you spoof?" and "300 contracts"; the event is not invented.
- Item 7 (:35-37 euro USD "spliced instrument"): REJECTED. Raw line 7 has "in the euro USD euro forex um ... yeah forex futures". Bullet removed.
- Item 8 (:40-42 Finviz day range ">= $0.75"): APPLIED. Raw line 7 says "day range ... 75 cents" with no comparison operator; audit records the direction as uncertain and quotes "over 300,000" as written.
- Item 8 (:43-45 Bund "defines a rule"): APPLIED, reworded as a historical example. Raw line 7: "in the past I trade maybe 100 contracts ... 10 ticks in the seconds"; "10 to 12 ticks seven ticks or more".
- Item 8 (:46-48 500-contract block flow): KEPT (genuine omitted specific).
- Item 8 (:49-51 fast-momentum breakout rule): REJECTED as a missed rule. Already at extract :58 and :131. Bullet removed.
- Item 8 (:52-54 forex anomaly): APPLIED, reworded to missing frequency/execution detail at extract :118. Added raw line 7 quote "maybe two or three times in the year".
