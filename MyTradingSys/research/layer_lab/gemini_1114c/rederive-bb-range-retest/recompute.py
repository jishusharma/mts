import csv
import json
from pathlib import Path

STUDY_DIR = Path("MyTradingSys/research/bb_range_retest_2026-11-04")


def holm_bonferroni(p_values):
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m
    running_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed):
        val = min(1.0, p * (m - rank))
        running_max = max(running_max, val)
        adjusted[orig_idx] = running_max
    return adjusted


def main():
    with open(STUDY_DIR / "dev_cells.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    with open(STUDY_DIR / "counts.csv", newline="", encoding="utf-8") as f:
        count_rows = list(csv.DictReader(f))

    with open(STUDY_DIR / "dev_survivors.json", encoding="utf-8") as f:
        survivors_json = json.load(f)

    regime_dev = (STUDY_DIR / "regime_mix_dev.txt").read_text(encoding="utf-8").strip()
    regime_count = (STUDY_DIR / "regime_mix_count.txt").read_text(encoding="utf-8").strip()

    # Confirmatory family: gate=range, session in {asia, london, ny}, side=both, tag=tagged, k in {0.25, 0.5, 1.0}
    family = [
        r for r in rows
        if r["gate"] == "range"
        and r["session"] in {"asia", "london", "ny"}
        and r["side"] == "both"
        and r["tag"] == "tagged"
    ]
    family.sort(key=lambda r: (float(r["k"]), ["asia", "london", "ny"].index(r["session"])))

    print(f"Regime mix dev: {regime_dev}")
    print(f"Regime mix count: {regime_count}")
    print(f"dev_survivors.json: {survivors_json}")
    print(f"Confirmatory family count: {len(family)}")

    p_vals = [float(r["p"]) for r in family]
    recomputed_holm = holm_bonferroni(p_vals)

    survivors = []
    fill_rates_sig = []
    fill_rates_re = []

    print("\n--- Confirmatory Family (9 cells) ---")
    for r, h_p in zip(family, recomputed_holm):
        n = int(r["n"])
        days = int(r["days"])
        fills = int(r["fills"])
        reentered = int(r["reentered"])
        signals = int(r["signals"])
        fr_sig = fills / signals
        fr_re = fills / reentered
        fill_rates_sig.append(fr_sig)
        fill_rates_re.append(fr_re)

        gross = float(r["gross"])
        net = float(r["net"])
        se = float(r["se"])
        ci_lo = float(r["ci_lo"])
        ci_hi = float(r["ci_hi"])
        hit_target = float(r["hit_target"])
        p = float(r["p"])
        holm_p_csv = float(r["holm_p"])
        t_val = float(r["t"])
        vs_ungated_t = float(r["vs_ungated_t"])

        # Recompute checks
        assert abs((gross - 0.14) - net) < 1e-9, f"net mismatch: {gross - 0.14} vs {net}"
        assert abs((net - 1.96 * se) - ci_lo) < 1e-9, f"ci_lo mismatch"
        assert abs((net + 1.96 * se) - ci_hi) < 1e-9, f"ci_hi mismatch"
        assert abs(h_p - holm_p_csv) < 1e-9, f"holm_p mismatch: {h_p} vs {holm_p_csv}"

        is_surv = (
            n >= 30
            and days >= 20
            and net > 0
            and h_p < 0.05
            and vs_ungated_t >= 2.0
        )
        if is_surv:
            survivors.append((r["session"], r["k"]))

        print(
            f"k={r['k']:>4} {r['session']:<6} | n={n:>3} days={days:>3} "
            f"fill={fr_sig*100:5.1f}% (re={fr_re*100:5.1f}%) "
            f"gross={gross:+.4f}% net={net:+.4f}% CI=[{ci_lo:+.4f}, {ci_hi:+.4f}] "
            f"hit={hit_target*100:4.1f}% p={p:.4f} holm_p={h_p:.4f} "
            f"vs_ung_t={vs_ungated_t:+.3f} surv={is_surv} (csv={r['survivor']})"
        )

    print(f"\nRecomputed fill rate range (fills/signals): {min(fill_rates_sig)*100:.1f}% - {max(fill_rates_sig)*100:.1f}%")
    print(f"Recomputed fill rate range (fills/reentered): {min(fill_rates_re)*100:.1f}% - {max(fill_rates_re)*100:.1f}%")
    print(f"Recomputed survivors: {len(survivors)} -> {survivors}")

    # Summary stats across 9 cells
    nets = [float(r["net"]) for r in family]
    grosses = [float(r["gross"]) for r in family]
    print(f"Family net range: {min(nets):+.4f}% to {max(nets):+.4f}%, mean={sum(nets)/len(nets):+.4f}%")
    print(f"Family gross range: {min(grosses):+.4f}% to {max(grosses):+.4f}%, mean={sum(grosses)/len(grosses):+.4f}%")

    # Also check ALL-session range tagged rows for k=0.25, 0.5, 1.0
    print("\n--- ALL-session range tagged (descriptive) ---")
    all_sess = [
        r for r in rows
        if r["gate"] == "range"
        and r["session"] == "ALL"
        and r["side"] == "both"
        and r["tag"] == "tagged"
    ]
    for r in sorted(all_sess, key=lambda x: float(x["k"])):
        print(
            f"k={r['k']:>4} ALL | n={r['n']} days={r['days']} "
            f"fill={float(r['fill_rate'])*100:.1f}% gross={float(r['gross']):+.4f}% "
            f"net={float(r['net']):+.4f}% p={float(r['p']):.4f}"
        )


if __name__ == "__main__":
    main()
