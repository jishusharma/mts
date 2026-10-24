"""T05 merge: reads out/placebo_*.csv and out/tpool_*.npz, adds the best-of-N null per study, writes out/tables.md and out/summary.json.
python t05_merge.py   (run from the repo root; seed printed)"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, str(HERE))
import t05_core as C  # noqa: E402

SEED = 20261016
STUDIES = [("screen", "Gross screen (session-extreme fade, 2026-10-15)"), ("mal_bb", "MAL BB mid engulf"),
           ("opr_bb", "OPR BB MTF centre"), ("wlow", "Weekly-low round sweep"), ("preopen", "Pre-open tops"),
           ("candle", "Candle close (126 arms)")]


def f(x, p=4):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return "-"
    return "-" if np.isnan(x) else f"{x:.{p}f}"


def table(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(map(str, r)) + " |" for r in rows])


def main():
    print(f"T05 merge SEED={SEED}")
    rng = np.random.default_rng(SEED)
    summ, md = {}, []
    for key, title in STUDIES:
        p = OUT / f"placebo_{key}.csv"
        if not p.exists():
            md.append(f"## {title}\n\nBLOCKED: {p.name} missing\n")
            continue
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        z = np.load(OUT / f"tpool_{key}.npz")
        prim = [r for r in rows if r["primary"] == "1" and r.get("t_gross")]
        N = int(rows[0]["n_trials_study"])
        pool = np.concatenate([z[r["arm"]] for r in prim]).astype(float)
        single = float(np.quantile(pool, 0.95))
        bon = C.best_of_n_bar(pool, N, rng)
        s = dict(study=key, N=N, single_bar_t=single, best_of_n_bar_t=bon, arms=len(prim),
                 n_p05=sum(float(r["p_mean"]) < 0.05 for r in prim), n_p05_expected=0.05 * len(prim),
                 n_beats_bestofn=sum(float(r["t_gross"]) > bon for r in prim),
                 n_sdr_gt12=sum(float(r["sd_ratio"]) > 1.2 for r in prim), max_sdr=max(float(r["sd_ratio"]) for r in prim),
                 median_sdr=float(np.median([float(r["sd_ratio"]) for r in prim])),
                 max_conflict=max(float(r["conflict_share"]) for r in prim))
        summ[key] = s
        md.append(f"## {title}\n\nTrials counted N = {N}. Single-arm placebo bar (95th pct of placebo t_gross, pooled over the {len(prim)} arms below) = {single:.2f}; "
                  f"best-of-{N} bar (95th pct of the max of {N} placebo arms, independence assumed) = {bon:.2f}. The study's own pass rule needs t_gross >= 2 + 0.14/SE per arm.\n")
        if key == "candle":
            bad = sorted(prim, key=lambda r: float(r["p_mean"]))[:12]
            show = bad
            md.append(f"Arms with empirical p < 0.05: {s['n_p05']} of {len(prim)} (chance alone gives {s['n_p05_expected']:.1f}); arms above the best-of-{N} bar: {s['n_beats_bestofn']}. "
                      f"Placebo SD / published SE: median {s['median_sdr']:.2f}, max {s['max_sdr']:.2f}, arms above 1.2: {s['n_sdr_gt12']}. Lowest-p 12 arms shown.\n")
        else:
            show = rows
        head = ["arm", "n", "mean G %", "pub mean", "SE", "placebo mean", "pub control", "p (mean)", "p (t)", "SD ratio", "t_gross", "need t_gross (pass rule)",
                "overlap share", "n_eff", "boot t_net", "conflict"]
        tab = []
        for r in show:
            if not r.get("t_gross"):
                continue
            tab.append([r["arm"], r["n"], f(r["mean_g"]), f(r.get("pub_mean")), f(r["se_pub"]), f(r["placebo_mean"]), f(r.get("ctrl_mean")), f(r["p_mean"], 3),
                        f(r["p_t"], 3), f(r["sd_ratio"], 2), f(r["t_gross"], 2), f(2 + 0.14 / float(r["se_pub"]), 2), f(r["overlap_share"], 2), r["n_eff"],
                        f(r["boot_t_net"], 2), f(r["conflict_share"], 3)])
        md.append(table(head, tab) + "\n")
        hy_cols = sorted({k for r in rows for k in r if k.startswith("hy_")})
        if hy_cols:
            hrows = []
            for r in (show if key == "candle" else rows):
                if any(r.get(c) for c in hy_cols):
                    cells = []
                    signs = []
                    for c in hy_cols:
                        v = r.get(c)
                        if v:
                            mu, nn = v.split("|")
                            cells.append(f"{float(mu):+.3f} ({nn})")
                            signs.append(np.sign(float(mu)))
                        else:
                            cells.append("-")
                    same = "same sign" if len(set(signs)) == 1 else f"{int(sum(s_ > 0 for s_ in signs))}+/{int(sum(s_ < 0 for s_ in signs))}-"
                    hrows.append([r["arm"]] + cells + [same])
            md.append("Half-year mean gross % (n), arms with n >= 100:\n\n" + table(["arm"] + [c[3:] for c in hy_cols] + ["signs"], hrows) + "\n")
    if "candle" in summ:
        rows = list(csv.DictReader(open(OUT / "placebo_candle.csv", encoding="utf-8")))
        hy_cols = sorted({k for r in rows for k in r if k.startswith("hy_")})
        tot = same = 0
        for r in rows:
            sg = [np.sign(float(r[c].split("|")[0])) for c in hy_cols if r.get(c)]
            if len(sg) >= 4:
                tot += 1
                same += len(set(sg)) == 1
        summ["candle"]["hy_arms"], summ["candle"]["hy_same_sign"] = tot, same
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8", newline="\n")
    (OUT / "tables.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
