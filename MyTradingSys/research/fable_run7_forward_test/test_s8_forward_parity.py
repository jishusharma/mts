"""R7 replay parity test (FORWARD_PREREG.md section 1, steps 1-5): the live decision code must reproduce R6's BTC S8 4h events.

Oracle A  = e2_run.signals + e2_run.stop_for on cached BTCUSDT 4h DEV klines (2020-01-01..2024-06-30, counts_only.load).
Candidate B = krown_live.s8_events(bars in the runner's klines_to_bars shape).  PASS iff A == B (0 mismatches, diff printed).

Contract the build card (krown-s8-4h-testnet-build) must satisfy, in MyTradingSys/backtest/layers/krown/krown_live.py:
  s8_events(bars) -> [alert dict]   bars = [{"t","o","h","l","c","v","tbv"}], closed bars only; alert =
      {layer:"krown", sub:"s8_break", event:"S8", tf:"4h", t_close:<signal bar OPEN ms>, side:"long"|"short",
       entry_price:<signal close>, stop:<far side of bars i-9..i>, bbwp:<float>}
  decide(alert, mark, position_flat) -> "take" | "skipped_busy" | "skipped_floor"
      mark = last price at decision time (the parity test passes the next bar's open); floor = |mark-stop|/mark < 0.0056.
Import failure = FAIL (never skip). Reads only cached bars < 2024-07-01; run: python -m unittest test_s8_forward_parity -v
"""
import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
MTS = HERE.parents[1]                                   # .../MyTradingSys
sys.path.insert(0, str(MTS.parent))
sys.path.insert(0, str(MTS / "research" / "fable_run6_powered_prereg"))
sys.path.insert(0, str(MTS / "backtest" / "layers" / "krown"))
sys.path.insert(0, str(MTS / "execution"))
import counts_only as co  # noqa: E402
import e2_run as e2  # noqa: E402

H4_MS = 4 * 3600 * 1000
EXPECTED_EVENTS = 277            # COUNTS.csv BTCUSDT DEV 135 + DEV_EXT 142
SIDE = {1: "long", -1: "short"}
_CACHE = {}


def load_bars():
    if "bars" not in _CACHE:
        rows, _ = co.load("BTCUSDT", "4h", lambda *_: None)
        co.guard(rows, "BTCUSDT 4h")
        _CACHE["bars"] = rows
    return _CACHE["bars"]


def to_runner_bars(rows):
    return [{"t": r[0], "o": r[1], "h": r[2], "l": r[3], "c": r[4], "v": 0.0, "tbv": 0.0} for r in rows]


def in_window(t):
    return e2.LO_MS <= t < e2.HI_MS


def oracle_set(rows):
    return {(rows[i][0], SIDE[s], e2.stop_for(rows, i, s)) for i, s in e2.signals(rows) if in_window(rows[i][0])}


def candidate_set(alerts):
    return {(a["t_close"], a["side"], a["stop"]) for a in alerts if in_window(a["t_close"])}


def diff_rows(a, b):
    return sorted(a - b) + sorted(b - a)


def import_live():
    import krown_live  # ImportError propagates: the test FAILS, never skips
    return krown_live


def oracle_decisions(rows):
    """Per in-window oracle signal: 'take' | 'skipped_busy' | 'skipped_floor' (same loop as e2_run.simulate_symbol)."""
    out, free_from = {}, -1
    for i, s in e2.signals(rows):
        t = rows[i][0]
        if not in_window(t) or i + 1 >= len(rows):
            continue
        if i < free_from:
            out[t] = "skipped_busy"
            continue
        tr = e2.run_trade(s, rows, i + 1, e2.stop_for(rows, i, s))
        if tr is None:
            out[t] = "skipped_floor"
            continue
        free_from = tr["exit_i"]
        out[t] = "take"
    return out


class FreezeAndGuard(unittest.TestCase):
    def test_oracle_event_count_within_freeze_bar(self):
        n = len(oracle_set(load_bars()))
        self.assertLessEqual(abs(n - EXPECTED_EVENTS), EXPECTED_EVENTS * 0.01, f"|A|={n}, expected {EXPECTED_EVENTS} +-1 %")

    def test_no_bar_at_or_after_cut_is_loaded(self):
        self.assertLess(max(r[0] for r in load_bars()), co.CUT_MS)

    def test_planted_sealed_timestamp_is_refused(self):
        planted = list(load_bars()) + [(co.CUT_MS, 1.0, 1.0, 1.0, 1.0)]   # synthetic bar, no price data
        with self.assertRaises(ValueError):
            co.guard(planted, "planted")


def _gate_marker():
    """Gate only: until krown_live exists the live-parity class is a STRICT xfail under pytest, so the smoke gate stays green while
    the tree has no build; once krown_live is on the tree the marker is off and every test must pass. Plain `python -m unittest`
    ignores marks: there the missing build FAILS (the recorded pre-build run)."""
    try:
        import pytest
    except ImportError:
        return lambda c: c
    built = importlib.util.find_spec("krown_live") is not None
    return pytest.mark.xfail(condition=not built, strict=True, reason="krown-s8-4h-testnet-build not shipped (krown_live missing)")


@_gate_marker()
class LiveParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_bars()
        cls.live = import_live()                         # ImportError = FAIL
        cls.alerts = cls.live.s8_events(to_runner_bars(cls.rows))
        cls.A = oracle_set(cls.rows)
        cls.B = candidate_set(cls.alerts)

    def test_batch_parity_zero_mismatches(self):
        d = diff_rows(self.A, self.B)
        for r in d:
            print("MISMATCH", "oracle-only" if r in self.A else "live-only", r)
        self.assertEqual(d, [], f"{len(d)} mismatches; |A|={len(self.A)} |B|={len(self.B)}")
        self.assertEqual(len(self.A), len(self.B))

    def test_planted_mismatch_is_detected(self):
        self.assertTrue(self.B, "candidate produced no events")
        victim = sorted(self.B)[len(self.B) // 2]
        d = diff_rows(self.A, self.B - {victim})
        self.assertEqual(d, [victim] if victim in self.A else d)
        self.assertGreaterEqual(len(d), 1)

    def test_no_event_inside_sealed_period(self):
        self.assertTrue(all(a["t_close"] < co.CUT_MS for a in self.alerts))

    def test_incremental_parity_last_300_bars(self):
        bars = to_runner_bars(self.rows)
        n = len(bars)
        batch = {(a["t_close"], a["side"], a["stop"]) for a in self.alerts if a["t_close"] >= bars[n - 300]["t"]}
        inc = set()
        for k in range(n - 299, n + 1):                  # newest bar index k-1; only events ON the newest bar count
            newest = bars[k - 1]["t"]
            inc |= {(a["t_close"], a["side"], a["stop"]) for a in self.live.s8_events(bars[:k]) if a["t_close"] == newest}
        self.assertEqual(diff_rows(batch, inc), [], "incremental run differs from batch (look-ahead or repaint)")

    def test_layer_signal_checks_and_skip_counts(self):
        import auto_trader as at
        cfg = at.load_config(MTS / "execution" / "auto_trader_config.json")
        by_t = {r[0]: i for i, r in enumerate(self.rows)}
        want = oracle_decisions(self.rows)
        got = {}
        free_from = -1
        for a in sorted((x for x in self.alerts if in_window(x["t_close"])), key=lambda x: x["t_close"]):
            i = by_t[a["t_close"]]
            if i + 1 >= len(self.rows):
                continue
            flat = i >= free_from
            d = self.live.decide(a, self.rows[i + 1][1], flat)
            got[a["t_close"]] = d
            if d != "take":
                continue
            s = 1 if a["side"] == "long" else -1
            tr = e2.run_trade(s, self.rows, i + 1, a["stop"])
            free_from = tr["exit_i"] if tr else free_from
            now = datetime.fromtimestamp((a["t_close"] + H4_MS) / 1000 + 60, timezone.utc)
            sig = at.layer_signal(a, cfg, now)
            self.assertNotIn("reject", sig, f"{a['t_close']}: {sig.get('reject')}")
            args = sig["plan_args"]
            arg = lambda k: args[args.index(k) + 1]
            stop_pct = round(abs(a["entry_price"] - a["stop"]) / a["entry_price"] * 100, 4)
            self.assertAlmostEqual(float(arg("--stop")), stop_pct, places=4)
            self.assertAlmostEqual(float(arg("--targets")), 2 * stop_pct, delta=2e-4)
            self.assertEqual(float(arg("--max-hold-minutes")), 24000.0)
        cnt = lambda m, k: sum(1 for v in m.values() if v == k)
        for k in ("take", "skipped_busy", "skipped_floor"):
            self.assertEqual(cnt(got, k), cnt(want, k), f"{k}: live {cnt(got, k)} vs oracle {cnt(want, k)}")
        self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main(verbosity=2)
