# CBP extractions.md quote problems (2026-10-23)

Run: `python scripts/dev/verify_extract_quotes.py F:/CryptoScrapper/cbp_v2/extractions.md` -> 7 problems.
After the checker fix: 5 remain. No CBP commit (nothing in CBP edited; its tree holds other sessions' uncommitted files). CBP sha: none.

| # | line | Row | Class | Proof | Action |
|---|---|---|---|---|---|
| 1 | 12 | Benjamin preamble digest | format mismatch + not verbatim | no `### A / date / id /` header; quote absent from all 9 inbox/Benjamin_*.txt | report; CBP drops or converts the digest |
| 2 | 32 | Krown preamble digest | format mismatch + not verbatim | same; absent from all inbox/Krown_*.txt | report |
| 3 | 74 | Jala INcmHEQAMZ8 | altered quote | transcript: "58 000 which is most likely the bottom this was the bottom 4 years ago and it looks like it s the bottom this year too"; row: "It was ... four years ago ... as well" | not edited; re-extract |
| 4 | 84 | Jason bO88AeBojf8 | missing transcript | fetch_captions_timed.py --analyst Jason bO88AeBojf8 -> HTTP 429 | OPEN: retry, re-run checker |
| 5 | 350 | Michaal _QG1bt4iwQc | checker bug (stutter) | transcript "this is is really a breakout" | fixed |
| 6 | 471 | Jala xIUHpTirh_g | altered quote (spliced) | transcript "it s gonna it s going to be going up"; row stitched | not edited |
| 7 | 481 | Krown wvu0onib6WU | checker bug (filler) | transcript "we see uh bitcoin below 75 000" | fixed |

Counts: checker bug 2, format mismatch 2 (also not verbatim), altered quote 2, missing transcript 1 (open).
No row marked rejected: no CBP rejection rule found (extract_prompt.md:4 only says verbatim).
Fix: norm() in scripts/dev/verify_extract_quotes.py drops fillers (uh, um, uhm, er, erm) and immediate repeated words on both sides.
Tests: test_cbp_quote_survives_caption_fillers_and_stutters fails on old checker (verified), passes now; test_cbp_spliced_quote_still_fails guards restarts.
