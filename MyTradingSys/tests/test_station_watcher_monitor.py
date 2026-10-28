"""station_watcher_monitor.check_flags (design 2026-10-28_watcher-ship-flow-guard-design.md).
Fails on the old module: it had no functions and ran a forever loop on import."""
import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("station_watcher_monitor", REPO / "MyTradingSys/research/pipeliner/station_watcher_monitor.py")
swm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(swm)   # old module: never returns (while True); new one is import-safe


def status(queue=None, lanes=None):
    return {"machines": {}, "lanes": lanes or {}, "queue": queue or []}


def extras(lag=None, slots=None, claims=None):
    return {"green_lag_min": lag, "gate_slots": slots or [], "stale_claims": claims or []}


def slot(age, alive=True, name="slot-0", pid=123):
    return {"slot": name, "age_min": age, "pid": pid, "alive": alive}


class CheckFlags(unittest.TestCase):
    def flags(self, ex, st=None, prev=()):
        f, p = swm.check_flags(st or status(), ex, set(prev))
        return f, p

    def test_ci_lag_threshold(self):
        self.assertEqual(self.flags(extras(lag=19))[0], [])
        f, p = self.flags(extras(lag=21))
        self.assertEqual(f, ["CI-RED-20m"])
        self.assertTrue(p[0]["text"].startswith("[operator] last ship red"))

    def test_gate_slot_threshold_and_dead_pid(self):
        self.assertEqual(self.flags(extras(slots=[slot(19)]))[0], [])
        f, p = self.flags(extras(slots=[slot(21)]))
        self.assertEqual(f, ["GATE-HELD-slot-0-21m"])
        self.assertIn("held 21 min", p[0]["text"])
        self.assertEqual(self.flags(extras(slots=[slot(90, alive=False)]))[0], [])

    def test_stale_claim_threshold(self):
        c = lambda h: [{"slug": "x", "owner": "JIS-NB/a", "age_h": h}]
        self.assertEqual(self.flags(extras(claims=c(23)))[0], [])
        f, p = self.flags(extras(claims=c(25)))
        self.assertEqual(f, ["STALE-CLAIM-x"])
        self.assertIn("release or finish x", p[0]["text"])

    def test_lane_idle_needs_two_polls(self):
        st = status(queue=[{"id": "c1", "lane": "codex"}], lanes={"codex": {"state": "idle"}})
        f1, p1 = self.flags(extras(), st)
        self.assertNotIn("LANE-IDLE-codex", f1)
        self.assertEqual(p1, [])
        f2, p2 = self.flags(extras(), st, prev=f1)
        self.assertIn("LANE-IDLE-codex", f2)
        self.assertEqual(len(p2), 1)
        # no ready cards -> never flagged
        f3, _ = self.flags(extras(), status(lanes={"codex": {"state": "idle"}}), prev=f1)
        self.assertEqual([x for x in f3 if "IDLE" in x], [])

    def test_signal_once_per_appearance(self):
        ex = extras(lag=30)
        f, p = self.flags(ex)
        self.assertEqual(len(p), 1)
        f, p = self.flags(ex, prev=f)          # stays: none
        self.assertEqual(p, [])
        f, p = self.flags(extras(), prev=f)    # clears
        self.assertEqual((f, p), ([], []))
        f, p = self.flags(ex, prev=f)          # returns: one
        self.assertEqual(len(p), 1)

    def test_gate_minutes_changing_is_not_a_new_appearance(self):
        f, _ = self.flags(extras(slots=[slot(21)]))
        f2, p2 = self.flags(extras(slots=[slot(26)]), prev=f)
        self.assertEqual(f2, ["GATE-HELD-slot-0-26m"])
        self.assertEqual(p2, [])

    def test_malformed_extras_is_error_not_green(self):
        for bad in ({"green_lag_min": "abc", "gate_slots": [], "stale_claims": []},
                    {"green_lag_min": None, "gate_slots": "x", "stale_claims": []},
                    {"green_lag_min": None, "gate_slots": [], "stale_claims": [{"slug": "a"}]},
                    {}):
            f, p = self.flags(bad)
            self.assertTrue(any(x.startswith("MONITOR ERROR") for x in f), bad)
            self.assertEqual(p, [])


if __name__ == "__main__":
    unittest.main()
