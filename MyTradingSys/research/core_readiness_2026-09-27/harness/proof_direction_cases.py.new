import sys
sys.dont_write_bytecode = True
"""
proof_direction_cases.py - table-driven cases for the proof-direction check in
math_object_builder.build_math_object (BUG-008 block, lines ~374-398 on
2026-09-27). This block decides "aligned" vs "contradiction", which the verdict
ladder uses to cap SETUP_FORMING at WATCH. It had zero unit tests on 2026-09-27.

Each case states the rule it pins. All cases PASS on current code: this file
freezes today's behaviour so the B071 fix and any D-decision change is visible.
To adopt: copy CASES + test_cases() into MyTradingSys/tests/test_proof_direction.py.

Rules pinned (current code, not Tom-cited - [SYSTEM] per BUG-008):
  short contradicts on: finished_auction.direction == "sell" | book_imbalance > 3.0 | last_3_delta all "positive"
  long  contradicts on: finished_auction.direction == "buy"  | book_imbalance < 0.33 | last_3_delta all "negative"
  bool book_imbalance is ignored; missing proof -> aligned; no candidates -> key absent.
finished_auction.direction names the EXHAUSTED side (SetupCandidatesBuilder L711-718:
an extreme-delta 1m bar whose next bar reverses without follow-through; "sell" =
sellers exhausted = bullish). So "sell contradicts SHORT" is semantically right.
Related defect, not pinned here: countSignals() (L551) adds +1 proof for ANY finished
auction, including one that favours the other side (see plan finding F7).
"""
import _common  # noqa: F401
from math_object_builder import build_math_object  # noqa: E402

BASE = {"current_price": 80000.0, "daily_vp": {"poc": 80000, "vah": 80400, "val": 79600},
        "structure": {"1h": {"swing_high": 80500, "swing_low": 79500}, "15m": {"swing_high": 80200, "swing_low": 79800}},
        "conditions": {}, "cvd": {"last_3_delta": ["positive", "negative", "positive"]}}


def snap(direction, fa="", book=1.0, last3=None):
    import copy
    s = copy.deepcopy(BASE)
    if last3 is not None:
        s["cvd"]["last_3_delta"] = last3
    s["setup_candidates"] = [{"rank": 1, "direction": direction, "setup_type": "ct_" + direction,
                              "zone": {"name": "daily_val", "price": 79600, "type": "daily_val"},
                              "math": {"net_rr_sanity": True},
                              "proof": {"finished_auction": {"direction": fa}, "book_imbalance": book}}]
    return s


CASES = [
    # id, snapshot, expected status, expected detail substring (or None)
    ("short_clean",            snap("short"),                                  "aligned", None),
    ("short_fa_sell",          snap("short", fa="sell"),                       "contradiction", "finished_auction=SELL"),
    ("short_fa_buy",           snap("short", fa="buy"),                        "aligned", None),
    ("short_book_3.01",        snap("short", book=3.01),                       "contradiction", "bid-heavy"),
    ("short_book_3.0_edge",    snap("short", book=3.0),                        "aligned", None),
    ("short_last3_pos",        snap("short", last3=["positive"] * 3),          "contradiction", "last_3_delta=pos"),
    ("long_clean",             snap("long"),                                   "aligned", None),
    ("long_fa_buy",            snap("long", fa="buy"),                         "contradiction", "finished_auction=BUY"),
    ("long_book_0.32",         snap("long", book=0.32),                        "contradiction", "ask-heavy"),
    ("long_book_0.33_edge",    snap("long", book=0.33),                        "aligned", None),
    ("long_book_0.0_nodata",   snap("long", book=0.0),                         "aligned", None),  # 0.0 = no data, fix 2026-10-02 (dsa_task_012_setup_candidates.md:514)
    ("long_last3_neg",         snap("long", last3=["negative"] * 3),           "contradiction", "last_3_delta=neg"),
    ("long_book_bool_ignored", snap("long", book=True),                        "aligned", None),
    ("long_two_reasons",       snap("long", fa="buy", book=0.1),               "contradiction", "ask-heavy"),
]


def test_cases():
    fails = []
    for cid, s, want, sub in CASES:
        mo = build_math_object(s)
        got = mo.get("proof_direction_status")
        det = "; ".join(mo.get("proof_direction_details") or [])
        if got != want or (sub and sub not in det):
            fails.append((cid, want, got, det))
    no_cands = build_math_object(dict(BASE))
    if "proof_direction_status" in no_cands:
        fails.append(("no_candidates_key_absent", "absent", no_cands.get("proof_direction_status"), ""))
    assert not fails, fails
    return len(CASES) + 1


if __name__ == "__main__":
    try:
        n = test_cases()
        print("RESULT: PASS (%d cases)" % n)
        raise SystemExit(0)
    except AssertionError as e:
        print("RESULT: FAIL", e)
        raise SystemExit(1)
