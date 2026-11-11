# Analyst video extraction status, 2026-11-12 (card tom-extract-opus-1112)

Counted this turn, not from memory: `build_ledger.py` rebuilt EXTRACTION_LEDGER.csv and GAPS.md (2026-11-11T21:05Z), then `python MyTradingSys/research/analyst_video_status_1112/count_status.py`. Unique video ids. Habib from `F:/CryptoScrapper/cbp_v2/extractions.md` + `verify_extract_quotes.py` (CBP store, outside the ledger). Wired rules from `research/wiring_audit_2026-10/WIRING_TOM_FABIO_HABIB.csv`.

## Counts

| analyst | ids known | transcript on disk | extract, quotes PASS | extract, quotes FAIL/NA | transcript, no extract | id, no transcript | rules wired / worth wiring, unwired |
|---|---|---|---|---|---|---|---|
| Tom | 37 | 35 | 35 | 2 | 0 | 2 | 108 / 57 |
| Fabio | 17 | 16 | 14 | 1 | 2 | 1 | 90 / 14 |
| Habib (Qriptal, CBP) | 5 | 1 | 1 | 4 (NO-TRANSCRIPT) | 0 | 4 | 5 / 5 |
| Malkan | 15 | 14 | 6 | 1 | 8 | 1 | - |
| Krown | 27 | 17 | 17 | 8 | 0 | 10 | - |
| Other / unknown | 158 | 72 | 12 | 38 | 58 | 86 | - |
| ALL (ledger) | 254 | 154 | 84 | 50 | 68 | 100 | - |

GAPS.md before -> after (2026-10-28 -> today): transcripts 145 -> 154; transcript with no extract 71 -> 68; priority id with no transcript 63 -> 56; extract with FAIL/NA quotes 32 -> 56; extracted but used by no layer 92 -> 129.
Video files on F:/MTS/data/tom_videos + fabio_videos: 24 mp4 + 4 webm (chart-reading frames; not transcripts).

How to read it (OURS):
- "Unknown" hides Tom: 42 of the 69 ON_DISK order-flow queue titles are Tom Vorwald EN channel videos ("World Trading Champion", "Wall Street scalper") with analyst = unknown. Tom's real backlog is in that row. Card ledger-attribution-and-thirds-fix-1112.
- "Used by no layer" is an id text match; rules are wired by rule id (Tom 108, Fabio 90 wired), so 129 overstates the waste.
- FAIL/NA rose 32 -> 56 mostly because extracts made on other machines have no transcript here (rumers 15, Krown +3, Habib 4): unverifiable on this host, not wrong. Two are real: wave-1 order-flow extracts `rFPCtOcfUMI`, `y67l86cSqb8` pass `verify_extract_quotes.py` but fail the ledger's position third; the two checkers cut transcripts differently (nested metadata block). Same card.
- Newest Tom video `M7ompiwv5co` is extracted (research/tom_swing_2026-11-09/).

## The two operator videos

| id | status | output |
|---|---|---|
| K31xH-6g9Vc (How to Backtest, Long & Short Ep. 12) | captions OK, 12 steps, 13 quotes PASS (verifier and ledger) | `research/backtest_howto_K31xH_1112/EXTRACT.md`, `GAP_TABLE.md` |
| j-JVi02_C88 (BTC below the 50W MA) | HTTP 429 at 2026-11-11T20:42Z; guard BLOCKED until 2026-11-12T02:42Z, not evaded | `research/btc_50w_ma_j-JVi02_1112/NOT_IN_DATA.md`; title claim checked on our data: `CHECK.md` |

K31xH-6g9Vc table (detail in GAP_TABLE.md):

| what it teaches | we already do | we do NOT do | should do | learn |
|---|---|---|---|---|
| 5 steps; fills on bar close; buy-and-hold compare; long/short split; log-vs-chart sanity check; fixed metric list; year x month table; back-adjust futures; parameter play; no IS/OOS in the tool | pre-reg, next-bar-open fill, placebo, fees 0.10 % RT, DEV/GAP/VALIDATION/HOLDOUT, Holm over repo m | trade-log sanity print vs klines; per-year and long/short lines in RESULT | card backtest-log-sanity-and-year-lines-1112 | his demo has no fees and picks parameters by best return (S10): the overfitting path our gates block |

j-JVi02_C88 table (title claim only; video text NOT_IN_DATA):

| claim | our data (482 closed weekly bars, 2017-08 .. 2026-11-02) | we do NOT do | should do | learn |
|---|---|---|---|---|
| BTC closed below the 50W MA | true: week of 2026-11-02 close 74,851 < MA 75,535 | no 50W MA reading in BIBLE.md | logged as scenario S025 (scenario_ledger, up 86k / down 63k, end 2027-01-26) | 7 earlier first breaks: +26w up 4/7; the 3 after a cycle top fell 18-56 %, the 4 near a halving rose 26-77 %; the break is a phase marker, not a signal |

## Backlog ranked (Tom/Fabio first; running work left alone)
Running, not touched: of-extract-ondisk-1112 (done on trunk, 10 extracts), btc-of-map-* chain, of-extract-fetch-1112, tom-fabio-newest-and-unextracted-videos-1112, analyst-call-backcatalogue-extract-1112 (Habib back catalogue).

| rank | what | ids | lane | card |
|---|---|---|---|---|
| 1 | 429 retry: 50W MA video + Tom's 2 extracts with no transcript | j-JVi02_C88, BB3c8visnkI, e83njGZFrPw | SONNET, after 02:42Z | extract-50w-ma-j-JVi02-retry-1112 |
| 2 | Order-flow ON_DISK ranks 11-20 (Tom channel) | 3JqMyzE8jIQ, Vd83oo_geMk, YopZ5ZDmMFw, usho6UVLqkE, 9VN9y2DVtGQ, AtR_c-B0jw8, ODdF0Bn_KSc, VOiy8mAALWA, uk4PZV59nYw, RwQBdF9TSvc | SONNET | of-extract-ondisk-wave2-1112 |
| 3 | Fabio transcripts with no extract | 9IliXww64uM, DyS79Eb92Ug | SONNET | fabio-two-transcripts-extract-1112 |
| 4 | Ledger attribution + thirds fix | 42 Tom ids, 2 wave-1 extracts | SONNET | ledger-attribution-and-thirds-fix-1112 |
| 5 | New BTC family from T3 + T7 (after the map's RESULT) | - | SONNET | of-family-level-and-auction-prereg-1112 |
| 6 | Backtest log sanity + per-year lines | - | SONNET | backtest-log-sanity-and-year-lines-1112 |
Later waves (not filed, DECISION OURS): ON_DISK ranks 21-69, Malkan 8 transcripts with no extract, Krown 10 ids with no transcript, 63 TO_FETCH ids (429 budget: about 5 per run).

## What transfers to BTC
One page: `TRANSFER_TO_BTC.md` (8 transferable ideas, 4 that do not, all SOURCED, verify exit 0). Three of the eight are already in the frozen BTC map (A1 large prints, A2 absorption, A3 funding extreme); flow-at-a-level and unfinished auction are not, and go to a new pre-registered family.

## Operator answer (plain words)
Almost every Tom and Fabio video we downloaded is extracted: Tom 35 of 35 transcripts, Fabio 14 of 16, and the newest Tom video too. The real gap is about 40 more Tom-channel order-flow videos that sat in an "unknown" bucket; ten were done yesterday, the next ten are queued. Your backtest video is extracted: we already do everything it teaches and more (fees, out-of-sample, placebo); two small checks from it are worth adding. The 50-week-average video was blocked by YouTube for 6 hours; on our own data BTC did close below that average last week, and in the past that meant a big fall when it came after a cycle top and a big rally when it came near a halving, so it is a phase marker, not a signal. What we learn from Tom and Fabio: big passive orders soaking up aggression, traders who are forced out, and auctions left unfinished at a high or low; on BTC we test these on BTC's own clocks with our own thresholds. Next: six cards filed, the 50W video retry first after 02:42 UTC.

DECISION (OURS): folder named analyst_video_status_1112 (not tom_*) because build_ledger.py assigns the channel from path words.
