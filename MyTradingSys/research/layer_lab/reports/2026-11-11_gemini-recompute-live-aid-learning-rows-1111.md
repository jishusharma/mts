COUNTS: MATCH=17 DIFF=0 NOT_IN_DATA=0

# Independent Gemini Recomputation: live_aid_learning 2026-11-11 Hit Rates from Review Tables

- **Card**: `gemini-recompute-live-aid-learning-rows-1111`
- **Date**: 2026-11-11 UTC
- **Reader / Auditor**: Gemini (`gemini-3.8-flash-low`, JIS-NUC throwaway worktree `gemini-q/gemini-recompute-live-aid-learning-rows-1111`)
- **Scope In (read-only)**:
  - `MyTradingSys/research/live_aid_learning/2026-11-11.md` (read)
  - `MyTradingSys/research/live_aid_review_2026-11-11/tables.md` (read)
  - `MyTradingSys/research/live_aid_review_2026-11-11/events.json` (read attempt; gitignored runtime file, not tracked in repo)
  - `MyTradingSys/research/live_aid_review_2026-11-11/analyze.py` (read)
  - `scripts/dev/live_aid_learn.py` (read; rule definition)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-recompute-live-aid-learning-rows-1111.md` (new report)
- **Scope Out Respected**:
  - No edit to source files; no live-tree edit; no deploy; no `.secrets` or `.env` read; read-only audit.
  - Zero push; no `sync.py ship`; no `REVIEWED` stamp.

---

## 1. Executive Summary & Verification Methodology

- Total target clauses / rows audited: **17** (exact match to all 17 rows of `2026-11-11.md`).
- Recomputation result: **MATCH = 17, DIFF = 0, NOT_IN_DATA = 0**.
- **Rule Specification** [SOURCED `scripts/dev/live_aid_learn.py:8,20,23-28`]:
  - `hit = r1h > 0` (percentage calculated as `100.0 * sum(r1h > 0) / n` rounded to integer).
  - Decision threshold: test only if `n >= 30` and `abs(hit - 50) >= 10.0` points.
  - Verdict logic:
    - If `n >= 30` and `abs(hit - 50) >= 10.0`:
      - If `hit < 50`: `test: drop or invert the flag (n <n>, <hit>%)`
      - If `hit >= 50`: `test: keep and weight the flag (n <n>, <hit>%)`
    - Else:
      - If `n < 30`: `NOT-ENOUGH-EVIDENCE (n < 30)`
      - If `n >= 30` and `abs(hit - 50) < 10.0`: `NOT-ENOUGH-EVIDENCE (gap < 10 pts)`
- **Data Source Note**:
  - `events.json` is gitignored (`.gitignore:2`) per repo policy against committing raw runtime/tick logs.
  - As defined in `scripts/dev/live_aid_learn.py:6-7,53-64`, input fallback when `events.json` is absent is the committed aggregate `tables.md` in `MyTradingSys/research/live_aid_review_2026-11-11/tables.md`.
  - All 17 flag groups recompute identically from `tables.md` sections `### By flag kind`, `### Idea by level state`, and `### Idea fades (rejected / failed break) by level`.
  - Every single row in `2026-11-11.md` agrees on `n`, `hit percent`, and `verdict`.

---

## 2. Row Recomputation Table (17 Rows)

| # | Flag Group / Change | Stated in `2026-11-11.md` (n, hit, verdict) | Recomputed from `tables.md` (OURS arithmetic) | Status | File:Line Citations & Quotes |
|---|---|---|---|---|---|
| 1 | `setup` | `n=1262`, `51%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=1262`, `51%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:7`: `\| setup \| 1262 \| 51% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:7`: `\| setup \| 1262 \| 51% \| -0.01 \| +0.27 \| -0.28 \|` |
| 2 | `idea` | `n=759`, `47%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=759`, `47%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:8`: `\| idea \| 759 \| 47% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:6`: `\| idea \| 759 \| 47% \| -0.01 \| +0.29 \| -0.31 \|` |
| 3 | `idea REJECTED` | `n=290`, `49%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=290`, `49%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:9`: `\| idea REJECTED \| 290 \| 49% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:14`: `\| REJECTED \| 290 \| 49% \| -0.03 \| +0.29 \| -0.36 \|` |
| 4 | `idea ACCEPTED` | `n=253`, `43%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=253`, `43%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:10`: `\| idea ACCEPTED \| 253 \| 43% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:16`: `\| ACCEPTED \| 253 \| 43% \| -0.02 \| +0.30 \| -0.31 \|` |
| 5 | `idea FAILED BREAK` | `n=216`, `49%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=216`, `49%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:11`: `\| idea FAILED BREAK \| 216 \| 49% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:15`: `\| FAILED BREAK \| 216 \| 49% \| +0.02 \| +0.28 \| -0.24 \|` |
| 6 | `idea fade @ Day open` | `n=128`, `46%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=128`, `46%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:12`: `\| idea fade @ Day open \| 128 \| 46% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:110`: `\| Day open \| 128 \| 46% \| -0.05 \| +0.22 \| -0.26 \|` |
| 7 | `idea fade @ 2-day-ago low` | `n=67`, `48%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=67`, `48%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:13`: `\| idea fade @ 2-day-ago low \| 67 \| 48% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:107`: `\| 2-day-ago low \| 67 \| 48% \| -0.03 \| +0.28 \| -0.32 \|` |
| 8 | `idea fade @ Asia low` | `n=56`, `45%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=56`, `45%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:14`: `\| idea fade @ Asia low \| 56 \| 45% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:109`: `\| Asia low \| 56 \| 45% \| +0.13 \| +0.36 \| -0.24 \|` |
| 9 | `idea fade @ Yesterday low` | `n=50`, `40%`, `test: drop or invert the flag (n 50, 40%)` | `n=50`, `40%`, `test: drop or invert the flag (n 50, 40%)` | `MATCH` | SOURCED `2026-11-11.md:15`: `\| idea fade @ Yesterday low \| 50 \| 40% \| first run \| test: drop or invert the flag (n 50, 40%) \|`<br>SOURCED `tables.md:116`: `\| Yesterday low \| 50 \| 40% \| -0.16 \| +0.30 \| -0.53 \|` |
| 10 | `idea fade @ Asia high` | `n=48`, `44%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=48`, `44%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:16`: `\| idea fade @ Asia high \| 48 \| 44% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:108`: `\| Asia high \| 48 \| 44% \| -0.00 \| +0.21 \| -0.24 \|` |
| 11 | `idea fade @ Yesterday high` | `n=46`, `52%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=46`, `52%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:17`: `\| idea fade @ Yesterday high \| 46 \| 52% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:115`: `\| Yesterday high \| 46 \| 52% \| +0.06 \| +0.27 \| -0.23 \|` |
| 12 | `idea fade @ Europe low` | `n=45`, `53%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=45`, `53%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:18`: `\| idea fade @ Europe low \| 45 \| 53% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:112`: `\| Europe low \| 45 \| 53% \| +0.09 \| +0.31 \| -0.27 \|` |
| 13 | `timing` | `n=41`, `56%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `n=41`, `56%`, `NOT-ENOUGH-EVIDENCE (gap < 10 pts)` | `MATCH` | SOURCED `2026-11-11.md:19`: `\| timing \| 41 \| 56% \| first run \| NOT-ENOUGH-EVIDENCE (gap < 10 pts) \|`<br>SOURCED `tables.md:8`: `\| timing \| 41 \| 56% \| +0.03 \| +0.24 \| -0.29 \|` |
| 14 | `idea fade @ Europe high` | `n=30`, `60%`, `test: keep and weight the flag (n 30, 60%)` | `n=30`, `60%`, `test: keep and weight the flag (n 30, 60%)` | `MATCH` | SOURCED `2026-11-11.md:20`: `\| idea fade @ Europe high \| 30 \| 60% \| first run \| test: keep and weight the flag (n 30, 60%) \|`<br>SOURCED `tables.md:111`: `\| Europe high \| 30 \| 60% \| -0.06 \| +0.29 \| -0.47 \|` |
| 15 | `idea fade @ Last week low` | `n=18`, `72%`, `NOT-ENOUGH-EVIDENCE (n < 30)` | `n=18`, `72%`, `NOT-ENOUGH-EVIDENCE (n < 30)` | `MATCH` | SOURCED `2026-11-11.md:21`: `\| idea fade @ Last week low \| 18 \| 72% \| first run \| NOT-ENOUGH-EVIDENCE (n < 30) \|`<br>SOURCED `tables.md:114`: `\| Last week low \| 18 \| 72% \| +0.10 \| +0.60 \| -0.42 \|` |
| 16 | `idea fade @ 2-day-ago high` | `n=16`, `62%`, `NOT-ENOUGH-EVIDENCE (n < 30)` | `n=16`, `62%`, `NOT-ENOUGH-EVIDENCE (n < 30)` | `MATCH` | SOURCED `2026-11-11.md:22`: `\| idea fade @ 2-day-ago high \| 16 \| 62% \| first run \| NOT-ENOUGH-EVIDENCE (n < 30) \|`<br>SOURCED `tables.md:106`: `\| 2-day-ago high \| 16 \| 62% \| -0.06 \| +0.34 \| -0.40 \|` |
| 17 | `idea fade @ Last week high` | `n=2`, `50%`, `NOT-ENOUGH-EVIDENCE (n < 30)` | `n=2`, `50%`, `NOT-ENOUGH-EVIDENCE (n < 30)` | `MATCH` | SOURCED `2026-11-11.md:23`: `\| idea fade @ Last week high \| 2 \| 50% \| first run \| NOT-ENOUGH-EVIDENCE (n < 30) \|`<br>SOURCED `tables.md:113`: `\| Last week high \| 2 \| 50% \| -0.04 \| +0.09 \| -0.21 \|` |

---

## 3. Discrepancies & Flagged Deviations

- Total rows flagged with discrepancies: **0**.
- Every single row in `2026-11-11.md` matches `tables.md` source counts, percentages, and `live_aid_learn.py` verdict rules.
