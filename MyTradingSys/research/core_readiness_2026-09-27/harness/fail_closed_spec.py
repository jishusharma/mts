import sys
sys.dont_write_bytecode = True
"""
fail_closed_spec.py - executable specification for B071 (fail-open proof direction).

RED until B071 lands. It defines the fixed behaviour; it does not implement it.

Required behaviour after the fix (both PowerShell Compute-Verdict and the Python
port backtest/verdict.py, which must stay in parity):
  S1. proof_dir_of(snap, fail_closed=True) returns "error" when build_math_object
      raises, returns no proof_direction_status, or returns a value outside
      {"aligned", "contradiction"}.
  S2. compute_verdict(snap, "error") never returns WATCH or SETUP_FORMING.
      Those become WAIT_PROOF with reason "proof_dir error" (decision D6 default;
      operator may pick a different floor, the spec then changes here first).
  S3. compute_verdict(snap, "aligned") and (snap, "contradiction") are unchanged
      (verdict_golden.py shows NO CHANGE).
Measured 2026-09-27 on current code: S1 FAIL (no fail_closed parameter); S2 violated on
1,917 of 9,168 snapshots (1,202 WATCH + 715 SETUP_FORMING).
Satisfiability proven 2026-09-27 on a scratch copy: the reference patch in
CORE_READINESS_PLAN.md task C2 turns S1+S2 PASS and verdict_golden.py stays NO CHANGE.
"""
import json
from collections import Counter
import _common  # noqa: F401
from snapshots import iter_snapshots  # noqa: E402
import verdict as V  # noqa: E402


def main():
    snaps, stats = iter_snapshots()
    print("load stats:", stats)
    bad = Counter(); fails = []
    # S1 - broken snapshot must yield "error", not "aligned"
    try:
        # cvd: null makes build_math_object raise AttributeError (verified 2026-09-27)
        r = V.proof_dir_of({"current_price": 80000.0, "cvd": None,
                            "setup_candidates": [{"rank": 1, "direction": "long", "proof": {}}]}, fail_closed=True)
    except TypeError:
        r = "NO fail_closed PARAMETER"
    except Exception as e:
        r = "RAISED %s" % type(e).__name__
    s1 = (r == "error")
    print("S1 proof_dir_of(broken, fail_closed=True) ->", r, "|", "PASS" if s1 else "FAIL")
    # S2 - "error" must never reach WATCH / SETUP_FORMING
    for p, s, t in snaps:
        v = V.compute_verdict(s, "error")["verdict"]
        if v in ("WATCH", "SETUP_FORMING"):
            bad[v] += 1
    s2 = not bad
    print("S2 compute_verdict(snap,'error') in {WATCH,SETUP_FORMING}:", dict(bad) or 0, "|", "PASS" if s2 else "FAIL")
    print("S3 run verdict_golden.py separately: must print NO CHANGE")
    ok = s1 and s2
    print("RESULT:", "PASS" if ok else "FAIL (expected until B071 fix lands)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
