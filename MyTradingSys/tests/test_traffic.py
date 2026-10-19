"""scripts/dev/traffic.py (TRAFFIC_CONTROLLER.md Part B). Written to fail on the code before traffic.py existed (no module):
the allocation must never give one card to two workers, must throttle on budget, re-route around a silent machine, and the
measurement must not count a lab runner's own claim as a second worker."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import traffic  # noqa: E402

UTC = timezone.utc
T0 = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)


def inv():
    return json.loads((REPO / traffic.INVENTORY).read_text(encoding="utf-8"))


def state(**kw):
    s = {"machines": {"JIS-NB": {"liveness": "ACTIVE", "open_claims": 0, "last_seen": "x"},
                      "JIS-NUC": {"liveness": "ACTIVE", "open_claims": 0, "last_seen": "x"},
                      "DESKTOP-F7IU69N": {"liveness": "SILENT", "open_claims": 0, "last_seen": None}},
         "leases": {"Pipeliner": {"state": "held"}},
         "lanes": {"codex": {"state": "off"}, "gemini-nuc": {"running": 1}},
         "budgets": {}, "desk": {"pending": 0},
         "queue": [{"id": f"s{i}", "lane": "SONNET", "weight": "NORMAL", "title": "t"} for i in range(12)]}
    s.update(kw)
    return s


def cards(props):
    out = []
    for p in props:
        if p["action"].startswith("start sessions for "):
            out += p["action"][len("start sessions for "):].split(", ")
        elif "(next CODEX card " in p["action"]:
            out.append(p["action"].split("(next CODEX card ")[1].rstrip(")"))
        elif p["action"].startswith("gemini_queue.py run "):
            out.append(p["action"].split()[2].split(":")[0])
    return out


class Allocate(unittest.TestCase):
    def test_no_card_given_twice_and_silent_machine_gets_nothing(self):
        s = state(lanes={"codex": {"state": "on", "runs": 0, "runs_cap": 10, "allowance_5h_pct": 10, "ready": 9},
                         "gemini-nuc": {"running": 0}},
                  budgets={"A": {"five_h": 10}, "B": {"five_h": 10}, "C": {"five_h": 10}},
                  queue=[{"id": "c1", "lane": "CODEX", "weight": "NORMAL", "title": "video transcript pull"},
                         {"id": "c2", "lane": "CODEX", "weight": "NORMAL", "title": "youtube captions"}]
                  + state()["queue"])
        props = traffic.allocate(s, inv())
        got = cards(props)
        self.assertEqual(len(got), len(set(got)), props)
        self.assertIn("c1", got)
        self.assertIn("c2", got)                       # gemini takes the next CODEX card, not codex's
        self.assertFalse([p for p in props if p["who"] == "DESKTOP-F7IU69N"], props)
        self.assertEqual(sum(1 for c in got if c.startswith("s")), 2 * inv()["slots_per_machine"])

    def test_unknown_budget_gets_one_session_per_machine(self):
        props = traffic.allocate(state(), inv())             # no BUDGET line from any login
        per = {p["who"]: cards([p]) for p in props if p["action"].startswith("start sessions")}
        self.assertEqual(per, {"JIS-NB": ["s0"], "JIS-NUC": ["s1"]}, props)

    def test_card_proposed_on_an_earlier_wake_is_not_proposed_again(self):
        """Review (Sonnet #7): a second wake before the worker's claim lands handed the same card to another machine."""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "reserved.json"
            first = traffic.allocate(state(), inv())
            traffic.save_reserved(T0, first, path)
            s = state()
            s["reserved"] = sorted(traffic.load_reserved(T0 + timedelta(minutes=5), path))
            again = cards(traffic.allocate(s, inv()))
            self.assertFalse(set(again) & set(cards(first)), (cards(first), again))
            self.assertFalse(traffic.load_reserved(T0 + timedelta(minutes=traffic.RESERVE_MIN + 1), path))

    def test_budget_throttles(self):
        i = inv()
        s = state(budgets={"B": {"five_h": 85}, "C": {"five_h": 85}, "A": {"five_h": 10}})
        s["queue"][0]["weight"] = "CRUCIAL"
        props = traffic.allocate(s, i)
        self.assertFalse([p for p in props if p["who"] == "JIS-NB"], props)     # both NB logins over 80%
        s = state(budgets={"B": {"five_h": 65}, "C": {"five_h": 65}, "A": {"five_h": 85}})
        s["queue"][3]["weight"] = "CRUCIAL"
        props = traffic.allocate(s, i)
        nb = [p for p in props if p["who"] == "JIS-NB"]
        self.assertEqual(cards(nb), ["s3"], props)                               # 60-80%: CRUCIAL only

    def test_silent_machine_with_claims_goes_to_pipeliner_never_auto_release(self):
        s = state()
        s["machines"]["DESKTOP-F7IU69N"]["open_claims"] = 2
        props = traffic.allocate(s, inv())
        p = [p for p in props if p["who"] == "Pipeliner"]
        self.assertEqual(len(p), 1, props)
        self.assertIn("release only by claim rules", p[0]["action"])

    def test_unreadable_lease_fails_closed(self):
        s = state(leases={"Pipeliner": {"state": "unknown", "error": "fetch failed"}},
                  desk={"pending": 5})
        props = traffic.allocate(s, inv())
        self.assertTrue(any(p["who"] == "operator" and "run nothing as Pipeliner" in p["action"] for p in props))
        self.assertFalse(any("You are Pipeliner" in p["action"] for p in props))

    def test_free_pipeliner_lease_with_pending_desk_starts_one_on_preferred_host(self):
        s = state(leases={"Pipeliner": {"state": "expired"}}, desk={"pending": 3})
        props = [p for p in traffic.allocate(s, inv()) if "You are Pipeliner" in p["action"]]
        self.assertEqual([p["who"] for p in props], ["JIS-NUC"])


class Measure(unittest.TestCase):
    def c(self, sha, mins, subject, body="", email="x@y", parents=("p",)):
        return {"sha": sha, "parents": list(parents), "at": T0 + timedelta(minutes=mins), "email": email,
                "subject": subject, "body": body}

    def test_overlap_vs_retry(self):
        cs = [self.c("1", 0, "claim a"), self.c("2", 5, "release a"), self.c("3", 9, "claim a"),
              self.c("4", 20, "claim b"), self.c("5", 21, "claim b")]
        got = traffic.overlapping_claims(cs, {"4": "JIS-NB", "5": "JIS-NUC"})
        self.assertEqual(list(got), ["b"])
        self.assertEqual(got["b"][1], "JIS-NUC 10-18T12:21Z")

    def test_lab_runner_own_claim_is_not_a_second_lane(self):
        cs = [self.c("1", 0, "claim x"), self.c("2", 0, "claim y")]
        host = {"1": "JIS-NUC", "2": "DESKTOP-F7IU69N"}
        codex = [{"start": T0 + timedelta(minutes=2), "end": T0 + timedelta(minutes=30), "card": "x"}]
        gem = [{"start": T0 + timedelta(minutes=2), "end": T0 + timedelta(minutes=30), "card": "y"}]
        traffic._INV.update(inv())
        d = traffic.duplicates(cs, host, [], codex, gem)
        self.assertNotIn("x", d["cards_worked_by_two_lanes"])
        self.assertEqual(d["cards_worked_by_two_lanes"]["y"], ["claude:DESKTOP-F7IU69N", "gemini-nuc"])

    def test_pipeliner_runs_count_work_commits_not_mentions(self):
        cs = [self.c("1", 0, "pipeliner: drain table"), self.c("2", 5, "session-planner & pipeliner: triage"),
              self.c("3", 9, "roles: fix stale texts (Pipeliner drain done)")]
        traffic._INV.update(inv())
        d = traffic.duplicates(cs, {"1": "JIS-NUC", "2": "DESKTOP-F7IU69N", "3": "JIS-NUC"}, [], [], [])
        self.assertEqual(sorted(d["pipeliner_runs_by_host"]), ["DESKTOP-F7IU69N", "JIS-NUC"])
        self.assertEqual(len(d["pipeliner_runs_by_host"]["JIS-NUC"]), 1)

    def test_claim_released_before_the_lab_run_is_not_a_duplicate(self):
        """Review (Sonnet #8): a set over 72 h counted claim -> release -> later lab run as two lanes at once."""
        cs = [self.c("1", 0, "claim z"), self.c("2", 20, "release z")]
        gem = [{"start": T0 + timedelta(minutes=40), "end": T0 + timedelta(minutes=60), "card": "z"}]
        traffic._INV.update(inv())
        d = traffic.duplicates(cs, {"1": "DESKTOP-F7IU69N", "2": "DESKTOP-F7IU69N"}, [], [], gem)
        self.assertNotIn("z", d["cards_worked_by_two_lanes"])
        self.assertIn("z", d["cards_claimed_by_two_hosts_in_turn"])

    def test_hours_and_gap(self):
        since = T0
        b = traffic.busy_hours([T0 + timedelta(minutes=10)], [(T0 + timedelta(hours=5), T0 + timedelta(hours=6, minutes=1))],
                               since, 10)
        self.assertEqual(b, {0, 5, 6})
        self.assertEqual(traffic.longest_gap(b, 10), 4)
        r = traffic.summarize("lane x", [], [], since, 10, "src", "no log")
        self.assertIsNone(r["idle_h"])            # unreadable source is unknown, never idle

    def test_gemini_log_parse(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "card-a.log"
            p.write_text("stuff\nEXIT 0 after 600s\n")
            end = (T0 + timedelta(hours=1)).timestamp()
            os.utime(p, (end, end))
            q = Path(d) / "card-b.log"
            q.write_text("still going\n")
            os.utime(q, (end, end))
            got = {g["card"]: g for g in traffic.read_gemini(d, T0, T0 + timedelta(hours=1, minutes=10))[0]}
        self.assertEqual(got["card-a"]["state"], "done")
        self.assertEqual(got["card-a"]["start"], T0 + timedelta(minutes=50))
        self.assertEqual(got["card-b"]["state"], "running")

    def test_liveness_and_budget_lines(self):
        i = inv()
        self.assertEqual(traffic.liveness(T0 - timedelta(minutes=10), T0, i), "ACTIVE")
        self.assertEqual(traffic.liveness(T0 - timedelta(minutes=100), T0, i), "IDLE")
        self.assertEqual(traffic.liveness(None, T0, i), "SILENT")
        b = traffic.budgets_from_signals([(T0, "jis-nb/?", "info", "BUDGET login=B 5h=42% week=30%"),
                                          (T0 + timedelta(minutes=1), "jis-nb/?", "info", "BUDGET login=B 5h=44% week=31%")])
        self.assertEqual(b["B"]["five_h"], 44)

    def test_budget_lines_carry_reset_and_pacing_state_per_login(self):
        """Operator 2026-10-20: SPEND/NORMAL/THROTTLE per Claude login from the newest BUDGET line, plus overall."""
        reset = (T0 + timedelta(hours=84)).strftime("%Y-%m-%dT%H:%MZ")          # half the week left: f = 0.5
        sigs = [(T0 - timedelta(minutes=5), "jis-nb/?", "note", f"BUDGET login=A 5h=10% week=30% reset={reset}"),   # 30 < 40: SPEND
                (T0 - timedelta(minutes=4), "jis-nuc/?", "note", f"BUDGET login=B 5h=10% week=48% reset={reset}"),  # on pace
                (T0 - timedelta(minutes=3), "jis-nb/?", "note", f"BUDGET login=C 5h=90% week=40% reset={reset}")]   # 5 h > 80
        b = traffic.budgets_from_signals(sigs)
        self.assertEqual(b["A"]["reset"], reset)
        v = traffic.spend_view(b, T0)
        self.assertEqual({k: r["state"] for k, r in v["logins"].items()}, {"A": "SPEND", "B": "NORMAL", "C": "THROTTLE"})
        self.assertEqual(v["overall"], "SPEND")
        self.assertIn("login A: SPEND", traffic.render_spend(v))

    def test_pacing_reset_in_the_past_or_over_a_week_away_is_unusable(self):
        """Review fix: a past reset gave f=1 (SPEND under 90%); a reset >168 h away gave f=0 (THROTTLE above 5%)."""
        at = (T0 - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%MZ")
        past = (T0 - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%MZ")
        far = (T0 + timedelta(hours=200)).strftime("%Y-%m-%dT%H:%MZ")
        self.assertEqual(traffic.pacing_state({"week": 50, "five_h": 5, "reset": past, "at": at}, T0)[0], "NORMAL")
        self.assertEqual(traffic.pacing_state({"week": 50, "five_h": 5, "reset": far, "at": at}, T0)[0], "NORMAL")

    def test_pacing_over_pace_stale_and_missing(self):
        reset = (T0 + timedelta(hours=84)).strftime("%Y-%m-%dT%H:%MZ")
        at = (T0 - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%MZ")
        self.assertEqual(traffic.pacing_state({"week": 60, "five_h": 5, "reset": reset, "at": at}, T0)[0], "THROTTLE")   # 60 > 55
        old = (T0 - timedelta(hours=7)).strftime("%Y-%m-%dT%H:%MZ")
        self.assertEqual(traffic.pacing_state({"week": 1, "five_h": 1, "reset": reset, "at": old}, T0)[0], "NORMAL")      # stale never SPEND
        self.assertEqual(traffic.pacing_state({"week": 1, "five_h": 1, "at": at}, T0)[0], "NORMAL")                        # no reset time
        soon = (T0 + timedelta(hours=10)).strftime("%Y-%m-%dT%H:%MZ")
        self.assertEqual(traffic.pacing_state({"week": 80, "five_h": 5, "reset": soon, "at": at}, T0)[0], "SPEND")       # <24 h left, <85
        self.assertEqual(traffic.spend_view({}, T0)["overall"], "UNKNOWN")
        allt = {l: {"week": 99, "five_h": 99, "reset": reset, "at": at} for l in "AB"}
        self.assertEqual(traffic.spend_view(allt, T0)["overall"], "THROTTLE")

    def test_attribution_by_author_email(self):
        cs = [self.c("1", 0, "some commit", email="e-ngineers@DESKTOP-F7IU69N")]
        inv_data = inv()
        host = traffic.attribute_commits(REPO, cs, [], inv_data)
        self.assertEqual(host.get("1"), "DESKTOP-F7IU69N")

    def test_inventory_has_no_emails(self):
        text = (REPO / traffic.INVENTORY).read_text(encoding="utf-8")
        self.assertNotRegex(text, r"[\w.]+@[\w-]+\.(com|org|net)")


if __name__ == "__main__":
    unittest.main()
