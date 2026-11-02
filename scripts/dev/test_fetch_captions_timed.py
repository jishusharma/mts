"""Spec-derived tests for scripts/dev/fetch_captions_timed.py pure components.

Covers:
  - parse_vtt: timestamp parsing, HTML tag stripping, entity decoding, consecutive deduplication
  - ip_hash: pseudonymization hash contract
  - daily_budget: defaults, env override, invalid value fallback, proxy budget
  - budget_used: rolling 24 h window from local record and fleet ytuse signals
  - current_level: local level vs fleet ytblock/ytclean resolution
  - fleet_block: live fleet block detection, clean signal cancellation
  - blocked_until: local block file future/past expiration, IP mismatch handling
"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

import fetch_captions_timed as fct


def test_parse_vtt_basic_cues_and_entity_decoding():
    raw_vtt = """WEBVTT
Kind: captions
Language: en

00:00:05.120 --> 00:00:08.500
<c>Bitcoin</c> is testing &amp; holding 68k.

00:01:15.000 --> 00:01:18.000
Support at &gt; 67000 &lt;reclaimed&gt;.
"""
    cues = fct.parse_vtt(raw_vtt)
    assert cues == [
        (5, "Bitcoin is testing & holding 68k."),
        (75, "Support at > 67000 <reclaimed>."),
    ]


def test_parse_vtt_hours_calculation():
    raw_vtt = """WEBVTT

01:02:03.456 --> 01:02:05.000
Over one hour mark.
"""
    cues = fct.parse_vtt(raw_vtt)
    # 1*3600 + 2*60 + 3 = 3723
    assert cues == [(3723, "Over one hour mark.")]


def test_parse_vtt_dedupes_consecutive_identical_lines():
    raw_vtt = """WEBVTT

00:00:01.000 --> 00:00:02.000
repeated phrase

00:00:02.000 --> 00:00:03.000
repeated phrase

00:00:03.000 --> 00:00:04.000
new phrase
"""
    cues = fct.parse_vtt(raw_vtt)
    assert cues == [
        (1, "repeated phrase"),
        (3, "new phrase"),
    ]


def test_parse_vtt_empty_or_non_matching_returns_empty():
    assert fct.parse_vtt("") == []
    assert fct.parse_vtt("WEBVTT\nKind: captions\nNOTE comment\n") == []


def test_ip_hash_empty_and_known_vector():
    assert fct.ip_hash("") == ""
    assert fct.ip_hash(None) == ""
    sample_ip = "198.51.100.42"
    expected = hashlib.sha256(("mts-yt:" + sample_ip).encode("ascii")).hexdigest()[:8]
    assert fct.ip_hash(sample_ip) == expected
    assert len(expected) == 8


def test_daily_budget_defaults_and_overrides(monkeypatch):
    monkeypatch.delenv("YT_DAILY_BUDGET", raising=False)
    monkeypatch.setattr(fct, "proxy_url", lambda: None)
    assert fct.daily_budget() == 40

    monkeypatch.setenv("YT_DAILY_BUDGET", "85")
    assert fct.daily_budget() == 85

    monkeypatch.setenv("YT_DAILY_BUDGET", "invalid-int")
    assert fct.daily_budget() == 40

    monkeypatch.delenv("YT_DAILY_BUDGET", raising=False)
    monkeypatch.setattr(fct, "proxy_url", lambda: "socks5://127.0.0.1:40000")
    assert fct.daily_budget() == 150


def test_budget_used_aggregates_local_stamps_and_other_hosts():
    now = datetime.now(timezone.utc)
    ih = "deadbeef"
    recent_1 = (now - timedelta(hours=2)).isoformat(timespec="seconds")
    recent_2 = (now - timedelta(hours=5)).isoformat(timespec="seconds")
    stale = (now - timedelta(hours=26)).isoformat(timespec="seconds")

    rec = {"req": {ih: [recent_1, recent_2, stale]}}

    # Fleet signals
    rows = [
        # Match from another host within 24h
        {
            "kind": "ytuse",
            "ih": ih,
            "host": "other-node",
            "t": (now - timedelta(hours=1)).strftime("%Y%m%dT%H%M%SZ"),
            "n": 4,
        },
        # From own host (should be ignored to prevent double count)
        {
            "kind": "ytuse",
            "ih": ih,
            "host": fct._host(),
            "t": (now - timedelta(hours=1)).strftime("%Y%m%dT%H%M%SZ"),
            "n": 10,
        },
        # Different IP hash (ignored)
        {
            "kind": "ytuse",
            "ih": "otherip",
            "host": "other-node",
            "t": (now - timedelta(hours=1)).strftime("%Y%m%dT%H%M%SZ"),
            "n": 99,
        },
        # Expired fleet row (ignored)
        {
            "kind": "ytuse",
            "ih": ih,
            "host": "other-node",
            "t": (now - timedelta(hours=25)).strftime("%Y%m%dT%H%M%SZ"),
            "n": 20,
        },
    ]

    used = fct.budget_used(rows, ih, rec=rec)
    # 2 local + 4 remote = 6
    assert used == 6


def test_current_level_resolves_newest_event_and_clean_signal():
    ih = "12345678"
    t1 = datetime(2026, 11, 2, 10, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 11, 2, 11, 0, 0, tzinfo=timezone.utc)
    t3 = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)

    # Local record at t1 with level 1
    rec = {"level": 1, "level_t": t1.isoformat()}
    assert fct.current_level([], ih, rec=rec) == 1

    # Fleet block at t2 with level 2 (newer than local record)
    rows = [
        {"kind": "ytblock", "ih": ih, "t": t2.strftime("%Y%m%dT%H%M%SZ"), "level": 2}
    ]
    assert fct.current_level(rows, ih, rec=rec) == 2

    # Fleet clean at t3 (newest event resets to 0)
    rows.append(
        {"kind": "ytclean", "ih": ih, "t": t3.strftime("%Y%m%dT%H%M%SZ")}
    )
    assert fct.current_level(rows, ih, rec=rec) == 0


def test_fleet_block_clean_overrides_earlier_block():
    ih = "abcd1234"
    t1 = datetime(2026, 11, 2, 10, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 11, 2, 11, 0, 0, tzinfo=timezone.utc)
    future_until = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()

    # Block at t1
    rows = [
        {"kind": "ytblock", "ih": ih, "t": t1.strftime("%Y%m%dT%H%M%SZ"), "until": future_until}
    ]
    assert fct.fleet_block(rows, ih) is not None

    # Clean at t2 (newer than t1 block) voids it
    rows.append(
        {"kind": "ytclean", "ih": ih, "t": t2.strftime("%Y%m%dT%H%M%SZ")}
    )
    assert fct.fleet_block(rows, ih) is None


def test_local_blocked_until_respects_expiration_and_ip(tmp_path, monkeypatch):
    block_json = tmp_path / "yt_block.json"
    monkeypatch.setenv("YT_BLOCK_FILE", str(block_json))
    monkeypatch.setattr(fct, "public_ip", lambda: "192.0.2.1")

    # Expired block
    past_iso = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    block_json.write_text(json.dumps({"blocked_until": past_iso, "ip": "192.0.2.1"}))
    assert fct._local_blocked_until() is None

    # Active block matching current IP
    future_time = datetime.now(timezone.utc) + timedelta(hours=4)
    future_iso = future_time.isoformat()
    block_json.write_text(json.dumps({"blocked_until": future_iso, "ip": "192.0.2.1"}))
    res = fct._local_blocked_until()
    assert res is not None
    assert abs((res - future_time).total_seconds()) < 2

    # Active block written from different IP (e.g. home IP vs VPN IP)
    monkeypatch.setattr(fct, "public_ip", lambda: "198.51.100.99")
    assert fct._local_blocked_until() is None

    # Check that check_ip=False ignores IP differences
    assert fct._local_blocked_until(check_ip=False) is not None
