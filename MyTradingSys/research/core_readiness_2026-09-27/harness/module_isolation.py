import sys
sys.dont_write_bytecode = True
"""
module_isolation.py - proves which snapshot fields gate L2 (proof direction) and
L3 (verdict ladder). PROJECT_VISION doctrine: modules never gate core behaviour.

For each archived snapshot the named field group is deleted and L2+L3 are
recomputed. Expected: identical (verdict, proof_dir) for every snapshot.
Group A - module-only fields (session frame, funding, OI, liquidation, basis,
          order_flow, post-funding VP): must be IDENTICAL, 0 diffs.
Group B - fields consumed by the Java Tom core (L1) but not read by L2/L3
          directly: must also be IDENTICAL; a diff or an exception means L2/L3
          reach into L1 inputs (hidden coupling) or fail when they are absent.
Exceptions are counted separately: an exception inside proof_dir_of is exactly
the B071 fail-open path (defaults to "aligned").
"""
import copy
from collections import Counter
import _common  # noqa: F401
from snapshots import iter_snapshots  # noqa: E402
from verdict import compute_verdict  # noqa: E402
from math_object_builder import build_math_object  # noqa: E402

GROUP_A = ["session", "session_timing", "funding", "open_interest", "oi_breakdown",
           "liquidation_clusters", "spot_perp_basis", "order_flow", "post_funding_vp", "alignment_pass"]
GROUP_B = ["weekly_vp", "intraday_4h_vp", "vwap", "prior_day", "trade_flow", "order_book_depth"]
# "cvd" is NOT in group B: L2 reads cvd.last_3_delta directly (math_object_builder BUG-008 block).
# Removing it flips 1,044 proof_dir results contradiction->aligned (measured 2026-09-27).


def l2l3(s):
    try:
        mo = build_math_object(s)
        pd = mo.get("proof_direction_status") or "aligned"
        err = None
    except Exception as e:
        pd, err = "aligned", type(e).__name__
    return compute_verdict(s, pd)["verdict"], pd, err


def run(snaps, group):
    diffs = Counter(); errs = Counter()
    for p, s, t in snaps:
        base = l2l3(s)
        s2 = copy.deepcopy(s)
        for k in group:
            s2.pop(k, None)
        got = l2l3(s2)
        if got[2]:
            errs[got[2]] += 1
        if got[:2] != base[:2]:
            diffs["%s/%s->%s/%s" % (base[0], base[1], got[0], got[1])] += 1
    return diffs, errs


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", choices=["A", "B", "both"], default="both")
    a = ap.parse_args()
    snaps, stats = iter_snapshots()
    print("load stats:", stats)
    ok = True
    groups = [("A module-only", GROUP_A), ("B L1-inputs", GROUP_B)]
    if a.group != "both":
        groups = [g for g in groups if g[0].startswith(a.group)]
    for name, g in groups:
        d, e = run(snaps, g)
        print("group %s %s" % (name, g))
        print("   diffs:", dict(d) or 0, "| exceptions in L2:", dict(e) or 0)
        if d or e:
            ok = False
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
