"""B147 exact row-drop tables: old Tom backtest rows vs rows regenerated with HEAD Java.

Reads  <old>/YYYY-MM.rows.jsonl  and <new>/YYYY-MM.rows.jsonl (tom_bt_run.py rows output) and the *.meta.json of the
two snapshot dirs. Prints markdown tables. A row = the top candidate of one kept 15-min snapshot (key: "t").
Fallback stop = the removed 0.2 % stop of SetupCandidatesBuilder: stop == zprice*1.002 (short) or zprice*0.998 (long), 0.01 tolerance.

Usage: python b147_row_drop_exact.py <old_snap_dir> <old_rows_dir> <new_snap_dir> <new_rows_dir>
"""
import collections
import glob
import json
import os
import sys


def meta(d):
    out = {}
    for f in sorted(glob.glob(os.path.join(d, "*.meta.json"))):
        m = json.load(open(f))
        out[m["month"]] = m
    return out


def rows(d):
    out = {}
    for f in sorted(glob.glob(os.path.join(d, "*.rows.jsonl"))):
        month = os.path.basename(f)[:7]
        with open(f, encoding="utf-8") as fh:
            out[month] = [json.loads(line) for line in fh if line.strip()]
    return out


def is_fallback(r):
    z, s, d = r.get("zprice"), r.get("stop"), r.get("dir")
    if z is None or s is None:
        return False
    f = 1.002 if d == "short" else 0.998
    return abs(s - z * f) <= 0.011


def main(old_snap, old_rows, new_snap, new_rows):
    mo, mn = meta(old_snap), meta(new_snap)
    ro, rn = rows(old_rows), rows(new_rows)
    months = sorted(set(mo) | set(mn))
    print("## Kept snapshots per month (old vs HEAD Java)\n")
    print("| month | evaluated | kept old | kept new | lost | gained |")
    print("|---|---|---|---|---|---|")
    to = tn = 0
    lost_all = []
    gained_all = 0
    for m in months:
        a = {r["t"]: r for r in ro.get(m, [])}
        b = {r["t"]: r for r in rn.get(m, [])}
        lost = [a[t] for t in a if t not in b]
        gained = [t for t in b if t not in a]
        lost_all.extend(lost)
        gained_all += len(gained)
        ko = mo.get(m, {}).get("kept", 0)
        kn = mn.get(m, {}).get("kept", 0)
        to += ko
        tn += kn
        print(f"| {m} | {mn.get(m, mo.get(m, {})).get('evaluated', '')} | {ko} | {kn} | {len(lost)} | {len(gained)} |")
    print(f"| **total** | | **{to}** | **{tn}** | **{len(lost_all)}** | **{gained_all}** |\n")
    fb_lost = sum(1 for r in lost_all if is_fallback(r))
    print(f"Lost snapshots whose OLD top candidate used the 0.2 % fallback stop: {fb_lost} of {len(lost_all)}"
          f" ({100.0 * fb_lost / max(1, len(lost_all)):.1f} %).\n")
    all_o = [r for m in ro for r in ro[m]]
    all_n = [r for m in rn for r in rn[m]]
    fo = sum(1 for r in all_o if is_fallback(r))
    fn = sum(1 for r in all_n if is_fallback(r))
    print(f"Rows with the fallback stop: old {fo} of {len(all_o)} ({100.0 * fo / max(1, len(all_o)):.1f} %), "
          f"new {fn} of {len(all_n)} ({100.0 * fn / max(1, len(all_n)):.1f} %).\n")
    print("## Proof histogram (top candidate per kept snapshot)\n")
    ho = collections.Counter(r.get("proof") for r in all_o)
    hn = collections.Counter(r.get("proof") for r in all_n)
    print("| proof | old | new |\n|---|---|---|")
    for p in sorted(set(ho) | set(hn), key=lambda x: (x is None, x)):
        print(f"| {p} | {ho.get(p, 0)} | {hn.get(p, 0)} |")
    print("\n## Long vs short at proof>=5\n")
    print("| run | long | short | SETUP_FORMING |\n|---|---|---|---|")
    for name, rs in (("old", all_o), ("new", all_n)):
        hi = [r for r in rs if (r.get("proof") or 0) >= 5]
        lo = sum(1 for r in hi if r.get("dir") == "long")
        sh = sum(1 for r in hi if r.get("dir") == "short")
        sf = sum(1 for r in rs if r.get("verdict") == "SETUP_FORMING")
        print(f"| {name} | {lo} | {sh} | {sf} |")
    print("\n## Verdict counts\n")
    vo = collections.Counter(r.get("verdict") for r in all_o)
    vn = collections.Counter(r.get("verdict") for r in all_n)
    print("| verdict | old | new |\n|---|---|---|")
    for v in sorted(set(vo) | set(vn), key=str):
        print(f"| {v} | {vo.get(v, 0)} | {vn.get(v, 0)} |")


if __name__ == "__main__":
    main(*sys.argv[1:5])
