# R3 Review: how Jala (@jalacrypto) chooses his fractals
Reviewer: Lab_Guy (no code, no YouTube fetched). Date 2026-10-31.
Sources read: `research/jala_layer_2026-10-31/method_jala.md` (22 timed quotes), `layer_lab/reports/2026-10-30_gemini-jala-method-extract.md`, `system/tasks/gemini-jala-method-extract.json`, `sim_desk/results/dir-jala_layer_2026-10-31.json` (source-extracted, no backtest), `gemini_burn_2026-10-31/QUOTE_AUDIT.md` (Jala row: UNCHECKABLE here, no caption files on this host), `cbp/ALT_BUY_PLAN_2026-10-31.md` (only the dominance quote), CBP status (Jala = thesis-only, off by default; 2 altered/spliced Jala quotes in the old extractions.md).

Caveat: the transcripts folder named in the report is NOT on disk in this worktree and `raw_transcripts_canonical/` holds none of the Jala ids. Quotes below are copied from method_jala.md, which passed verify_extract_quotes.py (22 quotes) on the host that had the captions; I could not re-verify them here.

## 1. What we know of his fractal selection rules
Verdict: very little. Only 3 of 22 quotes touch fractals, and none states selection rules. The report's claim "compares cycle patterns (2015, 2019, 2023)" has NO supporting quote in method_jala.md: the years are the extractor's wording, treat as UNVERIFIED.

| Question | Finding | Quote (as in method_jala.md) | Video id |
|---|---|---|---|
| Which past cycle/segment is overlaid | GAP | none | - |
| How aligned (anchor) | GAP. Only hint: the "three" is the next low off the lowest low in the bottom pocket (a low-anchored cycle phase, not a fractal rule) | "Now, the three is the next low that comes in off the lowest low in the bottom pocket." | p9KajODtBsU |
| Timeframe | GAP for the fractal. The trigger he pairs with it is a DAILY close vs the 400 SMA | "A close under the 400. Now, this is crucial." | -0UiEM32DX4 |
| What makes a fractal "fail" | Indirect: failure of a cup-and-handle (close under 400D) is what sends him to the fractal | "If we close beneath the 400, then that very well may indicate and confirm a failed cup and handle. And what does that mean? Well, if that happens, then now we look at the fractal." | -0UiEM32DX4 |
| What makes a fractal "confirm" | GAP. Only after-the-fact: fractal forecast a head-and-shoulders, price then tested the 400D | "Remember we talked about this. We did the fractal and I said expect some kind of like head and shoulder kind of setup" | xc4TyMS3HKc |
| Cup and handle | Fails on daily close under 400D | (quote above) | -0UiEM32DX4 |
| Head and shoulders | Called from the fractal beforehand; dated table row 2026-10-07 "Testing 400D as fractal forecasted" (table note, not a quote) | (quote above) | xc4TyMS3HKc |
| 400D MA | Support line; test then hold = support | "This brown line is the 400. Now, if we pass this 400 and we we passed the test, so to speak, and we and we we keep it as a support line" | xc4TyMS3HKc |
| Iron Dome | 200 and 400 simple day MAs crossing | "Of course, the iron dome is the 200 to 400 simple day moving averages crossing over." | 4wlnRxGsSdE |
| NUPL | STH NUPL turning yellow and crossing zero = the confirmation the "three" arrives on | "Notice that the three comes right in on the confirmation. See where the nuple turns yellow here and goes up through the zero line next to this EMA that goes up alongside it." | p9KajODtBsU |
| Outcome he called | 10-08 title "Bitcoin Loses the 400D (now we can expect 80-79K)"; 10-30 title "BTC under 79K -- We saw this two weeks ago" (video titles in dated table, not quotes) | - | lJ8rI4iiXG4, dmC1U_r8PFc |

Reading: the fractal is a SECONDARY tool he reaches for after a structural event (400D close break). Which cycle he overlays is not in our data.

## 2. Does he keep the 4-year cycle in mind?
Yes, one verbatim quote, thin otherwise:
- "We know every four years we get this three. Now, the three is the next low that comes in off the lowest low in the bottom pocket." (p9KajODtBsU). A 4-year recurring structure ("the three", a second low after the cycle low), confirmed by STH NUPL yellow/zero cross.
- Not found: any quote naming which prior cycle (2015/2019/2023) he overlays, or day-count alignment from halving or bottom. GAP.
- The report's phrase "cycle stage 3 confirmation" is the extractor's gloss, UNVERIFIED.

## 3. Coverage gap
- 30 latest videos tried; 12 captioned, 18 HTTP 429 with no quotes taken (the fractal videos may be among them). Of the 12 captioned, 9 ids carry quotes (-0UiEM32DX4, 4wlnRxGsSdE, 5x8DhXBwX9c, dmC1U_r8PFc, lJ8rI4iiXG4, mZSSzC6C_Qg, p9KajODtBsU, xIUHpTirh_g, xc4TyMS3HKc); J2h0pm74iw4, NOtT6auErWQ, EU77lbF-rMI appear in the dated table without quotes.
- The extract was a keyword scan of the latest 30 for general method; it was NOT filtered for "fractal" in title or captions. The video where "we did the fractal" (before 2026-10-07) was not read; it may be older than the latest-30 window.
- Caption files are not on this host (QUOTE_AUDIT: UNCHECKABLE). Needs the NUC or whichever machine holds them.
- Web: a standard search found nothing about Jala's fractal method (no posts, X threads or articles), so nothing to link. Generic context only, UNVERIFIED as to Jala: TradingView fractal overlays are anchored either to calendar year start or cycle bottom, e.g. https://vn.tradingview.com/chart/BTCUSD/ED9FBwdt-Bitcoin-Fractals-Comparison

## 4. Ready Gemini card spec (not filed)
Fields match existing gemini-*.json cards (id, title with [GEMINI], lane CODEX, kind run, worker agent, size, prio, goal, steps, commands, done_when, scope_in/out, note). Run as `gemini_queue.py run gemini-jala-fractal-method:low` (effort low). The Jala fetch hit 429 before: one try per video; if 429 persists mark UNVERIFIED. A local Whisper pass (asr_transcribe.py on JIS-NB) is a coordinator option, not for Gemini.

```json
{
  "id": "gemini-jala-fractal-method",
  "title": "[GEMINI] Jala (@jalacrypto): how he chooses and judges fractals (cycle overlaid, alignment anchor, timeframe, confirm/fail rule, outcome), timed quotes",
  "lane": "CODEX",
  "kind": "run",
  "worker": "agent",
  "size": "M",
  "prio": 2,
  "weight": "ROUTINE",
  "live_path": false,
  "goal": "Write MyTradingSys/research/jala_layer_2026-10-31/FRACTAL_METHOD_JALA.md. From the latest 50 videos of @jalacrypto, take every video with 'fractal' in the title OR in its captions. For each: video id, date, title, captioned or UNVERIFIED. Then a table, one row per fractal statement: which past cycle or segment he overlays (year, start and end), alignment anchor (cycle low, halving, ATH, 400D cross, date), timeframe (daily/weekly), what makes the fractal 'confirm', what makes it 'fail', link to 4-year cycle / 400D MA / NUPL / the 'three' / cup and handle / head and shoulders, and the outcome he called afterwards (date of call, level or direction, later result if stated); each row with timestamp and a verbatim caption quote, or NOT_IN_DATA. List videos that mention 'fractal' by keyword scan with line numbers. No verdict, no invention, no trading advice.",
  "steps": [
    "list latest 50 videos of @jalacrypto (ids, dates, titles)",
    "fetch captions with fetch_captions_timed.py, one try per video, 429 -> UNVERIFIED with no quotes, no retry loop",
    "keyword scan captions: fractal, overlay, 2015, 2019, 2023, four years, 4 year, halving, three, cup and handle, head and shoulder, 400, nupl; read the lines around each fractal hit",
    "write FRACTAL_METHOD_JALA.md: the video list, the statement table, a 'not stated' list",
    "run verify_extract_quotes.py until exit 0; fix or delete any failing quote"
  ],
  "commands": [
    "python scripts/dev/fetch_captions_timed.py --analyst Jala --channel @jalacrypto --latest 50 --out MyTradingSys/research/jala_layer_2026-10-31/transcripts",
    "python scripts/dev/verify_extract_quotes.py MyTradingSys/research/jala_layer_2026-10-31/FRACTAL_METHOD_JALA.md"
  ],
  "done_when": "FRACTAL_METHOD_JALA.md exists; first line counts videos read, captioned, UNVERIFIED, and videos with 'fractal'; every row has video id, timestamp and verbatim quote or NOT_IN_DATA; verify_extract_quotes.py exits 0.",
  "scope_in": ["MyTradingSys/research/jala_layer_2026-10-31/ (new files only: FRACTAL_METHOD_JALA.md, transcripts/)"],
  "scope_out": ["live tree; engine and layer code; any backtest; any trading verdict; .secrets and .env"],
  "tests": "verify_extract_quotes.py exit 0 is the gate; docs only",
  "refs": ["MyTradingSys/research/jala_layer_2026-10-31/method_jala.md", "MyTradingSys/research/fractals_2026-10-31/reviews/R3_JALA_FRACTALS.md"],
  "note": "Gemini rules: effort low (<card>:low); captions first (fetch_captions_timed.py), quote only from the caption file, one fetch try per video, 429 -> mark UNVERIFIED with no quotes; run verify_extract_quotes.py until exit 0; facts and quotes only, no verdict, no code change. Years or cycle names the speaker does not say are NOT_IN_DATA. Final report ends with a Noticed: line."
}
```

## 5. Draft rule set "Jala-style fractal" (to code later)
Almost everything is OURS until the card returns. Rows 1-6 are the most the quotes support.

| # | Parameter | Value | Label | Basis |
|---|---|---|---|---|
| 1 | Trigger to consult fractal | Daily close under 400-day SMA (BTC) | SOURCED | "If we close beneath the 400 ... now we look at the fractal" (-0UiEM32DX4) |
| 2 | Structure filter | 400D and 200D SMA ("Iron Dome") crossing/position | SOURCED | 4wlnRxGsSdE |
| 3 | Support test | Price tests 400D from above; hold = support | SOURCED | xc4TyMS3HKc |
| 4 | Cycle recurrence | "The three": next low after the cycle low, every 4 years | SOURCED (concept), OURS (days, which low) | p9KajODtBsU |
| 5 | Confirmation of the three | STH NUPL turns yellow and crosses zero (+ EMA) | SOURCED (event), OURS (EMA length, yellow threshold) | p9KajODtBsU |
| 6 | Pattern outputs | cup-and-handle fail; head-and-shoulders expected | SOURCED (names only) | -0UiEM32DX4, xc4TyMS3HKc |
| 7 | Reference cycles overlaid | prior 2-3 cycles | OURS (GAP) | not in data |
| 8 | Alignment anchor | cycle low (bottom) | OURS (GAP) | not in data |
| 9 | Overlay window / timeframe | daily, from anchor +/- N days | OURS (GAP) | not in data |
| 10 | Similarity metric / confirm threshold | e.g. correlation of normalised log returns >= X | OURS | not in data |
| 11 | Fail rule | path deviates more than Y% for Z days, or 400D reclaimed | OURS | not in data |
| 12 | Entry/stop/target | none | NOT_IN_DATA | method_jala.md section 6: structural invalidation only |
| 13 | Use | context filter, not a trade signal; fee-net OOS test; BTC has only 3-4 cycles so n is tiny | OURS | project rule |

Do not code until rows 7-11 are sourced from the card or explicitly set OURS and tested out-of-sample.

Noticed: the gemini report says 2015/2019/2023 overlays but method_jala.md has no quote for it; the transcripts dir named in the report is absent from the worktree (caption proof lives only on the host that fetched it); CBP already found 2 altered/spliced Jala quotes in old extractions.md.
Question: also run local Whisper on the 18 HTTP-429 videos? Default: no; Gemini card first, coordinator decides ASR only if fewer than 5 fractal videos get captions.
