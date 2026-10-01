"""test_proof_direction.py - proof-direction check (BUG-008 block) in
math_object_builder.build_math_object. This block decides "aligned" vs
"contradiction", which the verdict ladder uses to cap SETUP_FORMING at WATCH.

Adopted from research/core_readiness_2026-09-27/harness/proof_direction_cases.py
(task A1 of CORE_READINESS_PLAN.md). That file is the harness's read-only,
zero-dependency copy used by core_check.ps1; this file is the same cases
wired into the standing pytest suite so they run on every normal test pass.
Keep both in sync if the rules change; the harness copy is the one the
standing STATUS line depends on.

Rules pinned (current code, not Tom-cited - [SYSTEM] per BUG-008):
  short contradicts on: finished_auction.direction == "sell" | book_imbalance > 3.0 | last_3_delta all "positive"
  long  contradicts on: finished_auction.direction == "buy"  | book_imbalance < 0.33 | last_3_delta all "negative"
  bool book_imbalance is ignored; missing proof -> aligned; no candidates -> key absent.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "runtime"))
sys.dont_write_bytecode = True

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
    ("long_fa_buy",            snap("long", fa="buy"),                        "contradiction", "finished_auction=BUY"),
    ("long_book_0.32",         snap("long", book=0.32),                        "contradiction", "ask-heavy"),
    ("long_book_0.33_edge",    snap("long", book=0.33),                        "aligned", None),
    ("long_book_0.0_nodata",   snap("long", book=0.0),                         "aligned", None),  # 0.0 = no data, fix 2026-10-02 (dsa_task_012_setup_candidates.md:514)
    ("long_last3_neg",         snap("long", last3=["negative"] * 3),           "contradiction", "last_3_delta=neg"),
    ("long_book_bool_ignored", snap("long", book=True),                        "aligned", None),
    ("long_two_reasons",       snap("long", fa="buy", book=0.1),               "contradiction", "ask-heavy"),
]


def test_proof_direction_cases():
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
