"""Tests for the pooled count (cc_s3_pooled_count.py). Hand-built bars; expected numbers computed by hand."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cc_s3_pooled_count as P  # noqa: E402

DEV_END_MS = 1719792000000


def _bar(t):
    return {"t": t, "o": 1.0, "h": 1.0, "l": 1.0, "c": 1.0, "v": 1.0}


def test_pooled_is_btc_plus_eth_from_same_counter():
    # hand: 3 BTC fills + 5 ETH fills = 8
    assert P.pooled({"BTCUSDT": {"filled": 3}, "ETHUSDT": {"filled": 5}}) == 8


def test_dev_bars_cut_at_dev_end_and_count_refuses_late_bars():
    bars = [_bar(DEV_END_MS - 60000), _bar(DEV_END_MS), _bar(DEV_END_MS + 60000)]
    assert [b["t"] for b in P.dev_bars(bars)] == [DEV_END_MS - 60000]
    with pytest.raises(Exception):
        P.count_fills(bars, bars, 1.0, 0.1)  # bars >= 2024-07-01 must be refused before any count
