"""T02-F3 part a: event-forcing look-ahead (causality) fixtures for testnet layers.

Why: the T02 truncation audit ran every layer of live_runner_cli.build_default_registry on seeded random walks;
five layers produced 0 events there, so "no difference between full and cut-the-future" was vacuous for them
(MyTradingSys/research/dsa_backtest_audit_2026-10-16/T02_lookahead_time.md, T02-F3). This file holds
  1. a shared harness (causal_report / assert_causal), the method of scripts/T02/t02_truncation.py, and
  2. hand-built bars that FORCE an event, so the comparison covers real events: rsi|malkan_bull|1h and
     positioning|funding_cvd_fade|1h (parts b/c of the card add the other layers).

Method (layer L, bars B, cut index k, T = open time of B[k], a CLOSED bar):
  full = L(B)   trunc = L(B[:k+1])   nan = L(B[:k+1] + NaN tail)   x10 = L(B[:k+1] + tail with o/h/l/c x 10)
  Look-ahead <=> the events stamped t <= T differ between full / nan / x10 and trunc.
  late = in full (t<=T) but not in trunc; repaint = in trunc but not in full (t<=T).
Layer code is NOT changed; the real layer functions are taken from the live registry.
"""
import copy
import json
import math
import unittest

from MyTradingSys.backtest.layers.alerts import live_layers as ll
from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli

H = 3600000
DAY = 86400000
T0 = (1790000000000 // DAY) * DAY  # UTC midnight


# --------------------------------------------------------------------------- shared harness

def _canon(e):
    def f(x):
        if isinstance(x, float):
            return None if math.isnan(x) else round(x, 9)
        if isinstance(x, dict):
            return {k: f(v) for k, v in sorted(x.items())}
        if isinstance(x, (list, tuple)):
            return [f(v) for v in x]
        return x
    return json.dumps(f(e), sort_keys=True, default=str)


def _keyed(events, t_max):
    """{(t, event): canonical json} of the events stamped <= t_max."""
    return {(e["t"], e.get("event")): _canon(e) for e in events if e.get("t") is not None and e["t"] <= t_max}


def _poison(tail, mode):
    out = []
    for b in tail:
        nb = dict(b)
        if mode == "nan":
            for k in ("o", "h", "l", "c", "v", "tbv", "delta", "buy_vol", "sell_vol"):
                if k in nb:
                    nb[k] = float("nan")
        else:
            for k in ("o", "h", "l", "c"):
                nb[k] = b[k] * 10.0
        out.append(nb)
    return out


def causal_report(layer_fn, bars, cuts, before_call=None):
    """Run the four-way comparison for every cut index and return the findings without asserting.

    layer_fn(bars) -> list of events with "t" (bar open ms) and "event". before_call(visible_bars) is called
    before every layer call with the bars that are legitimately known at the cut (bars[:k+1]; all bars for the
    full run): use it to answer injected network fetchers (funding, candles) as of the cut, never as of the end.
    Returns {"events_full", "compared", "late", "repaint", "nan", "x10"}: events_full = layer events on all bars;
    compared = events (t <= T) the comparison actually covered, summed over the cuts (0 means a vacuous test);
    the other four are lists of (cut_index, event_key) differences.
    """
    def run(visible, bars_in):
        if before_call is not None:
            before_call(visible)
        return layer_fn(copy.deepcopy(bars_in))

    full = run(bars, bars)
    rep = {"events_full": len(full), "compared": 0, "late": [], "repaint": [], "nan": [], "x10": []}
    for k in cuts:
        T = bars[k]["t"]
        vis = bars[:k + 1]
        fwd_tail = bars[k + 1:]
        f = _keyed(full, T)
        tr = _keyed(run(vis, vis), T)
        rep["compared"] += len(tr)
        for key in sorted(set(f) - set(tr), key=str):
            rep["late"].append((k, key))
        for key in sorted(set(tr) - set(f), key=str):
            rep["repaint"].append((k, key))
        for mode in ("nan", "x10"):
            po = _keyed(run(vis, vis + _poison(fwd_tail, mode)), T)
            for key in sorted(set(po) ^ set(tr), key=str):
                rep[mode].append((k, key))
            for key in set(po) & set(tr):
                if po[key] != tr[key]:
                    rep[mode].append((k, key))
    return rep


def assert_causal(layer_fn, bars, cuts, before_call=None, min_events=1):
    """Fail on any late / repaint / NaN-tail / x10-tail difference, and on a vacuous fixture (< min_events events
    on all bars, or none covered by the cuts). Returns the report."""
    rep = causal_report(layer_fn, bars, cuts, before_call)
    if rep["events_full"] < min_events:
        raise AssertionError("fixture is vacuous: %d events on all bars (need >= %d)" % (rep["events_full"], min_events))
    if rep["compared"] < 1:
        raise AssertionError("fixture is vacuous: no event stamped <= a cut bar was compared")
    bad = {k: rep[k] for k in ("late", "repaint", "nan", "x10") if rep[k]}
    if bad:
        raise AssertionError("look-ahead differences: %r" % (bad,))
    return rep


def _bars_from_closes(closes, o0=100.0, t0=T0, step=H, pad=0.2, v=10.0):
    """Gap-free 1h bars (open = previous close)."""
    out, p = [], o0
    for i, c in enumerate(closes):
        out.append({"t": t0 + i * step, "o": p, "h": max(p, c) + pad, "l": min(p, c) - pad, "c": c,
                    "v": v, "tbv": v / 2.0})
        p = c
    return out


# --------------------------------------------------------------------------- planted peeks (harness self-test)

def fwd_peek_next_bar_layer(bars):
    """PLANTED look-ahead: an event on bar i only if the NEXT bar closed higher (reads bars[i+1])."""
    return [{"t": bars[i]["t"], "side": "long", "event": "peek_next"}
            for i in range(len(bars) - 1) if bars[i + 1]["c"] > bars[i]["c"]]


def peek_tail_layer(bars):
    """PLANTED look-ahead: bar 2 gets an event only if the LAST bar (the future at any cut) is far above bar 0."""
    if len(bars) > 3 and bars[-1]["c"] > bars[0]["c"] * 5:
        return [{"t": bars[2]["t"], "side": "long", "event": "peek_tail"}]
    return []


class TestHarnessSelfTest(unittest.TestCase):
    BARS = _bars_from_closes([100 + (i % 4) * 2 - (i % 3) for i in range(30)])

    def test_next_bar_peek_is_detected_as_late(self):
        rep = causal_report(fwd_peek_next_bar_layer, self.BARS, range(5, 29))
        self.assertGreater(rep["events_full"], 0)
        self.assertTrue(rep["late"], rep)  # event on bar k is in the full run but not in the cut at k
        with self.assertRaises(AssertionError):
            assert_causal(fwd_peek_next_bar_layer, self.BARS, range(5, 29))

    def test_tail_peek_is_detected_by_x10_poison(self):
        rep = causal_report(peek_tail_layer, self.BARS, range(5, 29))
        self.assertTrue(rep["x10"], rep)  # the x10 tail makes the event appear; the clean cut has none
        with self.assertRaises(AssertionError):
            assert_causal(peek_tail_layer, self.BARS, range(5, 29), min_events=0)

    def test_causal_layer_passes_and_vacuous_fixture_fails(self):
        def causal(bars):
            return [{"t": b["t"], "side": "long", "event": "up"} for i, b in enumerate(bars) if i and b["c"] > bars[i - 1]["c"]]
        rep = assert_causal(causal, self.BARS, range(5, 29))
        self.assertGreater(rep["compared"], 0)
        with self.assertRaises(AssertionError):
            assert_causal(lambda bars: [], self.BARS, range(5, 29))  # 0 events = the old vacuous case

    def test_planted_peek_wrapped_around_a_real_layer_is_detected(self):
        bars = TestMalkanBullCausal.bars()

        def leaky(b):  # real malkan_bull events, kept only once a later bar exists = reads the future
            ts = [x["t"] for x in b]
            return [e for e in ll.malkan_bull_layer(b) if ts.index(e["t"]) + 1 < len(b)]
        rep = causal_report(leaky, bars, range(30, len(bars)))
        self.assertTrue(rep["late"], rep)


# --------------------------------------------------------------------------- rsi|malkan_bull|1h

def _registry_fn(key, fetch_funding=None):
    reg = cli.build_default_registry(fetch_funding=fetch_funding or (lambda s, n: []), history_fetch=lambda *a, **k: [])
    fn = reg[key]["fn"]
    return getattr(fn, "raw", fn)


class TestMalkanBullCausal(unittest.TestCase):
    @staticmethod
    def bars():
        """30 bars +1 (Wilder RSI(14) saturates at 100 -> regime BULL), 12 bars -1 (RSI 93 ... 41, inside the
        40 +/- 2 band on bar 41), then +1 (RSI 45 on bar 42 leaves the band upward = MLK-S1 support, bullish candle).
        Computed by hand against rsi_core: bar 40 RSI 44, bar 41 RSI 41, bar 42 RSI 45."""
        closes = [100.0 + i for i in range(1, 31)]
        for _ in range(12):
            closes.append(closes[-1] - 1.0)
        for _ in range(6):
            closes.append(closes[-1] + 1.0)
        return _bars_from_closes(closes)

    def test_fixture_forces_the_expected_event(self):
        bars = self.bars()
        ev = _registry_fn("rsi|malkan_bull|1h")(bars)
        self.assertEqual(len(ev), 1, ev)
        self.assertEqual(ev[0]["t"], bars[42]["t"])
        self.assertEqual((ev[0]["side"], ev[0]["regime"], ev[0]["rule_id"]), ("long", "BULL", "MLK-S1"))
        self.assertGreater(bars[42]["c"], bars[42]["o"])

    def test_no_look_ahead_with_events(self):
        bars = self.bars()
        fn = _registry_fn("rsi|malkan_bull|1h")
        # cuts before the event (41), on it (42), after it, and the end
        rep = assert_causal(fn, bars, range(20, len(bars)))
        self.assertGreater(rep["events_full"], 0)
        self.assertGreater(rep["compared"], 0)
        self.assertEqual([rep[k] for k in ("late", "repaint", "nan", "x10")], [[], [], [], []])


# --------------------------------------------------------------------------- positioning|funding_cvd_fade|1h

class TestFundingFadeCausal(unittest.TestCase):
    N = 25

    @classmethod
    def bars(cls):
        closes = [10.0 + i for i in range(cls.N)]  # new price highs...
        deltas = [5] * 21 + [-9] * 4  # ...while cvd falls from bar 21 (bearish divergence)
        return [{"t": T0 + i * H, "o": c, "h": c, "l": c, "c": c, "v": 10.0, "tbv": 5.0 + d / 2.0}
                for i, (c, d) in enumerate(zip(closes, deltas))]

    @staticmethod
    def funding():
        """99 ordinary 8h rates before the bars, an extreme rate (pct 1.0) at bar 19, and a DECOY ordinary rate at
        bar 23: after bar 23 the as-of percentile falls below 0.95, so events exist only while the extreme is the
        latest known print. Leaking the decoy into an earlier cut would change the events."""
        rates = [0.0001 + 0.000001 * (i % 7) for i in range(99)]
        series = [(T0 - H - (99 - i) * 8 * H, r) for i, r in enumerate(rates)]
        series.append((T0 + 19 * H, 0.01))
        series.append((T0 + 23 * H, 0.0001))
        return series

    def _layer(self):
        box = {"now": None}
        series = self.funding()

        def fetch(symbol, limit):  # answers as of the close of the last legitimately known bar
            return [(t, r) for (t, r) in series if t <= box["now"]]

        def before(visible):
            box["now"] = visible[-1]["t"] + H

        return _registry_fn("positioning|funding_cvd_fade|1h", fetch_funding=fetch), before

    def test_fixture_forces_events(self):
        bars = self.bars()
        fn, before = self._layer()
        before(bars)
        ev = fn(bars)
        self.assertEqual([e["t"] for e in ev], [bars[21]["t"], bars[22]["t"]], ev)
        self.assertTrue(all(e["side"] == "short" and e["event"] == "funding_fade_bearish" for e in ev))

    def test_no_look_ahead_with_events(self):
        bars = self.bars()
        fn, before = self._layer()
        rep = assert_causal(fn, bars, range(5, self.N), before_call=before)
        self.assertGreater(rep["events_full"], 0)
        self.assertGreater(rep["compared"], 0)
        self.assertEqual([rep[k] for k in ("late", "repaint", "nan", "x10")], [[], [], [], []])


if __name__ == "__main__":
    unittest.main()
