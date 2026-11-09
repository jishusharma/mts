"""LEVEL TOUCH + SESSION BRIEF in the live loop (card level-touch-alerts-session-brief-1109). Alerts only: no order, size or gate."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from MyTradingSys.backtest.layers.alerts import live_level_touch as lt

UTC = timezone.utc


def ms(y, mo, d, h, mi):
    return int(datetime(y, mo, d, h, mi, tzinfo=UTC).timestamp() * 1000)


def bar(t, lo, hi):
    return {"t": t, "o": (lo + hi) / 2, "h": hi, "l": lo, "c": (lo + hi) / 2}


LEVELS = [dict(key="an:Michael:73500", level=73_500.0, who="Michael", side="buy", kind="analyst"),
          dict(key="PDH", level=76_000.0, who="PDH", side="", kind="system")]
T = ms(2026, 11, 8, 21, 55)


def read_lines(p):
    return Path(p).read_text(encoding="utf-8").splitlines()


class Touch(unittest.TestCase):
    def test_wick_within_tolerance_fires_1108_case(self):
        ev, st = lt.touch_events(LEVELS, [bar(T, 73_510.0, 73_700.0)], lt.empty_state(), T + 60_000)
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["level"], e["who"], e["side"]), (73_500.0, "Michael", "buy"))
        self.assertEqual(e["price"], 73_510.0)
        self.assertEqual(e["symbol"], "BTCUSDT")
        self.assertIn("2026-11-08T21:55", e["utc"])
        self.assertIn("LEVEL TOUCH", e["text"])

    def test_no_touch_no_alert(self):
        ev, _ = lt.touch_events(LEVELS, [bar(T, 73_900.0, 74_000.0)], lt.empty_state(), T + 60_000)
        self.assertEqual(ev, [])

    def test_once_per_level_per_utc_day(self):
        ev1, st = lt.touch_events(LEVELS, [bar(T, 73_510.0, 73_700.0)], lt.empty_state(), T + 60_000)
        ev2, st = lt.touch_events(LEVELS, [bar(T + 60_000, 73_480.0, 73_600.0)], st, T + 120_000)
        self.assertEqual((len(ev1), len(ev2)), (1, 0))
        nxt = ms(2026, 11, 9, 0, 5)
        ev3, st = lt.touch_events(LEVELS, [bar(nxt, 73_480.0, 73_600.0)], st, nxt + 60_000)
        self.assertEqual(len(ev3), 1)

    def test_state_file_survives_restart(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            _, st = lt.touch_events(LEVELS, [bar(T, 73_510.0, 73_700.0)], lt.empty_state(), T + 60_000)
            lt.save_state(st, p)
            ev, _ = lt.touch_events(LEVELS, [bar(T + 60_000, 73_490.0, 73_520.0)], lt.load_state(p), T + 120_000)
            self.assertEqual(ev, [])

    def test_touched_since_brief_is_recorded(self):
        _, st = lt.touch_events(LEVELS, [bar(T, 73_510.0, 73_700.0)], lt.empty_state(), T + 60_000)
        self.assertEqual([x["level"] for x in st["since_brief"]], [73_500.0])


class Poll(unittest.TestCase):
    def run_poll(self, d, fetch, levels=lambda now: LEVELS, now=None):
        return lt.poll(fetch, levels, Path(d) / "st.json", Path(d) / "alerts", Path(d) / "toasts.jsonl", now or T + 90_000)

    def test_alert_lands_in_log_and_toast(self):
        with tempfile.TemporaryDirectory() as d:
            out = self.run_poll(d, lambda: [bar(T, 73_510.0, 73_700.0)])
            self.assertEqual(len(out), 1)
            log = read_lines(Path(d) / "alerts" / "level_touch.jsonl")
            self.assertEqual(json.loads(log[0])["layer"], "level_touch")
            self.assertIn("LEVEL TOUCH", json.loads(read_lines(Path(d) / "toasts.jsonl")[0])["text"])

    def test_restart_does_not_refire(self):
        with tempfile.TemporaryDirectory() as d:
            self.run_poll(d, lambda: [bar(T, 73_510.0, 73_700.0)])
            again = self.run_poll(d, lambda: [bar(T, 73_510.0, 73_700.0)], now=T + 150_000)
            self.assertEqual(again, [])
            self.assertEqual(len(read_lines(Path(d) / "toasts.jsonl")), 1)

    def test_api_error_fails_closed_one_degraded_line(self):
        def boom():
            raise OSError("fapi blocked")
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_poll(d, boom), [])
            self.assertEqual(self.run_poll(d, boom, now=T + 150_000), [])  # still down: no second line
            lines = read_lines(Path(d) / "alerts" / "level_touch.jsonl")
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["event"], "LEVEL TOUCH DEGRADED")
            self.assertFalse((Path(d) / "toasts.jsonl").exists())
            out = self.run_poll(d, lambda: [bar(T, 73_510.0, 73_700.0)], now=T + 210_000)  # recovered: fires
            self.assertEqual(len(out), 1)

    def test_levels_error_fails_closed(self):
        def bad(now):
            raise ValueError("cbp unreadable")
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_poll(d, lambda: [bar(T, 73_510.0, 73_700.0)], levels=bad), [])


class Brief(unittest.TestCase):
    NOW = ms(2026, 11, 9, 7, 2)

    def test_due_slots_once_per_day(self):
        st = lt.empty_state()
        self.assertIsNone(lt.due_brief(ms(2026, 11, 9, 6, 59), st))
        self.assertEqual(lt.due_brief(self.NOW, st), "EU")
        st["brief_done"] = ["2026-11-09|EU"]
        self.assertIsNone(lt.due_brief(self.NOW, st))
        self.assertEqual(lt.due_brief(ms(2026, 11, 9, 13, 31), st), "US")
        self.assertIsNone(lt.due_brief(ms(2026, 11, 9, 20, 0), st))  # a late restart never sends a stale brief

    def test_text_two_zones_each_side_deduped_touches_event_scenarios(self):
        pts = [(75_000, "Krown"), (74_980, "Michael"), (74_000, "PDH"), (73_500, "Michael"), (73_000, "PDL"),
               (72_000, "VAL"), (76_500, "WO")]
        levels = [dict(key=f"k{i}", level=p, who=w, side="", kind="analyst") for i, (p, w) in enumerate(pts)]
        since = [dict(level=73_500.0, who="Michael", price=73_510.0, utc="2026-11-08T21:55Z")]
        txt = lt.brief_text("EU", 73_800.0, levels, since, "CPI 2026-11-10 12:30Z", ["pb-1", "pb-2"], self.NOW)
        self.assertIn("SESSION BRIEF", txt)
        self.assertIn("73,800", txt)
        self.assertEqual(txt.count("75,000") + txt.count("74,980"), 1)  # one zone
        self.assertIn("74,000", txt)
        self.assertNotIn("76,500", txt)  # third zone above
        self.assertIn("73,500", txt)
        self.assertIn("73,000", txt)
        self.assertNotIn("72,000", txt)  # third zone below
        self.assertIn("touched", txt)
        self.assertIn("CPI", txt)
        self.assertIn("pb-1", txt)

    def test_poll_emits_brief_once_and_resets_since(self):
        with tempfile.TemporaryDirectory() as d:
            kw = dict(price=73_800.0, next_event="none", scenario_ids=[])
            st_path = Path(d) / "st.json"
            _, st = lt.touch_events(LEVELS, [bar(T, 73_510.0, 73_700.0)], lt.empty_state(), T + 60_000)
            lt.save_state(st, st_path)

            def fetch():
                return [bar(self.NOW - 60_000, 73_790.0, 73_810.0)]

            def go(now):
                return lt.poll(fetch, lambda n: LEVELS, st_path, Path(d) / "alerts", Path(d) / "toasts.jsonl", now,
                               brief_ctx=lambda n: kw)
            self.assertEqual([a["event"] for a in go(self.NOW)], ["SESSION BRIEF"])
            self.assertEqual(go(self.NOW + 60_000), [])
            self.assertEqual(lt.load_state(st_path)["since_brief"], [])
            self.assertIn("SESSION BRIEF", (Path(d) / "toasts.jsonl").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
