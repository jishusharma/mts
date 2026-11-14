import json
from pathlib import Path

STUDY = Path(__file__).resolve().parents[3] / "mtf_lead_lag_2026-11-09"

for split in ("dev", "val"):
    data = json.loads((STUDY / f"RESULT_{split}.json").read_text(encoding="utf-8"))
    base_rate = data["base_rate_1d_flip_7d"]
    base_3d = data["baseline_fwd"]["3d"]
    print(f"=== {split.upper()} ===")
    print(f"base_rate_1d_flip_7d = {base_rate:.3f} ({base_rate*100:.1f}%)")
    print(f"baseline_fwd 3d: n={base_3d['n']}, mean={base_3d['mean_pct']:.3f}%, se={base_3d['se_pct']:.3f}%")
    for name, rule in data["rules"].items():
        hr = rule["hit_rate_1d_flip_7d"]
        hr_diff_pp = (hr - base_rate) * 100.0
        fwd3 = rule["fwd"]["3d"]
        diff_3d = fwd3["mean_pct"] - base_3d["mean_pct"]
        z_rule_se = diff_3d / fwd3["se_pct"]
        se_combined = (fwd3["se_pct"] ** 2 + base_3d["se_pct"] ** 2) ** 0.5
        z_combined = diff_3d / se_combined
        pass_hr = hr_diff_pp >= 10.0
        pass_ret_rule = z_rule_se > 2.0
        pass_ret_comb = z_combined > 2.0
        print(
            f"  {name}: events={rule['events']}, hit_rate={hr:.3f} (diff={hr_diff_pp:+.1f} pp, >=10pp: {pass_hr}), "
            f"3d_fwd: n={fwd3['n']}, mean={fwd3['mean_pct']:+.3f}%, se={fwd3['se_pct']:.3f}%, "
            f"diff_vs_base={diff_3d:+.3f}%, z(rule_se)={z_rule_se:+.2f} (>2: {pass_ret_rule}), "
            f"z(comb_se)={z_combined:+.2f} (>2: {pass_ret_comb})"
        )
