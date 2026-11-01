# Layer Lab Report: Blind Re-Read of Rumers Extracts 1 & 2 Testable Shortlists

- **Task**: `gemini-blind-read-rumers-extracts-1101`
- **Lane**: `CODEX`
- **Date**: 2026-11-01
- **Auditor**: Gemini worker (Antigravity JIS-NUC)
- **Extracts Audited**: `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md` and `RUMERS_EXTRACT_2.md`
- **Primary Deliverable**: `research/gemini_audits_2026-11-01/rumers_extract_blind_read.md`

---

## 1. Executive Summary

A blind re-read and provenance audit was conducted on the 8 mechanical setup rules defined in Section 3 of `RUMERS_EXTRACT_1.md` and `RUMERS_EXTRACT_2.md`. Each rule's Entry, Stop Loss, and Target conditions were systematically compared against the verbatim caption quotes cited in Section 2 of each extract and verified against the canonical raw transcripts in `raw_transcripts_canonical/`.

- **Total Setup Rules Audited**: 8
- **SUPPORTED**: 2 (25.0%)
- **PARTLY**: 6 (75.0%)
- **NOT_IN_QUOTE**: 0 (0.0%)
- **Deliverable First Line Verification**: `# SUPPORTED: 2, PARTLY: 6, NOT_IN_QUOTE: 0`

---

## 2. Findings Summary by Setup

| Setup Rule | Primary Video(s) | Status | Supported Fields | Unquoted Fields / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `EXTRACT_1 s3 T1` (`RUMERS-ORB-MANIP-REVERSAL`) | `6WfTIyJ-YzQ`, `aTMFouI9mF4` | SUPPORTED | Entry, Stop, Target | Fully supported by verbatim quotes on 15m range, 30-50% candle retracement, HOD/LOD stops, and 50%-100% range targets. |
| `EXTRACT_1 s3 T2` (`RUMERS-BOX-PDH-PDL-FADE`) | `EoQDQVblmMY` | PARTLY | Stop, Target | Stop (LOD) and Target (box center) quoted; Entry ("5m rejection candle closing back inside box") is in stated rules (R08) but omitted from Section 2 verbatim quotes. |
| `EXTRACT_1 s3 T3` (`RUMERS-VWAP-SEPARATOR-MEAN-REVERSION`) | `kozesVBKkg4` | PARTLY | Entry, Target | Entry (separation at open) and Target (reconvening with VWAP) quoted; Stop (exhaustion wick) cited at timestamp 00:14:56 but omitted from Section 2 quotes. |
| `EXTRACT_1 s3 T4` (`RUMERS-VWAP-KISS-PIVOT-CONTINUATION`) | `kozesVBKkg4` | PARTLY | Entry | Entry (KISS pivot bounce off VWAP) quoted; Stop (swing pivot) and Target (1:2 R:R) cited at timestamp 00:16:17 but omitted from Section 2 quotes. |
| `EXTRACT_2 s3 Setup T1` (15-Minute Pattern Scalp Reversal) | `T0H_jpQXdVI` | PARTLY | Entry, Stop | Entry (break of John Wick extreme) and Stop (below John Wick) quoted; Target (50% midpoint) defined in Section 1 (R04) but omitted from Section 2 quotes. |
| `EXTRACT_2 s3 Setup T2` (4-Point Boundary Confluence Fade) | `pcYO-yzAtrQ` | PARTLY | Entry, Stop | Entry (break of structure candle close) and Stop (above high) quoted; Target (midpoint or opposite boundary) in Section 1 (R09) but omitted from Section 2 quotes. |
| `EXTRACT_2 s3 Setup T3` (Hourly RSI Liquidity Reversal) | `hMURCHLnZVE` | PARTLY | Entry, Stop | Entry (close above hourly green candle) and Stop (below red/green extreme) quoted; Target (swing high / trail toward RSI 50) in Section 1 (R14) but omitted from Section 2 quotes. |
| `EXTRACT_2 s3 Setup T4` (9 EMA 20% ATR Separation Reversion) | `l0j1irTKIUw`, `xtN0U-j_4Jc` | SUPPORTED | Entry, Stop, Target | Fully supported by verbatim quotes on 9 EMA separation, reversal bar stop, and 9 EMA revisitation / trailing guide target. |

---

## 3. Verification Protocol

- Canonical transcripts checked in `raw_transcripts_canonical/` for all 9 referenced videos: `6WfTIyJ-YzQ`, `EoQDQVblmMY`, `kozesVBKkg4`, `aTMFouI9mF4`, `T0H_jpQXdVI`, `pcYO-yzAtrQ`, `hMURCHLnZVE`, `xtN0U-j_4Jc`, `l0j1irTKIUw`.
- All line numbers verified against committed files on branch.
- No backtest or live-tree changes made.

---

Noticed: The high proportion of PARTLY classifications reflects the extract constraint of 5 verbatim quotes per video, which led extractors to prioritize entry trigger mechanisms and stop risk definitions over profit target and trailing rules, even when those rules were explicitly stated in the timestamped rules of Section 1.
