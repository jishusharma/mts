"""Power gate for the 30 pooled family cells (PRE_REG_LONG.md): n = distinct days of the cell, sd = 1.5 x median stop % (design bound, geometry only,
no return used; OURS), unit %, cost 0.14, m auto + 30. Reads counts_long.csv, calls scripts/dev/prereg_gate.py, writes BLOCKED_LONG.md lines to stdout."""
import csv
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
rows = list(csv.DictReader(open(HERE / "counts_long.csv", encoding="utf-8")))
fam = [r for r in rows if r["tf"] == "15m" and r["session"] in ("asia", "london", "ny") and r["side"] == "both" and r["gate"] in ("range", "bearP40")
       and ((r["study"] == "A_r2r" and r["width"] == "any") or (r["study"] == "B_retest" and r["tag"] == "tagged"))]
print("# prereg_gate output (before any return; n = distinct days of the cell, sd = 1.5 x median stop %, m auto + 30, cost 0.14, unit %)\n")
for r in fam:
    lab = "%s %s %s %s" % (r["study"], r["gate"], r["session"], r["entry"] if r["study"] == "A_r2r" else "k" + r["k"])
    if not r["n"] or int(r["days"]) < 1:
        print("- %s n 0: empty cell (counts toward m), no gate run" % lab)
        continue
    sd = 1.5 * float(r["median_stop_pct"])
    p = subprocess.run([sys.executable, str(REPO / "scripts/dev/prereg_gate.py"), "--n", r["days"], "--sd", str(sd), "--cost", "0.14", "--m", "auto",
                        "--new-cells", "30", "--sd-source", "bb_long_window_2026-11-04/counts_long.csv:median_stop_pct x1.5 (design bound)"],
                       capture_output=True, text=True)
    print("- %s [n_events %s] -> %s" % (lab, r["n"], " ".join(p.stdout.split())[:400] or p.stderr.strip()))
