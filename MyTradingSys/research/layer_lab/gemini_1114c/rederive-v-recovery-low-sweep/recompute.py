"""Recompute headline counts and power-gate numbers for v_recovery_low_sweep_2026-11-04."""
import json
import math
from pathlib import Path
from statistics import NormalDist

REPO = Path(__file__).resolve().parents[5]
STUDY = REPO / "MyTradingSys/research/v_recovery_low_sweep_2026-11-04"
counts = json.loads((STUDY / "counts.json").read_text(encoding="utf-8"))

events = counts["events"]
n_days = counts["event_days"]
cost = 0.14  # TAKER_RT_PCT from MyTradingSys/backtest/research_kit.py:21
max_gross = 0.30  # MAX_PLAUSIBLE_GROSS from scripts/dev/prereg_gate.py:21
power_z = 0.84  # POWER_Z from scripts/dev/prereg_gate.py:22
sds = {"4h": 1.1, "24h": 2.5, "72h": 4.3}  # PRE_REG.md:22

print(f"counts.json -> events={events}, event_days={n_days}")
for m in (224,):
    z_holm = NormalDist().inv_cdf(1 - 0.05 / (2 * m))
    print(f"\nm={m}, z_holm={z_holm:.3f}")
    for hz, sd in sds.items():
        mde = (z_holm + power_z) * sd / math.sqrt(n_days)
        mde_plus_cost = mde + cost
        n_needed = ((z_holm + power_z) * sd / (max_gross - cost)) ** 2
        blocked = mde_plus_cost > max_gross
        print(
            f"  {hz} (sd={sd}): MDE={mde:.3f}, MDE+cost={mde_plus_cost:.3f} vs {max_gross:.2f}, "
            f"n_needed={n_needed:.0f}, gate={'BLOCK' if blocked else 'PASS'}"
        )
