"""Blind re-derivation and claim verification for wavetrend_c30_retest_2026-11-04."""
import csv
import json
from pathlib import Path

STUDY_DIR = Path(__file__).resolve().parents[3] / "wavetrend_c30_retest_2026-11-04"


def holm_adjust(pvals):
    """Holm-Bonferroni step-down adjusted p-values."""
    m = len(pvals)
    indexed = sorted(enumerate(pvals), key=lambda x: x[1])
    adj = [0.0] * m
    running_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed):
        val = min(1.0, p * (m - rank))
        running_max = max(running_max, val)
        adj[orig_idx] = running_max
    return adj


def find_row(cells, **kwargs):
    matches = [r for r in cells if all(r[k] == v for k, v in kwargs.items())]
    assert len(matches) == 1, f"Expected 1 match for {kwargs}, got {len(matches)}"
    return matches[0]


def main():
    with open(STUDY_DIR / "dev_cells.csv", newline="", encoding="utf-8") as f:
        cells = list(csv.DictReader(f))
    with open(STUDY_DIR / "counts.csv", newline="", encoding="utf-8") as f:
        counts = list(csv.DictReader(f))
    with open(STUDY_DIR / "dev_survivors.json", encoding="utf-8") as f:
        survivors_json = json.load(f)
    regime_mix = (STUDY_DIR / "regime_mix_dev.txt").read_text(encoding="utf-8").strip()

    print(f"Regime mix (regime_mix_dev.txt): {regime_mix}")
    print(f"dev_cells.csv rows: {len(cells)}, counts.csv rows: {len(counts)}")
    print(f"dev_survivors.json: {survivors_json} (count={len(survivors_json)})")

    # Verify counts.csv matches dev_cells.csv
    counts_map = {
        (r["conf"], r["entry"], r["gate"], r["session"], r["side"], r["tf"]): (
            int(r["days"]),
            int(r["n"]),
            int(r["signals"]),
        )
        for r in counts
    }
    mismatches = sum(
        1
        for r in cells
        if counts_map.get((r["conf"], r["entry"], r["gate"], r["session"], r["side"], r["tf"]))
        != (int(r["days"]), int(r["n"]), int(r["signals"]))
    )
    print(f"counts.csv vs dev_cells.csv mismatches: {mismatches}")

    # Confirmatory families
    fam_a = [
        r for r in cells
        if r["gate"] == "with" and r["session"] == "ALL" and r["conf"] in ("rsi", "div")
    ]
    fam_b = [
        r for r in cells
        if r["gate"] == "with"
        and r["session"] in ("asia", "london", "ny", "late")
        and r["conf"] in ("rsi", "div")
    ]
    print(f"Family A cells: {len(fam_a)}, Family B cells: {len(fam_b)}")

    for name, fam in [("Family A", fam_a), ("Family B", fam_b)]:
        recomputed_holm = holm_adjust([float(r["p"]) for r in fam])
        max_diff = max(abs(recomputed_holm[i] - float(fam[i]["holm_p"])) for i in range(len(fam)))
        surv = [
            r for i, r in enumerate(fam)
            if int(r["n"]) >= 30
            and int(r["days"]) >= 20
            and float(r["net"]) > 0
            and recomputed_holm[i] < 0.05
            and float(r["excess_t"]) >= 2.0
        ]
        mean_net = sum(float(r["net"]) for r in fam) / len(fam)
        print(f"{name}: max_holm_diff={max_diff:.2e}, survivors={len(surv)}, mean_net={mean_net:.6f}%")

    # Claim checks matching RESULT.md
    print("\n--- Bare dots (conf=none, gate=all, session=ALL, entry=signal) ---")
    for tf in ("15m", "30m", "1h"):
        for side in ("buy", "sell"):
            r = find_row(cells, conf="none", gate="all", session="ALL", entry="signal", tf=tf, side=side)
            print(f"  {tf} {side}: n={r['n']}, days={r['days']}, net={float(r['net']):.3f}%")

    n30 = [r for r in cells if int(r["n"]) >= 30]
    ci_below = [r for r in n30 if float(r["ci_hi"]) < 0]
    ci_above = [r for r in n30 if float(r["ci_lo"]) > 0]
    print(f"Cells with n>=30: {len(n30)}, CI entirely < 0: {len(ci_below)}, CI entirely > 0: {len(ci_above)}")

    print("\n--- Trend gate (conf=none, session=ALL, entry=signal) ---")
    for side in ("sell", "buy"):
        for tf in ("15m", "30m", "1h"):
            rw = find_row(cells, conf="none", gate="with", session="ALL", entry="signal", tf=tf, side=side)
            ra = find_row(cells, conf="none", gate="against", session="ALL", entry="signal", tf=tf, side=side)
            print(f"  {tf} {side}: with={float(rw['net']):.3f}%, against={float(ra['net']):.3f}%")

    print("\n--- Specific confirmatory cells ---")
    r15_rsi_sell = find_row(cells, conf="rsi", gate="with", session="ALL", entry="signal", tf="15m", side="sell")
    print(
        f"  15m sell rsi with signal ALL: n={r15_rsi_sell['n']}, days={r15_rsi_sell['days']}, "
        f"gross={float(r15_rsi_sell['gross']):.3f}%, net={float(r15_rsi_sell['net']):.3f}% "
        f"[{float(r15_rsi_sell['ci_lo']):.3f}, {float(r15_rsi_sell['ci_hi']):.3f}], "
        f"excess={float(r15_rsi_sell['excess']):.3f}% (t={float(r15_rsi_sell['excess_t']):.2f}), "
        f"holm_p={float(r15_rsi_sell['holm_p']):.3f}"
    )

    r1h_div_sig = find_row(cells, conf="div", gate="with", session="ALL", entry="signal", tf="1h", side="sell")
    print(
        f"  1h sell div with signal ALL: n={r1h_div_sig['n']}, days={r1h_div_sig['days']}, "
        f"net={float(r1h_div_sig['net']):.3f}% [{float(r1h_div_sig['ci_lo']):.3f}, {float(r1h_div_sig['ci_hi']):.3f}]"
    )

    r1h_div_ret = find_row(cells, conf="div", gate="with", session="ALL", entry="retest", tf="1h", side="sell")
    print(
        f"  1h sell div with retest ALL: n={r1h_div_ret['n']}, days={r1h_div_ret['days']}, "
        f"net={float(r1h_div_ret['net']):.3f}% [{float(r1h_div_ret['ci_lo']):.3f}, {float(r1h_div_ret['ci_hi']):.3f}], "
        f"excess_t={float(r1h_div_ret['excess_t']):.2f}, holm_p={float(r1h_div_ret['holm_p']):.2f}"
    )

    r15_rsi_buy = find_row(cells, conf="rsi", gate="with", session="ALL", entry="signal", tf="15m", side="buy")
    print(
        f"  15m buy rsi with signal ALL: n={r15_rsi_buy['n']}, days={r15_rsi_buy['days']}, "
        f"net={float(r15_rsi_buy['net']):.3f}% [{float(r15_rsi_buy['ci_lo']):.3f}, {float(r15_rsi_buy['ci_hi']):.3f}], "
        f"holm_p={float(r15_rsi_buy['holm_p']):.3f}"
    )

    # Retest vs signal in 12 pooled with-trend rsi/div pairs
    better = 0
    worse = 0
    drop_pcts = []
    for tf in ("15m", "30m", "1h"):
        for side in ("buy", "sell"):
            for conf in ("rsi", "div"):
                rs = find_row(cells, conf=conf, gate="with", session="ALL", entry="signal", tf=tf, side=side)
                rr = find_row(cells, conf=conf, gate="with", session="ALL", entry="retest", tf=tf, side=side)
                if float(rr["net"]) > float(rs["net"]):
                    better += 1
                else:
                    worse += 1
                if int(rs["signals"]) > 0:
                    drop_pcts.append(100.0 * (1.0 - int(rr["n"]) / int(rs["signals"])))
    print(
        f"  Retest vs signal (12 pooled with-trend rsi/div): better={better}, worse={worse}, "
        f"signal removal range={min(drop_pcts):.1f}%-{max(drop_pcts):.1f}%"
    )

    r15_asia = find_row(cells, conf="rsi", gate="with", session="asia", entry="signal", tf="15m", side="sell")
    print(
        f"  15m sell rsi with asia signal: n={r15_asia['n']}, days={r15_asia['days']}, "
        f"net={float(r15_asia['net']):.3f}% [{float(r15_asia['ci_lo']):.3f}, {float(r15_asia['ci_hi']):.3f}], "
        f"excess={float(r15_asia['excess']):.3f}% (t={float(r15_asia['excess_t']):.2f})"
    )

    r_bull = find_row(cells, conf="none", gate="reg_bull", session="ALL", entry="signal", tf="15m", side="buy")
    r_range = find_row(cells, conf="none", gate="reg_range", session="ALL", entry="signal", tf="15m", side="buy")
    r_bear_nz = [r for r in cells if r["gate"] == "reg_bear" and int(r["n"]) > 0]
    print(
        f"  Regime 15m buy none signal: reg_bull n={r_bull['n']} net={float(r_bull['net']):.3f}%, "
        f"reg_range n={r_range['n']} net={float(r_range['net']):.3f}%, reg_bear nonzero={len(r_bear_nz)}"
    )


if __name__ == "__main__":
    main()
