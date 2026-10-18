"""Count-only gate before a PRE_REG freeze (FABLE_RUNS_AUDIT E1; same rule as pit PRE_REG_V2 item 2).

    python scripts/dev/prereg_gate.py --n <events or days> --sd <sd of R> --cost <R> --m <Holm family size>

Prints MDE = (z_holm + 0.84) * sd / sqrt(n), z_holm = Phi^-1(1 - 0.05 / (2 m)) (two-sided), and exits 1 (BLOCK, do not
freeze) when MDE + cost exceeds MAX_PLAUSIBLE_GROSS (0.30 R, OURS; 0.84 = z for 80 % power, OURS). Exit 2 = bad input.
--sd must be the sd of per-event R (GATE_AUDIT Q1: 1 SD of per-event R is 1.4-4.5 R on the Kurisko data, never 1): sd <= 1 is
the unmeasured placeholder and exits 2 unless --sd-source <file:line> names a measured or two-point value.
--m auto --new-cells N: m = `verdicts.py count --split DEV` (--verdicts-csv overrides the file) + N new cells, so every
PRE_REG uses the same repo-wide m (GATE_AUDIT Q3). Use the number of independent units (days when clustered by day), not raw events.
"""
import argparse
import math
import sys
from pathlib import Path
from statistics import NormalDist

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verdicts  # noqa: E402

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
    ap.add_argument("--m", required=True, help="Holm family size, or 'auto' = DEV variant count + --new-cells")
    ap.add_argument("--new-cells", type=int, default=0)
    ap.add_argument("--verdicts-csv", default=str(verdicts.CSV_PATH))
    ap.add_argument("--sd-source", default="", help="file:line of the measured or two-point sd of per-event R")
    ap.add_argument("--max-gross", type=float, default=MAX_PLAUSIBLE_GROSS)
    a = ap.parse_args(argv)
    if a.m == "auto":
        seen, _ = verdicts.count_variants(a.verdicts_csv, "DEV")
        a.m = len(seen) + a.new_cells
    else:
        try:
            a.m = int(a.m)
        except ValueError:
            print("bad input: --m is an integer or 'auto'")
            return 2
    if a.n <= 0 or a.sd <= 0 or a.m < 1 or a.cost < 0:
        print("bad input: need n>0, sd>0, m>=1, cost>=0")
        return 2
    if a.sd <= 1 and not a.sd_source.strip():
        print("bad input: --sd is the sd of per-event R; sd <= 1 is an unmeasured placeholder (measured values are "
              "1.4-4.5 R): give the real sd or --sd-source <file:line>")
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
