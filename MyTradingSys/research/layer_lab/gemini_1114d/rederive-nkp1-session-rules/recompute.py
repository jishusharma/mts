import csv
import json
from pathlib import Path

STUDY_DIR = Path("MyTradingSys/research/nkp1-session-rules-phase-1114_2026-11-14")
Z_90 = 1.2816


def bh_adjust(pvals):
    m = len(pvals)
    indexed = sorted(enumerate(pvals), key=lambda x: x[1])
    q_sorted = [0.0] * m
    running_min = 1.0
    for rank_idx in range(m - 1, -1, -1):
        orig_idx, p = indexed[rank_idx]
        rank = rank_idx + 1
        q = min(1.0, p * m / rank)
        running_min = min(running_min, q)
        q_sorted[orig_idx] = running_min
    return q_sorted


def main():
    # 1. Check phase shares and eligible phases from cells_frozen.json
    frozen = json.loads((STUDY_DIR / "cells_frozen.json").read_text(encoding="utf-8"))
    shares = frozen["dev_phase_share"]
    phase_map = {
        "CAPITULATION": 1,
        "MARKDOWN": 2,
        "RELIEF": 3,
        "ACCUM-RANGE": 4,
        "MARKUP": 5,
        "DISTRIBUTION": 6,
    }
    eligible_phases = {phase_map[k] for k, v in shares.items() if v >= 0.05}
    print(f"Phase shares sum: {sum(shares.values()):.4f}")
    print(f"Eligible phases (>=5% DEV days): {sorted(eligible_phases)}")
    print(f"Frozen eligible_phases: {frozen['eligible_phases']}")

    # 2. Recompute Step B selection from dev_cells_all.csv
    dev_rows = []
    with (STUDY_DIR / "dev_cells_all.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["phase"] = int(row["phase"])
            row["layer"] = int(row["layer"])
            row["bucket"] = int(row["bucket"])
            row["n"] = int(row["n"])
            row["days"] = int(row["days"])
            row["mean"] = float(row["mean"]) if row["mean"] else None
            row["se"] = float(row["se"]) if row["se"] else None
            row["score"] = float(row["score"]) if row["score"] else None
            row["eligible"] = row["eligible"] == "True"
            dev_rows.append(row)

    print(f"\ndev_cells_all.csv total rows: {len(dev_rows)}")
    max_score_diff = 0.0
    elig_mismatches = 0
    for r in dev_rows:
        if r["mean"] is not None and r["se"] is not None:
            recomp_score = r["mean"] - Z_90 * r["se"]
            diff = abs(recomp_score - r["score"])
            if diff > max_score_diff:
                max_score_diff = diff
        recomp_elig = (r["phase"] in eligible_phases) and (r["n"] >= 150) and (r["days"] >= 40)
        if recomp_elig != r["eligible"]:
            elig_mismatches += 1
    print(f"Max |recomputed_score - csv_score|: {max_score_diff:.12g}")
    print(f"Eligibility mismatches: {elig_mismatches}")

    # Select top 3 per variant with score > 0, at most 1 cell per layer, eligible == True
    variants = ["NK1-UTC", "NK1-NY", "NK5-NYasia", "NK5-UTC4h"]
    recomp_kept = {}
    for v in variants:
        cands = [
            r for r in dev_rows
            if r["variant"] == v
            and (r["phase"] in eligible_phases)
            and r["n"] >= 150
            and r["days"] >= 40
            and r["score"] is not None
            and (r["mean"] - Z_90 * r["se"]) > 0.0
        ]
        cands.sort(key=lambda r: r["mean"] - Z_90 * r["se"], reverse=True)
        picked = []
        used_layers = set()
        for c in cands:
            if c["layer"] in used_layers:
                continue
            picked.append(c)
            used_layers.add(c["layer"])
            if len(picked) == 3:
                break
        recomp_kept[v] = picked
        print(f"Variant {v}: {len(cands)} positive eligible candidates -> {len(picked)} kept")
        for p in picked:
            print(f"  phase={p['phase']} layer={p['layer']} bucket={p['bucket']} n={p['n']} days={p['days']} mean={p['mean']:.6f} score={p['mean'] - Z_90*p['se']:.6f}")

    # 3. Recompute Step C VAL verdict & BH q-values from val_kept_cells.csv
    val_rows = []
    with (STUDY_DIR / "val_kept_cells.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            val_rows.append(row)

    print(f"\nval_kept_cells.csv total rows: {len(val_rows)}")
    pvals = [float(r["p"]) for r in val_rows]
    recomp_bh = bh_adjust(pvals)

    pass_count = 0
    for i, r in enumerate(val_rows):
        n = int(r["n"])
        net = float(r["net"])
        gross = float(r["gross"])
        costR = float(r["costR"])
        ci_lo = float(r["ci_lo"])
        ex5 = float(r["ex5"])
        placebo_p = float(r["placebo_p"])
        dev_net = float(r["dev_net"])
        shrink = float(r["shrink"])
        bh_q_csv = float(r["bh_q"])
        bh_q = recomp_bh[i]

        net_diff = abs((gross - costR) - net)
        shrink_diff = abs((net - dev_net) - shrink)
        bh_diff = abs(bh_q - bh_q_csv)

        if n < 150:
            verdict = "UNDERPOWERED"
        elif (net > 0) and (ci_lo > 0) and (ex5 > 0) and (placebo_p < 0.05) and (bh_q < 0.10):
            verdict = "PASS"
            pass_count += 1
        else:
            verdict = "FAIL"

        print(
            f"  VAL cell {r['variant']} {r['phase']} {r['layer']} {r['bucket']}: "
            f"n={n}, net={net:.6f}, ci_lo={ci_lo:.6f}, ex5={ex5:.6f}, "
            f"p={float(r['p']):.6f}, bh_q={bh_q:.6f} (csv={bh_q_csv:.6f}, diff={bh_diff:.2e}), "
            f"placebo_p={placebo_p:.4f}, net_diff={net_diff:.2e}, shrink_diff={shrink_diff:.2e}, "
            f"verdict={verdict} (csv={r['verdict']})"
        )

    overall_verdict = "NO KEPT CELLS" if len(val_rows) == 0 else ("PASS" if pass_count > 0 else "FAIL")
    mean_shrink = sum(float(r["net"]) - float(r["dev_net"]) for r in val_rows) / len(val_rows) if val_rows else 0.0
    print(f"\nOverall recomputed verdict: {overall_verdict} ({pass_count}/{len(val_rows)} passed)")
    print(f"Mean DEV-to-VAL shrinkage (VAL net - DEV net): {mean_shrink:.6f}")

    # 4. Check stepA_phase_table.csv consistency
    with (STUDY_DIR / "stepA_phase_table.csv").open(encoding="utf-8") as f:
        stepA = list(csv.DictReader(f))
    print(f"\nstepA_phase_table.csv rows: {len(stepA)}")
    max_stepA_net_diff = 0.0
    max_stepA_diff_diff = 0.0
    variant_totals = {v: {"dev_n_app": 0, "val_n_app": 0} for v in variants}
    for r in stepA:
        v = r["variant"]
        variant_totals[v]["dev_n_app"] += int(r["DEV_n_app"])
        variant_totals[v]["val_n_app"] += int(r["VAL_n_app"])
        for split in ("DEV", "VAL"):
            g_str = r[f"{split}_gross_app"]
            c_str = r[f"{split}_cost_app"]
            n_val_str = r[f"{split}_net_app"]
            n_opp_str = r[f"{split}_net_opp"]
            d_str = r[f"{split}_diff"]
            if g_str and c_str and n_val_str:
                max_stepA_net_diff = max(max_stepA_net_diff, abs((float(g_str) - float(c_str)) - float(n_val_str)))
            if n_val_str and n_opp_str and d_str:
                max_stepA_diff_diff = max(max_stepA_diff_diff, abs((float(n_val_str) - float(n_opp_str)) - float(d_str)))
    print(f"Max StepA net diff: {max_stepA_net_diff:.2e}, max diff diff: {max_stepA_diff_diff:.2e}")
    for v, t in variant_totals.items():
        print(f"  {v}: DEV_n_app={t['dev_n_app']}, VAL_n_app={t['val_n_app']}, total_app={t['dev_n_app'] + t['val_n_app']}")

    # 5. Check layer_coverage.csv
    with (STUDY_DIR / "layer_coverage.csv").open(encoding="utf-8") as f:
        cov = list(csv.DictReader(f))
    print(f"\nlayer_coverage.csv rows: {len(cov)}")
    for v in variants:
        v_rows = [r for r in cov if r["variant"] == v]
        sigs = {int(r["signals"]) for r in v_rows}
        c8 = [r for r in v_rows if r["layer"] == "C8"][0]
        c4 = [r for r in v_rows if r["layer"] == "C4"][0]
        print(f"  {v}: signals={sigs}, C8(dev={c8['dev_with_data']}, val={c8['val_with_data']}), C4(dev={c4['dev_with_data']}, val={c4['val_with_data']})")


if __name__ == "__main__":
    main()
