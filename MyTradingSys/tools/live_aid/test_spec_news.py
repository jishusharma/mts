"""Spec tests for live_aid news functions (REQUIREMENTS.md R12).

Functions tested:
  - newsTags(title)
  - newsMerge(list, incoming, max)
  - newsPulse(items, now)
  - newsCoins(x)
  - newsRead(x)

Node-backed spec tests execute live_aid_indicators.js directly through node.
Supports LIVE_AID_JS_PATH env var to verify scratch mutations against copies.
"""
import json
import os
import shutil
from pathlib import Path
import pytest
import subprocess

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
// Expose newsCoins if not exported by default api
const wrappedCode = jsCode.replace('var api = {', 'var api = { newsCoins: newsCoins, ');
new Function('module', 'exports', wrappedCode)(m, m.exports);
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


def test_news_tags_keywords_and_case():
    """Verify word rules and multi-tagging in newsTags."""
    res = call_js("newsTags", "Major Bitcoin hack reported as hackers exploit bridge")
    assert "hack" in res
    assert "btc" in res

    # War and tariffs
    assert call_js("newsTags", "New tariffs announced amid missile strike") == ["war"]

    # ETF and fed
    res_macro = call_js("newsTags", "SEC reviews ETF filing following FOMC rate hike")
    assert "etf" in res_macro
    assert "fed" in res_macro

    # Delisting
    assert call_js("newsTags", "Exchange delists three tokens") == ["delist"]


def test_news_tags_edge_and_empty():
    """newsTags handles empty strings, null, and non-string gracefully."""
    assert call_js("newsTags", "") == []
    assert call_js("newsTags", None) == []
    assert call_js("newsTags", 12345) == []


def test_news_merge_dedup_and_sort():
    """newsMerge deduplicates by _id and sorts descending by time."""
    list_items = [
        {"_id": "1", "time": 100, "title": "First"},
        {"_id": "2", "time": 200, "title": "Second"},
    ]
    incoming = [
        {"_id": "2", "time": 200, "title": "Second Updated"},
        {"_id": "3", "time": 300, "title": "Third"},
    ]
    merged = call_js("newsMerge", list_items, incoming, 10)
    assert len(merged) == 3
    # Check descending order by time
    assert [x["_id"] for x in merged] == ["3", "2", "1"]
    # Incoming should be preserved on de-dup because incoming is concatenated first
    assert merged[1]["title"] == "Second Updated"


def test_news_merge_max_cap_and_malformed():
    """newsMerge enforces max slice and ignores items without _id."""
    incoming = [
        {"_id": "a", "time": 10},
        {"_id": "b", "time": 20},
        {"_id": "c", "time": 30},
        {"no_id": True, "time": 40},
        None,
    ]
    merged = call_js("newsMerge", [], incoming, 2)
    assert len(merged) == 2
    assert [x["_id"] for x in merged] == ["c", "b"]

    # Null list and incoming
    assert call_js("newsMerge", None, None, 5) == []


def test_news_pulse_thresholds_and_levels():
    """newsPulse evaluates QUIET, BUSY, EVENT based on NW thresholds (mark=7, win=1h, event=3)."""
    now = 1_000_000_000
    win_ms = 3_600_000

    # 1. Below mark (importance < 7)
    items_low = [{"_id": "1", "time": now - 1000, "importance": 6}]
    pulse_low = call_js("newsPulse", items_low, now)
    assert pulse_low["n"] == 0
    assert pulse_low["level"] == "QUIET"
    assert pulse_low["top"] is None

    # 2. Exactly at mark (importance = 7), level = BUSY (n=1)
    items_busy1 = [{"_id": "1", "time": now - 1000, "importance": 7}]
    pulse_busy1 = call_js("newsPulse", items_busy1, now)
    assert pulse_busy1["n"] == 1
    assert pulse_busy1["level"] == "BUSY"
    assert pulse_busy1["top"]["_id"] == "1"

    # 3. Two items >= 7 -> still BUSY
    items_busy2 = [
        {"_id": "1", "time": now - 1000, "importance": 7},
        {"_id": "2", "time": now - 2000, "importance": 8},
    ]
    pulse_busy2 = call_js("newsPulse", items_busy2, now)
    assert pulse_busy2["n"] == 2
    assert pulse_busy2["level"] == "BUSY"
    assert pulse_busy2["top"]["_id"] == "2"

    # 4. Three items >= 7 -> EVENT
    items_event = items_busy2 + [{"_id": "3", "time": now - 3000, "importance": 9}]
    pulse_event = call_js("newsPulse", items_event, now)
    assert pulse_event["n"] == 3
    assert pulse_event["level"] == "EVENT"
    assert pulse_event["top"]["_id"] == "3"


def test_news_pulse_window_edges():
    """newsPulse window edge cases: x.time <= now and x.time > now - NW.winMs."""
    now = 1_000_000_000
    win_ms = 3_600_000

    # Item exactly at now: included
    at_now = [{"_id": "1", "time": now, "importance": 8}]
    assert call_js("newsPulse", at_now, now)["n"] == 1

    # Item in future (time > now): excluded
    future = [{"_id": "1", "time": now + 1, "importance": 8}]
    assert call_js("newsPulse", future, now)["n"] == 0

    # Item at exact lower boundary (time == now - winMs): excluded because strictly >
    boundary_exact = [{"_id": "1", "time": now - win_ms, "importance": 8}]
    assert call_js("newsPulse", boundary_exact, now)["n"] == 0

    # Item 1 ms inside lower boundary: included
    boundary_inside = [{"_id": "1", "time": now - win_ms + 1, "importance": 8}]
    assert call_js("newsPulse", boundary_inside, now)["n"] == 1


def test_news_coins_extraction():
    """newsCoins extracts coin tickers from string and object suggestions."""
    # Objects
    x_obj = {"suggestions": [{"coin": "btc"}, {"coin": "eth"}]}
    assert call_js("newsCoins", x_obj) == ["BTC", "ETH"]

    # Strings
    x_str = {"suggestions": ["sol", "ADA"]}
    assert call_js("newsCoins", x_str) == ["SOL", "ADA"]

    # Mixed and falsy
    x_mixed = {"suggestions": [{"coin": "link"}, "", None, {"coin": ""}, "DOT"]}
    assert call_js("newsCoins", x_mixed) == ["LINK", "DOT"]

    # Empty / null
    assert call_js("newsCoins", {}) == []
    assert call_js("newsCoins", None) == []


def test_news_read_word_rules():
    """newsRead applies NR word rules in priority order."""
    # Hack rule: NEGATIVE, SOURCED
    r_hack = call_js("newsRead", {"title": "Crypto exchange hacked for $50M"})
    assert r_hack["tag"] == "NEGATIVE"
    assert "hack" in r_hack["why"]
    assert r_hack["src"] == "SOURCED"

    # Halt withdrawals rule: NEGATIVE
    r_halt = call_js("newsRead", {"title": "Platform halts all trading and withdrawals"})
    assert r_halt["tag"] == "NEGATIVE"
    assert "halt" in r_halt["why"]

    # Macro rule: UNKNOWN, SOURCED
    r_macro = call_js("newsRead", {"title": "US CPI report shows inflation easing"})
    assert r_macro["tag"] == "UNKNOWN"
    assert "macro" in r_macro["why"]
    assert r_macro["src"] == "SOURCED"

    # ETF approval: POSITIVE
    r_etf_up = call_js("newsRead", {"title": "SEC approves first spot Bitcoin ETF"})
    assert r_etf_up["tag"] == "POSITIVE"

    # ETF rejection: NEGATIVE
    r_etf_down = call_js("newsRead", {"title": "Regulator rejects spot ETF application"})
    assert r_etf_down["tag"] == "NEGATIVE"


def test_news_read_coins_and_btc_sentiment():
    """newsRead handles non-BTC coin filter, and BTC-specific buying/selling direction."""
    # Non-BTC coin with no BTC reference: NEUTRAL
    r_non_btc = call_js("newsRead", {
        "title": "Solana ecosystem hits new milestone",
        "suggestions": [{"coin": "SOL"}]
    })
    assert r_non_btc["tag"] == "NEUTRAL"
    assert r_non_btc["why"] == "not about BTC"
    assert r_non_btc["src"] == "SOURCED"

    # BTC buying / adoption: POSITIVE
    r_btc_buy = call_js("newsRead", {"title": "MicroStrategy purchases additional Bitcoin for reserve"})
    assert r_btc_buy["tag"] == "POSITIVE"
    assert "BTC buying" in r_btc_buy["why"]

    # BTC selloff / lawsuit: NEGATIVE
    r_btc_sell = call_js("newsRead", {"title": "Massive Bitcoin sell-off dumps market amid lawsuit"})
    assert r_btc_sell["tag"] == "NEGATIVE"
    assert "BTC selling" in r_btc_sell["why"]

    # BTC mentioned without buy/sell direction: UNKNOWN
    r_btc_unknown = call_js("newsRead", {"title": "Bitcoin daily trading volume summary"})
    assert r_btc_unknown["tag"] == "UNKNOWN"
    assert r_btc_unknown["why"] == "no rule matched"


def test_news_read_empty_and_multiline():
    """newsRead handles multiline titles and empty / null inputs."""
    multiline = {"title": "Bitcoin ETF approved by regulators\nAdditional paragraph details..."}
    assert call_js("newsRead", multiline)["tag"] == "POSITIVE"

    empty = call_js("newsRead", {})
    assert empty["tag"] == "UNKNOWN"
    assert empty["why"] == "no title"

    null_item = call_js("newsRead", None)
    assert null_item["tag"] == "UNKNOWN"
    assert null_item["why"] == "no title"
