import sys
sys.dont_write_bytecode = True
"""
core_invariants.py - Tom core (Java SetupCandidatesBuilder) output invariants,
checked over every archived snapshot in runtime_data/snapshots.

Layer: L1 (Tom core, Java). Checks what SetupCandidatesBuilder wrote, not a
re-computation. Pure read. No network. No writes.

Each invariant is a numbered check with a BASELINE count of known violations
measured 2026-09-27 on 9,145 snapshots (2026-09-13 .. 2026-09-26). Result:
  PASS  - every check <= its baseline and no unknown check fired
  FAIL  - any check above baseline (regression) - prints examples
Counts below baseline are reported as IMPROVED (update the baseline on purpose).

Scope switch --since ISO restricts to snapshots at/after a code boundary.
Golden boundary for current Tom-core code: 2026-09-24T13:51:32Z (last
SetupCandidatesBuilder change, commit acca1d0; last pf_ zone seen 13:24:11Z).

Run from repo root:
  python MyTradingSys/research/core_readiness_2026-09-27/harness/core_invariants.py
  python .../core_invariants.py --since 2026-09-24T13:51:32Z
"""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest"))
from snapshots import iter_snapshots, parse_ts  # noqa: E402

# Spec constants. Source in brackets. Change only with the source.
FEE_RT = 0.001            # B070: 2 * taker 0.0005 (backtest/fees.py); FORMULAS.md section 17
NET_MIN = 2.0              # compiled_engine.md sec 6 row 4, sec 7 Min R:R 2:1 NET
GROSS_SANITY = 1.5         # compiled_engine.md sec 7 pre-filter
TRIGGER_READY_PCT = 0.1    # compiled_engine.md sec 2.6 two-tier table
TARGET_MIN_R, TARGET_MAX_R = 2.0, 3.5   # SetupCandidatesBuilder L147-148 [SYSTEM, B060] - not in compiled_engine.md
MIN_STOP_PCT = 0.001       # SetupCandidatesBuilder L46 [SYSTEM v1.3.3] - not in compiled_engine.md
CAPS = [("weekly_", 0.5), ("daily_", 0.4), ("4h_", 0.4), ("prior_day_", 0.4), ("pf_", 0.4),
        ("1h_swing_", 0.5), ("15m_swing_", 0.3), ("5m_swing_", 0.3), ("vwap_band", 0.2),
        ("fvg", 0.2), ("vwap", 0.2)]   # compiled_engine.md sec 2.6 table (prior_day_close: default 0.4)

# Baselines measured 2026-09-27 (full corpus / since golden boundary).
BASELINE_FULL = {
    "I01 net_rr != fee model (+-0.011)": 0,
    "I02 rr_sanity != (gross>=1.5)": 0,
    "I03 net_rr_sanity != (net>=2.0) beyond rounding": 0,
    "I04 SCB candidate geometry stop/entry/target misordered": 0,
    "I05 SCB gross_rr outside [2.0,3.5] (+-0.011)": 3063,   # all pre-B060 (ceiling landed 2026-09-21); 0 on current code
    "I06 SCB stop closer than 0.1% of zone": 0,
    "I07 tier inconsistent with distance_pct": 0,
    "I08 distance_pct > distance_cap": 0,
    "I09 distance_cap != spec table": 0,
    "I10 score.raw != min(95, 50+7*proof+bonus)": 0,
    "I11 ranks 1..3 not sorted by score.raw desc": 0,
    "I12 setup_candidates[0] is not rank 1 (extra/FVG candidate on top)": None,   # INFO until decision D3; 343 on 2026-09-27
    "I13 extra candidate with misordered geometry (rank>=10)": 116,
    "I14 fvg_* entry candidate emitted (compiled_engine sec 2: FVG is EXIT not entry)": None,   # INFO until decision D3; 3491 on 2026-09-27
    "I15 POC-zone candidate emitted (needs trend_unhealthy)": 0,
}
BASELINE_SINCE = {k: 0 for k in BASELINE_FULL}
BASELINE_SINCE.update({"I12 setup_candidates[0] is not rank 1 (extra/FVG candidate on top)": None,
                       "I14 fvg_* entry candidate emitted (compiled_engine sec 2: FVG is EXIT not entry)": None})
# After decision D3 lands (extra candidates moved out of setup_candidates), set I12 and I14
# to 0 in BASELINE_SINCE and move --since to the D3 deploy time.


def cap_for(ztype):
    for pre, c in CAPS:
        if ztype.startswith(pre):
            return c
    return 0.4


def check(snaps):
    hits = Counter(); ex = defaultdict(list)

    def hit(k, e):
        hits[k] += 1
        if len(ex[k]) < 3:
            ex[k].append(e)

    for p, s, t in snaps:
        cands = s.get("setup_candidates") or []
        if cands and cands[0].get("rank") != 1:
            hit("I12 setup_candidates[0] is not rank 1 (extra/FVG candidate on top)", p.name)
        scb = [c for c in cands if (c.get("rank") or 99) <= 3]
        for c in cands:
            m = c.get("math") or {}
            g, n = m.get("gross_rr"), m.get("net_rr")
            d = c.get("direction"); z = c.get("zone") or {}
            e, st, tg = z.get("price"), m.get("stop"), m.get("target")
            is_scb = (c.get("rank") or 99) <= 3
            if str(c.get("setup_type", "")).startswith("fvg_"):
                hit("I14 fvg_* entry candidate emitted (compiled_engine sec 2: FVG is EXIT not entry)", p.name)
            geom_ok = None
            if None not in (e, st, tg):
                geom_ok = (d == "long" and st < e < tg) or (d == "short" and tg < e < st)
            if not is_scb:
                if geom_ok is False:
                    hit("I13 extra candidate with misordered geometry (rank>=10)", (p.name, c.get("setup_type")))
                continue
            if "poc" in str(z.get("type", "")):
                hit("I15 POC-zone candidate emitted (needs trend_unhealthy)", p.name)
            if g is not None and n is not None:
                if None not in (e, st, tg) and e != st and abs(round((abs(tg - e) - FEE_RT * e) / (abs(e - st) + FEE_RT * e), 2) - n) > 0.011:
                    hit("I01 net_rr != fee model (+-0.011)", (p.name, g, n))
                if bool(m.get("rr_sanity")) != (g >= GROSS_SANITY):
                    hit("I02 rr_sanity != (gross>=1.5)", (p.name, g))
                # net_rr is rounded to 2 dp on output; sanity uses the unrounded value.
                if bool(m.get("net_rr_sanity")) != (n >= NET_MIN) and abs(n - NET_MIN) > 0.005:
                    hit("I03 net_rr_sanity != (net>=2.0) beyond rounding", (p.name, n))
                if not (TARGET_MIN_R - 0.011 <= g <= TARGET_MAX_R + 0.011):
                    hit("I05 SCB gross_rr outside [2.0,3.5] (+-0.011)", (p.name, g))
            if geom_ok is False:
                hit("I04 SCB candidate geometry stop/entry/target misordered", (p.name, d, st, e, tg))
            if None not in (e, st) and e and abs(e - st) / e < MIN_STOP_PCT - 1e-6:
                hit("I06 SCB stop closer than 0.1% of zone", (p.name, e, st))
            dp, cap, tier = m.get("distance_pct"), m.get("distance_cap"), m.get("tier")
            if dp is not None and tier is not None:
                exp = "trigger_ready" if dp <= TRIGGER_READY_PCT + 0.005 else "conditional"
                if tier != exp and abs(dp - TRIGGER_READY_PCT) > 0.005:
                    hit("I07 tier inconsistent with distance_pct", (p.name, dp, tier))
            if dp is not None and cap is not None and dp > cap + 0.005:
                hit("I08 distance_pct > distance_cap", (p.name, dp, cap))
            if cap is not None and abs(cap - cap_for(str(z.get("type", "")))) > 1e-9:
                hit("I09 distance_cap != spec table", (p.name, z.get("type"), cap))
            sc = c.get("score") or {}
            if sc.get("raw") is not None and sc.get("proof_count") is not None:
                exp_raw = min(95, 50 + 7 * sc["proof_count"] + (sc.get("confluence_bonus") or 0))
                if sc["raw"] != exp_raw:
                    hit("I10 score.raw != min(95, 50+7*proof+bonus)", (p.name, sc))
        raws = [((c.get("score") or {}).get("raw") or 0) for c in scb]
        if any(raws[i] < raws[i + 1] for i in range(len(raws) - 1)):
            hit("I11 ranks 1..3 not sorted by score.raw desc", p.name)
    return hits, ex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="ISO timestamp; only snapshots at/after it")
    a = ap.parse_args()
    snaps, stats = iter_snapshots()
    base = BASELINE_FULL
    if a.since:
        b = parse_ts(a.since)
        snaps = [x for x in snaps if x[2] >= b]
        base = BASELINE_SINCE
    print("load stats:", stats, "| checked snapshots:", len(snaps))
    hits, ex = check(snaps)
    fail = False
    for k, b in base.items():
        n = hits.get(k, 0)
        if b is None:
            print("  INFO     %-80s %6d" % (k, n)); continue
        tag = "OK" if n == b else ("IMPROVED" if n < b else "REGRESS")
        if n > b:
            fail = True
        print("  %-8s %-80s %6d (baseline %d)" % (tag, k, n, b))
        if n > b:
            for e in ex[k]:
                print("           e.g.", e)
    unknown = [k for k in hits if k not in base]
    for k in unknown:
        fail = True
        print("  UNKNOWN  %s %d" % (k, hits[k]))
    print("RESULT:", "FAIL" if fail else "PASS")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
