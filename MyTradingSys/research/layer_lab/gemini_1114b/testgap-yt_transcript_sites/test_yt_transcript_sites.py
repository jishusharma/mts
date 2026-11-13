"""Unit tests for scripts/dev/yt_transcript_sites.py.

Mutation test record (Step 3):
Mutated copy created in scratch file with flipped branch:
  File: scripts/dev/yt_transcript_sites.py:158
  Original:
    if not rows:
        return "WAITING: none"
  Mutated:
    if rows:
        return "WAITING: none"
Resulting failure when pointed at mutated copy:
  test_waiting_report_empty_returns_waiting_none failed with:
    AssertionError: assert 'WAITING: 0 v...XY.md path 3)' == 'WAITING: none'
      - WAITING: none
      + WAITING: 0 video(s); Chrome panel path withdrawn until the operator names a device (YT_PROXY.md path 3)
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
import pytest

REPO = Path(__file__).resolve().parents[5]
DEV = REPO / "scripts" / "dev"
sys.path.insert(0, str(DEV))

import yt_transcript_sites


def test_instances_default_when_no_env(monkeypatch):
    # SOURCED: INSTANCES = ("yt.chocolatemoo53.com",) (scripts/dev/yt_transcript_sites.py:25)
    # SOURCED: env = (os.environ.get("YT_SITE_INSTANCES") or "").strip() (scripts/dev/yt_transcript_sites.py:33)
    # SOURCED: return tuple(h.strip() for h in env.split(",") if h.strip()) if env else INSTANCES (scripts/dev/yt_transcript_sites.py:34)
    # OURS: when YT_SITE_INSTANCES is unset, returns default tuple ("yt.chocolatemoo53.com",)
    monkeypatch.delenv("YT_SITE_INSTANCES", raising=False)
    assert yt_transcript_sites.instances() == ("yt.chocolatemoo53.com",)


def test_instances_from_env_parsed(monkeypatch):
    # SOURCED: return tuple(h.strip() for h in env.split(",") if h.strip()) if env else INSTANCES (scripts/dev/yt_transcript_sites.py:34)
    # OURS: comma-separated list with surrounding whitespace splits and strips into tuple of hosts
    monkeypatch.setenv("YT_SITE_INSTANCES", " inst1.example.org, inst2.example.org ,  ")
    assert yt_transcript_sites.instances() == ("inst1.example.org", "inst2.example.org")


def test_read_waiting_nonexistent_file_returns_empty(tmp_path, monkeypatch):
    # SOURCED: except (OSError, ValueError): return [] (scripts/dev/yt_transcript_sites.py:126-127)
    # OURS: nonexistent file triggers OSError, caught and returns empty list []
    monkeypatch.setenv("YT_WAITING_FILE", str(tmp_path / "nonexistent.json"))
    assert yt_transcript_sites.read_waiting() == []


def test_read_waiting_malformed_json_returns_empty(tmp_path, monkeypatch):
    # SOURCED: data = json.loads(waiting_file().read_text(encoding="utf-8")) (scripts/dev/yt_transcript_sites.py:124)
    # SOURCED: except (OSError, ValueError): return [] (scripts/dev/yt_transcript_sites.py:126-127)
    # OURS: content "{broken json" triggers json.loads ValueError, caught and returns empty list []
    f = tmp_path / "bad.json"
    f.write_text("{broken json", encoding="utf-8")
    monkeypatch.setenv("YT_WAITING_FILE", str(f))
    assert yt_transcript_sites.read_waiting() == []


def test_read_waiting_non_list_json_returns_empty(tmp_path, monkeypatch):
    # SOURCED: return data if isinstance(data, list) else [] (scripts/dev/yt_transcript_sites.py:125)
    # OURS: content '{"id": "v1"}' parses to dict; not a list, so returns empty list []
    f = tmp_path / "dict.json"
    f.write_text('{"id": "v1"}', encoding="utf-8")
    monkeypatch.setenv("YT_WAITING_FILE", str(f))
    assert yt_transcript_sites.read_waiting() == []


def test_add_and_read_waiting_normal(tmp_path, monkeypatch):
    # SOURCED: rows.append({"id": vid, "channel": channel, "time": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"), "paths_tried": list(paths_tried)}) (scripts/dev/yt_transcript_sites.py:133-134)
    # OURS: adding vid="abc12345678", channel="@trader", paths_tried=("p1", "p2") with now=datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)
    # OURS: expected entry is {"id": "abc12345678", "channel": "@trader", "time": "2026-11-14T12:00:00+00:00", "paths_tried": ["p1", "p2"]}
    f = tmp_path / "waiting.json"
    monkeypatch.setenv("YT_WAITING_FILE", str(f))
    fixed_now = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)
    yt_transcript_sites.add_waiting("abc12345678", channel="@trader", paths_tried=("p1", "p2"), now=fixed_now)
    assert yt_transcript_sites.read_waiting() == [
        {"id": "abc12345678", "channel": "@trader", "time": "2026-11-14T12:00:00+00:00", "paths_tried": ["p1", "p2"]}
    ]


def test_drop_waiting_removes_entry(tmp_path, monkeypatch):
    # SOURCED: keep = [r for r in rows if r.get("id") != vid] (scripts/dev/yt_transcript_sites.py:142)
    # OURS: after adding "v1" and "v2", dropping "v1" leaves only "v2"
    f = tmp_path / "waiting.json"
    monkeypatch.setenv("YT_WAITING_FILE", str(f))
    fixed_now = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)
    yt_transcript_sites.add_waiting("v1", channel="@ch1", now=fixed_now)
    yt_transcript_sites.add_waiting("v2", channel="@ch2", now=fixed_now)
    yt_transcript_sites.drop_waiting("v1")
    assert [r["id"] for r in yt_transcript_sites.read_waiting()] == ["v2"]


def test_pending_filters_cached_timed_and_raw_files(tmp_path, monkeypatch):
    # SOURCED: rows = [r for r in rows if not (Path(cache_dir) / (str(r.get("id")) + "_timed.txt")).exists() and not (Path(cache_dir) / (str(r.get("id")) + "_raw.txt")).exists()] (scripts/dev/yt_transcript_sites.py:151-152)
    # OURS: cache directory contains v1_timed.txt and v2_raw.txt; pending() returns only v3
    f = tmp_path / "waiting.json"
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "v1_timed.txt").write_text("cues", encoding="utf-8")
    (cache / "v2_raw.txt").write_text("raw text", encoding="utf-8")
    monkeypatch.setenv("YT_WAITING_FILE", str(f))
    fixed_now = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)
    yt_transcript_sites.add_waiting("v1", now=fixed_now)
    yt_transcript_sites.add_waiting("v2", now=fixed_now)
    yt_transcript_sites.add_waiting("v3", now=fixed_now)
    assert [r["id"] for r in yt_transcript_sites.pending(cache_dir=cache)] == ["v3"]


def test_waiting_report_empty_returns_waiting_none(tmp_path, monkeypatch):
    # SOURCED: if not rows: return "WAITING: none" (scripts/dev/yt_transcript_sites.py:158-159)
    # OURS: when waiting file is empty, waiting_report() returns "WAITING: none"
    monkeypatch.setenv("YT_WAITING_FILE", str(tmp_path / "waiting.json"))
    assert yt_transcript_sites.waiting_report() == "WAITING: none"


def test_list_channel_mock_normal(monkeypatch):
    # SOURCED: res = _json(base + "resolveurl?url=" + urllib.parse.quote("https://www.youtube.com/" + handle.lstrip("/"), safe="")) (scripts/dev/yt_transcript_sites.py:100)
    # SOURCED: ucid = (res or {}).get("ucid") (scripts/dev/yt_transcript_sites.py:101)
    # SOURCED: got = _json(base + "channels/" + urllib.parse.quote(ucid) + "/latest") or {} (scripts/dev/yt_transcript_sites.py:105)
    # SOURCED: d = datetime.fromtimestamp(p, timezone.utc).strftime("%Y-%m-%d") if isinstance(p, (int, float)) else "" (scripts/dev/yt_transcript_sites.py:109)
    # SOURCED: out.append((v["videoId"], v.get("title") or "", d)) (scripts/dev/yt_transcript_sites.py:111)
    # SOURCED: return out[:n] (scripts/dev/yt_transcript_sites.py:112)
    # OURS: published=1700000000 converts to UTC date string "2023-11-14"
    # OURS: returns list of 3-tuples [("vid01", "BTC Review", "2023-11-14")]
    def fake_json(url):
        if "resolveurl" in url:
            return {"ucid": "UC123"}
        if "channels/UC123/latest" in url:
            return {"videos": [{"videoId": "vid01", "title": "BTC Review", "published": 1700000000}]}
        return None

    monkeypatch.setattr(yt_transcript_sites, "_json", fake_json)
    assert yt_transcript_sites.list_channel("@analyst", n=5, sleep=lambda s: None) == [
        ("vid01", "BTC Review", "2023-11-14")
    ]
