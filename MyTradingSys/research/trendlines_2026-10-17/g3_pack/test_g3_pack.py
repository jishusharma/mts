"""Tests for the G3 trend-line pack: causal pre-filter and chart, DEV fences, seeded windows, blindness."""
import csv
import json
import random
import re
from datetime import date, datetime, timezone
from pathlib import Path

import g3_pack as g

HERE = Path(__file__).resolve().parent
T0 = int(datetime(2022, 3, 1, tzinfo=timezone.utc).timestamp() * 1000)


def fake_bars(n=700, step=4 * g.HOUR, seed=5):
    """Random walk with slow waves so swings, lines and volume exist."""
    rng, out, px = random.Random(seed), [], 30_000.0
    for k in range(n):
        o = px
        px *= 1 + rng.gauss(0.0004, 0.008) + 0.004 * ((k // 40) % 2 * 2 - 1)
        out.append(dict(t=T0 + k * step, o=o, h=max(o, px) * 1.003, l=min(o, px) * 0.997, c=px, vol=100 * rng.uniform(0.5, 3)))
    return out


def line_bars(n=140, t0=T0):
    """Hand-built rising support: swings at 20, 60, 100 on a straight line; bars between sit well above it."""
    B = []
    for k in range(n):
        line = 30_000.0 * (1.002 ** k)
        low = line if k in (20, 60, 100) else line * 1.03 + (3 if k % 2 else 0)
        B.append(dict(t=t0 + k * 4 * g.HOUR, o=low * 1.02, h=low * 1.04, l=low, c=low * 1.02, vol=10.0))
    return B


def mixed_bars():
    """Random walk followed by a planted line: positives exist at the end (indices 560..)."""
    walk = fake_bars(420)
    return walk + line_bars(140, walk[-1]["t"] + 4 * g.HOUR)


def leaks(fn, bars, idxs):
    """True if fn(bars, i) changes when every bar after i is removed or poisoned (look-ahead)."""
    for i in idxs:
        poisoned = bars[:i + 1] + [dict(b, h=b["h"] * 3, l=b["l"] / 3, c=b["c"] * 2, o=b["o"] * 2, vol=b["vol"] * 50) for b in bars[i + 1:]]
        a, b, c = fn(bars, i), fn(bars[:i + 1], i), fn(poisoned, i)
        if not (json.dumps(a) == json.dumps(b) == json.dumps(c)):
            return True
    return False


def chart_fn(code):
    return lambda bars, i: g.tl_chart(code, bars, i, "W-1").p


def test_prefilter_is_causal_and_harness_catches_a_leak():
    bars = mixed_bars()
    idxs = list(range(260, 559, 23)) + [559]
    assert not leaks(g.pf_line, bars, idxs)
    assert g.pf_line(bars, 559) == "support"  # exercised on real positives, not only None == None
    leaky = lambda B, i: B[i + 1]["c"] > B[i]["c"] if i + 1 < len(B) else None
    assert leaks(leaky, bars, idxs)


def test_chart_includes_no_bar_after_the_decision_bar():
    """A chart built for decision bar i must be byte-identical when all later bars are removed or poisoned."""
    bars = fake_bars()
    for code in g.UNITS:
        assert not leaks(chart_fn(code), bars, [g.UNITS[code]["shown"] + 5, 400, 650]), code

    def off_by_one_chart(B, i):  # the failure this test exists for: a window that ends one bar late
        return g.tl_chart("TL4H", B, min(i + 1, len(B) - 1), "W-1").p
    assert leaks(off_by_one_chart, bars, [300, 400])


def test_chart_is_blind_and_independent_of_the_pre_filter():
    bars = mixed_bars()
    on, off = set(), set()
    for i in list(range(260, 559, 23)) + [559]:
        p = g.tl_chart("TL4H", bars, i, "W-1").p
        texts = [x["s"] for x in p if x["k"] == "text"]
        assert not any(re.search(r"20[12]\d|\d\d:\d\d", s) for s in texts), texts
        labs = tuple(s for s in texts if not re.fullmatch(r"[-+\d.:%\s]+", s))
        (on if g.pf_line(bars, i) else off).add(labs)
    assert on and off and on == off and len(on) == 1  # same labels and overlays whatever the pre-filter says


def test_windows_are_seeded_spaced_and_split_in_halves():
    elig = list(range(300, 3000))
    tag = lambda i: "support" if i % 13 == 0 else None
    a, b = g.pick("TL4H", elig, tag), g.pick("TL4H", elig, tag)
    assert a == b and len({r["window_id"] for r in a}) == len(a) == 20
    assert all(re.fullmatch(r"TL4H-\d\d", r["window_id"]) for r in a)
    assert sorted(r["half"] for r in a).count("enriched") == 10 and all(tag(r["edge"]) for r in a if r["half"] == "enriched")
    edges = sorted(r["edge"] for r in a)
    assert all(y - x >= g.UNITS["TL4H"]["space"] for x, y in zip(edges, edges[1:]))
    assert [r["window_id"] for r in g.pick("TL4H", elig, tag, seed=1)] == [r["window_id"] for r in a]  # ids carry no information
    assert [r["edge"] for r in g.pick("TL4H", elig, tag, seed=1)] != [r["edge"] for r in a]


def test_dev_fences_never_read_later_data(tmp_path):
    head = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
    d = tmp_path / "d"
    d.mkdir()
    (d / "BTCUSDT-1d-2024-06.csv").write_text(
        head + f"{g.ms_of(date(2024, 6, 30))},1,2,0.5,1.5,10,0,0,0,0,0,0\n" + f"{g.ms_of(date(2024, 7, 1))},1,2,0.5,1.5,10,0,0,0,0,0,0\n", encoding="utf-8")
    assert [g.iso(b["t"]) for b in g.load_daily(d)] == ["2024-06-30T00:00:00Z"]
    k = tmp_path / "k"
    k.mkdir()
    last = g.ms_of(date(2024, 6, 30))
    rows = "".join(f"{last + g.DAY - 240 * g.MIN + m * g.MIN},1,2,0.5,1.5,1,0,0,0,0,0,0\n" for m in range(240))  # one full 4h bucket
    (k / "BTCUSDT-1m-2024-06.csv").write_text(head + rows + f"{last + g.DAY},9,9,9,9,1,0,0,0,0,0,0\n", encoding="utf-8")
    (k / "BTCUSDT-1m-2024-07.csv").write_text("this file must never be opened\n", encoding="utf-8")
    got = g.load_4h(k)
    assert len(got) == 1 and g.iso(got[0]["t"]) == "2024-06-30T20:00:00Z"


def test_known_line_is_found_and_a_broken_one_is_not():
    B = line_bars()
    assert g.pf_line(B, 139) == "support"
    B2 = [dict(b) for b in B]
    B2[120].update(c=B2[120]["l"] * 0.9, l=B2[120]["l"] * 0.9)  # a close through the line: broken before the decision bar
    assert g.pf_line(B2, 139) != "support"


def test_published_window_list_and_readme_do_not_reveal_the_half():
    p = HERE / "WINDOWS.csv"
    if p.exists():
        wins = list(csv.DictReader(open(p, encoding="utf-8")))
        assert wins and "half" not in wins[0] and "prefilter_tag" not in wins[0]
        assert not any("random" in w["window_id"] or "enriched" in w["window_id"] for w in wins)
        assert all(date(2021, 3, 1) <= datetime.strptime(w["right_edge_utc"][:10], "%Y-%m-%d").date() <= date(2024, 7, 1) for w in wins)
    if (HERE / "README.md").exists():
        txt = (HERE / "README.md").read_text(encoding="utf-8").lower()
        assert "enriched" not in txt and "pre-filter" not in txt and "prefilter" not in txt and "10 random" not in txt
        assert (HERE / "ANSWER_KEY_CLOSED" / "SELECTION_RULES.md").exists()
