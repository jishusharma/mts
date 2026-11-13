import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ship_timing_report as T


def w(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


class ShipTimingReport(unittest.TestCase):
    def test_stats_and_join(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            w(d / "t1" / "runtime_data" / "gate_timing.jsonl", [
                {"step": "ship_wall", "secs": 60, "ok": True, "utc": "2026-11-13T10:00:00Z", "sha": "aa"},
                {"step": "ship", "ok": True, "utc": "2026-11-13T10:00:00Z", "sha": "aa", "gate_mode": "smoke",
                 "gate_reason": "fast smoke: 1", "phases": {"slot_wait_s": 30}},
                {"step": "ship_wall", "secs": 600, "ok": False, "utc": "2026-11-13T11:00:00Z", "sha": "bb"},
                {"step": "ship_wall", "secs": 90, "ok": True, "utc": "2026-11-12T11:00:00Z", "sha": "cc"}])
            w(d / "home.jsonl", [{"step": "ship", "utc": "2026-11-13T11:00:01Z", "sha": "bb", "gate_mode": "full", "tree": "x"},
                                 {"step": "ship", "utc": "2026-11-13T11:30:00Z", "sha": "zz", "tree": "C:\\tmp\\mts_run_1\\w"}])
            ships, n = T.collect_ships(str(d), str(d / "home.jsonl"), T.parse_utc("2026-11-13T00:00:00Z"), T.parse_utc("2026-11-14T00:00:00Z"))
            self.assertEqual((n, len(ships)), (1, 2))
            s = T.ship_stats(ships)
            self.assertEqual((s["passed"], s["failed"], s["slow_n"], s["failed_min"], s["total_min"]), (1, 1, 1, 10.0, 11.0))
            self.assertEqual(s["slow_share"], 90.9)
            self.assertEqual(s["modes"], {"smoke": 1, "full": 1})
            self.assertEqual(s["slot_wait_rows"], 1)

    def test_empty_and_wait(self):
        self.assertEqual(T.ship_stats([]), {"ships": 0})
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "wait.log"
            w(p, [{"ts": "2026-11-13T10:00:00Z", "mode": "full", "wait_s": 600}, {"ts": "2026-11-01T10:00:00Z", "mode": "fast", "wait_s": 5}])
            r = T.slot_wait(str(p), T.parse_utc("2026-11-13T00:00:00Z"), T.parse_utc("2026-11-14T00:00:00Z"))
            self.assertEqual((r["rows"], r["by_mode"]["full"]["wait_min"]), (1, 10.0))


if __name__ == "__main__":
    unittest.main()
