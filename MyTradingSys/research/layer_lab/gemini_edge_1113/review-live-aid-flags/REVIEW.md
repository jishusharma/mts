# Blind Review: Live Aid Flags & Liquidation Meaning Studies (2026-11-13)

**Verdict: SOUND**

## 1. Executive Summary & Verdict
- **Verdict: SOUND**
- Blind review of `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md` and `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md`, together with their underlying execution scripts and imported code (`MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py`, `scripts/dev/live_aid_learn.py`, `MyTradingSys/tools/live_aid/home.js`, `MyTradingSys/tools/live_aid/liq_rates.js`, and `MyTradingSys/research/live_aid_learning/2026-11-13.md`).
- **Recount Verification:**
  - In `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md`, the headline verdict is explicitly `NOT MEASURED. No usable liquidation history exists. No number is given.` (`MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:5`). Recount confirmed that `runtime_data/live_aid/xliq_events.jsonl` does not exist on disk, no historical execution data exists, and `liq_meaning.py` writes empty rows `rows: []` to `MyTradingSys/tools/live_aid/liq_rates.js:6`. This claim is 100% verified and consistent with live repo state.
  - In `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md`, headline numbers cite the daily replay learning output `MyTradingSys/research/live_aid_learning/2026-11-13.md` (e.g. setup n=1342, 51%; idea n=763, 47%; Europe high n=30, 60%). The underlying 28-day replay event log (`events.json`) is not committed on disk (`MyTradingSys/research/live_aid_learning/2026-11-13.md:37-38` notes real browser log rows = 0; replay refreshed via public Binance 1m data-api). Therefore, the raw events are UNVERIFIABLE on local disk, but all cited numbers in `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md` MATCH their cited source documents exactly (see Table 1).
- **Look-Ahead Hunt:** ZERO look-ahead bias found. In `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:82-89`, decision reference price `ref` is taken strictly from the close of the last full minute inside the bin (`t_ref`), and forward returns are measured at `t_ref + h * 60_000` (`h in (5, 15, 60)`). Feature bins are strictly aligned to past/current windows.
- **Fee & Slippage Hunt:** `liq_meaning.py` measures pure price excursion (`(f / ref - 1) * 100`) as a descriptive context observation, not an execution strategy; no fees or slippage are deducted, consistent with its descriptive scope (`MyTradingSys/tools/live_aid/liq_rates.js:2-4` and `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:25-26`).

---

## 2. Claim Verification & Recount Table

| Section & Document | Claim | Claimed Value | Recounted / Source Value | Status | Citation |
|---|---|---|---|---|---|
| RESULT: Verdict | Liquidation burst continuation verdict | `NOT MEASURED` | `NOT MEASURED` (no xliq_events.jsonl on disk) | MATCH | SOURCED `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:5`, `MyTradingSys/tools/live_aid/liq_rates.js:6` |
| RESULT: Inputs | Collector history file | xliq_events.jsonl missing | Missing (file not found on disk) | MATCH | SOURCED `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:10` |
| RESULT: Thresholds | Minimum span threshold | 24 h minimum span | MIN_SPAN_H = 24 | MATCH | SOURCED `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:18`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:20` |
| RESULT: Thresholds | Burst USD bucket thresholds | 250k / 1M / 5M USD | BUCKETS list: 250k, 1M, 5M | MATCH | SOURCED `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:19`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:21` |
| RESULT: Thresholds | Same-side burst dedup window | 15 min | DEDUP_MS = 15 * 60_000 | MATCH | SOURCED `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:19`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:23` |
| RESULT: Thresholds | Return horizons | 5, 15, 60 min | HORIZ = (5, 15, 60) | MATCH | SOURCED `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:19`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:24` |
| RESULT: Thresholds | Anecdote threshold | n < 30 | r["n"] < 30 | MATCH | SOURCED `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:19`, `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:132` |
| REVIEW: Section 0 | Setup banner replay hit rate | n=1342, 51% | n=1342, 51% (raw events not committed on disk) | UNVERIFIABLE (DATA NOT ON DISK) | SOURCED `MyTradingSys/research/live_aid_learning/2026-11-13.md:7`, `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:79` |
| REVIEW: Section 0 | Idea banner replay hit rate | n=763, 47% | n=763, 47% (raw events not committed on disk) | UNVERIFIABLE (DATA NOT ON DISK) | SOURCED `MyTradingSys/research/live_aid_learning/2026-11-13.md:8`, `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:79` |
| REVIEW: Section 1 | Level story fade Europe high | n=30, 60% | n=30, 60% (raw events not committed on disk) | UNVERIFIABLE (DATA NOT ON DISK) | SOURCED `MyTradingSys/research/live_aid_learning/2026-11-13.md:20`, `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:28` |
| REVIEW: Section 0 | Removal of IDEA/SETUP banners | Gone since card live-aid-board-render-1111 | Confirmed by code comment in flashes() | MATCH | SOURCED `MyTradingSys/tools/live_aid/home.js:67`, `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:10` |
| REVIEW: Section 0 | WaveTrend one-line sentence commit | Commit 35888094e | Commit 35888094efe968fee24548ea3a3b4bba4dcf4ae6 | MATCH | SOURCED `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:13` |
| REVIEW: Section 5 | MTS layer surviving PASS | 0 of 40 fee-net rows | 0 of 40 fee-net rows | MATCH | SOURCED `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:80` |

---

## 3. Look-Ahead Hunt
Inspection of `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py`:
1. **Burst Grouping & Bin Timestamps:**
   - In `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:56-69`:
     Bins are strictly formed from event timestamps `t <= end` where `end = (b + 1) * win_ms`.
2. **Reference Price Bar vs Return Evaluation:**
   - In `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:82-87`:
     For an aligned 1m bin ending at `end`, `t_ref = end - 60_000` is the start of the 1m candle that closes exactly at `end`.
   - The reference price `ref` is the close of the candle inside the bin (`c[t_ref]`), which is known when the burst bin closes.
   - Forward prices `f` are evaluated at horizons `h in (5, 15, 60)` minutes into the future (`t_ref + h * 60_000`).
   - No bar after `end` is used to trigger or bucket the burst.
3. **Verdict on Look-Ahead:** **CLEAN. No look-ahead detected.**

---

## 4. Fee and Slippage Audit
1. **Model Scope:**
   - In `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:89`, price return is calculated as `(f / ref - 1) * 100`.
   - No transaction fees or slippage are deducted.
2. **Evaluation:**
   - As documented in `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:25-26` and `MyTradingSys/tools/live_aid/liq_rates.js:2`, this study measures raw market continuation after liquidation bursts as descriptive context for the operator, not as an automated trading strategy.
   - There are no missing fees or double-counted fees within the stated descriptive scope.
3. **Verdict on Fees & Slippage:** **CLEAN. Consistent with descriptive market measurement.**

---

## 5. Citations & References
- SOURCED `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:1-33`
- SOURCED `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:1-141`
- SOURCED `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:1-82`
- SOURCED `MyTradingSys/tools/live_aid/home.js:51-76,400-450`
- SOURCED `MyTradingSys/tools/live_aid/liq_rates.js:1-15`
- SOURCED `MyTradingSys/research/live_aid_learning/2026-11-13.md:1-60`
