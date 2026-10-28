# FABIO V3 SOURCING 2026-10-02

Session: MTS-2026-10-02-1930Z-CLI-BLD-fabio-v3-shadow. Spec: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md` section 7.1 (P01, P03, P04, P07, P12, P21, P31, P34).

Rule: decision is SOURCE only when the quote gives the numeric value; otherwise SHADOW. Quotes are verbatim from the raw transcript at the location (`[m:ss]` stamps dropped, line breaks joined; `0j:4` = whole transcript on line 4, so the quote was located inside that line by text search). Locations: 0j = raw_transcripts_canonical/0jM5Y31YJak_raw.txt, ja = jasv3L-d8ZE_raw.txt, 8C = 8CWKfoSJu3c_raw.txt.

| id | name | spec value | quote | location | decision |
|---|---|---|---|---|---|
| P01 | S1 balance; N | {60,120,240} | "We can see that the market is balanced at this time and if we plot a profile for the current situation we can just see balance" | 0j:4 | SHADOW |
| P03 | S2 pressure p; drift q | {0.05,0.10}; 0.25 | "So the market is clearly building pressure down." | 0j:4 | SHADOW |
| P04 | S3 L, z_hi, r_abs, r_ctl | 60, {2.0,2.5,3.0}, 0.25, 1.0 | "the result of the price for a pressure in by delta was almost zero." ; "can see the punch to the wall I marked for you and you can see the rewarded effort of the sellers." | 0j:4; 8C:42-44 | SHADOW |
| P07 | S4 window m | {5,15} (C), 15 | "You see again big trades in the direction of the trend because we studied auction market theory and we know that this is a sell model day and we continue to sell" | 0j:4 | SHADOW |
| P12 | S7 off | variant | "We can scale other two contract here on the way down." | ja:70-71 | SHADOW |
| P21 | mgmt dist, be_k | {1.0,2.0} | "the market exploded in my direction and I put my stop loss to break even." | 0j:4 | SHADOW |
| P31 | stop floor f | {0.3%,0.5%} | quote not located | spec source column '-' | SHADOW |
| P34 | US_CLOSED excluded; London/Asia windows | - | quote not located | spec source column '-' | SHADOW |

## Result

SOURCE: 0 of 8. SHADOW: 8 of 8. No quote gives a number for any grid or fixed value (60/120/240, 0.05/0.10, 0.25, 2.0/2.5/3.0, 5/15, 1.0/2.0, 0.3%/0.5%). Every quote supports the idea only, as FABIO_PROVENANCE_AUDIT_2026-10-01.md already recorded (P01/P03/P04/P07/P12/P21 CONCEPT-ONLY, P31/P34 NO-SOURCE). The live path therefore runs all 8 as shadow collection: every grid value is logged as a `collection_only` signal and no order is placed.

## Checks run

| id | transcript location | quote is a substring of the located lines | same quote in extract file |
|---|---|---|---|
| P01 | 0j:4 | yes | not in extract (raw transcript only) |
| P03 | 0j:4 | yes | not in extract (raw transcript only) |
| P04 | 0j:4 | yes | extract_0jM5Y31YJak.md |
| P04 | 8C:42-44 | yes | extract_8CWKfoSJu3c.md |
| P07 | 0j:4 | yes | not in extract (raw transcript only) |
| P12 | ja:70-71 | yes | not in extract (raw transcript only) |
| P21 | 0j:4 | yes | not in extract (raw transcript only) |

## P31 and P34: searched, not located

Spec source column is `-` for both. Case-insensitive search of the 8 Fabio raw transcripts (0j, ja, 8C, fZ, LQ, 0Ky, Faw, Staph) for asia, london, 0.3, 0.5 %, minimum stop, stop size/distance, stop floor, tight/wide stop, pips, ticks returned only lines that do not state a stop floor or a window time:

- `fZ:15` "So we came from a London session where" (names London; no window time).
- `0Ky:4` "You can understand you know that London session is not worth to trade for me. My profit factor is really low." (names London; no window time).
- `fZ:104` "tight stop loss because if we break down" (no number).
- `LQ:781` "0.5% per trade, okay?" (his per-trade risk, not a stop floor).
- `asia`: 0 hits in all 8 files.
