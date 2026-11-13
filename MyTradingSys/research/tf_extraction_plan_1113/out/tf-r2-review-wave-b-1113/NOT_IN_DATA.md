# NOT_IN_DATA: tf-r2-review-wave-b-1113 (login B, JIS-NUC, 2026-11-13 13:50Z)

Wave B cannot be reviewed yet. Nothing here is a PASS or FIX verdict on the extractors' work.

| card | output on trunk | gate on JIS-NUC | blocker |
|---|---|---|---|
| tf-g1-prime-captions-1113 | ANSWERS.md (851e174d2, "gate exit 0" on the host that had the captions) + NOT_IN_DATA.md | `verify_extract_quotes.py` FAIL: 14 NO-TRANSCRIPT (O5s9zWI0n2s 7, VHhvg96W6lc 7); 1 quote OK (9IliXww64uM) | `raw_transcripts_canonical/O5s9zWI0n2s_raw.txt` and `VHhvg96W6lc_raw.txt` exist only on the host that fetched them; the folder is git-ignored |
| tf-g2-tom-feed-triage-1113 | NOT_IN_DATA.md only (card state active) | nothing to check | NUC caption lockout until 2026-11-13T13:58:11Z |
| tf-g3-fabio-shorts-partners-1113 | NOT_IN_DATA.md only | nothing to check | Fabio short transcripts not on JIS-NUC; caption lockout |

Unblock: the reviewer runs on the host whose `raw_transcripts_canonical/` holds O5s9zWI0n2s and VHhvg96W6lc (or after the NUC caption wave of PLAN_24H_2026-11-13 lands them here), and after tf-g2 and tf-g3 write ANSWERS.md. No caption fetch from this review: YouTube dispatch belongs to the gemini-yt session.
