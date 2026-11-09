"""Krown S8 4h live code tests (card krown-s8-4h-testnet-build). Offline, synthetic bars only (no bar >= 2024-07-01, no network).
Run: python -m pytest MyTradingSys/backtest/layers/krown/test_krown_live.py

Expected values are computed here independently (raw min/max over the bars, hand-written floor cases), not from krown_live.
"""
import contextlib
import io
import math
import random
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import krown_live as kl  # noqa: E402

T0, H4 = 1_600_000_000_000, 14_400_000


def mk(seed, n=900):
    """Alternating quiet / wild 60-bar blocks so BBWP compresses then expands: S8 fires several times."""
    r, p, out = random.Random(seed), 100.0, []
    for i in range(n):
        vol = 0.002 if (i // 60) % 2 == 0 else 0.02
        o = p
        c = o * (1 + r.gauss(0, vol))
        h = max(o, c) * (1 + abs(r.gauss(0, vol / 2)))
        l = min(o, c) * (1 - abs(r.gauss(0, vol / 2)))
        out.append({"t": T0 + i * H4, "o": o, "h": h, "l": l, "c": c, "v": 1.0, "tbv": 0.5})
        p = c
    return out


def quiet(fn, *a):
    with contextlib.redirect_stderr(io.StringIO()) as err:
        return fn(*a), err.getvalue()


class S8EventsTest(unittest.TestCase):
    def test_events_have_the_alert_fields_and_hand_computed_stop(self):
        bars = mk(3)
        ev = kl.s8_events(bars)
        self.assertGreaterEqual(len(ev), 3)
        by_t = {b["t"]: i for i, b in enumerate(bars)}
        for e in ev:
            i = by_t[e["t"]]
            self.assertGreaterEqual(i, 10)
            self.assertEqual(e["event"], "S8")
            self.assertEqual(e["entry_price"], bars[i]["c"])
            win = bars[i - 9:i + 1]
            self.assertEqual(e["stop"], min(b["l"] for b in win) if e["side"] == "long" else max(b["h"] for b in win))
            self.assertLess(e["stop"], e["entry_price"]) if e["side"] == "long" else self.assertGreater(e["stop"], e["entry_price"])
            self.assertTrue(math.isfinite(e["bbwp"]))

    def test_no_repaint_one_bar_incremental_equals_batch(self):
        for seed in (1, 4):
            bars = mk(seed)
            batch = {(e["t"], e["side"], e["stop"]) for e in kl.s8_events(bars)}
            inc = set()
            for k in range(200, len(bars) + 1):          # window grows one bar at a time; only events on the newest bar count
                inc |= {(e["t"], e["side"], e["stop"]) for e in kl.s8_events(bars[max(0, k - 300):k]) if e["t"] == bars[k - 1]["t"]}
            self.assertEqual(inc, {x for x in batch if x[0] >= bars[199]["t"]})

    def test_future_bars_never_change_past_events(self):
        bars = mk(2)
        cut = kl.s8_events(bars[:600])
        full = [e for e in kl.s8_events(bars) if e["t"] <= bars[599]["t"]]
        self.assertEqual(cut, full)

    def test_bad_input_fails_closed(self):
        bars = mk(3)
        self.assertEqual(kl.s8_events([]), [])
        shuffled = bars[:100] + [bars[50]] + bars[100:]
        out, err = quiet(kl.s8_events, shuffled)
        self.assertEqual(out, [])
        self.assertIn("krown_live", err)
        nan = [dict(b) for b in bars]
        nan[400]["c"] = float("nan")
        self.assertEqual(quiet(kl.s8_events, nan)[0], [])
        missing = [dict(b) for b in bars]
        del missing[10]["h"]
        self.assertEqual(quiet(kl.s8_events, missing)[0], [])
        self.assertEqual(quiet(kl.s8_events, bars[:50])[0], [])      # shorter than the BBWP warm-up: nothing, no crash


class DecideTest(unittest.TestCase):
    def a(self, side, stop):
        return {"side": side, "stop": stop}

    def test_floor_boundary_long_and_short(self):
        self.assertEqual(kl.decide(self.a("long", 99.44), 100.0, True), "take")             # risk 0.56 % = the floor: kept
        self.assertEqual(kl.decide(self.a("long", 99.45), 100.0, True), "skipped_floor")    # 0.55 %
        self.assertEqual(kl.decide(self.a("short", 100.56), 100.0, True), "take")
        self.assertEqual(kl.decide(self.a("short", 100.55), 100.0, True), "skipped_floor")

    def test_wrong_side_stop_is_a_floor_skip_never_an_order(self):
        self.assertEqual(kl.decide(self.a("long", 101.0), 100.0, True), "skipped_floor")
        self.assertEqual(kl.decide(self.a("short", 99.0), 100.0, True), "skipped_floor")

    def test_busy_is_checked_first_and_counts_as_busy(self):
        self.assertEqual(kl.decide(self.a("long", 90.0), 100.0, False), "skipped_busy")
        self.assertEqual(kl.decide(self.a("long", 99.9), 100.0, False), "skipped_busy")

    def test_garbage_fails_closed(self):
        for alert, mark in (({}, 100.0), (self.a("up", 90.0), 100.0), (self.a("long", None), 100.0), (self.a("long", 90.0), None),
                            (self.a("long", 90.0), float("nan")), (self.a("long", 90.0), 0), (self.a("long", float("inf")), 100.0)):
            self.assertEqual(kl.decide(alert, mark, True), "skipped_floor", (alert, mark))


class RunnerWiringTest(unittest.TestCase):
    def test_registry_carries_the_4h_krown_layer_and_the_runner_fetches_4h(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
        from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
        reg = cli.build_default_registry()
        e = reg["krown|s8_break|4h"]
        self.assertEqual((e["layer"], e["sub"], e["tf"], e["confirm_lag_bars"]), ("krown", "s8_break", "4h", 0))
        self.assertIn("4h", cli.HIST_TF_MS)
        self.assertEqual(cli.HIST_TF_MS["4h"], 4 * 3600 * 1000)
        src = Path(cli.__file__).read_text(encoding="utf-8")
        self.assertIn("4h", re.search(r'"--tfs",\s*default="([^"]+)"', src).group(1).split(","))

    def test_registered_layer_without_enough_history_stays_silent(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
        from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
        fn = cli.build_default_registry(history_fetch=lambda *a: (_ for _ in ()).throw(OSError("down")))["krown|s8_break|4h"]["fn"]
        out, err = quiet(fn, mk(3)[:99])               # 99 bars < 300 needed, history fetch errors: fail closed
        self.assertEqual(out, [])
        self.assertIn("history", err)


if __name__ == "__main__":
    unittest.main()
