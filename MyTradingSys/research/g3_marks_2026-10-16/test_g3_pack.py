"""Tests for the G3 pack: causality of every pre-filter and chart, DEV fences, seeded windows, blindness."""
import csv
import gzip
import json
import random
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import g3_pack as g

HERE = Path(__file__).resolve().parent
T0 = int(datetime(2025, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)


def fake_rows(days=8, seed=7):
    """Random-walk 1m footprint rows with the fields load_intraday produces."""
    rng, rows, px = random.Random(seed), [], 100_000.0
    cvd = 0.0
    for k in range(days * 1440):
        t = T0 + k * g.MIN
        if t % g.DAY == 0:
            cvd = 0.0
        o = px
        px += rng.gauss(0, 18) + (6 if (k // 600) % 2 else -6)
        c, buy, sell = px, rng.uniform(0.5, 6), rng.uniform(0.5, 6)
        cvd += buy - sell
        b = int(o // 10 * 10)
        rows.append(dict(t=t, o=o, h=max(o, c) + 5, l=min(o, c) - 5, c=c, buy=buy, sell=sell, delta=buy - sell, cvd=cvd,
                         bbn=int(rng.random() < 0.02), bsn=int(rng.random() < 0.02),
                         fp=f"{b}:{buy / 2:.3f}:{sell / 2:.3f}|{b + 10}:{buy / 2:.3f}:{sell / 2:.3f}"))
    return rows


def fake_daily(n=620, seed=3):
    rng, out, px = random.Random(seed), [], 20_000.0
    for k in range(n):
        o = px
        px *= 1 + rng.gauss(0.001, 0.03) + (0.05 if k % 90 == 0 else 0)
        out.append(dict(t=int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp() * 1000) + k * g.DAY, o=o, h=max(o, px) * 1.01,
                        l=min(o, px) * 0.99, c=px, vol=1000 * rng.uniform(0.5, 2.5) * (3 if k % 37 == 0 else 1)))
    return out


def test_value_area_and_rsi_known_numbers():
    # POC 110 (5); target 70 % of 10 = 7; 110 alone is 5, the upper neighbour 120 (3) beats the lower 100 (1): VA = 110..120
    assert g.value_area({100.0: 1, 110.0: 5, 120.0: 3, 130.0: 1}) == (110.0, 120.0, 110.0)
    closes = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]
    diffs = [closes[k] - closes[k - 1] for k in range(1, 15)]
    ag, al = sum(d for d in diffs if d > 0) / 14, -sum(d for d in diffs if d < 0) / 14
    r = g.rsi14(closes)
    assert abs(r[14] - (100 - 100 / (1 + ag / al))) < 1e-9
    ag2, al2 = (ag * 13 + 0.0) / 14, (al * 13 + 0.28) / 14  # next change is -0.28
    assert abs(r[15] - (100 - 100 / (1 + ag2 / al2))) < 1e-9
    assert g.rsi14([float(k) for k in range(40)])[30] == 100.0


def leaks(pf, build, idxs, full=None):
    """True if pf at i changes when the data after i is removed (look-ahead)."""
    full = full or build(None)
    return any(pf(full, i) != pf(build(i), i) for i in idxs)


def test_daily_prefilters_are_causal_and_harness_catches_a_leak():
    full = fake_daily()
    build = lambda cut: g.Daily(full if cut is None else full[:cut + 1])
    idxs = list(range(300, 600, 30))
    D_full, hits = build(None), {}
    for name, pf in (("krs1", g.pf_krs1), ("krs8", g.pf_krs8), ("div", g.pf_mal1617)):
        assert not leaks(pf, build, idxs, D_full), name
        hits[name] = sum(1 for i in range(280, 600) if pf(D_full, i))
    assert hits["krs8"] + hits["div"] > 0  # the harness is exercised on real positives, not only on None == None

    def leaky(D, i):  # uses the next bar: must be flagged
        return D.d[i + 1]["c"] > D.d[i]["c"] if i + 1 < len(D.d) else None
    assert leaks(leaky, build, idxs, D_full)


def test_weekly_prefilter_is_causal():
    full = fake_daily(900)
    D = g.Daily(full)
    for wk in range(30, len(D.w) - 1, 12):
        end = D.w[wk]["end"]
        cut = [x for x in full if x["t"] < end]
        D2 = g.Daily(cut)
        assert D2.w[wk]["end"] == end and g.pf_mal25(D, wk) == g.pf_mal25(D2, wk)


def test_intraday_prefilters_and_charts_are_causal_and_blind():
    rows = fake_rows()
    for code, u in g.UNITS.items():
        if u["fam"] != "intra":
            continue
        cx = g.Intra(rows, u["tf"])
        for i in (u["shown"] + 77, len(cx.bars) - 20):
            end = cx.bars[i]["t"] + cx.tf_ms
            cut = [r for r in rows if r["t"] < end]
            poisoned = [dict(r, h=r["h"] * 3, l=r["l"] / 3, c=r["c"] * 2, o=r["o"] * 2, buy=r["buy"] * 50, delta=r["delta"] * 50,
                             fp="1:9999:9999", bbn=5) if r["t"] >= end else r for r in rows]
            c1, c2 = g.Intra(cut, u["tf"]), g.Intra(poisoned, u["tf"])
            assert g.INTRA_PF[code](cx.bars, i, cx) == g.INTRA_PF[code](c1.bars, i, c1) == g.INTRA_PF[code](c2.bars, i, c2)
            p1, p2 = g.intra_chart(code, c1, i, "W-1").p, g.intra_chart(code, c2, i, "W-1").p
            assert json.dumps(p1) == json.dumps(p2), code  # nothing after the right edge reaches the picture
            texts = [p["s"] for p in p1 if p["k"] == "text"]
            assert not any(re.search(r"20[12]\d", s) for s in texts), texts  # dates are hidden


def test_daily_chart_is_causal_and_blind():
    full = fake_daily(900)
    for code in ("KRS1", "KRS8", "MAL25", "MAL1617"):
        D = g.Daily(full)
        i = 400 if code != "MAL25" else 60
        end = D.w[i]["end"] if code == "MAL25" else D.d[i]["t"] + g.DAY
        D1 = g.Daily([x for x in full if x["t"] < end])
        ch_full, ch_cut = g.daily_chart(code, D, i, "W-1").p, g.daily_chart(code, D1, i, "W-1").p
        assert json.dumps(ch_full) == json.dumps(ch_cut), code
        assert not any(re.search(r"20[12]\d", p["s"]) for p in ch_full if p["k"] == "text")


def test_windows_are_seeded_spaced_and_split_in_halves():
    elig = list(range(300, 1500))
    tag = lambda i: "up" if i % 13 == 0 else None
    a, b = g.pick("KRS8", elig, tag), g.pick("KRS8", elig, tag)
    assert a == b and len({r["window_id"] for r in a}) == len(a) == 20
    assert sorted(r["half"] for r in a).count("enriched") == 10 and all(tag(r["edge"]) for r in a if r["half"] == "enriched")
    edges = sorted(r["edge"] for r in a)
    assert all(y - x >= g.UNITS["KRS8"]["space"] for x, y in zip(edges, edges[1:]))
    assert [r["window_id"] for r in g.pick("KRS8", elig, tag, seed=1)] == [r["window_id"] for r in a]  # ids carry no information
    assert [r["edge"] for r in g.pick("KRS8", elig, tag, seed=1)] != [r["edge"] for r in a]
    div = g.pick("MAL1617", elig, lambda i: ("bear" if i % 13 == 0 else "bull" if i % 17 == 0 else None), g.UNITS["MAL1617"]["quota"])
    assert sum(1 for r in div if r["tag"] == "bear" and r["half"] == "enriched") == 5
    assert sum(1 for r in div if r["tag"] == "bull" and r["half"] == "enriched") == 5


def test_dev_fences_never_read_later_data(tmp_path):
    head = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
    ms = lambda d: int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)
    (tmp_path / "BTCUSDT-1d-2024-06.csv").write_text(
        head + f"{ms(date(2024, 6, 30))},1,2,0.5,1.5,10,0,0,0,0,0,0\n" + f"{ms(date(2024, 7, 1))},1,2,0.5,1.5,10,0,0,0,0,0,0\n", encoding="utf-8")
    assert [iso for iso in (g.iso(b["t"]) for b in g.load_daily(tmp_path))] == ["2024-06-30T00:00:00Z"]
    cols = "t,o,h,l,c,buy_vol,sell_vol,delta,cvd_day,b999_buy_n,b999_sell_n,fp\n"
    for d in (date(2025, 3, 31), date(2025, 4, 1)):
        with gzip.open(tmp_path / f"{d.isoformat()}.csv.gz", "wt", encoding="utf-8", newline="") as f:
            f.write(cols + f"{ms(d)},1,2,0.5,1.5,1,1,0,0,0,0,10:1:1\n")
    assert [g.iso(r["t"]) for r in g.load_intraday(tmp_path)] == ["2025-03-31T00:00:00Z"]


def test_published_window_list_does_not_reveal_the_half():
    p = HERE / "WINDOWS.csv"
    if not p.exists():
        return
    wins = list(csv.DictReader(open(p, encoding="utf-8")))
    assert wins and "half" not in wins[0] and "prefilter_tag" not in wins[0]
    assert not any("random" in w["window_id"] or "enriched" in w["window_id"] for w in wins)
    first, last = date(2021, 3, 1), date(2025, 3, 31)
    assert all(first <= datetime.strptime(w["right_edge_utc"][:10], "%Y-%m-%d").date() <= last for w in wins)
    assert all(not (date(2024, 6, 30) < datetime.strptime(w["right_edge_utc"][:10], "%Y-%m-%d").date() < date(2024, 12, 2)) for w in wins)


# ---- GPT audit 2026-10-16 HIGH findings (READER_PROTOCOL.md section 1 rows "outside P / break-in" and "RSI divergence")
def test_fab4_break_in_needs_at_least_four_closes_outside():
    from types import SimpleNamespace as NS

    def run_case(n_out):
        B = [dict(t=T0 + k * 5 * g.MIN, c=100.0) for k in range(12)]
        i = 11
        for k in range(i - n_out, i):
            B[k]["c"] = 150.0  # above the old VAH (110)
        cx = NS(va_prior=lambda t: (90.0, 110.0, 100.0), day_first={B[0]["t"] // g.DAY: 0})
        return g.pf_fab4(B, i, cx)
    assert run_case(2) is None and run_case(3) is None  # protocol: at least 4 closes outside before the break-in
    assert run_case(4) == "down" and run_case(6) == "down"


def test_divergence_prefilter_takes_a_20_bar_extremum_older_than_3_bars():
    from types import SimpleNamespace as NS
    n, i, a, b = 100, 90, 40, 80  # b is 10 bars before i but still the highest close of the last 20
    c, r = [100.0] * n, [50.0] * n
    c[a], c[b] = 120.0, 130.0  # ref high 5..60 bars before b, lower than b
    r[a], r[b] = 70.0, 60.0  # RSI lower at the new high
    d = [dict(o=100.0, c=99.0) for _ in range(n)]  # red trigger candle at i
    assert g.pf_mal1617(NS(c=c, rsi=r, d=d), i) == "bear"
    # mirror: lowest close of the last 20 is 10 bars old, RSI higher there
    c2, r2 = [100.0] * n, [50.0] * n
    c2[a], c2[b] = 80.0, 70.0
    r2[a], r2[b] = 30.0, 40.0
    d2 = [dict(o=100.0, c=101.0) for _ in range(n)]
    assert g.pf_mal1617(NS(c=c2, rsi=r2, d=d2), i) == "bull"
    # the reference window moves with b: a high 61+ bars before b does not count
    c3 = list(c); c3[a] = 100.0; c3[b - 61] = 120.0
    assert g.pf_mal1617(NS(c=c3, rsi=r, d=d), i) is None


def test_load_intraday_drops_rows_after_the_final_allowed_day(tmp_path):
    ms = lambda d: int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)
    cols = "t,o,h,l,c,buy_vol,sell_vol,delta,cvd_day,b999_buy_n,b999_sell_n,fp\n"
    d = date(2025, 3, 31)
    with gzip.open(tmp_path / f"{d.isoformat()}.csv.gz", "wt", encoding="utf-8", newline="") as f:
        f.write(cols + f"{ms(d)},1,2,0.5,1.5,1,1,0,0,0,0,10:1:1\n" + f"{ms(d) + g.DAY},1,2,0.5,1.5,1,1,0,0,0,0,10:1:1\n")
    assert [g.iso(r["t"]) for r in g.load_intraday(tmp_path)] == ["2025-03-31T00:00:00Z"]


# ---- blindness cards g3-remove-visible-chart-cues-that-disclo + g3-assess-and-remove-visible-chart-side- (GPT audit 2026-10-16 HIGH)
def _labels(ch):
    return sorted(p["s"] for p in ch.p if p["k"] == "text" and not re.fullmatch(r"[-+\d.:%\s]+", p["s"]))


def test_chart_drawing_never_depends_on_the_pre_filter_state():
    """An overlay drawn only when the pre-filter condition holds tells the reader which half a window is in."""
    rows = fake_rows()
    cx = g.Intra(rows, 30)
    ok_seen, no_seen = set(), set()
    for i in range(250, len(cx.bars) - 1, 5):
        ok = g.bal_run(cx.bars, i - 12, i - 1, 1.5)[0]
        (ok_seen if ok else no_seen).add(tuple(_labels(g.intra_chart("TOM15", cx, i, "W-1"))))
    assert ok_seen and no_seen, "fixture must cover balance and no-balance edges"
    assert ok_seen == no_seen and len(ok_seen) == 1


def test_intraday_chart_shows_no_clock_time_of_the_right_edge():
    rows = fake_rows()
    for code, u in g.UNITS.items():
        if u["fam"] != "intra":
            continue
        cx = g.Intra(rows, u["tf"])
        ch = g.intra_chart(code, cx, len(cx.bars) - 20, "W-1")
        assert not [p["s"] for p in ch.p if p["k"] == "text" and re.search(r"\d\d:\d\d(?! UTC)", p["s"])], code


def test_readme_does_not_publish_the_enrichment_rules():
    txt = (HERE / "README.md").read_text(encoding="utf-8").lower()
    assert "enriched" not in txt and "pre-filter" not in txt and "prefilter" not in txt and "10 random" not in txt
    assert (HERE / "ANSWER_KEY_CLOSED" / "SELECTION_RULES.md").exists()
