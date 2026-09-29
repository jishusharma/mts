import sys
sys.dont_write_bytecode = True
"""P1 (regenerated vs archived live snapshots). Usage: python p1_compare.py live_files.json regen.jsonl
Compares fields that derive from klines only; candidates by (rank, setup, dir, zone, stop, target); proof_count is
reported separately (live includes the book-imbalance proof, which the archive cannot regenerate)."""
import json
from collections import Counter


def g(o, *k):
    for x in k:
        if not isinstance(o, dict):
            return None
        o = o.get(x)
    return o


FIELDS = [("current_price",), ("daily_vp", "poc"), ("daily_vp", "vah"), ("daily_vp", "val"), ("weekly_vp", "poc"),
          ("weekly_vp", "vah"), ("weekly_vp", "val"), ("weekly_vp", "prior_week_poc"), ("intraday_4h_vp", "poc"),
          ("vwap", "price"), ("prior_day", "poc"), ("prior_day", "close"), ("prior_day", "high"), ("prior_day", "low"),
          ("structure", "15m", "swing_high"), ("structure", "15m", "swing_low"), ("structure", "1h", "swing_high"),
          ("structure", "1h", "swing_low"), ("structure", "5m", "swing_high"), ("structure", "5m", "swing_low"),
          ("trade_flow", "net_delta_1m"), ("trade_flow", "net_delta_5m"), ("trade_flow", "net_delta_15m"),
          ("trade_flow", "net_delta_1h"), ("conditions", "cvd_slope"), ("conditions", "vwap_slope"),
          ("conditions", "price_vs_va"), ("conditions", "fvg_unfilled_count"), ("conditions", "cvd_trade_flow_aligned")]


def close(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) <= 0.011 + 1e-9 * abs(a)
    return a == b


def cand_key(c):
    m = c.get("math") or {}
    return (c.get("rank"), c.get("setup_type"), c.get("direction"), g(c, "zone", "name"), m.get("stop"), m.get("target"))


def main(live_list, regen):
    live = json.load(open(live_list))
    rg = [json.loads(l) for l in open(regen, encoding="utf-8")]
    ok, tot, bad = Counter(), Counter(), Counter()
    cand_all = cand_top = pc_eq = pc_n = pc_eq_nobook = pc_n_nobook = 0
    for f, r in zip(live, rg):
        s = json.load(open(f, encoding="utf-8"))
        for fld in FIELDS:
            a, b = g(s, *fld), g(r, *fld)
            tot[".".join(fld)] += 1
            if close(a, b):
                ok[".".join(fld)] += 1
        ls = [c for c in s.get("setup_candidates", []) if c and (c.get("rank") or 99) <= 3]
        rs = [c for c in r.get("setup_candidates", []) if c and (c.get("rank") or 99) <= 3]
        cand_all += [cand_key(c) for c in ls] == [cand_key(c) for c in rs]
        cand_top += (cand_key(ls[0]) if ls else None) == (cand_key(rs[0]) if rs else None)
        for a, b in zip(ls, rs):
            if cand_key(a) == cand_key(b):
                pa, pb = g(a, "score", "proof_count"), g(b, "score", "proof_count")
                pc_n += 1; pc_eq += pa == pb
                if not g(a, "proof", "book_imbalance"):
                    pc_n_nobook += 1; pc_eq_nobook += pa == pb
    n = len(rg)
    print("pairs", n)
    for k in tot:
        print("  %-38s %d/%d" % (k, ok[k], tot[k]))
    print("top-3 candidate list identical (rank,setup,dir,zone,stop,target): %d/%d" % (cand_all, n))
    print("rank-1 candidate identical: %d/%d" % (cand_top, n))
    print("proof_count equal where candidate identical: %d/%d; where live book_imbalance==0: %d/%d" % (pc_eq, pc_n, pc_eq_nobook, pc_n_nobook))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
