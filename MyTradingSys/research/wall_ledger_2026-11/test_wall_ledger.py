"""Hand-derived fixtures for the wall ledger (written from the rule before the module).

Rule: placed = a grid cell over threshold for `persist` consecutive snapshots;
pulled = gone without trade volume in the cell; filled = gone with trade volume
in the cell; touched = best bid/ask or a trade inside the cell while it rested.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))
import wall_ledger as wl  # noqa: E402


def snap(ts, bids=None, asks=None, trades=None):
    return {"ts": ts, "bids": bids or {}, "asks": asks or {}, "trades": trades or []}


# Base book: mid 100,000; 20 BTC at 99,500 = 1.99M USD (over 1.5M); 30 BTC at 101,000 = 3.03M.
BASE_BIDS = {99_990.0: 1.0, 99_500.0: 20.0}
BASE_ASKS = {100_010.0: 1.0, 101_000.0: 30.0}


def test_bucket_floors_to_10_usd_grid():
    assert wl.bucket(99_507.5, 10) == 99_500.0
    assert wl.bucket(99_500.0, 10) == 99_500.0
    assert wl.bucket(99_499.99, 10) == 99_490.0


def test_cell_usd_sums_levels_inside_one_cell():
    # 10 BTC at 99,501 + 10 BTC at 99,509 = 995,010 + 995,090 = 1,990,100 USD in cell 99,500
    cells = wl.cell_usd({99_501.0: 10.0, 99_509.0: 10.0}, 10)
    assert cells[99_500.0] == pytest.approx(1_990_100.0)


def test_candidates_apply_threshold():
    c = wl.candidates(snap(0, BASE_BIDS, BASE_ASKS), 1_500_000, 10)
    assert set(c) == {("bid", 99_500.0), ("ask", 101_000.0)}


def test_threshold_is_inclusive():
    # 15 BTC at 100,000 = exactly 1.5M
    c = wl.candidates(snap(0, {}, {100_000.0: 15.0}), 1_500_000, 10)
    assert ("ask", 100_000.0) in c


def test_wall_must_persist_to_be_placed():
    snaps = [snap(0, BASE_BIDS, BASE_ASKS), snap(1, BASE_BIDS, BASE_ASKS)]
    assert wl.build_ledger(snaps, persist=3) == []


def test_flicker_that_vanishes_before_persisting_is_not_a_row():
    gone = {99_990.0: 1.0}
    snaps = [snap(0, BASE_BIDS, {100_010.0: 1.0}), snap(1, BASE_BIDS, {100_010.0: 1.0}),
             snap(2, gone, {100_010.0: 1.0})]
    assert wl.build_ledger(snaps, persist=3) == []


def test_placed_wall_open_with_distance_and_age():
    snaps = [snap(t, BASE_BIDS, BASE_ASKS) for t in (0, 5, 10, 20)]
    rows = {(r["side"], r["level"]): r for r in wl.build_ledger(snaps, persist=3)}
    bid = rows[("bid", 99_500.0)]
    assert bid["outcome"] == "open"
    assert bid["placed_ts"] == 0
    assert bid["age_s"] == 20
    # mid 100,000; (99,500 - 100,000) / 100,000 = -0.5 %
    assert bid["distance_pct"] == pytest.approx(-0.5)
    assert rows[("ask", 101_000.0)]["distance_pct"] == pytest.approx(1.0)


def test_pulled_without_trades_and_untouched():
    gone = {99_990.0: 1.0}
    snaps = [snap(t, BASE_BIDS, BASE_ASKS) for t in (0, 1, 2)] + [snap(3, gone, BASE_ASKS)]
    rows = {(r["side"], r["level"]): r for r in wl.build_ledger(snaps, persist=3)}
    bid = rows[("bid", 99_500.0)]
    assert bid["outcome"] == "pulled"
    assert bid["end_ts"] == 3
    assert bid["age_s"] == 3
    assert bid["touched"] is False


def test_filled_when_trade_volume_in_cell_on_vanish():
    gone = {99_990.0: 1.0}
    snaps = [snap(t, BASE_BIDS, BASE_ASKS) for t in (0, 1, 2)]
    snaps.append(snap(3, gone, BASE_ASKS, trades=[(99_505.0, 20.0)]))
    rows = {(r["side"], r["level"]): r for r in wl.build_ledger(snaps, persist=3)}
    assert rows[("bid", 99_500.0)]["outcome"] == "filled"
    assert rows[("bid", 99_500.0)]["touched"] is True


def test_trade_outside_cell_does_not_fill():
    gone = {99_990.0: 1.0}
    snaps = [snap(t, BASE_BIDS, BASE_ASKS) for t in (0, 1, 2)]
    snaps.append(snap(3, gone, BASE_ASKS, trades=[(99_510.0, 5.0)]))  # next cell up
    rows = {(r["side"], r["level"]): r for r in wl.build_ledger(snaps, persist=3)}
    assert rows[("bid", 99_500.0)]["outcome"] == "pulled"


def test_touched_by_best_price_then_pulled_is_not_before_touch():
    # best bid moves into the wall cell at t=3, wall pulled at t=4 with no trades in it
    near = {99_505.0: 1.0, 99_500.0: 20.0}
    gone = {99_505.0: 1.0}
    snaps = [snap(t, BASE_BIDS, BASE_ASKS) for t in (0, 1, 2)]
    snaps += [snap(3, near, {99_515.0: 1.0, 101_000.0: 30.0}), snap(4, gone, {99_515.0: 1.0, 101_000.0: 30.0})]
    rows = {(r["side"], r["level"]): r for r in wl.build_ledger(snaps, persist=3)}
    bid = rows[("bid", 99_500.0)]
    assert bid["outcome"] == "pulled"
    assert bid["touched"] is True


def test_dip_below_threshold_closes_the_wall_and_replace_is_new_row():
    small = {99_990.0: 1.0, 99_500.0: 5.0}
    snaps = [snap(t, BASE_BIDS, BASE_ASKS) for t in (0, 1, 2)]
    snaps.append(snap(3, small, BASE_ASKS))
    snaps += [snap(t, BASE_BIDS, BASE_ASKS) for t in (4, 5, 6)]
    bids = [r for r in wl.build_ledger(snaps, persist=3) if r["side"] == "bid"]
    assert [r["outcome"] for r in bids] == ["pulled", "open"]
    assert bids[1]["placed_ts"] == 4


def test_pulled_before_touch_rate():
    rows = [
        {"outcome": "pulled", "touched": False},
        {"outcome": "pulled", "touched": False},
        {"outcome": "pulled", "touched": True},
        {"outcome": "filled", "touched": True},
        {"outcome": "open", "touched": False},
    ]
    s = wl.summary(rows)
    assert s == {"placed": 5, "open": 1, "pulled": 3, "filled": 1,
                 "pulled_before_touch": 2, "pulled_before_touch_rate": 0.5}


def test_rate_none_when_nothing_closed():
    assert wl.summary([])["pulled_before_touch_rate"] is None


def test_defaults_are_the_card_values():
    assert wl.THRESHOLD_USD == 1_500_000
    assert wl.GRID_USD == 10
