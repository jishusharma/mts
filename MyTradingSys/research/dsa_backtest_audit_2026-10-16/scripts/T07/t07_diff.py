"""T07 step 2b: diff every published number against the sandbox rerun; write out/rerun_diff.csv and out/determinism.csv.
Tolerance: counts exact, other numbers 1e-6 absolute, words exact. Run after t07_rerun.py (tags a for every study, b for mal_bb_mid_engulf).
"""
import csv
import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t07_common as T  # noqa: E402

REPO = HERE.parents[4]
RES = REPO / "MyTradingSys" / "research"
SB = Path("C:/Users/E-ngineers/AppData/Local/Temp/dsa_audit/T07/sandbox")
OUT = HERE / "out"


def sandbox_dir(key, tag="a"):
    return SB / f"{key}__{tag}" / "MyTradingSys" / "research" / T.RESULTS[key][0]


def main():
    rows, summary = [], {}
    for key, (folder, pairs) in T.RESULTS.items():
        for pub_rel, rr_rel in pairs:
            pub = T.parse_file(RES / folder / pub_rel)
            rrf = sandbox_dir(key) / rr_rel
            if not rrf.is_file():
                for k, kind, v in pub:
                    rows.append([key, pub_rel, k, kind, v, "", "", "NO_RERUN_FILE"])
                continue
            rr = {k: (kind, v) for k, kind, v in T.parse_file(rrf)}
            pk = set()
            for k, kind, v in pub:
                pk.add(k)
                if k not in rr:
                    rows.append([key, pub_rel, k, kind, v, "", "", "MISSING_IN_RERUN"])
                    continue
                v2 = rr[k][1]
                if kind == "text":
                    ok, d = (v == v2), ""
                else:
                    d = abs(float(v) - float(v2))
                    ok = d == 0 if kind == "count" else d <= 1e-6
                if key == "mfe_exit" and not ok and kind == "num":
                    # the current fire files label TRAIN through 2024-12 (VALIDATION bars): returns computed on them are withheld, counts kept
                    v2, d = "WITHHELD_VALIDATION_WINDOW", ""
                rows.append([key, pub_rel, k, kind, v, v2, d if d == "" else f"{d:.3g}", "MATCH" if ok else "DIFF"])
            for k, (kind, v2) in rr.items():
                if k not in pk:
                    rows.append([key, pub_rel, k, kind, "", v2, "", "EXTRA_IN_RERUN"])
    with open(OUT / "rerun_diff.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["result", "published_file", "key", "kind", "published", "rerun", "abs_diff", "status"])
        w.writerows(rows)
    # per-result summary
    for r in rows:
        s = summary.setdefault(r[0], {})
        s[r[7]] = s.get(r[7], 0) + 1
    for k, s in summary.items():
        print(k, s)
    # determinism: mal_bb_mid_engulf run a vs b (RESULT.md, ledger.csv, trials.csv); EXPOSURE_LEDGER.csv carries a wall-clock stamp and is excluded
    det = []
    for f in ("RESULT.md", "ledger.csv", "trials.csv"):
        a = hashlib.sha256((sandbox_dir("mal_bb_mid_engulf", "a") / f).read_bytes()).hexdigest()
        b = hashlib.sha256((sandbox_dir("mal_bb_mid_engulf", "b") / f).read_bytes()).hexdigest()
        det.append(["mal_bb_mid_engulf", f, a, b, a == b])
    with open(OUT / "determinism.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["study", "file", "sha256_run_a", "sha256_run_b", "identical"])
        w.writerows(det)
    print(det)


if __name__ == "__main__":
    main()
