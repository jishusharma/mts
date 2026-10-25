"""hosts.py: the machine rename (JIS-NB -> JIS-DESKTOP, DESKTOP-F7IU69N -> JIS-LAPTOP) must not break any old state."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hosts  # noqa: E402
import live_owner as lo  # noqa: E402
import mts_signal as S  # noqa: E402
import supervisor  # noqa: E402

NOW = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)


class HostsTest(unittest.TestCase):
    def test_canonical_maps_old_and_new_case_insensitive(self):
        for n in ("JIS-NB", "jis-nb", "Jis-Desktop", "the desktop", "JIS-NB.lan"):
            self.assertEqual(hosts.canonical(n), "JIS-DESKTOP", n)
        for n in ("DESKTOP-F7IU69N", "desktop-f7iu69n", "JIS-LAPTOP", "the Lenovo laptop"):
            self.assertEqual(hosts.canonical(n), "JIS-LAPTOP", n)
        self.assertEqual(hosts.canonical("jis-nuc"), "JIS-NUC")
        self.assertEqual(hosts.canonical("Some-Other"), "Some-Other")          # unknown: unchanged
        self.assertEqual(hosts.canonical(""), "")

    def test_round_trip_and_same_host(self):
        for c in hosts.HOSTS:
            self.assertEqual(hosts.canonical(hosts.canonical(c)), c)
            for a in hosts.aliases(c):
                self.assertTrue(hosts.same_host(a, c))
                self.assertEqual(hosts.canonical(a), c)
        self.assertFalse(hosts.same_host("JIS-NB", "DESKTOP-F7IU69N"))
        self.assertFalse(hosts.same_host("", ""))
        self.assertTrue(hosts.same_host("x", "X"))

    def test_unc_tries_new_name_first_old_second(self):
        self.assertEqual(hosts.unc_hosts("JIS-NB"), ["JIS-DESKTOP", "JIS-NB"])
        self.assertEqual(hosts.unc_path("JIS-NB", "MTS-Queue"), chr(92) * 2 + "JIS-DESKTOP" + chr(92) + "MTS-Queue")   # neither reachable: new name

    def test_owner_file_written_under_old_name_matches_new_host(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "live_owner.json").write_text(json.dumps({"host": "jis-nb", "heartbeat": (NOW - timedelta(seconds=5)).isoformat()}), encoding="utf-8")
            self.assertTrue(lo.check(d, "jis-desktop", NOW)[0])               # same machine: allowed (restart), not "owned by a peer"
            self.assertTrue(lo.claim(d, "JIS-DESKTOP", NOW)[0])
            self.assertFalse(lo.check(d, "jis-laptop", NOW)[0])               # a different machine is still refused
            self.assertTrue(lo.release(d, "jis-desktop")[0])
            self.assertFalse((Path(d) / "live_owner.json").exists())

    def test_ack_under_old_name_counts_for_new_host(self):
        ack = {"t": S.stamp(S.now()), "kind": "ack", "id": "b-old111", "state": "done", "host": "jis-nb"}
        self.assertEqual(S.ack_state([ack], "b-old111", "jis-desktop"), "done")
        self.assertEqual(S.ack_state([ack], "b-old111", "jis-laptop"), "none")
        bc = {"t": S.stamp(S.now()), "kind": "broadcast", "prio": "high", "id": "b-old111", "to": "desktop-f7iu69n", "from": "x/C"}
        self.assertTrue(S.to_me(bc["to"], "jis-laptop"))
        self.assertFalse(S.to_me(bc["to"], "jis-desktop"))
        self.assertEqual(S.hosts_seen([ack, {**ack, "host": "JIS-DESKTOP"}]), {"jis-desktop"})

    def test_host_named_shows_new_name_with_noun(self):
        keep = os.environ.get("MTS_SIGNALS_HOST")
        try:
            os.environ["MTS_SIGNALS_HOST"] = "jis-nb"
            self.assertEqual(S.host_named(), "JIS-DESKTOP (the desktop)")
            os.environ["MTS_SIGNALS_HOST"] = "DESKTOP-F7IU69N"
            self.assertEqual(S.host_named(), "JIS-LAPTOP (the Lenovo laptop)")
            os.environ["MTS_SIGNALS_HOST"] = "jis-laptop"
            self.assertEqual(S.host_named(), "JIS-LAPTOP (the Lenovo laptop)")
            os.environ["MTS_SIGNALS_HOST"] = "jis-nuc"
            self.assertEqual(S.host_named(), "JIS-NUC (the NUC)")
        finally:
            if keep is None:
                os.environ.pop("MTS_SIGNALS_HOST", None)
            else:
                os.environ["MTS_SIGNALS_HOST"] = keep
        self.assertEqual(S.MACHINE_NOUN["JIS-NB"], "the desktop")
        self.assertEqual(S.MACHINE_NOUN["JIS-LAPTOP"], "the Lenovo laptop")

    def test_supervisor_host_rules_follow_the_machine_not_the_spelling(self):
        self.assertEqual(supervisor.weekly_cap("B", "JIS-DESKTOP"), supervisor.weekly_cap("B", "JIS-NB"))
        self.assertEqual(supervisor.weekly_cap("B", "jis-desktop"), 75)
        self.assertEqual(supervisor.lane_owner({"A": {"host": "JIS-NB"}}, "jis-desktop"), "A")
        rows = [{"id": "c1", "lane": "JIS-NB"}]
        self.assertEqual(len(supervisor.pick_cards(rows, "JIS-DESKTOP", 3, live="JIS-NB")), 1)


if __name__ == "__main__":
    unittest.main()
