"""Live Aid setup board core (setup_board.js, card live-aid-board-core-1111): LONG and SHORT evidence lists from existing layer
outputs; strength = count of live items (no weight). Hand-built input, expected lists written by hand. Skips (never fails) without node.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

MOD = Path(__file__).resolve().parent / "setup_board.js"


def _board(inp):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = ("const B=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{"
              "console.log(JSON.stringify(B.board(JSON.parse(j))))})")
    out = subprocess.run([node, "-e", runner, str(MOD)], input=json.dumps(inp), capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert out.returncode == 0, out.stderr[-1500:]
    return json.loads(out.stdout)


def test_module_exists():
    assert MOD.exists()


def test_two_long_one_short():
    inp = {"15m": {"div": {"rsi": 1, "wt": 0, "cvd": None}, "sweep": 1},
           "1h": {"bb": {"out": 1, "cvd": "spike"}}}
    r = _board(inp)
    assert r["long"] == [{"layer": "rsi_div", "tf": "15m", "side": "long"}, {"layer": "sweep", "tf": "15m", "side": "long"}]
    assert r["short"] == [{"layer": "bb_cvd", "tf": "1h", "side": "short"}]
    assert r["strength"] == {"long": 2, "short": 1}


def test_all_layers_and_sides():
    inp = {"4h": {"div": {"rsi": -1, "wt": -1, "cvd": -1}, "absorb": -1, "vfi": {"v": 1}, "sqz": {"rel": 0, "v": -1},
                  "adx": {"v": 1}, "va": "below", "bb": {"out": -1, "cvd": "dip"}}}
    r = _board(inp)
    assert [i["layer"] for i in r["short"]] == ["rsi_div", "wt_div", "cvd_div", "absorb", "sqz_release"]
    assert [i["layer"] for i in r["long"]] == ["bb_cvd", "vfi", "adx_di", "value_area"]
    assert r["strength"] == {"long": 4, "short": 5}


def test_not_live_items_are_skipped():
    inp = {"15m": {"sqz": {"rel": -1, "v": 1}, "adx": {"v": 0}, "vfi": {"v": null_}, "va": "inside", "bb": {"out": 1, "cvd": "dip"}}} if False else \
          {"15m": {"sqz": {"rel": -1, "v": 1}, "adx": {"v": 0}, "vfi": {"v": None}, "va": "inside", "bb": {"out": 1, "cvd": "dip"}}}
    assert _board(inp) == {"long": [], "short": [], "strength": {"long": 0, "short": 0}}


def test_empty_input():
    for e in ({}, None):
        assert _board(e) == {"long": [], "short": [], "strength": {"long": 0, "short": 0}}
