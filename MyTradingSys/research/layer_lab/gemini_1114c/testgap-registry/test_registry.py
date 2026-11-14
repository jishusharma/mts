"""Hand-computed unit tests for MyTradingSys/backtest/layers/promotion/registry.py.

Covers pure functions and file validation across normal, empty, and malformed inputs
via sys.path insert (no network):
- alert_source, entry_for_source, decision_for_source (longest-prefix & shadow precedence)
- grandfather_error (empty, valid, malformed date/structure)
- size_entry (normal contract multiple, bool/ceiling/inf/zero rejections)
- make_collection_only (non-mutating shadow_side preservation) and load_registry

Mutation check (broken scratch copy):
In `entry_for_source` (`registry.py:55`), mutating
`return max(hits, key=lambda e: len(e["setup_id"])) if hits else None`
to `return min(hits, key=lambda e: len(e["setup_id"])) if hits else None`
caused `test_normal_decision_and_longest_prefix` to fail
(`AssertionError: assert 'shadow' == 'testnet'`; 1 failed, 4 passed).
"""
import json
import sys
from pathlib import Path

import pytest

PROMO_DIR = Path(__file__).resolve().parents[4] / "backtest" / "layers" / "promotion"
if str(PROMO_DIR) not in sys.path:
    sys.path.insert(0, str(PROMO_DIR))

import registry as reg  # noqa: E402


def _entry(setup_id="layer:fabio:volume_fvg:", mode="shadow"):
    return {
        "setup_id": setup_id,
        "mode": mode,
        "manifest": "m.json",
        "promoted_at": "2026-11-14T00:00:00Z",
        "commit": "abc1234",
    }


def test_normal_decision_and_longest_prefix():
    # Hand-computed: "layer:fabio:volume_fvg:1h" matches both "layer:fabio:" (len 12)
    # and "layer:fabio:volume_fvg:" (len 23); longest prefix ("testnet") wins -> "trade".
    src = reg.alert_source({"layer": "fabio", "sub": "volume_fvg", "tf": "1h"})
    assert src == "layer:fabio:volume_fvg:1h"

    entries = [_entry("layer:fabio:", "shadow"), _entry("layer:fabio:volume_fvg:", "testnet")]
    grandfather = {"layer:fabio:": {"reason": "grandfathered", "review_by": "2026-12-01"}}

    assert reg.entry_for_source(src, entries)["mode"] == "testnet"
    assert reg.decision_for_source(src, entries, grandfather) == "trade"
    # Registry shadow entry overrides grandfathered prefix -> "shadow"
    assert reg.decision_for_source("layer:fabio:other:1h", entries, grandfather) == "shadow"
    # Unregistered and not grandfathered -> "unregistered"
    assert reg.decision_for_source("layer:rsi:div:5m", entries, grandfather) == "unregistered"


def test_empty_inputs():
    assert reg.grandfather_error({}) is None
    assert reg.entry_for_source("layer:fabio:volume_fvg:1h", []) is None
    assert reg.decision_for_source("layer:fabio:volume_fvg:1h", [], {}) == "unregistered"
    assert reg.alert_source({}) == "layer:None:None:None"


def test_malformed_grandfather_and_registry_error():
    err_date = reg.grandfather_error({"layer:x:": {"reason": "ok", "review_by": "2026-02-30"}})
    assert err_date == "pre_pipeline_sources[layer:x:]: review_by is not a date"
    assert reg.grandfather_error([]) == "pre_pipeline_sources is not an object"

    # Unreadable registry (entries=None), malformed grandfather, or non-str source -> "registry_error"
    assert reg.decision_for_source("layer:x:y:1h", None, {}) == "registry_error"
    assert reg.decision_for_source("layer:x:y:1h", [], {"layer:x:": {"reason": "ok", "review_by": "bad"}}) == "registry_error"
    assert reg.decision_for_source(123, [], {}) == "registry_error"


def test_size_entry_normal_and_malformed():
    # SOURCED Deribit contract multiple of 10 (registry.py:96); OURS default ceiling 10000 (registry.py:94)
    assert reg.size_entry({"size_usd": 100, "max_loss_usd": 25.5}) == (100, 25.5)

    bad_cases = [
        None,
        {"size_usd": True, "max_loss_usd": 10},       # bool is subclass of int, must fail
        {"size_usd": 15, "max_loss_usd": 10},         # not a multiple of 10
        {"size_usd": 10010, "max_loss_usd": 10},      # exceeds default ceiling 10000
        {"size_usd": 100, "max_loss_usd": 0},         # non-positive loss
        {"size_usd": 100, "max_loss_usd": float("inf")},
    ]
    for case in bad_cases:
        with pytest.raises(ValueError):
            reg.size_entry(case)


def test_make_collection_only_and_load_registry_malformed(tmp_path):
    orig = {"layer": "fabio", "sub": "volume_fvg", "tf": "1h", "side": "short"}
    out = reg.make_collection_only(orig, "shadow: layer:fabio:")
    assert out == {
        "layer": "fabio",
        "sub": "volume_fvg",
        "tf": "1h",
        "shadow_side": "short",
        "collection_only": True,
        "promotion_note": "shadow: layer:fabio:",
    }
    assert orig["side"] == "short" and "collection_only" not in orig

    ok_path = tmp_path / "ok.json"
    ok_path.write_text(json.dumps({"version": 1, "entries": []}), encoding="utf-8")
    assert reg.load_registry(ok_path) == ([], None)

    dup_path = tmp_path / "dup.json"
    dup_path.write_text(json.dumps({"version": 1, "entries": [_entry(), _entry()]}), encoding="utf-8")
    entries, err = reg.load_registry(dup_path)
    assert entries == []
    assert isinstance(err, str) and "duplicate setup_id" in err
