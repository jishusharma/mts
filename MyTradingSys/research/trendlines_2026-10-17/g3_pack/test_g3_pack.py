"""Tests for the trend-line G3 pack: chart causality, pre-filter causality, DEV fence, seeded spaced halves, blindness.
Run: python -m pytest MyTradingSys/research/trendlines_2026-10-17/g3_pack/test_g3_pack.py (cwd = this folder).
"""
import csv
import json
import math
import random
import re
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import g3_pack as g
from MyTradingSys.backtest.layers.trendlines.trendline_core import TrendlineDetector

HERE = Path(__file__).resolve().parent
T0 = int(datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)


def fake_bars(n=900, tf_ms=g.HOUR, seed=1):
    """A drifting sine with noise: swing pivots, eligible lines and contacts all occur (about 50 positive edges of 900)."""
    rng, out = random.Random(seed), []
    for k in range(n):
        base = 30_000 * math.exp(0.0003 * k) * (1 + 0.03 * math.sin(2 * math.pi * k / 50))
        o, c = base * (1 + rng.gauss(0, 0.002)), base * (1 + rng.gauss(0, 0.002))
        out.append(dict(t=T0 + k * tf_ms, o=o, h=max(o, c) * 1.001, l=min(o, c) * 0.999, c=c, v=rng.uniform(1, 9)))
    return out


def poison(bars, i):
    """Same bars up to i; everything after is replaced by absurd values (a chart that reads them cannot stay identical)."""
    return [b if k <= i else dict(b, o=b["o"] * 4, h=b["h"] * 5, l=b["l"] / 5, c=b["c"] * 3, v=b["v"] * 90) for k, b in enumerate(bars)]


def leaky_chart(code, bars, i, blind_id):
    """The old-style mistake: scale and draw one bar past the decision bar of the series handed in."""
    u = g.UNITS[code]
    vis = bars[i - u["shown"] + 1:i + 2]
    ch = g.Chart(blind_id, u["shown"])
    g.draw_price(ch, vis, 36, 560)
    return ch


def test_chart_contains_no_bar_after_decision_time_and_harness_catches_a_leak():
    for code, u in g.UNITS.items():
        bars = fake_bars(700)
        i = u["shown"] + 60
        clean = json.dumps(g.trend_chart(code, bars[:i + 1], i, "W-1").p)
        # a chart built from poisoned future data must not change a single primitive
        assert json.dumps(g.trend_chart(code, poison(bars, i), i, "W-1").p) == clean, code
        # the harness is not vacuous: a builder that includes bar i+1 changes the picture
        assert json.dumps(leaky_chart(code, poison(bars, i), i, "W-1").p) != json.dumps(leaky_chart(code, bars[:i + 1] + [bars[i]], i, "W-1").p)


def test_chart_text_has_no_date_clock_time_or_selection_hint():
    bars = fake_bars(700)
    for code, u in g.UNITS.items():
        i = u["shown"] + 10
        texts = [p["s"] for p in g.trend_chart(code, bars[:i + 1], i, f"{code}-07").p if p["k"] == "text"]
        assert not any(re.search(r"20[12]\d|\d\d:\d\d", s) for s in texts), texts
        assert not any(re.search(r"enrich|random|filter|line_contact|touch|eligible", s, re.I) for s in texts), texts


def test_chart_is_the_same_whatever_the_detector_state():
    """No overlay may depend on the pre-filter: two windows in different states carry the same label set."""
    bars = fake_bars(900)
    flags = g.prefilter_flags(bars, TrendlineDetector)
    on = [k for k in range(250, 880) if flags[k]]
    off = [k for k in range(250, 880) if not flags[k]]
    assert on and off, "fixture must hit both states"
    lab = lambda k: sorted(p["s"] for p in g.trend_chart("TL1H", bars[:k + 1], k, "W-1").p if p["k"] == "text" and not re.fullmatch(r"[-+\d.:%\s]+", p["s"]))
    assert lab(on[0]) == lab(off[0])
    kinds = lambda k: sorted({p["c"] for p in g.trend_chart("TL1H", bars[:k + 1], k, "W-1").p})
    assert set(kinds(on[0])) <= {"#101820", "#2a3744", "#1b2733", g.GREEN, g.RED, g.GREY, g.TXT}  # no highlight colour anywhere


def test_prefilter_is_causal():
    bars = fake_bars(900)
    full = g.prefilter_flags(bars, TrendlineDetector)
    assert any(full), "fixture must produce positives"
    for t in range(220, 880, 37):
        cut = g.prefilter_flags(bars[:t + 1], TrendlineDetector)
        assert cut[t] == full[t], t
        assert g.prefilter_flags(poison(bars, t)[:t + 1], TrendlineDetector)[t] == full[t]


def test_prefilter_needs_an_already_eligible_unbroken_line():
    class Fake:  # events written by hand: line 1 eligible known at bar 20, touched at bar 30, broken at bar 32
        def __init__(self, **kw):
            pass

        def feed(self, bars):
            self.events = [dict(line=1, state="eligible", bar=19, known_at=20, arm="A"), dict(line=1, state="touched", bar=30, known_at=30),
                           dict(line=1, state="broken", bar=32, known_at=32), dict(line=2, state="touched", bar=40, known_at=40)]
            return self
    f = g.prefilter_flags([None] * 60, Fake)
    assert [t for t, x in enumerate(f) if x] == [30, 31]  # contact bar and the next bar; the break at 32 closes it; line 2 never eligible


def test_loader_refuses_bar_at_or_after_2024_07_01(tmp_path):
    ms = lambda d: int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)
    row = lambda t: f"{t},100,101,99,100,1.0,{t + 59999},1,1,0.5,0.5,0\n"
    (tmp_path / "BTCUSDT-1m-2024-06.csv").write_text("open_time,open,high,low,close,volume,close_time,qv,n,tb,tq,ig\n" + row(ms(date(2024, 6, 30))) + row(ms(date(2024, 7, 1))), newline="\n")
    with pytest.raises(ValueError):
        g.load_bars(tmp_path)


def test_windows_are_seeded_spaced_and_split_in_halves():
    elig = list(range(300, 4000))
    flag = lambda i: i % 13 == 0
    a, b = g.pick("TL1H", elig, flag), g.pick("TL1H", elig, flag)
    assert a == b and len({r["window_id"] for r in a}) == len(a) == 20
    assert sorted(r["half"] for r in a).count("enriched") == 10 and all(flag(r["edge"]) for r in a if r["half"] == "enriched")
    edges = sorted(r["edge"] for r in a)
    assert all(y - x >= g.UNITS["TL1H"]["space"] for x, y in zip(edges, edges[1:]))
    assert [r["window_id"] for r in g.pick("TL1H", elig, flag, seed=1)] == [r["window_id"] for r in a]  # ids carry no information
    assert [r["edge"] for r in g.pick("TL1H", elig, flag, seed=1)] != [r["edge"] for r in a]


def test_eligible_edges_stay_inside_dev():
    bars = fake_bars(60, tf_ms=g.DAY)
    for b in bars:
        b["t"] += 900 * g.DAY  # 2024-06-19.. : the last bars straddle 2024-07-01
    for code in g.UNITS:
        for i in g.eligible_edges(code, bars):
            assert bars[i]["t"] + g.TF_MS[g.UNITS[code]["tf"]] <= g.CUTOFF_MS


def test_published_files_do_not_reveal_the_half_or_rules():
    p = HERE / "WINDOWS.csv"
    if p.exists():
        wins = list(csv.DictReader(open(p, encoding="utf-8")))
        assert wins and "half" not in wins[0] and "prefilter_tag" not in wins[0]
        assert all(g.DEV_FIRST <= datetime.strptime(w["right_edge_utc"][:10], "%Y-%m-%d").date() <= date(2024, 7, 1) for w in wins)  # a final 1d bar closes at 2024-07-01T00:00, the exclusive DEV cutoff
        assert all(re.fullmatch(r"TL(1H|4H|1D)-\d\d", w["window_id"]) for w in wins)
    if (HERE / "README.md").exists():
        txt = (HERE / "README.md").read_text(encoding="utf-8").lower()
        assert "enriched" not in txt and "pre-filter" not in txt and "prefilter" not in txt
        assert (HERE / "ANSWER_KEY_CLOSED" / "SELECTION_RULES.md").exists()
