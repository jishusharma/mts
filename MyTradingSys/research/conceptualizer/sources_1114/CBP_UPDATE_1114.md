# CBP update 2026-11-14

Store: 22 rows (was 19 on the board; +5 new rows ingested, window prune left 17 before). Board rebuilt, republished at <artifact-url> Market-data step (`fetch_board_data.py`) exited 1, so market overlay is the last data. Lean over the newest call per analyst (6): 4 BEARISH / 1 NEUTRAL / 1 BULLISH. Over all 22 rows: 20 BEARISH / 1 BULLISH / 1 NEUTRAL.

## Newest call per analyst
| Analyst | Video | Date | Bias | Symbols | Key level | Verified quote (caption, <15 words) |
|---|---|---|---|---|---|---|
| Benjamin | 7XTLBzDzOHA | 2026-11-13 | BEARISH | BTC | 200-week MA under test (2015, 2020 fell ~30% below it) | "Bitcoin is probably entering this final phase of capitulation of a four-year cycle." |
| Jason | aNNrh4GJGuA | 2026-11-13 | NEUTRAL | BTC ETH SOL XRP INJ | 75k support lost; reclaim 73k (200-day MA) | "Basically the support level of 75k gave way." |
| Jala | hJVmuVCxyDU | 2026-11-13 | BEARISH | BTC | 68K upper lip of bottom pocket | "we have to be decidedly bearish still until this changes" |
| Krown | jI8dKkBSPuQ | 2026-11-12 | BEARISH | BTC | daily 200 SMA 73,080; ~65,000 on a break | "for this next month, I want to be more defensive." |
| Michael | KeMDM3_h-W0 | 2026-11-12 | BEARISH | BTC | 75k closes; 70-72k zone | "We've just been trending lower since the 21st of September." |
| Habib (Qriptal) | BwnXW_wwggY | 2026-11-10 | BULLISH | BTC | support 73k-72k, invalid 70k | "I am now flipping bullish. I am waiting for the support below." |

Quotes were string-matched against the cached caption files (`raw_transcripts_canonical/<id>_raw.txt`); the extract files for Jason, Jala and Krown pass `verify_extract_quotes.py` (PASS 0 problems).

## Newly ingested (5 rows)
Jason aNNrh4GJGuA (11-13), Jala hJVmuVCxyDU (11-13), Jala RaTGViedzBQ (11-12), Krown jI8dKkBSPuQ (11-12), Michael KeMDM3_h-W0 (11-12). Captions via `yt.py get --transcript`, route v6 (own IPv6; WARP route locked until 2026-11-16). Shipped 0a77eabb, CI green.

## Still missing / why
- Rekt, Bob, Michaal, CCU: no rows in the 5-day window. Channel listing (public transcript site) shows nothing newer than Rekt 11-03, Bob 09-14, Michaal 11-09 (4IwClJva4B4, altcoin video, not in store: check whether it was rejected), so no new upload to fetch. CCU not re-listed this pass.
- Habib: newest stored is 11-10; the listing shows no newer upload than BwnXW_wwggY (11-11 per the site date, same video).
- Michael KeMDM3_h-W0 Gemini extract card was still running on the NUC at write time (queue busy with other cards); the row itself is ingested, so the extract file is only the audit copy. Run `nuc_lab.py gemini-status`.
- 12 videos sit on the waiting list (`fetch_captions_timed.py --waiting`); they are older or non-analyst items, not new calls.
- Board market data (`fetch_board_data.py` exit 1): not investigated; the script is in `F:\CryptoScrapper\cbp_v2\tools`.
- Row extraction (bias, pointers) in `cbp_run.py` used the `claude -p` pass, not Gemini; Gemini cards produced the audit extracts.
