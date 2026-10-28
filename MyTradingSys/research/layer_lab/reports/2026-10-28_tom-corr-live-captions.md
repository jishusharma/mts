# Lab Report: Tom DAX Correlation Live Stream Captions & Extract Verification (2026-10-28)

**Task**: `tom-corr-live-captions`  
**Card Title**: `Fetch captions of Tom live 'DAX Short Using My Correlation Trick' via gemini_queue on JIS-NUC once the stream ends. DONE when: raw_transcripts_canonical/<id>_raw.txt exists, EXTRACT.md in MyTradingSys/research/tom_correlation_trick_2026-10-26/ gets a section 1b with new quotes and verify_extract_quotes.py exits 0, and any numeric threshold Tom states is listed vs our OURS values`  
**Worker / Reviewer**: Google Gemini (Antigravity, host DESKTOP-F7IU69N)  
**Deliverables**:
- `raw_transcripts_canonical/e83njGZFrPw_raw.txt` & `raw_transcripts_canonical/e83njGZFrPw_timed.txt`
- [`MyTradingSys/research/tom_correlation_trick_2026-10-26/EXTRACT.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-tom-corr-live-captions/MyTradingSys/research/tom_correlation_trick_2026-10-26/EXTRACT.md) (Section 1b added)
- [`MyTradingSys/research/layer_lab/reports/2026-10-28_tom-corr-live-captions.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-tom-corr-live-captions/MyTradingSys/research/layer_lab/reports/2026-10-28_tom-corr-live-captions.md)

---

## 1. Summary of Execution

1. **Stream Identification**:
   - Live stream title: *"LIVE TRADING: DAX Short Using My Correlation Trick!"*
   - English video ID: `e83njGZFrPw` (German version: `liEJMfE_PXg`).
   - The stream ended and was fully archived on YouTube.
2. **Captions Ingestion**:
   - YouTube `timedtext` API was fetched via `youtube_transcript_api` fallback in `fetch_captions_timed.py`.
   - Result: 283 timed text snippets, 1802 spoken English words cleanly extracted into `raw_transcripts_canonical/e83njGZFrPw_raw.txt` and `e83njGZFrPw_timed.txt`.
3. **Extraction & SOURCED Quotes**:
   - Added `## 1b. Live stream quotes (e83njGZFrPw)` to `EXTRACT.md` containing 6 verbatim SOURCED quotes with exact timestamps and `BEGIN`/`MIDDLE`/`END` position tags.
   - Verified that `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tom_correlation_trick_2026-10-26/EXTRACT.md` exits 0 (all 15 quotes across `EXTRACT.md` pass verbatim text and position matching).
4. **Numeric Thresholds Comparison**:
   - Stated explicitly: **no thresholds stated**. Across the entire live stream `e83njGZFrPw`, Tom provides zero numeric thresholds (no numeric lookback days, no percentage cutoff, no point/tick stop or target). All entry, stop, and target rules remain purely structural.
   - Compiled a comparative table comparing Tom's structural rules against OURS pre-registered parameters in Section 4.

---

## 2. Thresholds Comparison Table

| Parameter | Tom's stated threshold (`e83njGZFrPw`) | OURS pre-registered value (Section 4) | Match / Gap |
|---|---|---|---|
| Divergence lookback | no thresholds stated (visual intraday / multi-session comparison) | 2 days (primary; variants 1, 3, 5 d) | Parameter is entirely OURS |
| Divergence magnitude | no thresholds stated ("significantly more compared to the wonderful S&P future") | Top quintile (top 20% vs trailing 250 d) | Cutoff is entirely OURS |
| Basket definition | S&P future (ES) + DAX heavyweights (Siemens, SAP, Allianz, Airbus, Telekom) | Primary: median sign of ES, Nikkei, BTC; H2: ES, NQ, DXY | Basket membership differs; Tom uses ES + individual heavyweights |
| Entry trigger | no thresholds stated (structural: 2nd lower balance accepted + VPOC shift down + profile low rejection) | Convergence start: basket turns towards DAX direction and DAX fails to make new extreme | Both require confirmation; Tom uses profile/balance acceptance, OURS uses convergence turn |
| Stop loss | no thresholds stated (structural: above 2nd move where market accepted lower prices) | Trailing / structural | Consistent philosophy (structural reference), zero numeric points |
| Take profit | no thresholds stated (structural: test lower boundary of sideways phase / range traversal) | Full range / fee-net expectancy > 0 | Both target opposite boundary of range/balance |

---

## 3. Independent Verification Command

```powershell
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tom_correlation_trick_2026-10-26/EXTRACT.md
```
**Output**:
```text
OK       EXTRACT.md:9
OK       EXTRACT.md:14
OK       EXTRACT.md:19
OK       EXTRACT.md:24
OK       EXTRACT.md:29
OK       EXTRACT.md:34
OK       EXTRACT.md:39
OK       EXTRACT.md:44
OK       EXTRACT.md:47
OK       EXTRACT.md:58
OK       EXTRACT.md:64
OK       EXTRACT.md:70
OK       EXTRACT.md:76
OK       EXTRACT.md:82
OK       EXTRACT.md:88
PASS: 0 problem(s)
```

---

## 4. Findings Table

| Severity | File:Line | What is Wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| SOUND | `MyTradingSys/research/tom_correlation_trick_2026-10-26/EXTRACT.md:51-118` | Section 1b integrated with verbatim quotes and threshold comparison. | `verify_extract_quotes.py` passes with 0 defects; all criteria satisfied. | None. Deliverable complete. |

---

## 5. Verdict

**PASS**: Video `e83njGZFrPw` captions fetched and preserved; `EXTRACT.md` updated with Section 1b SOURCED quotes and threshold comparison table against Section 4 OURS values; `verify_extract_quotes.py` exits 0.
