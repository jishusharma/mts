"""Unit tests for scripts/dev/make_home.py.

Existing coverage check (Step 1):
  No test file named for make_home.py exists in scripts/ or MyTradingSys/.
  scripts/dev/test_artifacts.py imports make_home in 8 tests (lines 119, 136,
  143, 151, 163, 188, 290, 358) against the live registry.json, but had no
  isolated unit tests for empty/malformed registries or render() </ escaping.

Mutation test record (Step 4):
Mutated copy created in a scratch directory with inverted write-first sort key:
  File: scripts/dev/make_home.py:54
  Original:
    pages.sort(key=lambda p: (not p["write"], WRITE_FIRST.index(p["slug"]) if p["write"] else 0))
  Mutated:
    pages.sort(key=lambda p: (p["write"], WRITE_FIRST.index(p["slug"]) if p["write"] else 0))
Resulting failure when pointed at mutated scratch copy:
  test_build_normal_sorting_write_first_and_retire_filtering failed with:
    AssertionError: assert ['alpha_page', 'research_map'] == ['research_map', 'alpha_page']
"""
import sys
from datetime import datetime, timezone
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[5]
DEV = REPO / "scripts" / "dev"
sys.path.insert(0, str(DEV))

import make_home as mh  # noqa: E402


def test_build_normal_sorting_write_first_and_retire_filtering():
    # SOURCED: WRITE_FIRST = ("research_map",) (scripts/dev/make_home.py:25)
    # SOURCED: AMBER_DAYS, RED_BEHIND_DAYS = 14, 3 (scripts/dev/make_home.py:26)
    # SOURCED: pages.sort(key=lambda p: (not p["write"], WRITE_FIRST.index(p["slug"]) if p["write"] else 0)) (scripts/dev/make_home.py:54)
    # OURS: now = 2026-11-14 00:00 UTC -> IST = 05:30 IST; research_map sorts before alpha_page despite appearing later in reg["pages"]
    reg = {
        "home_login": "jishusharma1985",
        "home_slug": "mts_home",
        "pages": [
            {
                "slug": "mts_home",
                "title": "MTS Home",
                "status": "canonical",
                "single_owner": "jishusharma1985",
                "urls": {"jishusharma1985": "https://claude.ai/artifact/home001"},
            },
            {
                "slug": "alpha_page",
                "title": "Alpha Page",
                "status": "canonical",
                "single_owner": "jishusharma1985",
                "purpose": "Alpha summary",
                "db": True,
                "published_at": "2026-11-13T12:00:00Z",
                "urls": {
                    "jishusharma1985": "https://claude.ai/artifact/alpha001",
                    "jishu.sharma": "https://claude.ai/artifact/alpha_old",
                    "jishu.awgp": "https://claude.ai/artifact/alpha_deleted",
                },
                "deleted": {"jishu.awgp": "2026-11-01"},
            },
            {
                "slug": "research_map",
                "title": "Research Map",
                "status": "canonical",
                "single_owner": "jishusharma1985",
                "urls": {"jishusharma1985": "https://claude.ai/artifact/rmap001"},
            },
            {
                "slug": "old_page",
                "title": "Old Page",
                "status": "retire",
                "urls": {
                    "jishusharma1985": "",
                    "jishu.sharma": "https://claude.ai/artifact/old001",
                },
            },
        ],
        "unpinned_old": {
            "jishu.sharma": [{"title": "Unpinned Copy", "url": "https://claude.ai/artifact/unpin001"}]
        },
    }
    now = datetime(2026, 11, 14, 0, 0, tzinfo=timezone.utc)
    d = mh.build(reg, now=now)

    assert d["generated"] == "2026-11-14 00:00 UTC · 05:30 IST"
    assert d["home"] == "jishusharma1985"
    assert d["amberDays"] == 14
    assert d["redDays"] == 3
    assert [p["slug"] for p in d["pages"]] == ["research_map", "alpha_page"]

    rmap, alpha = d["pages"]
    assert rmap["write"] is True
    assert rmap["pub"] == "never published"
    assert rmap["pubIso"] == ""
    assert rmap["behind"] is True

    assert alpha["write"] is False
    assert alpha["db"] is True
    assert alpha["purpose"] == "Alpha summary"
    assert alpha["pub"] == "2026-11-13 12:00 UTC · 17:30 IST"
    assert alpha["pubIso"] == "2026-11-13T12:00:00Z"
    assert alpha["behind"] is False

    assert d["retire"] == [
        {"login": "jishu.sharma", "title": "Alpha Page", "url": "https://claude.ai/artifact/alpha_old"},
        {"login": "jishu.sharma", "title": "Old Page", "url": "https://claude.ai/artifact/old001"},
        {"login": "jishu.sharma", "title": "Unpinned Copy", "url": "https://claude.ai/artifact/unpin001"},
    ]


def test_build_empty_registry():
    # SOURCED: return {"generated": af.stamp_text(now), "home": home, "pages": pages, "retire": retire, "amberDays": AMBER_DAYS, "redDays": RED_BEHIND_DAYS} (scripts/dev/make_home.py:55)
    # OURS: empty pages=[] and no unpinned_old -> pages=[] and retire=[]; 03:20 UTC + 05:30 = 08:50 IST
    reg = {"home_login": "jishusharma1985", "home_slug": "mts_home", "pages": []}
    now = datetime(2026, 11, 14, 3, 20, tzinfo=timezone.utc)
    d = mh.build(reg, now=now)
    assert d == {
        "generated": "2026-11-14 03:20 UTC · 08:50 IST",
        "home": "jishusharma1985",
        "pages": [],
        "retire": [],
        "amberDays": 14,
        "redDays": 3,
    }


def test_build_malformed_entries_handled_gracefully():
    # SOURCED: for r in rows if isinstance(rows, list) else []: (scripts/dev/make_home.py:52)
    # SOURCED: if pg["status"] != "canonical" or not url or pg["slug"] == reg["home_slug"]: continue (scripts/dev/make_home.py:40-41)
    # OURS: non-list unpinned_old is ignored, blank url is skipped, malformed published_at falls back to "never published"
    reg = {
        "home_login": "jishusharma1985",
        "home_slug": "mts_home",
        "pages": [
            {
                "slug": "blank_url",
                "title": "Blank URL",
                "status": "canonical",
                "urls": {"jishusharma1985": ""},
            },
            {
                "slug": "bad_date",
                "title": "Bad Date",
                "status": "canonical",
                "published_at": "not-a-date",
                "last_published": {},
                "urls": {"jishusharma1985": "https://claude.ai/artifact/bad001"},
            },
        ],
        "unpinned_old": {"jishu.sharma": "malformed-not-a-list"},
    }
    now = datetime(2026, 11, 14, 0, 0, tzinfo=timezone.utc)
    d = mh.build(reg, now=now)
    assert [p["slug"] for p in d["pages"]] == ["bad_date"]
    assert d["pages"][0]["pub"] == "never published"
    assert d["pages"][0]["pubIso"] == ""
    assert d["pages"][0]["behind"] is True
    assert d["retire"] == []


def test_build_malformed_missing_home_login_raises():
    # SOURCED: home = reg["home_login"] (scripts/dev/make_home.py:31)
    # OURS: missing required key "home_login" raises KeyError
    with pytest.raises(KeyError):
        mh.build({"home_slug": "mts_home", "pages": []})


def test_render_escapes_closing_script_tag():
    # SOURCED: return TPL.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")) (scripts/dev/make_home.py:170)
    # OURS: "</script>" inside data is escaped to "<\\/script>" so embedded JSON cannot close the <script> tag
    data = {
        "generated": "2026-11-14 00:00 UTC · 05:30 IST",
        "home": "jishusharma1985",
        "pages": [{"slug": "x", "title": "</script><script>alert(1)</script>", "url": "https://claude.ai/artifact/x",
                   "owner": "jishusharma1985", "purpose": "", "db": False, "write": False, "behind": False,
                   "pub": "never published", "pubIso": ""}],
        "retire": [],
        "amberDays": 14,
        "redDays": 3,
    }
    html = mh.render(data)
    payload = html.split("const DATA = ")[1].split(";\n")[0]
    assert "<title>MTS Home</title>" in html
    assert "</script>" not in payload
    assert "<\\/script>" in payload
