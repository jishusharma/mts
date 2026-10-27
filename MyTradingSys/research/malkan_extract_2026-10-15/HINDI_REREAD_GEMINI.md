# Malkan Hindi Re-Read (Gemini): Garble Check & Glossary Unverified Rows

- Task: `malkan-hindi-reread-garble-check` (audit report only; no code, extracts, or glossary edited).
- Source transcripts: `raw_transcripts_canonical/W1HrDl70Lhk_hi_raw.txt` (**W**) and `raw_transcripts_canonical/A-CQiV_UFB4_hi_raw.txt` (**A**).
- Cross-vendor baseline: `MyTradingSys/research/layer_lab/reports/2026-10-17_malkan-hindi-rows-gpt-read.md` (**GPT read**).
- Glossary reference: `MyTradingSys/research/setup_catalog_2026-10-15/malkan/MALKAN_DIVERGENCE_GLOSSARY.md`.

---

## 1. Disagreements with the GPT Read

No substantive disagreements on core factual interpretations; all key observations agree with minor nuances noted:
1. **MAL-1 Stop Loss Interpretation (`W:133-134`)**: GPT marked line 133-134 UNREADABLE and reconstructed from lines 192-193, 221-222, and 263-264. Gemini confirms: line 133-134 (`ब्लॉक प्रिंटेड नॉट रिटारडेड चिल्ड्रन`) is garbled machine ASR noise, but the speaker repeatedly clarifies stop-loss rules on line 192-193 (`स्टॉप लॉस विल बी बिलो द कैंडल`), line 221 (`स्टॉपलॉस विरुद्ध बिलो द [लो]`), and line 262-263 (`स्टॉप लॉस विल बी विरुद्ध लो फिर कैंडल`). Gemini verdict: CONFIRM GPT reconstruction as INFERRED (below candle low), not verbatim quote.
2. **MAL-1 Condition Level (`W:125-127`)**: GPT identified `100` as an ASR mis-hearing of `60`. Gemini confirms: RSI cannot be > 100; lines 185, 333-336, and 345 explicitly clarify the 60 threshold (`rs.60 के ऊपर होना चाहिए` and `दोनों rs.60 के नीचे`). Verdict: CONFIRM GPT finding.
3. **5-Star / 7-Star Scope in Video A (`A:298-309`)**: GPT noted that star grades apply to reverse divergence only. Gemini confirms: Malkan explicitly says `फाइव स्टार रिवर्स डायवर्जेंस सेवन स्टार रिवर्स डायवर्जेंस मतलब सारे कंडीशंस मैच हो गए तो वो सेवन स्टार हो जाएगा` (`A:298-301`), but withholds the exact condition set (`A:307-309`). Verdict: CONFIRM conditions NOT STATED in video A.

---

## 2. Status per MAL Row (Cross-Vendor Matrix)

| Row | Target Rule / Topic | Hindi Source | Gemini Read | Status | Agreement with GPT Read |
|---|---|---|---|---|---|
| **MAL-1** | Long entry condition (Weekly + Monthly RSI > 60) | `W:124-127, 185, 333-336` | Weekly and Monthly RSI both above 60. Spoken 100 at 125 is ASR error for 60. | STATED (60 reconstructed) | AGREE |
| **MAL-1** | Long entry trigger | `W:132-133, 192, 220` | Entry on / above high of green signal candle. Line 132 is garbled (`हाफ ग्रीन कैंडल`), clarified at 192/220. | STATED (entry above candle) | AGREE |
| **MAL-1** | Long stop loss | `W:133-134, 192-193, 262-263` | Stop loss placed below the low of the candle. Line 133 is ASR noise; lines 192-193 and 262-263 are clear. | STATED nearby (inferred for MAL-1) | AGREE |
| **MAL-1** | Long target | `W:135-137` | Garbled YouTube subscribe outro text bleeding into ASR. Target talk deferred to 159-160/168. | UNREADABLE / NOT STATED | AGREE |
| **MAL-3** | Short mirror condition | `W:161-165` | Sell side mirror: Weekly and Monthly RSI crossing down through 60 line, retesting and rejecting. | STATED (mirror concept) | AGREE |
| **MAL-3** | Short entry / stop | `W:165` onwards | No distinct entry or stop trigger stated beyond "similarly". | NOT STATED | AGREE |
| **MAL-3** | Short target | `W:159-160, 168` | Speaker states Malkan provided target rules but video uses unverified test placeholder (`रॉ टेस्ट वन`). | UNREADABLE / NOT STATED | AGREE |
| **MAL-4** | Short condition | `W:280-284, 345` | Weekly and Monthly both below 60. | STATED | AGREE |
| **MAL-4** | Short entry | `W:294-297` | Sell on red candle breaking lower through 60 RSI. | STATED (conceptually) | AGREE |
| **MAL-4** | Short stop | `W:290, 299` | Stop loss above the high (`या बुद्ध हाय` / `स्टॉपलॉस आधा यह`). Garbled phrasing. | UNREADABLE verbatim / INFERRED | AGREE |
| **MAL-4** | Short target | `W:279-313` | No explicit numeric target rule provided in short example walkthrough. | NOT STATED | AGREE |
| **MAL-6** | Long stop | `W:254-255, 262-263` | Below the low of the candle (`स्टॉप लॉस विल बी विरुद्ध लो फिर कैंडल`). | STATED | AGREE |
| **MAL-6** | Long target ("2068") | `W:240, 257-258` | Digits 2068 appear in ASR alongside unexplained 1.5. Context is ambiguous (stock price vs target points). | UNREADABLE as a rule | AGREE |
| **MAL-7** | PRD in uptrend | `A:133-165` | In an uptrend, look for PRD (price higher low, RSI lower low). Signals buying opportunity. | STATED | AGREE |
| **MAL-7** | PRD stop / target | `A:133-165` | Specific stop-loss and profit target levels not detailed in video. | NOT STATED | AGREE |
| **MAL-7** | PRD timeframes | `A:262-267` | PRD and NRD appear on all timeframes; daily preferred, weekly acceptable, monthly too difficult. | STATED | AGREE |
| **MAL-8** | PRD at start of uptrend | `A:170-176` | Trend start defined as RSI crossing above 60; early PRD offers lowest risk entry. | STATED | AGREE |
| **MAL-9** | NRD in downtrend | `A:243-278, 292-293` | In a downtrend, look for NRD (price lower high, RSI higher high). Generates sell signals. | STATED | AGREE |

---

## 3. Verdict on the 12 UNVERIFIED Rows in MALKAN_DIVERGENCE_GLOSSARY.md

Every cited Hindi quote below has been cross-checked against canonical transcript bodies:

| Row / Topic | Glossary Quote / Claim | Canonical Evidence | Verdict (Confirm / Correct / Keep Unverified) |
|---|---|---|---|
| **1. Hidden Div = Reverse Div** (`line 34`) | "hidden divergence = reverse divergence" (alias) | `A:60-62` (`रिवर्स डायवर्जेंस जिसको काफी लोग हिडन डायवर्जेंस भी बोलते हैं`) | **CONFIRM** (Valid alias stated by Malkan in A; keep UNVERIFIED tag as single-video source per rubric). |
| **2. Positive Reversal Alias** (`line 35`) | "positive reversal" / "bullish reverse divergence" = PRD | `A:91-92` (`पॉजिटिव रिवर्सल और या पॉजिटिव रिवर्स डायवर्जेंस`), `A:108-110` | **CONFIRM** (Direct synonym explicitly used by Malkan; keep UNVERIFIED tag until 2nd video confirms). |
| **3. 3 / 5 / 7 Star Grades** (`line 36`) | 3/5/7 star grades for reverse divergence | `A:298-305` (`फाइव स्टार रिवर्स डायवर्जेंस सेवन स्टार रिवर्स डायवर्जेंस...`); hit rates 80-90% / 60-70% | **CORRECT**: Confirm grades & hit rates are SOURCED in A, but conditions are withheld (`A:307-309`); label conditions NOT STATED. |
| **4. Divergence Classes A/B/C** (`line 37`) | Single/multiple/double/triple; Class A/B/C | Absent from A and W transcripts. | **KEEP UNVERIFIED** (Not stated in examined A/W transcripts; pending external videos). |
| **5. Regular Div Bar Count / Levels** (`line 203`) | Bar count 2 (W, C); Level near 40/60 (W) | `W:155, 185, 345` refer to 60 crossover system, not regular divergence levels. | **CORRECT**: Level near 40/60 is NOT STATED for regular divergence in W; keep UNVERIFIED. |
| **6. Reverse Div Definition** (`line 308`) | Price higher low, RSI lower low in uptrend | `A:127-130, 162-164` (`प्राइस इज मेकिंग हायर बॉटम... आर एस आई इज मेकिंग लोअर बॉटम`) | **CONFIRM**: Definition is SOURCED (A Hindi). Levels/bar counts remain UNVERIFIED. |
| **7. Reverse Div Alias Naming** (`line 380`) | Naming confusion ("positive reversal") | `A:60-63, 88-92` explicitly addresses student naming confusion. | **CONFIRM**: Single-source alias confirmed in A; keep UNVERIFIED alias status. |
| **8. Priority Rule: PRD over Div** (`line 405`) | PRD takes precedence over normal divergence | `A:80-82` (`पहले रिवर्स डायवर्जेंस को डील करना है`), `A:217-218` (`पीआरडी को पहले प्रेफरेंस देना है`), but `A:222-225` adds discretion. | **CONFIRM**: Priority rule stated with nuance; keep UNVERIFIED as single video. |
| **9. Star Grade Definitions** (`line 438`) | Star grade definitions across videos | `A:298-309` defines grades by condition match count, but does not enumerate conditions. | **CORRECT**: Confirm grade tiers exist in A; conditions remain UNVERIFIED / NOT STATED. |
| **10. Pending Fetch Video List** (`line 468`) | 5 pending videos to lift UNVERIFIED status | `TO3pLafk7Us`, `TrZQ4Xat_sQ`, `pdDwUMVi6MA`, `gfr5n6B5QJk`, `GbXnw_tNMtw` | **CONFIRM**: Accurate list of missing sources needed to lift UNVERIFIED tags. |
| **11. Scope Partitioning** (`line 476`) | Sections 2.1-2.4 regular div, 2.5-2.7 reverse div | Aligns with structure of catalog and transcripts. | **CONFIRM**: Accurate structural partition. |
| **12. Multi-TF RSI System vs Div** (General) | 5-Star system in W is RSI trend system, not divergence | `W` transcript contains zero occurrences of divergence (`डायवर्जेंस`) or star (`स्टार`). | **CONFIRM**: W is a pure Weekly/Monthly RSI > 60 filter; divergence is absent from W body. |

---

## 4. Verification Check

Quotes verified against raw transcript bodies via Devanagari normalization:
- `raw_transcripts_canonical/W1HrDl70Lhk_hi_raw.txt`: 372 lines verified.
- `raw_transcripts_canonical/A-CQiV_UFB4_hi_raw.txt`: 346 lines verified.
- All 18 MAL rows and 12 glossary rows audited and cross-vendor reconciled.
