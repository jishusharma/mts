"""Trend-line G3 marking pack: seeded windows, a causal pre-filter, blind chart drawing, marking sheets.

Question the two readers answer per chart: "is there an OBVIOUS, legitimate trend line here?" (Krown K-03,
`E:35` "if it ain't obvious it's probably not a trend line"). Definitions: research/layer_rebuild_2026-10-15/
READER_PROTOCOL.md section 4 (OURS). DEV only (2022-01-01..2024-06-30); the loader refuses any later bar.
Structure copied from research/g3_marks_2026-10-16/g3_pack.py with its 2026-10-17 blindness fixes: ids <unit>-NN,
no dates or clock labels, overlays identical for every window (here: none), selection rule only in the closed key.

  python g3_pack.py counts              # eligible edges and pre-filter positives per unit (no outcomes involved)
  python g3_pack.py build               # WINDOWS.csv, MARKING_SHEET_reader{1,2}.csv, ANSWER_KEY_CLOSED/KEY.csv
  python g3_pack.py draw --out DIR      # one PNG per window, rebuilt from WINDOWS.csv (PNGs are not committed)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
sys.path.insert(0, str(HERE.parent))

SEED = 20261017
N_HALF = 10
MIN, HOUR, DAY = 60_000, 3_600_000, 86_400_000
KLINES = Path("F:/MTS/data/tom_raw/klines")
DEV_FIRST = date(2022, 1, 1)
DEV_LAST = date(2024, 6, 30)
CUTOFF_MS = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
DETECTOR = dict(k=3, transform="log", price_arm="wick", max_age=500)  # contract primary family; only the pre-filter reads it
TOUCH_LOOKBACK = 3  # pre-filter: the contact starts on the edge bar or up to 3 bars before it (READER_PROTOCOL sec.3 rule)

# code: label, timeframe, bars shown, first allowed edge date, minimum spacing between windows in bars
UNITS = {
    "TL1H": dict(label="TL-1h", tf="1h", shown=240, edge0=date(2022, 3, 1), space=48),
    "TL4H": dict(label="TL-4h", tf="4h", shown=180, edge0=date(2022, 4, 1), space=24),
    "TL1D": dict(label="TL-1d", tf="1d", shown=180, edge0=date(2022, 7, 1), space=15),
}
TF_MS = {"1h": HOUR, "4h": 4 * HOUR, "1d": DAY}


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ms_of(d):
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)


# ---------------------------------------------------------------- data (DEV fence) and detector
def load_bars(klines=KLINES):
    """Closed bars per timeframe from 1m klines 2022-01..2024-06; any bar at or after 2024-07-01 raises."""
    from count_only import load_dev_1m  # same DEV loader as the count-only card: refuses any bar >= 2024-07-01
    from MyTradingSys.backtest.layers.trendlines.trendline_core import resample_closed
    b1 = load_dev_1m(klines)
    return {tf: resample_closed(b1, tf) for tf in TF_MS}


def prefilter_flags(bars, det_cls):
    """flags[t] = True when, using only information known at the close of bar t, a live unbroken line that is already
    eligible (arm A or B, eligibility known before the contact) had a new contact episode on bars t-3..t.
    Built from the append-only event list filtered by `known_at <= t` and `bar <= t`, so no later event can reach it."""
    det = det_cls(tf="x", **DETECTOR).feed(bars)
    by_line = defaultdict(list)
    for e in det.events:
        by_line[e["line"]].append(e)
    flags = [False] * len(bars)
    for evs in by_line.values():
        elig = [e["known_at"] for e in evs if e["state"] == "eligible"]
        if not elig:
            continue
        first_elig = min(elig)
        broken = [e["bar"] for e in evs if e["state"] == "broken"]
        broke_at = min(broken) if broken else None
        retired = [e["bar"] for e in evs if e["state"] == "retired"]
        retired_at = min(retired) if retired else None
        for e in evs:
            if e["state"] != "touched" or e["bar"] <= first_elig:
                continue
            for t in range(e["bar"], min(e["bar"] + TOUCH_LOOKBACK, len(bars) - 1) + 1):
                if (broke_at is None or broke_at > t) and (retired_at is None or retired_at > t) and e["known_at"] <= t and first_elig <= t:
                    flags[t] = True
    return flags


# ---------------------------------------------------------------- window selection (seeded)
def spaced_pick(order, taken, space, n):
    got = []
    for i in order:
        if len(got) >= n:
            break
        if all(abs(i - j) >= space for j in taken + got):
            got.append(i)
    return got


def pick(code, eligible, flag_of, seed=SEED):
    """Half enriched (pre-filter true at the edge, seeded draw), half random; spaced; returns records in shuffled id order."""
    u = UNITS[code]
    rng = random.Random(f"{seed}-{code}")
    cands = [i for i in eligible if flag_of(i)]
    rng.shuffle(cands)
    got = spaced_pick(cands, [], u["space"], N_HALF)
    recs = [dict(edge=i, half="enriched", tag="line_contact") for i in got]
    rest = list(eligible)
    rng.shuffle(rest)
    rnd = spaced_pick(rest, got, u["space"], N_HALF)
    recs += [dict(edge=i, half="random", tag="line_contact" if flag_of(i) else "") for i in rnd]
    rng.shuffle(recs)
    for k, r in enumerate(recs, 1):
        r["window_id"] = f"{code}-{k:02d}"
    return recs


def eligible_edges(code, bars):
    u = UNITS[code]
    lo = ms_of(u["edge0"])
    return [i for i, b in enumerate(bars) if b["t"] >= lo and i >= u["shown"] and b["t"] + TF_MS[u["tf"]] <= CUTOFF_MS]


def build_windows(bars_by_tf, det_cls):
    recs = []
    for code, u in UNITS.items():
        bars = bars_by_tf[u["tf"]]
        flags = prefilter_flags(bars, det_cls)
        for r in pick(code, eligible_edges(code, bars), lambda i, f=flags: f[i]):
            recs.append(dict(r, unit=code, end=bars[r["edge"]]["t"] + TF_MS[u["tf"]]))
    return recs


# ---------------------------------------------------------------- drawing geometry (blind: no dates, % axis)
W_PX, H_PX, X0, X1 = 1400, 860, 70, 1300
GREEN, RED, GREY, TXT = "#39bd93", "#e66c6c", "#6b7a88", "#d7dee5"


def nice_step(span):
    for s in (0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 5, 10, 20, 50, 100):
        if span / s <= 9:
            return s
    return 200


class Chart:
    def __init__(self, title, n):
        self.p = [dict(k="rect", x=0, y=0, w=W_PX, h=H_PX, c="#101820")]
        self.n = n
        self.text(12, 8, title, 14)

    def text(self, x, y, s, size=11, c=TXT):
        self.p.append(dict(k="text", x=x, y=y, s=s, c=c, size=size))

    def x(self, k):
        return X0 + (k + 0.5) * (X1 - X0) / self.n

    def y(self, v):
        return self.top + self.h - (v - self.lo) / (self.hi - self.lo) * self.h

    def line(self, pts, c, w=1):
        pts = [[round(a, 1), round(b, 1)] for a, b in pts]
        if len(pts) >= 2:
            self.p.append(dict(k="line", pts=pts, c=c, w=w))

    def panel(self, top, height, lo, hi, label, fmt="{:.2f}", step=None):
        self.top, self.h, self.lo, self.hi = top, height, lo, hi
        self.p.append(dict(k="line", pts=[[X0, top], [X1, top], [X1, top + height], [X0, top + height], [X0, top]], c="#2a3744", w=1))
        self.text(X0 + 4, top + 2, label, 11, GREY)
        step = step or (hi - lo) / 6
        v = (lo // step + 1) * step
        while v < hi:
            self.line([(X0, self.y(v)), (X1, self.y(v))], "#1b2733")
            self.text(8, self.y(v) - 7, fmt.format(v), 10, GREY)
            v += step

    def bars(self, vals, base, color_of):
        w = max(1.0, (X1 - X0) / self.n * 0.6)
        for k, v in enumerate(vals):
            y0, y1 = self.y(base), self.y(v)
            self.p.append(dict(k="rect", x=round(self.x(k) - w / 2, 1), y=round(min(y0, y1), 1), w=round(w, 1), h=max(1.0, round(abs(y1 - y0), 1)), c=color_of(k, v)))


def draw_price(ch, vis, top, height):
    ref = vis[-1]["c"]
    pct = lambda p: (p / ref - 1) * 100
    lo, hi = pct(min(b["l"] for b in vis)), pct(max(b["h"] for b in vis))
    pad = (hi - lo) * 0.04 or 0.1
    lo, hi = lo - pad, hi + pad
    ch.panel(top, height, lo, hi, "price, % from last close (linear axis)", "{:+.1f}%", nice_step(hi - lo))
    w = max(1.0, (X1 - X0) / ch.n * 0.6)
    for k, b in enumerate(vis):
        col = GREEN if b["c"] >= b["o"] else RED
        ch.line([(ch.x(k), ch.y(pct(b["h"]))), (ch.x(k), ch.y(pct(b["l"])))], col, 1)
        y0, y1 = ch.y(pct(b["o"])), ch.y(pct(b["c"]))
        ch.p.append(dict(k="rect", x=round(ch.x(k) - w / 2, 1), y=round(min(y0, y1), 1), w=round(w, 1), h=max(1.0, round(abs(y1 - y0), 1)), c=col))


def trend_chart(code, bars, i, blind_id):
    """Candles and volume of the `shown` bars ending at bar i. Same panels and text for every window: no overlay, no date,
    no clock time, nothing computed from the detector. Reads bars[:i+1] only."""
    u = UNITS[code]
    n = u["shown"]
    if i - n + 1 < 0:
        raise ValueError("window starts before the first bar")
    vis = bars[i - n + 1:i + 1]
    ch = Chart(f"{blind_id} | {u['label']} | BTCUSDT {u['tf']} | last closed bar = right edge (offset 0) | dates hidden", n)
    draw_price(ch, vis, 36, 560)
    for k in range(0, n, 20):  # bar offsets from the right edge, never a clock time
        ch.text(ch.x(k) - 8, ch.top + ch.h + 2, str(k - n + 1), 10, GREY)
    ch.panel(36 + 560 + 24, 150, 0, max(b["v"] for b in vis) * 1.05, "volume (BTC)", "{:.0f}")
    ch.bars([b["v"] for b in vis], 0, lambda k, v: GREEN if vis[k]["c"] >= vis[k]["o"] else RED)
    ch.text(12, H_PX - 18, "Offset 0 = last closed bar. Mark: is there an obvious, legitimate trend line? Anchors as offsets.", 10, GREY)
    return ch


def render(jobs, ps1=HERE / "render_png.ps1", batch=20):
    with tempfile.TemporaryDirectory() as td:  # primitives never land in the repo folder
        for s in range(0, len(jobs), batch):
            tmp = Path(td) / f"render_{s}.json"
            tmp.write_text(json.dumps([dict(out=str(j["out"]), w=W_PX, h=H_PX, prims=j["prims"]) for j in jobs[s:s + batch]]), encoding="utf-8")
            subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1), str(tmp)], check=True)


# ---------------------------------------------------------------- outputs
SHEET_COLS = ["window_id", "row", "reader", "obvious_line", "side", "anchor1_offset", "anchor2_offset", "touches_seen", "note"]


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _env():
    from MyTradingSys.backtest.layers.trendlines.trendline_core import TrendlineDetector
    return TrendlineDetector


def cmd_build(args):
    bars = load_bars(args.klines)
    recs = build_windows(bars, _env())
    order = {c: n for n, c in enumerate(UNITS)}
    recs.sort(key=lambda r: (order[r["unit"]], r["window_id"]))
    win = [dict(window_id=r["window_id"], row=UNITS[r["unit"]]["label"], timeframe=UNITS[r["unit"]]["tf"], bars_shown=UNITS[r["unit"]]["shown"],
                right_edge_utc=iso(r["end"]), seed=f"{SEED}-{r['unit']}") for r in recs]
    write_csv(HERE / "WINDOWS.csv", list(win[0]), win)
    key = [dict(window_id=r["window_id"], row=UNITS[r["unit"]]["label"], half=r["half"], prefilter_tag=r["tag"], right_edge_utc=iso(r["end"])) for r in recs]
    (HERE / "ANSWER_KEY_CLOSED").mkdir(exist_ok=True)
    write_csv(HERE / "ANSWER_KEY_CLOSED" / "KEY.csv", list(key[0]), key)
    for n, who in ((1, "operator"), (2, "claude")):
        write_csv(HERE / f"MARKING_SHEET_reader{n}_{who}.csv", SHEET_COLS,
                  [dict(window_id=r["window_id"], row=UNITS[r["unit"]]["label"], reader=f"reader{n}_{who}") for r in recs])
    sha = hashlib.sha256((HERE / "ANSWER_KEY_CLOSED" / "KEY.csv").read_bytes()).hexdigest()
    print(f"windows={len(recs)} key_sha256={sha}")
    per = defaultdict(lambda: defaultdict(int))
    for r in recs:
        per[UNITS[r["unit"]]["label"]][r["half"]] += 1
    for k, v in per.items():
        print(k, dict(v))


def cmd_counts(args):
    bars = load_bars(args.klines)
    det = _env()
    for code, u in UNITS.items():
        b = bars[u["tf"]]
        flags = prefilter_flags(b, det)
        el = eligible_edges(code, b)
        print(code, "eligible", len(el), "pre-filter positives", sum(1 for i in el if flags[i]))


def cmd_draw(args):
    bars = load_bars(args.klines)
    label_to_code = {u["label"]: c for c, u in UNITS.items()}
    jobs = []
    Path(args.out).mkdir(parents=True, exist_ok=True)
    for w in csv.DictReader(open(HERE / "WINDOWS.csv", encoding="utf-8")):
        code = label_to_code[w["row"]]
        u = UNITS[code]
        end = int(datetime.strptime(w["right_edge_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() * 1000)
        b = bars[u["tf"]]
        i = next(k for k in range(len(b) - 1, -1, -1) if b[k]["t"] + TF_MS[u["tf"]] == end)
        jobs.append(dict(out=Path(args.out) / f"{w['window_id']}.png", prims=trend_chart(code, b[:i + 1], i, w["window_id"]).p))
    render(jobs)
    print(f"drawn={len(jobs)} -> {args.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["counts", "build", "draw"])
    ap.add_argument("--klines", default=str(KLINES))
    ap.add_argument("--out", default=r"F:\MTS\data\g3_pack_trendlines_2026-10-17\charts")
    a = ap.parse_args()
    {"counts": cmd_counts, "build": cmd_build, "draw": cmd_draw}[a.cmd](a)
