# Quote Audit: Extract Markdown Files in MyTradingSys/research

**Audit Execution Timestamp**: 2026-10-31T01:00:10Z
**Gate Tool**: `scripts/dev/verify_extract_quotes.py`
**Canonical Transcripts Directory**: `raw_transcripts_canonical/` (148 transcripts present)

## 1. Summary of Scope & Methodology
- Every committed extract markdown file under `MyTradingSys/research` matching the card command `git ls-files MyTradingSys/research | grep -i -E "extract|_levels|rules"` quoting video captions via `Source GPS` was audited.
- For each extract, caption availability was verified in `raw_transcripts_canonical/<id>_raw.txt` or adjacent `inbox/`.
- If no caption file exists on host: classified as **UNCHECKABLE** (exit code 1).
- If caption file(s) exist on host: `verify_extract_quotes.py` was executed read-only and recorded exit code (0 = PASS, 1 = FAIL) and failing quote count.
- For completeness and strict zero-assumption diligence, Section 2 covers the 43 command-matched extract/rules/levels files, and Section 3 covers the remaining 30 research documents quoting video captions.

## 2. Command-Matched Extracts Table (`extract|_levels|rules`)

| Extract Path | Exit Code | Failing Quote Count / Status | Total Quotes | Video IDs |
|---|:---:|:---:|:---:|---|
| `MyTradingSys/research/_archive/loose_2026-10/T064_TF_CONFIRMATION_EXTRACT.md` | `1` | **2** | 35 | 0KyIEdvVKMQ, 0jM5Y31YJak, 7BQPMJ39WpI, 8CWKfoSJu3c, 96iPFDpXEcU, FawPrRUGNpk, HySZZSjMxF8, WQ_OAdz-PJ8, fZlNGWvd2Ko, jasv3L-d8ZE, pgdmKLJ0hhA, zAwEX_tRUfE |
| `MyTradingSys/research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md` | `0` | **0** | 1 | 4MoNjEQ2Dd8 |
| `MyTradingSys/research/fast_track_2026-09-27/EXTRACTION_METHOD_V2_FABIO.md` | `0` | **0** | 1 | fZlNGWvd2Ko |
| `MyTradingSys/research/krown_audit_2026-10-22/GEMINI_RULES_QUOTE_AUDIT.md` | `1` | **UNCHECKABLE** | 18 | -9rAJNUpMsk, EQy4HouRMMk, SOaAP9vBgM4, UHY740h3e-Y |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md` | `0` | **0** | 70 | -NXzJs5JRks |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_14bxwxC8gBQ.md` | `0` | **0** | 59 | 14bxwxC8gBQ |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_2-nG9bsMoPQ.md` | `1` | **1** | 74 | 2-nG9bsMoPQ |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_2ei4fj-Ba24.md` | `0` | **0** | 100 | 2ei4fj-Ba24 |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_6aA-P4Gvhrc.md` | `1` | **1** | 66 | 6aA-P4Gvhrc |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_7IxfsuD2wCM.md` | `0` | **0** | 100 | 7IxfsuD2wCM |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_8MvxK_nxO-0.md` | `0` | **0** | 56 | 8MvxK_nxO-0 |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_Aysdt7PBETQ.md` | `0` | **0** | 39 | Aysdt7PBETQ |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_HhV4HI9p5Uw.md` | `0` | **0** | 24 | HhV4HI9p5Uw |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_INOCBmqQupc.md` | `0` | **0** | 68 | INOCBmqQupc |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_LB3DRYxnA0A.md` | `1` | **UNCHECKABLE** | 10 | LB3DRYxnA0A |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_OggsnATGbOg.md` | `1` | **UNCHECKABLE** | 3 | OggsnATGbOg |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md` | `0` | **0** | 18 | P3rDSh187TE |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_UqAvU1loT_k.md` | `1` | **1** | 58 | UqAvU1loT_k |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_V0gjxlaW2Qk.md` | `1` | **UNCHECKABLE** | 3 | V0gjxlaW2Qk |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_ZNvLh3JyOco.md` | `1` | **UNCHECKABLE** | 2 | ZNvLh3JyOco |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract__JoJbu_Ug-A.md` | `1` | **UNCHECKABLE** | 11 | _JoJbu_Ug-A |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract__t_XIBrcjRk.md` | `0` | **0** | 49 | _t_XIBrcjRk |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_fMRvOt26xcA.md` | `1` | **UNCHECKABLE** | 11 | fMRvOt26xcA |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_ftK2BqggabQ.md` | `1` | **1** | 63 | ftK2BqggabQ |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_hNfjyrJEytI.md` | `1` | **UNCHECKABLE** | 14 | hNfjyrJEytI |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_kcMnnQr1VFg.md` | `1` | **1** | 93 | kcMnnQr1VFg |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_qEfES84jwwo.md` | `0` | **0** | 65 | qEfES84jwwo |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_sCLLZKY_r8g.md` | `1` | **UNCHECKABLE** | 2 | sCLLZKY_r8g |
| `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_vjzy_KxJ_y8.md` | `0` | **0** | 93 | vjzy_KxJ_y8 |
| `MyTradingSys/research/malkan_extract_2026-10-15/COMPARE.md` | `0` | **0** | 24 | -CBvFi40sIQ, 2HcJ3NeZmEQ, A-CQiV_UFB4, W1HrDl70Lhk, Wvq1TZh8aF0 |
| `MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md` | `0` | **0** | 75 | -CBvFi40sIQ, 2HcJ3NeZmEQ, A-CQiV_UFB4, W1HrDl70Lhk, Wvq1TZh8aF0, cQ-y1oULkBw |
| `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_-CBvFi40sIQ.md` | `0` | **0** | 72 | -CBvFi40sIQ |
| `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_2HcJ3NeZmEQ.md` | `0` | **0** | 33 | 2HcJ3NeZmEQ |
| `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md` | `0` | **0** | 63 | A-CQiV_UFB4 |
| `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md` | `0` | **0** | 96 | W1HrDl70Lhk |
| `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md` | `0` | **0** | 115 | Wvq1TZh8aF0 |
| `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_cQ-y1oULkBw.md` | `0` | **0** | 61 | cQ-y1oULkBw |
| `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md` | `1` | **9 (partial captions)** | 21 | 2HcJ3NeZmEQ, 5Aoyw_sG_88, GbXnw_tNMtw, cQ-y1oULkBw, hGPqIpWRUMQ, v8pCR_bA0_0 |
| `MyTradingSys/research/pizzino_layer_2026-10-27/method_extraction.md` | `1` | **UNCHECKABLE** | 33 | 0ao14GkGLZY, 326kGNFr8tM, 4kpH94Hb0GQ, 7wl0C1lVfRE, 8TvLQ87KrfU, BsNHqXJeGbA, CY7-W_b7UAU, E_AP5kudK5Y, FPaXP3LE6c8, GaHjNt91mPU, Hlot1KhrlMs, IjC2eoUzA6M, ItDvhFyZoG8, Pg8Z7BezFeo, RCq5pfzA4oo, ZYrKqu8TxHo, a0sy0EW_nSA, nE2pJFXUjSU, y0gP2Ih6jwE |
| `MyTradingSys/research/setup_catalog_2026-10-15/EXTRACTION_CRITICAL_GAPS_2026-10-18.md` | `0` | **0** | 37 | 06R-ebyOhDI, 0KyIEdvVKMQ, 0jM5Y31YJak, 5Ljfwvtktek, 7BQPMJ39WpI, FawPrRUGNpk, HySZZSjMxF8, Khgj5q1-ln8, Of_wlv3xaZo, Pz8f0wWW12M, QClPWDJ-BrU, StaphlRH8NQ, cUTsoU-15Tc, etg6j0JybfE, o-w5Gxss6T0, zAwEX_tRUfE |
| `MyTradingSys/research/tom_correlation_trick_2026-10-26/EXTRACT.md` | `1` | **6 (partial captions)** | 15 | T6hDJcHrVBM, e83njGZFrPw, zQTbdEweG3c |
| `MyTradingSys/research/yt_feed_2026-10-31/COWEN_LEVELS_2026-10-31.md` | `1` | **UNCHECKABLE** | 21 | 21mBnslOLd0, 4oHSuPTr8H0, KZ1Jro92t48, bWdXPK3Hlok, bekghgecip8, eN6dpreDIk4, oYPawyUxnnE |
| `MyTradingSys/research/yt_feed_2026-10-31/REKT_LEVELS_2026-10-31.md` | `1` | **UNCHECKABLE** | 16 | BFMztI2UDQ4, C1kVrs-u0WM, MRBXsqgIGb8, P0v26DCPiZ4, XMbLOHZRSFo, ZAGbis1hfXw, s22yyxspRT0, y1VZlQtjUwY |

### Detailed Failures with Line Numbers (Command-Matched Extracts)

#### `MyTradingSys/research/_archive/loose_2026-10/T064_TF_CONFIRMATION_EXTRACT.md` (Exit 1, 2 failure(s))
- `POSITION T064_TF_CONFIRMATION_EXTRACT.md:41 tagged END, found MIDDLE`
- `POSITION T064_TF_CONFIRMATION_EXTRACT.md:96 tagged MIDDLE, found BEGIN`

#### `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_2-nG9bsMoPQ.md` (Exit 1, 1 failure(s))
- `POSITION extract_2-nG9bsMoPQ.md:117 tagged BEGIN, found MIDDLE`

#### `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_6aA-P4Gvhrc.md` (Exit 1, 1 failure(s))
- `POSITION extract_6aA-P4Gvhrc.md:123 tagged BEGIN, found MIDDLE`

#### `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_UqAvU1loT_k.md` (Exit 1, 1 failure(s))
- `POSITION extract_UqAvU1loT_k.md:254 tagged MIDDLE, found BEGIN`

#### `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_ftK2BqggabQ.md` (Exit 1, 1 failure(s))
- `POSITION extract_ftK2BqggabQ.md:99 tagged BEGIN, found MIDDLE`

#### `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_kcMnnQr1VFg.md` (Exit 1, 1 failure(s))
- `POSITION extract_kcMnnQr1VFg.md:404 tagged MIDDLE, found END`

#### `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md` (Exit 1, 9 failure(s))
- `NO-TRANSCRIPT MALKAN_RULES_2026-10-31.md:46 v8pCR_bA0_0`
- `NO-TRANSCRIPT MALKAN_RULES_2026-10-31.md:50 v8pCR_bA0_0`
- `NO-TRANSCRIPT MALKAN_RULES_2026-10-31.md:54 v8pCR_bA0_0`
- `NO-TRANSCRIPT MALKAN_RULES_2026-10-31.md:82 5Aoyw_sG_88`
- `NO-TRANSCRIPT MALKAN_RULES_2026-10-31.md:86 5Aoyw_sG_88`
- `NO-TRANSCRIPT MALKAN_RULES_2026-10-31.md:90 5Aoyw_sG_88`
- `NO-TRANSCRIPT MALKAN_RULES_2026-10-31.md:118 hGPqIpWRUMQ`
- `NO-TRANSCRIPT MALKAN_RULES_2026-10-31.md:122 hGPqIpWRUMQ`
- `NO-TRANSCRIPT MALKAN_RULES_2026-10-31.md:126 hGPqIpWRUMQ`

#### `MyTradingSys/research/tom_correlation_trick_2026-10-26/EXTRACT.md` (Exit 1, 6 failure(s))
- `NO-TRANSCRIPT EXTRACT.md:58 e83njGZFrPw`
- `NO-TRANSCRIPT EXTRACT.md:64 e83njGZFrPw`
- `NO-TRANSCRIPT EXTRACT.md:70 e83njGZFrPw`
- `NO-TRANSCRIPT EXTRACT.md:76 e83njGZFrPw`
- `NO-TRANSCRIPT EXTRACT.md:82 e83njGZFrPw`
- `NO-TRANSCRIPT EXTRACT.md:88 e83njGZFrPw`

### Uncheckable Extracts (No Caption File on Host)

- `MyTradingSys/research/krown_audit_2026-10-22/GEMINI_RULES_QUOTE_AUDIT.md` (18 quotes, missing video IDs: -9rAJNUpMsk, EQy4HouRMMk, SOaAP9vBgM4, UHY740h3e-Y)
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_LB3DRYxnA0A.md` (10 quotes, missing video IDs: LB3DRYxnA0A)
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_OggsnATGbOg.md` (3 quotes, missing video IDs: OggsnATGbOg)
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_V0gjxlaW2Qk.md` (3 quotes, missing video IDs: V0gjxlaW2Qk)
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_ZNvLh3JyOco.md` (2 quotes, missing video IDs: ZNvLh3JyOco)
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract__JoJbu_Ug-A.md` (11 quotes, missing video IDs: _JoJbu_Ug-A)
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_fMRvOt26xcA.md` (11 quotes, missing video IDs: fMRvOt26xcA)
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_hNfjyrJEytI.md` (14 quotes, missing video IDs: hNfjyrJEytI)
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_sCLLZKY_r8g.md` (2 quotes, missing video IDs: sCLLZKY_r8g)
- `MyTradingSys/research/pizzino_layer_2026-10-27/method_extraction.md` (33 quotes, missing video IDs: 0ao14GkGLZY, 326kGNFr8tM, 4kpH94Hb0GQ, 7wl0C1lVfRE, 8TvLQ87KrfU, BsNHqXJeGbA, CY7-W_b7UAU, E_AP5kudK5Y, FPaXP3LE6c8, GaHjNt91mPU, Hlot1KhrlMs, IjC2eoUzA6M, ItDvhFyZoG8, Pg8Z7BezFeo, RCq5pfzA4oo, ZYrKqu8TxHo, a0sy0EW_nSA, nE2pJFXUjSU, y0gP2Ih6jwE)
- `MyTradingSys/research/yt_feed_2026-10-31/COWEN_LEVELS_2026-10-31.md` (21 quotes, missing video IDs: 21mBnslOLd0, 4oHSuPTr8H0, KZ1Jro92t48, bWdXPK3Hlok, bekghgecip8, eN6dpreDIk4, oYPawyUxnnE)
- `MyTradingSys/research/yt_feed_2026-10-31/REKT_LEVELS_2026-10-31.md` (16 quotes, missing video IDs: BFMztI2UDQ4, C1kVrs-u0WM, MRBXsqgIGb8, P0v26DCPiZ4, XMbLOHZRSFo, ZAGbis1hfXw, s22yyxspRT0, y1VZlQtjUwY)

## 3. Comprehensive Audit: All Research Markdown Documents Quoting Captions

For full corpus coverage across `MyTradingSys/research`, here is the audit of the remaining 30 files with `Source GPS` video quotes:

| Document Path | Exit Code | Failing Quote Count / Status | Total Quotes | Video IDs |
|---|:---:|:---:|:---:|---|
| `MyTradingSys/research/EXEC_PROVENANCE_AUDIT.md` | `0` | **0** | 52 | 0jM5Y31YJak, 3o1VVsfBmmU, 4MoNjEQ2Dd8, 8CWKfoSJu3c, BVpYGKz9PBU, FawPrRUGNpk, UOBgXV20yCM, UrZ4vpHJ97g, WSCIURybK3U, fZlNGWvd2Ko, k0zm5NYn0IQ, kXhIAug0Gh8, qLnQan0KGmQ, tS6ZEiHj8gQ, yRvMW6lgN1o |
| `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md` | `1` | **UNCHECKABLE** | 11 | Jn9hM3jwEik, MiQePVTGCXQ, SfPE7sWygLE, _QG1bt4iwQc, fnRXA4AzEcI, lJ8rI4iiXG4 |
| `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md` | `1` | **UNCHECKABLE** | 9 | BHwoN7VPrBE, XeQV2ECtZVQ, inqHN8q57X4 |
| `MyTradingSys/research/fast_track_2026-09-27/ANGLE_TRADE_CATALOG.md` | `0` | **0** | 39 | 0jM5Y31YJak, 3o1VVsfBmmU, 4MoNjEQ2Dd8, 8CWKfoSJu3c, BVpYGKz9PBU, FawPrRUGNpk, OUM9LYwL8eA, T6hDJcHrVBM, UOBgXV20yCM, UrZ4vpHJ97g, WSCIURybK3U, Wvq1TZh8aF0, dh-ysRR8f-M, fZlNGWvd2Ko, jasv3L-d8ZE, k0zm5NYn0IQ, kXhIAug0Gh8, l8RZrBfzvp4, n7ZSkjb7JXs, pgdmKLJ0hhA, tS6ZEiHj8gQ, ujedEcmvBMk, wPMiyJXL0zU, yRvMW6lgN1o, zAwEX_tRUfE, zQTbdEweG3c |
| `MyTradingSys/research/fast_track_2026-09-27/FABIO_LINE_BY_LINE_fZlNGWvd2Ko.md` | `0` | **0** | 25 | fZlNGWvd2Ko |
| `MyTradingSys/research/fast_track_2026-09-27/MISSING_PIECES_2026-09-30.md` | `1` | **1** | 23 | LQvv5xgy_ik, fZlNGWvd2Ko, jasv3L-d8ZE, yRvMW6lgN1o |
| `MyTradingSys/research/fast_track_2026-09-27/PROVENANCE_AUDIT_TOM.md` | `0` | **0** | 52 | -dMWA_bbm3o, 3JqMyzE8jIQ, 3o1VVsfBmmU, 43JaKHRvxHk, 4MoNjEQ2Dd8, BVpYGKz9PBU, KEe_CWHyuSg, NkQeOVDTAec, YmygDgtoxO8, YopZ5ZDmMFw, aursfDVYzUk, k0zm5NYn0IQ, oa8kxSLLkAo, qLnQan0KGmQ, rFPCtOcfUMI, rrHj24GSR6M, tS6ZEiHj8gQ, y67l86cSqb8, yRvMW6lgN1o, zAwEX_tRUfE, zQTbdEweG3c |
| `MyTradingSys/research/fast_track_2026-09-27/TOM_LINE_BY_LINE_4MoNjEQ2Dd8.md` | `0` | **0** | 20 | 4MoNjEQ2Dd8 |
| `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md` | `1` | **UNCHECKABLE** | 22 | -0UiEM32DX4, 4wlnRxGsSdE, 5x8DhXBwX9c, dmC1U_r8PFc, lJ8rI4iiXG4, mZSSzC6C_Qg, p9KajODtBsU, xIUHpTirh_g, xc4TyMS3HKc |
| `MyTradingSys/research/krown_capture_2026-10-16/KROWN_VIEWS_HIGHS.md` | `1` | **3 (partial captions)** | 9 | 14bxwxC8gBQ, 2-nG9bsMoPQ, _t_XIBrcjRk, dzH7m9cQeZA, fMRvOt26xcA, qEfES84jwwo |
| `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md` | `1` | **UNCHECKABLE** | 12 | 8cC9Jpc8D5c, LMRNBdMiQ2g, TDQwVve6G3Y, bXug2l6qICc, dLq5Jyir3Iw, ro6tMlqbbBI, zay_owGmjo0 |
| `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md` | `1` | **2** | 229 | -NXzJs5JRks, 0jM5Y31YJak, 14bxwxC8gBQ, 2-nG9bsMoPQ, 2HcJ3NeZmEQ, 2ei4fj-Ba24, 2xnNPIyHGQ4, 43JaKHRvxHk, 4VXpUjhKG2U, 6aA-P4Gvhrc, 7IxfsuD2wCM, 8MvxK_nxO-0, A-CQiV_UFB4, FawPrRUGNpk, INOCBmqQupc, Ly62G168MkQ, UqAvU1loT_k, Wvq1TZh8aF0, _t_XIBrcjRk, cQ-y1oULkBw, cw8LWQmec1E, gFJBg8Bsw68, kcMnnQr1VFg, m3IMdc7QwN4, qEfES84jwwo, uFxYcpiaOpw, viT_VzF5Fsw, vjzy_KxJ_y8 |
| `MyTradingSys/research/layer_lab/gpt-catalog-notstated-audit/CATALOG_AUDIT.md` | `0` | **0** | 13 | 0jM5Y31YJak, 4MoNjEQ2Dd8, 8CWKfoSJu3c, FawPrRUGNpk, YkclL6xgu-s, fZlNGWvd2Ko, jasv3L-d8ZE, viT_VzF5Fsw, yRvMW6lgN1o |
| `MyTradingSys/research/layer_lab/reports/2026-10-15_gpt-catalog-notstated-audit.md` | `0` | **0** | 13 | 0jM5Y31YJak, 4MoNjEQ2Dd8, 8CWKfoSJu3c, FawPrRUGNpk, YkclL6xgu-s, fZlNGWvd2Ko, jasv3L-d8ZE, viT_VzF5Fsw, yRvMW6lgN1o |
| `MyTradingSys/research/layer_lab/reports/layer_review_tom_guidance.md` | `0` | **0** | 29 | -dMWA_bbm3o, 43JaKHRvxHk, 4MoNjEQ2Dd8, 4VXpUjhKG2U, 8CWKfoSJu3c, FawPrRUGNpk, Fj4FDZQxw0I, Ld1dhjGdTCA, T6hDJcHrVBM, YmygDgtoxO8, k0zm5NYn0IQ, l8RZrBfzvp4, sQ_biBKhPVU, y67l86cSqb8, zQTbdEweG3c |
| `MyTradingSys/research/observer_severity_context/DESIGN.md` | `0` | **0** | 3 | qLnQan0KGmQ, wPMiyJXL0zU, y67l86cSqb8 |
| `MyTradingSys/research/pizzino_layer_2026-10-27/method_jason.md` | `1` | **UNCHECKABLE** | 15 | 0ao14GkGLZY, 4kpH94Hb0GQ, BsNHqXJeGbA, CY7-W_b7UAU, GaHjNt91mPU, Hlot1KhrlMs, ItDvhFyZoG8, RCq5pfzA4oo, nE2pJFXUjSU |
| `MyTradingSys/research/pizzino_layer_2026-10-27/method_michael.md` | `1` | **UNCHECKABLE** | 18 | 326kGNFr8tM, 7wl0C1lVfRE, 8TvLQ87KrfU, E_AP5kudK5Y, FPaXP3LE6c8, IjC2eoUzA6M, Pg8Z7BezFeo, ZYrKqu8TxHo, a0sy0EW_nSA, y0gP2Ih6jwE |
| `MyTradingSys/research/rsi_kurisko_2026-10-09/RSI_VIDEO_SEARCH.md` | `0` | **0** | 10 | 5MgOwizsnjk, 6rHybt-DfQ0, I0rxiH1jZwc, LD_LOEeKzMs, XNfOIzPYChA, rCTrQ4fkL1Y |
| `MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md` | `1` | **1** | 341 | 06R-ebyOhDI, 0CrkbfuIhkc, 0jM5Y31YJak, 15JoLK0PbMU, 1utSjHs_Mq8, 2xnNPIyHGQ4, 3o1VVsfBmmU, 43JaKHRvxHk, 4MoNjEQ2Dd8, 4VXpUjhKG2U, 5Ljfwvtktek, 6BAzqewtPUk, 7BQPMJ39WpI, 8CWKfoSJu3c, 96iPFDpXEcU, 9IliXww64uM, BVpYGKz9PBU, DVZVE9rXGtU, DyS79Eb92Ug, FawPrRUGNpk, G0CiJcuXCRs, HySZZSjMxF8, Is1HvdfQm5c, K8qtT2_axPo, Khgj5q1-ln8, LQvv5xgy_ik, Ld1dhjGdTCA, Ly62G168MkQ, NkQeOVDTAec, ODdF0Bn_KSc, OUM9LYwL8eA, Of_wlv3xaZo, Pz8f0wWW12M, QClPWDJ-BrU, ShYS_pD5cxQ, Sy-x5AQ9-Pk, UrZ4vpHJ97g, VOiy8mAALWA, VxN5IxTwpbE, WQ_OAdz-PJ8, WSCIURybK3U, YYYuaetck_0, YkclL6xgu-s, YopZ5ZDmMFw, aursfDVYzUk, cw8LWQmec1E, etg6j0JybfE, fZlNGWvd2Ko, gFJBg8Bsw68, gWjHq5UMisY, hQ8sOq67x5o, jXR1afMy-3o, jasv3L-d8ZE, k0zm5NYn0IQ, kXhIAug0Gh8, lO-Iptd29t4, m3IMdc7QwN4, o-w5Gxss6T0, oPyUif2Zrtk, pgdmKLJ0hhA, qLnQan0KGmQ, tS6ZEiHj8gQ, uFxYcpiaOpw, uk4PZV59nYw, viT_VzF5Fsw, wPMiyJXL0zU, yRvMW6lgN1o, zAwEX_tRUfE |
| `MyTradingSys/research/setup_catalog_2026-10-15/drafts/KRW-RANGE-BB-MAP.md` | `0` | **0** | 16 | 6aA-P4Gvhrc, INOCBmqQupc, qEfES84jwwo |
| `MyTradingSys/research/setup_catalog_2026-10-15/drafts/MAL-BB-MID-ENGULF.md` | `0` | **0** | 1 | 2HcJ3NeZmEQ |
| `MyTradingSys/research/setup_catalog_2026-10-15/drafts/MAL-BB-RSI-4060.md` | `0` | **0** | 7 | -CBvFi40sIQ, 2HcJ3NeZmEQ, A-CQiV_UFB4, W1HrDl70Lhk, Wvq1TZh8aF0, cQ-y1oULkBw |
| `MyTradingSys/research/setup_catalog_2026-10-15/malkan/MALKAN_DIVERGENCE_GLOSSARY.md` | `0` | **0** | 81 | A-CQiV_UFB4, GbXnw_tNMtw, Wvq1TZh8aF0, cQ-y1oULkBw |
| `MyTradingSys/research/vp_pivots_2026-10-09/SOURCES.md` | `0` | **0** | 18 | 0CrkbfuIhkc, 1utSjHs_Mq8, BVpYGKz9PBU, HySZZSjMxF8, ODdF0Bn_KSc, YmygDgtoxO8, aursfDVYzUk, kXhIAug0Gh8, oa8kxSLLkAo, sQ_biBKhPVU |
| `MyTradingSys/research/wiring_audit_2026-10/QUOTES_USED_MALKAN_KROWN.md` | `0` | **0** | 163 | -NXzJs5JRks, 14bxwxC8gBQ, 2-nG9bsMoPQ, 2ei4fj-Ba24, 6aA-P4Gvhrc, 7IxfsuD2wCM, 8MvxK_nxO-0, A-CQiV_UFB4, Aysdt7PBETQ, GbXnw_tNMtw, HhV4HI9p5Uw, INOCBmqQupc, UqAvU1loT_k, Wvq1TZh8aF0, _t_XIBrcjRk, cQ-y1oULkBw, ftK2BqggabQ, kcMnnQr1VFg, qEfES84jwwo, vjzy_KxJ_y8 |
| `MyTradingSys/research/wiring_audit_2026-10/QUOTES_USED_TOM_FABIO.md` | `0` | **0** | 442 | -dMWA_bbm3o, 0KyIEdvVKMQ, 0jM5Y31YJak, 3JqMyzE8jIQ, 3o1VVsfBmmU, 43JaKHRvxHk, 4MoNjEQ2Dd8, 8CWKfoSJu3c, 96iPFDpXEcU, BVpYGKz9PBU, DVZVE9rXGtU, FawPrRUGNpk, Fj4FDZQxw0I, Khgj5q1-ln8, LQvv5xgy_ik, Ld1dhjGdTCA, NkQeOVDTAec, Of_wlv3xaZo, Pz8f0wWW12M, StaphlRH8NQ, VumVuGnCcFM, YmygDgtoxO8, YopZ5ZDmMFw, cUTsoU-15Tc, dh-ysRR8f-M, fZlNGWvd2Ko, jasv3L-d8ZE, k0zm5NYn0IQ, kXhIAug0Gh8, l8RZrBfzvp4, lO-Iptd29t4, o-w5Gxss6T0, oa8kxSLLkAo, qLnQan0KGmQ, rFPCtOcfUMI, ujedEcmvBMk, wPMiyJXL0zU, y67l86cSqb8, yRvMW6lgN1o, zQTbdEweG3c |
| `MyTradingSys/research/yt_feed_2026-10-31/JASON_BAR_UPDATE_2026-10-31.md` | `1` | **UNCHECKABLE** | 48 | 4kpH94Hb0GQ, DFXb-Qt_JdI, GaHjNt91mPU, JTbBJ-OhDN0, U5c_3iRZLV4, dH-Y0pxOPD8, es_I-z8Pnek, iZisjh6Dags, pQMbwmoFZqU, v_Aw5x7Hsns |
| `MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md` | `1` | **UNCHECKABLE** | 18 | BU6j1p-bNUY, DU0nwsY-8WY, FYxQXT8J7ek, VWsFf5rQoqE, aKbB7gV67M4, ctJSV8aTDSk, fk1dkrGUar4, wzve_n4gBY4 |
| `MyTradingSys/research/yt_feed_2026-10-31/MICHAEL_BAR_UPDATE_2026-10-31.md` | `1` | **UNCHECKABLE** | 49 | 2mgLIG4myCU, 326kGNFr8tM, 7wl0C1lVfRE, E_AP5kudK5Y, F0HeO0os0GM, IjC2eoUzA6M, KKnktsvQMyo, NWwIbm6j6wg, _LDxOX42NS8 |

### Detailed Failures in Other Research Documents

#### `MyTradingSys/research/fast_track_2026-09-27/MISSING_PIECES_2026-09-30.md` (Exit 1, 1 failure(s))
- `POSITION MISSING_PIECES_2026-09-30.md:175 tagged END, found MIDDLE`

#### `MyTradingSys/research/krown_capture_2026-10-16/KROWN_VIEWS_HIGHS.md` (Exit 1, 3 failure(s))
- `NO-TRANSCRIPT KROWN_VIEWS_HIGHS.md:34 fMRvOt26xcA`
- `NO-TRANSCRIPT KROWN_VIEWS_HIGHS.md:37 dzH7m9cQeZA`
- `NO-TRANSCRIPT KROWN_VIEWS_HIGHS.md:59 dzH7m9cQeZA`

#### `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md` (Exit 1, 2 failure(s))
- `POSITION KROWN_SETUP_CATALOG.md:383 tagged BEGIN, found MIDDLE`
- `POSITION KROWN_SETUP_CATALOG.md:622 tagged MIDDLE, found END`

#### `MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md` (Exit 1, 1 failure(s))
- `POSITION SETUP_CATALOG.md:658 tagged MIDDLE, found BEGIN`

