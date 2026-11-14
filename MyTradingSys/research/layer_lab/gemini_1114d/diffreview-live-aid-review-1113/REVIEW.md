# Diff Review: `live_aid_review_2026-11-13` and `live_aid_liq_meaning_2026-11-13` (last 24 h)

Scope: `git log --since="24 hours ago" origin/fast-track --name-status -- MyTradingSys/research/live_aid_review_2026-11-13 MyTradingSys/research/live_aid_liq_meaning_2026-11-13` (3 commits found; counts SOURCED from `git log` / `git show --stat`).

## Commits Reviewed

| sha | date (IST) | target files touched | Result: line match |
|---|---|---|---|
| `0be17fc4ae095d980c128c57afba17f063d0251b` | 2026-11-13 19:22:36 | `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md`, `liq_meaning.py` (+ 15 other files) | YES (matches Result: items) |
| `b5dda085e75755197a8b7d51b51ac33a95880fa8` | 2026-11-13 17:58:07 | `MyTradingSys/research/live_aid_review_2026-11-13/fixture_home_chart.html`, `fixture_home_chart.png`, `render_fixture.js` (+ 3 other files) | YES (matches Result: items) |
| `98ca71600530142484f1062be3b0cd521e0b8c9a` | 2026-11-13 17:43:21 | `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md` (+ 4 other files) | YES (matches Result: items) |

## Findings

| sha | file:line | severity | category | evidence |
|---|---|---|---|---|
| `0be17fc4ae095d980c128c57afba17f063d0251b` | MyTradingSys/research/live_aid_liq_meaning_2026-11-13/RESULT.md:18 | MED | missing test | `liq_meaning.py` implements `load_events`, `bursts`, `rows_from`, `write_js`, and `main`, but `"Logic was checked on a synthetic series only (not a result)."` — no Python unit test file exercises `liq_meaning.py` (`test_liq_rates.py` tests only `liq_rates.js`). |
| `0be17fc4ae095d980c128c57afba17f063d0251b` | MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:1 | LOW | commit header count | Commit subject states `ship: 16 file(s)`, whereas `git show --stat 0be17fc4ae095d980c128c57afba17f063d0251b` reports 17 files changed. |
| `b5dda085e75755197a8b7d51b51ac33a95880fa8` | MyTradingSys/research/live_aid_review_2026-11-13/render_fixture.js:10 | LOW | dead code | Unused variable `"const body = H.render ? '' : '';"` left in the fixture renderer. |
| `98ca71600530142484f1062be3b0cd521e0b8c9a` | MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:82 | LOW | unsourced numbers | `"replay 11-10: event sweep to 73,525 then squeeze to 74,844; page flagged both sides"` cites no file/line, and neither number appears in `MyTradingSys/research/live_aid_learning/`. |
| `98ca71600530142484f1062be3b0cd521e0b8c9a` | MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:1 | LOW | commit header count | Commit subject states `ship: 4 file(s)`, whereas `git show --stat 98ca71600530142484f1062be3b0cd521e0b8c9a` reports 5 files changed. |

## Per-Commit Notes

- **`0be17fc4ae095d980c128c57afba17f063d0251b`**: Parameters in `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py:20-24` (`MIN_SPAN_H`, `BUCKETS`, `DEDUP_MS`, `HORIZ`) and `MyTradingSys/tools/live_aid/home.js:85` (`VOL_AVG`, `VOL_HI`, `VOL_LO`) are labeled `OURS`; Krown MAs in `MyTradingSys/tools/live_aid/home.js:79` are labeled `SOURCED: Krown KR-M01 (MA_CONCEPTS.md)`.
- **`b5dda085e75755197a8b7d51b51ac33a95880fa8`**: Session high/low lines in `MyTradingSys/tools/live_aid/home.js:139` are labeled `(OURS)`, and `MyTradingSys/tools/live_aid/test_live_aid_guidance.py:139-160` adds the 2 new tests matching the `Result:` line.
- **`98ca71600530142484f1062be3b0cd521e0b8c9a`**: Height shares in `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:4-5` are labeled as `ESTIMATES from the layout code`, `0 of 40` in `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:80` matches `MyTradingSys/research/STATUS.md:7`, `setup 51% n 1342, idea 47% n 763` in `MyTradingSys/research/live_aid_review_2026-11-13/REVIEW.md:79` matches `MyTradingSys/research/live_aid_learning/2026-11-13.md:7-8`, and all 3 raw task JSONs were created.
