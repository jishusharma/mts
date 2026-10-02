import sys
sys.dont_write_bytecode = True
"""Diagnostic for the Tom core backtest all-shorts question (research, offline, read-only on repo + snapshots).

The row cache (F:\\MTS\\data\\tom_bt/*.rows.jsonl, tom_bt.py:99-112) keeps only the FINAL verdict, not the reason.
This script re-reads the snapshots whose cached row has proof >= 5, replays tom_bt.snapshot_to_row's two-pass logic
(tom_bt.py:101-105) and records the verdict reason per row, plus a stage attribution obtained by calling
compute_verdict on a condition-stripped copy (no price_vs_va / cvd_slope), so no verdict.py logic is duplicated:
  stage0  compute_verdict(stripped, 'aligned')  = lines 110-121 (net_rr / tier / proof ladder)
  stage1  compute_verdict(stripped, pd_all)     = + lines 122-125 (proof-direction gates)
  final   compute_verdict(full, pd)             = + lines 127-137 (broken-VA and flow gates)
Writes <TOM_WORK_DIR>/allshorts.diag.jsonl (one row per proof>=5 cached row) and prints the tables.
Usage: python MyTradingSys/backtest/tom_bt_diag.py"""
import collections
import glob
import gzip
import json
import os
import re
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

SNAP_DIR = Path(os.environ.get("TOM_SNAP_DIR", r"F:\MTS\data\tom_snapshots"))
WORK = Path(os.environ.get("TOM_WORK_DIR", r"F:\MTS\data\tom_bt"))
OUT = Path(os.environ.get("TOM_DIAG_OUT", str(WORK / "allshorts.diag.jsonl")))
_TS = re.compile(r'"timestamp_utc"\s*:\s*"([^"]+)"')


def main():
    from snapshots import parse_ts
    import verdict
    from verdict import compute_verdict, proof_dir_of

    want, base = {}, collections.Counter()
    nrows = 0
    for p in sorted(WORK.glob("*.rows.jsonl")):
        mon = p.name.replace(".rows.jsonl", "")
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                nrows += 1
                base[(r.get("proof") or 0, r.get("dir") or "")] += 1
                if (r.get("proof") or 0) >= 5:
                    want.setdefault(mon, {})[r["t"]] = r
    n_want = sum(len(v) for v in want.values())
    print("cache rows: %d; cached rows with proof>=5: %d in %d months" % (nrows, n_want, len(want)))

    t0 = time.time()
    out = []
    for mon in sorted(want):
        path = SNAP_DIR / (mon + ".jsonl.gz")
        need = want[mon]
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            for line in fh:
                m = _TS.search(line)
                if not m or parse_ts(m.group(1)) not in need:
                    continue
                s = json.loads(line)
                t = parse_ts(s.get("timestamp_utc", ""))
                cached = need.pop(t)
                # exact cache path (tom_bt.py:101-105): proof direction only when the full first pass is WATCH/FORMING
                v = compute_verdict(s, "aligned")
                pd = "aligned"
                if v["verdict"] in ("WATCH", "SETUP_FORMING"):
                    pd = proof_dir_of(s, fail_closed=True)
                    v = compute_verdict(s, pd)
                # stage attribution on a condition-stripped copy (no flow / VA gates)
                bare = dict(s)
                bare["conditions"] = {}
                v0 = compute_verdict(bare, "aligned")
                pd_all = proof_dir_of(s, fail_closed=True)
                v1 = compute_verdict(bare, pd_all)
                v_all = compute_verdict(s, pd_all)  # variant: proof direction always computed (no cache shortcut)
                cond = s.get("conditions") or {}
                try:
                    det = verdict.build_math_object(s).get("proof_direction_details") or []
                except Exception as e:  # keep the row; the error is tabulated
                    det = ["ERR " + type(e).__name__]
                mth = (v.get("top") or {}).get("math") or {}
                out.append(dict(t=t, direction=v["direction"], proof=v["proof"], proof_dir=pd, reason=v["reason"],
                                verdict=v["verdict"], stage0=v0["verdict"], stage0_reason=v0["reason"],
                                stage1=v1["verdict"], proof_dir_all=pd_all, verdict_pd_always=v_all["verdict"],
                                reason_pd_always=v_all["reason"], price_vs_va=cond.get("price_vs_va"),
                                cvd_slope=cond.get("cvd_slope"), net_rr=v["net_rr"],
                                net_rr_sanity=mth.get("net_rr_sanity"), tier=mth.get("tier"),
                                cached_verdict=cached["verdict"],
                                pd_details=[re.sub(r"=[-\d.]+", "=#", x) for x in det]))
        if need:
            print("MISSING %d proof>=5 snapshots in %s" % (len(need), mon))
    out.sort(key=lambda r: r["t"])
    with open(OUT, "w", encoding="utf-8", newline="\n") as fo:
        for r in out:
            fo.write(json.dumps(r) + "\n")
    print("replayed %d proof>=5 rows in %.1fs; written %s" % (len(out), time.time() - t0, OUT))
    print("replay-vs-cache verdict mismatches:", sum(1 for r in out if r["verdict"] != r["cached_verdict"]))

    def tab(title, keyf, rows):
        c = collections.Counter(keyf(r) for r in rows)
        print("\n== %s (n=%d)" % (title, len(rows)))
        for k, n in sorted(c.items(), key=lambda kv: (-kv[1], str(kv[0]))):
            print("  %-70s %d" % (k, n))

    def rkey(r):  # reason with the numeric tail removed so net_rr values group
        return re.sub(r"[-\d.]+ < [\d.]+", "X < floor", r["reason"]) if r["reason"].startswith("net_rr") else r["reason"]

    print("\nproof>=5 rows scanned: %d" % len(out))
    tab("verdict x direction (all proof>=5)", lambda r: (r["verdict"], r["direction"]), out)
    loss = [r for r in out if r["verdict"] != "SETUP_FORMING"]
    tab("LOSSES by reason", rkey, loss)
    tab("LOSSES by (reason, direction)", lambda r: (rkey(r), r["direction"]), loss)
    tab("LOSSES by stage-that-removed it (stage0 verdict, stage1 verdict, final verdict, reason-class)",
        lambda r: (r["stage0"], r["stage1"], r["verdict"], rkey(r)), loss)
    tab("net_rr_sanity x tier x direction for stage0 losses",
        lambda r: (r["net_rr_sanity"], r["tier"], r["direction"]), [r for r in loss if r["stage0"] not in ("WATCH", "SETUP_FORMING")])
    tab("flow-gate losses: (direction, cvd_slope, price_vs_va)", lambda r: (r["direction"], r["cvd_slope"], r["price_vs_va"]),
        [r for r in loss if r["reason"] in ("flow contradiction",) or "broken" in r["reason"]])
    tab("proof-direction details (math_object_builder) by direction", lambda r: (r["direction"], tuple(r["pd_details"])), out)
    tab("survivors: (direction, cvd_slope, price_vs_va)", lambda r: (r["direction"], r["cvd_slope"], r["price_vs_va"]),
        [r for r in out if r["verdict"] == "SETUP_FORMING"])
    print("\n== base rate from cache: top-candidate direction by proof (all %d rows)" % nrows)
    for pr in range(0, 7):
        print("  proof %d: long=%d short=%d none=%d" % (pr, base[(pr, "long")], base[(pr, "short")], base[(pr, "")]))


if __name__ == "__main__":
    main()
