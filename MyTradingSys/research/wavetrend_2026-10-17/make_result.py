"""Render RESULT.md from atlas_out/atlas_results.json (no recomputation)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
o = json.loads((HERE / "atlas_out" / "atlas_results.json").read_text(encoding="utf-8"))
f = lambda x, d=2: "n/a" if x is None or x != x else f"{x:.{d}f}"
L = []
w = L.append
cells = o["cells"]
npass = sum(c["pass_gross_dev"] for c in cells)
w("# WaveTrend DEV atlas: RESULT (card wavetrend-dev-atlas, run 2026-10-17)")
w("")
w(f"Verdict: **{'INCONCLUSIVE' if npass == 0 else 'MIXED'}** - {npass} of 9 frozen cells pass the gross DEV screen. "
  "FAIL/INCONCLUSIVE: stop; this atlas adopts no rule and the cells are not tuned or re-cut; any strategy needs its own PRE_REG with Binance-venue costs, VALIDATION once, HOLDOUT sealed.")
w("")
w("Status: EXPLORATORY BEHAVIOUR TABLE on DEV (2022-01-01..2024-06-30), one run, gross (no fees, no funding). Cells, outcomes, arms and Holm m = 9 exactly as `PRE_REG.md` s5-s6 (committed `cd663831` / `7e75c720`, before `atlas.py`). `atlas.py` raises on any cell not in `PRE_REG.md`. VALIDATION reads: 0. HOLDOUT reads: 0 (the loader refuses bars >= 2024-07-01).")
w("")
w("Reproduce: `python atlas.py --out atlas_out` then `python make_result.py` (seed 20261017, 200 draws). Tests: `python -m pytest test_atlas.py`.")
w("")
w("## Primary arms (Verdict arms)")
w("")
w("Primary outcome: signed gross return open(t+1) -> close(t+12) in the implied direction (reversal toward the centre for A1/A2/C1, direction of the cross for B1, continuation for B2). Means are in percent (SE = day-clustered). Verdict per cell: PASS only if Holm (m = 9) rejects vs the random clock with a positive difference AND the conjunction beats WT-alone and context-alone (|z| > 1.96); otherwise FAIL (no gross edge on DEV), never a strategy verdict.")
w("")
w("| arm | n | mean % | SE % | verdict |")
w("|---|---|---|---|---|")
for c in cells:
    j = c["conj"]
    w(f"| {c['cell']} {c['tf']} {c['event']} {c['context']} | {j['n']} | {f(j['mean_bps']/100,4)} | {f(j['se_bps']/100,4)} | {'PASS' if c['pass_gross_dev'] else 'FAIL'} |")
w("")
w("## Every cell, every arm (primary outcome, bps; hit = share of signed 12-bar returns > 0 with Wilson 95 % CI)")
w("")
w("| Cell | TF | Event | Context | Arm | N | Days | Ev/day | Mean bps | SE bps | Hit (CI) | Mean H4 | Mean H48 | MFE med | MAE med | Resp med |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for c in cells:
    for arm, lab in (("conj", "conjunction"), ("wt_alone", "WT alone"), ("context_alone", "context alone"), ("random_clock", "random clock")):
        a = c[arm]
        hit = f"{a['hit']*100:.1f}%" + (f" ({a['hit_lo']*100:.1f}-{a['hit_hi']*100:.1f})" if "hit_lo" in a else "")
        w(f"| {c['cell']} | {c['tf']} | {c['event']} | {c['context']} | {lab} | {a['n']} | {a.get('days','-')} | {a.get('events_per_day','-')} | "
          f"{f(a['mean_bps'])} | {f(a['se_bps'])} | {hit} | {f(a['mean4_bps'])} | {f(a['mean48_bps'])} | {f(a['mfe_med'],1)} | {f(a['mae_med'],1)} | {f(a.get('resp_med'),1) if 'resp_med' in a else '-'} |")
w("")
w("MFE/MAE are medians over bar extremes (upper bounds), 12 bars, implied direction. Response time = bars until wt1 re-crosses wt2 or reaches 0 against the event side, censored at 12. Random clock: 200 draws matched on TF, UTC hour slot and vol tercile, each draw taking the event's own implied direction. Context alone: same bin, bars with no event of that type, hour slot matched, 200 draws with the bar's own side. SE of the two control arms = SD of the 200 draw means. Median episode depth (max side x wt1, outcome only) for A cells: " +
  ", ".join(f"{c['cell']} {f(c['depth_med_conj'],1)}" for c in cells if "depth_med_conj" in c) + ".")
w("")
w("## Tests, Holm and honest MDE")
w("")
w("| Cell | conj - random clock (bps) | SE | z | p | Holm adj p (m=9) | vs WT alone (diff, z) | vs context alone (diff, z) | Event-days found / PRE_REG | Realised MDE bps (Holm 9, 80 %) | PRE_REG MDE bps (SD x rc SD) | Passes gross DEV |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|")
for c in cells:
    t = c["tests"]
    r, a, x = t["vs_random_clock"], t["vs_wt_alone"], t["vs_context_alone"]
    w(f"| {c['cell']} | {f(r['diff_bps'])} | {f(r['se_bps'])} | {f(r['z'])} | {f(r['p'],3)} | {f(c['holm_adj_p'],3)} | {f(a['diff_bps'])}, {f(a['z'])} | {f(x['diff_bps'])}, {f(x['z'])} | "
      f"{c['event_days_found']} / {c['event_days_prereg']}{' (underpowered)' if c['underpowered'] else ''} | {f(c['realised_mde_bps_holm9'])} | {f(c['mde_bps_prereg_sd'])} | {'yes' if c['pass_gross_dev'] else 'no'} |")
w("")
short = ", ".join(f"{c['cell']} {c['conj']['n']} with an outcome vs {c['events_prereg']} frozen" for c in cells if c["conj"]["n"] != c["events_prereg"])
w("Honest MDE: the realised MDE uses the root-sum-square of the day-clustered SE of the conjunction and the draw SE of the matched random clock (the PRE_REG figure assumes independent unit-variance days, so it is the optimistic bound). Events with an outcome equal the PRE_REG counts except where a signal sits within 12 bars of the series end: " + (short or "none") + ". Event and event-day counts re-derived before any outcome match PRE_REG for all cells: " + str(all(c["counts_match_prereg"] for c in cells)) + ".")
w("")
w("## Per-cell statement")
w("")
w("FAIL here means \"does not pass the gross DEV screen\", not \"no effect\": a cell whose realised MDE exceeds any plausible gross effect (W04-W08 at 14-68 bps against a 12-bar mean move of a few bps) is an underpowered null, read as INCONCLUSIVE for that cell.")
w("")
for c in cells:
    t = c["tests"]["vs_random_clock"]
    w(f"- **{c['cell']}** ({c['tf']} {c['event']} {c['context']}): conj {f(c['conj']['mean_bps'])} bps vs random clock {f(c['random_clock']['mean_bps'])} (diff {f(t['diff_bps'])}, z {f(t['z'])}, Holm adj p {f(c['holm_adj_p'],3)}): "
      f"{'passes' if c['pass_gross_dev'] else 'does NOT pass'} gross DEV. Realised MDE {f(c['realised_mde_bps_holm9'])} bps: a true effect smaller than this was not detectable here.")
w("")
w("## Controls beside the A cells (never cells, never in Holm; unconditioned, same primary outcome, reversal direction)")
w("")
w("| TF | Control | N | Days | Mean bps | SE | Random clock bps | diff z | Hit % |")
w("|---|---|---|---|---|---|---|---|---|")
for r in o["controls"]:
    if r.get("n") == 0:
        continue
    j = r["conj"]
    w(f"| {r['tf']} | {r['event']} | {j['n']} | {j['days']} | {f(j['mean_bps'])} | {f(j['se_bps'])} | {f(r['random_clock']['mean_bps'])} | {f(r['tests']['vs_random_clock']['z'])} | {j['hit']*100:.1f} |")
w("")
w("## Descriptive rows outside Holm (4h unconditioned, flagged underpowered; C2 on 5m/15m, no cell)")
w("")
w("| TF | Event | N | Days | Mean bps | SE | Random clock bps | diff z |")
w("|---|---|---|---|---|---|---|---|")
for r in o["descriptive"]:
    if r.get("n") == 0:
        continue
    j = r["conj"]
    w(f"| {r['tf']} | {r['event']} | {j['n']} | {j['days']} | {f(j['mean_bps'])} | {f(j['se_bps'])} | {f(r['random_clock']['mean_bps'])} | {f(r['tests']['vs_random_clock']['z'])} |")
w("")
w("## Checks")
w("")
w("- Observation module vs `wt_parity_ref.py` on DEV bars (max abs difference, wt1 / wt2): " + "; ".join(f"{k}: {v['max_abs_diff_wt1']:.1e} / {v['max_abs_diff_wt2']:.1e} over {v['valid_both']} bars (valid module {v['valid_module']} = ref {v['valid_ref']})" for k, v in o["module_crosscheck"].items()) + ". The PRE_REG counts are therefore unchanged by the module.")
w("- Trial ids: WT-A01..WT-A09 = W01..W09, one primary test each (PRE_REG s7). The L=60 and A3 controls and the descriptive rows are not trials.")
w("")
w("## Known weaknesses")
w("")
w("1. Draw-based controls: the random-clock SE reflects control resampling noise (200 draws), not independent days of the control; the conjunction SE is day-clustered. The difference z treats the arms as independent (the conjunction is a subset of WT-alone, so the WT-alone contrast is conservative).")
w("2. 5m and 15m cells rest on strongly autocorrelated events within a day; the day cluster is the unit.")
w("3. Bin edges, k, c, R_out, G were chosen on DEV counts (PRE_REG s8); VALIDATION is the only independent check and was not opened.")
w("4. The implied direction is a measurement convention, not a rule. A null on the implied direction says nothing about the opposite sign; the signed table above shows which sign each cell leaned.")
(HERE / "RESULT.md").write_text("\n".join(L) + "\n", newline="\n", encoding="utf-8")
