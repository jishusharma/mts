"""Hand-specified US-open bucket and rate-table contracts (study.py / RESULT.md)."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE / "live_aid_indicators.js"
RATES_JS = HERE / "us_open_rates.js"


def _node(js):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = "const A=require(process.argv[1]); let j=''; process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j); console.log(JSON.stringify(" + js + "))})"
    out = subprocess.run([node, "-e", runner, str(JS)], input="{}", capture_output=True,
                         text=True, timeout=30, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


# Hand expectations use px=100, so each level's fraction is its distance / 100.
@pytest.mark.parametrize("level,expected", [
    (100, None),  # equal-to-mark levels are omitted
    (100.2499, "0-0.25"), (100.25, "0.25-0.5"),
    (100.4999, "0.25-0.5"), (100.5, "0.5-1"),
    (100.9999, "0.5-1"), (101, "1-2"),
    (101.9999, "1-2"), (102, "2+"), (300, "2+"),
])
def test_us_open_bucket_edges(level, expected):
    result = _us_open(level, 100)
    assert (result["up"][0]["bucket"] if result["up"] else None) == expected


@pytest.mark.parametrize("level", [99.75, 99.5, 99, 98, 97, 0, -1])
def test_us_open_below_mark_uses_absolute_distance_and_down_side(level):
    result = _us_open(level, 100)
    assert result["up"] == []
    assert len(result["down"]) == 1
    distance = (100 - level) / 100
    expected = "0-0.25" if distance < 0.0025 else "0.25-0.5" if distance < 0.005 else "0.5-1" if distance < 0.01 else "1-2" if distance < 0.02 else "2+"
    assert result["down"][0]["bucket"] == expected


def _us_open(level, px, include_daily=True, rates=None):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    day = 1_800_000_000_000 - (1_800_000_000_000 % 86_400_000)
    payload = json.dumps({"day": day, "level": level, "px": px, "daily": ([[day-86400000,100,level,level,100,1]] if include_daily else [])})
    runner = "const A=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);const r=A.usOpen([],j.daily,j.day,j.day,j.px,j.rates);console.log(JSON.stringify(r))})"
    payload = json.loads(payload)
    payload["rates"] = rates or {}
    payload = json.dumps(payload)
    out = subprocess.run([node, "-e", runner, str(JS)], input=payload, capture_output=True,
                         text=True, timeout=30, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_empty_inputs_have_no_box_or_ladder():
    r = _us_open(101, 100, include_daily=False)
    assert r["box"] is None and r["or"] is None
    assert r["up"] == [] and r["down"] == [] and r["priorDays"] == 0


def test_malformed_level_is_omitted():
    r = _us_open("bad", 100)
    assert r["up"] == [] and r["down"] == []


@pytest.mark.xfail(strict=True, reason="scope-blocked defect: zero mark emits a non-finite ladder distance; see report")
def test_zero_mark_level_is_omitted():
    r = _us_open(101, 0)
    assert r["up"] == [] and r["down"] == []


def test_rates_table_counts_never_exceed_denominators():
    # The study records touch<=n; held<=number touched (nt). Validate every checked-in cell.
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    code = "const fs=require('fs'),vm=require('vm');let s={};vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),s);process.stdout.write(JSON.stringify(s.US_OPEN_RATES))"
    out = subprocess.run([node, "-e", code, str(RATES_JS)], capture_output=True, text=True, timeout=30, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    rates = json.loads(out.stdout)["rates"]
    assert len(rates) == 8
    expected_kind_sample_totals = {
        "dayH": 1230, "dayL": 1230, "pdh": 1015, "pdl": 1050,
        "d3h": 1085, "d3l": 1115, "d7h": 1141, "d7l": 1167,
    }
    for kind, buckets in rates.items():
        assert set(buckets) == {"0-0.25", "0.25-0.5", "0.5-1", "1-2", "2+"}, kind
        for bucket, row in buckets.items():
            assert 0 <= row["nt"] <= row["n"], (kind, bucket, row)
            assert 0 <= row["touch"] <= 100 and 0 <= row["held"] <= 100, (kind, bucket, row)
            assert (row["n"] == 0) == (row["touch"] is None), (kind, bucket, row)
            assert (row["nt"] == 0) == (row["held"] is None), (kind, bucket, row)
            if row["n"]:
                assert abs(row["touch"] - 100 * row["nt"] / row["n"]) <= 0.5, (kind, bucket, row)
        assert sum(row["n"] for row in buckets.values()) == expected_kind_sample_totals[kind], kind


def test_us_open_hides_rates_until_each_denominator_reaches_30():
    row = {"n": 29, "touch": 84, "nt": 30, "held": 53}
    rates = {kind: {"1-2": dict(row)} for kind in ("pdh", "pdl")}
    r = _us_open(101, 100, rates=rates)
    pdh = next(row for row in r["up"] if row["k"] == "pdh")
    assert (pdh["n"], pdh["touch"], pdh["nt"], pdh["held"]) == (29, None, 30, 53)

    row = {"n": 30, "touch": 84, "nt": 29, "held": 53}
    rates = {kind: {"1-2": dict(row)} for kind in ("pdh", "pdl")}
    r = _us_open(101, 100, rates=rates)
    pdh = next(row for row in r["up"] if row["k"] == "pdh")
    assert (pdh["n"], pdh["touch"], pdh["nt"], pdh["held"]) == (30, 84, 29, None)
