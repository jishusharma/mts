# T04 clean-room twin: mal_bb_mid_engulf arm A1 and weekly-low round sweep arm RL (2026-10-24)

**Result:** both shipped studies reproduce from their PRE_REG alone. After the twin's own bugs are fixed, the twin finds the same 1,179 A1 events (every return within 5e-6 pp) and the same 685 RL events and returns. No shipped bug changes a verdict; the one residual is a float tie-break on one control event (S3). The recurring ambiguity is the cooldown boundary, which moved 21 of 1,179 A1 events until the PRE_REG's own printed counts settled it. All four verdicts are FAIL in every event set. No S1 or S2 finding, so no S1/S2 card.

Card `dsa-audit-04-clean-room-twin`. Scope: DEV only (bars before 2024-07-01), BTCUSDT 1m from F:/MTS/data/tom_raw/klines (read only, own loader). The optional third twin (opr_preopen_tops H2) was dropped as instructed.
Method discipline: twins were written from the two PRE_REG.md files plus FORMULAS.md s.1 (RSI seed, cited by the PRE_REG) and brief section 1d. study.py, test_study.py and common.py were opened only after both twins had run (step 4). I read the ledger.csv header before the diff. The PRE_REG's printed counts (A1 1,179, control 2,486, A2 807; pooled 1,060, round 1,006, weekly 103) are spec text; I used them once, to settle the cooldown boundary (ambiguity 1), and say so there. The brief's table also prints RL n 685; I did not tune to it (the twin's first run already gave 685).

Files: `scripts/T04/twin_common.py` (loader, indicators, stats), `twin_mal_bb.py`, `twin_wlow.py`, `t04_diff.py` (diff, classes, verdicts), `test_twin_diff.py`, `out/` (twin event lists, three diff tables, `t04_results.json`). Re-run: `python scripts/T04/t04_diff.py` (about 4 min, needs F:/MTS/data and pandas).

## 1. Ambiguity log (each DECISION is OURS)

Cooldown, funding and fill rules are the same in both studies.

| # | Point where the spec allows more than one reading | Reading chosen (DECISION, OURS) | Effect vs shipped |
|---|---|---|---|
| 1 | "60-minute cooldown": is an event exactly 60 minutes after the kept one allowed (>= 60) or not (> 60)? | First draft: allowed (>= 60). Corrected to > 60 because only that reproduces the PRE_REG counts 1,179 / 2,486 / 807 and 1,060 / 1,006 | 21 A1 events, 3 pooled WL events differ with the >= reading. Shipped uses `t[i] - last <= cd` skip, i.e. > 60. **Spec ambiguity**, settled by the printed counts, not by the wording |
| 2 | MAL s.3 "SHORT at the engulf-bar close" vs s.1 "fill at the open of the second following 1m bar (d = 1)" | Decision at the 5m close, fill at the open of the 1m bar one minute after that close (= second following 1m bar if the signal bar's last 1m bar is the first "bar") | Every one of 1,179 returns matches shipped to 5e-6 pp, so the reading is the shipped one. Wording is still loose |
| 3 | Exit: "h = 60 minutes after the entry open" gives a time, not a price | Open of the 1m bar at entry + 60 min | matches |
| 4 | Funding "per settlement crossed": boundary at entry or exit | Settlement s counts if entry < s <= exit | matches |
| 5 | MAL "t_DIFF" and DIFF standard error: the PRE_REG points to a template whose SE is an OLS day-clustered sandwich | Twin used sqrt(SE_arm^2 + SE_ctrl^2) (first reading) | t_DIFF 0.44 (twin) vs 0.61 (shipped) on identical events; both far below 2. **Spec ambiguity** (S3) |
| 6 | "arm MDD (sum of net % of one clip) <= buy-and-hold DEV MDD": sums of trade % vs price drawdown % | Cumulative sum of net %, peak to trough, vs price drawdown in percent of peak | Same as shipped (A1 152 vs 67.8). Not like-for-like (brief lead L7), not tested here |
| 7 | HTF "last closed" bar when the 5m close coincides with a 1h/4h close | Closed if its end <= the 5m bar end | matches (0 bar-level HTF disagreements) |
| 8 | RSI14 seed | FORMULAS.md s.1 (SMA seed over first 14 deltas) | matches |
| 9 | "falling": net delta over "the last 6 bars" and BB mid "lower than 10 bars ago" | Six 5m bars including the signal bar; strict < | one float-tie bar differs, see section 4 |
| 10 | Engulf "close below the previous green bar's open", green/red with doji | Strict <; green close > open, red close < open | matches |
| 11 | A1 control cooldown: "same cooldown" shared with A1 or separate | Separate ledger per set ("within each set") | control n 2,486 reproduced |
| 12 | Weekly level: "weeks before the first two full weeks have none" | Level from the second full week (week of 2022-01-10 uses 2022-01-03..09) | matches |
| 13 | Round level "highest multiple of 1000 not above the lowest close of the previous 60 minutes" | The 60 closes before the break bar, current bar excluded | matches |
| 14 | First break "a 1m low at least p below the level while ALL of the previous 60 closes were at or above it" | low <= level x (1 - p); previous closes >= level | matches |
| 15 | Pooled ledger: "union of both families with a global 60-minute cooldown, a weekly-low event wins a tie" | Per-family cooldown first, then union sorted by time with weekly first, then the global cooldown | matches (after ambiguity 1) |
| 16 | RL "a close above the level at index r <= 5" and fill rule for a 1m decision bar | Strict >, first such r (bar 0 counts); fill at the open two 1m bars after the decision bar; control decides at index 5, fill at index 7 | matches |
| 17 | Events whose exit lies beyond the DEV tape | Dropped | matches (shipped drops 0) |
| 18 | Float ties in indicator comparisons (SMA values equal in exact arithmetic) | Round mid to 6 decimals before comparing (twin v3) | see section 4 |

## 2. Diff by class

Keys: A1 by engulf-bar open time; WL by first-break bar open time. "Return differs" means |G_twin - G_shipped| > 0.001 pp. The shipped ledger.csv has no entry or exit price and, for WL, no return column: A1 returns use `G_short_h60`; WL returns were recomputed by calling the shipped study.py functions (`net_cells`) on its events.

### 2a. mal_bb_mid_engulf, arm A1 (shipped ledger 1,179 rows)

Counts by twin version (matched, return_differs, twin_only, shipped_only):

- v0 (twin as first written): {'matched': 1173, 'return_differs': 0, 'twin_only': 16, 'shipped_only': 6}
- v1 (+ exact SMA): {'matched': 1174, 'return_differs': 0, 'twin_only': 16, 'shipped_only': 5}
- v2 (+ cooldown > 60 min): {'matched': 1179, 'return_differs': 0, 'twin_only': 0, 'shipped_only': 0}
- v3 (+ tie rounding, the corrected twin): {'matched': 1179, 'return_differs': 0, 'twin_only': 0, 'shipped_only': 0}

Pre-cooldown state counts, twin vs PRE_REG s.5: falling 69,176 (v3 69,173) vs 69,174; falling + touch 26,367 vs 26,367; + HTF 10,673 vs 10,673.

The 22 v0 differences (16 twin-only, 6 shipped-only), classified: **21 spec ambiguity** (cooldown boundary), **1 twin bug** (T1, a 1e-9 drift of the running-sum SMA flips one `mid < mid[-10]` comparison; gone after the exact-SMA fix), **0 shipped bug**, **0 residual**. First 10 twin-only:

| UTC key | class | twin G % | shipped G % |
|---|---|---|---|
| 2022-01-05 23:50 | spec_ambiguity | -0.28734 | - |
| 2022-04-12 00:05 | spec_ambiguity | -0.41838 | - |
| 2022-05-03 14:35 | spec_ambiguity | -0.10977 | - |
| 2022-07-26 07:30 | spec_ambiguity | 0.09099 | - |
| 2022-08-01 20:00 | spec_ambiguity | -0.45459 | - |
| 2022-08-04 04:40 | spec_ambiguity | 0.10902 | - |
| 2022-08-28 11:05 | spec_ambiguity | -0.04896 | - |
| 2022-09-18 18:55 | spec_ambiguity | -0.54296 | - |
| 2022-10-19 13:00 | spec_ambiguity | -0.05642 | - |
| 2023-03-07 12:15 | spec_ambiguity | -0.12071 | - |

All 6 shipped-only:

| UTC key | class | twin G % | shipped G % |
|---|---|---|---|
| 2022-07-26 07:55 | spec_ambiguity | - | 0.00332 |
| 2023-03-28 05:40 | spec_ambiguity | - | -0.40865 |
| 2023-07-15 16:30 | spec_ambiguity | - | -0.15475 |
| 2023-09-23 11:45 | twin_bug | - | -0.00527 |
| 2024-05-29 17:15 | spec_ambiguity | - | -0.04311 |
| 2024-06-28 17:45 | spec_ambiguity | - | -0.05380 |

Return differs: 0 events (largest |dG| 5.0e-06 pp, the 5-decimal rounding of the ledger). Full table: `scripts/T04/out/diff_mal_bb_A1.csv`.

### 2b. opr_weekly_low_round_sweep, arm RL (shipped ledger 1,060 rows)

Pooled break ledger, v0 (cooldown >= 60): {'matched': 1059, 'return_differs': 0, 'twin_only': 2, 'shipped_only': 1}. With cooldown > 60 (v2): {'matched': 1060, 'return_differs': 0, 'twin_only': 0, 'shipped_only': 0}. All 3 differences are **spec ambiguity** (cooldown boundary, ambiguity 1); levels and families agree on all 1,060 rows.

| UTC key | class | twin G % | shipped G % |
|---|---|---|---|
| 2023-03-10 04:05 | spec_ambiguity | - | - |
| 2024-01-03 12:08 | spec_ambiguity | - | - |
| 2024-01-03 12:09 | spec_ambiguity | - | - |

RL arm (685 shipped events, control 375), with returns, v0: {'matched': 684, 'return_differs': 0, 'twin_only': 1, 'shipped_only': 1}; v2: {'matched': 685, 'return_differs': 0, 'twin_only': 0, 'shipped_only': 0}. The 2 v0 differences are the same two breaks:

| UTC key | class | twin G % | shipped G % |
|---|---|---|---|
| 2023-03-10 04:05 | spec_ambiguity | -0.64083 | - |
| 2024-01-03 12:09 | spec_ambiguity | - | 2.30610 |

Return differs: 0. Full tables: `diff_wlow_pooled.csv`, `diff_wlow_RL.csv`.

## 3. Every difference, classified

| Class | A1 | RL pooled | RL arm |
|---|---|---|---|
| spec ambiguity | 21 | 3 | 2 |
| twin bug | 1 | 0 | 0 |
| shipped bug | 0 | 0 | 0 |
| unexplained | 0 | 0 | 0 |

Twin bugs found and fixed: **T1** running-sum SMA drift (v0 to v1); **T2** none left after tie rounding for the twin's own side. The shipped-side float issue is in section 4.

## 4. Shipped-side findings

- **F1 (S3) float tie on a flat BB mid.** The shipped `falling()` compares pandas rolling means, `mid < prior`. At 5m bar index 173060 the two means are equal in exact arithmetic (checked with Fractions) but shipped has 26044.69 < 26044.690000000002 and marks the bar falling; a twin comparing exact ties (v3) does not. Bar-level state: 1 disagreement in 69,174 falling bars; zero effect on the 1,179 A1 events; it is consistent with the A1 control being 2,486 (shipped) vs 2,485 (v3). State comparison: {"falling": {"twin": 69173, "shipped": 69174, "disagree_after_warmup": 1, "bars": [173060]}, "touch": {"twin": 191777, "shipped": 191788, "disagree_after_warmup": 0, "bars": []}, "htf": {"twin": 82647, "shipped": 82647, "disagree_after_warmup": 0, "bars": []}, "engulf_a": {"twin": 33150, "shipped": 33152, "disagree_after_warmup": 0, "bars": []}}. Class: shipped bug, immaterial.
- **F2 (S3) the ledgers cannot be audited alone.** Neither ledger.csv carries entry price, exit price or time; WL carries no return at all. A diff needs the study code. Suggest `entry_ms, entry_px, exit_ms, exit_px, G` columns in the template.
- **F3 (S3) t_DIFF method not in the PRE_REG** (ambiguity 5): same events give 0.44 or 0.61.
- No S1 or S2 finding: no event, return, level or cooldown error that changes a count beyond the boundary, and no verdict changes.

## 5. Verdict on shipped, twin and corrected events

Columns: mean G (after funding, %), t_cost = (mean - 0.14) / day-clustered SE, DIFF vs control, t_DIFF, verdict.

A1:

| Event set | n | mean G | t_cost | DIFF | t_DIFF | Verdict |
|---|---|---|---|---|---|---|
| shipped events (study.py) || n 1179 | 0.0124 | -6.02 | 0.0111 | 0.61 | FAIL |
| twin v0, as first written || n 1189 | 0.0105 | -6.16 | 0.0087 | 0.35 | FAIL |
| twin v1, + exact SMA || n 1190 | 0.0105 | -6.17 | 0.0087 | 0.35 | FAIL |
| twin v2, + cooldown > 60 min || n 1179 | 0.0124 | -6.02 | 0.0111 | 0.44 | FAIL |
| corrected twin v3, + tie rounding || n 1179 | 0.0124 | -6.02 | 0.0110 | 0.44 | FAIL |

RL:

| Event set | n | mean G | t_cost | DIFF | t_DIFF | Verdict |
|---|---|---|---|---|---|---|
| shipped events (study.py) || n 685 | 0.0317 | -3.23 | 0.0321 | 0.48 | FAIL |
| twin v0, as first written || n 685 | 0.0274 | -3.38 | 0.0240 | 0.39 | FAIL |
| corrected twin v2, cooldown > 60 min || n 685 | 0.0317 | -3.23 | 0.0321 | 0.51 | FAIL |

No verdict changes: every set is FAIL on mean G < 0.14 % and t_cost far below 2, before DIFF or drawdown are read. The shipped RL mean is +0.0317 % (twin v0 +0.0274 % from one swapped event; corrected twin identical to shipped to 1e-14). The shipped numbers stand.

## 6. S3 findings for PRE_REG_TEMPLATE.md

1. State the cooldown boundary as an inequality ("the next event must be more than 60 minutes after the last kept event") and print which scale (minutes of the decision bar close).
2. State the fill as one rule in one place (decision bar, delay in 1m bars, price column), not two sentences that read differently.
3. Give the exit as a time and a price column ("open of the bar at entry + h").
4. Give the DIFF standard error formula, not "template" (0.44 vs 0.61).
5. Say how exact float ties are resolved, or require comparisons on prices rounded to the tick.
6. State the funding crossing as an interval (entry, exit].
7. Ledgers should carry entry/exit time, price and return so a second implementation can diff without reading code.
8. Print state-bar counts and the final ledger counts in the PRE_REG, as these two did: they were the only way the cooldown ambiguity could be settled, and they worked.

## 7. Limits

DEV only; no VALIDATION or HOLDOUT bar was read. The twin shares the data files with the shipped study (the same CSVs), so it does not test the data (T01 does). One reader of the spec (me) made the twin; a second reader could resolve other ambiguities differently. Only arms A1 and RL were twinned; A2, AS and all secondary cells are untested.
