"""test_book_imbalance_nodata.py - book_imbalance 0.0 is "no order-book data", not "ask-heavy vs LONG".

Block under test: the BUG-008 proof-direction check in math_object_builder.build_math_object
(runtime/math_object_builder.py, the `_book` reads near :399-413 in the pre-fix file).

Definitions the expected values come from (never from the code under test):
  - 0.0 means "no order-book data": MyTradingSys/market_data/dsa_task_012_setup_candidates.md:514
    ("`book_imbalance = 0.0` means **no order-book data** ... Counting 'no data' as a directional proof signal is
    logically wrong") and :44 ("Exclude 0.0 / no-data from proof_count").
  - The Java side skips 0.0 the same way: src/main/java/datafeed/SetupCandidatesBuilder.java:581
    (`if (bookImbalance != 0.0)`); a failed depth fetch or an empty ask side yields 0.0:
    src/main/java/datafeed/MarketDataSnapshot.java:213-214.
  - Operator approval of the fix (2026-09-30 22:30 UTC, item 1, "treat 0.0 or missing depth as unknown (no
    contradiction either side)"): MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_INBOX.md:14-15.
  - Thresholds that stay as they are (ask-heavy vs LONG: < 0.33; bid-heavy vs SHORT: > 3.0): pinned in
    MyTradingSys/tests/test_proof_direction.py:13-15 (rule table) and MyTradingSys/runtime/live_session_journal.md:550
    (B024 "book_imbalance threshold 0.4/1.5 -> 0.33/3.0"). Boundary 0.33 is NOT ask-heavy (strict <).
  - Expected status/detail strings follow the same table.

Fails on the pre-fix code: test_long_book_0_0_is_no_data (and its int-0 twin).
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "runtime"))
sys.dont_write_bytecode = True

from math_object_builder import build_math_object  # noqa: E402

_ABSENT = object()

BASE = {"current_price": 80000.0, "daily_vp": {"poc": 80000, "vah": 80400, "val": 79600},
        "structure": {"1h": {"swing_high": 80500, "swing_low": 79500}, "15m": {"swing_high": 80200, "swing_low": 79800}},
        "conditions": {}, "cvd": {"last_3_delta": ["positive", "negative", "positive"]}}


def snap(direction, book=_ABSENT):
    """Top candidate with no other contradiction source: finished_auction direction empty, last_3_delta mixed."""
    s = copy.deepcopy(BASE)
    proof = {"finished_auction": {"direction": ""}}
    if book is not _ABSENT:
        proof["book_imbalance"] = book
    s["setup_candidates"] = [{"rank": 1, "direction": direction, "setup_type": "ct_" + direction,
                              "zone": {"name": "daily_val", "price": 79600, "type": "daily_val"},
                              "math": {"net_rr_sanity": True},
                              "proof": proof}]
    return s


def _run(direction, book=_ABSENT):
    mo = build_math_object(snap(direction, book))
    return mo.get("proof_direction_status"), list(mo.get("proof_direction_details") or [])


def _has(details, needle):
    return any(needle in d for d in details)


# ---- LONG ----------------------------------------------------------------------------------------------------

def test_long_book_0_0_is_no_data():
    status, details = _run("long", 0.0)
    assert not _has(details, "ask-heavy"), details
    assert status == "aligned", (status, details)


def test_long_book_int_0_is_no_data():
    status, details = _run("long", 0)
    assert not _has(details, "ask-heavy"), details
    assert status == "aligned", (status, details)


def test_long_book_0_2_still_ask_heavy():
    status, details = _run("long", 0.2)
    assert status == "contradiction", (status, details)
    assert _has(details, "ask-heavy vs LONG"), details


def test_long_book_0_01_still_ask_heavy():
    # smallest realistic non-zero ratio after Java's 2-decimal rounding (MarketDataSnapshot.java:315)
    status, details = _run("long", 0.01)
    assert status == "contradiction", (status, details)
    assert _has(details, "ask-heavy vs LONG"), details


def test_long_book_0_33_boundary_not_ask_heavy():
    status, details = _run("long", 0.33)
    assert status == "aligned", (status, details)
    assert not _has(details, "ask-heavy"), details


def test_long_book_key_absent_is_no_data():
    status, details = _run("long")
    assert status == "aligned", (status, details)
    assert not _has(details, "book_imbalance"), details


def test_long_book_none_is_no_data():
    status, details = _run("long", None)
    assert status == "aligned", (status, details)
    assert not _has(details, "book_imbalance"), details


# ---- SHORT ---------------------------------------------------------------------------------------------------

def test_short_book_0_0_no_book_contradiction():
    status, details = _run("short", 0.0)
    assert not _has(details, "bid-heavy"), details
    assert not _has(details, "book_imbalance"), details
    assert status == "aligned", (status, details)


def test_short_book_3_5_still_bid_heavy():
    status, details = _run("short", 3.5)
    assert status == "contradiction", (status, details)
    assert _has(details, "bid-heavy vs SHORT"), details


def test_short_book_3_0_boundary_not_bid_heavy():
    status, details = _run("short", 3.0)
    assert status == "aligned", (status, details)
    assert not _has(details, "bid-heavy"), details


# ---- other contradiction sources keep working when the book is no-data ---------------------------------------

def test_long_book_0_0_other_reasons_still_fire():
    s = snap("long", 0.0)
    s["setup_candidates"][0]["proof"]["finished_auction"]["direction"] = "buy"
    mo = build_math_object(s)
    details = list(mo.get("proof_direction_details") or [])
    assert mo.get("proof_direction_status") == "contradiction", mo.get("proof_direction_status")
    assert _has(details, "finished_auction=BUY vs LONG"), details
    assert not _has(details, "ask-heavy"), details
