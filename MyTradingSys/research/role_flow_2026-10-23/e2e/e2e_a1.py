"""E2E edge cases for flow-a1: tasks.status_line / stale_raw and supervisor.plan_lines, old code vs new code.
usage: python e2e_a1.py <worktree> <old_tasks.py>"""
import importlib.util, json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

W = Path(sys.argv[1]); OLD = Path(sys.argv[2])
sys.path.insert(0, str(W / "scripts" / "dev"))
import tasks as NEW                                    # noqa: E402
import supervisor as S                                 # noqa: E402
spec = importlib.util.spec_from_file_location("tasks_old", OLD); OLDM = importlib.util.module_from_spec(spec); spec.loader.exec_module(OLDM)

AT = datetime(2026, 10, 23, 12, 0, tzinfo=timezone.utc)
def iso(dt): return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
def card(i, state="raw", age_h=2.0, lane="SONNET", **kw):
    c = {"id": i, "state": state, "lane": lane, "created": iso(AT - timedelta(hours=age_h))}
    c.update(kw); return c
def ready(n): return [card(f"R{k}", "ready", 5) for k in range(n)]

def old_line(cards):
    try: return OLDM.status_line(cards)                # old code has no clock argument; ages do not matter to it
    except TypeError: return OLDM.status_line(cards, AT)

CASES = [  # id, description, cards, expected word on NEW, expected stale count
    ("E01", "empty board", [], "REFINE_OK", 0),
    ("E02", "operator case: 1 raw 2 h old + 5 ready", [card("B1")] + ready(5), "REFINE_NEEDED", 1),
    ("E03", "1 raw 30 min old, 0 ready (queue empty, card fresh)", [card("B1", age_h=0.5)], "REFINE_NEEDED", 0),
    ("E04", "boundary: exactly 1 h old", [card("B1", age_h=1.0)] + ready(5), "REFINE_OK", 0),
    ("E05", "boundary: 1 h + 1 s old", [card("B1", age_h=1 + 1/3600)] + ready(5), "REFINE_NEEDED", 1),
    ("E06", "created missing", [dict(card("B1"), created="")] + ready(5), "REFINE_NEEDED", 1),
    ("E07", "created garbage", [dict(card("B1"), created="yesterday")] + ready(5), "REFINE_NEEDED", 1),
    ("E08", "naive timestamp (no Z) treated as UTC", [dict(card("B1"), created=(AT - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S"))] + ready(5), "REFINE_NEEDED", 1),
    ("E09", "+05:30 offset, 2 h old in UTC", [dict(card("B1"), created=(AT - timedelta(hours=2)).astimezone(timezone(timedelta(hours=5, minutes=30))).isoformat())] + ready(5), "REFINE_NEEDED", 1),
    ("E10", "future-dated (clock skew)", [card("B1", age_h=-3)] + ready(5), "REFINE_OK", 0),
    ("E11", "parked by asks, 3 d old", [card("B1", age_h=72, asks="which year?")] + ready(5), "REFINE_OK", 0),
    ("E12", "refine_tries=2 (MAX), 3 d old", [card("B1", age_h=72, refine_tries=2)] + ready(5), "REFINE_OK", 0),
    ("E13", "refine_tries=1, 3 d old", [card("B1", age_h=72, refine_tries=1)] + ready(5), "REFINE_NEEDED", 1),
    ("E14", "refined state, 3 d old, 0 ready", [card("B1", "refined", 72)], "REFINE_NEEDED", 0),
    ("E15", "old ready/active/done cards only", [card("A", "ready", 90), card("B", "active", 90), card("C", "done", 90)], "REFINE_OK", 0),
    ("E16", "mix: 3 stale, 1 fresh, 1 parked, 1 maxed", [card("a"), card("b", age_h=30), card("c", age_h=5), card("d", age_h=0.2),
                                                         card("e", asks="?"), card("f", refine_tries=2)] + ready(5), "REFINE_NEEDED", 3),
    ("E17", "1 raw 2 h + 3 ready DSA-lane only", [card("B1")] + [card(f"D{k}", "ready", 5, lane="DSA-NB") for k in range(3)], "REFINE_NEEDED", 1),
]

rows, fails = [], 0
for cid, desc, cards, want, want_n in CASES:
    new = NEW.status_line(cards, AT); n = len(NEW.stale_raw(cards, AT)); old = old_line(cards)
    ok = new.split()[0] == want and n == want_n
    fails += not ok
    rows.append((cid, "PASS" if ok else "FAIL", desc, old.split()[0], new.split()[0], n, want, want_n))

# plan_lines gating
T0 = datetime(2026, 10, 23, 10, 0, tzinfo=timezone.utc)
def plan(mode):
    p = S.pace_plan(T0, _rd(), 95)
    p["mode"] = mode; return p
def _rd():
    import test_supervisor as TS                     # reuse the suite's own usage fixture
    return TS._rd(10, 20)
live = {"A": {"host": "JIS-NUC", "mode": "NORMAL", "run": 0, "free": 3, "at": "x", "dsa": "up"}}
PL = [  # id, desc, mode, ctx, expect RUN line
    ("P01", "NORMAL, refine_raw=4", "NORMAL", {"ci": {"red": False}, "picks": [], "refine_raw": 4}, True),
    ("P02", "NORMAL, refine_raw=0", "NORMAL", {"ci": {"red": False}, "picks": [], "refine_raw": 0}, False),
    ("P03", "NORMAL, refine_raw missing (card load failed)", "NORMAL", {"ci": {"red": False}, "picks": []}, False),
    ("P04", "mode STOP", "STOP", {"ci": {"red": False}, "picks": [], "refine_raw": 4}, False),
    ("P05", "mode SUPERVISOR-ONLY", "SUPERVISOR-ONLY", {"ci": {"red": False}, "picks": [], "refine_raw": 4}, False),
    ("P06", "CI red", "NORMAL", {"ci": {"red": True, "message": "3mg"}, "picks": [], "refine_raw": 4}, False),
    ("P07", "THROTTLE mode", "THROTTLE", {"ci": {"red": False}, "picks": [], "refine_raw": 4}, True),
    ("P08", "CRUCIAL-ONLY mode", "CRUCIAL-ONLY", {"ci": {"red": False}, "picks": [], "refine_raw": 4}, True),
    ("P09", "peers unknown", "NORMAL", {"ci": {"red": False}, "picks": [], "refine_raw": 4, "peers_unknown": True}, True),
]
for pid, desc, mode, ctx, want in PL:
    out = S.plan_lines("A", "JIS-NUC", plan(mode), live, ctx, gate_key=False)
    got = [l for l in out if l.startswith("RUN Session_Planner")]
    ok = bool(got) == want and len(got) <= 1
    fails += not ok
    rows.append((pid, "PASS" if ok else "FAIL", desc, "-", got[0] if got else "(none)", len(got), "line" if want else "no line", ""))

print("| case | result | edge case | old code | new code | stale/lines | expected | exp n |")
print("|---|---|---|---|---|---|---|---|")
for r in rows: print("| " + " | ".join(str(x) for x in r) + " |")
print(f"\nTOTAL {len(rows)} cases, {len(rows) - fails} pass, {fails} fail")
sys.exit(1 if fails else 0)
