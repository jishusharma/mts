"""Spec tests for live_aid analyst and verdict board functions (REQUIREMENTS.md R13 and R14).

Functions tested:
  - rosterRead(roster, rows, rejected, now)
  - analystVote(read)
  - levelWatch(levels, px)
  - zones(watch, px)
  - lean(votes)
  - actions(ln, zs, pulse)

Node-backed spec tests execute live_aid_indicators.js directly through node.
Supports LIVE_AID_JS_PATH env var to verify scratch mutations against copies.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import pytest

HERE = Path(__file__).resolve().parent
DEFAULT_JS = HERE / "live_aid_indicators.js"


def get_js_path():
    override = os.environ.get("LIVE_AID_JS_PATH")
    if override:
        return Path(override)
    return DEFAULT_JS


def run_js_calls(calls, js_path=None):
    """Execute a list of function calls against the JS file via node.
    Each call is a dict: {'fn': '<name>', 'args': [<arg1>, ...]}
    Returns list of return values.
    """
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed or not on PATH")

    target = js_path or get_js_path()
    assert target.exists(), f"Target JS file not found: {target}"

    runner_js = r"""
const fs = require('fs');
const jsCode = fs.readFileSync(process.argv[1], 'utf8');
const m = {exports: {}};
new Function('module', 'exports', jsCode)(m, m.exports);
const api = m.exports;

const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const results = payload.map(call => {
    const fn = api[call.fn];
    if (typeof fn !== 'function') {
        throw new Error('Function not found: ' + call.fn);
    }
    return fn.apply(null, call.args || []);
});
process.stdout.write(JSON.stringify(results));
"""
    proc = subprocess.run(
        [node, "-e", runner_js, str(target)],
        input=json.dumps(calls),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Node execution failed (code {proc.returncode}):\n{proc.stderr}")
    return json.loads(proc.stdout)


def call_js(fn, *args, js_path=None):
    return run_js_calls([{"fn": fn, "args": list(args)}], js_path=js_path)[0]


def test_roster_read_states_and_freshness():
    """rosterRead assigns states FRESH (<=3d), STALE (>3d), NOT_FETCHED, NO_ROW, and OFF."""
    # Base timestamp: 2026-11-03T12:00:00Z
    now = 1793707200000  # Date.parse('2026-11-03T12:00:00Z')

    roster = [
        {"short": "Alpha", "channel": "AlphaCh", "enabled": True, "ingested": True},
        {"short": "Beta", "channel": "BetaCh", "enabled": True, "ingested": True},
        {"short": "Gamma", "channel": "GammaCh", "enabled": True, "ingested": False},
        {"short": "Delta", "channel": "DeltaCh", "enabled": True, "ingested": True},
        {"short": "Epsilon", "channel": "EpsCh", "enabled": False, "ingested": True},
        {"short": "Zeta", "channel": "ZetaCh", "enabled": True, "ingested": True},
    ]

    rows = [
        # Alpha: published today (age 0d <= 3d) -> FRESH
        {"analyst": "Alpha", "published": "2026-11-03", "bias": "BULLISH"},
        # Zeta: published exactly 3 days ago (2026-10-31, age 3d == freshDays 3) -> FRESH
        {"analyst": "Zeta", "published": "2026-10-31", "bias": "NEUTRAL"},
        # Beta: published 4 days ago (2026-10-30, age 4d > 3d) -> STALE
        {"analyst": "Beta", "published": "2026-10-30", "bias": "BEARISH"},
        # Beta older row that should not be picked as newest
        {"analyst": "Beta", "published": "2026-10-25", "bias": "NEUTRAL"},
    ]

    rejected = [
        {"analyst": "Alpha"},
        {"analyst": "Alpha"},
        {"analyst": "Beta"},
    ]

    res = call_js("rosterRead", roster, rows, rejected, now)
    assert len(res) == 6

    by_short = {r["short"]: r for r in res}

    # Alpha: FRESH, age 0, 1 row, 2 rejected
    assert by_short["Alpha"]["state"] == "FRESH"
    assert by_short["Alpha"]["ageDays"] == 0
    assert by_short["Alpha"]["bias"] == "BULLISH"
    assert by_short["Alpha"]["rows"] == 1
    assert by_short["Alpha"]["rejected"] == 2
    assert by_short["Alpha"]["last"] == "2026-11-03"

    # Zeta: FRESH at exact boundary age 3d <= freshDays (3)
    assert by_short["Zeta"]["state"] == "FRESH"
    assert by_short["Zeta"]["ageDays"] == 3
    assert by_short["Zeta"]["bias"] == "NEUTRAL"
    assert by_short["Zeta"]["rows"] == 1

    # Beta: STALE, age 4, 2 rows, 1 rejected, newest published chosen
    assert by_short["Beta"]["state"] == "STALE"
    assert by_short["Beta"]["ageDays"] == 4
    assert by_short["Beta"]["bias"] == "BEARISH"
    assert by_short["Beta"]["rows"] == 2
    assert by_short["Beta"]["rejected"] == 1
    assert by_short["Beta"]["last"] == "2026-10-30"

    # Gamma: no rows, ingested=false -> NOT_FETCHED
    assert by_short["Gamma"]["state"] == "NOT_FETCHED"
    assert by_short["Gamma"]["rows"] == 0
    assert by_short["Gamma"]["last"] == ""
    assert by_short["Gamma"]["ageDays"] is None

    # Delta: no rows, ingested=true -> NO_ROW
    assert by_short["Delta"]["state"] == "NO_ROW"
    assert by_short["Delta"]["rows"] == 0
    assert by_short["Delta"]["last"] == ""
    assert by_short["Delta"]["ageDays"] is None

    # Epsilon: enabled=false -> OFF
    assert by_short["Epsilon"]["state"] == "OFF"
    assert by_short["Epsilon"]["enabled"] is False


def test_roster_read_empty_and_no_levels():
    """rosterRead handles empty roster, analysts with no rows, and default values."""
    assert call_js("rosterRead", [], [], [], 1793707200000) == []
    assert call_js("rosterRead", None, None, None, 1793707200000) == []

    # Analyst in roster with no rows at all
    roster = [{"short": "Solo", "enabled": True}]
    res = call_js("rosterRead", roster, [], [], 1793707200000)
    assert len(res) == 1
    assert res[0]["short"] == "Solo"
    assert res[0]["channel"] == ""
    assert res[0]["inRoster"] is True
    assert res[0]["state"] == "NO_ROW"
    assert res[0]["rows"] == 0
    assert res[0]["rejected"] == 0


def test_analyst_vote_sentiment_and_tie():
    """analystVote nets FRESH biases and returns 1, -1, 0 (tie), or null (no fresh views)."""
    # 1. Clear Bullish net (+1)
    bull_read = [
        {"state": "FRESH", "bias": "BULLISH"},
        {"state": "FRESH", "bias": "NEUTRAL"},
        {"state": "STALE", "bias": "BEARISH"},  # ignored because STALE
    ]
    assert call_js("analystVote", bull_read) == 1

    # 2. Clear Bearish net (-1)
    bear_read = [
        {"state": "FRESH", "bias": "BEARISH"},
        {"state": "FRESH", "bias": "BEARISH"},
        {"state": "FRESH", "bias": "BULLISH"},
    ]
    assert call_js("analystVote", bear_read) == -1

    # 3. Exact tie vote (+1 and -1 sum to 0 -> Math.sign(0) == 0)
    tie_read = [
        {"state": "FRESH", "bias": "BULLISH"},
        {"state": "FRESH", "bias": "BEARISH"},
    ]
    assert call_js("analystVote", tie_read) == 0

    # 4. Neutral only (sum 0 -> 0)
    neutral_read = [{"state": "FRESH", "bias": "NEUTRAL"}]
    assert call_js("analystVote", neutral_read) == 0

    # 5. NO_VIEW or unlisted biases skipped
    no_view_read = [{"state": "FRESH", "bias": "NO_VIEW"}]
    assert call_js("analystVote", no_view_read) is None

    # 6. No fresh votes / empty read returns null
    assert call_js("analystVote", []) is None
    assert call_js("analystVote", None) is None
    assert call_js("analystVote", [{"state": "STALE", "bias": "BULLISH"}]) is None


def test_level_watch_price_exactly_at_level():
    """levelWatch handles price exactly at a level (distance 0.0, side 'above', zone 'AT')."""
    levels = [{"level": 80000.0, "analyst": "Krown", "published": "2026-11-03", "said": "pivot"}]
    px = 80000.0

    res = call_js("levelWatch", levels, px)
    assert len(res) == 1
    assert res[0]["level"] == 80000.0
    assert res[0]["dist"] == 0.0
    assert res[0]["side"] == "above"  # d >= 0 -> 'above'
    assert res[0]["zone"] == "AT"      # abs(d) <= 0.3 -> 'AT'
    assert res[0]["analyst"] == "Krown"


def test_level_watch_bands_and_thresholds():
    """levelWatch classifies zones (AT <= 0.3%, NEAR <= 1.5%, WATCH <= 6.0%) and drops >6%."""
    px = 1000.0

    levels = [
        {"level": 1002.0},   # +0.20% -> AT
        {"level": 1010.0},   # +1.00% -> NEAR
        {"level": 1050.0},   # +5.00% -> WATCH
        {"level": 1070.0},   # +7.00% -> outside band, dropped
        {"level": 998.0},    # -0.20% -> AT
        {"level": 990.0},    # -1.00% -> NEAR
        {"level": 950.0},    # -5.00% -> WATCH
        {"level": 930.0},    # -7.00% -> outside band, dropped
    ]

    res = call_js("levelWatch", levels, px)
    levels_returned = [r["level"] for r in res]

    # Dropped beyond 6%
    assert 1070.0 not in levels_returned
    assert 930.0 not in levels_returned
    assert len(res) == 6

    by_level = {r["level"]: r for r in res}
    assert by_level[1002.0]["zone"] == "AT"
    assert by_level[1002.0]["side"] == "above"
    assert by_level[998.0]["zone"] == "AT"
    assert by_level[998.0]["side"] == "below"

    assert by_level[1010.0]["zone"] == "NEAR"
    assert by_level[1010.0]["side"] == "above"
    assert by_level[990.0]["zone"] == "NEAR"
    assert by_level[990.0]["side"] == "below"

    assert by_level[1050.0]["zone"] == "WATCH"
    assert by_level[950.0]["zone"] == "WATCH"


def test_level_watch_filtering_and_sorting():
    """levelWatch filters expired/NaN levels, sorts nearest first, and handles invalid px."""
    px = 50000.0
    levels = [
        {"level": 51000.0},  # +2.0%
        {"level": 50100.0},  # +0.2%
        {"level": 49950.0},  # -0.1% (nearest)
        {"level": 49000.0},  # -2.0%
        {"level": 50050.0, "expired": True},      # expired -> must be filtered
        {"level": "invalid_string"},              # non-finite -> must be filtered
    ]

    res = call_js("levelWatch", levels, px)
    assert len(res) == 4
    # Nearest first: 49950 (0.1%), 50100 (0.2%), then 51000/49000 (2.0%)
    assert res[0]["level"] == 49950.0
    assert res[1]["level"] == 50100.0

    # Non-positive or invalid price returns empty list
    assert call_js("levelWatch", levels, 0) == []
    assert call_js("levelWatch", levels, -100) == []
    assert call_js("levelWatch", levels, None) == []


def test_zones_clustering_and_merge():
    """zones merges levels within AV.merge (0.25%) into single [lo..hi] zone."""
    px = 80000.0
    # 80100 and 80150: diff is 50 on 80100 = 0.0624% <= 0.25% -> merged
    # 80400: diff from 80150 is 250 on 80150 = 0.31% > 0.25% -> separate zone
    watch = [
        {"level": 80100.0},
        {"level": 80150.0},
        {"level": 80400.0},
    ]

    zs = call_js("zones", watch, px)
    assert len(zs) == 2

    # Nearest zone is [80100, 80150]
    z1 = next(z for z in zs if z["lo"] == 80100.0)
    assert z1["hi"] == 80150.0
    assert len(z1["items"]) == 2

    z2 = next(z for z in zs if z["lo"] == 80400.0)
    assert z2["hi"] == 80400.0
    assert len(z2["items"]) == 1


def test_zones_inside_and_distance_calculations():
    """zones marks price inside as side 'at' and dist 0; exterior zones compute distance to edge."""
    # Zone spanning 79900 to 80100
    watch = [{"level": 79900.0}, {"level": 80050.0}]

    # Case 1: px inside zone (80000 inside [79900, 80050])
    zs_inside = call_js("zones", watch, 80000.0)
    assert len(zs_inside) == 1
    z_in = zs_inside[0]
    assert z_in["dist"] == 0.0
    assert z_in["side"] == "at"
    assert z_in["zone"] == "AT"

    # Case 2: px below zone (px=79000, lo=79900)
    # dist = (lo / px - 1) * 100 > 0, side = 'above'
    zs_below = call_js("zones", watch, 79000.0)
    z_bel = zs_below[0]
    assert z_bel["side"] == "above"
    assert z_bel["dist"] > 0
    expected_d = (79900.0 / 79000.0 - 1.0) * 100.0
    assert abs(z_bel["dist"] - expected_d) < 1e-6

    # Case 3: px above zone (px=81000, hi=80050)
    # dist = (hi / px - 1) * 100 < 0, side = 'below'
    zs_above = call_js("zones", watch, 81000.0)
    z_ab = zs_above[0]
    assert z_ab["side"] == "below"
    assert z_ab["dist"] < 0
    expected_d = (80050.0 / 81000.0 - 1.0) * 100.0
    assert abs(z_ab["dist"] - expected_d) < 1e-6


def test_lean_thresholds_and_sample_size():
    """lean requires at least 3 valid votes and checks 2+ bull/bear and 2x majority."""
    # Less than 3 valid votes -> NOT ENOUGH DATA
    assert call_js("lean", [])["call"] == "NOT ENOUGH DATA"
    assert call_js("lean", [1, 1])["call"] == "NOT ENOUGH DATA"
    assert call_js("lean", [1, None, -1, None])["call"] == "NOT ENOUGH DATA"

    # Bullish lean: bull >= 2 and bull >= 2 * bear
    assert call_js("lean", [1, 1, 0])["call"] == "BULLISH LEAN"
    assert call_js("lean", [1, 1, -1])["call"] == "BULLISH LEAN"
    assert call_js("lean", [1, 1, 1, -1])["call"] == "BULLISH LEAN"

    # Bearish lean: bear >= 2 and bear >= 2 * bull
    assert call_js("lean", [-1, -1, 0])["call"] == "BEARISH LEAN"
    assert call_js("lean", [-1, -1, 1])["call"] == "BEARISH LEAN"
    assert call_js("lean", [-1, -1, -1, 1])["call"] == "BEARISH LEAN"

    # Mixed: 3+ votes but neither threshold met
    assert call_js("lean", [1, 1, -1, -1])["call"] == "MIXED"
    assert call_js("lean", [0, 0, 0])["call"] == "MIXED"
    assert call_js("lean", [1, -1, 0])["call"] == "MIXED"

    # Check output structure
    ln = call_js("lean", [1, 1, -1, None])
    assert ln["bull"] == 2
    assert ln["bear"] == 1
    assert ln["n"] == 3
    assert ln["total"] == 4
    assert ln["call"] == "BULLISH LEAN"


def test_actions_ordering_now_before_next_before_later():
    """actions enforces strict ranking NOW before NEXT before LATER."""
    zones_list = [
        {"zone": "WATCH", "side": "above", "lo": 85000, "hi": 85000},
        {"zone": "AT", "side": "at", "lo": 80000, "hi": 80000},
        {"zone": "NEAR", "side": "below", "lo": 79000, "hi": 79000},
        {"zone": "WATCH", "side": "below", "lo": 75000, "hi": 75000},
        {"zone": "NEAR", "side": "above", "lo": 81000, "hi": 81000},
    ]

    # Without news event
    acts = call_js("actions", {"call": "MIXED"}, zones_list, None)
    when_seq = [a["when"] for a in acts]
    assert when_seq[0] == "NOW"
    assert when_seq[1] in ("NEXT", "NEXT")
    assert when_seq[2] in ("NEXT", "NEXT")
    assert when_seq[3] in ("LATER", "LATER")
    assert when_seq[4] in ("LATER", "LATER")

    # With news EVENT: prepends news action with when='NOW'
    pulse = {"level": "EVENT", "n": 4}
    acts_event = call_js("actions", {"call": "MIXED"}, zones_list, pulse)
    assert acts_event[0]["when"] == "NOW"
    assert acts_event[0]["kind"] == "news"
    assert acts_event[0]["n"] == 4

    # Verify monotonic ranking order
    rank = {"NOW": 0, "NEXT": 1, "LATER": 2}
    ranks = [rank[a["when"]] for a in acts_event]
    assert ranks == sorted(ranks)


def test_actions_with_lean_direction():
    """actions sets withLean true when zone lies in the direction of the lean."""
    zones_list = [
        {"zone": "NEAR", "side": "above", "lo": 81000},
        {"zone": "NEAR", "side": "below", "lo": 79000},
        {"zone": "AT", "side": "at", "lo": 80000},
    ]

    # 1. Bullish lean -> side 'above' has withLean True, others False
    acts_bull = call_js("actions", {"call": "BULLISH LEAN"}, zones_list, None)
    by_side_bull = {a["w"]["side"]: a["withLean"] for a in acts_bull}
    assert by_side_bull["above"] is True
    assert by_side_bull["below"] is False
    assert by_side_bull["at"] is False

    # 2. Bearish lean -> side 'below' has withLean True, others False
    acts_bear = call_js("actions", {"call": "BEARISH LEAN"}, zones_list, None)
    by_side_bear = {a["w"]["side"]: a["withLean"] for a in acts_bear}
    assert by_side_bear["below"] is True
    assert by_side_bear["above"] is False
    assert by_side_bear["at"] is False

    # 3. Mixed lean -> all False
    acts_mixed = call_js("actions", {"call": "MIXED"}, zones_list, None)
    for a in acts_mixed:
        assert a["withLean"] is False


def test_analyst_verdict_edge_and_malformed():
    """Edge cases: empty, null, and non-array inputs for all analyst functions."""
    assert call_js("rosterRead", None, None, None, 0) == []
    assert call_js("analystVote", None) is None
    assert call_js("levelWatch", None, 50000) == []
    assert call_js("zones", None, 50000) == []
    assert call_js("actions", None, None, None) == []

    empty_lean = call_js("lean", None)
    assert empty_lean["call"] == "NOT ENOUGH DATA"
    assert empty_lean["bull"] == 0
    assert empty_lean["bear"] == 0
    assert empty_lean["n"] == 0
    assert empty_lean["total"] == 0
