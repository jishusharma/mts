"""Count-only DEV pass for the c1-v2 detector (card wavetrend-c1-v2). NO outcome is computed.

Reuses the FROZEN v1 pipeline (count_events: load_dev/resample/wt_series/context/bin_of,
select_cells FLOOR and rule) with ONLY the C1 detector swapped to c1_v2.events (paired
confirmed price + WT pivots, DISPOSITION_2026-10-19 correction). k=2, G=20 exactly as
PRE_REG s2 froze (no variant shopping). DEV only, 2022-01..2024-06-30; the loader refuses
any bar >= 2024-07-01 (VALIDATION/HOLDOUT sealed). The input manifest (input_manifest.json)
is re-verified against the files on disk before counting: any mismatch aborts the run.

Outputs (in --out): c1v2_counts_k2_G20.csv (context-binned count table, same schema as the
frozen counts CSV) + c1v2_SELECTION.md (frozen c1v2 cell selection) + v1_C1_sanity.csv (v1
detector C1 counts recomputed on this same data, to be compared against PRE_REG's frozen
C1 row: 3840/907, 1288/694, 392/331, 104/102, 15/15). No return, MFE/MAE or fee anywhere.

Usage: python c1v2_counts.py --out <dir>
"""
import argparse
import csv
import json
from pathlib import Path

import c1_v2
import count_events as ce
import select_cells as sc
import input_manifest as im

K = 2
G = 20


def manifest_check(klines_dir):
    """Verify the on-disk DEV files byte-match input_manifest.json; abort on any mismatch.
    Same file selection as input_manifest.main: glob BTCUSDT-1m-202[234]-*.csv, keep < 2024-07."""
    man = json.loads((Path(__file__).resolve().parent / "input_manifest.json").read_text(encoding="utf-8"))
    expected = {f["name"]: f for f in man["files"]}
    files = [f for f in sorted(Path(klines_dir).glob("BTCUSDT-1m-202[234]-*.csv")) if f.stem[-7:] < "2024-07"]
    assert len(files) == im.EXPECTED_FILES, f"DEV file count {len(files)} != manifest {im.EXPECTED_FILES}"
    names = [f.name for f in files]
    assert names == sorted(expected), f"DEV file set changed: {names} != manifest"
    for f in files:
        h = im.sha256_file(f)
        assert h == expected[f.name]["sha256"], f"{f.name}: sha256 mismatch (input manifest broken)"
    return [str(f) for f in files]


def run():
    files = manifest_check(ce.ARCH)
    A = ce.load_dev(files)
    res = {}
    wt_cache = {}
    for tf, m in ce.TFS.items():
        B = ce.resample(A, m)
        wt1, wt2 = ce.wt_series(B)
        h = ce.HTF[tf]
        htf_wt1 = None
        if h:
            if h not in wt_cache:
                wt_cache[h] = ce.wt_series(ce.resample(A, ce.TFS[h]))
            htf_wt1 = wt_cache[h][0]
        ctx = ce.context(B, wt1, m, htf_wt1, ce.TFS[h] if h else None)
        edges = {"vol": ce.tercile_edges(ctx["vol"]), "part": ce.tercile_edges(ctx["part"])}
        c1_v1, _ = ce.ev_C(B, wt1, K, G, 53)
        c1_v2 = c1_v2.events(B, wt1, K, G)
        res[tf] = (c1_v1, c1_v2, ctx, edges, m, len(wt1))
    return res


def _rows(tf, m, events, ctx, edges, name):
    out = []
    days = {}
    for t, side in events:
        d = (t * m) // 1440
        e = days.setdefault(("ALL", "all"), [0, set(), 0, 0])
        e[0] += 1; e[1].add(d); e[2 + (0 if side > 0 else 1)] += 1
        for var, b in ce.bin_of(ctx, edges, t, side).items():
            if b is not None:
                e = days.setdefault((var, b), [0, set(), 0, 0])
                e[0] += 1; e[1].add(d); e[2 + (0 if side > 0 else 1)] += 1
    for (var, b), (n, ds, up, lo) in days.items():
        out.append({"tf": tf, "event": name, "var": var, "bin": b, "events": n, "event_days": len(ds),
                    "side_up": up, "side_lo": lo, "mde_d": round(float(ce.mde_d(len(ds))), 3)})
    return out


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    res = run()
    rows_v1, rows_v2 = [], []
    for tf, (c1_v1, c1_v2, ctx, edges, m, n) in res.items():
        rows_v1 += _rows(tf, m, c1_v1, ctx, edges, "C1_v1")
        rows_v2 += _rows(tf, m, c1_v2, ctx, edges, "C1_v2")
    with open(out / "v1_C1_sanity.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_v1[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows_v1)
    with open(out / "c1v2_counts_k2_G20.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_v2[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows_v2)
    # frozen c1v2 cell selection: same rule, C1_v2 rows only
    chosen = sc.select([r for r in rows_v2 if r["event"] == "C1_v2"])
    lines = [f"# c1-v2 frozen cell selection (k={K}, G={G}, FLOOR={sc.FLOOR}, rule = select_cells.py s4).",
             "c1v2 counts: c1v2_counts_k2_G20.csv. Count-only; no outcome read. v1 C1 sanity: v1_C1_sanity.csv.",
             "", "| cell | tf | event | context | events | event_days | side_up | side_lo | mde_d |", "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(chosen, 1):
        lines.append(f"| W{i:02d}v2 | {r['tf']} | C1_v2 | {r['var']}:{r['bin']} | {r['events']} | {r['event_days']} | {r['side_up']} | {r['side_lo']} | {r['mde_d']} |")
    if not chosen:
        lines.append("| - | no c1v2 cell clears FLOOR: c1-v2 stays count-only frozen, no outcome read (card gate unmet) |")
    (out / "c1v2_SELECTION.md").write_text("\n".join(lines) + "\n", newline="\n", encoding="utf-8")
    # console summary: per-TF C1 event/days, v1 vs v2
    for tf in ce.TFS:
        c1_v1, c1_v2e, _, _, m, _ = res[tf]
        d1 = len({(t * m) // 1440 for t, _ in c1_v1}); d2 = len({(t * m) // 1440 for t, _ in c1_v2e})
        print(f"{tf}: C1 v1 {len(c1_v1)} events/{d1} days -> c1v2 {len(c1_v2e)} events/{d2} days")
    print("cells frozen:", [f"{r['tf']}:{r['var']}:{r['bin']}" for r in chosen] or "none")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    main(a.out)
