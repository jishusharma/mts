# Report: yt-gem-fabio-fetch-2 (Fabio Caption Fetch & Live-Trade Notes)

- **Date:** 2026-10-24
- **Task ID:** yt-gem-fabio-fetch-2
- **Runner:** Gemini Flash (Antigravity, JIS-NUC)
- **Scope In:** `extracts/gemini_out/fabio`; `raw_transcripts_canonical` (new files only)
- **Done When:** one note per id (5) in `extracts/gemini_out/fabio/`, transcripts fetched or NO CAPTIONS recorded

---

## 1. Summary of Caption Fetching

Five candidate Fabio-related videos were processed via `python scripts/dev/fetch_captions_timed.py --analyst Fabio <vid>`:
1. **Khgj5q1-ln8**: OK (manual captions, 1947 words, SOURCED: `raw_transcripts_canonical/Khgj5q1-ln8_timed.txt:7`)
2. **cUTsoU-15Tc**: OK (auto captions, 4377 words, SOURCED: `raw_transcripts_canonical/cUTsoU-15Tc_timed.txt:7`)
3. **06R-ebyOhDI**: OK (auto captions, 1132 words, SOURCED: `raw_transcripts_canonical/06R-ebyOhDI_timed.txt:7`)
4. **Pz8f0wWW12M**: OK (auto captions, 6606 words, SOURCED: `raw_transcripts_canonical/Pz8f0wWW12M_timed.txt:7`)
5. **DD73wDVvObI**: OK (auto captions, 6690 words, SOURCED: `raw_transcripts_canonical/DD73wDVvObI_timed.txt:7`)

Total fetched: 5 (OURS). No-caption: 0 (OURS). Stop on 429 hit: 0 (OURS).

---

## 2. Per-Video Findings & Duplicate Checks

Each video was checked against `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md` (dedupe by daily P/L at start):

| Video ID | Title | Duration (s) | Speaker as Stated | Live Trades | Duplicate-of | Note File |
|---|---|---|---|---|---|---|
| `Khgj5q1-ln8` | My Signature Orderflow Model | 692 (SOURCED: `Khgj5q1-ln8_timed.txt:6`) | Fabio Valentini / Fabervaale ENG | N (OURS) | None (OURS) | `extracts/gemini_out/fabio/Khgj5q1-ln8_note.md` |
| `cUTsoU-15Tc` | The Simplest Orderflow Trading Model | 1485 (SOURCED: `cUTsoU-15Tc_timed.txt:6`) | Fabio Valentini / Fabervaale ENG | N (OURS) | None (OURS) | `extracts/gemini_out/fabio/cUTsoU-15Tc_note.md` |
| `06R-ebyOhDI` | How To Find The BEST Entry Zones | 433 (SOURCED: `06R-ebyOhDI_timed.txt:6`) | Fabio Valentini / Fabervaale ENG | Y (SOURCED: `06R-ebyOhDI_timed.txt:21-23`) | None (OURS) | `extracts/gemini_out/fabio/06R-ebyOhDI_note.md` |
| `Pz8f0wWW12M` | The Only Orderflow Guide You'll Ever Need | 2464 (SOURCED: `Pz8f0wWW12M_timed.txt:6`) | Fabio Valentini / Fabervaale ENG | N (OURS) | None (OURS) | `extracts/gemini_out/fabio/Pz8f0wWW12M_note.md` |
| `DD73wDVvObI` | 4 Trading Champions Trade the Same Session (Live Trading) | 2134 (SOURCED: `DD73wDVvObI_timed.txt:6`) | World Class Edge / Fabio, Emir, Freddy, Andrea | Y (SOURCED: `DD73wDVvObI_timed.txt:928-930`) | None (OURS) | `extracts/gemini_out/fabio/DD73wDVvObI_note.md` |

### Key Details:
- **06R-ebyOhDI**: States two executions taken ("One in London session and one in New York session using this orderflow", SOURCED: `raw_transcripts_canonical/06R-ebyOhDI_timed.txt:22-23`), but no contract quantities, order fill tickets, or starting/ending P/L amounts are shown. No match against existing ledger rows F1-F14.
- **DD73wDVvObI**: Multi-trader live trading in UAE. Fabio trades NASDAQ and reports closing +1.75R positive for the day ("closed 1.75 R positive for the day", SOURCED: `raw_transcripts_canonical/DD73wDVvObI_timed.txt:929`). Starting Daily P/L does not match any entry in `FABIO_TRADE_LEDGER.md`.

---

## 3. Verification

Command executed:
```powershell
python scripts/dev/verify_extract_quotes.py extracts/gemini_out/fabio/Khgj5q1-ln8_note.md extracts/gemini_out/fabio/cUTsoU-15Tc_note.md extracts/gemini_out/fabio/06R-ebyOhDI_note.md extracts/gemini_out/fabio/Pz8f0wWW12M_note.md extracts/gemini_out/fabio/DD73wDVvObI_note.md
```

Result:
- Khgj5q1-ln8: 2 quotes verified OK
- cUTsoU-15Tc: 2 quotes verified OK
- 06R-ebyOhDI: 2 quotes verified OK
- Pz8f0wWW12M: 2 quotes verified OK
- DD73wDVvObI: 2 quotes verified OK
- Total: `PASS: 0 problem(s)` across 10 quotes.
