"""RU1: tasks.dispatch() snapshot. In-process fixtures, no git or repo files."""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import lane_health  # noqa: E402
import tasks  # noqa: E402

AS_OF = datetime(2026, 10, 18, 19, 0, 0, tzinfo=timezone.utc)


def card(cid, **kw):
    c = {"id": cid, "title": cid.upper(), "state": "ready", "lane": "SONNET", "prio": 3, "size": "S", "est_turns": 10, "worker": "agent",
         "goal": "g", "done_when": "d", "steps": ["s"], "scope_in": [f"x/{cid}.py"], "tests": "t", "created": "2026-10-18T10:00:00Z",
         "depends_on": [], "note": "", "weight": "", "live_path": False}
    c.update(kw)
    return c


def snap(cards, holds=(), claims=None, lane=None, host=None):
    return tasks.dispatch(cards, {}, set(holds), claims or {}, lane or lane_health.blank(), AS_OF, host)


def reasons(s):
    return {e["id"]: (e["reason_code"], e["why"]) for e in s["excluded"]}


def test_held_card_excluded_with_announcement_id():
    s = snap([card("a", note="HOLD A-20261018-1"), card("b")], holds={"A-20261018-1"})
    assert [r["id"] for r in s["dispatch"]] == ["b"]
    assert reasons(s)["a"][0] == "hold" and "A-20261018-1" in reasons(s)["a"][1]


def test_claimed_by_slug_and_by_area_overlap():
    claims = {"a": {"host": "JIS-NB", "account": "u", "area": "-"}, "other": {"host": "JIS-NUC", "account": "v", "area": "x/c"}}
    s = snap([card("a"), card("b")], claims=claims)
    assert [r["id"] for r in s["dispatch"]] == ["b"]
    r = reasons(s)
    assert r["a"][0] == "claimed" and "JIS-NB" in r["a"][1]
    s2 = snap([card("c", scope_in=["x/c/deep.py"])], claims=claims)
    assert reasons(s2)["c"][0] == "claimed" and "overlaps claim other" in reasons(s2)["c"][1]


def test_dependency_not_done_excluded_done_dependency_passes():
    cards = [card("dep", state="active"), card("a", depends_on=["dep"]), card("fin", state="done"), card("b", depends_on=["fin"])]
    s = snap(cards)
    assert reasons(s)["a"][0] == "dependency" and "dep" in reasons(s)["a"][1]
    assert [r["id"] for r in s["dispatch"]] == ["b"]


def test_raw_card_and_down_lane_excluded():
    down = lane_health.go_down(lane_health.blank(), "limit", "x", AS_OF)
    s = snap([card("raw1", state="raw"), card("cx", lane="CODEX", kind="audit"), card("ok")], lane=down)
    r = reasons(s)
    assert r["raw1"][0] == "state" and r["cx"][0] == "lane_down"
    assert [x["id"] for x in s["dispatch"]] == ["ok"]


def test_ranking_matches_hand_ranked_fixture_and_reviewer_slots():
    cards = [card("p2routine", prio=2), card("p1routine", prio=1), card("p1crucial", prio=1, weight="CRUCIAL", note="REVIEWED:2026-10-18 ACCEPT"),
             card("ci-1", prio=1, pinned=True), card("p1old", prio=1, created="2026-10-17T10:00:00Z"),
             card("p1crit", prio=1, live_path=True, lane="JIS-NB", commands=["x"], note="REVIEWED: lab 2026-10-18")]
    s = snap(cards)
    assert [r["id"] for r in s["dispatch"]] == ["ci-1", "p1crit", "p1crucial", "p1old", "p1routine", "p2routine"]
    slot = {r["id"]: r["reviewer"] for r in s["dispatch"]}
    assert slot["p1crit"] == "REVIEW session" and slot["p1crucial"] == "review Agent" and slot["p1routine"].startswith("none")
    assert [r["rank"] for r in s["dispatch"]] == [1, 2, 3, 4, 5, 6]


def test_crucial_without_real_stamp_excluded():
    s = snap([card("c", weight="CRUCIAL")])
    assert reasons(s)["c"][0] == "no_stamp"


def test_deterministic_output_and_table_limit():
    cards = [card(f"c{i:02d}", prio=1 + i % 3) for i in range(30)]
    import json
    a = json.dumps(snap(cards), sort_keys=True)
    b = json.dumps(snap(list(reversed(cards))), sort_keys=True)
    assert a == b
    assert len(tasks.dispatch_table(snap(cards))) <= tasks.DISPATCH_TABLE_MAX
