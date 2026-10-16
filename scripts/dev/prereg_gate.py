"""Count-only gate before a PRE_REG freeze (FABLE_RUNS_AUDIT E1; same rule as pit PRE_REG_V2 item 2).

    python scripts/dev/prereg_gate.py --n <events or days> --sd <sd of R> --cost <R> --m <Holm family size>

Prints MDE = (z_holm + 0.84) * sd / sqrt(n), z_holm = Phi^-1(1 - 0.05 / (2 m)) (two-sided), and exits 1 (BLOCK, do not
freeze) when MDE + cost exceeds MAX_PLAUSIBLE_GROSS (0.30 R, OURS; 0.84 = z for 80 % power, OURS). Exit 2 = bad input.
Use the number of independent units (days when clustered by day), not raw events.
"""
import argparse
import math
import sys
from statistics import NormalDist

MAX_PLAUSIBLE_GROSS = 0.30  # R, OURS
POWER_Z = 0.84  # 80 % power, OURS


def z_holm(m):
    return NormalDist().inv_cdf(1 - 0.05 / (2 * m))


def mde(n, sd, m):
    return (z_holm(m) + POWER_Z) * sd / math.sqrt(n)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=float, required=True)
    ap.add_argument("--sd", type=float, required=True)
    ap.add_argument("--cost", type=float, required=True)
    ap.add_argument("--m", type=int, required=True)
    ap.add_argument("--max-gross", type=float, default=MAX_PLAUSIBLE_GROSS)
    a = ap.parse_args(argv)
    if a.n <= 0 or a.sd <= 0 or a.m < 1 or a.cost < 0:
        print("bad input: need n>0, sd>0, m>=1, cost>=0")
        return 2
    d = mde(a.n, a.sd, a.m)
    need = ((z_holm(a.m) + POWER_Z) * a.sd / (a.max_gross - a.cost)) ** 2 if a.max_gross > a.cost else float("inf")
    ok = d + a.cost <= a.max_gross
    print(f"n {a.n:g} sd {a.sd:g} m {a.m} z_holm {z_holm(a.m):.3f} MDE {d:.3f} R + cost {a.cost:g} = {d + a.cost:.3f} "
          f"vs max plausible gross {a.max_gross:g}; n needed {need:.0f}")
    print("PASS: may freeze" if ok else "BLOCK: do not freeze (write BLOCKED.md with these numbers)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
