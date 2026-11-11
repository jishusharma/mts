MATCH=6 DIFF=0 NOT_IN_DATA=0

# Gemini Blind Read: live_aid_learn.py (d15ca1597)

## Clause Verification Table

| # | Clause Requirement | Status | Docstring Quote (`scripts/dev/live_aid_learn.py`) | Implementation Quote (`scripts/dev/live_aid_learn.py`) | Test / Artifact Quote |
|---|--------------------|--------|---------------------------------------------------|---------------------------------------------------------|-----------------------|
| 1 | hit = r1h > 0 | MATCH | L8: `"Hit = r1h > 0 (as analyze.py)."` | L45: `100.0 * sum(1 for e in v if float(e["r1h"]) > 0) / len(v)` | `scripts/dev/test_live_aid_learn.py:11`: `"r1h": 0.1 if i < wins else -0.1`; `MyTradingSys/research/live_aid_learning/2026-11-11.md:3`: `"Hit = price moved the flag's way after 1h (descriptive, no fees)."` |
| 2 | r1h None/empty skipped | MATCH | L6: `"<flag-log CSV: kind,side,state,at,r1h>"` | L35: `ev = [e for e in events if e.get("r1h") not in (None, "")]` | `scripts/dev/test_live_aid_learn.py:40-42`: `def test_none_r1h_skipped(): ... e = ev(...) + [{"kind": "idea", ... "r1h": None}]` |
| 3 | test only if n >= 30 and \|hit-50\| >= 10 | MATCH | L8: `"Rule (OURS, not sourced): 'test' only if n >= 30 and |hit - 50| >= 10 points."` | L20: `MIN_N, MIN_GAP = 30, 10.0`; L24-25: `if n >= MIN_N and abs(hit - 50) >= MIN_GAP: return "test: %s the flag (n %d, %.0f%%)" % ("drop or invert" if hit < 50 else "keep and weight", n, hit)` | `scripts/dev/test_live_aid_learn.py:23-25`: `def test_large_gap_enough_n_is_implement(): ... assert r["verdict"].startswith("test")`; `MyTradingSys/research/live_aid_learning/2026-11-11.md:15,20`: rows `n=50, 40%` and `n=30, 60%` get `test:` |
| 4 | else NOT-ENOUGH-EVIDENCE + reason | MATCH | L8: `"Rule (OURS, not sourced): 'test' only if n >= 30 and |hit - 50| >= 10 points."` | L26-27: `why = "n < %d" % MIN_N if n < MIN_N else "gap < %d pts" % MIN_GAP; return "NOT-ENOUGH-EVIDENCE (%s)" % why` | `scripts/dev/test_live_aid_learn.py:28-37`: tests verify small n gives `"n < 30"` and small gap gives `"gap < 10 pts"`; `MyTradingSys/research/live_aid_learning/2026-11-11.md:7-14,16-19,21-23`: all non-test rows show `NOT-ENOUGH-EVIDENCE (<reason>)` |
| 5 | input --log, else events.json, else tables.md | MATCH | L6-7: `"Input, first found: --log <flag-log CSV: kind,side,state,at,r1h>; review events.json (replay.js output); else the committed aggregate tables.md of research/live_aid_review_2026-11-11"` | L104-110: `if a.log: ... elif ev.exists(): ... else: rows, src = load_tables_md(REVIEW / "tables.md")` | `scripts/dev/test_live_aid_learn.py:50-55`: `def test_tables_md_fallback_parses_committed_review(): rows = la.load_tables_md(la.REVIEW / "tables.md")`; `MyTradingSys/research/live_aid_learning/2026-11-11.md:3`: `"Source: replay aggregates (live_aid_review_2026-11-11/tables.md)."` |
| 6 | writes live_aid_learning/<date>.md; check 2026-11-11.md rows | MATCH | L3-4: `"writes MyTradingSys/research/live_aid_learning/<date>.md."` | L19: `OUT = ROOT / "MyTradingSys" / "research" / "live_aid_learning"`; L115: `(out / (a.date + ".md")).write_text(...)` | `MyTradingSys/research/live_aid_learning/2026-11-11.md:1-35`: exactly 17 flag group rows (matching `scripts/dev/live_aid_learn.py:116`: `rows=17`), 2 implement items (n>=30 and \|hit-50\|>=10), and top 6 operator items correctly ranked by \|hit-50\| |

## Summary of 2026-11-11.md Row Audit

- Total rows evaluated: 17 SOURCED (`MyTradingSys/research/live_aid_learning/2026-11-11.md:7-23`).
- Implement list: 2 rows with `test:` SOURCED (`MyTradingSys/research/live_aid_learning/2026-11-11.md:25-27`):
  - `idea fade @ Yesterday low` (n=50, 40% -> drop or invert)
  - `idea fade @ Europe high` (n=30, 60% -> keep and weight)
- Not enough evidence: 15 rows SOURCED (`MyTradingSys/research/live_aid_learning/2026-11-11.md:7-14,16-19,21-23`):
  - 12 rows failed due to `gap < 10 pts` (n >= 30, but 40% <= hit <= 60%)
  - 3 rows failed due to `n < 30` (`Last week low` n=18, `2-day-ago high` n=16, `Last week high` n=2)
- Operator list: Exactly 6 rows SOURCED (`MyTradingSys/research/live_aid_learning/2026-11-11.md:29-35`), sorted by descending `|hit - 50|`.
