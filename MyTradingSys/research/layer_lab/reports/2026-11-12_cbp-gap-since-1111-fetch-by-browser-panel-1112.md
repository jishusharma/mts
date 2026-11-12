# CBP Gap Since 11-11: Newest Michaal, Jala, Qriptal Uploads (Gemini Lane)

- Card: `cbp-gap-since-1111-fetch-by-browser-panel-1112`
- Date: 2026-11-12 (UTC)
- Host: JIS-NUC
- Model: Gemini 3.8 Flash (Low)

## 1. Caption Lockout Status & Guard Check

- Command: `python scripts/dev/fetch_captions_timed.py --status`
- Status output: `BLOCKED until 2026-11-13T13:58:11+00:00 (host JIS-NUC, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS); budget used 0 of 40 in 24 h (OURS, ip 015a8ee6); last run budget used 1 of 5` (SOURCED: `fetch_captions_timed.py --status`)
- Caption lock unlock time: `2026-11-13T13:58:11+00:00` (OURS: recorded from guard status).
- Execution mode: Zero direct YouTube network requests performed. Captions and channel listing queried via `yt_transcript_sites.py` (Path 4 public transcript instance `yt.chocolatemoo53.com`) and Gemini web search grounding.

## 2. Channel Upload Findings Since 2026-11-11

Channel queries were executed via `yt_transcript_sites.list_channel` and verified against web search.

1. **Michaal (@michaelvdpoppe)**:
   - Handle: `@michaelvdpoppe`
   - Newest upload found: `4IwClJva4B4` ("I Bet Everything On These Altcoins After The Midterms!", published `2026-11-08`) (SOURCED: `scripts/dev/yt_transcript_sites.py:list_channel('@michaelvdpoppe', n=3)`).
   - Findings: **No new upload on channel** since 2026-11-11 (newest remains 2026-11-08).

2. **Jala (@jalacrypto)**:
   - Handle: `@jalacrypto`
   - New uploads found since 2026-11-11: 2 videos
     1. Video ID: `q_lc2teStyg` | Published: `2026-11-11` | Title: "My BTC Target Got Hit (73.1K) and I'm Feeling GOOD! (Good TA pays off)"
     2. Video ID: `RaTGViedzBQ` | Published: `2026-11-12` | Title: "CHEAP Bitcoin Coming! (Don't Miss the 'Bottom Pocket' Fire Sale!)"
   - Transcripts cached in `raw_transcripts_canonical/` (git-ignored).
   - Calls extracted and verified via `verify_extract_quotes.py`:
     - `MyTradingSys/research/cbp_gap_1112/q_lc2teStyg/EXTRACT.md`: 2 calls verified (GPS BEGIN & END)
     - `MyTradingSys/research/cbp_gap_1112/RaTGViedzBQ/EXTRACT.md`: 3 calls verified (GPS MIDDLE & END)
   - Both rows validated with `cbp_run.build_row` and landed in CBP store `runtime_data/cbp/cbp_store/rows.json`.

3. **Qriptal (@qriptal)**:
   - Handle: `@qriptal`
   - Newest upload found: `BwnXW_wwggY` ("Bitcoin: This is what you should be waiting for!", published `2026-11-10`) (SOURCED: `scripts/dev/yt_transcript_sites.py:list_channel('@qriptal', n=5)`).
   - Findings: **No new upload on channel** since 2026-11-11 (newest remains 2026-11-10).

## 3. One-Line Summary Per Analyst

- **Michaal**: No new upload on channel since 2026-11-11 (newest upload `4IwClJva4B4` on 2026-11-08).
- **Jala**: 2 new uploads (`q_lc2teStyg` 2026-11-11, `RaTGViedzBQ` 2026-11-12); 5 verified calls extracted across 2 EXTRACT.md files; 2 rows landed in `rows.json`.
- **Qriptal**: No new upload on channel since 2026-11-11 (newest upload `BwnXW_wwggY` on 2026-11-10).

## 4. Verification Commands & Exits

- `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/cbp_gap_1112/q_lc2teStyg/EXTRACT.md` -> Exit 0 (`PASS: 0 problem(s)`)
- `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/cbp_gap_1112/RaTGViedzBQ/EXTRACT.md` -> Exit 0 (`PASS: 0 problem(s)`)
- `python -c "import sys; sys.path.insert(0, 'MyTradingSys'); import cbp; print(len(cbp.load()['rows']))"` -> 2 rows (SOURCED: `runtime_data/cbp/cbp_store/rows.json`)
