"""Tests for liq_rates.js (run through node). Rows are injected so the tests hold whether or not data was measured."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

JS = Path(__file__).resolve().parent / "liq_rates.js"
ROWS = [
    {"win": "1m", "side": "long", "bucket": "250k-1M", "lo": 250000, "hi": 1000000, "n": 40, "cont5": 0.5, "cont15": 0.55, "cont60": 0.6, "med15": -0.05},
    {"win": "1m", "side": "long", "bucket": "1M-5M", "lo": 1000000, "hi": 5000000, "n": 12, "cont5": 0.4, "cont15": 0.3, "cont60": 0.2, "med15": 0.1},
    {"win": "2m", "side": "short", "bucket": "5M+", "lo": 5000000, "hi": 1e12, "n": 3, "cont5": 1.0, "cont15": 0.0, "cont60": 0.5, "med15": 0.2},
]
INJECT = """
const L = require(process.argv[1]);
const q = JSON.parse(require('fs').readFileSync(0, 'utf8'));
L.rows = q.rows;
console.log(JSON.stringify(q.calls.map(c => L.read(c[0], c[1], c[2]))));
"""
SHIPPED = "const L=require(process.argv[1]);console.log(JSON.stringify({rows:L.rows,note:L.note,r:L.read('9m','long',1e9)}))"


def node():
    n = shutil.which("node")
    if not n:
        pytest.skip("node not installed")
    return n


def run(calls):
    out = subprocess.run([node(), "-e", INJECT, str(JS)], input=json.dumps({"rows": ROWS, "calls": calls}),
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_picks_right_bucket():
    r = run([["1m", "long", 250000], ["1m", "long", 999999], ["1m", "long", 1000000], ["2m", "short", 9e6]])
    assert [x["bucket"] if x else None for x in r] == ["250k-1M", "250k-1M", "1M-5M", "5M+"]


def test_null_cases():
    assert run([["1m", "long", 249999], ["3m", "long", 2e6], ["1m", "short", 2e6], ["2m", "long", 2e6]]) == [None] * 4


def test_shipped_file_rows_valid():
    res = subprocess.run([node(), "-e", SHIPPED, str(JS)], capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, res.stderr
    d = json.loads(res.stdout)
    assert d["r"] is None
    if not d["rows"]:
        assert d["note"].startswith("not measured")
    for row in d["rows"]:
        assert row["n"] >= 1
        for k in ("cont5", "cont15", "cont60"):
            assert row[k] is None or 0 <= row[k] <= 1


def test_fixture_rows_in_range():
    for row in ROWS:
        assert row["n"] > 0 and all(0 <= row[k] <= 1 for k in ("cont5", "cont15", "cont60"))
