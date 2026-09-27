import sys
sys.dont_write_bytecode = True
"""
decision_matrices.py - historical effect of operator decisions D1, D3, D4
(CORE_READINESS_PLAN.md section 3), measured on archived snapshots with the
Python verdict port. Read-only. About 3 passes over the corpus.

  D1  revert floor/ceiling R:R suspension (hard stop always applies)
  D3  extra/FVG candidates removed from setup_candidates (ranks 1-3 only)
  D4  directional proof count: drop book/finished-auction signals that favour
      the other side, drop speed (crypto proxy). Rank-1 re-score, approximate:
      rank order is not recomputed.
Measured 2026-09-27 (9,175 snapshots):
  D1: SETUP_FORMING->WAIT_RR 158, WATCH->WAIT_RR 807, WAIT_PROOF->WAIT_RR 1195, WAIT_TRIGGER->WAIT_RR 893
  D3: WAIT_PROOF->NO_TRADE 174, WAIT_TRIGGER->NO_TRADE 114, WAIT_RR->NO_TRADE 59
  D4: SETUP_FORMING->WATCH 198, WATCH->WAIT_PROOF 521, WAIT_RR->WAIT_PROOF 110
  D1+D4 fate of the 260 SETUP_FORMING: WAIT_RR 158, WATCH 79, SETUP_FORMING 23
"""
import copy
from collections import Counter
import _common  # noqa: F401
from snapshots import iter_snapshots  # noqa: E402
import verdict as V  # noqa: E402


def g(o, k):
    return o.get(k) if isinstance(o, dict) else None


def no_suspend(s):
    s2 = copy.deepcopy(s)
    s2["daily_vp"] = dict(s2.get("daily_vp") or {}, val=0, vah=0)   # mode inputs only
    for tf in ("1h", "15m"):
        st = (s2.get("structure") or {}).get(tf)
        if isinstance(st, dict):
            st["swing_low"] = 0; st["swing_high"] = 0
    return s2


def directional(s):
    c = s.get("setup_candidates") or []
    if not c or c[0].get("rank") != 1:
        return s, 0
    s3 = copy.deepcopy(s); top = s3["setup_candidates"][0]
    pr = top.get("proof") or {}; d = top.get("direction"); drop = 0
    bi = pr.get("book_imbalance"); fa = pr.get("finished_auction")
    if isinstance(bi, (int, float)) and not isinstance(bi, bool) and bi != 0 and ((d == "long" and bi < 0.67) or (d == "short" and bi > 1.5)):
        drop += 1
    if g(fa, "detected") and ((d == "long" and g(fa, "direction") == "buy") or (d == "short" and g(fa, "direction") == "sell")):
        drop += 1
    if g(pr.get("speed"), "picking_up"):
        drop += 1
    top.setdefault("score", {})["proof_count"] = (top["score"].get("proof_count") or 0) - drop
    return s3, drop


def main():
    snaps, stats = iter_snapshots()
    print("load stats:", stats)
    m1, m3, m3b, both = Counter(), Counter(), Counter(), Counter()
    for p, s, t in snaps:
        pd = V.proof_dir_of(s)
        base = V.compute_verdict(s, pd)["verdict"]
        v1 = V.compute_verdict(no_suspend(s), pd)["verdict"]
        if v1 != base: m1["%s->%s" % (base, v1)] += 1
        s3, drop = directional(s)
        if drop:
            v4 = V.compute_verdict(s3, pd)["verdict"]
            if v4 != base: m3["%s->%s" % (base, v4)] += 1
        c = s.get("setup_candidates") or []
        if c and c[0].get("rank") != 1:
            s2 = dict(s); s2["setup_candidates"] = [x for x in c if (x.get("rank") or 99) <= 3]
            v2 = V.compute_verdict(s2, V.proof_dir_of(s2))["verdict"]
            if v2 != base: m3b["%s->%s" % (base, v2)] += 1
        if base == "SETUP_FORMING":
            both[V.compute_verdict(no_suspend(s3), pd)["verdict"]] += 1
    print("D1", dict(m1.most_common())); print("D3", dict(m3b.most_common()))
    print("D4", dict(m3.most_common())); print("D1+D4 fate of SETUP_FORMING", dict(both))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
