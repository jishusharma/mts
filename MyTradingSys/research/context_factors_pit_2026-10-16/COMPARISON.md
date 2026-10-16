# COMPARISON: two independent runs of the same prompt (2026-10-16)

The prompt "point-in-time CONTEXT FACTORS for backtesting" ran twice on 2026-10-16: once on Opus 5.5 (JIS-NUC, folder
`research/context_factors_2026-10-16/`, shipped 00:59Z) and once on Fable 5.1 (this folder, `context_factors_pit_2026-10-16/`,
built in parallel without knowing the first had shipped; see REPORT.md "Folder name"). Neither read a VALIDATION or HOLDOUT bar.
This file compares them (counts and definitions only; the only outcome number in it is the Opus card's published verdict), says
what the comparison changes, and traces where each study's results went downstream. Written by the Fable session; the Opus folder
is not edited.

## 1. Is such a comparison worth having?

Yes, and it is the cheapest replication the project can get. Both sessions got the same words from the same traders and the same
rules, and built the factors independently. Where the two agree, a conclusion does not hang on one session's OURS choices. Where
they disagree, the disagreement names the exact parameter the result hinges on, which no single run can see. It also found a
process gap: the second run built a same-named folder for twelve hours while the first was already on trunk, and the trunk had
by then adopted conventions (day units, Holm, a realised-MDE rule) that the second run's PRE_REG contradicts. Section 4 says what
that changes. The cost of the comparison is this file plus one count-only card step; no outcome is read.

## 2. Side by side (definitions, parameters, counts)

| item | Opus (context_factors_2026-10-16) | Fable (context_factors_pit_2026-10-16) |
|---|---|---|
| decision grid | 19,729 1h closes per side (2022-04-01 .. 2024-06-30, 90-day warm-up) | 21,888 1h closes per side (whole DEV from 2022-01-01) |
| bars | 1m archive aggregated to 5m | 1m with the FORMULAS s.8 bucket convention |
| factor columns | 24 in 7 families | 7 families (grid of ~60 columns incl. sub-fields) |
| level sources | 8 layers (prior D/W, session H/L, PD VA, PW VA, Krown zones, VWAPs, round 1,000s, 4h BB mid) | 9 sources (same set plus the weekly ladder of W_LADDER_PCT) |
| "at a level" | nearest same-side level within 1.0 x ATR14(1h) | within K_ZONE 0.5 x ATR14(4h) (alt 1.0) |
| role flip | completed 1h close through the level | last closed 1h close (T1; alt 4h close) |
| share of hours at a level | 90 % | 94.5 % |
| stop ladder | D -> 12h -> 8h; W_max = 1.0 x ATR14(D); floor 0.56 % | D -> 12h -> 8h; W = 2.5 % of price (alt 1.5 %); floor 0.56 % |
| armed / operator condition | close past the prior D open | same words (ladder_cond, T3; alt touch rule) |
| phase A (chosen) | weekly close vs SMA10(W) + slope | daily fractal pivots, HH&HL = markup |
| phase B (variant) | 30 d trend tag + 90 d range position | 30-day return vs 7.5 % with SMA50 split |
| Bollinger veto | 1h walk: 3 closes beyond, bands opening; 63 vetoed per side | 4h walk down, 3+ closes beyond, bandwidth expanding; 426 short episodes |
| engulf | operator rule (close past previous open); classic rule only as variant (tick noise) | operator rule |
| planted leaks | 8 of 8 caught | 7 of 7 caught |
| replay == vectorised | 39,458 rows, 0 mismatches | 128,736 points, 0 mismatching fields |
| what the angles found | 5 spec errors (ladder moved on too-tight stops; today's H/L missing; 1-hour-old VWAP and session range as levels; tick-noise engulf) | 2 engine bugs (two-pass BB variance; ATR sliding window), tie rounding, RT-1 day-close grid, and an origin bug in the pandas checker |
| ledger | 4 h same-side cooldown: 2,817 long / 2,781 short events on 769 / 754 days | first touch + valid ladder stop: 1,636 / 1,651 episodes on 694 / 700 days |
| test design | one composite cell C (confluence >= 2, armed ladder, no walk veto, weekly phase) vs context-matched controls | 14 cells: 7 per-factor filter contrasts x 2 sides vs context_null matched controls |
| trade | entry at T + 60 s, ladder stop, 2 R target, 24 h time stop, 7 bp per side + funding | entry open[t+1], ladder stop, 1.5 R target, both-touched = stop, 24 h max hold, 0.14 % |
| power unit, sd, plausible, cost | distinct UTC days, 1.5 R, 0.20 R, 0.081 R -> 1246 days; 0 of 86 buckets | episodes, 1.28 R, 0.15 R, 0 (cost-free contrast) -> 572 episodes; 9 of 14 cells |
| Holm m | 37 | 36 |
| decisions logged | D1 run the card, D2 walk veto, D3 extend DEV, D4 days + Holm, D5 no invalidation flag | W 2.5 %, target 1.5 R, last_closed, K_ZONE 0.5, plausible 0.15 R |

## 3. What is robust and what is definition-dependent

Robust (both engines, independent definitions):
- The context can be rebuilt point in time; both replay builds match their vectorised builds exactly, and every planted leak is caught.
- "At a level" alone selects nothing: 90 % (Opus) and 94.5 % (Fable) of hours have a same-side level within the zone. Only confluence, the stop rule or a trigger narrows it.
- No single factor is testable on DEV once the unit is the distinct UTC day (section 4): the Fable cells have at most 700 days per side.
- Directional 4h/D candle patterns are rare at a level (Opus 522 D-engulf events; Fable 261 / 287 4h episodes).
- The eur_low_us_sweep HOLDOUT read is real (both sessions checked RESULT.md independently).

Definition-dependent (the parameter the result hinges on is named):
- The band-walk veto fires on 2 % of Opus events (1h walk) and 26 % of Fable short episodes (4h walk with expanding bandwidth). Any band verdict is a verdict on the walk definition, not on "the band".
- Phase: weekly SMA10 slope (Opus) vs daily fractal pivots (Fable) are different objects; Opus found its own two definitions agree on 45.8 % of events. A phase factor needs one chosen definition frozen across studies before any read.
- The ladder: W_max = 1.0 x ATR14(D) (Opus) vs 2.5 % of price (Fable) put different shares of events on the 12h/8h rungs (Opus: D in 86-87 %; Fable: D in 59 %, from T4 counts 12,558 of 21,888 grid rows). The Codex fix-1 report already shows the stop width changes the R unit by about 25 %.
- The power verdict: "9 of 14 cells" (Fable) and "0 of 86 buckets" (Opus) come from three OURS choices, not from the data: the unit (episode vs day), the per-trade sd (1.28 vs 1.5 R) and the plausible effect (0.15 vs 0.20 R). Section 4 settles it.

## 4. What the comparison changes for this study

The trunk has adopted, through the Opus chain, a power convention this study's PRE_REG.md contradicts: units = distinct UTC days
with Holm (Opus D4, enforced by `context_factors_2026-10-16/AUDIT_BEFORE_RUN.md` item 2 and `pit_levels_2026-10-16/AUDIT_BEFORE_RUN.md`),
and a realised-MDE verdict rule (FAIL only when the realised MDE plus cost is at or under the plausible effect; Codex card
gptb-context-v2-fix2-mde-rule, done). Running PRE_REG.md as written would put a second convention into VERDICTS.csv. So:

1. PRE_REG.md stays frozen and unread; `PRE_REG_V2.md` (this folder) is its successor with day units, the recounted Holm m and the
   realised-MDE rule. Nothing else changes (engine sha, contrasts, outcome function, episode ledger, DEV only).
2. Day counts of the 14 cells (count-only, from the committed grid rule):

| cell | long n | long days | own 572 / trunk free 441 / trunk net 1246 | short n | short days | own / free / net |
|---|---|---|---|---|---|---|
| F1 at a side-aware level (every episode) | 1636 | 694 | yes / yes / no | 1651 | 700 | yes / yes / no |
| F2 confluence n_layers >= 2 | 1305 | 654 | yes / yes / no | 1307 | 657 | yes / yes / no |
| F3 operator condition (ladder_cond) | 965 | 448 | no / yes / no | 965 | 452 | no / yes / no |
| F4 4h pattern in the trade direction | 261 | 161 | no / no / no | 287 | 177 | no / no / no |
| F5 band state (long re-entry / short walk veto) | 36 | 27 | no / no / no | 40 | 27 | no / no / no |
| F6 phase A with the trade | 578 | 247 | no / no / no | 382 | 162 | no / no / no |
| F7 HTF alignment | 885 | 376 | no / no / no | 667 | 299 | no / no / no |

   "own" = this study's sd bound 1.28 R and 0.15 R, cost 0; "trunk free" = sd 1.5 R, 0.20 R, cost 0 (a filter contrast pays no
   extra fee); "trunk net" = Opus's 0.081 R cost. Four cells (F1 and F2, both sides) are powered under both the own and the
   trunk-free convention; none is powered under the net convention. So the honest version of "9 of 14" is **4 of 14 by design**,
   and every cell is read under the realised-MDE rule so that an unpowered cell can be INCONCLUSIVE but never FAIL.
3. Card `context-factors-one-run` is rescoped to PRE_REG_V2.md and gets a count-only first step that nobody has yet: a
   cross-engine agreement table between the Opus frames (`run_dev.py vec`, read-only) and this grid at shared decision hours
   (at a level, confluence >= 2, armed ladder, stop rung, phase, veto, 4h pattern direction), with Cohen's kappa per factor. A
   factor with kappa < 0.4 is labelled definition-fragile in RESULT.md whatever its verdict word.
4. Card `context-factors-pit-audit` (new, S) runs the 6-item AUDIT_BEFORE_RUN on PRE_REG_V2.md before the outcome read, the way
   the Opus and pit_levels PRE_REGs were audited; the one-run card depends on it.
5. The DEV_EXT segment (Opus D3, applied: 2020-2021 1m, 731 days) is not used by this study: its loader refuses bars outside DEV,
   and `COUNTS_DEV_EXT.md` shows no single factor reaches the trunk-net threshold even with it. A later successor may add it.

## 5. Where the Opus results went downstream (trace, trunk as of 2026-10-16 ~17:00 UTC)

| step | artefact | state |
|---|---|---|
| ship | 0cf5a41f "24 factors PIT-proven, 8 planted leaks caught" | on fast-track |
| card | `tasks/context-composite-dev-read.json` (SONNET) | done 05:13Z: INCONCLUSIVE (241 of 1,010 events matched on 164 days, gate 387; E = -0.023 R, t = -0.32; mean net_R -0.137 R) |
| verdict ledger | `research/VERDICTS.csv` row 24 | INCONCLUSIVE, kill scope none, one_run yes, commit 3e961c2f |
| registry audit | `layer_lab/reports/2026-10-16_gpt-verdict-registry-audit.md` row 21 | verdict supported; note that the registry's numeric fields are in other units than the RESULT table |
| morning report | `research/autopilot_2026-10-16/MORNING_REPORT.md` | "No edge found, nothing promoted"; commit table rows 3e961c2f .. 759632a0 |
| hand-over | `system/NEXT_SESSION.md` AUTOPILOT-3 line; queue Q86 | successor card queued |
| independent audit | `context_factors_2026-10-16/AUDIT_BEFORE_RUN.md` | FIX-FIRST 2 of 6 on PRE_REG_V2 (stop comparability; plausible set after counts, realised-MDE rule) |
| successor PRE_REG | `PRE_REG_V2.md` (Q77, Sonnet) + card `context-composite-v2-dev-read` | READY in the queue, but the audit says FIX-FIRST: the two fixes exist only as `PRE_REG_V3_ADDENDUM_DRAFT.md` in `layer_lab/context_fix1_stop_strata/` and `context_fix2_mde_rule/` (Codex cards done); no PRE_REG_V3 is assembled in the folder |
| D3 | `OPERATOR_DECISIONS.md` D3-dev-ext; `COUNTS_DEV_EXT.md`; `dev_ext.py` | applied: DEV_EXT 2020-2021 fetched and checksummed; still no factor powered at m = 37 |
| D1, D2, D4, D5 | REPORT.md s.4 only | not in OPERATOR_DECISIONS.md; D4 (days + Holm) is applied de facto by both audits without a logged decision |
| Research Map | `system/artifacts/research_map.html` DATA item `ctxcomp` + PIT item | v8 published 2026-10-16 |

Gaps in that chain, for whoever takes Q86: (a) assemble PRE_REG_V3 from the two addendum drafts before running, or the V2 card
runs against an audit that said FIX-FIRST; (b) log D4 as a decision so the convention is a record, not a habit; (c) the Opus
RESULT's funding path note (Research Map `ctxcomp.data`) says the PRE_REG path did not exist on the NUC, a reproducibility nit.

## 6. Where this study stands in the same channels after this commit

| channel | state |
|---|---|
| folder on trunk | shipped (ship 2 of this session) |
| card queue | `context-factors-pit-audit` (S, new) -> `context-factors-one-run` (M, rescoped to PRE_REG_V2.md, depends on the audit) |
| VERDICTS.csv | no row: nothing read yet (correct) |
| NEXT_SESSION.md queue | Q87 (audit) and Q88 (one run) appended after Q86 |
| OPERATOR_DECISIONS.md | D6-two-context-engines: the five defaults of REPORT.md s."Operator decisions" plus the adoption of day units, logged with a JSON block |
| Research Map | DATA `planned` entry "Context factors, second engine" in the repo copy; republish is the next super session's step (SUPER_SESSION.md) |
| audit | pending (Q87) |
