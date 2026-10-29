"""Popup cleanup must match every producer title: one popup max per producer."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHOW = (ROOT / "scripts/core/show-alert.ps1").read_text(encoding="utf-8")
START = (ROOT / "scripts/core/start-trading-day.ps1").read_text(encoding="utf-8")

TITLES = {
    "alert": ["MTS ALERT #3", "MTS ALERT #12"],
    "change": ["MTS #4 - VERDICT CHANGE", "MTS #5 - ZONE CHANGE"],
    "tape": ["TAPE #7 - div"],
    "health": ["MTS live health RED"],
}


def rxs():
    return re.findall(r"^# POPUP_PRODUCER_RX: (.+)$", SHOW, re.M)


def producer(title):
    hit = [r for r in rxs() if re.search(r, title)]
    return hit[0] if hit else None


def test_every_title_form_has_a_pattern():
    for forms in TITLES.values():
        for t in forms:
            assert producer(t), t


def test_one_pattern_per_producer_and_no_cross_kill():
    assert producer("MTS ALERT #3") == producer("MTS #4 - VERDICT CHANGE")
    assert producer("TAPE #7 - div") != producer("MTS ALERT #3")
    assert producer("MTS live health RED") != producer("MTS ALERT #3")
    assert not re.search(producer("TAPE #7 - div"), "MTS ALERT #3")


def test_start_trading_day_kill_pattern_matches_both_mts_forms():
    m = re.search(r'MainWindowTitle -match "([^"]+)"', START)
    assert m
    pat = m.group(1)
    for t in TITLES["alert"] + TITLES["change"]:
        assert re.search(pat, t), t
    assert not re.search(pat, "TAPE #7 - div")
