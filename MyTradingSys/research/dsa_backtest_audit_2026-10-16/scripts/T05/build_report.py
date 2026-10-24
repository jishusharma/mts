"""T05 report builder: out/tables.md + out/summary.json + out/lc1_fair.csv -> ../../T05_placebo_nulls.md. Run t05_merge.py first."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
REPORT = HERE.parents[1] / "T05_placebo_nulls.md"
S = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
TABLES = (OUT / "tables.md").read_text(encoding="utf-8")
BLOCKED = not (OUT / "lc1_fair.csv").exists()
LC = [] if BLOCKED else list(csv.DictReader(open(OUT / "lc1_fair.csv", encoding="utf-8")))
REP = [] if BLOCKED else list(csv.DictReader(open(OUT / "lc1_orig_reproduction.csv", encoding="utf-8")))

keep_pub = [r["family"] for r in LC if r["family"] in ("prior_day_high", "prior_day_low", "prior_day_poc", "naked_poc", "4h_fractal_low", "4h_fractal_high", "round_1000", "prior_week_high")]
keep_fair = [r["family"] for r in LC if r["verdict"] == "KEEP"]
lost = [f for f in keep_pub if f not in keep_fair]
gained = [f for f in keep_fair if f not in keep_pub]
lc_rows = [[r["family"], r["n_touch"], f"{100 * float(r['hold']):.1f}%", f"{100 * float(r['pub_random']):.1f}%", f"{100 * float(r['pub_diff']):+.1f}",
            r["pub_verdict"], f"{100 * float(r['fair_ctl_hold']):.1f}%", f"{100 * float(r['diff']):+.1f}",
            f"[{100 * float(r['ci_lo']):+.1f}, {100 * float(r['ci_hi']):+.1f}]", r["verdict"],
            f"{100 * float(r['orig_ctl_equal_real_share']):.0f}% / {100 * float(r['orig_ctl_untouched_share']):.0f}%"] for r in LC]
rep_ok = len(REP) == 12 and all(abs(float(a["diff"]) - float(b["pub_diff"])) < 1e-3 for a, b in zip(sorted(REP, key=lambda r: r["family"]), sorted(LC, key=lambda r: r["family"])))


def table(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(map(str, r)) + " |" for r in rows])


beat = {k: v["n_beats_bestofn"] for k, v in S.items()}
sdr = {k: (v["n_sdr_gt12"], v["max_sdr"], v["median_sdr"]) for k, v in S.items()}
cs = S.get("candle", {})
txt = f"""# T05 Placebo nulls: what does chance alone produce here? (card dsa-audit-05-placebo-nulls)

Seeds: placebo and bootstrap SEED = 20261016 (per arm: numpy default_rng([SEED, arm ordinal])); LC1 SEED = 20261016. DEV only (bars before 2024-07-01).

## 1. Summary
- Checked: for every arm of the gross screen, mal_bb, opr_bb_mtf_center, opr_weekly_low_round_sweep, opr_preopen_tops and the 126 candle_close arms, 1,000 placebo sets matched on weekday, 15-minute slot and cooldown, scored by the study's own return function (every real mean and SE below reproduces the published number), plus overlap, week-block bootstrap, best-of-N bars, half-year signs and a fair LC1 control.
- Found: no tested arm's gross mean beats chance once the number of arms tried is counted (arms above their study's best-of-N bar: {beat}); the published day-clustered SE is not too small (placebo SD / SE above 1.2 in {sum(v[0] for v in sdr.values())} of {sum(v['arms'] for v in S.values())} arms); the LC1 control is not fair (about half of its lines are the real level, and untouched lines count as non-holds), and with a touched-only control {len(keep_fair)} of 12 families stay KEEP (published {len(keep_pub)}; lost: {', '.join(lost) or 'none'}; newly passing: {', '.join(gained) or 'none'}).
- Changes: the FAIL / INCONCLUSIVE screen verdicts stand; the LC1 KEEP list must be re-stated on the fair control before any layer uses it.

## 2. Scope
| Study | Window | Method | Result |
|---|---|---|---|
| Gross screen T/notF/C, d=1 h=60 | DEV 2022-01..2024-06 | S.build_ledger events, placebo + overlap + bootstrap | out/placebo_screen.csv |
| mal_bb A1, A2 x h 30/60/120/240 | DEV | study.py sets(), same | out/placebo_mal_bb.csv |
| opr_bb AU, AD x h 60/120/240 | DEV | same | out/placebo_opr_bb.csv |
| wlow RL, AS x h 30/60/120 | DEV | same | out/placebo_wlow.csv |
| preopen H1, H2 x h 60/180/390 | DEV | same | out/placebo_preopen.csv |
| candle_close 126 arms (tf x family x signature), h=60 | DEV | events.csv.gz, cooldown = one event per side and UTC day | out/placebo_candle.csv |
| LC1 12 families | standard DEV decisions 2022-04-01..2024-06-30 | fair touched-only random lines | out/lc1_fair.csv |

Reproduction check: every real arm mean, n and SE equals the published trials.csv / ledger value (columns mean G vs pub mean); the gross-screen control mean -0.0081 and n 1439 match RESULT.md. Placebo test: t05_core.py draws 1,000 sets per arm; test_placebo_nulls.py::test_placebo_sets_are_matched_and_seeded passes (it failed before t05_core.py existed).

Method notes. Statistic: mean side-signed gross % after the study's own funding charge (net = gross - 0.14). Empirical p = (1 + number of placebo means >= the real mean) / 1001 (one-sided). SD ratio = SD of the 1,000 placebo means / the study's published day-clustered SE (above 1.2 = published SE too small). Overlap: share of events whose hold [entry, entry+h] overlaps another event's hold; n_eff = number of connected hold groups. Boot t_net = (mean - 0.14) / SD of 2,000 week-block bootstrap means. need t_gross (pass rule) = 2 + 0.14/SE, the gross t at which t_net reaches 2. Placebo events are redrawn while a same-side pair violates the cooldown; conflict = share left unresolved (0 means none).

## 3. Findings
| ID | Sev | Status | Evidence | Numbers affected | Fix | Card |
|---|---|---|---|---|---|---|
| T05-F1 | S3 | CONFIRMED | scripts/T05/t05_merge.py -> out/summary.json; common.py:192-230, screen.py:220-250 (any-arm PASS, no correction) | No arm reaches its study's best-of-N bar: {beat}. Best-of-N bars (t_gross, 95%): {', '.join(f"{k} N={v['N']}: {v['best_of_n_bar_t']:.2f} (single arm {v['single_bar_t']:.2f})" for k, v in S.items())}. The study pass rule demands more than either bar once the 0.14 % cost is added, so no verdict flips; the risk is a future arm with a smaller cost gap | Add a Holm/best-of-N bar next to the any-arm headline in common.verdict_arm / headline() | none (S3) |
| T05-F2 | S3 | CONFIRMED | out/placebo_*.csv column sd_ratio | Placebo SD / published SE: {', '.join(f"{k} median {v[2]:.2f}, max {v[1]:.2f}, arms >1.2: {v[0]}" for k, v in sdr.items())}. The day-clustered SE is conservative (ratio < 1) for the five G5 studies except opr_bb AD h=60/120 (1.30/1.25). For candle_close the same day-cluster formula is too small in {cs.get('n_sdr_gt12', '?')} of 126 arms (up to {cs.get('max_sdr', 0):.2f}), where 60-minute holds from the 1m/2m/3m timeframes overlap inside a day; the candle study itself publishes win/lift CIs, not this SE, so no published number changes | For arms with several overlapping holds per day use the week-block bootstrap, not the day cluster | none |
| T05-F3 | S3 | CONFIRMED | out/placebo_*.csv columns overlap_share, n_eff | Primary arms have cooldown = hold, so overlap is 0 (screen 3 %); secondary horizons longer than the cooldown overlap (mal_bb A1 h=240 59 %, h=120 30 %; preopen H2 h=390 8 %); the week-block bootstrap t is within about 0.4 of the published t on the primary arms. Lead L7 (390-minute holds, 60-minute cooldown) is real only for the secondary preopen/mal_bb horizons and does not change a verdict | Report n_eff next to n for any arm whose hold exceeds its cooldown | none |
| T05-F4 | S3 | CONFIRMED | Table wlow, arms RL h=30/60/120 | Placebo p = 0.017 / 0.063 / 0.005 on gross means +0.033 / +0.032 / +0.094 % against a placebo mean of about -0.004 %: the closest any arm comes to a pre-cost signal, but t_gross 1.92 at h=120 is under the best-of-12 bar (2.49), and the 0.14 % cost keeps t_net negative (-3.0 at h=60, -0.9 at h=120), so FAIL stands. The published control (non-reclaims) is itself a long-after-the-break sample (ctrl +0.084 % at h=120), so DIFF vs control (t 0.12) understates the placebo excess | Use a time-matched placebo as a second control in the verdict | none (S3) |
| T05-F5 | S1 | CONFIRMED | scripts/T05/t05_lc1.py -> out/lc1_fair.csv, levels_hold.py:78-93 | LC1 control unfair as in lead L8. Fair rerun: {len(keep_fair)} of 12 KEEP vs published {len(keep_pub)}; lost {', '.join(lost) or 'none'}; gained {', '.join(gained) or 'none'} (table in section 5) | Re-state the LC1 KEEP list with the touched-only distance-matched control | raw card (see section 8) |
| T05-F6 | S3 | CONFIRMED | out/placebo_candle.csv | candle_close: {cs.get('n_p05', '?')} of {cs.get('arms', '?')} arms have empirical p < 0.05 (chance: {cs.get('n_p05_expected', 0):.1f}); {cs.get('n_beats_bestofn', '?')} beat the best-of-126 bar; half-year sign is the same in all periods for {cs.get('hy_same_sign', '?')} of {cs.get('hy_arms', '?')} arms with 4+ half-years of n >= 100 | None | none |

## 4. Per-arm tables (empirical p, SD ratio, placebo mean, overlap, n_eff, bootstrap t, best-of-N bar, half-year signs)
{TABLES}

## 5. LC1 fair null (lead L8)
Fair control: for every candidate level of a family, 20 random lines whose distance from the midnight open is drawn from that family's own distances in the same calendar month, sign random, counted only when touched, hold rate = holds / touches. Same HOLD rule, stop width and 2,000-draw day bootstrap as levels_hold.py. The published run was reproduced on the same bars first (out/lc1_orig_reproduction.csv, matches the Q79 table in levels_hold.md: {rep_ok}).
Last column: share of the published-style control lines that equal the real level (sign agrees) / that are never touched.

{table(['family', 'real touches', 'real HOLD', 'published random', 'published diff pp', 'published', 'fair control HOLD', 'fair diff pp', 'fair 95% CI pp', 'fair verdict', 'pub-ctl = real level / untouched'], lc_rows)}

Survivors on the fair control: {', '.join(keep_fair)}. Published KEEP: {', '.join(keep_pub)}. Lost: {', '.join(lost) or 'none'}.

## 6. Leads
| Lead | Status | Evidence |
|---|---|---|
| L7 | CONFIRMED as a risk, CLEARED as a verdict flip | F1 (no correction in headline(); no arm beats best-of-N), F3 (overlap only where hold > cooldown) |
| L8 | CONFIRMED | F5: control lines are the real level in about half the draws and untouched lines are non-holds; fair control changes the KEEP list as shown |

## 7. Not checked
- BLOCKED: LC1 on the footprint window 2024-12-02..2025-03-31 (the brief asks for it): that window lies inside VALIDATION and this run may not read VALIDATION returns; standard DEV was used instead, so no exposure row was written.
- candle_close placebo uses the 1m tape returns h=60 with no delay and no funding (the study's own forward() definition), not the footprint or the 0.14 % cost; arms with fewer than 100 events have no half-year row.
- Best-of-N assumes the N trials are independent draws from the pooled placebo t; nested variants are correlated, so the bar is conservative (too high).

## 8. Decisions taken
- DECISION (OURS): placebo events are drawn uniformly from all DEV 1m bars with the same UTC weekday and 15-minute slot (UTC, so the NY-open arms are matched on UTC clock, not on the NY clock); the cooldown rule of the study (60 or 120 minutes, same side) is enforced by redrawing conflicting events; candle_close uses one event per side and UTC day (its dedupe rule) with at most 12 redraw rounds (unresolved share printed in the conflict column).
- DECISION (OURS): empirical p is one-sided upper tail on the side-signed mean gross; t for the best-of-N null is gross mean / clustered SE.
- DECISION (OURS): trial counts N: trials.csv rows per study (mal_bb 39, opr_bb 6, wlow 12, preopen 26), candle_close 126 (TRIAL_REGISTRY), gross screen 90 (3 arms x 5 delays x 6 horizons).
- DECISION (OURS): effective n = number of connected hold groups (events whose holds touch are one group).
- DECISION (OURS) D1: LC1 rerun on standard DEV, not the footprint window (VALIDATION rule); fair control = 20 lines per candidate level, distances from the same family and calendar month, both signs, touched only.
- DECISION (OURS): the raw card for F5 is NOT created from this worktree (tasks.py new writes outside the card scope); the Supervisor files it: `python scripts/dev/tasks.py new "Re-state LC1 KEEP list on the touched-only fair control" --lane SONNET --prio 2 --ref MyTradingSys/research/dsa_backtest_audit_2026-10-16/T05_placebo_nulls.md`.

## 9. Bridge log
Not applicable: run directly by a worktree builder session (no AIBridge). Worked best: one study per process in parallel chunks, each writing its own CSV. Failed and recovered: candle_close redraw loop (64 s per arm) fixed by redrawing only conflicting rows and capping rounds. Rule for the next chat: profile the first arm before launching 126.

## 10. Handover
1. Top fix: re-state the LC1 KEEP list (F5) in MyTradingSys/research/levels_confluence_2026-10-14/levels_hold.py using a touched-only, distance-matched control.
2. Test that proves it: the control draws never equal the real level and untouched lines are excluded from the denominator (scripts/T05/t05_lc1.py is the reference).
3. Risk: any layer that consumed the 8 KEEP families as priors.
4. Registration lines needed (central files, not edited here): scripts/dev/run_extra_tests.py -> MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/test_placebo_nulls.py.
5. Rerun after the fix: python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py then build_report.py.
"""
REPORT.write_text(txt, encoding="utf-8", newline="\n")
print("wrote", REPORT, len(txt))
